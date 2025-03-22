import math
import os, datetime, uuid, traceback
from uuid import UUID
from urllib.parse import quote

from app.helpers.math_helper import get_pagination
from app.models.template import Template
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.helpers import solr_helper as solrh, gcp_helper as gcph, date_helper as dateh
from app.helpers import share_applicants_helper as share_app_h
from app.models.job import Job
from app.api.v1.endpoints.models.applicant_model import FeedbackPayload, FilterRequest, ShareRequest
from app.services.applicants import construct_query
from app.db.session import get_db
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers import regex_helper as regexh
from app.models.applicant import Applicant
from app.api.v1.endpoints.applicants import PERSIMMON_DATA_BUCKET
from app.models.shared import Shared
from app.models.company import Company
from app.models.recruiter import Recruiter

AUTHORIZED_SENDER = os.getenv("FROM_ADDRESS")

router = APIRouter()

@router.post("/applicants")
async def share_applicant(
    data: ShareRequest,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    """Shares applicant information via email."""
    try:
        db_job: Job = Job.get_by_code(session=session, code=data.job_code)
        if not db_job:
            raise HTTPException(status_code=404, detail="Job not found.")

        missing_applicants: list = Applicant.get_missing_applicants(session=session, job_id=db_job.id, applicant_uuids=data.applicant_uuids)
        if missing_applicants:
            raise HTTPException(status_code=404, detail=f"Applicants not found: {missing_applicants}")
        
        if data.email_type == "default" and data.sender != AUTHORIZED_SENDER:
            raise ValueError("The sender address is not authorized")
        
        domain = regexh.get_domain_from_email(email=token['email'])
        company_details = Company.get_by_domain(session=session, domain=domain)
        if not company_details:
            raise HTTPException(status_code=404,detail="Company details not found")
        
        recuriter: Recruiter = Recruiter.get_by_email_id(session, token['email'])
        if not recuriter:
            raise HTTPException(status_code=404, detail="Associated recuriter not found")

        token_uuid: str = str(uuid.uuid4())
        shared_applicants = Shared(uuid=token_uuid, details=data.applicant_uuids)
        shared_applicants.create(session=session, created_by=token["email"])

        payload = {
            "jc": data.job_code,
            "jt": db_job.title,
            "se": token["email"],
            "token_uuid": token_uuid,
            "count": len(data.applicant_uuids),
            "hs": 1 if data.hide_salary else 0,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
        }

        success_emails = []
        failed_emails = []

        api_key = None
        if data.email_type != "default":
            api_key = share_app_h.get_api_key(session=session, email=token["email"], service_type=data.email_type)

        body_template_data = {
            "CompanyName": company_details.name,
            "JobTitle": db_job.title,
            "RecruiterName": recuriter.full_name,
            "Designation": recuriter.designation,
        }

        for recipient_email in data.recipient_emails:
            payload["re"] = recipient_email
            body_template_data['Link'] = share_app_h.generate_shareable_link(payload, data.redirect_url)
            subject, body = share_app_h.get_share_applicants_email_templates(body_template_data)
            email_result = await share_app_h.share_applicants_send_email(
                email_service=data.email_type,
                api_key=api_key,
                sender=data.sender,
                recipient=recipient_email,
                subject=subject,
                body=body,
            )
            if email_result["status"] == "success":
                success_emails.append(email_result)
            else:
                failed_emails.append(email_result)

        if data.email_type == 'default':
            template:Template = Template.get_by_company_id(session=session, id=company_details.id)
            if not template:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
            template.email_data.update({
                "id": template.email_data.get("id"),
                "send_count": template.email_data.get("send_count") + len(success_emails)
            })
            template.update(session=session)

        response = {
            "message": "Shared Applicants Successfully",
            "success_count": len(success_emails),
            "failure_count": len(failed_emails),
            "successful_emails": success_emails,
            "failed_emails": failed_emails,
        }
        if failed_emails:
            response["message"] += " with some failures"
        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Share Applicants: {e}")


@router.get("/applicants/details")
def verify_email(
    decoded_data: dict = Depends(share_app_h.get_current_user),
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
    page: int,
    request: FilterRequest,
    decoded_data: dict = Depends(share_app_h.get_current_user),
    session: Session = Depends(get_db)
):
    share_applicants: Shared = Shared.get_by_uuid(session=session, uuid=decoded_data['token_uuid'])
    print("share applicants : ", share_applicants)
    query = 'applicant_uuid:("' + '" OR "'.join(share_applicants.details) + '")'

    final_query, exclude_query = construct_query(request)
    page_size = 20
    total_count = len(share_applicants.details)
    pagination = get_pagination(page=page, page_size=page_size, total_records=total_count)
    solr_response_with_filters = await solrh.query_solr_with_filters(query=query, filters=final_query, rows=page_size,start=pagination['offset'],exclude=exclude_query)
    documents = solr_response_with_filters.get("response", {}).get("docs", [])
    N = total_count
    for i,document in enumerate(documents):
        percentile = ((N-i-(pagination['offset']))/N)*100
        document["score"] = math.ceil(percentile)
        if decoded_data['hs']:
            document['current_ctc'] = None
            document['expected_ctc'] = None
    
    return {
            "solr_response": solr_response_with_filters,
            "pagination": {
                'total_pages': pagination['total_pages'],
                'total_count': total_count
            }
        }


@router.get("/applicants/{uuid}")
async def get_applicant(
    uuid: UUID,
    session: Session = Depends(get_db),
    decoded_data: dict = Depends(share_app_h.get_current_user),
):
    try:
        applicant_exists: Applicant = Applicant.get_by_uuid(session=session, uuid=str(uuid))
        if not applicant_exists:
            raise HTTPException(status_code=404, detail="Applicant not found")
        applicant_exists.details['applied_date'] = dateh.convert_epoch_to_utc(applicant_exists.meta["audit"]["created_at"])
        if decoded_data['hs']:
            applicant_exists.details['current_ctc'] = None
            applicant_exists.details['expected_ctc'] = None
        if applicant_exists.feedback:
            feedback = next((fb for fb in applicant_exists.feedback if fb['given_by'] == decoded_data['re']), None)
        else:
            feedback = None
        return {
            "message": "Applicant details retrieved successfully",
            "status": 200,
            "data": {
                "details": applicant_exists.details,
                "stage_uuid": applicant_exists.stage_uuid,
                "job_id": applicant_exists.job_id,
                "uuid": applicant_exists.uuid,
                "feedback": feedback
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/applicants/{uuid}/resume")
def get_resume(
    uuid: UUID,
    action: str = "view",
    session: Session = Depends(get_db),
    decoded_data: dict = Depends(share_app_h.get_current_user),
):
    """Retrieve a PDF file from GCP and send it back to the client."""
    try:
        applicant_exists: Applicant = Applicant.get_by_uuid(session=session, uuid=str(uuid))
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
    

@router.post("/{applicant_uuid}/feedback")
async def add_feedback(
    applicant_uuid: UUID,
    feedback: FeedbackPayload,
    session: Session = Depends(get_db),
    decoded_data: dict = Depends(share_app_h.get_current_user),
):
    """
    Add feedback for an applicant.

    Args:
        applicant_uuid (str): The applicant UUID for which feedback needs to be added.
        feedback (FeedbackPayload): The feedback details to be added.

    Returns:
        JSON response indicating success or failure.
    Raises:
        HTTPException: If the applicant is not found or invalid feedback format.
        HTTPEXception: If the feedback is already given by the recruiter.
    """
    try:
        applicant_existed: Applicant = Applicant.get_by_uuid(session=session, uuid=str(applicant_uuid))
                
        if not applicant_existed:
            raise HTTPException(status_code=404, detail="Applicant not found")

            
        feedback_dict = feedback.model_dump().get("feedback", [])

        if applicant_existed.feedback:
            for fd in applicant_existed.feedback:
                if fd.get("given_by") == feedback.feedback[0].given_by:
                    raise HTTPException(status_code=400, detail="Feedback already given by the recruiter")

            applicant_existed.feedback.append(feedback_dict[0])
            flag_modified(applicant_existed, "feedback")  # Ensure JSONB field is updated
        else:
            applicant_existed.feedback = feedback_dict

        applicant_existed.update(session=session)

        return {"status": "success", "message": "Feedback updated successfully"}

    except HTTPException:
        raise  
    except Exception as e:
        session.rollback()  
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")
