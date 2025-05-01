import asyncio
import traceback
from app.db.session import get_db
from app.helpers.log_helper import log_execution_time
from app.models.applicant import Applicant
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.job import Job
from app.api.v1.endpoints.models.job_model import JobModel
from app.helpers import jd_helper as jdh , db_helper as dbh
from app.helpers import solr_helper as solrh
from app.helpers import match_score_helper as matchh

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
    enhanced_description = jdh.extract_features_from_jd(text=job.description, ai_clarifying_questions=job.ai_clarifying_questions)
    print('the enhanced job desciption is : ', enhanced_description)
    enhanced_description = enhance_jd(jd=enhanced_description,job=job)
    return {
        "id": job_exists.id,
        "code": job_exists.code,
        "title": job.title,
        "type": job.type.value,
        "status": job.status.value,
        "workplace_type": job.workplace_type.value,
        "location": job.location,
        "team_size": job.team_size,
        "currency": job.currency,
        "min_salary": job.min_salary,
        "max_salary": job.max_salary,
        "min_experience": job.min_experience,
        "max_experience": job.max_experience,
        "target_date": job.target_date,
        "description": job.description,
        "enhanced_description": enhanced_description,
        "is_posted_for_client": job.is_posted_for_client,
        "ai_clarifying_questions": [q.model_dump() for q in job.ai_clarifying_questions],
        "publish_on_career_page": job.publish_on_career_page,
        "publish_on_job_boards": job.publish_on_job_boards,
        "meta": dbh.update_meta(job_exists.meta, updated_by)
    }

def enhance_jd(jd: str, job: Job):
    jd.setdefault("salary", {})
    jd.setdefault("company_size", {})
    jd.setdefault("team_size", {})
    jd.setdefault("location", {})
    jd.setdefault("workmode", {})
    jd['salary']['currency'] = job.currency
    jd["salary"]["max_value"] = job.max_salary
    jd["salary"]["min_value"] = job.min_salary
    jd["company_size"]["value"] =  job.company.number_of_employees
    jd["company_size"]["preference"] =  "Good to have"
    jd["team_size"]["value"] = job.team_size
    jd["team_size"]["preference"] =  "Good to have"
    jd["location"]["first_priority"] = job.location
    jd["location"]["second_priority"] = "Any"
    jd["workmode"]["value"] = "Any"
    jd["industry_type"] = [{
        "name": job.company.industry_type,
        "pref": "Must have",
        "min": job.min_experience,
        "max": job.max_experience
    }]
    return jd


@log_execution_time
async def generate_ai_score_with_job_description(
    job_code: str,
    job_description: str,
):
    try:
        db_gen = get_db()
        session = next(db_gen) 
        job_details = Job.get_by_code(session=session, code=job_code)
        if not job_details:
            raise HTTPException(status_code=404, detail="Job not found")

        response = await solrh.query_solr(job_code=job_code, rows=10000)
        documents = response.get("response", {}).get("docs", [])
        print("solr documents length : ", len(documents))
        if not documents:
            raise HTTPException(status_code=404, detail="No records found in Solr")

        semaphore = asyncio.Semaphore(20)
        async def fetch_resume(applicant_uuid: str, doc_id: str):
            async with semaphore:
                try:
                    applicant = Applicant.get_by_uuid(session=session, uuid=applicant_uuid)
                    stage_info = applicant.status.get("stages", [])[1]
                    message = stage_info.get("message", "")
                    gcs_path = message.split("is converted to")[1].strip()

                    resume_text = await read_gcs_text_file_local(gcs_path)
                    match_score = await matchh.calculate_match_percentage(
                        resume_text=resume_text,
                        jd_text=job_description
                    )

                    full_name = applicant.details["personal_information"]["full_name"]

                    # Update in DB
                    applicant.details["persimmon_score"] = match_score
                    Applicant.update_details_jsonb_key(
                        session=session,
                        applicant_uuid=applicant_uuid,
                        key="persimmon_score",
                        value=match_score
                    )

                    # Update in Solr
                    await solrh.update_applicant_document(doc_id, {
                        "persimmon_score": {"set": match_score}
                    })

                    return (full_name, match_score)
                except Exception:
                    traceback.print_exc()
                    return None

        all_results = []

        for chunk in chunkify(documents, 100): 
            tasks = [fetch_resume(doc["applicant_uuid"], doc["id"]) for doc in chunk if doc.get("applicant_uuid")]
            results = await asyncio.gather(*tasks)
            all_results.extend(filter(None, results))  

        all_results.sort(key=lambda x: x[1], reverse=True)

        return {
            "match_scores": all_results
        }

    except HTTPException:
        traceback.print_exc()
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


def chunkify(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


async def read_gcs_text_file_local(file_path: str):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return str(e)
