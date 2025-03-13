import os
from typing import Annotated, Optional, List
from fastapi import APIRouter, Query, status
from asyncer import asyncify, create_task_group, syncify
from app.core.config import settings
from app.schemas.response_schema import GetResponseBase, create_response
from fastapi import Depends, HTTPException, File, Form, UploadFile
from app.models.company import Company,CompanyTypeEnum,BusinessTypeEnum
from app.models.template import Template
from app.models.recruiter import Recruiter
from app.api.v1.endpoints.models.recruiter_model import RecruiterModel
from app.api.v1.endpoints.models.company_model import CompanyModel
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers.regex_helper import get_domain_from_email
import app.helpers.email_helper as emailh
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
import traceback

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

@router.post("")
async def create_recruiter_endpoint( 
    full_name: str = Form(...),
    whatsapp_number: str = Form(...),
    designation: str = Form(...),
    linkedin_url: str = Form(...),
    email_id: str = Form(...),
    company_name: str = Form(...),
    website: str = Form(...),  
    number_of_employees: str = Form(...),
    industry_type: str = Form(...),
    company_type: CompanyTypeEnum = Form(...),
    company_linkedin_url: str = Form(...),
    tagline: Optional[str] = Form(None),  # ✅ NULL instead of empty string
    business_type: Optional[BusinessTypeEnum] = Form(None),
    about: Optional[str] = Form(None),
    instagram_url: Optional[str] = Form(None),
    facebook_url: Optional[str] = Form(None),
    x_url: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    company_images: Optional[List[UploadFile]] = File(None),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        # Check if recruiter already exists by WhatsApp number
        existing_recruiter = Recruiter.get_by_whatsapp_number(session=session, whatsapp_number=whatsapp_number)
        if existing_recruiter:
            raise HTTPException(status_code=409, detail="This WhatsApp number is already registered. Please use a different number")

        email_domain = get_domain_from_email(email_id)
        company_record = Company.get_by_domain(session=session, domain=email_domain)
        created_by = token['email']
        try:
            
            validated_company = CompanyModel(
                name = company_name,
                website= website,
                number_of_employees= number_of_employees,
                industry_type= industry_type,
                company_type= company_type.value,
                tagline= tagline,
                business_type= business_type.value,
                about= about,
                linkedin_url= company_linkedin_url,
                instagram_url= instagram_url,
                facebook_url= facebook_url,
                x_url= x_url,
                logo= logo,
                company_images= company_images
            )
            validated_recruiter = RecruiterModel(
                full_name=full_name,
                whatsapp_number=whatsapp_number,
                designation=designation,
                linkedin_url=linkedin_url,
                email_id=email_id,
                company=validated_company  
            )
        except ValueError as e:
               raise HTTPException(status_code=422, detail=str(e))




        logo_bytes = company_images_bytes = None
        if logo:
            file_size = logo.file.seek(0, 2)  # Get file size in bytes
            logo.file.seek(0)  # Reset file pointer
            if file_size > 5 * 1024 * 1024:
                 raise HTTPException(status_code=400, detail="Logo size must be less than 5MB.")

            logo_bytes = logo.file.read() if logo else None  
      
        # Validate and process company images
        if company_images:
            for image in company_images:
                img_size = image.file.seek(0, 2)  # Get file size in bytes
                image.file.seek(0)  # Reset file pointer
                if img_size > 5 * 1024 * 1024:  # Limit images to 5MB
                    raise HTTPException(status_code=400, detail="Each image must be less than 5MB.")
            company_images_bytes = [image.file.read() for image in company_images] if company_images else None  

        if company_record:
            company_id = company_record.id
        else:
            company_data = Company(
                name=company_name,
                website=website,
                number_of_employees=number_of_employees,
                industry_type=industry_type,
                company_type=company_type,
                tagline=tagline,
                business_type=business_type,
                about=about,
                linkedin_url=company_linkedin_url,
                instagram_url=instagram_url,
                facebook_url=facebook_url,
                x_url=x_url,
                domain=email_domain,
                logo=logo_bytes,
                company_images=company_images_bytes
            )
            company_record = company_data.create(session=session, created_by=created_by)
            company_id = company_record.id

            # Create email template for new company
            email_id = os.getenv("TEMPLATE_EMAIL_ID")
            email_template = Template(company_id=company_record.id, template_data=emailh.get_email_templates(), email_id=email_id)
            email_template.create(session=session, created_by=created_by)

        recruiter_data = Recruiter(
            full_name=full_name,
            whatsapp_number=whatsapp_number,
            designation=designation,
            linkedin_url=linkedin_url,
            email_id=email_id,
            company_id=company_id
        )

        recruiter_record = recruiter_data.create(session=session, created_by=created_by)

        return {
            "message": "Recruiter created successfully",
            "data": recruiter_record,
            "status": 201
        }

    except HTTPException as e:
        raise e
    except IntegrityError as e:
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already exists, please provide a new Email ID")
        else:
            raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/{recruiter_id}")
async def update_recruiter_endpoint(
    recruiter_id : int,
    full_name: str = Form(...),
    whatsapp_number: str = Form(...),
    designation: str = Form(...),
    linkedin_url: str = Form(...),
    email_id: str = Form(...),
    company_name: str = Form(...),
    website: str = Form(...),  
    number_of_employees: str = Form(...),
    industry_type: str = Form(...), 
    company_linkedin_url: str = Form(...),
    company_type: CompanyTypeEnum = Form(...),   
    tagline: Optional[str] = Form(None),     # ✅ NULL instead of empty string
    business_type: Optional[BusinessTypeEnum] = Form(None),
    about: Optional[str] = Form(None),
    instagram_url: Optional[str] = Form(None),
    facebook_url: Optional[str] = Form(None),
    x_url: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    company_images: Optional[List[UploadFile]] = File(None),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        recruiter = session.query(Recruiter).filter(Recruiter.id == recruiter_id).first()
        if not recruiter:
            raise HTTPException(status_code=404, detail="Recruiter not found")
        
        # Check if WhatsApp number exists for another recruiter
        if whatsapp_number and whatsapp_number != recruiter.whatsapp_number:
            existing_recruiter = Recruiter.get_by_whatsapp_number(session=session, whatsapp_number=whatsapp_number)
            if existing_recruiter:
                raise HTTPException(status_code=409, detail="This WhatsApp number is already registered. Please use a different number")

        if email_id and email_id != recruiter.email_id:
            email_domain = get_domain_from_email(email_id)
            company_record = Company.get_by_domain(session=session, domain=email_domain)
            recruiter.email_id = email_id
        else:
            email_domain = get_domain_from_email(recruiter.email_id)
            company_record = Company.get_by_domain(session=session, domain=email_domain)

        created_by = token['email']
        try:
            
            validated_company = CompanyModel(
                name = company_name,
                website= website,
                number_of_employees= number_of_employees,
                industry_type= industry_type,
                company_type= company_type.value,
                tagline= tagline,
                business_type= business_type.value,
                about= about,
                linkedin_url= company_linkedin_url,
                instagram_url= instagram_url,
                facebook_url= facebook_url,
                x_url= x_url,
                logo= logo,
                company_images= company_images
            )
            validated_recruiter = RecruiterModel(
                full_name=full_name,
                whatsapp_number=whatsapp_number,
                designation=designation,
                linkedin_url=linkedin_url,
                email_id=email_id,
                company=validated_company  
            )
        except ValueError as e:
               raise HTTPException(status_code=422, detail=str(e))


        logo_bytes = company_images_bytes = None
        if logo:
            file_size = logo.file.seek(0, 2)  # Get file size in bytes
            logo.file.seek(0)  # Reset file pointer
            if file_size > 5 * 1024 * 1024:
                 raise HTTPException(status_code=400, detail="Logo size must be less than 5MB.")

            logo_bytes = logo.file.read() if logo else None  
      
        # Validate and process company images
        if company_images:
            for image in company_images:
                img_size = image.file.seek(0, 2)  # Get file size in bytes
                image.file.seek(0)  # Reset file pointer
                if img_size > 5 * 1024 * 1024:  # Limit images to 5MB
                    raise HTTPException(status_code=400, detail="Each image must be less than 5MB.")
            company_images_bytes = [image.file.read() for image in company_images] if company_images else None   

        # Update recruiter details

        recruiter.full_name = full_name 
        recruiter.whatsapp_number = whatsapp_number 
        recruiter.designation = designation 
        recruiter.linkedin_url = linkedin_url 
        recruiter.company_id = recruiter.company_id

         
        company_record = session.query(Company).filter_by(domain=email_domain).first()
        
        company_record.name = company_name
        company_record.website = website
        company_record.number_of_employees = number_of_employees
        company_record.industry_type = industry_type
        company_record.company_type = company_type
        company_record.tagline = tagline
        company_record.business_type = business_type
        company_record.about = about
        company_record.linkedin_url = company_linkedin_url
        company_record.instagram_url = instagram_url
        company_record.facebook_url = facebook_url
        company_record.x_url = x_url
        company_record.logo = logo_bytes 
        company_record.company_images = company_images_bytes
       
       
        session.commit()
        recruiter_data = {
            "full_name": recruiter.full_name,
            "whatsapp_number": recruiter.whatsapp_number,
            "designation": recruiter.designation,
            "linkedin_url": recruiter.linkedin_url,
            "email_id" : recruiter.email_id
        }
        return {
            "message": "Recruiter updated successfully",
            "data": recruiter_data,
            "status": 200
        }

    except HTTPException as e:
        session.rollback()
        raise e
    except IntegrityError as e:
        print("expection occured here")
        traceback.print_exc()
        session.rollback()
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already exists, please provide a new Email ID")
        else:
            raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/{email_id}')
def verify_recruiter_by_email(
    email_id: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
    ):
    try:
        exists = Recruiter.exists_by_email_id(session=session, email=email_id)
        return exists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_recruiter(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
) -> dict:
    email_id = token['email']
    try:
        recruiter = Recruiter.get_by_created_by_email(session=session, email=email_id)
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recuriter not found.")
        
        recruiter_data = {
            "full_name": recruiter.full_name,
            "whatsapp_number": recruiter.whatsapp_number,
            "designation": recruiter.designation,
            "linkedin_url": recruiter.linkedin_url,
            "email_id" : recruiter.email_id
        }
        
        return {
            "message": "Recruiter fetched successfully",
            "recruiter": recruiter_data,
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        return e
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")
    
    #return create_response(message=f"Get all recruiters", data=data, meta=meta)
    