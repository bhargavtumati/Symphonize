import uuid
from typing import Dict, List
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db 
from app.models.applicant import Applicant

def get_applicants_data(applicant_uuids: List[uuid.UUID], session: Session = Depends(get_db)) -> Dict:
    """Retrieve multiple applicants' details from DB in a single query."""
    
    uuid_strings = [str(applicant_uuid) for applicant_uuid in applicant_uuids]
    applicants = Applicant.get_applicants_by_uuid(session=session, uuids=uuid_strings)
   
    return {app.uuid: app.details for app in applicants if app}