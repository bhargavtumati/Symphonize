import asyncio
import logging
import os
import re
import traceback
import uuid
from typing import List, Optional
from uuid import UUID
from app.models.company import Company
from fastapi.responses import JSONResponse
import httpx
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status,BackgroundTasks
from pydantic import ValidationError, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.api.v1.endpoints.models.applicant_model import (ApplicantDetailsPartialUpdate, 
                        ApplicantPartialUpdate, ApplicantRequest, FilterRequest,
                        OpinionEnum,ApplicantModel, MeetingModel,
                        FeedbackPayload, FeedbackPromptRequest)

from app.db.session import get_db

from app.helpers import (db_helper as dbh, gcp_helper as gcph, solr_helper as solrh, 
                        date_helper as dateh,zoom_helper as zoomh, regex_helper as regexh, 
                        email_helper as emailh,data_helper as datah, pdf_helper as pdfh,
                        import_resumes_helper as imph, match_score_helper as matchh, google_meet_helper as gmeeth)

from app.helpers.firebase_helper import verify_firebase_token
from app.helpers.log_helper import log_execution_time
from app.helpers.otlpless_helper import verify_otpless_token
from app.helpers.math_helper import get_pagination
from app.models.applicant import Applicant, InterviewType
from app.models.job import Job
from app.models.stages import Stages
from app.models.integration import Integration
from app.models.template import Template
from app.services import applicants as ap
from urllib.parse import quote
from datetime import datetime
import app.helpers.image_helper as imageh

load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("DatabaseUploader")

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

SCHEDULED_INTERVIEW = "Scheduled an Interview"
APPLICANT_NOT_FOUND = "Applicant not found"
SOLR_BASE_URL=os.getenv("SOLR_BASE_URL")
PERSIMMON_DATA_BUCKET=os.getenv("PERSIMMON_DATA_BUCKET")
PERSIMMON_IMAGES_BUCKET = os.getenv("PERSIMMON_IMAGES_BUCKET")

@router.post("/upload-resume/")
@log_execution_time
async def upload_resumes(
    background_tasks: BackgroundTasks ,
    job_code: str,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token),
):
    created_by = token['email']
    allowed_extensions = {"pdf", "docx"}
    success_files = []
    errors = []
    duplicates = []
    results_to_process = []
    paths = []

    # Step 1: Validate job
    job = Job.get_by_code(session=session, code=job_code)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_id = job.id
    job_description = job.description

    # Step 2: Validate extensions
    valid_files = [file for file in files if file.filename.split('.')[-1].lower() in allowed_extensions]
    if not valid_files:
        raise HTTPException(status_code=400, detail="No valid files found")

    # Step 3: Process uploads only (no JSON/LLM here)
    for file in valid_files:
        try:
            text = await pdfh.extract_text_from_file(file)
            if not text:
                raise Exception(f"Text extraction failed: {file.filename}")

            # Check duplicates
            mobile_matches = re.findall(r"(?:\+\d{1,3}[-.\s]?)?\d{10}", text)
            email_matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

            mobile_exists = None
            email_exists = None
            if mobile_matches:
                mobile_exists = await Applicant.get_by_mobile_number(session, mobile_matches[0], job_id)
            if email_matches:
                email_exists = await Applicant.get_by_email_id(session, email_matches[0], job_id)

            if mobile_exists or email_exists:
                duplicates.append(f"Duplicate detected: {file.filename}")
                continue

            file_upload = await imph.upload_resumes(job_code, file, session, created_by)
            path = file_upload['uploaded_files'][0]
            paths.append(path)
            applicant_uuid = file_upload['applicant_uuid']

            # ✅ Save this for background processing
            results_to_process.append({
                "text": text,
                "path": path,
                "uuid": applicant_uuid
            })

            success_files.append(file.filename)

        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    # Step 4: Run async processing in background (concurrent)
    if results_to_process:
        background_tasks.add_task(imph.run_resume_processing_tasks, results_to_process, created_by, job_description)

    return {
        "status": "success" if not errors and not duplicates else "partial success",
        "uploaded_files": paths,
        "duplicates": duplicates,
        "errors": errors,
        "total_files": len(files)
    }


@router.patch("")
async def partial_update(
    job_id: int,
    applicants: ApplicantPartialUpdate,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    try:
        updated_by = token['email']
        db_job = Job.get_by_id(session = session, id = job_id, email = updated_by)

        if not db_job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Job not found")

        applicant_uuids = [str(uuid) for uuid in applicants.applicant_uuids]
        stage_uuid = str(applicants.stage_uuid)
        stage_name = ''
        if len(applicant_uuids) > 0:
            recruiter_job_stages = Stages.get_by_id(session=session, job_id=job_id)
            if not recruiter_job_stages:
                raise HTTPException(status_code=404, detail='Recruiter job stages not found')

            for stage in recruiter_job_stages.stages:
                if stage['uuid'] == stage_uuid:
                    stage_name = stage['name']

            if stage_name == "new":
                raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND,
                    detail = "Once an applicant is moved to any other stage, they should not be allowed to move back to the new stage"
                )
            
            stage_uuids = [stage['uuid'] for stage in recruiter_job_stages.stages]
            if stage_uuid not in stage_uuids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage uuid")

            await solrh.update_solr_documents_partially(uuids=applicant_uuids,set_uuid=stage_uuid,search_category="applicant_uuid")
                
            for applicant_uuid in applicant_uuids:
                existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=str(applicant_uuid))
                if not existing_applicant:
                    raise HTTPException(status_code=404, detail=f'Applicant with an uuid {str(applicant_uuid)} was not found')

                existing_applicant.stage_uuid = stage_uuid
                existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
                existing_applicant.update(session=session)

        return {
            "message": f'Successfully moved to {stage_name}',
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Solr: {str(e)}")

@router.post("/filter")
async def get_applicants_filter(
    job_code: str,
    page: int,
    request: Optional[FilterRequest] ,
    stage_uuid: Optional[UUID] = None,
    name: Optional[str] = None,
    show_ai_results: Optional[bool] = False,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    try:
        db_job = Job.get_by_code(
            session = session, 
            code = job_code
        )

        if not db_job:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "Please enter valid Job code"
            )

        # Pagination setup
        page_size = 20
        final_query,exclude_query = ap.construct_query(request)

        # Query Solr with filters
        query_parts = []
        matching_query = None
        non_matching_query = None
        no_matched_documents = []
        matched_documents = []

        if job_code:
            query_parts.append(f"job_code:\"{job_code}\"")
        if stage_uuid:
            query_parts.append(f"stage_uuid:\"{stage_uuid}\"")
        if name:
            query_parts.append(f"full_name:{name}*")
        query = " AND ".join(query_parts)  # Combine query parts with AND

        matching_query = f"{query}" if show_ai_results and final_query is None else f"({query}) AND ({final_query})"
        match_records = await solrh.query_solr_with_filters(query=matching_query,exclude=exclude_query)
        if match_records:
            total_matched_documents = match_records.get("response", {}).get("numFound", 0)
        matched_documents = match_records.get("response", {}).get("docs", [])
 
        N = total_matched_documents
        for i,document in enumerate(matched_documents):
            document["score"] = round(document["score"])

        if final_query:
            non_matching_query = f"{query}" if show_ai_results and final_query is None else f"({query}) AND NOT({final_query})"
            no_match_records = await solrh.query_solr_with_filters(query=non_matching_query,exclude=exclude_query)
            no_matched_documents = no_match_records.get("response", {}).get("docs", [])
            for i,document in enumerate(no_matched_documents):
                document["score"] = round(document["score"])
        
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

    

@router.get("/{uuid}")
async def get_applicant(
    uuid: UUID,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    try:
        applicant_exists: Applicant = Applicant.get_by_uuid(session=session, uuid=str(uuid))
        if not applicant_exists:
            raise HTTPException(status_code=404, detail=APPLICANT_NOT_FOUND)
        applicant_exists.details['applied_date'] = dateh.convert_epoch_to_utc(applicant_exists.meta["audit"]["created_at"])

        total_skills = 0
        total_communication = 0
        total_professionalism = 0
        total_likes = 0
        total_dislikes = 0
        total_num_of_reviews = 0
        avg_skills ,avg_communication,avg_professionalism,total_avg= 0,0,0,0
        image_url = None
         
        if  applicant_exists.feedback:
            for feedback in applicant_exists.feedback:
                total_skills += feedback['rating']["skill"]
                total_professionalism += feedback['rating']["professionalism"]
                total_communication += feedback['rating']["communication"]
                opinion = feedback.get("opinion",[])
                if opinion == OpinionEnum.LIKE:
                    total_likes += 1
                elif opinion == OpinionEnum.DISLIKE:
                    total_dislikes += 1

                total_num_of_reviews += 1

                avg_communication = round(total_communication/total_num_of_reviews,1)
                avg_skills = round(total_skills/total_num_of_reviews,1)
                avg_professionalism = round(total_professionalism/total_num_of_reviews,1)

                total_avg = round((total_communication+total_skills+total_professionalism)/total_num_of_reviews,1)

        if applicant_exists.details['applicant_image']:
            applicant_image_file_path = applicant_exists.details['applicant_image']
            image_url = await imageh.get_base64_image(file_path=applicant_image_file_path)

        return {
            "message": "Applicant details retrieved successfully",
            "status": status.HTTP_200_OK,
            "data": {
                "details": applicant_exists.details,
                "image_url": image_url,
                "stage_uuid": applicant_exists.stage_uuid,
                "job_id": applicant_exists.job_id,
                "uuid": applicant_exists.uuid,
                "feedback": applicant_exists.feedback if applicant_exists.feedback else [],
                "total_skills": total_skills,
                "total_communication": total_communication,
                "total_professionalism": total_professionalism, 
                "total_reviews": total_num_of_reviews, 
                "avg_skills": avg_skills,
                "avg_communication": avg_communication, 
                "avg_professionalism": avg_professionalism,
                "total_avg": total_avg,
                "total_likes": total_likes,
                "total_dislikes": total_dislikes
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{uuid}/resume")
def get_resume(
    uuid: UUID,
    action: str = "view",
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    """Retrieve a PDF file from GCP and send it back to the client."""
    try:
        applicant_exists: Applicant = Applicant.get_by_uuid(session=session, uuid=str(uuid))
        if not applicant_exists:
            raise HTTPException(status_code=404, detail=APPLICANT_NOT_FOUND)
        file_path = applicant_exists.details["original_resume"]
        full_name = applicant_exists.details["personal_information"]["full_name"].replace(' ','_')
        download_filename = quote(f"Persimmon_{full_name}_Resume.pdf")
        return gcph.retrieve_from_gcp( path_to_file=file_path, download_filename=download_filename, action=action)
    
    except HTTPException as e:
        traceback.print_exc()
        raise e

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/career-page")
async def create_applicant_in_career_page(
    job_id: int,
    job_code: str,
    phone_number: str,
    full_name: str,
    email_id: str,
    linkedin_url: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_db), 
    token: str = Depends(verify_otpless_token)  
):
    allowed_extensions = {"pdf", "docx"}  
    file_extension = file.filename.split('.')[-1].lower()

    job = Job.get_by_job_id(session=session, job_id=job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail=f"File '{file.filename}' has an unsupported file extension. Only '.pdf' and '.docx' files are allowed."
        )
    
    try:
        ApplicantModel(
            phone_number = phone_number,
            full_name = full_name,
            email_id = email_id,
            linkedin_url = linkedin_url
        )
    except ValidationError as e:
        error_messages = [
            {
                "loc"   : ["body", error["loc"][0]], 
                "msg"   : error["msg"][13:], 
                "input" : error["input"]
            } for error in e.errors()
        ]
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail = error_messages
        )
    
    file_success, error_message, flatten_resume = await ap.process_resume(
        file, session, email_id, int(job_id), job_code, phone_number, full_name, email_id, linkedin_url
    )
    
    return JSONResponse(
        content = {
            "status": "success" if not error_message else "failed",
            "message": "Job Applied successfully" if not error_message else "Failed to Apply Job",
            "success_file": file_success,
            "errors": error_message,
            "extracted_text": flatten_resume
        },
        status_code = 500 if error_message else 201
    )  

@router.post("/data-storage")
async def data_storage(
    request:ApplicantRequest, 
    job_code: str,
    session: Session = Depends(get_db),
    token : dict = Depends(verify_firebase_token)
):
    created_by=token['email'] 
    job_id = Job.get_id_by_code(session=session,code=job_code)
    if not job_id:
        raise HTTPException(status_code=404, detail=f"Job with code '{job_code}' not found.")
    applicant_uuid = str(uuid.uuid4())
    stage_uuid=""
    try:
        stages_existing: Stages = Stages.get_by_id(session=session, job_id=job_id)
        print(f"the stages_existing are {stages_existing.stages}")
        if len(stages_existing.stages) > 0:
            stage_uuid = stages_existing.stages[0]['uuid']
    except Exception as e: 
        raise HTTPException(status_code=404, detail="Stages not found")

    applicant_uuid = str(uuid.uuid4())
    applicant_data = Applicant(details=request.details, stage_uuid=stage_uuid, job_id=job_id, uuid=applicant_uuid)
    try:
        created_applicant = applicant_data.create(session=session,created_by=created_by)
        return {
            "status": 200,
            "message": "Applicant created successfully.",
            "data": created_applicant
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create applicant. Please try again. {str(e)}")

    
@router.post('/{uuid}/create-meeting')
async def create_meeting(
    uuid: UUID,
    end_time: datetime,
    from_address: EmailStr,
    interview_type: InterviewType,
    meeting_details: MeetingModel,
    user_id: Optional[str] = None,
    platform_name:Optional[str]=None,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    try:
        email = token['email']
        create_response = {
            "status": status.HTTP_201_CREATED,
            "message": "Interview scheduled successfully",
        }

        if platform_name == "undefined":
            platform_name = None

        if platform_name and platform_name not in ["zoom","google_meet","microsoft_teams"]:
            raise HTTPException(status_code=404,detail="Platform name is invalid")

        if interview_type == InterviewType.ONLINE and not platform_name:
            raise HTTPException(status_code=404,detail="Platform name query param value is required for online interview")

        domain = regexh.get_domain_from_email(email=email)
        if not domain:
            raise HTTPException(status_code=404,detail="Domain is invalid")

        company_details = Company.get_by_domain(session=session,domain=domain)

        if interview_type == InterviewType.ONLINE and platform_name == "zoom":
            integration_details: Integration = Integration.get_credentials(session=session,company_id=company_details.id,platform_name=platform_name)
            if not integration_details:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration details not found")
            credentials = integration_details.credentials

            response = zoomh.validate_access_token(credentials=credentials,integration=integration_details,email=email,session=session)

            dateh.validate_future_datetime(dt=end_time,timezone_str=meeting_details.timezone,field_name="end_time")
            dateh.validate_future_datetime(dt=meeting_details.start_time,timezone_str=meeting_details.timezone,field_name="start_time")
            duration = dateh.calculate_duration_in_minutes(start_time=meeting_details.start_time,end_time=end_time)
            meeting_details.duration = duration
            response = zoomh.create_meeting(data=meeting_details.model_dump_json(),user_id=user_id,token=response.get('access_token'))
            create_response["data"] = response

            body = f"""
            <p>Hi There!</p>
            <p>Here is the meeting invite link {response['join_url']}</p>
            <br/>
            <p>Thank you for choosing Persimmon.</p>
            <p>-The Persimmmon Team</p>
            """
            
        elif interview_type == InterviewType.ONLINE and platform_name == "google_meet":
            integration_details: Integration = Integration.get_credentials_by_mailid(session=session,email=email,platform_name=platform_name)
            if not integration_details:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration details not found")
            credentials = integration_details.credentials

            response =  gmeeth.validate_access_token(credentials=credentials,integration=integration_details,email=email,session=session)
            
            dateh.validate_future_datetime(dt=end_time,timezone_str=meeting_details.timezone,field_name="end_time")
            dateh.validate_future_datetime(dt=meeting_details.start_time,timezone_str=meeting_details.timezone,field_name="start_time")
            duration = dateh.calculate_duration_in_minutes(start_time=meeting_details.start_time,end_time=end_time)
            meeting_details.duration = duration

   
            gmeet_request = gmeeth.CreateGoogleMeetingRequest(
                      token=response.get('access_token'),
                      summary=meeting_details.agenda,
                      start_time=meeting_details.start_time.isoformat(),
                      duration_minutes=meeting_details.duration,
                      time_zone=meeting_details.timezone,
                      attendees=[invite.email for invite in meeting_details.settings.meeting_invitees]
                     )

            response = await gmeeth.create_meeting(gmeet_request)

            create_response["data"] = response

            body = f"""
            <p>Hi There!</p>
            <p>Here is the meeting invite link {response['meeting_link']}</p>
            <br/>
            <p>Thank you for choosing Persimmon.</p>
            <p>-The Persimmmon Team</p>
            """            
          
        elif interview_type == InterviewType.FACE_TO_FACE:
            body = f"""
            <p>Hi There!</p>
            <p>Here are the location details for your upcoming face-to-face interview:</p>
            <p>{meeting_details.agenda}</p>
            <br/>
            <p>Thank you for choosing Persimmon.</p>
            <p>-The Persimmmon Team</p>
            """

        elif interview_type == InterviewType.PHONE_CALL:
            body = f"""
            <p>Hi There!</p>
            <p>Here are the contact details for your upcoming telephonic round interview:</p>
            <p>{meeting_details.agenda}</p>
            <br/>
            <p>Thank you for choosing Persimmon.</p>
            <p>-The Persimmmon Team</p>
            """

        applicant = Applicant.get_by_uuid(session=session, uuid=str(uuid))
        cc_addresses = [meeting.email for meeting in meeting_details.settings.meeting_invitees]
        to_addresses = [email, applicant.details.get('personal_information').get('email')]

        if from_address == os.getenv("FROM_ADDRESS"):
            result = emailh.send_email(subject=SCHEDULED_INTERVIEW,body=body,to_email=to_addresses,from_email=from_address,reply_to_email=email,cc_addresses=cc_addresses)
            create_response["email_result"] = result

            if result.find("Email sent successfully") != -1:
                template:Template = Template.get_by_company_id(session=session, id=company_details.id)
                if not template:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
                template.email_data.update({
                    "id": template.email_data.get("id"),
                    "send_count": template.email_data.get("send_count") + 1
                })
                template.update(session=session)
            return create_response
        else:
            integration: Integration = Integration.get_credentials(session=session,company_id=company_details.id,platform_name='email')
            if not integration:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration details not found")
            
            credentials = integration.credentials
            for cred in credentials.get('credentials'):
                if cred.get('service_type') == 'sendgrid':
                    api_key = cred['api_key']
                    senders = await emailh.get_sendgrid_senders(api_key = api_key)
                    if from_address in senders:
                        response = await emailh.sendgrid_send_mail(api_key=api_key, from_email=from_address, to_email=to_addresses, subject=SCHEDULED_INTERVIEW, body=body, cc_addresses=cc_addresses, reply_to_email=email)
                        if response.get("message") == "Email sent successfully!":
                            create_response["email_result"] = response
                            return create_response
                    else:
                        raise HTTPException(status_code=404, detail="Sender email not found in Sendgrid, please contact your administrator")
                    
                if cred.get('service_type') == 'brevo':
                    api_key = cred['api_key']
                    senders = await emailh.get_brevo_senders(api_key = api_key)
                    if from_address in senders:
                        response = await emailh.brevo_send_mail(api_key=api_key, from_email=from_address, to_email=to_addresses, subject=SCHEDULED_INTERVIEW, body=body, cc_addresses=cc_addresses, reply_to_email=email)
                        if response.get("message") == "Email sent successfully!":
                            create_response["email_result"] = response
                            return create_response
                    else:
                        raise HTTPException(status_code=404, detail="Sender email not found in Brevo, please contact your administrator")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{applicant_uuid}/feedback")
async def add_feedback(
    applicant_uuid: UUID,
    feedback: FeedbackPayload,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
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
        
        overall_feedback = feedback.feedback[0].overall_feedback
        feedback.feedback[0].overall_feedback=overall_feedback.strip()
        
            
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


@router.patch("/{applicant_id}/update_details")
async def update_applicant(
    applicant_id: UUID,
    update_data: ApplicantDetailsPartialUpdate,
    db: Session = Depends(get_db),
    token : dict = Depends(verify_firebase_token)
):
    """
    Partially updates an applicant's details.

    Updates the applicant's personal, job, and social media information.

    Args:
        applicant_id (UUID): The UUID of the applicant to be updated.
        update_data (ApplicantDetailsPartialUpdate): The data to be updated.

    Returns:
        A JSON response with a status and a message.

    Raises:
        HTTPException: If the applicant is not found, or if the update data is invalid.
    """
    try:
        solr_formatted_dob = None
        pattern = r"^(?P<years>\d{1,2}) Years (?P<months>\d{1,2}) Months$"
        print(f"update informations {update_data.job_information.work_experience}")
        if update_data.job_information.work_experience:
            match = re.match(pattern,update_data.job_information.work_experience)
            years, months = int(match.group("years")), int(match.group("months"))
            print(f"{years} years and {months} months")

            update_data.job_information.work_experience = f"{years}.{months}"
            print(f"update informations {update_data.job_information.work_experience}")

        if update_data.personal_information.date_of_birth:
            solr_formatted_dob = datah.convert_to_solr_date(update_data.personal_information.date_of_birth)


        # Fetch database applicant
        db_applicant = Applicant.get_by_uuid(session=db, uuid=str(applicant_id))

        if not db_applicant:
            raise HTTPException(status_code=404, detail=APPLICANT_NOT_FOUND)

        #Fetch database job
        db_job = Job.get_by_job_id(session=db, job_id=db_applicant.job_id)

        job_description = db_job.description
        
        #Update the match score 
        
        
        job_info = update_data.job_information
        existing_job_info = db_applicant.details['job_information']

        # If either current_ctc or expected_ctc is present in the update
        if job_info.current_ctc is not None or job_info.expected_ctc is not None:
            current_ctc = job_info.current_ctc or existing_job_info.get('current_ctc')
            expected_ctc = job_info.expected_ctc or existing_job_info.get('expected_ctc')

            if current_ctc is not None and expected_ctc is not None:
                if current_ctc >= expected_ctc:
                    raise HTTPException(
                        status_code=400,
                        detail="Current CTC cannot be greater than or equal to expected CTC"
                    )


        # Fetch Solr document
        solr_data = await solrh.get_solr_applicant_by_applicant_uuid(applicant_id, details=True)
        if not solr_data:
            raise HTTPException(status_code=404, detail="Solr document not found")

        existing_solr_doc = solr_data[0]

        # Merge and validate updated data
        try:
            merged_details = datah.deep_update(db_applicant.details, update_data.model_dump(exclude_unset=True))
            validated_details = merged_details
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors())

        # Update database details
        db_applicant.details = validated_details

        #updating the match score
        match_score = await matchh.calculate_match_percentage(resume_text=db_applicant.details,jd_text=job_description)
        db_applicant.details["match_score"] = match_score
        
        flag_modified(db_applicant, "details")
        db_applicant.update(session=db)

        # Solr partial update preparation
        if solr_formatted_dob:
            update_data.personal_information.date_of_birth = solr_formatted_dob
        solr_update_payload = datah.flatten_dict_solr(update_data.model_dump(exclude_unset=True))
       
        solr_update_payload['persimmon_score'] = {
                                                    'set': match_score
                                                        }
        
        # Update Solr document
        try:
            await solrh.update_applicant_document(
                doc_id=existing_solr_doc["id"],
                update_fields=solr_update_payload
            )
        except Exception as e:
            logger.error(f"Solr update failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Database updated but Solr sync failed"
            )

        return {
            "status": "success", 
            "message": "Applicant details updated successfully"
            }
    
    except HTTPException as e:
        raise e
    
    except Exception as e:
        traceback.print_exc()
        logger.error(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")


@router.post("/regenerate-ai-score")
async def regenerate_ai_score(
    job_code: str,
    feedback_prompt: FeedbackPromptRequest,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    try:
        job_details = Job.get_by_code(session=session, code=job_code)
        if not job_details:
            raise HTTPException(status_code=404, detail="Job not found")

        response = await solrh.query_solr(job_code=job_code)

        documents = response.get("response", {}).get("docs", [])
        if not documents:
            raise HTTPException(status_code=404, detail="No records found in Solr")

        async def fetch_resume(applicant_uuid: str):
            try:
                applicant = Applicant.get_by_uuid(session=session, uuid=applicant_uuid)
                stage_info = applicant.status.get("stages", [])[1]
                message = stage_info.get("message", "")
                gcs_path = message.split("is converted to")[1].strip().replace("/persimmon-data/", "")
                resume_text = await gcph.read_gcs_text_file_async(
                    bucket_name=PERSIMMON_DATA_BUCKET,
                    blob_path=gcs_path
                )
                return resume_text
            except Exception as e:
                return None

        resume_tasks = [fetch_resume(doc.get("applicant_uuid")) for doc in documents if doc.get("applicant_uuid")]
        resume_texts = await asyncio.gather(*resume_tasks)
        resumes = [{'text': text,'doc':doc} for text,doc in zip(resume_texts,documents) if text is not None]
        ai_results = await matchh.process_in_batches(resumes=resumes, jd_text=job_details.description, feedback=feedback_prompt.feedback_prompt)
        ai_results = [result['doc'] for result in ai_results if result['doc']]
        ai_results.sort(key=lambda a: a['persimmon_score'],reverse=True)
        ai_top_results = ai_results[:10]
        
        return {
            "solr_response": ai_top_results,
            "pagination": {
                'total_pages': 0,
                'total_count': len(ai_top_results)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

@router.get("/messages/{number}")
async def get_messages(
    number: int
):
    try:
        wati_api_token = os.getenv("WATI_API_TOKEN")
        headers = {"Authorization": f"Bearer {wati_api_token}"}
        url = f"https://app-server.wati.io/api/v1/getMessages/{number}"
        response =requests.get(url , headers=headers)
        print("the url is ",url)
        if response.status_code == 200:
            message_texts = [
                    item["text"]
                    for item in response.json()["messages"]["items"]
                    if item.get("eventType") == "message" and "text" in item
                ]
            return message_texts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
