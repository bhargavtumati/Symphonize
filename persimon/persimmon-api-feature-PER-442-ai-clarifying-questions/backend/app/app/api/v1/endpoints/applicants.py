from fastapi import APIRouter, Depends,status,HTTPException
from app.services import applicants as ap 
from app.api.v1.endpoints.models.applicant_model import ApplicantPartialUpdate,FilterRequest
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.helpers import db_helper as dbh,solr_helper as solrh
from fastapi import APIRouter, UploadFile, File
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers.math_helper import get_pagination
from app.models.applicant import Applicant
from app.models.stages import Stages
from typing import List,Optional, Dict
from uuid import UUID
import httpx
import os
import re
from app.helpers import s3_helper as s3h, solr_helper as solrh

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}


from fastapi import APIRouter, UploadFile, File
from typing import List
from pathlib import Path
import httpx

router = APIRouter()
SOLR_BASE_URL=os.getenv("SOLR_BASE_URL")


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
        applicant_uuids = [str(uuid) for uuid in applicants.applicant_uuids]
        stage_uuid = str(applicants.stage_uuid)
        stage_name = ''
        if len(applicant_uuids) > 0:
            recruiter_job_stages = Stages.get_by_id(session=session, job_id=job_id)
            if recruiter_job_stages:
                for stage in recruiter_job_stages.stages:
                    if stage['uuid'] == stage_uuid:
                        stage_name = stage['name']

            if not recruiter_job_stages:
                raise HTTPException(status_code=404, detail='Recruiter job stages not found')

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
                    return {"message": "No matching documents found for update in solr"}
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
    token: dict = Depends(verify_firebase_token)
):
    try:
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
        print(f"Solr response with filters: {solr_response_with_filters}")

        # Return the response from Solr
        return {
            "solr_response": solr_response_with_filters,
            "pagination": {
                'total_pages': pagination['total_pages'],
                'total_count': total_count
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/applicants/{applicant_id}", response_model=dict)
async def get_applicant_resume(applicant_id: int, db: Session = Depends(get_db), token: dict = Depends(verify_firebase_token)):
    """
    Retrieve an applicant's resume URL.

    Args:
        applicant_id (int): The ID of the applicant.
        db (Session): The database session.

    Returns:
        dict: The URL of the applicant's resume.
    """
    # Fetch the applicant
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Fetch resume file path from the applicant details
    original_resume = applicant.details.get('orignal_resume')
    if not original_resume:
        raise HTTPException(status_code=404, detail="No resume found for the applicant")

    # Format the GCP path correctly
    bucket_name = 'persimmon-ai'
    original_resume = original_resume.replace('gs://persimmon-ai/', '')  # Remove GCP prefix

    # Generate the signed URL
    try:
        signed_url = await s3h.get_file_url_from_gcp(bucket_name, original_resume)
        if not signed_url:
            raise HTTPException(status_code=500, detail="Error generating the signed URL")
        return {"message": "Resume successfully fetched", "url": signed_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving the file: {str(e)}")
