import os
import re
import time
import uuid
import json
import logging
from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime, timezone

from tika import parser

from pydantic import BaseModel

from fastapi import (
APIRouter, 
HTTPException,
UploadFile,
File, 
Form,
Depends
)
from fastapi.security import (
HTTPBearer, 
HTTPAuthorizationCredentials
)
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.db.session import get_db
from app.models.job import Job
from app.models.stages import Stages
from app.models.applicant import Applicant
from app.helpers import (
data_helper as datah,
gcp_helper as gcph,
json_helper as jsonh,
db_helper as dbh,
solr_helper as solrh, 
image_helper as imageh,
classifier_helper as classifierh,
match_score_helper as matchsh
)
from app.helpers.log_helper import log_execution_time
from app.helpers.firebase_helper import verify_firebase_token, get_base_url
from app.schemas.response_schema import GetResponseBase, create_response
from app.api.v1.endpoints.models.resume_model import  FilePathPayload, FilePath
from app.helpers.data_helper import read_file_as_pdf

IN_PROGRESS = "In progress"
AT_STAGE_ONE_UPLOAD = "at stage 1 upload"
GS_PATH = "gs://"
INVALID_GCP_PATH = "Invalid GCP path. Ensure it starts with 'gs://'."
INVALID_GCP_PATH_FORMAT = "Invalid GCP path. Format should be 'gs://bucket_name/blob_name'."
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
    return create_response(message="Get all resumes", data={}, meta=api_reference)


@router.get("/classify")
def classify_resumes() -> GetResponseBase:
    response = {}
    return create_response(
        message="Classify resumes", data=response, meta=api_reference
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


class ExtractTextRequest(BaseModel):
    source: str  
    uuid: str
    match_score: str

@router.post("/extract-text")
@log_execution_time
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
        match_score = request.match_score
        updated_by = token['email']
        original_token = credentials.credentials
        
        try:
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
            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
            if not existing_applicant:
                raise HTTPException(status_code=404, detail="Applicant was not found")
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
                        "uuid": request.uuid,
                        "match_score": match_score
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
            try:
                logger.info(f"========calling delete_records_by_applicant_uuid for applicant_uuid : {request.uuid}")
                await solrh.delete_records_by_applicant_uuid(request.uuid)
            except Exception as e:
                logger.error(f"Exception In Exception block while deleting record from solr for applicant_uuid : {request.uuid}, Error Mesaage: {str(e)}")
            
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


@router.post("/upload")
@log_execution_time
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

    unique_id = None
    original_token = credentials.credentials
    #print("the original token is : ",original_token)
    created_by = token['email']
    PERSIMMON_DATA=os.getenv("PERSIMMON_DATA", "/persimmon-data")
    ENVIRONMENT=os.getenv("ENVIRONMENT", "development")
    allowed_extensions = {"pdf", "docx"} 
    created_applicant = None 
    mobile_number_existance = None
    email_number_existance = None
    match_score = []

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

    errors = []
    uploaded_files = []
    images = []
    job_id = None
    stage_uuid = None
    job_description = None
    match_score_list = []

    try:
        job = Job.get_by_code(session=session, code=job_code)
        if job:
            job_id = job.id
            job_description = job.description

    except Exception as e:
        raise HTTPException(status_code=404, detail="Job not found")

    ## get the new stage uuid for this job
    try:
        stages_existing: Stages = Stages.get_by_id(session=session, job_id=job_id)
        if  stages_existing and len(stages_existing.stages) > 0:
            stage_uuid = stages_existing.stages[0]['uuid']
    except Exception as e: 
        raise HTTPException(status_code=404, detail=f"Stages not found {str(e)}")

    for file in files:
        try:
            unique_id = uuid.uuid4()
            original_file_name = f"{unique_id}_{file.filename}"

            destination = f"{PERSIMMON_DATA}/{ENVIRONMENT}/resumes/raw/{original_file_name}"

            content = await file.read()  # Read the file content
            print(f"Attempting to write to {destination}")
            with open(destination, 'wb') as writer:
                writer.write(content)

            parsed = parser.from_file(destination)
            text = parsed.get('content', '')
            text = text if text else ''
            
            
            mobile_pattern = re.compile(r"(?:\+\d{1,3}[-.\s]?)?\d{10}")

            email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

            mobile_matches = mobile_pattern.findall(text)

            email_matches = email_pattern.findall(text)

            if mobile_matches:
                mobile_number_existance = await Applicant.get_by_mobile_number(
                                            session=session, mobile_number=mobile_matches[0],
                                            job_id=job_id
                                            )

            if email_matches:
                email_number_existance = await Applicant.get_by_email_id( 
                                            session=session, email_id=email_matches[0],
                                            job_id=job_id
                                        )                
            if  email_number_existance or mobile_number_existance:
                raise HTTPException(
                    status_code=400,
                    detail=f"applicant already exists {destination}"
                )

            print(f"the text for  {text}") 
            match_score = await matchsh.calculate_match_percentage(text,job_description)
            match_score_list.append(match_score)

            print("successfully written to destination")
            uploaded_files.append(destination)
            file_extension = file.filename.split('.')[-1].lower()
            try:
                if file_extension == "pdf":
                    image_extracted = imageh.extract_first_face_from_pdf(BytesIO(content),file.filename)
                elif file_extension == "docx":
                    image_extracted = imageh.extract_first_face_from_docx(BytesIO(content),file.filename)
            except HTTPException as e:
                logger.error(f"Failed to extract face image from document: {str(e)}")
            images.append(image_extracted)
        except Exception as e:
            print(f"exception while converting document to text: {str(e)}")
            errors.append(str(e))

    if len(images) < len(uploaded_files):
        diff = len(uploaded_files) - len(images)
        diff = [None] * diff
        images.extend(diff)

    end_time = time.time()
    duration = round(end_time - start_time, 2)
    logger.info(f"Upload completed in {duration} seconds.")

    for index,uploaded_file in enumerate(uploaded_files):
        details = {
            "original_resume":uploaded_file,
            "context":"document-added",
            "file_upload":uploaded_file,
            "applicant_image": images[index]
            }
        api_end_time = datetime.now(timezone.utc)
        status = {
            "overall_status": IN_PROGRESS,
            "stages": [
                {
                    "stage": AT_STAGE_ONE_UPLOAD,
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
                    "uuid": applicant_uuid,
                    "match_score": str(match_score_list[index])
                }
            }
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


class Flatten(BaseModel):
    source: str
    uuid: str
    match_score: str

@router.post("/flatten")
@log_execution_time
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
    match_score = request.match_score

    try:
        source = Path(request.source)
        destination = source.parent.parent / "flat" / (source.stem + ".json")
        with open(request.source, "r",encoding="utf-8") as reader:
            data_to_be_processed = reader.read()
        json_to_be_processed = json.loads(data_to_be_processed) 
        
        existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
        if not existing_applicant:
            raise HTTPException(status_code=404,detail="Applicant was not found")
        job_code = Job.get_code_with_id(session=session, id=existing_applicant.job_id)

        logger.info(f"========= flattening for solr: json_to_be_processed: {json_to_be_processed}")
       # Flatten and process the data for Solr
        flattened_data_solr = await jsonh.flatten_resume_data_solr(json_to_be_processed)
        flattened_data_solr = datah.convert_nulls_to_empty_strings(flattened_data_solr)
        flattened_data_solr['applicant_uuid'] = existing_applicant.uuid
        flattened_data_solr['stage_uuid'] = existing_applicant.stage_uuid
        flattened_data_solr['persimmon_score'] = match_score
        flattened_data_solr['job_code'] = job_code

        logger.info(f"========= flattening for database: json_to_be_processed: {json_to_be_processed}")
        flattened_data = await jsonh.flatten_resume_data(json_to_be_processed)
        flattened_data = datah.convert_nulls_to_empty_strings(flattened_data)

        logger.info(f"========= before writing to destination {str(destination)}")
        # Upload data to Solr
        response = await solrh.upload_to_solr(flattened_data_solr)
        logger.info(f"========= solr upload done for applicant_uuid: {request.uuid}")
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
        details["applicant_image"] = existing_details["applicant_image"]
        details['persimmon_score'] = match_score
        details["file_upload"] = str(destination)
        existing_applicant.details = details
        existing_applicant.status['stages'].append(status)
        existing_applicant.status['overall_status'] = "success"
        existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
        flag_modified(existing_applicant, 'status')
        existing_applicant.update(session=session)

        logger.info("========= updated the status")

        return {
            "status": 200,
            "message": "success",
            "flattened_resume_solr": flattened_data_solr,
            "file_upload": file_upload
        }

    except Exception as e:
        logger.error("========= handling catch all")
        print(f"the exception as e {str(e)}")
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
        
        try:
            logger.info(f"========calling delete_records_by_applicant_uuid for applicant_uuid : {request.uuid}")
            await solrh.delete_records_by_applicant_uuid(request.uuid)
        except Exception as e:
            logger.error(f"Exception In Exception block while deleting record from solr for applicant_uuid : {request.uuid}, Error Mesaage: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            logger.info(f"========calling delete_duplicate_records for applicant_uuid : {request.uuid}")
            time.sleep(4)
            await solrh.delete_duplicate_records(request.uuid)
        except Exception as e:
            logger.error(f"Exception In Finally block while deleting duplicate records from solr for applicant_uuid : {request.uuid}, Error Mesaage: {str(e)}")
    

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
        process = "Not Completed" if IN_PROGRESS in overall_statuses else "Completed"

        return {
            "statuses": statuses,
            "process" : process
            }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    
    

@router.post("/get-file")
async def get_pdf(payload: FilePath, token: dict = Depends(verify_firebase_token)):
    try:
        print("file_path to download resume",payload.file_path)
        pdf_file = await read_file_as_pdf(payload.file_path)
        filename = os.path.basename(payload.file_path)
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        return StreamingResponse(pdf_file, media_type="application/pdf", headers=headers)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    