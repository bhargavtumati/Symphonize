from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from app.schemas.response_schema import create_response
from app.api.v1.endpoints.models.job_model import JobModel, JobPartialUpdate, JobDescription
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers import math_helper as mathh, db_helper as dbh ,jd_helper as jdh, solr_helper as solrh
from app.models.company import Company
from app.models.job import Job
from app.db.session import SessionLocal, get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from app.helpers.regex_helper import get_domain_from_email
import tldextract
from app.models.recruiter import Recruiter
from app.models.stages import Stages
from app.helpers.company_helper import get_or_create_company, handle_company_association
from app.helpers.job_helper import generate_job_code, prepare_job_data, enhance_jd
from app.helpers.stages_helper import prepare_default_stages, create_stages

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

@router.post("")
def create_job(
    job: JobModel,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    try:
        created_by = token["email"]
        existing_recruiter: Recruiter = Recruiter.get_by_email_id(session=session, email=created_by)
        if not existing_recruiter:
            raise HTTPException(status_code=404, detail="Recruiter not found")

        company_record, company_code = get_or_create_company(job=job, session=session, created_by=created_by)
        job_code = generate_job_code(session=session, company_code=company_code)
        enhanced_description = jdh.extract_features_from_jd(text=job.description, ai_clarifying_questions=job.ai_clarifying_questions)
        enhanced_description = enhance_jd(jd=enhanced_description,job=job)

        job_record = Job(
            title=job.title,
            code=job_code,
            type=job.type,
            status=job.status,
            workplace_type=job.workplace_type,
            location=job.location,
            team_size=job.team_size,
            min_salary=job.min_salary,
            max_salary=job.max_salary,
            min_experience=job.min_experience,
            max_experience=job.max_experience,
            target_date=job.target_date,
            description=job.description,
            enhanced_description=enhanced_description,
            is_posted_for_client=job.is_posted_for_client,
            company_id=company_record.id,
            ai_clarifying_questions=[q.model_dump() for q in job.ai_clarifying_questions],
            publish_on_career_page=job.publish_on_career_page,
            publish_on_job_boards=job.publish_on_job_boards,
        )
        job_data: Job = job_record.create(session=session, created_by=created_by)
        create_stages(session=session, recruiter_id=existing_recruiter.id, job_id=job_data.id, email=created_by)
        
        return {
            "message": "Job created successfully",
            "data": job_data,
            "status": status.HTTP_201_CREATED,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('')
def get_jobs(
    page: int,
    code:Optional[str] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
    client_name: Optional[str] = None,
    target_date: Optional[str] = None,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
    sort:Optional[str]=None
):

    try:
        sort_type=None
        sort_value=None
        created_by = token['email']
        if sort:    
            sort=sort.split(",")
            sort_type=sort[0]
            sort_value=sort[1]
        jobs=[]
        page_size = 12
        company = Company.get_by_name(session=session, company_name=client_name)
        total_count = Job.get_count(session=session, code=code, title=title, location=location, company=company, created_by_email=created_by, client_name=client_name,target_date=target_date)
        pagination = mathh.get_pagination(page=page,page_size=page_size,total_records=total_count)
        try:
            jobs = Job.get_all(session=session, limit=page_size, offset=pagination['offset'], code=code, title=title, location=location, company=company, created_by_email=created_by, client_name=client_name,target_date=target_date,sort_order=sort_type,sort_column=sort_value)
        except Exception as e:
            print(f"Error occurred while fetching the jobs: {str(e)}")
        posted_jobs = []
        for job in jobs:
            posted_job = {
                'id': job.id,
                'code': job.code,
                'title': job.title,
                'location': job.location,
                'posted_on': job.meta['audit']['created_at'],
                'target_date': job.target_date,
                'applicants':Job.get_all_applicants_count(session=session,job_id=job.id),
                'status': job.status
            }
            company = Company.get_by_id(session=session,company_id=job.company_id)
            posted_job['client_name'] = company.name
            posted_jobs.append(posted_job)
            
        return {
            'jobs': posted_jobs,
            'pagination': {
                'total_pages': pagination['total_pages'],
                'total_count': total_count
            },
            'status': status.HTTP_200_OK
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
def update_job(
    id: int,
    job: JobModel,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    try:
        updated_by = token["email"]
        job_exists: Job = Job.get_by_id(session=session, id=id, email=updated_by)
        if not job_exists:
            raise HTTPException(status_code=404, detail="Job not found")

        job_data = prepare_job_data(job, job_exists, updated_by)
        for key, value in job_data.items():
            setattr(job_exists, key, value)

        job_exists.meta.update(dbh.update_meta(job_exists.meta, updated_by))
        company_data = handle_company_association(job, job_exists, session, updated_by)
        job_data = job_exists.update(session=session)

        return {
            "message": "Job updated successfully",
            "data": {"job": job_data, "company": company_data},
            "status": status.HTTP_200_OK,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/{id}')
def get_job_by_id(
    id: int,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)):
    try:
        email = token['email']
        job_data: Job = Job.get_by_id(session=session, id=id, email=email)

        if not job_data:
            raise HTTPException(status_code=404, detail="Job not Found")
        
        company_data = Company.get_by_id(session=session, company_id=job_data.company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company or client not Found")

        return {
            "job": job_data,
            "company": company_data,
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{id}")
def update_job_partial(id: int, job_update: JobPartialUpdate, session: Session = Depends(get_db), token: dict = Depends(verify_firebase_token)):
    try:
        updated_by = token['email']
        existing_job: Job = Job.get_by_id(session=session, id=id, email=updated_by)
        if not existing_job:
            raise HTTPException(status_code=404, detail="Job not Found")
        
        update_data = job_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_job, key, value)
        existing_job.meta.update(dbh.update_meta(existing_job.meta, updated_by))
        existing_job.update(session=session)
        return {
            "message": "Job status updated successfully",
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-ai-clarifying-questions")
def generate_ai_clarifying_questions(
    input: JobDescription,
    token: dict = Depends(verify_firebase_token)
):
    try:
        serialized_input = input.model_dump()
        enhanced_description = jdh.extract_features_from_jd(text=serialized_input["description"])

        if "error" in enhanced_description:
            raise HTTPException(status_code=500, detail=str(enhanced_description["error"]))
        
        return {
            "enhanced_description": enhanced_description
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/')
def get_all_jobs_for_given_domain(
    domain: str,
   # token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        # Extract email from the token
        #email = token['email']
        
        # Query all jobs
        jobs_data = session.query(Job).filter(Job.meta["audit"]["created_by"]["email"].astext.ilike(f"%{domain}%"),
        Job.publish_on_career_page == True).all()

        if not jobs_data:
            raise HTTPException(status_code=404, detail="No jobs found for this domain")
        
     
        
        return {
            "jobs": jobs_data,
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get('get_job_by/{id}/public')
def get_job_by_id_public(
    id: int,
    session: Session = Depends(get_db)):
    try:
        
        job_data: Job = Job.get_by_id(session=session, id=id)

        if not job_data:
            raise HTTPException(status_code=404, detail="Job not Found")
        
        company_data = Company.get_by_id(session=session, company_id=job_data.company_id)
        if not company_data:
            raise HTTPException(status_code=404, detail="Company or client not Found")

        return {
            "job": job_data,
            "company": company_data,
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    