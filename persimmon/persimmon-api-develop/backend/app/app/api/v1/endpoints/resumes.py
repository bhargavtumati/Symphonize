import asyncio
import logging
import os
import tempfile
import time
import uuid
import json
import requests
from io import BytesIO
from typing import List, Optional
from tempfile import SpooledTemporaryFile
from datetime import datetime,timezone

from asyncer import asyncify, create_task_group, syncify
from dotenv import load_dotenv
from fastapi import (APIRouter, File, Form, HTTPException, Query, UploadFile,
                     status,Depends)
from fastapi.responses import JSONResponse
from app.db.session import get_db
from app.models.job import Job
from app.models.applicant import Applicant
from app.models.company import Company
from app.models.recruiter import Recruiter
from app.api.v1.endpoints.models.applicant_model import ResumeFlatten
from app.api.v1.endpoints.models.resume_model import EmailTemplate, ResumeParseRequest,FilePathPayload
from app.core.config import settings
from app.helpers import classifier_helper as classifierh
from app.helpers import data_helper as datah
from app.helpers import gcp_helper as gcph
from app.helpers import json_helper as jsonh
from app.helpers import email_helper as emailh
from app.helpers import pdf_helper as pdfh
from app.helpers import db_helper as dbh
from app.helpers import solr_helper as solrh, image_helper as imageh
from app.models.stages import Stages
from app.schemas.response_schema import GetResponseBase, create_response
from app.helpers.firebase_helper import verify_firebase_token,get_base_url
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func
from sqlalchemy import cast, String
from typing import List, Dict, Optional
from pydantic import EmailStr
from app.models.template import Template

security = HTTPBearer()

router = APIRouter()
load_dotenv()

import logging

# Configure logging
logger = logging.getLogger(__name__)


api_reference: dict[str, str] = {
    "api_reference": "https://github.com/symphonize/persimmon-api"
}

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("ResumeUploader")

@router.get("/")
def get_resumes() -> GetResponseBase:
    return create_response(message=f"Get all resumes", data={}, meta=api_reference)


@router.get("/classify")
def classify_resumes() -> GetResponseBase:
    response = {}
    return create_response(
        message=f"Classify resumes", data=response, meta=api_reference
    )


@router.post("/process")
def process(
    job_description: str = Form(...),
    job_title: str = Form(...),
    company_name: Optional[str] = Form(None),
    classifier_version: str = Form(...),
    vectorizer_version: str = Form(...),
    files: List[UploadFile] = File(...),
):
    return classifierh.process_resumes(
        job_description,
        job_title,
        company_name,
        classifier_version,
        vectorizer_version,
        files,
    )


from tika import parser
from pathlib import Path

@router.post("/legacy-extract-text")
async def legacy_extract_text(
    request: ResumeParseRequest,
    session=Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: dict = Depends(verify_firebase_token),
    base_url: str = Depends(get_base_url)
):
    api_start_time = datetime.now(timezone.utc)
    updated_by = token['email']
    gspath = request.payload
    text = None
    file_upload = None
    status = None
    try:
        # Validate GCP path
        if not gspath.startswith("gs://"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GCP path. Ensure it starts with 'gs://'."
            )

        # Extract bucket and blob details
        parts = gspath.replace("gs://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError("Invalid GCP path. Format should be 'gs://bucket_name/blob_name'.")

        bucket_name, blob_name = parts
        filename = blob_name.split('/')[-1]

        # Download file from GCP
        file_like_object = await gcph.download_from_gcp(bucket_name, blob_name, filename)
        if not file_like_object:
            raise Exception("Failed to download the file from GCP.")

        # Wrap the file content in a file-like object
        upload_file = UploadFile(file=file_like_object)

        # Extract text from the file
        text = await pdfh.extract_text_from_file(file=upload_file)
        if not text:
            raise Exception("No text could be extracted from the provided file.")

        # Write and upload the extracted text
        with SpooledTemporaryFile() as temp_file:
            temp_file.write(text.encode("utf-8"))
            temp_file.seek(0)

            destination_blob_name = f"s2/{filename}.txt"
            file_upload = await gcph.upload_to_gcp(bucket_name, temp_file, destination_blob_name)

        # Update status in the database
        api_end_time = datetime.now(timezone.utc)
        details = {
            "original_resume": request.original_resume,
            "context": "at stage 2 text extracted",
            "file_upload": file_upload
        }
        status = {
            "stage": "at stage 2 upload",
            "status": "success",
            "message": "The file is converted to text and uploaded to GCP successfully.",
            "start": api_start_time.isoformat(),
            "end": api_end_time.isoformat()
        }
        existing_applicant = Applicant.get_id_by_gcp_path(session=session, gcp_path=gspath)
        if not existing_applicant:
            raise HTTPException(status_code=404, detail=f"Applicant with gcp_path {gspath} was not found")

        existing_applicant.details = details
        existing_applicant.status['stages'].append(status)
        existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
        flag_modified(existing_applicant, 'status')
        existing_applicant.update(session=session)

        # Trigger Pub/Sub message
        pubsub_message = {
            "apiEndpoint": f"{base_url}/api/v1/ai/extract-features-from-resumes-llm",
            "accessToken": credentials.credentials,
            "gs_path": file_upload,
            "original_resume": request.original_resume
        }
        pubsub_response = await gcph.send_message_to_pubsub(pubsub_message, topic_name="text-to-json")
        logger.info(f"Pub/Sub message sent: {pubsub_response}")

        return {
            "status": "success",
            "message": "Text extracted successfully.",
            "extracted_text": text,
            "file_upload": file_upload
        }

    except Exception as e:
        # Always update status as failed in case of any exception
        print("this is the exception block ")
        api_end_time = datetime.now(timezone.utc)
        status = {
            "stage": "at stage 2 upload",
            "status": "failed",
            "message": f"The file failed to process due to: {str(e)}.",
            "start": api_start_time.isoformat(),
            "end": api_end_time.isoformat()
        }
        try:
            existing_applicant = Applicant.get_id_by_original_path(session=session, gcp_path=request.original_resume)
            if existing_applicant:
                existing_applicant.status['stages'].append(status)
                existing_applicant.status['overall_status'] = "failed"
                existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
                flag_modified(existing_applicant, 'status')
                existing_applicant.update(session=session)
        except Exception as db_exception:
            logger.error(f"Failed to update the database with failure status: {str(db_exception)}")

        raise HTTPException(status_code=500, detail=str(e))

class ExtractTextRequest(BaseModel):
    source: str  
    uuid: str

@router.post("/extract-text")
async def extract_text(
    request: ExtractTextRequest,
    session : Session = Depends(get_db),
    base_url: str = Depends(get_base_url),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: dict = Depends(verify_firebase_token)
):
    try:
        api_start_time = datetime.now(timezone.utc)

        source = Path(request.source)
        updated_by = token['email']
        original_token = credentials.credentials
        
        try:
            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)

            if not existing_applicant:
                raise HTTPException(status_code=404, detail=f"Applicant was not found")
            
            #the prevention of duplicate api calls using the stage in data base
            stage_exist = any(stage["stage"] == "document-to-text" for stage in existing_applicant.status["stages"])
            if stage_exist:
                return "The stage already got processed"
            parsed = parser.from_file(request.source)
            text = parsed.get('content', '')
            text = text if text else ''
            destination = source.parent.parent / "processed" / "text" / (source.stem + '.txt')
            with open(destination, 'w',encoding="utf-8") as writer:
                writer.write(text)
        except Exception as e:
            logger.error(f"Error during file processing: {str(e)}")
        api_end_time = datetime.now(timezone.utc)
        if destination:            
            status = {
                "stage":"document-to-text",
                "status": "success",
                "message": f"{str(source)} is converted to {str(destination)}",
                "start": api_start_time.isoformat(),
                "end": api_end_time.isoformat()
            }
            existing_applicant.status['stages'].append(status)
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            try:
                existing_applicant.update(session=session)
            except Exception as e:
                logger.error(f"Error updating the applicant details: {str(e)}")
                raise HTTPException(
                    status_code=460, detail=f"error updating the applicant details {str(e)}"
                )
            
            try:
                pubsub_message = {
                    "endpoint": f"{base_url}/api/v1/ai/text-to-json",
                    "token": original_token,
                    "payload": {
                        "source": str(destination),
                        "uuid": request.uuid
                    }
                }

                # Send the message to Pub/Sub
                pubsub_response = await gcph.send_message_to_pubsub(pubsub_message, topic_name=os.getenv("TOPIC_NAME"))
                logger.info(f"Pub/Sub message sent: {pubsub_response}")
            except Exception as e:
                logger.error(f"Failed to send Pub/Sub message: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send Pub/Sub message: {str(e)}"
                )
        else:
            status = {
                "stage":"document-to-text",
                "status": "failed",
                "message": f"{str(source)} is not converted to {str(destination)}",
                "start": api_start_time.isoformat(),
                "end": api_end_time.isoformat()
            }
            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
            print("the applicant data ", existing_applicant.details)
            existing_applicant.status['stages'].append(status)
            existing_applicant.status['overall_status'] = "failed"
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            print("the existing applicant object : ", existing_applicant)
            try:
                existing_applicant.update(session=session)
            except Exception as e:
                logger.error(f"Error updating the applicant details: {str(e)}")
                raise HTTPException(
                    status_code=460, detail=f"error updating the applicant details {str(e)}"
                )
            
        if text:
            return {
                "status": "success",
                "message": f"Text extracted successfully from {str(source)}.",
                "extracted_text": text,
                "file_upload": destination
            }
        else:
            return {
                "status": "failure",
                "message": f"No text could be extracted from the {str(source)}.",
                "extracted_text": None,
                "file_upload": None
            }
    except HTTPException as e:
        print(e)
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/legacy-upload")
async def legacy_upload_resumes(
    job_code:str,
    files: List[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token),
    base_url: str = Depends(get_base_url) 
):
    """
    Endpoint to upload up to 100 resumes to GCP.
    """

    #capture the start time 
    api_start_time = datetime.now(timezone.utc)

    unique_id = uuid.uuid4()
    original_token = credentials.credentials
    #print("the original token is : ",original_token)
    created_by = token['email']
    BUCKET= os.getenv("BUCKET")
    FOLDER = os.getenv("FOLDER")
    allowed_extensions = {"pdf", "docx"} 
    created_applicant = None 
    for file in files:
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                 detail=f"File type '{file_extension}' is not allowed. Only {', '.join(allowed_extensions)} files are permitted." 
            )
    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Cannot upload more than 100 files at a time.")

    start_time = time.time()
    logger.info(f"Starting upload of {len(files)} files...")

    tasks = []
    for file in files:
        unique_id = uuid.uuid4()
        original_file_name = f"{unique_id}_{file.filename}"
        #gcs_path = f"s1/{original_file_name}"
        gcs_path = f"{FOLDER}/{original_file_name}"

        # Convert UploadFile to SpooledTemporaryFile
        temp_file = tempfile.SpooledTemporaryFile()
        content = await file.read()  # Read the file content
        temp_file.write(content)    # Write content to the temporary file
        temp_file.seek(0)           # Reset file pointer to the start

        # Pass SpooledTemporaryFile to the GCP upload function
        #tasks.append(gcph.upload_to_gcp("symphonize", temp_file, gcs_path))
        tasks.append(gcph.upload_to_gcp(BUCKET, temp_file, gcs_path))

    # Concurrently upload files
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle results
    uploaded_files = []
    errors = []
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Failed to upload {files[idx].filename}: {str(result)}")
            errors.append({files[idx].filename: str(result)})
        else:
            uploaded_files.append(result)

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    logger.info(f"Upload completed in {duration} seconds.")

    for uploaded_file in uploaded_files:
        job_id = Job.get_id_by_code(session=session,code=job_code)
        print("the job id is : ",job_id)
        if len(uploaded_files) > 0: 
            applicant_uuid = str(uuid.uuid4())
            stage_uuid=""
            try:
                stages_existing: Stages = Stages.get_by_id(session=session, job_id=job_id)
                print(f"the stages_existing are {stages_existing.stages}")
                if len(stages_existing.stages) > 0:
                    stage_uuid = stages_existing.stages[0]['uuid']
            except Exception as e: 
                raise HTTPException(status_code=404, detail=f"Stages not found {str(e)}")
        details = {
            "original_resume":uploaded_file,
            "context":"at stage 1 upload",
            "file_upload":uploaded_file
            }
        api_end_time = datetime.now(timezone.utc)
        status = {
            "overall_status": "In progress",
            "stages": [
                {
                    "stage": "at stage 1 upload",
                    "status": "success",
                    "message": "the file is uploaded to GCP",
                    "start": api_start_time.isoformat(),
                    "end": api_end_time.isoformat()
                }
            ]
         }

        applicant_uuid = str(uuid.uuid4())
        print("the applicant uuid is : ",applicant_uuid,stage_uuid,job_id,details,status)
        applicant_data = Applicant(details=details, stage_uuid=stage_uuid, job_id=job_id, uuid=applicant_uuid,status=status)
        print(f"the applicant data also {applicant_data} this is after the aapplicant")
        try:
            print("created by before insertion",created_by)
            created_applicant = applicant_data.create(session=session,created_by=created_by)
            print("the created applicant is : ",created_applicant)
        except Exception as e: 
            raise HTTPException(status_code=404, detail="Failed to create applicant")

        #Send a message to Pub/Sub after successful uploads
        try:
            pubsub_message = {
                "apiEndpoint": f"{base_url}/api/v1/resumes/extract-text",
                "accessToken": original_token,
                "gs_path": uploaded_file,
                "original_resume": uploaded_file
            }
            pubsub_response = await gcph.send_message_to_pubsub(pubsub_message,topic_name="document-to-text")  # Call the service function
            logger.info(f"Pub/Sub message sent: {pubsub_response}")
        except Exception as e:
            logger.error(f"Failed to send Pub/Sub message: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to send Pub/Sub message: {str(e)}")

    # Return the response
    return JSONResponse({
        "uploaded_files": uploaded_files,
        "errors": errors,
        "total_files": len(files),
        "successful_uploads": len(uploaded_files),
        "failed_uploads": len(errors),
        "upload_duration_seconds": duration,
        "job_code": job_code,
        "pubsub_status": "Message sent successfully"
    })

@router.post("/upload")
async def upload_resumes(
    job_code:str,
    files: List[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token),
    base_url: str = Depends(get_base_url) 
):
    """
    Endpoint to upload up to 100 resumes to GCP.
    """

    #capture the start time 
    api_start_time = datetime.now(timezone.utc)

    unique_id = uuid.uuid4()
    original_token = credentials.credentials
    #print("the original token is : ",original_token)
    created_by = token['email']
    BUCKET= os.getenv("BUCKET")
    FOLDER = os.getenv("FOLDER")
    PERSIMMON_DATA=os.getenv("PERSIMMON_DATA", "/persimmon-data")
    ENVIRONMENT=os.getenv("ENVIRONMENT", "development")
    allowed_extensions = {"pdf", "docx"} 
    created_applicant = None 
    for file in files:
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                 detail=f"File type '{file_extension}' is not allowed. Only {', '.join(allowed_extensions)} files are permitted." 
            )
    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Cannot upload more than 100 files at a time.")

    start_time = time.time()
    logger.info(f"Starting upload of {len(files)} files...")

    tasks = []
    errors = []
    uploaded_files = []
    base64_images = []

    for file in files:
        try:
            unique_id = uuid.uuid4()
            original_file_name = f"{unique_id}_{file.filename}"
            #gcs_path = f"s1/{original_file_name}"
            # gcs_path = f"{FOLDER}/{original_file_name}"
            destination = f"{PERSIMMON_DATA}/{ENVIRONMENT}/resumes/raw/{original_file_name}"

            # Convert UploadFile to SpooledTemporaryFile
            # temp_file = tempfile.SpooledTemporaryFile()
            content = await file.read()  # Read the file content
            print(f"Attempting to write to {destination}")
            with open(destination, 'wb') as writer:
                writer.write(content)
            print(f"successfully written to destination")
            uploaded_files.append(destination)
            file_extension = file.filename.split('.')[-1].lower()
            try:
                if file_extension == "pdf":
                    image_base64 = imageh.extract_first_image_from_pdf(BytesIO(content))
                elif file_extension == "docx":
                    image_base64 = imageh.extract_first_image_from_docx(BytesIO(content))
            except HTTPException as e:
                raise e
            base64_images.append(image_base64)
        except Exception as e:
            print(f"exception while converting document to text: {str(e)}")
            errors.append(str(e))

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    logger.info(f"Upload completed in {duration} seconds.")

    for index,uploaded_file in enumerate(uploaded_files):
        try:
            job_id = Job.get_id_by_code(session=session,code=job_code)
        except Exception as e:
            return HTTPException(status_code=404,detail="Job not found")
        print("the job id is : ",job_id)
        if len(uploaded_files) > 0: 
            applicant_uuid = str(uuid.uuid4())
            stage_uuid=""
            try:
                stages_existing: Stages = Stages.get_by_id(session=session, job_id=job_id)
                print(f"the stages_existing are {stages_existing.stages}")
                if len(stages_existing.stages) > 0:
                    stage_uuid = stages_existing.stages[0]['uuid']
            except Exception as e: 
                raise HTTPException(status_code=404, detail=f"Stages not found {str(e)}")
        details = {
            "original_resume":uploaded_file,
            "context":"document-added",
            "file_upload":uploaded_file,
            "applicant_image": base64_images[index]
            }
        api_end_time = datetime.now(timezone.utc)
        status = {
            "overall_status": "In progress",
            "stages": [
                {
                    "stage": "at stage 1 upload",
                    "status": "success",
                    "message": "the file is uploaded to GCP",
                    "start": api_start_time.isoformat(),
                    "end": api_end_time.isoformat()
                }
            ]
         }

        applicant_uuid = str(uuid.uuid4())
        print("the applicant uuid is : ",applicant_uuid,stage_uuid,job_id,details,status)
        applicant_data = Applicant(details=details, stage_uuid=stage_uuid, job_id=job_id, uuid=applicant_uuid,status=status)
        print(f"the applicant data also {applicant_data} this is after the aapplicant")
        try:
            print("created by before insertion",created_by)
            created_applicant = applicant_data.create(session=session,created_by=created_by)
            print("the created applicant is : ",created_applicant)
        except Exception as e: 
            raise HTTPException(status_code=404, detail="Failed to create applicant")

        #Send a message to Pub/Sub after successful uploads
        try:
            pubsub_message = {
                "endpoint": f"{base_url}/api/v1/resumes/extract-text",
                "token": original_token,
                "payload": {
                    "source": uploaded_file,
                    "uuid": applicant_uuid
                }
            }
            # pubsub_response = await gcph.send_message_to_pubsub(pubsub_message,topic_name="document-to-text")  # Call the service function
            pubsub_response = await gcph.send_message_to_pubsub(pubsub_message,topic_name=os.getenv("TOPIC_NAME")) # Call the service function
            logger.info(f"Pub/Sub message sent: {pubsub_response}")
        except Exception as e:
            logger.error(f"Failed to send Pub/Sub message: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to send Pub/Sub message: {str(e)}")

    # Return the response
    return {
        "uploaded_files": uploaded_files,
        "errors": errors,
        "total_files": len(files),
        "successful_uploads": len(uploaded_files),
        "failed_uploads": len(errors),
        "upload_duration_seconds": duration,
        "job_code": job_code,
        "pubsub_status": "Message sent successfully"
    }


class FlattenForDatabase(BaseModel):
    source: str
    uuid: str

@router.post("/flatten-for-database")
async def flattern_resume_data_from_json(
    request: FlattenForDatabase,
    session=Depends(get_db),
    credentials: HTTPAuthorizationCredentials=Depends(security),
    token: dict=Depends(verify_firebase_token),
    base_url: str=Depends(get_base_url)
):
    api_start_time = datetime.now(timezone.utc)
    updated_by = token['email']
    flattened_data = None
    file_upload = None

    try:
        source = Path(request.source)
        with open(request.source, 'r') as reader:
            string_to_be_processed = reader.read()
            json_to_be_processed = json.loads(string_to_be_processed)
        flattened_data = await jsonh.flatten_resume_data(json_to_be_processed)
        flattened_data = datah.convert_nulls_to_empty_strings(flattened_data)

        destination = source.parent.parent / "flat" / (source.stem + "-db.json")
        if flattened_data:
            json_string = json.dumps(flattened_data, indent=4)
            with open(destination, "w") as writer:
                writer.write(json_string)

        # Update status in the database
        if flattened_data:
            api_end_time = datetime.now(timezone.utc)
            status = {
                "stage": "flatten-for-database",
                "status": "success",
                "message": "The file is inserted into the database and uploaded to GCP successfully.",
                "start": api_start_time.isoformat(),
                "end": api_end_time.isoformat()
            }
            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
            if not existing_applicant:
                raise HTTPException(status_code=404, detail=f"Applicant with id as {request.payload} was not found")

            existing_applicant.status['stages'].append(status)
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            existing_applicant.update(session=session)

            return {
                "status": 200,
                "message": "success",
                "flattened_resume": flattened_data,
                "file_upload": file_upload
            }
    except Exception as e:
        # Always update status as failed in case of any exception
        api_end_time = datetime.now(timezone.utc)
        status = {
            "stage": "flatten-for-database",
            "status": "failed",
            "message": f"The file failed to insert into the database due to: {str(e)}.",
            "start": api_start_time.isoformat(),
            "end": api_end_time.isoformat()
        }
        try:
            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
            if existing_applicant:
                existing_applicant.status['stages'].append(status)
                existing_applicant.status['overall_status'] = "failed"
                existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
                flag_modified(existing_applicant, 'status')
                existing_applicant.update(session=session)
        except Exception as db_exception:
            logger.error(f"Failed to update the database with failure status: {str(db_exception)}")

        raise HTTPException(status_code=500, detail=str(e))

@router.post("/legacy-flatten-for-database")
async def legacy_flattern_resume_data_from_json(
    request: ResumeParseRequest,
    session=Depends(get_db),
    credentials: HTTPAuthorizationCredentials=Depends(security),
    token: dict=Depends(verify_firebase_token),
    base_url: str=Depends(get_base_url)
):
    api_start_time = datetime.now(timezone.utc)
    updated_by = token['email']
    gspath = request.payload
    flattened_data = None
    file_upload = None

    # Ensure status is always updated
    try:
        # Validate GCP path
        if not gspath.startswith("gs://"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GCP path. Ensure it starts with 'gs://'."
            )

        # Extract bucket and blob details
        parts = gspath.replace("gs://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError("Invalid GCP path. Format should be 'gs://bucket_name/blob_name'.")

        bucket_name, blob_name = parts
        filename = blob_name.split('/')[-1]
        
        # Download file from GCP
        file_like_object = await gcph.download_from_gcp(bucket_name, blob_name, filename)
        if file_like_object:
            content = file_like_object.read()
            response_json = json.loads(content)

        # Flatten the data
        flattened_data = await jsonh.flatten_resume_data(response_json)
        flattened_data = datah.convert_nulls_to_empty_strings(flattened_data)

        # Write and upload flattened data
        if flattened_data:
            json_string = json.dumps(flattened_data, indent=4)
            with SpooledTemporaryFile() as temp_file:
                temp_file.write(json_string.encode("utf-8"))
                temp_file.seek(0)

                destination_blob_name = f"s4/{filename}.json"
                file_upload = await gcph.upload_to_gcp(bucket_name, temp_file, destination_blob_name)

        # Update status in the database
        if flattened_data:
            api_end_time = datetime.now(timezone.utc)
            status = {
                "stage": "at stage 4 upload",
                "status": "success",
                "message": "The file is inserted into the database and uploaded to GCP successfully.",
                "start": api_start_time.isoformat(),
                "end": api_end_time.isoformat()
            }
            details = flattened_data
            details["original_resume"] = request.original_resume
            details["file_upload"] = request.payload
            existing_applicant: Applicant = Applicant.get_id_by_original_path(session=session, gcp_path=request.original_resume)
            if not existing_applicant:
                raise HTTPException(status_code=404, detail=f"Applicant with id as {request.payload} was not found")

            existing_applicant.details = details
            existing_applicant.status['stages'].append(status)
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            existing_applicant.update(session=session)

            return {
                "status": 200,
                "message": "success",
                "flattened_resume": flattened_data,
                "file_upload": file_upload
            }
    except Exception as e:
        # Always update status as failed in case of any exception
        api_end_time = datetime.now(timezone.utc)
        status = {
            "stage": "at stage 4 upload",
            "status": "failed",
            "message": f"The file failed to insert into the database due to: {str(e)}.",
            "start": api_start_time.isoformat(),
            "end": api_end_time.isoformat()
        }
        try:
            existing_applicant: Applicant = Applicant.get_id_by_original_path(session=session, gcp_path=request.original_resume)
            if existing_applicant:
                existing_applicant.status['stages'].append(status)
                existing_applicant.status['overall_status'] = "failed"
                existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
                flag_modified(existing_applicant, 'status')
                existing_applicant.update(session=session)
        except Exception as db_exception:
            logger.error(f"Failed to update the database with failure status: {str(db_exception)}")

        raise HTTPException(status_code=500, detail=str(e))


class Flatten(BaseModel):
    source: str
    uuid: str

@router.post("/flatten")
async def flatten(
    request: Flatten,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    api_start_time = datetime.now(timezone.utc)
    updated_by = token['email']
    flattened_data_solr = None
    file_upload = None
    existing_applicant = None

    try:
        existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
        #to stop the applicant creation when duplicate api calls happens . 
        #if applicant is already created, then return the message
        if not existing_applicant:
            raise HTTPException(status_code=404,detail=f"Applicant was not found")
        
        stage_exist = any(stage["stage"] == "flatten" for stage in existing_applicant.status["stages"])
        if stage_exist:
            return "The stage already got processed"
        
        applicant_exist = await solrh.is_applicant_exist(request.uuid)
        if applicant_exist:
            return "applicant already exist"

        source = Path(request.source)
        destination = source.parent.parent / "flat" / (source.stem + ".json")
        with open(request.source, "r",encoding="utf-8") as reader:
            data_to_be_processed = reader.read()
        json_to_be_processed = json.loads(data_to_be_processed) 
        job_code = Job.get_code_with_id(session=session, id=existing_applicant.job_id)
        if not existing_applicant:
            raise HTTPException(status_code=404, detail=f'Applicant with id as was not found')

        logger.info(f"========= flattening for solr: json_to_be_processed: {json_to_be_processed}")
            
       # Flatten and process the data for Solr
        flattened_data_solr = await jsonh.flatten_resume_data_solr(json_to_be_processed)
        flattened_data_solr = datah.convert_nulls_to_empty_strings(flattened_data_solr)
        flattened_data_solr['applicant_uuid'] = existing_applicant.uuid
        flattened_data_solr['stage_uuid'] = existing_applicant.stage_uuid
        flattened_data_solr['job_code'] = job_code

        logger.info(f"========= flattening for database: json_to_be_processed: {json_to_be_processed}")
        flattened_data = await jsonh.flatten_resume_data(json_to_be_processed)
        flattened_data = datah.convert_nulls_to_empty_strings(flattened_data)

        logger.info(f"========= before writing to destination {str(destination)}")
        # Upload data to Solr
        response = await solrh.upload_to_solr(flattened_data_solr)
        logger.info(f"========= solrh.upload_to_solr(flattened_data_solr): response: {response}")
        if response["status_code"] != 200:
            raise Exception(f"status: {response['status_code']} message: {response['message']}")

        # Upload flattened data to GCP
        json_string = json.dumps(flattened_data_solr, indent=4)
        with open(destination, "w",encoding="utf-8") as writer:
            writer.write(json_string)
        logger.info(f"========= written to destination {str(destination)}")
        # Update the applicant's status in the database
        status = {
            "stage": "flatten",
            "status": "success",
            "message": "The file is converted to JSON",
            "api_start_time": api_start_time.isoformat(),
            "api_end_time": datetime.now(timezone.utc).isoformat()
        }
        existing_details = existing_applicant.details
        details = flattened_data
        details["original_resume"] = existing_details["original_resume"]
        details["file_upload"] = str(destination)
        existing_applicant.details = details
        existing_applicant.status['stages'].append(status)
        existing_applicant.status['overall_status'] = "success"
        existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
        flag_modified(existing_applicant, 'status')
        existing_applicant.update(session=session)
        logger.info(f"========= updated the status")

        return {
            "status": 200,
            "message": "success",
            "flattened_resume_solr": flattened_data_solr,
            "file_upload": file_upload
        }

    except Exception as e:
        logger.error("========= handling catch all")
        # Handle errors and update status as "failed"
        api_end_time = datetime.now(timezone.utc)
        status = {
            "stage": "flatten",
            "status": "failed",
            "message": str(e),
            "api_start_time": api_start_time.isoformat(),
            "api_end_time": api_end_time.isoformat()
        }
        existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
        if existing_applicant:
            existing_applicant.status['stages'].append(status)
            existing_applicant.status['overall_status'] = "failed"
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            existing_applicant.update(session=session)

        logger.error(f"flatten: str{e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/legacy-flatten-for-solr")
async def leagacy_flattern_resume_data_from_solr(
    request: ResumeParseRequest,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    api_start_time = datetime.now(timezone.utc)
    updated_by = token['email']
    gspath = request.payload
    flattened_data_solr = None
    file_upload = None
    existing_applicant = None

    try:
        # Validate GCP path
        if not gspath.startswith("gs://"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GCP path. Ensure it starts with 'gs://'."
            )

        # Extract bucket name and blob name from GCP path
        parts = gspath.replace("gs://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError("Invalid GCP path. Format should be 'gs://bucket_name/blob_name'.")

        bucket_name, blob_name = parts
        filename = blob_name.split('/')[-1]

        # Download the file from GCP
        file_like_object = await gcph.download_from_gcp(bucket_name, blob_name, filename)
        if file_like_object:
            content = file_like_object.read()
            response_json = json.loads(content)

        existing_applicant: Applicant = Applicant.get_id_by_gcp_path(session=session, gcp_path=gspath)
        job_code = Job.get_code_with_id(session=session, id=existing_applicant.job_id)
        if not existing_applicant:
            raise HTTPException(status_code=404, detail=f'Applicant with id as {gspath} was not found')

        # Flatten and process the data for Solr
        flattened_data_solr = await jsonh.flatten_resume_data_solr(response_json)
        flattened_data_solr = datah.convert_nulls_to_empty_strings(flattened_data_solr)
        flattened_data = await jsonh.flatten_resume_data(response_json)
        flattened_data = datah.convert_nulls_to_empty_strings(flattened_data)
        flattened_data_solr['applicant_uuid'] = existing_applicant.uuid
        flattened_data_solr['stage_uuid'] = existing_applicant.stage_uuid
        flattened_data_solr['job_code'] = job_code

        # Upload data to Solr
        response = await solrh.upload_to_solr(flattened_data_solr)
        if response["status_code"] != 200:
            raise Exception("Service unavailable (503). The API is temporarily down.")

        # Upload flattened data to GCP
        json_string = json.dumps(flattened_data_solr, indent=4)
        with SpooledTemporaryFile() as temp_file:
            temp_file.write(json_string.encode("utf-8"))
            temp_file.seek(0)
            destination_blob_name = f"s5/{filename}_solr.json"
            file_upload = await gcph.upload_to_gcp(bucket_name, temp_file, destination_blob_name)

        # Update the applicant's status in the database
        status = {
            "stage": "at stage 5 upload",
            "status": "success",
            "message": "The file is converted to JSON and uploaded to Solr",
            "api_start_time": api_start_time.isoformat(),
            "api_end_time": datetime.now(timezone.utc).isoformat()
        }
        details = flattened_data
        details["original_resume"] = request.original_resume
        details["file_upload"] = request.payload
        existing_applicant.details = details 
        existing_applicant.status['stages'].append(status)
        existing_applicant.status['overall_status'] = "success"
        existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
        flag_modified(existing_applicant, 'status')
        existing_applicant.update(session=session)

        return {
            "status": 200,
            "message": "success",
            "flattened_resume_solr": flattened_data_solr,
            "file_upload": file_upload
        }

    except Exception as e:
        # Handle errors and update status as "failed"
        api_end_time = datetime.now(timezone.utc)
        status = {
            "stage": "at stage 5 upload",
            "status": "failed",
            "message": str(e),
            "api_start_time": api_start_time.isoformat(),
            "api_end_time": api_end_time.isoformat()
        }
        existing_applicant: Applicant = Applicant.get_id_by_original_path(session=session, gcp_path=request.original_resume)
        if existing_applicant:
            existing_applicant.status['stages'].append(status)
            existing_applicant.status['overall_status'] = "failed"
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            existing_applicant.update(session=session)

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-status")
async def process_file_paths(
    payload: FilePathPayload,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    try:
        file_paths = payload.file_paths

        if not file_paths:
            raise HTTPException(status_code=400, detail="File paths list cannot be empty")

        # Fetch all applicants in a single database call
        applicants = Applicant.get_all_by_original_path(session=session, file_paths=file_paths)
        print("the type of applicants",type(applicants))
        if not applicants:
            raise HTTPException(status_code=404, detail="No matching records found for the provided file paths")

        statuses = []
        overall_statuses = []

        # Process the fetched applicants
        for applicant in applicants:
            # Parse the status JSON
            status_json = applicant.status  # Assuming `status` is stored as JSON
            overall_statuses.append(status_json.get("overall_status") if status_json else None)
            
            if isinstance(status_json, dict):
                statuses.append(
                    {
                        "resume": applicant.details["original_resume"],  # Use the `gcp_path` from the applicant record
                        "stages_status": status_json  # Assuming `status` contains stages
                    }
                )

        # Determine the overall process status
        process = "Not Completed" if "In progress" in overall_statuses else "Completed"

        return {
            "statuses": statuses,
            "process" : process
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException as e:
        raise e
    
