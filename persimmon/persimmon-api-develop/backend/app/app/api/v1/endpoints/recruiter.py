import os
from typing import Annotated
from fastapi import APIRouter, File, Query, UploadFile, status
from asyncer import asyncify, create_task_group, syncify
from app.core.config import settings
from app.schemas.response_schema import GetResponseBase, create_response
from fastapi import Depends, HTTPException
from fastapi.responses import Response
from app.models.company import Company
from app.models.template import Template
from app.models.recruiter import Recruiter
from app.api.v1.endpoints.models.recruiter_model import RecruiterModel, UpdateRecruiterModel
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers.regex_helper import get_domain_from_email
from app.helpers.image_helper import binary_to_base64, get_initials
from app.helpers import email_helper as emailh, gcp_helper as gcph
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import CursorResult
from app.db.session import get_db

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}
PERSIMMON_IMAGES_BUCKET=os.getenv("PERSIMMON_IMAGES_BUCKET")
ENVIRONMENT=os.getenv("ENVIRONMENT")

@router.post("")
async def create_recruiter_endpoint( 
    recruiter: RecruiterModel, 
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        print("token email", token['email'], "payload email", recruiter.email_id)
        if token['email'] != recruiter.email_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail=f"The logged-in email ID does not match the email ID provided in the request payload. Please ensure you are using the correct account."
            )
        existing_recruiter = Recruiter.get_by_whatsapp_number(session=session, whatsapp_number=recruiter.whatsapp_number)
        if existing_recruiter:
            raise ValueError("WhatsAppNumberExists")
        
        email_domain = get_domain_from_email(recruiter.email_id)

        company_record = Company.get_by_domain(session=session, domain=email_domain)
        created_by = token['email']
        if company_record:
            company_id = company_record.id
        else:
            company_data = Company(**recruiter.company.model_dump())
            company_data.domain = email_domain
            company_record = company_data.create(session=session, created_by=created_by)
            company_id = company_record.id
            email_id = os.getenv("TEMPLATE_EMAIL_ID")
            email_data = {
                "id": email_id,
                "send_count": 0
            }
            template = Template.get_by_company_id(session=session, id=company_record.id)
            if not template:
                email_template = Template(company_id = company_record.id, template_data = emailh.get_email_templates(), email_data = email_data)
                email_template.create(session=session, created_by=created_by)

        recruiter_data = Recruiter(
            full_name=recruiter.full_name,
            whatsapp_number=recruiter.whatsapp_number,
            designation=recruiter.designation,
            linkedin_url=recruiter.linkedin_url,
            email_id=recruiter.email_id,  # Ensure this matches the field in your Recruiter model
            gmail_id=recruiter.gmail_id,
            company_id=company_id
        )
        
        recruiter_record = recruiter_data.create(session=session, created_by=created_by)
        return {
            "message": "Recruiter created successfully",
            "data": recruiter_record,
            "status": status.HTTP_201_CREATED
        }

    except ValueError as e:
        if str(e) == "WhatsAppNumberExists":
            raise HTTPException(status_code=409, detail="This WhatsApp number is already registered. Please use a different number")
    
    except IntegrityError as e:
        # Check if the error is related to unique constraint violation
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already exists, please provide a new Email ID")
        else:
            raise HTTPException(status_code=500, detail="Database error occurred.")
            
    except HTTPException as e:
        raise e 
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/{email_id}')
def verify_recruiter_by_email(
    email_id: EmailStr,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
    ):
    try:
        exists = Recruiter.exists_by_email_id(session=session, email=email_id)
        return exists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('/verify/{gmail_id}')
def verify_recruiter_by_gmail(
    gmail_id: EmailStr,
    session: Session = Depends(get_db)
):
    try:
        recruiter = Recruiter.exists_by_gmail_id(session=session, gmail_id=gmail_id)
        if recruiter:
            return {
                "status": 200,
                "message": "Recruiter verified successfully",
                "email_id": recruiter.email_id
            }
        else:
            return HTTPException(status_code=404, detail="Recruiter not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("")
def get_recruiter(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
) -> dict:
    email_id = token['email']
    try:
        recruiter = Recruiter.get_by_email_id(session=session, email=email_id)
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recuriter not found.")
        if recruiter.profile_image:
            profile_image_file_path = recruiter.profile_image.replace(f"/{PERSIMMON_IMAGES_BUCKET}/", "")
            print(f"------ Profile Image File Path ------ {profile_image_file_path}")
            profile_image = gcph.generate_signed_url(PERSIMMON_IMAGES_BUCKET, file_name=profile_image_file_path)
        else:
            profile_image = None
        
        recruiter_data = {
            "full_name": recruiter.full_name,
            "whatsapp_number": recruiter.whatsapp_number,
            "designation": recruiter.designation,
            "linkedin_url": recruiter.linkedin_url,
            "email_id" : recruiter.email_id,
            "profile_image": profile_image
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


@router.patch("/update")
async def update_recruiter( 
    recruiter: UpdateRecruiterModel, 
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        existing_recruiter: Recruiter = Recruiter.get_by_email_id(session=session, email=token["email"])
        if not existing_recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found.")

        if recruiter.whatsapp_number and existing_recruiter.whatsapp_number != recruiter.whatsapp_number:
            if Recruiter.get_by_whatsapp_number(session=session, whatsapp_number=recruiter.whatsapp_number):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="WhatsApp number already exists.")

        Recruiter.update_details(
            session=session, 
            recruiter_id=existing_recruiter.id, 
            full_name=recruiter.full_name, 
            whatsapp_number=recruiter.whatsapp_number,
            designation=recruiter.designation,
            linkedin_url=recruiter.linkedin_url
        )
        return {
            "message": "Recruiter details updated successfully",
            "status": status.HTTP_200_OK
        }
    except HTTPException as e:
        raise e 
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/profile/image")
async def update_recruiter_profile_image(
    file: UploadFile = File(...),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Only JPEG and PNG images are allowed")
        
        contents = await file.read()
        if len(contents) > 2 * 1024 * 1024: 
            raise HTTPException(status_code=400, detail="File size exceeds 2MB")
        
        if not Recruiter.exists_by_email_id(session=session, email=token['email']):
            raise HTTPException(status_code=404, detail=f"recruiter not found")
        
        main_path = f"/{PERSIMMON_IMAGES_BUCKET}/{ENVIRONMENT}/recruiter/profile-images"
        destination = gcph.save_image_to_destination(file ,main_path=main_path)
        Recruiter.update_profile_image(session=session, email=token['email'], image_path=destination)
        
        profile_image_file_path = destination.replace(f"/{PERSIMMON_IMAGES_BUCKET}/", "")
        print(f"------ Profile Image File Path ------ {profile_image_file_path}")
        profile_image = gcph.generate_signed_url(PERSIMMON_IMAGES_BUCKET, file_name=profile_image_file_path)
        
        return {
            "message": "Image uploaded successfully",
            "profile_image": profile_image
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during database call {str(e)}")
    

@router.get("/profile/image")
def get_recruiter_profile_image(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    email_id = token['email']
    try:
        recruiter = Recruiter.get_by_email_id(session=session, email=email_id)
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recuriter not found.")
        if recruiter.profile_image:
            profile_image_file_path = recruiter.profile_image.replace(f"/{PERSIMMON_IMAGES_BUCKET}/", "")
            print(f"------ Profile Image File Path ------ {profile_image_file_path}")
            profile_image = gcph.generate_signed_url(PERSIMMON_IMAGES_BUCKET, file_name=profile_image_file_path)
        else:
            profile_image = None
        alternative_text = get_initials(recruiter.full_name)
        return {
            "status":200,
            "message":"Recruiter profile image retrived successfully",
            "profile_image": profile_image,
            "alternative_text": alternative_text
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")
    