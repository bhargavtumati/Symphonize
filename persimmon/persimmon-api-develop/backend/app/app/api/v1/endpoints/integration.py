from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status, Depends

from pydantic import EmailStr

from sqlalchemy.orm import Session

from jinja2 import Template

from app.db.session import get_db
from app.models.job import Job
from app.models.company import Company
from app.models.integration import Integration
from app.models.recruiter import Recruiter
from app.helpers import db_helper as dbh, regex_helper as regexh, zoom_helper as zoomh
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers import email_helper as emailh
from app.api.v1.endpoints.models.integration_model import IntegrationModel, APIKeyModel

router = APIRouter()

@router.post('/{name}')
def create_integration(
    name: str,
    request: IntegrationModel,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    try:
        email = token['email']
        domain = regexh.get_domain_from_email(email=email)

        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session,domain=domain)
        integration: Integration = Integration.get_credentials(session=session,company_id=company_details.id,platform_name=name)

        if request.code:
            response = zoomh.get_access_token(request.client_id,request.client_secret,request.code,request.redirect_uri)

        expires_in = datetime.utcnow() + timedelta(seconds=response.get('expires_in'))
        expires_in = expires_in.isoformat()
        credentials = {
            "client_id": request.client_id,
            "client_secret": request.client_secret,
            "redirect_uri": request.redirect_uri,
            "refresh_token": response.get('refresh_token'),
            "access_token": response.get('access_token'),
            "expires_in": expires_in
        }

        if integration:
            integration.credentials.update(credentials)
            integration.meta.update(dbh.update_meta(meta=integration.meta, email=email))
            integration.update(session=session)
        else:
            integration = Integration(
                type=name,
                credentials=credentials,
                company_id=company_details.id
            )
            integration.create(session=session,created_by=email)

        return {
            "status": status.HTTP_201_CREATED,
            "message": "Zoom integration is successful"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.get('/{name}/users')
def get_zoom_account_users(
    name: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token['email']
        domain = regexh.get_domain_from_email(email=email)

        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session,domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail="Company details not found")

        integration: Integration = Integration.get_credentials(session=session,company_id=company_details.id,platform_name=name)
        if not integration:
            raise HTTPException(status_code=404,detail="Integration details not found")
            
        response = zoomh.validate_access_token(credentials=integration.credentials,integration=integration,email=email,session=session)
        response = zoomh.get_users(token=response.get("access_token"))
        return {
            "status": status.HTTP_200_OK,
            "message": "Retrieved zoom account users successfully",
            "data": response
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.get('/{name}/user')
def get_zoom_account_user(
    name: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token['email']
        domain = regexh.get_domain_from_email(email=email)

        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session,domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail="Company details not found")

        integration: Integration = Integration.get_credentials(session=session,company_id=company_details.id,platform_name=name)
        if not integration:
            raise HTTPException(status_code=404,detail="Integration details not found")
            
        response = zoomh.validate_access_token(credentials=integration.credentials,integration=integration,email=email,session=session)
        response = zoomh.get_user_by_id(token=response.get("access_token"),user_id=email)
        return {
            "status": status.HTTP_200_OK,
            "message": "Retrieved zoom account user data successfully",
            "data": response
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.get('/{name}/verify-status')
def verify_integration_status(
    name: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token['email']
        domain = regexh.get_domain_from_email(email=email)
        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session,domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail="Company details not found")

        integration: Integration = Integration.get_credentials(session=session,company_id=company_details.id,platform_name=name)
        if integration:
            return True
        else:
            return False
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@router.post('/email/{name}')
async def create_email_integration(
    name: str,
    request: APIKeyModel,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):   
    try:
        email = token['email']
        domain = regexh.get_domain_from_email(email=email)

        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")
        
        name = name.lower().strip()
        
        if name == 'brevo':
            await emailh.get_brevo_senders(api_key = request.api_key)
        elif name == 'sendgrid':
            await emailh.get_sendgrid_senders(api_key = request.api_key)

        company_details = Company.get_by_domain(session=session, domain=domain)
        integration: Integration = Integration.get_credentials(session=session, company_id=company_details.id, platform_name='email')
        
        if integration:
            credentials = integration.credentials
            for cred in credentials.get('credentials'):
                if cred.get('service_type') == name:
                    cred['api_key'] = request.api_key
                    break
            else:
                service_details = {
                    "service_type": name,
                    "api_key" : request.api_key
                }
                credentials.get('credentials').append(service_details)
                
            integration.credentials.update(credentials)
            integration.meta.update(dbh.update_meta(meta=integration.meta, email=email))
            integration.update(session=session)
        
        else:
            service_credentials = {
                "credentials" : [
                    {
                        "service_type" : name,
                        "api_key" : request.api_key
                    }
                ]
            }
            integration = Integration(
                type = 'email',
                credentials = service_credentials,
                company_id = company_details.id
            )
            integration.create(session=session,created_by=email)

        return {
            "status": status.HTTP_201_CREATED,
            "message": "Email integration is successful"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@router.get('/email/{name}/senders')
async def get_email_senders(
    name: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token['email']
        domain = regexh.get_domain_from_email(email=email)

        if not domain:
            raise HTTPException(status_code=404, detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session, domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail="Company details not found")

        integration: Integration = Integration.get_credentials(session=session, company_id=company_details.id, platform_name='email')
        if not integration:
            raise HTTPException(status_code=404,detail="Email Integration details not found")
        
        name = name.lower().strip()
        credentials = integration.credentials
        for cred in credentials.get('credentials'):
            if cred.get('service_type') == name:
                api_key = cred['api_key'] 
                break
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} credentials not found")

        if name == 'brevo':
            senders = await emailh.get_brevo_senders(api_key = api_key)
        elif name == 'sendgrid':
            senders = await emailh.get_sendgrid_senders(api_key = api_key)

        return {
            "status": status.HTTP_200_OK,
            "message": f"Retrieved {name} account senders successfully",
            "data": senders
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@router.post("/email/{name}/send")
async def send_email_user(
    name: str,
    job_code: str = Form(...),
    to_email: List[str] = Form(...),
    from_email: EmailStr = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    to_email = to_email[0].split(",")
    email_results = []
    failed_emails = []
    
    try:
        domain = regexh.get_domain_from_email(email=token['email'])
        if not domain:
            raise HTTPException(status_code=404, detail="Domain is invalid")
        
        if not to_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient email is required")
        
        company_details = Company.get_by_domain(session=session, domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail="Company details not found")
        
        job: Job = Job.get_by_code(session=session, code=job_code)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated job not found")
        
        recruiter: Recruiter = Recruiter.get_by_email_id(session, token['email'])
        if not recruiter:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated recuriter not found")

        integration: Integration = Integration.get_credentials(session=session, company_id=company_details.id, platform_name='email')
        if not integration:
            raise HTTPException(status_code=404,detail="Email Integration details not found")
        
        name = name.lower().strip()
        credentials = integration.credentials
        for cred in credentials.get('credentials'):
            if cred.get('service_type') == name:
                api_key = cred['api_key'] 
                break
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} credentials not found")

        for email in to_email:
            try:
                email_body, email_subject = emailh.render_email_variables(session=session, to_email=email, body=body, subject=subject, company=company_details, job=job, recuriter=recruiter)
                if name == 'brevo':
                    response = await emailh.brevo_send_mail(api_key=api_key, from_email=from_email, to_email=email, subject=email_subject, body=email_body, files=files)
                elif name == 'sendgrid':
                    response = await emailh.sendgrid_send_mail(api_key=api_key, from_email=from_email, to_email=email, subject=email_subject, body=email_body, files=files)

                email_results.append({"email": email, "status": "success"})

            except HTTPException as e:
                failed_emails.append({"email": email, "error": str(e.detail)})
            except Exception as e:
                failed_emails.append({"email": email, "error": str(e)})

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

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error occurred")
    finally:
        if files:
            for file in files:
                await file.close()


@router.post("/email/{name}/test-email")
async def send_test_email(
    name: str,
    to_email: EmailStr = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    from_email: EmailStr = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    token : dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    email_results = []
    failed_emails = []
    try:
        email = token['email']
        domain = regexh.get_domain_from_email(email=email)

        if not domain:
            raise HTTPException(status_code=404, detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session, domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail="Company details not found")

        integration: Integration = Integration.get_credentials(session=session, company_id=company_details.id, platform_name='email')
        if not integration:
            raise HTTPException(status_code=404,detail="Email Integration details not found")
        
        name = name.lower().strip()
        credentials = integration.credentials
        for cred in credentials.get('credentials'):
            if cred.get('service_type') == name:
                api_key = cred['api_key'] 
                break
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} credentials not found")
        
        try:
            if name == 'brevo':
                response = await emailh.brevo_send_mail(api_key=api_key, from_email=from_email, to_email=to_email, subject=subject, body=body, files=files)
            elif name == 'sendgrid':
                response = await emailh.sendgrid_send_mail(api_key=api_key, from_email=from_email, to_email=to_email, subject=subject, body=body, files=files)

            if response: 
                email_results.append({"email": to_email, "status": "success"}) #"response":response['response']
        except HTTPException as e:
            failed_emails.append({"email": to_email, "error": str(e.detail)})

        except Exception as e:
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error sending email : {str(e)}")