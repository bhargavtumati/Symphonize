import base64
import uuid
import json
import os
import httpx
import traceback
from typing import List,Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from pydantic import EmailStr
from python_http_client.exceptions import UnauthorizedError, ForbiddenError, HTTPError

import sib_api_v3_sdk

from fastapi import HTTPException,UploadFile, status

from sqlalchemy.orm import Session

from jinja2 import Template

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Cc, ReplyTo, Attachment, FileContent, FileName, FileType, Disposition

from app.api.v1.endpoints.models.resume_model import EmailTemplate
from app.models.company import Company
from app.models.job import Job
from app.models.recruiter import Recruiter
from app.models.applicant import Applicant
from app.models import template as temp
from app.helpers import regex_helper as regexh
from app.models.integration import Integration
from app.models.customization import Customization
from app.api.v1.endpoints.integration import EMAIL_INTEGRATION_DETAILS_NOT_FOUND



def send_email(subject: str, body: str, to_email: EmailStr, from_email: EmailStr, reply_to_email: EmailStr, attachments: Optional[List[UploadFile]]=None, cc_addresses: Optional[List[EmailStr]]=None):
    """
    Send an email using the Sendinblue SMTP service.

    Args:
        subject (str): The subject of the email.
        template_path (str): Path to the HTML template file.
        template_data (dict): Data for rendering the template.
        to_email (str): Recipient's email address.
        from_email (str): Sender's email address.
        reply_to_email (str): Reply-to email address.
        attachment_path (str, optional): Path to the file to attach.

    Returns:
        None
    """
    SMTP_SERVER = "smtp-relay.brevo.com"
    SMTP_PORT = 587  # For TLS
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    # credentials = get_smtp_credentials()
    # Load and render the email template
    # template = Template(template_path)
    # body = template.render(template_data)
    #print("the body is ",body)
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email

    if isinstance(to_email,list):
        msg['To'] = ', '.join(to_email)
    else:
        msg['To'] = to_email

    if cc_addresses:
        msg["Cc"] = ", ".join(cc_addresses)
    else:
        cc_addresses = ""
        
    msg['Subject'] = subject
    msg['Reply-To'] = reply_to_email
    msg.attach(MIMEText(body,'html'))  # Use 'html' to send HTML content

    # Attach a file if provided
    if attachments:
        #print("the attachment is ",attachment)
        try:
            for attachment in attachments:
                attachment.file.seek(0)
                file_content = attachment.file.read()
                #print(f"file content is {file_content}")
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file_content)
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{attachment.filename}"'
                )
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching file: {e}")

    # Connect to the SMTP server and send the email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start TLS for security
            server.login(SMTP_USER, SMTP_PASSWORD)  # Log in using your SMTP credentials
            all_recipients = to_email + cc_addresses
            server.sendmail(from_email, all_recipients, msg.as_string())  # Send the email
            print(f"Email sent successfully to {to_email} with CC: {cc_addresses}!")
            return f"Email sent successfully to {to_email} with CC: {cc_addresses}!" if cc_addresses else f"Email sent successfully to {to_email}!"
    except Exception as e:
        print(traceback.format_exc())
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")


def get_email_templates():
    """
    returns the email templates
    """
    current_dir = os.path.dirname(__file__)
    templates_list = os.path.join(current_dir, '..', 'datasets', 'email_templates.json')
    with open(templates_list, 'r') as file:
        templates: List[str] = json.load(file)  

    for template in templates:
        template['uuid'] = str(uuid.uuid4())
    
    return {
        "templates" : templates
    }


def add_email_template(templates:dict, payload:EmailTemplate):
    new_emplate = {
        "uuid": str(uuid.uuid4()),
        "name": payload.name,
        "subject": payload.subject,
        "body": payload.body,
        "default": False
    }
    templates['templates'].append(new_emplate)
    return templates
 
def update_email_templates(templates:dict, payload:EmailTemplate):
    for temp in templates["templates"]:
        if temp and temp.get("uuid") == payload.uuid:
            if payload.name:
                temp['name'] = payload.name
            temp["body"] = payload.body
            temp["subject"] = payload.subject
            return templates
    raise HTTPException(status_code=404, detail="Template uuid does not exists")


def render_email_variables(session: Session, to_email:str, body:str, subject: str, company:Company, job:Job, recuriter: Recruiter) -> tuple[str, str]:
    """Renders the dynamic variables for email body and subject"""

    applicant: Applicant = Applicant.get_by_emailid_and_job_id(session=session, emailid=to_email, job_id=job.id)
    if not applicant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found")

    candidate_name = applicant.details.get("personal_information").get("full_name", "Unknown")
    body_template_data = {
        "CandidateName": candidate_name,
        "CompanyName": company.name,
        "JobTitle": job.title,
        "JobType": job.type.name.title().replace("_", " "),
        "Title": job.title,
        "WorkplaceType": job.workplace_type.name.title().replace("_", " "),
        "JobLocation": job.location,
        "MinExperience": job.min_experience,
        "MaxExperience": job.max_experience,
        "MinSalary": job.min_salary,
        "MaxSalary": job.max_salary,
        "Industry": company.industry_type,
        "CompanyType": company.type.name.title().replace("_", " "),
        "CompanySize": company.number_of_employees,
        "RecruiterName": recuriter.full_name,
        "Designation": recuriter.designation,
        "CompanyWebsite": company.website,
        "RecruiterContactNumber": recuriter.whatsapp_number,
        "CareerPageJobLink": get_career_page_job_link(session=session, company=company, job_code=job.code)  
    }
    
    subject_template_date = {
        "JobTitle": job.title,
        "CompanyName" : company.name
    }

    body = Template(body).render(body_template_data)
    subject = Template(subject).render(subject_template_date)
    
    return (body, subject)


def get_career_page_job_link(session: Session, company: Company, job_code: str):
    FE_URL = os.getenv("FE_URL")
    default_job_url = f"{FE_URL}/connection/{company.domain}/jobs?jobCode={job_code}"

    customization: Customization = Customization.get_customization_settings(session=session, company_id=company.id)

    if customization:
        career_page_url = customization.settings.get('career_page_url')
        if career_page_url:
            return f"{career_page_url}?jobURL={default_job_url}"

    return default_job_url
    
    
async def get_brevo_senders(api_key: str):
    """Fetch verified sender emails from Brevo."""

    BREVO_URL = "https://api.brevo.com/v3/senders"
    headers = {
        "accept": "application/json",
        "api-key": api_key
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BREVO_URL, headers=headers)

        if response.status_code == 401:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
        elif response.status_code == 403:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden. Check your API key permissions.")
        elif response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Unexpected error: {response.text}")

        response_data = response.json()
        if "senders" not in response_data:
            raise HTTPException(status_code=500, detail="Invalid response from Brevo API.")

        active_senders = [sender["email"] for sender in response_data["senders"] if sender.get("active") == True]
        return active_senders
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error validating credentials: {str(e)}")


async def get_sendgrid_senders(api_key: str):
    """Fetch verified sender emails from SendGrid."""
    
    SENDGRID_API_URL = "https://api.sendgrid.com/v3/verified_senders"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(SENDGRID_API_URL, headers=headers)

        if response.status_code == 200:
            senders = response.json().get("results", [])
            sender_emails = [sender["from_email"] for sender in senders]
            return sender_emails

        elif response.status_code == 401 or response.status_code == 403:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key. Please check your SendGrid API Key.")

        elif response.status_code == 429:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Please try again later.")

        elif response.status_code >= 500:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="SendGrid server error. Please try again later.")

        else:
            raise HTTPException(status_code=response.status_code, detail=f"Unexpected error: {response.text}")

    except httpx.HTTPStatusError as http_error:
        raise HTTPException(status_code=http_error.response.status_code, detail=f"HTTP error occurred: {http_error}")

    except httpx.RequestError as request_error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Network error: {request_error}")
    
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    

async def send_mails_via_integrations(
    name: str,
    job_code: str ,
    to_email: List[str],
    from_email: EmailStr,
    subject: str,
    body: str,
    files: Optional[List[UploadFile]],
    token: dict,
    session: Session
):
    try:
        to_email = parse_recipient_list(to_email)
        job, recruiter, company_details = fetch_job_recruiter_company_info(
            session=session, job_code=job_code, email_id=token["email"]
        )

        integration: Integration = Integration.get_credentials(session=session, company_id=company_details.id, platform_name='email')
        if not integration:
            raise HTTPException(status_code=404,detail=EMAIL_INTEGRATION_DETAILS_NOT_FOUND)
        
        name = name.lower().strip()
        credentials = integration.credentials
        for cred in credentials.get('credentials'):
            if cred.get('service_type') == name:
                api_key = cred['api_key'] 
                break
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} credentials not found")
        await validate_sender_for_email_integrations(from_email=from_email, api_key=api_key, service_type=name)
        email_results = []
        failed_emails = []
        for email in to_email:
            try:
                email_body, email_subject = render_email_variables(
                    session=session, to_email=email, body=body, subject=subject, company=company_details, job=job, recuriter=recruiter
                )
                if name == 'brevo':
                    await brevo_send_mail(
                        api_key=api_key, from_email=from_email.lower(), to_email=[email.lower()], subject=email_subject, body=email_body, files=files
                    )
                elif name == 'sendgrid':
                    await sendgrid_send_mail(
                        api_key=api_key, from_email=from_email.lower(), to_email=[email.lower()], subject=email_subject, body=email_body, files=files
                    )

                email_results.append({"email": email, "status": "success"})

            except HTTPException as e:
                failed_emails.append({"email": email, "error": str(e.detail)})
            except Exception as e:
                failed_emails.append({"email": email, "error": str(e)})

        return generate_response(email_results, failed_emails)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error occurred")
    finally:
        if files:
            for file in files:
                await file.close()


async def brevo_send_mail(api_key: str, from_email: EmailStr, to_email: List[EmailStr], subject: str, body: str, files: Optional[List[UploadFile]] = None, reply_to_email: Optional[EmailStr] = None, cc_addresses: Optional[List[EmailStr]] = None):
    """Send email via Brevo with form data and multiple file attachments."""

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    email_data = sib_api_v3_sdk.SendSmtpEmail(
        sender={"email": from_email},
        to=[{"email": email} for email in to_email],
        subject=subject,
        html_content=body,
        cc=[{"email":cc} for cc in cc_addresses] if cc_addresses else None,
        reply_to={"email":reply_to_email} if reply_to_email else None
    )

    if files:
        attachments = []
        for file in files:
            try:
                file_content = await file.read()  
                encoded_file = base64.b64encode(file_content).decode()  
                
                attachments.append({
                    "name": file.filename,
                    "content": encoded_file
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")

        if attachments:
            email_data.attachment = attachments  

    try:
        response = api_instance.send_transac_email(email_data)
        return {"status": status.HTTP_200_OK, "message": "Email sent successfully!", "response": response}
    except sib_api_v3_sdk.rest.ApiException as e:
        if e.status == 401:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key. Please check your Brevo API key.")
        elif e.status == 403:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid sender email. Verify that your 'from_email' is authorized in Brevo.")
        else:
            raise HTTPException(status_code=e.status, detail=f"Brevo error: {json.loads(e.body)['message']}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


async def sendgrid_send_mail(api_key: str, from_email: EmailStr, to_email: List[EmailStr], subject: str, body: str, files: List[UploadFile] = None, reply_to_email: Optional[EmailStr] = None, cc_addresses: Optional[List[EmailStr]] = None):
    """Send an email via SendGrid with optional file attachments."""

    message = Mail(
        from_email=Email(from_email),
        to_emails=[To(email) for email in to_email],
        subject=subject,
        html_content=body
    )

    if cc_addresses:
        message.cc = [Cc(cc) for cc in cc_addresses]
    
    if reply_to_email:
        message.reply_to = ReplyTo(reply_to_email)

    if files:
        attachments = []
        for file in files:
            try:
                file_content = await file.read()  
                encoded_file = base64.b64encode(file_content).decode()  
                
                attachment = Attachment(
                    FileContent(encoded_file),
                    FileName(file.filename),
                    FileType(file.content_type or "application/octet-stream"),
                    Disposition("attachment")
                )
                attachments.append(attachment)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {str(e)}")

        message.attachment = attachments  

    try:
        sg = sendgrid.SendGridAPIClient(api_key)
        response = sg.send(message)

        if response.status_code == 202:
            return {"status": status.HTTP_200_OK, "message": "Email sent successfully!", "response":response}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Unexpected error: {response.body}")
        
    except UnauthorizedError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key. Please check your credentials.")

    except ForbiddenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid sender email. Please verify your 'from_email' in SendGrid settings.")

    except HTTPError as e:
        raise HTTPException(status_code=e.status_code, detail=f"HTTP error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


def parse_recipient_list(to_email: List[str]) -> List[str]:
    if not to_email or to_email == [''] or to_email[0].strip().replace(',', '') == '':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Minimum one recipient required.")
    return to_email[0].split(",")


def validate_sender_email(from_email: EmailStr):
    if from_email != os.getenv("FROM_ADDRESS"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The from address is not authorized.")


def get_user_domain(email_id: str) -> str:
    domain = regexh.get_domain_from_email(email=email_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Invalid domain.")
    return domain


def fetch_job_recruiter_company_info(session: Session, job_code: str, email_id: str):
    job = Job.get_by_code(session=session, code=job_code)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated job not found.")
    
    domain = get_user_domain(email_id=email_id)
    company_details = Company.get_by_domain(session=session, domain=domain)
    if not company_details:
        raise HTTPException(status_code=404, detail="Company details not found.")
    
    recruiter = Recruiter.get_by_email_id(session, email_id)
    if not recruiter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recruiter not found.")
    
    return job, recruiter, company_details,


def process_emails(session, to_email, from_email, body, subject, files, company_details, job, recruiter):
    email_results, failed_emails = [], []
    reply_to_email = "no-reply@symphonize.ai"
    
    for email in to_email:
        try:
            if "@" not in email:
                failed_emails.append({"email": email, "error": "Invalid email format"})
                continue
            
            email_body, email_subject = render_email_variables(
                session=session, to_email=email, body=body, subject=subject, 
                company=company_details, job=job, recuriter=recruiter
            )
            
            result = send_email(
                subject=email_subject, body=email_body, to_email=email.lower(), 
                from_email=from_email.lower(), reply_to_email=reply_to_email, attachments=files
            )
            
            if result:
                email_results.append({"email": email, "status": "success"})
        except Exception as e:
            failed_emails.append({"email": email, "error": str(e)})
            session.rollback()
    
    return email_results, failed_emails


async def validate_sender_for_email_integrations(from_email: str, api_key: str, service_type: str):
    if service_type == 'brevo':
        senders = await get_brevo_senders(api_key)
        if from_email.lower() not in senders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="The sender email or from address is not authorized in the Brevo account."
            )
        return
    if service_type == 'sendgrid':
        senders = await get_sendgrid_senders(api_key)
        if from_email.lower() not in senders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The sender email or from address is not authorized in the sendgrid account."
            )
    

def update_send_email_count(session, company_id: int, success_count: int):
    template = temp.Template.get_by_company_id(session=session, id=company_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
    
    template.email_data.update({
        "id": template.email_data.get("id"),
        "send_count": template.email_data.get("send_count", 0) + success_count
    })
    template.update(session=session)


def generate_response(email_results, failed_emails):
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