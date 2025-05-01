import logging
import os
from fastapi import (
    APIRouter, 
    File, 
    Form, 
    HTTPException, 
    UploadFile,
    status,
    Depends
)
from app.db.session import get_db
from app.models.company import Company
from app.helpers.firebase_helper import verify_firebase_token
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import EmailStr
from typing import List
from dotenv import load_dotenv

from app.helpers import email_helper as emailh

router = APIRouter()

MINIMUM_RECIPIENTS_REQUIRED = "At least one recipient email is required."

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


api_reference: dict[str, str] = {
    "api_reference": "https://github.com/symphonize/persimmon-api"
}

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("SendingEmail")

@router.post("/send-email")
async def send_email_user(
    job_code: str = Form(...),
    to_email: List[str] = Form(...),
    from_email: EmailStr = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    service_type = File("default"),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    if service_type in ['brevo', 'sendgrid']:
        return await emailh.send_mails_via_integrations(
            name=service_type,
            job_code=job_code,
            to_email=to_email,
            from_email=from_email,
            subject=subject,
            body=body,
            files=files,
            token=token,
            session=session
        )
    else:
        try:
            to_email = emailh.parse_recipient_list(to_email)
            emailh.validate_sender_email(from_email)
            
            job, recruiter, company_details = emailh.fetch_job_recruiter_company_info(
                session=session, job_code=job_code, email_id=token["email"]
            )
            
            email_results, failed_emails = emailh.process_emails(
                session, to_email, from_email, body, subject, files, company_details, job, recruiter
            )
            emailh.update_send_email_count(session, company_details.id, len(email_results))
            
            return emailh.generate_response(email_results, failed_emails)
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/test-email")
async def send_test_email(
    to_email: EmailStr = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    from_email: EmailStr = Form(...),
    token : dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        emailh.validate_sender_email(from_email)
        domain = emailh.get_user_domain(token['email'])

        company_details = Company.get_by_domain(session=session, domain=domain)
        if not company_details:
            raise HTTPException(status_code=404, detail="Company details not found.")
        
        reply_to_email = "no-reply@symphonize.ai"
        email_results = emailh.send_email(
            subject=subject, body=body, to_email=to_email, from_email=from_email, reply_to_email=reply_to_email, attachments=files
        )
        
        emailh.update_send_email_count(session, company_details.id, 1)
        
        return {
            "status": "success",
            "message": email_results
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))