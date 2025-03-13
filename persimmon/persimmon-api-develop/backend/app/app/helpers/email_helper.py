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
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

from app.api.v1.endpoints.models.resume_model import EmailTemplate
from app.models.company import Company
from app.models.job import Job
from app.models.recruiter import Recruiter
from app.models.applicant import Applicant



def send_email(subject: str, body: str, to_email: EmailStr, from_email: EmailStr, reply_to_email: EmailStr, attachments: Optional[List[UploadFile]]=None):
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
            server.sendmail(from_email, to_email, msg.as_string())  # Send the email
            print(f"Email sent successfully to {to_email}!")
            return f"Email sent successfully to {to_email}!"
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
        "RecruiterContactNumber": recuriter.whatsapp_number
    }
    
    subject_template_date = {
        "JobTitle": job.title,
        "CompanyName" : company.name
    }

    body = Template(body).render(body_template_data)
    subject = Template(subject).render(subject_template_date)
    
    return (body, subject)


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


async def brevo_send_mail(api_key: str, from_email: str, to_email: str, subject: str, body: str, files: List[UploadFile] = None):
    """Send email via Brevo with form data and multiple file attachments."""

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    email_data = sib_api_v3_sdk.SendSmtpEmail(
        sender={"email": from_email},
        to=[{"email": to_email}],
        subject=subject,
        html_content=body
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


async def sendgrid_send_mail(api_key: str, from_email: str, to_email: str, subject: str, body: str, files: List[UploadFile] = None):
    """Send an email via SendGrid with optional file attachments."""

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=body
    )

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


# # Example usage
# if __name__ == "__main__":
#     recipients = ['gvkartheek9@gmail.com', 'gundacharanreddy7@gmail.com']
#     subject = "Test Email with Template and Attachment"
#     template_path = """
# <html>
#   <body>
#     <h1>Hello {{ name }}</h1>
#     <p>{{ message }}</p>
#   </body>
# </html>

# """
    
#     template_data = {
#         "name": "User",
#         "message": "This is a test email sent using Python and Sendinblue."
#     }
#     from_email = "careers@tekworks.ai"
#     reply_to_email = "xyzabc@symphonize.ai"
#     attachment_path = "C:/Users/kartheek/persimmon-email/persimmon-xp/email/MOHDAZHER[3y_8m].pdf"  # Path to the attachment file

#     for recipient in recipients:
#         send_email(subject, template_path, template_data, recipient, from_email, reply_to_email, attachment_path)

