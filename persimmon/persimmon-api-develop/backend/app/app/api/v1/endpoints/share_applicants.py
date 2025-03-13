import os
import datetime
import uuid
from typing import Optional
from uuid import UUID
from urllib.parse import quote

import jwt

from fastapi import APIRouter, Depends, HTTPException, Header

from sqlalchemy.orm import Session

from app.helpers import email_helper as emailh
from app.helpers import solr_helper as solrh, regex_helper as regexh, gcp_helper as gcph, date_helper as dateh
from app.models.company import Company
from app.models.integration import Integration
from app.models.job import Job
from app.api.v1.endpoints.models.applicant_model import FilterRequest, ShareRequest
from app.services.applicants import construct_query
from app.db.session import get_db
from app.helpers.firebase_helper import verify_firebase_token
from app.models.applicant import Applicant
from app.api.v1.endpoints.applicants import PERSIMMON_DATA_BUCKET
from app.models.shared import Shared

router = APIRouter()

# Secret key for signing JWT
# python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.getenv("SECRET_KEY")

@router.post("/applicants")
def share_applicant(
    data: ShareRequest,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
    ):
    email = token['email']
    token_uuid: str = str(uuid.uuid4())
    payload = {
        "jc": data.job_code,       
        "jt": data.job_title, 
        "se": email,
        "re": data.recipient_email,
        "token_uuid": token_uuid, 
        "count": len(data.applicant_uuids),
        "hs": 1 if data.hide_salary else 0,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7) 
    }
    try:
        share_applicants = Shared(uuid = token_uuid, details = data.applicant_uuids)
        share_applicants.create(session=session, created_by=email)

        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        shareable_link = f"http://localhost:8080/api/v1/share/verify-applicant?token={jwt_token}"
        reply_to = "no-reply@symphonize.ai"
        name = data.email_type
        if name == 'default':
            if data.sender != os.getenv("FROM_ADDRESS"):
                raise ValueError("The sender address is not authorized")
            emailh.send_email(
                subject = f"Applicants for {data.job_title}", 
                body = f"<p>open the link {shareable_link}</p>",
                to_email = data.recipient_email, 
                from_email = data.sender, 
                reply_to_email = reply_to
            )
            return {"status": 200, "message": "Applicants Shared Successfully"}

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
            if cred.get('service_type') == name:
                api_key = cred['api_key'] 
                break
        else:
            raise HTTPException(status_code=404, detail=f"{name} credentials not found")

        if name == 'brevo':
            emailh.brevo_send_mail(
                api_key=api_key,
                from_email=data.sender,
                to_email=data.recipient_email,
                subject=f"Applicants for {data.job_title}", 
                body= f"<p>open the link {shareable_link}</p>",
            )
            return {"status": 200, "message": "Applicants Shared Successfully"}
        
        if name == 'sendgrid':
            emailh.sendgrid_send_mail(
                api_key=api_key,
                from_email=data.sender,
                to_email=data.recipient_email,
                subject=f"Applicants for {data.job_title}", 
                body= f"<p>open the link {shareable_link}</p>",
            )
            return {"status": 200, "message": "Applicants Shared Successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Share Applicants: {e}")


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        # Decode JWT
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_data  # Return decoded payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.DecodeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/applicants/details")
def verify_email(
    decoded_data: dict = Depends(get_current_user),
    session: Session = Depends(get_db)
):

    # if decoded_data["re"] != request.email:
    #     raise HTTPException(status_code=403, detail="Unauthorized access")

    db_job = Job.get_by_code(session=session, code=decoded_data['jc'])

    details = {
        "job_code": decoded_data['jc'], 
        "job_title": decoded_data['jt'],
        "sender": decoded_data['se'],
        "recipient_email": decoded_data['re'],
        "count": decoded_data["count"],
        "hide_salary": True if decoded_data['hs'] else False,
        "enhanced_description": db_job.enhanced_description
    }
    return {"message": "Access granted", "details": details}


@router.post("/applicants/filter")
async def get_applicants(
    request: FilterRequest,
    decoded_data: dict = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    print("token_uuid : ",decoded_data['token_uuid'])
    share_applicants: Shared = Shared.get_by_uuid(session=session, uuid=decoded_data['token_uuid'])
    print("share applicants : ", share_applicants)
    query = 'applicant_uuid:("' + '" OR "'.join(share_applicants.details) + '")'

    final_query, exclude_query = construct_query(request)
    solr_response_with_filters = await solrh.query_solr_with_filters(query=query, filters=final_query, rows=len(share_applicants.details),start=0)
    
    return {
        "solr_response": solr_response_with_filters,
    }


@router.get("/applicants/{uuid}")
async def get_applicant(
    uuid: str,
    session: Session = Depends(get_db),
    decoded_data: dict = Depends(get_current_user),
):
    try:
        try:
            uuid_obj = UUID(uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid or Required UUID")
        applicant_exists: Applicant = Applicant.get_by_uuid(session=session, uuid=uuid)
        applicant_exists.details['applied_date'] = dateh.convert_epoch_to_utc(applicant_exists.meta["audit"]["created_at"])
        if not applicant_exists:
            raise HTTPException(status_code=404, detail="Applicant not found")
        return {
            "message": "Applicant details retrieved successfully",
            "status": 200,
            "data": {
                "details": applicant_exists.details,
                "stage_uuid": applicant_exists.stage_uuid,
                "job_id": applicant_exists.job_id,
                "uuid": applicant_exists.uuid
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/applicants/{uuid}/resume")
def get_resume(
    uuid: str,
    action: str = "view",
    session: Session = Depends(get_db),
    decoded_data: dict = Depends(get_current_user),
):
    """Retrieve a PDF file from GCP and send it back to the client."""
    try:
        try:
            uuid_obj = UUID(uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid or Required UUID")
        applicant_exists: Applicant = Applicant.get_by_uuid(session=session, uuid=uuid)
        if not applicant_exists:
            raise HTTPException(status_code=404, detail="Applicant not found")
        file_path = applicant_exists.details["original_resume"].replace(f'/{PERSIMMON_DATA_BUCKET}/', '')
        full_name = applicant_exists.details["personal_information"]["full_name"].replace(' ','_')
        download_filename = quote(f"Persimmon_{full_name}_Resume.pdf")
        return gcph.retrieve_from_gcp(bucket_name=PERSIMMON_DATA_BUCKET, file_path=file_path, download_filename=download_filename, action=action)
    
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))