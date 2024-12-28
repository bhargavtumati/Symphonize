from app.helpers import zoho_helper as zohoh, classifier_helper as classifierh
from app.models.zrapplicant import ZrApplicant
from app.models.resume import Resume
from app.models.candidacy import Candidacy
from app.models.zrjob import ZrJob
from app.core.config import settings
import json
from sqlalchemy.orm import Session

async def classify(candidate_id: str, applicant_id: str, job_id: str, session: Session):
    attachments = await zohoh.get_attachments(candidate_id)
    applicant = ZrApplicant(
        name="",
        description="",
        candidate_id=candidate_id,
        applicant_id=applicant_id,
        job_id=job_id,
        attachments=attachments,
    )

    existing_applicant = ZrApplicant.get_by_id(session=session,applicant_id=applicant_id)

    if existing_applicant is None:
        applicant.create(session=session)
    
    attachment_id = attachments['data'][0]['id']
    attachment = await zohoh.get_attachment_by_id(candidate_id=candidate_id, attachment_id=attachment_id)

    existing_resume = Resume.get_by_id(session=session, attachment_id=attachment['attachment']['id'])

    if existing_resume is None:
        resume = Resume(detail=attachment, features={})
        persimmon_resume_id = resume.create(session=session)
    else:
        persimmon_resume_id = existing_resume.id

    job = await zohoh.get_job_by_id(job_id=job_id)

    existing_job = ZrJob.get_by_id(session=session, job_id=job["job"]["id"])

    if existing_job is None:
        zrjob = ZrJob(detail=job, features={})
        persimmon_job_id = zrjob.create(session=session)
    else:
        persimmon_job_id = existing_job.id

    if job["job"]["id"] and attachment["attachment"]["id"]:
        classifierh.run_once()
        #Concat resume extracted text and job description
        message = job["job"]["job_description"] + " " + attachment["attachment"]["text"]
        result, probs = classifierh.classify_message(message=message, model_version=settings.CLASSIFIER_VERSION, vectorizer_version=settings.VECTORIZER_VERSION)

        match_score = str(round(probs[classifierh.get_class_key('Match')] * 100, 2))
        
        probabilities = []
        for i, prob in enumerate(probs):
            probabilities.append(
                {
                    "label": classifierh.class_labels[i],
                    "probability": round(float(prob), 4)
                }
            )

        match = {
            "result": result,
            "score": match_score,
            "probabilities": probabilities
        }

        #create candidacy
        candidacy_record = Candidacy(job_id=persimmon_job_id, resume_id=persimmon_resume_id, match=match)
        candidacy_record.create(session=session)

        # Get applicant details
        applicant_details = await zohoh.get_applicant_by_id(applicant_id=applicant_id)
        applicant_details["data"][0]["Persimmon_Match_Percent"] = match_score 
        applicant_details["data"][0]["Persimmon_Match_Label"] = result
        json_data = json.dumps(applicant_details)

        #update applicant details
        await zohoh.update_applicant_by_id(applicant_id=applicant_id, applicant_details=json_data)

