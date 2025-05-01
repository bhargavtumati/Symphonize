from app.helpers import ai_helper as aih
from app.helpers import gcp_helper as gcph
from app.helpers import db_helper as dbh
from app.models.applicant import Applicant
from pydantic import BaseModel
from app.api.v1.endpoints.models.resume_model import ResumeParseRequest
from app.helpers.firebase_helper import verify_firebase_token, get_base_url
from app.helpers.log_helper import log_execution_time
from app.helpers import solr_helper as solrh
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from tempfile import SpooledTemporaryFile
from sqlalchemy.orm import Session
from app.db.session import get_db
from datetime import datetime, timezone
from sqlalchemy.orm.attributes import flag_modified
import json
import logging
import os
import time
import re

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()

router = APIRouter()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=log_level)
logger = logging.getLogger("ResumeParsing")


class JDRequest(BaseModel):
    input: Optional[str] = None
    prompt: str


@router.post("/generate-job-description")
async def generate_job_description(
    jd: JDRequest, token: dict = Depends(verify_firebase_token)
):
    try:
        if not jd.input and not jd.prompt:
            raise HTTPException(
                status_code=400,
                detail="Please provide either input or prompt for job description generation",
            )

        if not jd.input and jd.prompt:
           full_input = (
                 jd.prompt
                 + "\n"
                 + "Please generate a job description that includes all the skills and expertise mentioned above, ensuring the total number of characters are strictly above 3500, including spaces, special characters also."
            )
        
        elif jd.input and jd.prompt:
            full_input = (
                (jd.input)
                 + "\n"
                 + jd.prompt
                 + "\n"
                 + "Please do required changes without changing the entire job description, ensuring the total number of characters are strictly above 3500, including spaces, special characters also."
            )

        ai_response = aih.get_gemini_ai_response(input=full_input)

        return {
            "job_description": ai_response,
            "status": status.HTTP_200_OK,
            "message": "Job description generated successfully"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/extract-features-from-resumes")
# async def gemini_response(
class TextToJsonRequest(BaseModel):
    source: str
    uuid: str
    match_score: str


from pathlib import Path

@router.post("/text-to-json")
@log_execution_time
async def text_to_json(
    request: TextToJsonRequest,
    session=Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    token: dict = Depends(verify_firebase_token),
    base_url: str = Depends(get_base_url),
):
    logger.info("invoked text-to-json")
    match_score = request.match_score
    try:
        api_start_time = datetime.now(timezone.utc)
        text = ""
        generated_json = ""
        file_upload = None
        updated_by = token["email"]
        original_token = credentials.credentials
        source = Path(request.source)
        destination = source.parent.parent / "json" / (source.stem + ".json")

        try:
            with open(request.source, "r",encoding="utf-8") as reader:
                text = reader.read()
            print("the text after the read is ",text)
            generated_json = await aih.extract_features_from_resume(text)
            #print("this is beofre the 1st exception", generated_json)
            with open(destination, "w",encoding="utf-8") as writer:
                writer.write(generated_json)
            file_upload = str(destination)
            logger.info(f"========= successfully written to {destination}")
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print("Rate limit hit. Adjust API usage or increase quotas.")
                time.sleep(60)
                generated_json = await aih.extract_features_from_resume(text)
                if "429" in str(generated_json) or "ResourceExhausted" in str(generated_json):
                    raise ValueError("second Rate limit hit. Adjust API usage or increase quotas.")
                #10 retries
                # for retry_count in range(10):  # Retry up to 10 times
                #     generated_json = await aih.extract_features_from_resume(text)

                #     if "429" not in str(generated_json) and "ResourceExhausted" not in str(generated_json):
                #         print(f"Success after {retry_count + 1} attempt(s).")
                #         break  # Exit the retry loop on success

                #     print(f"Rate limit hit. Retrying... ({retry_count + 1}/10)")
                #     time.sleep(60)  # 1-minute delay before retrying

                # Check if retries were exhausted without success
                # if generated_json is None or "429" in str(generated_json) or "ResourceExhausted" in str(generated_json):
                #     raise ValueError("Rate limit hit after maximum retries. Adjust API usage or increase quotas.")
                with open(destination, "w",encoding="utf-8") as writer:
                    writer.write(generated_json)
                print("the file upload will be happening to the destination ", destination)
                file_upload = str(destination)
              #1min delay 
              #retry mechanism to work on that file .
            else:
                raise HTTPException(
                    status_code=400, detail="the llm response is not generated"
                )

        api_end_time = datetime.now(timezone.utc)
        if file_upload:
            status = {
                "stage": "text-to-json",
                "status": "success",
                "message": f"{str(source)} is converted to {str(destination)}",
                "start": api_start_time.isoformat(),
                "end": api_end_time.isoformat(),
            }

            existing_applicant: Applicant = Applicant.get_by_uuid(session=session, uuid=request.uuid)
            if not existing_applicant:
                raise HTTPException(status_code=404, detail="Applicant was not found")
            existing_applicant.status["stages"].append(status)
            existing_applicant.meta.update(
                dbh.update_meta(existing_applicant.meta, updated_by)
            )
            flag_modified(existing_applicant, "status")
            print("the existing applicant object : ", existing_applicant)
            try:
                existing_applicant.update(session=session)
            except Exception as e:
                logger.error(f"Error updating applicant: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"error updating applicant {str(e)}",
                )
            try:
                pubsub_message = {
                    "endpoint": f"{base_url}/api/v1/resumes/flatten",
                    "token": original_token,
                    "payload": {
                        "source": str(destination),
                        "uuid": request.uuid,
                        "match_score": match_score
                    },
                }

                pubsub_response = await gcph.send_message_to_pubsub(
                    pubsub_message, topic_name = os.getenv("TOPIC_NAME")
                )
                logger.info(f"Pub/Sub message sent: {pubsub_response}")                
            except Exception as e:
                logger.error(f"Failed to send Pub/Sub message: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to send Pub/Sub message: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Unable to parse the file or upload the JSON to GCP",
            )

        if generated_json:
            return {
                "status": "success",
                "message": f"generated {str(destination)} from {str(source)}",
                "generated_json": str(generated_json),
                "destination": file_upload,
            }
        else:
            return {
                "status": "failure",
                "message": f"Unable to process {str(source)}",
                "generated_json": None,
            }
    except Exception as e:
        logger.error(f"text-to-json exception: {str(e)}")
        try:
            existing_applicant = Applicant.get_by_uuid(
                session=session, uuid=request.uuid
            )
            print("the try block is after the existing applicant ", existing_applicant)
            if existing_applicant:
                status = {
                    "stage": "text-to-json",
                    "status": "failure",
                    "message": str(e),
                }
                existing_applicant.status["overall_status"] = "failed"
                existing_applicant.status["stages"].append(status)
                existing_applicant.meta.update(
                    dbh.update_meta(existing_applicant.meta, token["email"])
                )
                flag_modified(existing_applicant, "status")
                existing_applicant.update(session=session)
                logger.info(f"========calling delete_records_by_applicant_uuid for applicant_uuid : {request.uuid}")
                await solrh.delete_records_by_applicant_uuid(request.uuid)
                logger.error(f"Exception In Exception block while deleting record from solr for applicant_uuid : {request.uuid}, Error Mesaage: {str(e)}")
        except Exception as ex:
            logger.error(f"Failed to update applicant status: {str(ex)}")
        # Raise the original exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
