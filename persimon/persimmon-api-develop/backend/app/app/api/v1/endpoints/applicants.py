import json
import logging
import os
import traceback
import uuid
from typing import Dict, List, Optional
from uuid import UUID
from fastapi.responses import JSONResponse
import httpx
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.api.v1.endpoints.models.applicant_model import (
    ApplicantPartialUpdate, ApplicantRequest, FilterRequest, PayloadModel,Message, ApplicantModel)
from app.db.session import get_db
from app.helpers import db_helper as dbh, gcp_helper as gcph, solr_helper as solrh, date_helper as dateh
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers.otlpless_helper import verify_otpless_token
from app.helpers.math_helper import get_pagination
from app.models.applicant import Applicant
from app.models.job import Job
from app.models.stages import Stages
import math
from app.services import applicants as ap
from urllib.parse import quote

load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("DatabaseUploader")

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}



router = APIRouter()
SOLR_BASE_URL=os.getenv("SOLR_BASE_URL")
PERSIMMON_DATA_BUCKET=os.getenv("PERSIMMON_DATA_BUCKET")


@router.post("/upload-resume")
async def upload_resumes(
    job_id: int,
    job_code: str,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    
    allowed_extensions = {"pdf", "docx"}  
    errors = []
    success_files = []
    flatten_resumes = []
    created_by = token['email']
    for file in files:
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            detail= f"File '{file.filename}' has an unsupported file extension. Only '.pdf' and '.docx' files are allowed."
            errors.append(detail)
            continue
        file_success, error_message, flatten_resume = await ap.process_resume(file, session,created_by,job_id,job_code)
        
        if file_success:
            success_files.append(file.filename)
            if flatten_resume:
                flatten_resumes.append(flatten_resume)
        if error_message:
            errors.append(error_message)

    return {
        "status": "success" if not errors else "partial success",
        "success_files": success_files,
        "errors": errors,
        "extracted_texts": flatten_resumes
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
                    detail = f"Once an applicant is moved to any other stage, they should not be allowed to move back to the new stage"
                )
            
            stage_uuids = [stage['uuid'] for stage in recruiter_job_stages.stages]
            if stage_uuid not in stage_uuids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stage uuid")

            params = {
                "q": f"applicant_uuid:({' OR '.join(applicant_uuids)})", 
                "rows": len(applicant_uuids),
                "wt": "json"
            }

            async with httpx.AsyncClient() as client:
                solr_response = await client.get(f"{SOLR_BASE_URL}/resumes/select", params=params)
                solr_response.raise_for_status()  
                documents = solr_response.json().get("response", {}).get("docs", [])
                updates = []
                for document in documents:
                    if document["applicant_uuid"] in applicant_uuids:
                        updates.append({
                            "id": document["id"],  
                            "stage_uuid": {"set": stage_uuid}  
                        })

                if not updates:
                    raise HTTPException(status_code=404,detail="No matching documents found for update in solr")
                update_url = f"{SOLR_BASE_URL}/resumes/update?commit=true"
                try:
                    update_response = await client.post(update_url, json=updates)
                except httpx.RequestError as e:
                    print(f"Request error occurred: {e}")
                # TODO: Investigate 500 error coming from solr after atomic update happened successfully
                
            for applicant_uuid in applicant_uuids:
                existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=str(applicant_uuid))
                if not existing_applicant:
                    raise HTTPException(status_code=404, detail=f'Applicant with id as {applicant_id} was not found')

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
        # Log the job_id
        print(f"Job ID provided: {job_code}")

        # Pagination setup
        page_size = 20
        solr_response = await solrh.query_solr(job_code,stage_uuid)
        if solr_response:
            total_count = solr_response.get("response", {}).get("numFound", 0)
        else:
            total_count = 0
        print(f"the total count is: {total_count}")
        pagination = get_pagination(page=page, page_size=page_size, total_records=total_count)

        print(f"the offset is: {pagination['offset']} {pagination}")

        final_query,exclude_query = ap.construct_query(request)

        # Query Solr with filters
        query_parts = []
        if job_code:
            query_parts.append(f"job_code:\"{job_code}\"")
        if stage_uuid:
            query_parts.append(f"stage_uuid:\"{stage_uuid}\"")
        if name:
            query_parts.append(f"full_name:\"{name}\"")
        query = " AND ".join(query_parts)  # Combine query parts with AND

        
        solr_response_with_filters = await solrh.query_solr_with_filters(query=query, filters=final_query, rows=page_size,start=pagination['offset'],exclude=exclude_query)
        documents = solr_response_with_filters.get("response", {}).get("docs", [])
        N = total_count
        for i,document in enumerate(documents):
            percentile = ((N-i-(pagination['offset']))/N)*100
            document["score"] = math.ceil(percentile)
        
        # Return the response from Solr
        return {
            "solr_response": solr_response_with_filters,
            "pagination": {
                'total_pages': pagination['total_pages'],
                'total_count': total_count
            }
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    except HTTPException as e:
        traceback.print_exc()
        raise str(e)

@router.get("/{uuid}")
async def get_applicant(
    uuid: str,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
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
            "status": status.HTTP_200_OK,
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


@router.get("/{uuid}/resume")
def get_resume(
    uuid: str,
    action: str = "view",
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
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

@router.post("/career-page")
async def create_applicant_in_career_page(
    job_id: int,
    job_code: str,
    phone_number: int,
    full_name: str,
    email_id: str,
    linkedin_url: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_db), 
    token: str = Depends(verify_otpless_token)  
):
    allowed_extensions = {"pdf", "docx"}  
    file_extension = file.filename.split('.')[-1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
            detail=f"File '{file.filename}' has an unsupported file extension. Only '.pdf' and '.docx' files are allowed."
        )
    
    try:
        applicant_data = ApplicantModel(
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
    # try:
    #     pubsub_message = {
    #         "job_id": job_id, 
    #         "applicant_id":applicant_uuid,
    #         "stage_uuid":stage_uuid 
    #     }
    #     pubsub_response = gcph.send_message_to_pubsub(pubsub_message,topic_name="solr-text")  # Call the service function
    #     logger.info(f"Pub/Sub message sent: {pubsub_response}")
    # except Exception as e:
    #     logger.error(f"Failed to send Pub/Sub message: {str(e)}")
    #     raise HTTPException(status_code=500, detail=f"Failed to send Pub/Sub message: {str(e)}")
    try:
        created_applicant = applicant_data.create(session=session,created_by=created_by)
        return {
            "status": 200,
            "message": "Applicant created successfully.",
            "data": created_applicant
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create applicant. Please try again. {str(e)}")


@router.post("/upload-to-solr")
async def upload_to_solr(
    flatten_json: PayloadModel, 
    stage_uuid: str ,
    job_code: str ,
    applicant_uuid :str, 
    token: dict = Depends(verify_firebase_token)
):
    flatten_resume_solr=flatten_json.data
    applicant_uuid=str(uuid.uuid4())
    # Convert the flatten_json1 (which is a Python dict) to JSON
    
    print(f"the json data is : {flatten_resume_solr}  {type(flatten_resume_solr)}")
    flatten_resume_solr['uuid'] = applicant_uuid
    flatten_resume_solr['stage_uuid'] = stage_uuid
    flatten_resume_solr['job_code'] = job_code

    json_data = json.dumps(flatten_resume_solr)
    print(f"{json_data}")
    # Send the JSON data to Solr
    response = requests.post(os.getenv("SOLR_URL"), headers={"Content-Type": "application/json"}, data=json_data)

    # Send a message to Pub/Sub after successful uploads
    # try:
    #     pubsub_message = {
    #         "token": token,
    #         "job_code": job_code , 
    #         "applicant_id":None,
    #         "stage_uuid":None
    #     }
    #     pubsub_response = gcph.send_message_to_pubsub(pubsub_message,topic_name="")  # Call the service function
    #     logger.info(f"Pub/Sub message sent: {pubsub_response}")
    # except Exception as e:
    #     logger.error(f"Failed to send Pub/Sub message: {str(e)}")
    #     raise HTTPException(status_code=500, detail=f"Failed to send Pub/Sub message: {str(e)}")
    
    # Check if the request was successful
    if response.status_code == 200:
        return {
            "status":200,
            "message": "Document uploaded successfully"
            }
    else:
        return {
            "status":204,
            "message": f"Error uploading the document: {response.text}"
            }
