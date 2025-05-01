import os
import datetime
from typing import Optional

import jwt

from jinja2 import Template

from fastapi import HTTPException, Header

from sqlalchemy.orm import Session

from app.helpers import email_helper as emailh
from app.models.integration import Integration
from app.models.applicant import Applicant
from app.models.shared import Shared

# Secret key for signing JWT | python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.getenv("SECRET_KEY")
DEFAULT_REPLY_TO = "no-reply@symphonize.ai"
AUTHORIZED_SENDER = os.getenv("FROM_ADDRESS")

def validate_applicants(session, job_id, applicant_uuids):
    nonexistent_applicants = Applicant.validate_applicant_uuids(
        session=session, job_id=job_id, applicant_uuids=applicant_uuids
    )
    if nonexistent_applicants:
        raise HTTPException(status_code=404, detail=f"Applicants not found: {nonexistent_applicants}")
    

def validate_sender(email_type, sender):
    if email_type == "default" and sender != AUTHORIZED_SENDER:
        raise ValueError("The sender address is not authorized")
    

def create_shared_record(session, email, token_uuid, applicant_uuids):
    shared_applicants = Shared(uuid=token_uuid, details=applicant_uuids)
    shared_applicants.create(session=session, created_by=email)
    
    
def generate_payload(db_job, email, data, token_uuid):
    return {
        "jc": data.job_code,
        "jt": db_job.title,
        "se": email,
        "token_uuid": token_uuid,
        "count": len(data.applicant_uuids),
        "hs": 1 if data.hide_salary else 0,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
    }


def generate_shareable_link(payload: dict, redirect_url: str) -> str:
    """Generates a shareable link with a JWT token."""
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return f"{redirect_url}?token={jwt_token}"


def get_api_key(session: Session, company_id: int, service_type: str):
    integration: Integration = Integration.get_credentials(session=session, company_id=company_id, platform_name='email')
    if not integration:
        raise HTTPException(status_code=404,detail="Email Integration details not found")
    credentials = integration.credentials
    for cred in credentials.get('credentials'):
        if cred.get('service_type') == service_type:
            api_key = cred['api_key'] 
            return api_key
    raise HTTPException(status_code=404, detail=f"{service_type} credentials not found")


async def send_email_via_service(
    email_service: str,
    api_key: str,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
    reply_to: str = DEFAULT_REPLY_TO,
):
    """Sends an email using the specified service."""
    try:
        if email_service == "default":
            emailh.send_email(
                subject=subject, body=body, to_email=recipient, from_email=sender, reply_to_email=reply_to
            )
        elif email_service == "brevo":
            await emailh.brevo_send_mail(
                api_key=api_key, from_email=sender, to_email=[recipient], subject=subject, body=body
            )
        elif email_service == "sendgrid":
            response = await emailh.sendgrid_send_mail(
                api_key=api_key, from_email=sender, to_email=[recipient], subject=subject, body=body
            )
            print("sendgrid response ", response)
        else:
            raise ValueError(f"Unsupported email service: {email_service}")
        return {"email": recipient, "status": "success"}
    except HTTPException as e:
        return {"email": recipient, "error": str(e.detail), "status": "failed"}
    except Exception as e:
        return {"email": recipient, "error": str(e), "status": "failed"}


async def dispatch_applicant_emails(session, data, payload, company, recruiter):
    success_emails, failed_emails = [], []
    api_key = None
    if data.email_type != "default":
        api_key = get_api_key(session=session, company_id=company.id, service_type=data.email_type)
        await emailh.validate_sender_for_email_integrations(from_email=data.sender, api_key=api_key, service_type=data.email_type)

    body_template_data = {
        "CompanyName": company.name,
        "JobTitle": payload["jt"],
        "RecruiterName": recruiter.full_name,
        "Designation": recruiter.designation,
    }

    for recipient_email in data.recipient_emails:
        payload["re"] = recipient_email
        body_template_data["Link"] = generate_shareable_link(payload, data.redirect_url)
        subject, body = get_share_applicants_email_templates(body_template_data)
        email_result = await send_email_via_service(
            email_service=data.email_type,
            api_key=api_key,
            sender=data.sender.lower(),
            recipient=recipient_email.lower(),
            subject=subject,
            body=body,
        )
        (success_emails if email_result["status"] == "success" else failed_emails).append(email_result)
    
    return success_emails, failed_emails


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_data 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.DecodeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    

def get_share_applicants_email_templates(body_template_data: dict) -> tuple:
    subject = "Access applicant list & provide feedback"
    body = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }
                .email-container {
                    max-width: 600px;
                    margin: 20px auto;
                    background: #ffffff;
                    padding: 20px;
                    border-radius: 8px;
                    /*box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);*/
                }
                .content {
                    font-size: 16px;
                    color: #333;
                }
                .button-container {
                    margin: 20px 0;
                }
                .button {
                    display: inline-block;
                    background-color: #007BFF;
                    color: #ffffff !important;
                    padding: 12px 20px;
                    font-size: 16px;
                    border-radius: 5px;
                    text-decoration: none;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
        <div class="email-container">
            <div class="content">
                <p>Dear Hiring team,</p>
                <p>{{RecruiterName}} has shared a list of applicants, applied for {{JobTitle}} for your review. You can access the list using the link below and provide your feedback.</p>
                <div class="button-container">
                    <a href="{{Link}}" class="button">View Applicants</a>
                </div>
                <p>To proceed, please enter your email ID to get access.</p>
                <p>Your feedback is valuable and will help us make informed hiring decisions. Let us know if you have any questions!</p>
                <p>Best regards,</p>
                <p>{{RecruiterName}}<br>{{Designation}}<br>{{CompanyName}}</p>
            </div>
        </div>
        </body>
        </html>
        """
    body = Template(body).render(body_template_data)
    return (subject, body)