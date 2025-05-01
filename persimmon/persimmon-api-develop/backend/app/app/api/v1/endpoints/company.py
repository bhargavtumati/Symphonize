import os
import traceback
from typing import Optional, List

from pydantic import ValidationError

from sqlalchemy.orm import Session

from fastapi import APIRouter, status
from fastapi import Depends, HTTPException, UploadFile, Form, File

from app.db.session import get_db
from app.helpers.firebase_helper import verify_firebase_token
from app.models.master_data import MasterData
from app.models.job import Job
from app.helpers import regex_helper as regexh, db_helper as dbh, company_helper as companyh
from app.models.company import Company, CompanyTypeEnum, BusinessTypeEnum
from app.api.v1.endpoints.models.company_model import CompanyModel, RemoveImageModel, IndustryType, Department, Designation
import app.helpers.image_helper as imageh

router = APIRouter()

api_reference: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}
PERSIMMON_IMAGES_BUCKET=os.getenv("PERSIMMON_IMAGES_BUCKET")
ENVIRONMENT=os.getenv("ENVIRONMENT")
COMPANY_NOT_FOUND = "Company not found"

@router.get("")
async def get_company_by_domain(
    domain: str,  # The domain will be passed as a query parameter
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        # Step 1: Retrieve company details by domain
        company_record:Company = Company.get_by_domain(session=session, domain=domain)
        if not company_record:
            raise HTTPException(status_code=404, detail=COMPANY_NOT_FOUND)

        # if company_record.logo:
        #     logo_file_path = company_record.logo.replace(f"/{PERSIMMON_IMAGES_BUCKET}/", "")

        # Step 2: Return company details
        company_data = {k:v for k,v in {
            "id": company_record.id,
            "name": company_record.name,
            "website": company_record.website,
            "number_of_employees": company_record.number_of_employees,
            "industry_type": company_record.industry_type,
            "linkedin": company_record.linkedin,
            "type": company_record.type.name if company_record.type else None,
            "business_type": company_record.business_type.name if company_record.business_type else None,
            "about": company_record.about,
            "tagline": company_record.tagline,
            "facebook": company_record.facebook,
            "twitter": company_record.twitter,
            "instagram": company_record.instagram,
            "logo": await imageh.get_base64_image(company_record.logo) if company_record.logo else None,
            "images": [
                {
                    "url": await imageh.get_base64_image(image),
                    "uploaded_path": image
                } for image in company_record.images] if company_record.images else None,
            "status": status.HTTP_200_OK,
            "messsage": "Company details retrieved successfully"
        }.items() if v}

        return company_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("")
def update_company_details(
    name: Optional[str] = Form(None),
    number_of_employees: Optional[str] = Form(None),
    industry_type: Optional[str] = Form(None),
    linkedin: Optional[str] = Form(None),
    type: Optional[CompanyTypeEnum] = Form(None),
    business_type: Optional[BusinessTypeEnum] = Form(None),
    about: Optional[str] = Form(None),
    tagline: Optional[str] = Form(None),
    facebook: Optional[str] = Form(None),
    twitter: Optional[str] = Form(None),
    instagram: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token.get("email")
        domain = regexh.get_domain_from_email(email=email)
        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session,domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail=COMPANY_NOT_FOUND)
            
        form_data = {
            k: v for k, v in {
                "name": name,
                "number_of_employees": number_of_employees,
                "industry_type": industry_type,
                "linkedin": linkedin,
                "type": type,
                "business_type": business_type,
                "about": about,
                "tagline": tagline,
                "facebook": facebook,
                "twitter": twitter,
                "instagram": instagram,
            }.items()
            if v is not None
        }

        if len(form_data) == 0 and not logo and not images:
            raise HTTPException(status_code=400, detail="No data provided for update")

        try:
            company_data = CompanyModel(**form_data) 
        except ValidationError as e:
            error_messages = [
                {
                    "loc"   : ["body", error["loc"][0]], 
                    "msg"   : error["msg"][13:], 
                    "input" : error["input"]
                } for error in e.errors()
            ]
            raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail = error_messages
            )

        update_data = company_data.model_dump(exclude_unset=True)

        if logo:
            if logo.content_type not in ["image/png", "image/jpeg"]:
                raise HTTPException(status_code=400, detail="Logo must be a PNG or JPEG image.")
            if logo.size > 5 * 1024 * 1024:  # 5 MB
                raise HTTPException(status_code=400, detail="Logo size must be 5 MB or less.")
            main_path = f"/{PERSIMMON_IMAGES_BUCKET}/{ENVIRONMENT}/company/logos"
            destination = imageh.save_image_to_destination(logo,main_path=main_path)
            update_data["logo"] = destination
        
        if images:
            existing_image_count = len(company_details.images) if company_details.images else 0
            total_images = len(images) + existing_image_count
            if total_images > 10 and existing_image_count > 0:
                raise HTTPException(status_code=400, detail=f"Total number of company images must be 10 or less. You already have {existing_image_count} images. You can upload up to {10 - existing_image_count} more images.")
            elif existing_image_count == 10:
                raise HTTPException(status_code=400, detail=f"Total number of company images must be 10 or less. You already uploaded {existing_image_count} images before.")

            for image in images:
                if image.content_type not in ["image/png", "image/jpeg"]:
                    raise HTTPException(status_code=400, detail=f"Image {image.filename} must be a PNG or JPEG.")
                if image.size > 5 * 1024 * 1024:
                    raise HTTPException(status_code=400, detail=f"Image {image.filename} size must be 5 MB or less.")
            main_path = f"/{PERSIMMON_IMAGES_BUCKET}/{ENVIRONMENT}/company/images"
            company_image_paths = [imageh.save_image_to_destination(image,main_path=main_path) for image in images]
            update_data["images"] = company_details.images + company_image_paths if existing_image_count > 0 else company_image_paths

        for key, value in update_data.items():
            setattr(company_details, key, value)
        company_details.meta.update(dbh.update_meta(company_details.meta, email))
        company_details.update(session=session)
           
        if number_of_employees or industry_type:
            jobs: list[Job] = Job.get_company_jobs(company_id=company_details.id,session=session) 
            companyh.update_enhanced_description(jobs=jobs, session=session, updated_by=email, number_of_employees=number_of_employees, industry_type=industry_type)
            
        return {
            "message": "Company details updated successfully",
            "status": status.HTTP_200_OK
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/image")
def remove_company_image(
    image: RemoveImageModel,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token.get("email")
        domain = regexh.get_domain_from_email(email=email)
        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details: Company = Company.get_by_domain(session=session,domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail=COMPANY_NOT_FOUND)

        new_images = [path for path in company_details.images if path != image.path]
        if len(new_images) == len(company_details.images):
            raise HTTPException(status_code=404,detail="Image not found")
        Company.remove_image(session=session, company_id=company_details.id, new_images=new_images)

        return {
            "message": "Image removed successfully",
            "status": status.HTTP_200_OK
            }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/logo")
def remove_company_logo(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token.get("email")
        domain = regexh.get_domain_from_email(email=email)
        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details: Company = Company.get_by_domain(session=session,domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail=COMPANY_NOT_FOUND)
        
        if not company_details.logo:
            raise HTTPException(status_code=404,detail="Logo not found")
        
        Company.remove_logo(session=session, company_id=company_details.id)

        return {
            "message": "Logo removed successfully",
            "status": status.HTTP_200_OK
            }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/industry-type")
async def add_new_industry_type(
    industry_type: IndustryType,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        new_industry_type = MasterData(value={"name": industry_type.industry_type}, type = "Industry Type")
        existing_record = new_industry_type.get_existing_record(session=session, key="name")
        if existing_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Industry Type already exists")
        new_industry_type.create(session=session)
        result = MasterData.get_all_by_type(session=session, type="Industry Type")
        industry_types_list = [row[0] for row in result]
        return {
            "status": status.HTTP_200_OK,
            "message": "Industry type added successfully",
            "industry_types": industry_types_list
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")   
    

@router.get("/industry-types")
async def get_all_industry_types(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        result = MasterData.get_all_by_type(session=session, type="Industry Type")
        industry_types = [row[0] for row in result]
        print("industry types are ",industry_types)
        return {
            "status": status.HTTP_200_OK,
            "industry_types": industry_types
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")
    

@router.post("/department")
async def add_department(
    department: Department,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        new_dept = MasterData(value={"name": department.department}, type = "department",)
        existing_record = new_dept.get_existing_record(session=session, key="name")
        if existing_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department already exists")
        new_dept.create(session=session)
        result = MasterData.get_all_by_type(session=session, type="department")
        departments_list = [row[0] for row in result]
        return {
            "status": status.HTTP_200_OK,
            "message": "Department added successfully",
            "departments": departments_list
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")   
    

@router.get("/departments")
async def get_all_department_names(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        result = MasterData.get_all_by_type(session=session, type="department")
        departments = [row[0] for row in result]
        return {
            "status": status.HTTP_200_OK,
            "departments": departments
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")
    

@router.post("/designation")
async def add_designation(
    designation: Designation,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        new_designation = MasterData(value={"title": designation.designation}, type = "designation")
        existing_record = new_designation.get_existing_record(session=session, key="title")
        if existing_record:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Designation already exists")
        new_designation.create(session=session)
        result = MasterData.get_all_designations(session=session)
        designations_list = [row[0] for row in result]
        return {
            "status": status.HTTP_200_OK,
            "message": "Designation added successfully",
            "designations": designations_list
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")
    

@router.get("/designations")
async def get_all_designation_names(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        result = MasterData.get_all_designations(session=session)
        designations_list = [row[0] for row in result]
        return {
            "status": status.HTTP_200_OK,
            "designations": designations_list
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")