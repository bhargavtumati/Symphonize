from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.response_schema import create_response
from app.api.v1.endpoints.models.job_model import JobModel, JobPartialUpdate
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers import math_helper as mathh, db_helper as dbh ,jd_helper as jdh, solr_helper as solrh
from app.models.company import Company
from app.models.job import Job
from app.db.session import SessionLocal, get_db
from sqlalchemy.orm import Session
from typing import Optional
from app.helpers.regex_helper import get_domain_from_email
import tldextract


router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

@router.post('')
def create_job( 
    job: JobModel,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        created_by = token['email']
        company_code = ''
        enhanced_description = None
        if job.is_posted_for_client:
            extracted = tldextract.extract(job.company.website)
            domain = extracted.domain + '.' + extracted.suffix
        else:
            domain = get_domain_from_email(created_by)

        company_record: Company = Company.get_by_domain(session=session, domain=domain)
        if company_record:
            company_id = company_record.id
        else:
            company_data = Company(**job.company.model_dump())
            company_data.domain = domain
            company_record = company_data.create(session=session, created_by=created_by)
            company_id = company_record.id
        company_code = company_record.name.capitalize()[:3]
        if company_code:
            sequence_number = Job.get_next_sequence_number(session=session, company_code=company_code)
            job_code = f'{company_code}{sequence_number:04d}'

        job.ai_clarifying_questions = [q.dict() for q in job.ai_clarifying_questions]
        job_record =  Job(
            title= job.title,
            code= job_code,
            type= job.type,
            status= job.status,
            workplace_type = job.workplace_type,
            location= job.location,
            team_size= job.team_size,
            min_salary= job.min_salary,
            max_salary= job.max_salary,
            min_experience= job.min_experience,
            max_experience= job.max_experience,
            target_date= job.target_date,
            description= job.description,
            enhanced_description = jdh.extract_features_from_jd(job.description),
            is_posted_for_client= job.is_posted_for_client,
            company_id= company_id,
            ai_clarifying_questions= job.ai_clarifying_questions,
            publish_on_career_page= job.publish_on_career_page,
            publish_on_job_boards= job.publish_on_job_boards
        )
        
        job_data = job_record.create(session=session, created_by=created_by)
        return {
            "message": "Job created successfully",
            "data": job_data,
            "status": status.HTTP_201_CREATED
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('')
def get_jobs(
    page: int,
    id: Optional[int] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
    client_name: Optional[str] = None,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)):
    try:
        created_by = token['email']
        page_size = 12
        company = Company.get_by_name(session=session, company_name=client_name)
        total_count = Job.get_count(session=session, id=id, title=title, location=location, company=company, created_by_email=created_by, client_name=client_name)
        pagination = mathh.get_pagination(page=page,page_size=page_size,total_records=total_count)
        jobs = Job.get_all(session=session, limit=page_size, offset=pagination['offset'], id=id, title=title, location=location, company=company, created_by_email=created_by, client_name=client_name)
        posted_jobs = []
        for job in jobs:
            posted_job = {
                'id': job.id,
                'code': job.code,
                'title': job.title,
                'location': job.location,
                'posted_on': job.meta['audit']['created_at'],
                'target_date': job.target_date,
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

@router.put('/{id}')
def update_job(
    id: int,
    job: JobModel,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        updated_by = token['email']
        job_exists: Job = Job.get_by_id(session=session, id=id)
        if not job_exists:
            raise HTTPException(status_code=404, detail="Job not found")

        company_data = {}
        job_data = {
            "id": job_exists.id,
            "title": job.title,
            "type": job.type.value,
            "status": job.status.value,
            "workplace_type": job.workplace_type.value,
            "location": job.location,
            "team_size": job.team_size,
            "min_salary": job.min_salary,
            "max_salary": job.max_salary,
            "min_experience": job.min_experience,
            "max_experience": job.max_experience,
            "target_date": job.target_date,
            "description": job.description,
            "is_posted_for_client": job.is_posted_for_client,
            "ai_clarifying_questions": [q.dict() for q in job.ai_clarifying_questions],
            "publish_on_career_page": job.publish_on_career_page,
            "publish_on_job_boards": job.publish_on_job_boards,
            "meta": job_exists.meta
        }

        for key, value in job_data.items():
            setattr(job_exists, key, value)

        job_exists.meta.update(dbh.update_meta(job_exists.meta, updated_by))
        if job.is_posted_for_client:
            extracted = tldextract.extract(job.company.website)
            domain = extracted.domain + '.' + extracted.suffix
        else:
            domain = get_domain_from_email(job_exists.meta["audit"]["created_by"]["email"])
        
        company_exists: Company = Company.get_by_domain(session=session, domain=domain)

        if company_exists:
            company_data = company_exists.to_dict()

        if (job_exists.is_posted_for_client and job.is_posted_for_client) or (job.is_posted_for_client and not job_exists.is_posted_for_client):
            if company_exists:
                company_data = {
                    "id": company_exists.id,
                    "name": job.company.name,
                    "website": job.company.website,
                    "number_of_employees": job.company.number_of_employees,
                    "industry_type": job.company.industry_type,
                    "linkedin": job.company.linkedin,
                    "type": job.company.type.value,
                    "domain": domain,
                    "meta": company_exists.meta
                }

                job_exists.company_id = company_exists.id
                for key, value in company_data.items():
                    setattr(company_exists, key, value)
            
                company_exists.meta.update(dbh.update_meta(company_exists.meta, updated_by))
                company_data = company_exists.update(session=session).to_dict()
            else:
                new_client = Company(**job.company.model_dump())
                new_client.domain = domain
                company_data = new_client.create(session=session, created_by=updated_by)
                job_exists.company_id = company_data.id


        elif (job_exists.is_posted_for_client and not job.is_posted_for_client) or (not job_exists.is_posted_for_client and not job.is_posted_for_client):
            job_exists.company_id = company_exists.id

        job_data = job_exists.update(session=session)

        return { 
            "message": "Job updated successfully",
            "data": {
                "job": job_data,
                "company": company_data
            },
            "status": status.HTTP_200_OK
        }

    except Exception as e:
        print('error',str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/{id}')
def get_job_by_id(
    id: int,
    token: dict = Depends(verify_firebase_token),
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{id}")
def update_job_partial(id: int, job_update: JobPartialUpdate, session: Session = Depends(get_db), token: dict = Depends(verify_firebase_token)):
    try:
        updated_by = token['email']
        existing_job: Job = Job.get_by_id(session=session, id=id)
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))