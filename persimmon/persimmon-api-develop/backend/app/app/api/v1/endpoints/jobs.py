from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.response_schema import create_response
from app.api.v1.endpoints.models.job_model import JobModel, JobPartialUpdate, JobDescription, JobResponse
from app.helpers.firebase_helper import verify_firebase_token
from app.helpers import math_helper as mathh, db_helper as dbh ,jd_helper as jdh, solr_helper as solrh
from app.models.company import Company
from app.models.job import Job
from app.models.applicant import Applicant
from app.db.session import get_db
from sqlalchemy.orm import Session
from typing import Optional
from app.helpers.regex_helper import get_domain_from_email
import tldextract,json, httpx
from app.models.recruiter import Recruiter
from app.models.stages import Stages
from app.helpers.company_helper import get_or_create_company, handle_company_association
from app.helpers.job_helper import generate_job_code, prepare_job_data, enhance_jd
from app.helpers.stages_helper import prepare_default_stages, create_stages
import xml.etree.ElementTree as ET


router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}


@router.post("/post-job")
async def post_job(job: dict):
    target_websites = [
        "https://api.jobsite1.com/post-job",
        "https://api.jobsite2.com/post-job",
        "https://api.jobsite3.com/post-job"
    ]

    results = []
    for url in target_websites:
        try:
            response = await httpx.post(url, json=job)
            response.raise_for_status()
            results.append({"site": url, "status": "success", "data": response.json()})
        except httpx.HTTPStatusError as e:
            results.append({"site": url, "status": "failure", "error": str(e)})

    failed_posts = [result for result in results if result["status"] == "failure"]
    if failed_posts:
        raise HTTPException(status_code=500, detail={"message": "Failed to post job on some websites.", "results": results})

    return {"message": "Job posted successfully on all target websites.", "results": results}


@router.get('/{jobboard}/xml', summary="Get all jobs as XML feed", response_class=Response)
def get_all_jobs_as_xml(
    jobboard: str,
    session: Session = Depends(get_db)
):
    try:
        jobs = session.query(Job).filter(Job.publish_on_job_boards.contains([jobboard]))
        # Create the XML root element
        root = ET.Element("jobs")
        
        # Generate XML from the job data
        for job in jobs:
            job_element = ET.SubElement(root, "job")
            ET.SubElement(job_element, "id").text = str(job.id)
            ET.SubElement(job_element, "code").text = job.code
            ET.SubElement(job_element, "title").text = job.title
            ET.SubElement(job_element, "type").text = job.type.name
            ET.SubElement(job_element, "status").text = job.status.name
            ET.SubElement(job_element, "workplace_type").text = job.workplace_type.name
            ET.SubElement(job_element, "location").text = job.location
            ET.SubElement(job_element, "team_size").text = str(job.team_size)
            ET.SubElement(job_element, "min_salary").text = str(job.min_salary)
            ET.SubElement(job_element, "max_salary").text = str(job.max_salary)
            ET.SubElement(job_element, "min_experience").text = str(job.min_experience)
            ET.SubElement(job_element, "max_experience").text = str(job.max_experience)
            ET.SubElement(job_element, "target_date").text = str(job.target_date.isoformat())
            ET.SubElement(job_element, "description").text = job.description
            ET.SubElement(job_element, "enhanced_description").text = json.dumps(job.enhanced_description)
            ET.SubElement(job_element, "is_posted_for_client").text = str(job.is_posted_for_client)
            ET.SubElement(job_element, "company_id").text = str(job.company_id)
            ET.SubElement(job_element, "ai_clarifying_questions").text = json.dumps(job.ai_clarifying_questions)
            ET.SubElement(job_element, "publish_on_career_page").text = str(job.publish_on_career_page)
            ET.SubElement(job_element, "publish_on_job_boards").text = json.dumps(job.publish_on_job_boards)

            posted_on = job.meta.get('audit', {}).get('created_at', 'N/A')
            ET.SubElement(job_element, "posted_on").text = str(posted_on)

        # Convert XML to string
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        
        return Response(content=xml_str, media_type="application/xml")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/domain/{name}')
def get_all_jobs_for_given_domain(
    name: str,
    search_term: Optional[str] = None,
    session: Session = Depends(get_db)
):
    try:
        jobs_data = Job.search_jobs_by_domain(session=session, domain=name, search_term=search_term)
        if not jobs_data:
            raise HTTPException(status_code=404, detail=f'Jobs not found')
        
        return {
            "jobs": jobs_data,
            "message": "Jobs retrieved successfully",
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/code/{job_code}')
def get_job_by_code_in_career_page(
    job_code: str,
    session: Session = Depends(get_db)
):
    try:
        job_data = Job.get_by_code(session=session, code=job_code)
        if not job_data:
            raise HTTPException(status_code=404, detail=f'Job not found')
        
        return {
            "job": job_data,
            "message": "Job retrieved successfully",
            "status": status.HTTP_200_OK
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("",response_model=JobResponse)
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

        company_record = get_or_create_company(job=job, session=session, created_by=created_by)
        company_details: Company = Company.get_by_id(session=session, company_id=existing_recruiter.company_id)
        company_code = company_details.name.capitalize()[:3]
        job_code = generate_job_code(session=session, company_code=company_code)
        enhanced_description = jdh.extract_features_from_jd(text=job.description, ai_clarifying_questions=job.ai_clarifying_questions)
        print('the enhanced job desciption is : ', enhanced_description)
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
        
        return JobResponse(
            message= "Job created successfully",
            data= {
                "id" : job_data.id,
                "code": job_data.code
            },
            status=status.HTTP_201_CREATED
        )

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
    posted_on: Optional[str] = None,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
    sort:Optional[str]="desc,posted_on"
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
        total_count = Job.get_count(session=session, code=code, title=title, location=location, company=company, created_by_email=created_by, client_name=client_name, target_date=target_date, posted_on=posted_on)
        pagination = mathh.get_pagination(page=page,page_size=page_size,total_records=total_count)
        try:
            jobs = Job.get_all(session=session, limit=page_size, offset=pagination['offset'], code=code, title=title, location=location, company=company, created_by_email=created_by, client_name=client_name, target_date=target_date, posted_on=posted_on, sort_order=sort_type, sort_column=sort_value)
        except Exception as e:
            print(f"Error occurred while fetching the jobs: {str(e)}")
        posted_jobs = []
        for job in jobs:
            posted_job = {
                'id': job['id'],
                'code': job['code'],
                'title': job['title'],
                'location': job['location'],
                'posted_on': job['meta']['audit']['created_at'],
                'target_date': job['target_date'],
                'applicants': job['applicant_count'],
                'status': job['status'],
                'client_name': job['client_name']
            }
            posted_jobs.append(posted_job)
            
        return {
            'jobs': posted_jobs,
            'pagination': {
                'total_pages': pagination['total_pages'],
                'total_count': total_count
            },
            'status': status.HTTP_200_OK,
            'message': "Jobs list retrieved successfully"
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

        stages_existing: Stages = Stages.get_by_id(session=session, job_id=id)
        if not stages_existing:
            raise HTTPException(status_code=404, detail="Stages not found")
        stages =  stages_existing.stages
        shortlisted_uuid = None
        selected_uuid = None
        rejected_uuid = None

        for stage in stages:
            if stage['name'] == 'Shortlisted':
                shortlisted_uuid = stage['uuid']
            elif stage['name'] == 'Selected':
                selected_uuid = stage['uuid']
            elif stage['name'] == 'Rejected':
                rejected_uuid = stage['uuid']
        
        shortlisted_count = Applicant.get_count(session=session, job_id=id, stage_uuid=shortlisted_uuid)
        selected_count = Applicant.get_count(session=session, job_id=id, stage_uuid=selected_uuid)
        rejected_count = Applicant.get_count(session=session, job_id=id, stage_uuid=rejected_uuid)

        applicant_count = Job.get_all_applicants_count(session=session, job_id=id)

        return {
            "job": job_data,
            "company": company_data,
            "count": {
                "all_applicants": applicant_count,
                "shortlisted": shortlisted_count,
                "selected": selected_count,
                "rejected": rejected_count
            },
            "status": status.HTTP_200_OK,
            "message": "Retrieved job details successfully"
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
            "enhanced_description": enhanced_description,
            "status": status.HTTP_200_OK,
            "message": "Generated AI clarifying questions successfully" 
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
