from sqlalchemy.orm import Session
from app.models.job import Job
from app.api.v1.endpoints.models.job_model import JobModel

def generate_job_code(session: Session, company_code: str):
    """
    Generates a unique job code.
    """
    if company_code:
        sequence_number = Job.get_next_sequence_number(session=session, company_code=company_code)
        return f"{company_code}{sequence_number:04d}"
    return None

def prepare_job_data(job: JobModel, job_exists: Job, updated_by: str) -> dict:
    """
    Prepares the data to update a job record.
    """
    return {
        "id": job_exists.id,
        "code": job_exists.code,
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
        "enhanced_description": job.enhanced_description,
        "is_posted_for_client": job.is_posted_for_client,
        "ai_clarifying_questions": [q.dict() for q in job.ai_clarifying_questions],
        "publish_on_career_page": job.publish_on_career_page,
        "publish_on_job_boards": job.publish_on_job_boards,
        "meta": job_exists.meta,
    }

def enhance_jd(jd: str, job: Job):
    jd.setdefault("salary", {})
    jd.setdefault("company_size", {})
    jd.setdefault("team_size", {})
    jd.setdefault("location", {})
    jd.setdefault("workmode", {})
    jd["salary"]["max_value"] = job.max_salary
    jd["salary"]["min_value"] = job.min_salary
    jd["company_size"]["value"] =  job.company.number_of_employees
    jd["company_size"]["preference"] =  "Good to have"
    jd["team_size"]["value"] = job.team_size
    jd["team_size"]["preference"] =  "Good to have"
    jd["location"]["first_priority"] = job.location
    jd["location"]["second_priority"] = "Any"
    jd["workmode"]["value"] = "Any"
    return jd
