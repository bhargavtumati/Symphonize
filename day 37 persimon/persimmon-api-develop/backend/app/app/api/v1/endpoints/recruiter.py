from typing import Annotated
from fastapi import APIRouter, Query, status
from asyncer import asyncify, create_task_group, syncify
from app.core.config import settings
from app.schemas.response_schema import GetResponseBase, create_response
from fastapi import Depends, HTTPException
from app.models.company import Company
from app.models.recruiter import Recruiter
from app.api.v1.endpoints.models.recruiter_model import RecruiterModel
#from app.helpers.firebase_helper import verify_firebase_token
from app.helpers.regex_helper import get_domain_from_email
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

@router.get("")
def get_recruiters() -> GetResponseBase:
    return create_response(message=f"Get all recruiters", data={}, meta=meta)

@router.post("")
async def create_recruiter_endpoint( 
    recruiter: RecruiterModel, 
 #   token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        existing_recruiter = Recruiter.get_by_whatsapp_number(session=session, whatsapp_number=recruiter.whatsapp_number)
        if existing_recruiter:
            raise ValueError("WhatsAppNumberExists")
        
        email_domain = get_domain_from_email(recruiter.email_id)

        company_record = Company.get_by_domain(session=session, domain=email_domain)
        created_by = "bharat@gmail.cpom"#token['email']
        if company_record:
            company_id = company_record.id
        else:
            company_data = Company(**recruiter.company.model_dump())
            company_data.domain = email_domain
            company_record = company_data.create(session=session, created_by=created_by)
            company_id = company_record.id

        recruiter_data = Recruiter(
            full_name=recruiter.full_name,
            whatsapp_number=recruiter.whatsapp_number,
            designation=recruiter.designation,
            linkedin_url=recruiter.linkedin_url,
            email_id=recruiter.email_id,  # Ensure this matches the field in your Recruiter model
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
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/{email_id}')
def verify_recruiter_by_email(
    email_id: str,
 #   token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
    ):
    try:
        recruiter = Recruiter.verify_by_email(session=session, email=email_id)
        if recruiter:
            return True
        else: 
            return False
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
