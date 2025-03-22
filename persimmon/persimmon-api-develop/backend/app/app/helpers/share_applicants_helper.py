import os
from typing import Optional

import jwt

from jinja2 import Template

from fastapi import HTTPException, Header

from sqlalchemy.orm import Session

from app.helpers import email_helper as emailh, regex_helper as regexh
from app.models.company import Company
from app.models.integration import Integration
from app.models.recruiter import Recruiter
from app.models.job import Job

# Secret key for signing JWT | python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.getenv("SECRET_KEY")
DEFAULT_REPLY_TO = "no-reply@symphonize.ai"
AUTHORIZED_SENDER = os.getenv("FROM_ADDRESS")

def generate_shareable_link(payload: dict, redirect_url: str) -> str:
    """Generates a shareable link with a JWT token."""
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return f"{redirect_url}?token={jwt_token}"


async def share_applicants_send_email(
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
            if sender != AUTHORIZED_SENDER:
                raise ValueError("The sender address is not authorized")
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
        return {"email": recipient, "error": str(e.detail)}
    except Exception as e:
        return {"email": recipient, "error": str(e)}


def get_api_key(session: Session, email: str, service_type: str):
    domain = regexh.get_domain_from_email(email = email)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain is invalid")

    company_details = Company.get_by_domain(session=session, domain=domain)
    if not company_details:
        raise HTTPException(status_code=404,detail="Company details not found")

    integration: Integration = Integration.get_credentials(session=session, company_id=company_details.id, platform_name='email')
    if not integration:
        raise HTTPException(status_code=404,detail="Email Integration details not found")
    
    credentials = integration.credentials
    for cred in credentials.get('credentials'):
        if cred.get('service_type') == service_type:
            api_key = cred['api_key'] 
            return api_key
        
    raise HTTPException(status_code=404, detail=f"{service_type} credentials not found")


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
                <p>{{RecruiterName}} has shared a list of applicants who applied for {{JobTitle}} for your review. You can access the list using the link below and provide your feedback.</p>
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