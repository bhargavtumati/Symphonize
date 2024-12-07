import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.schemas.response_schema import GetResponseBase, create_response
from app.services import zrapplicants as sa
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import zrapplicant

router = APIRouter()

meta: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}


class CreateZrApplicantRequest(BaseModel):
    id: int
    name: str
    description: str | None = None


@router.get("/")
def get_applicants() -> GetResponseBase:

    return create_response(message=f"Get all applicants", data={}, meta=meta)


@router.get("/classify")
async def classify_applicant(
    context: str,
    candidate_id: str,
    applicant_id: str,
    job_id: str,
    session: Session = Depends(get_db),
):
    data = {
        "candidate_id": candidate_id,
        "applicant_id": applicant_id,
        "job_id": job_id,
    }
    await sa.classify(
        candidate_id=candidate_id,
        applicant_id=applicant_id,
        job_id=job_id,
        session=session,
    )
    meta["context"] = context
    meta["id"] = uuid.uuid4()
    return create_response(message=f"Classified applicants", data=data, meta=meta)


@router.get("/{applicant_id}")
def get_applicants(applicant_id: int) -> GetResponseBase:

    return create_response(
        message=f"Get applicant by id {applicant_id}", data={}, meta=meta
    )
