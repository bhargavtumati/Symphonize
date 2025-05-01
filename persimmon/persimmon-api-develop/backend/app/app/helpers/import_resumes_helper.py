import asyncio
import logging
import os
import tempfile
import time
import traceback
import uuid
import json
import requests
import re
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
from app.helpers import db_helper as dbh,ai_helper as aih
from app.helpers import solr_helper as solrh, image_helper as imageh,async_helper as asynch
from app.models.stages import Stages
from app.schemas.response_schema import GetResponseBase, create_response
from app.helpers.firebase_helper import verify_firebase_token,get_base_url
from app.helpers.log_helper import log_execution_time
from app.services import applicants as ap
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import func
from sqlalchemy import cast, String
from typing import List, Dict, Optional
from pydantic import EmailStr
from app.models.template import Template
import logging
from pathlib import Path
from tika import parser


load_dotenv()
logger = logging.getLogger(__name__)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("ImportResumes")

@log_execution_time
async def run_resume_processing_tasks(results, created_by, job_description):
    await process_all_resumes(results, created_by, job_description)

@log_execution_time
async def process_all_resumes(results, created_by, job_description):
    async def handle_resume(r):
        try:
            await ap.resume_process(
                created_by=created_by,
                text=r["text"],
                job_description=job_description,
                destination=r["path"],
                applicant_uuid=r["uuid"]
            )
        except Exception as e:
            print(f"Error processing resume {r['uuid']}: {str(e)}")

    await asyncio.gather(*[handle_resume(r) for r in results])


class ExtractTextRequest(BaseModel):
    source: str  
    uuid: str

import aiofiles

@log_execution_time
async def extract_text(
    text:str,
    source: str ,
    uuid: str,
    created_by : EmailStr
):
    
    db_gen = get_db()
    session = next(db_gen) 
    try:
        api_start_time = datetime.now(timezone.utc)
        
        updated_by = created_by
        #original_token = credentials.credentials
        try:
            # parsed = parser.from_file(source)
            # print(f" the parsed is {parsed}")
            # text = parsed.get('content', '')
            # print(f"the text is after the parsing is  {text}")
            # text = text if text else ''

            # print(f" the text is {text}")
            source = Path(source)
            
            destination = source.parent.parent / "processed" / "text" / (source.stem + '.txt')
            async with aiofiles.open(destination, 'w',encoding="utf-8") as writer:
                await writer.write(text)
        except Exception as e:
            traceback.print_exc()
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
            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=uuid)
            if not existing_applicant:
                raise HTTPException(status_code=404, detail=f"Applicant was not found")
            existing_applicant.status['stages'].append(status)
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            print("the existing applicant is ", existing_applicant)
            try:
                existing_applicant.update(session=session)
            except Exception as e:
                logger.error(f"Error updating the applicant details: {str(e)}")
                raise HTTPException(
                    status_code=460, detail=f"error updating the applicant details {str(e)}"
                )
            
        else:
            status = {
                "stage":"document-to-text",
                "status": "failed",
                "message": f"{str(source)} is not converted to {str(destination)}",
                "start": api_start_time.isoformat(),
                "end": api_end_time.isoformat()
            }
            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=uuid)
            #print("the applicant data ", existing_applicant.details)
            existing_applicant.status['stages'].append(status)
            existing_applicant.status['overall_status'] = "failed"
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            print("the existing applicant object : ", existing_applicant)
            try:
                existing_applicant.update(session=session)
            except Exception as e:
                traceback.print_exc()
                logger.error(f"Error updating the applicant details: {str(e)}")
                raise HTTPException(
                    status_code=460, detail=f"error updating the applicant details {str(e)}"
                )
            try:
                logger.info(f"========calling delete_records_by_applicant_uuid for applicant_uuid : {uuid}")
                await solrh.delete_records_by_applicant_uuid(uuid)
            except Exception as e:
                logger.error(f"Exception In Exception block while deleting record from solr for applicant_uuid : {uuid}, Error Mesaage: {str(e)}")
            
        if text:
            return {
                "status": "success",
                "message": f"Text extracted successfully from {str(source)}.",
                "extracted_text": text,
                "file_upload": str(destination)
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
    finally:
        session.close()
    

async def upload_resumes(
    job_code:str,
    file: UploadFile,
    session: Session ,
    created_by : EmailStr
):
    """
    Endpoint to upload up to 100 resumes to GCP.
    """

    #capture the start time 
    api_start_time = datetime.now(timezone.utc)

    unique_id = None
    #print("the original token is : ",original_token)
    PERSIMMON_DATA=os.getenv("PERSIMMON_DATA", "/persimmon-data")
    ENVIRONMENT=os.getenv("ENVIRONMENT", "development")
    allowed_extensions = {"pdf", "docx"} 
    created_applicant = None 
    mobile_number_existance = None
    email_number_existance = None
    image_extracted = None
    applicant_uuid = None

    start_time = time.time()

    tasks = []
    errors = []
    uploaded_files = []
    images = []
    job_id = None
    stage_uuid = None

    try:
        job = Job.get_by_code(session=session, code=job_code)
        if job:
            job_id = job.id

    except Exception as e:
        raise HTTPException(status_code=404, detail="Job not found")

    ## get the new stage uuid for this job
    try:
        stages_existing: Stages = Stages.get_by_id(session=session, job_id=job_id)
        if  stages_existing and len(stages_existing.stages) > 0:
            stage_uuid = stages_existing.stages[0]['uuid']
    except Exception as e: 
        raise HTTPException(status_code=404, detail=f"Stages not found {str(e)}")

   
    try:
        unique_id = uuid.uuid4()
        original_file_name = f"{unique_id}_{file.filename}"

        destination = f"{PERSIMMON_DATA}/{ENVIRONMENT}/resumes/raw/{original_file_name}"

        content = await file.read()  # Read the file content
        #print(f"the main content is {content}")
        print(f"Attempting to write to {destination}")
        with open(destination, 'wb') as writer:
            writer.write(content)

        
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
        #print("the applicant uuid is : ",applicant_uuid,stage_uuid,job_id,details,status)
        applicant_data = Applicant(details=details, stage_uuid=stage_uuid, job_id=job_id, uuid=applicant_uuid,status=status)
        #print(f"the applicant data also {applicant_data} this is after the aapplicant")
        try:
            created_applicant = applicant_data.create(session=session,created_by=created_by)
        except Exception as e: 
            raise HTTPException(status_code=404, detail="Failed to create applicant")


    # Return the response
    return {
        "applicant_uuid": applicant_uuid,
        "uploaded_files": uploaded_files,
        "errors": errors,
        "total_files": file,
        "successful_uploads": len(uploaded_files),
        "failed_uploads": len(errors),
        "upload_duration_seconds": duration,
        "job_code": job_code,
        "pubsub_status": "Message sent successfully"
    }

class TextToJsonRequest(BaseModel):
    source: str
    uuid: str


async def call_with_retry(func, *args, retries=2, delay=5, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                if attempt == retries:
                    raise
                await asyncio.sleep(delay * attempt)
            else:
                raise



@log_execution_time
async def text_to_json(
    text: str,
    source: str,
    uuid: str,
    created_by: EmailStr
):
    from datetime import datetime, timezone
    import aiofiles
    from pathlib import Path
    import traceback

    logger.info(f"[{uuid}] text_to_json invoked")
    api_start_time = datetime.now(timezone.utc)
    email_id = created_by
    updated_by = created_by
    source = Path(source)
    destination = source.parent.parent / "json" / (source.stem + ".json")

    db_gen = get_db()
    session = next(db_gen) 

    try:
        # Step 1: Read file
        t1 = time.time()
        async with aiofiles.open(source, mode="r", encoding="utf-8") as reader:
            text = await reader.read()
        logger.info(f"[{uuid}] File read in {time.time() - t1:.2f}s")

        # Step 2: LLM JSON Extraction
        t2 = time.time()
        generated_json = await call_with_retry(aih.extract_features_from_resume, text)
        logger.info(f"[{uuid}] LLM extraction took {time.time() - t2:.2f}s")

        # Step 3: Write generated JSON to file
        t3 = time.time()
        if "429" in str(generated_json) or "ResourceExhausted" in str(generated_json):
            raise ValueError("Rate limit hit. Adjust API usage or increase quotas.")
        async with aiofiles.open(destination, mode="w", encoding="utf-8") as writer:
            await writer.write(generated_json)
        logger.info(f"[{uuid}] File write took {time.time() - t3:.2f}s")

        # Step 4: Update applicant status in DB (non-blocking)
        existing_applicant = await asynch.run_blocking(Applicant.get_by_uuid, session=session, uuid=uuid)
        if not existing_applicant:
            raise HTTPException(status_code=404, detail=f"Applicant not found")

        status = {
            "stage": "text-to-json",
            "status": "success",
            "message": f"{str(source)} converted to {str(destination)}",
            "start": api_start_time.isoformat(),
            "end": datetime.now(timezone.utc).isoformat(),
        }

        existing_applicant.status["stages"].append(status)
        existing_applicant.meta.update(
            dbh.update_meta(existing_applicant.meta, updated_by)
        )
        flag_modified(existing_applicant, "status")
        await asynch.run_blocking(existing_applicant.update, session=session)

        return {
            "status": "success",
            "message": f"Generated {destination} from {source}",
            "generated_json": generated_json,
            "destination": str(destination),
            "file_upload": str(destination)
        }

    except Exception as e:
        logger.error(f"[{uuid}] Exception: {e}")
        traceback.print_exc()

        # Attempt to update applicant status to failure
        try:
            existing_applicant = await asynch.run_blocking(Applicant.get_by_uuid, session=session, uuid=uuid)
            if existing_applicant:
                existing_applicant.status["overall_status"] = "failed"
                existing_applicant.status["stages"].append({
                    "stage": "text-to-json",
                    "status": "failure",
                    "message": str(e),
                })
                existing_applicant.meta.update(
                    dbh.update_meta(existing_applicant.meta, email_id)
                )
                flag_modified(existing_applicant, "status")
                await asynch.run_blocking(existing_applicant.update, session=session)

                await solrh.delete_records_by_applicant_uuid(uuid)
                logger.info(f"[{uuid}] Deleted records from Solr")
        except Exception as ex:
            logger.error(f"[{uuid}] Failed to update applicant status: {ex}")

        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    finally:
        session.close()
  
    
class Flatten(BaseModel):
    source: str
    uuid: str

import aiofiles

@log_execution_time
async def flatten(
    source : str,
    uuid: str,
    created_by : EmailStr,
    match_score: str
):
    api_start_time = datetime.now(timezone.utc)
    updated_by = created_by
    flattened_data_solr = None
    file_upload = None
    existing_applicant = None
    
    db_gen = get_db()
    session = next(db_gen) 

    try:
        source = Path(source)
        destination = source.parent.parent / "flat" / (source.stem + ".json")
        async with aiofiles.open(source, "r",encoding="utf-8") as reader:
            data_to_be_processed = await reader.read()
        json_to_be_processed = json.loads(data_to_be_processed) 
        
        existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=uuid)
        if not existing_applicant:
            raise HTTPException(status_code=404,detail=f"Applicant was not found")
        job_code = Job.get_code_with_id(session=session, id=existing_applicant.job_id)

        #logger.info(f"========= flattening for solr: json_to_be_processed: {json_to_be_processed}")
       # Flatten and process the data for Solr
        flattened_data_solr = await jsonh.flatten_resume_data_solr(json_to_be_processed)
        flattened_data_solr = await datah.convert_nulls_to_empty_strings(flattened_data_solr)
        flattened_data_solr['applicant_uuid'] = existing_applicant.uuid
        flattened_data_solr['stage_uuid'] = existing_applicant.stage_uuid
        flattened_data_solr['job_code'] = job_code
        flattened_data_solr['persimmon_score'] = match_score

        logger.info(f"========= flattening for database: json_to_be_processed: {json_to_be_processed}")
        flattened_data = await jsonh.flatten_resume_data(json_to_be_processed)
        flattened_data = await datah.convert_nulls_to_empty_strings(flattened_data)

        logger.info(f"========= before writing to destination {str(destination)}")
        # Upload data to Solr
        response = await solrh.upload_to_solr(flattened_data_solr)
        logger.info(f"========= solr upload done for applicant_uuid: {uuid}")
        logger.info(f"========= solrh.upload_to_solr(flattened_data_solr): response: {response}")
        if response["status_code"] != 200:
            raise Exception(f"status: {response['status_code']} message: {response['message']}")

        # Upload flattened data to GCP
        json_string = json.dumps(flattened_data_solr, indent=4)
        async with aiofiles.open(destination, "w",encoding="utf-8") as writer:
            await writer.write(json_string)
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

        logger.info(f"========= updated the status")

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
        existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=uuid)
        if existing_applicant:
            existing_applicant.status['stages'].append(status)
            existing_applicant.status['overall_status'] = "failed"
            existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
            flag_modified(existing_applicant, 'status')
            existing_applicant.update(session=session)
        
        try:
            logger.info(f"========calling delete_records_by_applicant_uuid for applicant_uuid : {uuid}")
            await solrh.delete_records_by_applicant_uuid(uuid)
        except Exception as e:
            logger.error(f"Exception In Exception block while deleting record from solr for applicant_uuid : {uuid}, Error Mesaage: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()