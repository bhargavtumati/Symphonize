from fastapi import APIRouter, status
from pydantic import BaseModel, ValidationError
from fastapi import Depends, HTTPException, UploadFile, Form, File
from app.helpers.firebase_helper import verify_firebase_token
from app.models.company import Company, CompanyTypeEnum, BusinessTypeEnum
from app.api.v1.endpoints.models.company_model import CompanyModel, RemoveImageModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.helpers import regex_helper as regexh, db_helper as dbh, image_helper as imageh, gcp_helper as gcph
from typing import Optional, List
import os

router = APIRouter()

api_reference: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}
PERSIMMON_IMAGES_BUCKET=os.getenv("PERSIMMON_IMAGES_BUCKET")
ENVIRONMENT=os.getenv("ENVIRONMENT")

@router.get("")
def get_company_by_domain(
    domain: str,  # The domain will be passed as a query parameter
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        # Step 1: Retrieve company details by domain
        company_record:Company = Company.get_by_domain(session=session, domain=domain)
        if not company_record:
            raise HTTPException(status_code=404, detail="Company not found")

        if company_record.logo:
            logo_file_path = company_record.logo.replace(f"/{PERSIMMON_IMAGES_BUCKET}/", "")

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
            "logo": gcph.generate_signed_url(f"{PERSIMMON_IMAGES_BUCKET}",file_name=logo_file_path) if company_record.logo else None,
            "images": [
                {
                    "url": gcph.generate_signed_url(f"{PERSIMMON_IMAGES_BUCKET}",file_name=image.replace(f"/{PERSIMMON_IMAGES_BUCKET}/", "")),
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
    website: Optional[str] = Form(None),
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
            raise HTTPException(status_code=404,detail="Company not found")

        form_data = {k:v for k,v in {
            "name": name,
            "website": website,
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
        }.items() if v}
        
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

        logo_bytes = company_images_bytes = None
        if logo:
            if logo.content_type not in ["image/png", "image/jpeg"]:
                raise HTTPException(status_code=400, detail="Logo must be a PNG or JPEG image.")
            if logo.size > 5 * 1024 * 1024:  # 5 MB
                raise HTTPException(status_code=400, detail="Logo size must be 5 MB or less.")
            main_path = f"/{PERSIMMON_IMAGES_BUCKET}/{ENVIRONMENT}/company/logos"
            destination = gcph.save_image_to_destination(logo,main_path=main_path)
            update_data["logo"] = destination
        
        if images:
            existing_image_count = len(company_details.images) if company_details.images else 0
            total_images = len(images) + existing_image_count
            if total_images > 10 and existing_image_count > 0:
                raise HTTPException(status_code=400, detail=f"Total number of company images must be 10 or less. You already have {existing_image_count} images. You can upload up to {10 - existing_image_count} more images.")
            else:
                raise HTTPException(status_code=400, detail=f"Total number of company images must be 10 or less. You already uploaded {existing_image_count} images before.")

            for image in images:
                if image.content_type not in ["image/png", "image/jpeg"]:
                    raise HTTPException(status_code=400, detail=f"Image {image.filename} must be a PNG or JPEG.")
                if image.size > 5 * 1024 * 1024:
                    raise HTTPException(status_code=400, detail=f"Image {image.filename} size must be 5 MB or less.")
            main_path = f"/{PERSIMMON_IMAGES_BUCKET}/{ENVIRONMENT}/company/images"
            company_image_paths = [gcph.save_image_to_destination(image,main_path=main_path) for image in images]
            update_data["images"] = company_details.images + company_image_paths if existing_image_count > 0 else company_image_paths

        for key, value in update_data.items():
            setattr(company_details, key, value)
        company_details.meta.update(dbh.update_meta(company_details.meta, email))
        company_details.update(session=session)

        return {
            "message": "Company details updated successfully",
            "status": status.HTTP_200_OK
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
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
            raise HTTPException(status_code=404,detail="Company not found")

        new_images = [path for path in company_details.images if path != image.path]
        Company.remove_image(session=session, company_id=company_details.id, new_images=new_images)

        return {
            "message": "Image removed successfully",
            "status": status.HTTP_200_OK
            }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
