import math
import os, datetime, uuid, traceback
from uuid import UUID
from urllib.parse import quote

from app.helpers.math_helper import get_pagination
from app.models.template import Template
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.models.job import Job
from app.api.v1.endpoints.models.applicant_model import FeedbackPayload, FilterRequest, ShareRequest
from app.services.applicants import construct_query
from app.db.session import get_db
from app.models.applicant import Applicant
from app.api.v1.endpoints.applicants import PERSIMMON_DATA_BUCKET
from app.models.shared import Shared
from app.models.company import Company
from app.models.recruiter import Recruiter
from app.helpers import (
    solr_helper as solrh,
    gcp_helper as gcph,
    date_helper as dateh,
    share_applicants_helper as share_app_h,
    email_helper as emailh,
    regex_helper as regexh,
)
from app.helpers.firebase_helper import verify_firebase_token

APPLICANT_NOT_FOUND = "Applicant not found"
AUTHORIZED_SENDER = os.getenv("FROM_ADDRESS")
PERSIMMON_IMAGES_BUCKET = os.getenv("PERSIMMON_IMAGES_BUCKET")

router = APIRouter()

@router.post("/applicants")
async def share_applicant(
    data: ShareRequest,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    """Shares applicant information via email."""
    try:
        db_job, recruiter, company_details = emailh.fetch_job_recruiter_company_info(
            session=session, job_code=data.job_code, email_id=token["email"]
        )
        share_app_h.validate_applicants(session, db_job.id, data.applicant_uuids)
        share_app_h.validate_sender(data.email_type, data.sender)

        token_uuid = str(uuid.uuid4())
        share_app_h.create_shared_record(session, token["email"], token_uuid, data.applicant_uuids)
        
        payload = share_app_h.generate_payload(db_job, token["email"], data, token_uuid)
        
        success_emails, failed_emails = await share_app_h.dispatch_applicant_emails(session, data, payload, company_details, recruiter)
        
        if data.email_type == 'default':
            emailh.update_send_email_count(session, company_details.id, len(success_emails))
        
        return emailh.generate_response(success_emails, failed_emails)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to Share Applicants: {e}")
    

@router.get("/applicants/details")
def verify_email(
    decoded_data: dict = Depends(share_app_h.get_current_user),
    session: Session = Depends(get_db)
):
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
    try:
        page_size = 20
        final_query,exclude_query = construct_query(request)
        show_ai_results = False

        # Query Solr with filters
        query_parts = []
        matching_query = None
        non_matching_query = None
        no_matched_documents = []
        matched_documents = []

        share_applicants: Shared = Shared.get_by_uuid(session=session, uuid=decoded_data['token_uuid'])
        print("share applicants : ", share_applicants)
        query = 'applicant_uuid:("' + '" OR "'.join(share_applicants.details) + '")'

        matching_query = f"{query}" if show_ai_results and final_query is None else f"({query}) AND ({final_query})"
        print("matching query : ", matching_query)
        match_records = await solrh.query_solr_with_filters(query=matching_query,exclude=exclude_query)
        if match_records:
            total_matched_documents = match_records.get("response", {}).get("numFound", 0)
        matched_documents = match_records.get("response", {}).get("docs", [])
 
        N = total_matched_documents
        for i,document in enumerate(matched_documents):
            document["score"] = round(document["score"])

        # if final_query:
        #     non_matching_query = f"{query}" if show_ai_results and final_query is None else f"({query}) AND NOT({final_query})"
        #     no_match_records = await solrh.query_solr_with_filters(query=non_matching_query,exclude=exclude_query)
        #     no_matched_documents = no_match_records.get("response", {}).get("docs", [])
        #     for i,document in enumerate(no_matched_documents):
        #         document["score"] = round(document["score"])
        #     print("non_matching_query : ", non_matching_query)
        
        combined_documents = matched_documents + no_matched_documents
        if show_ai_results:
            combined_documents.sort(key=lambda x: x["persimmon_score"], reverse=True)
            ai_results = combined_documents[:10]

            #calculate the rank of the ai_results
            for i,document in enumerate(ai_results):
                document["rank"] = i + 1

            return {
            "solr_response": ai_results,
            "pagination": {
                'total_pages': 0,
                'total_count': len(ai_results)
            }
        }

        total_count = len(combined_documents)

        #compute ranks 
        for i,document in enumerate(combined_documents):
            document["rank"] = i + 1
        
        # Pagination setup
        pagination = get_pagination(page=page, page_size=page_size, total_records=total_count)
        start_index = pagination['offset']
        end_index = start_index + page_size
        paginated_records = combined_documents[start_index:end_index]

        # Return the response from Solr
        return {
            "solr_response": paginated_records,
            "pagination": {
                'total_pages': pagination['total_pages'],
                'total_count': total_count
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/applicants/{uuid}")
async def get_applicant(
    uuid: UUID,
    session: Session = Depends(get_db),
    decoded_data: dict = Depends(share_app_h.get_current_user),
):
    try:
        applicant_exists: Applicant = Applicant.get_by_uuid(session=session, uuid=str(uuid))
        if not applicant_exists:
            raise HTTPException(status_code=404, detail=APPLICANT_NOT_FOUND)
        
        applicant_exists.details['applied_date'] = dateh.convert_epoch_to_utc(
            applicant_exists.meta["audit"]["created_at"]
        )

        if decoded_data['hs']:
            applicant_exists.details['current_ctc'] = None
            applicant_exists.details['expected_ctc'] = None

        feedback = next(
            (fb for fb in applicant_exists.feedback if fb['given_by'] == decoded_data['re']),
            None
        ) if applicant_exists.feedback else None

        image_url = None
        if applicant_exists.details['applicant_image']:
            logo_file_path: str = applicant_exists.details['applicant_image'].replace(
                f'/{PERSIMMON_IMAGES_BUCKET}/', ''
            )
            image_url: str = gcph.generate_signed_url(
                f"{PERSIMMON_IMAGES_BUCKET}",file_name=logo_file_path
            )

        return {
            "message": "Applicant details retrieved successfully",
            "status": 200,
            "data": {
                "details": applicant_exists.details,
                "image_url":  image_url ,
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
            raise HTTPException(status_code=404, detail=APPLICANT_NOT_FOUND)
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
            raise HTTPException(status_code=404, detail=APPLICANT_NOT_FOUND)

            
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
