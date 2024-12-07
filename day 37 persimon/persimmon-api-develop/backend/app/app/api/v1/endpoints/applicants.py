from fastapi import APIRouter, Depends, status, HTTPException
from app.services import applicants as ap
from app.api.v1.endpoints.models.applicant_model import (
    ApplicantPartialUpdate,
    FilterRequest,
)
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.helpers import db_helper as dbh, solr_helper as solrh
from fastapi import APIRouter, UploadFile, File

# from app.helpers.firebase_helper import verify_firebase_token
from app.helpers.math_helper import get_pagination
from app.models.applicant import Applicant
from app.models.stages import Stages
from typing import List, Optional, Dict
import httpx

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}


from fastapi import APIRouter, UploadFile, File
from typing import List
from pathlib import Path
import httpx

router = APIRouter()
SOLR_URL = "https://thoroughly-complete-cow.ngrok-free.app/solr"
COLLECTION_NAME = "persimmon_resumes"


@router.post("/upload-resume")
async def upload_resumes(
    job_id: int,
    job_code: str,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_db),
    # token: dict = Depends(verify_firebase_token)
):

    allowed_extensions = {"pdf", "docx"}
    errors = []
    success_files = []
    flatten_resumes = []
    created_by = "bharat@gmail.com"  # token['email']
    for file in files:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            detail = f"File '{file.filename}' has an unsupported file extension. Only '.pdf' and '.docx' files are allowed."
            errors.append(detail)
            continue
        file_success, error_message, flatten_resume = await ap.process_resume(
            file, session, created_by, job_id, job_code
        )
        
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
        "extracted_texts": flatten_resumes,
    }


@router.get("")
def get_applicants(
    job_id: int,
    page: int,
    stage_uuid: Optional[str] = None,
    name: Optional[str] = None,
    # token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    try:
        page_size = 20
        total_count = Applicant.get_count(
            session=session, job_id=job_id, stage_uuid=stage_uuid, name=name
        )
        pagination = get_pagination(
            page=page, page_size=page_size, total_records=total_count
        )
        posted_applicants = Applicant.get_all(
            session=session,
            limit=page_size,
            offset=pagination["offset"],
            job_id=job_id,
            stage_uuid=stage_uuid,
            name=name,
        )
        return {
            "applicants": posted_applicants,
            "pagination": {
                "total_pages": pagination["total_pages"],
                "total_count": total_count,
            },
            "status": status.HTTP_200_OK,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("")
async def partial_update(
    job_id: int,
    applicants: ApplicantPartialUpdate,
    session: Session = Depends(get_db),
    # token: dict = Depends(verify_firebase_token)
):
    try:
        updated_by = "bharat@gmail.com"  # token['email']
        applicant_uuids = applicants.applicant_uuids
        stage_uuid = applicants.stage_uuid
        stage_name = ""
        if len(applicant_uuids) > 0:
            recruiter_job_stages = Stages.get_by_id(session=session, job_id=job_id)
            if recruiter_job_stages:
                for stage in recruiter_job_stages.stages:
                    if stage["uuid"] == stage_uuid:
                        stage_name = stage["name"]

            if not recruiter_job_stages:
                raise HTTPException(
                    status_code=404, detail="Recruiter job stages not found"
                )

            params = {
                "q": f"uuid:({' OR '.join(applicant_uuids)})",
                "rows": len(applicant_uuids),
                "wt": "json",
            }

            async with httpx.AsyncClient() as client:
                solr_response = await client.get(
                    f"{SOLR_URL}/{COLLECTION_NAME}/select", params=params
                )
                solr_response.raise_for_status()
                documents = solr_response.json().get("response", {}).get("docs", [])

                updates = []
                for document in documents:
                    if document["uuid"][0] in applicant_uuids:
                        updates.append(
                            {"id": document["id"], "stage_uuid": {"set": [stage_uuid]}}
                        )

                if not updates:
                    return {"message": "No matching documents found for update in solr"}
                update_url = f"{SOLR_URL}/{COLLECTION_NAME}/update?commit=true"
                update_response = await client.post(update_url, json=updates)
                update_response.raise_for_status()

            for applicant_uuid in applicant_uuids:
                existing_applicant: Applicant = Applicant.get_by_uuid(
                    session=session, uuid=applicant_uuid
                )
                if not existing_applicant:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Applicant with id as {applicant_id} was not found",
                    )

                existing_applicant.stage_uuid = stage_uuid
                #     existing_applicant.meta.update(dbh.update_meta(existing_applicant.meta, updated_by))
                existing_applicant.update(session=session)

        return {
            "message": f"Successfully moved to {stage_name}",
            "status": status.HTTP_200_OK,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500, detail=f"Error connecting to Solr: {str(e)}"
        )


@router.post("/filter")
async def get_applicants_filter(
    request: FilterRequest,
    job_code: str,
    page: int,
    stage_uuid: Optional[str] = None,
    name: Optional[str] = None,
):
    try:
        # Log the job_id
        print(f"Job ID provided: {job_code}")

        # Pagination setup
        page_size = 20
        solr_response = await solrh.query_solr(job_code, stage_uuid)
        if solr_response:
            total_count = solr_response.get("response", {}).get("numFound", 0)
        else:
            total_count = 0
        print(f"the total count is: {total_count}")
        pagination = get_pagination(
            page=page, page_size=page_size, total_records=total_count
        )

        print(f"the offset is: {pagination['offset']} {pagination}")

        final_query, exclude_query = ap.construct_query(request)

        # Query Solr with filters
        query_parts = []
        if job_code:
            query_parts.append(f'job_code:"{job_code}"')
        if stage_uuid:
            query_parts.append(f'stage_uuid:"{stage_uuid}"')
        if name:
            query_parts.append(f'full_name:"{name}"')
        query = " AND ".join(query_parts)  # Combine query parts with AND

        solr_response_with_filters = await solrh.query_solr_with_filters(
            query=query,
            filters=final_query,
            rows=page_size,
            start=pagination["offset"],
            exclude=exclude_query,
        )
        print(f"Solr response with filters: {solr_response_with_filters}")

        # Return the response from Solr
        return solr_response_with_filters

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
