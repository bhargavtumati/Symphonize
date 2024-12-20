import uuid
from app.models.recruiter import Recruiter
from app.models.stages import Stages
from sqlalchemy.orm import Session

def prepare_default_stages():
    """
    Prepares the default stages for a job.
    """
    return [
        {"uuid": str(uuid.uuid4()), "name": "new"},
        {"uuid": str(uuid.uuid4()), "name": "Pre-Screened"},
        {"uuid": str(uuid.uuid4()), "name": "Shortlisted"},
        {"uuid": str(uuid.uuid4()), "name": "Interviewing"},
        {"uuid": str(uuid.uuid4()), "name": "Selected"},
        {"uuid": str(uuid.uuid4()), "name": "Rejected"},
    ]

def create_stages(session: Session, recruiter_id: int, job_id: int, email: str):
    """
    Creates the default stages for a job under a recruiter.
    """
    default_stages = prepare_default_stages()
    stages = Stages(recruiter_id=recruiter_id, job_id=job_id, stages=default_stages)
    stages.create(session=session, created_by=email)