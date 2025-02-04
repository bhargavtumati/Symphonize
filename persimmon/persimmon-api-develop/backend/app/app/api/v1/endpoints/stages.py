from fastapi import APIRouter, Depends, HTTPException, status
from app.helpers.firebase_helper import verify_firebase_token
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.stages import Stages
from app.models.job import Job
from app.api.v1.endpoints.models.stages_model import StagesPartialUpdate
from app.helpers import db_helper as dbh
from app.helpers import stages_helper as stagesh
from app.models.applicant import Applicant
import httpx
import os

router = APIRouter()
SOLR_BASE_URL=os.getenv("SOLR_BASE_URL")

api_reference: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

@router.get("")
def get_stages(
    job_id: int,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        email = token['email']
        job_exists = Job.get_by_id(session=session, id=job_id, email=email)
        if not job_exists:
            raise HTTPException(status_code=404, detail="Job not found")

        stages: Stages = Stages.get_by_id(session=session, job_id=job_id)
        if not stages:
            raise HTTPException(status_code=404, detail="Stages not found")
        filtered_stages: list[dict] = stages.stages[1:]

        return {
            "stages": filtered_stages,
            "message": "Stages list retrieved successfully",
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch('')
async def update_stages(
    job_id: int,
    stages: StagesPartialUpdate,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        updated_by =  token['email']
        job_exists = Job.get_by_id(session=session, id=job_id, email=updated_by)
        if not job_exists:
            raise HTTPException(status_code=404, detail="Job not found")
            
        stages_dict = stages.model_dump()
        existing_stages: Stages = Stages.get_by_id(session=session, job_id=job_id)
        if not existing_stages:
            raise HTTPException(status_code=404, detail="Stages not found")

        restricted_stages_names = ['Shortlisted', 'Rejected', 'Selected']
        restricted_stages = [stage for stage in existing_stages.stages if stage['name'] in restricted_stages_names]
        stagesh.check_immutable_objects(stages_dict['stages'], restricted_stages)

        if len(stages_dict['stages']) > 18:
            raise HTTPException(status_code=400, detail="Maximum 20 stages are allowed")
        
        stage_names = [stage['name'] for stage in stages_dict['stages']]
        stage_uuids = [stage['uuid'] for stage in stages_dict['stages']]
        if len(set(stage_names)) != len(stage_names) or len(set(stage_uuids)) != len(stage_uuids):
            raise HTTPException(status_code=400, detail="Duplicate stages are not allowed")

        removed_stage_uuids = []
        stage_uuids = []
        for stage in stages_dict['stages']:
            stage['uuid'] = str(stage['uuid'])
            stage_uuids.append(stage['uuid'])

        for stage in existing_stages.stages:
            if stage['uuid'] not in stage_uuids:
                removed_stage_uuids.append(stage['uuid'])
        
        if len(removed_stage_uuids) > 0:
            params = {
                "q": f"stage_uuid:({' OR '.join(removed_stage_uuids)})", 
                "wt": "json"
            }

            async with httpx.AsyncClient() as client:
                solr_response = await client.get(f"{SOLR_BASE_URL}/resumes/select", params=params)
                solr_response.raise_for_status()  
                documents = solr_response.json().get("response", {}).get("docs", [])

                updates = []
                for document in documents:
                    if document["stage_uuid"] in removed_stage_uuids:
                        updates.append({
                            "id": document["id"],  
                            "stage_uuid": {"set": existing_stages.stages[0]['uuid']}  
                        })
                if len(updates) > 0:
                    update_url = f"{SOLR_BASE_URL}/resumes/update?commit=true"
                    try:
                        update_response = await client.post(update_url, json=updates)
                    except httpx.RequestError as e:
                        print(f"Request error occurred: {e}")
                    # TODO: Investigate 500 error coming from solr after atomic update happened successfully
            
            for removed_stage_uuid in removed_stage_uuids:
                existing_applicants: list[Applicant] = Applicant.get_by_stage_uuid(session=session, stage_uuid=removed_stage_uuid)
                for applicant in existing_applicants:
                    applicant.stage_uuid = existing_stages.stages[0]['uuid']
                    applicant.meta.update(dbh.update_meta(applicant.meta, updated_by))
                    applicant.update(session=session)

        
        existing_stages.meta.update(dbh.update_meta(existing_stages.meta, updated_by))
        updated_stages = [existing_stages.stages[0]] + stages_dict["stages"]
        existing_stages.stages = updated_stages
        existing_stages.update(session=session)

        return {
            "message": "Stages updated successfully",
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Solr: {str(e)}")
