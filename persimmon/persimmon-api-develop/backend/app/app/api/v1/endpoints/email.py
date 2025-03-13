import logging
import os
from fastapi import (APIRouter, File, Form, HTTPException, UploadFile,
                     status,Depends)
from app.db.session import get_db
from app.models.job import Job
from app.models.applicant import Applicant
from app.models.company import Company
from app.models.recruiter import Recruiter
from app.helpers.firebase_helper import verify_firebase_token
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from pydantic import EmailStr
from typing import List
from app.helpers import email_helper
from dotenv import load_dotenv

from app.helpers import regex_helper as regexh, email_helper as emailh

router = APIRouter()

load_dotenv()

import logging

# Configure logging
logger = logging.getLogger(__name__)


api_reference: dict[str, str] = {
    "api_reference": "https://github.com/symphonize/persimmon-api"
}

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("SendingEmail")


@router.post("/send-email")
def send_email_user(
    job_code: str = Form(...),
    to_email: List[str] = Form(...),
    from_email: EmailStr = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    # reply_to_email: EmailStr = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    if to_email == [''] or len(to_email) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient email is required")
    reply_to_email = "no-reply@symphonize.ai"
    to_email = to_email[0].split(",")
    email_results = []
    failed_emails = []
    try:
        if from_email != os.getenv("FROM_ADDRESS"):
            raise ValueError("The from address is not authorized")
        # Validate input parameters
        if not to_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient email is required")
        
        domain = regexh.get_domain_from_email(email=token['email'])
        if not domain:
            raise HTTPException(status_code=404, detail="Domain is invalid")
        
        if not to_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient email is required")
        
        job: Job = Job.get_by_code(session=session, code=job_code)
        if not job:
            logger.error(f"Job not found with job code : {job_code}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated job not found")
        
        company_details = Company.get_by_domain(session=session, domain=domain)
        if not company_details:
            logger.error(f"Company not found for job: {job.id}")
            raise HTTPException(status_code=404,detail="Company details not found")
        
        recruiter: Recruiter = Recruiter.get_by_email_id(session, token['email'])
        if not recruiter:
            logger.warning(f"Recruiter not found for email: {token['email']}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated recuriter not found")

        # Process emails
        for email in to_email:
            try:
                if "@" not in email:
                    logger.warning(f"Invalid email format: {email}")
                    failed_emails.append({"email": email, "error": "Invalid email format"})
                    continue

                email_body, email_subject = emailh.render_email_variables(session=session, to_email=email, body=body, subject=subject, company=company_details, job=job, recuriter=recruiter)
                result = email_helper.send_email(subject=email_subject, body=email_body, to_email=email, from_email=from_email, reply_to_email=reply_to_email, attachments=files)

                if result:
                    email_results.append({"email": email, "status": "success"})

            except Exception as e:
                logger.error(f"Error processing email {email}: {str(e)}", exc_info=True)
                failed_emails.append({"email": email, "error": str(e)})
                session.rollback()  # Rollback any database changes for this email

        response = {
            "message": "Email processing completed",
            "success_count": len(email_results),
            "failure_count": len(failed_emails),
            "successful_emails": email_results,
            "failed_emails": failed_emails
        }

        if failed_emails:
            response["message"] += " with some failures"

        return response

    except ValueError as he:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(he))
    except Exception as e:
        logger.critical(f"Unexpected error in send_email_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred"
        )



@router.post("/test-email")
async def send_test_email(
    to_email: EmailStr = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    from_email: EmailStr = Form(...),
    token : dict = Depends(verify_firebase_token)
):
    if from_email != os.getenv("FROM_ADDRESS"):
        raise ValueError("The from address is not authorized")
    email_results = []
    failed_emails = []
    reply_to_email = "xyz@symphonize.com"
    try:
        if not to_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient email is required")
        
        try:
            if "@" not in to_email:
                logger.warning(f"Invalid email format: {to_email}")
                failed_emails.append({"email": to_email, "error": "Invalid email format"})
            
            result = email_helper.send_email(subject=subject, body=body, to_email=to_email, from_email=from_email, reply_to_email=reply_to_email, attachments=files)
            if result: 
                email_results.append({"email": to_email, "status": "success"})

        except Exception as e:
            logger.error(f"Error processing email {to_email}: {str(e)}", exc_info=True)
            failed_emails.append({"email": to_email, "error": str(e)})

        response = {
            "message": "Email processing completed",
            "success_count": len(email_results),
            "failure_count": len(failed_emails),
            "successful_emails": email_results,
            "failed_emails": failed_emails
        }

        if failed_emails:
            response["message"] += " with some failures"

        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.critical(f"Unexpected error in send_email_user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error occurred")