import os
from typing import Annotated
from fastapi import APIRouter, Query, status
from asyncer import asyncify, create_task_group, syncify
from app.core.config import settings
from app.schemas.response_schema import GetResponseBase, create_response
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from app.models.company import Company
from app.models.template import Template
from app.models.recruiter import Recruiter
from app.api.v1.endpoints.models.recruiter_model import RecruiterModel
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
    recruiter: RecruiterModel, 
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
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
            email_template = Template(company_id = company_record.id, template_data = emailh.get_email_templates(), email_id=email_id)
            email_template.create(session=session, created_by=created_by)

        recruiter_data = Recruiter(
            full_name=recruiter.full_name,
            whatsapp_number=recruiter.whatsapp_number,
            designation=recruiter.designation,
            linkedin_url=recruiter.linkedin_url,
            email_id=recruiter.email_id,  # Ensure this matches the field in your Recruiter model
            company_id=company_id
        )
        
        recruiter_record = recruiter_data.create(session=session, created_by=created_by)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Recruiter created successfully",
                "data": recruiter_record,
                "status": status.HTTP_201_CREATED
            }
        )

    except ValueError as e:
        traceback.print_exc()
        if str(e) == "WhatsAppNumberExists":
            raise HTTPException(status_code=409, detail="This WhatsApp number is already registered. Please use a different number")
    
    except IntegrityError as e:
        traceback.print_exc()
        # Check if the error is related to unique constraint violation
        if "duplicate key value violates unique constraint" in str(e.orig):
            raise HTTPException(status_code=409, detail="Email already exists, please provide a new Email ID")
        else:
            raise HTTPException(status_code=500, detail="Database error occurred.")
            
    except HTTPException as e:
        traceback.print_exc()
        raise e 
    
    except Exception as e:
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
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def get_recruiter(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
) -> dict:
    email_id = token['email']
    try:
        recuriter = Recruiter.get_by_created_by_email(session=session, email=email_id)
        if not recuriter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recuriter not found.")
        
        recuriter_data = {
            "full_name": recuriter.full_name,
            "whatsapp_number": recuriter.whatsapp_number,
            "designation": recuriter.designation,
            "linkedin_url": recuriter.linkedin_url,
            "email_id" : recuriter.email_id
        }
        
        return {
            "message": "Recruiter fetched successfully",
            "recuriter": recuriter_data,
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        return e
    except Exception as e:
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}")
    
    #return create_response(message=f"Get all recruiters", data=data, meta=meta)
    