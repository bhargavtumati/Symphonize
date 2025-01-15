from app.api.v1.endpoints.models.job_model import JobModel
from sqlalchemy.orm import Session
import tldextract
from app.models.company import Company
from app.models.job import Job
from app.helpers import db_helper as dbh, regex_helper as regexh, job_helper as jobh

def get_or_create_company(job: JobModel, session: Session, created_by: str):
    """
    Retrieves or creates a company record based on job details and domain.
    """
    if job.is_posted_for_client:
        extracted = tldextract.extract(job.company.website)
        domain = extracted.domain + "." + extracted.suffix
    else:
        domain = regexh.get_domain_from_email(created_by)

    company_record = Company.get_by_domain(session=session, domain=domain)
    if not company_record:
        company_data = Company(**job.company.model_dump())
        company_data.domain = domain
        company_record = company_data.create(session=session, created_by=created_by)
    return company_record

def update_or_create_company(
    job: JobModel,
    company_exists: Company,
    domain: str,
    session: Session,
    updated_by: str,
) -> dict:
    """
    Updates an existing company or creates a new one if it doesn't exist.
    """
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
            "meta": company_exists.meta,
        }

        for key, value in company_data.items():
            setattr(company_exists, key, value)

        company_exists.meta.update(dbh.update_meta(company_exists.meta, updated_by))
        return company_exists.update(session=session).to_dict()

    new_company = Company(**job.company.model_dump())
    new_company.domain = domain
    return new_company.create(session=session, created_by=updated_by).to_dict()

def handle_company_association(
    job: JobModel, job_exists: Job, session: Session, updated_by: str
) -> dict:
    """
    Handles the logic for associating or updating the company for the job.
    """
    if job.is_posted_for_client:
        extracted = tldextract.extract(job.company.website)
        domain = f"{extracted.domain}.{extracted.suffix}"
    else:
        domain = regexh.get_domain_from_email(job_exists.meta["audit"]["created_by"]["email"])

    company_exists: Company = Company.get_by_domain(session=session, domain=domain)
    company_data = {}

    if (job_exists.is_posted_for_client and job.is_posted_for_client) or (
        job.is_posted_for_client and not job_exists.is_posted_for_client
    ):
        company_data = update_or_create_company(
            job=job,
            company_exists=company_exists,
            domain=domain,
            session=session,
            updated_by=updated_by,
        )
        job_exists.company_id = company_data["id"]

    elif (job_exists.is_posted_for_client and not job.is_posted_for_client) or (
        not job_exists.is_posted_for_client and not job.is_posted_for_client
    ):
        if company_exists:
            job_exists.company_id = company_exists.id
    return company_data