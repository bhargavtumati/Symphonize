from typing import Optional, List
from fastapi import APIRouter, Query, Form, UploadFile, File
from asyncer import asyncify, create_task_group, syncify
from app.core.config import settings
import httpx
from app.schemas.response_schema import GetResponseBase, create_response
from app.helpers import classifier_helper as classifierh

router = APIRouter()

api_reference: dict[str, str] = {
    "api_reference": "https://github.com/symphonize/persimmon-api"
}


@router.get("/")
def get_resumes() -> GetResponseBase:
    return create_response(message=f"Get all resumes", data={}, meta=api_reference)


@router.get("/classify")
def classify_resumes() -> GetResponseBase:
    response = {}
    return create_response(
        message=f"Classify resumes", data=response, meta=api_reference
    )


@router.get("/{resume_id}")
def get_resume_by_id(resume_id: int) -> GetResponseBase:
    return create_response(
        message=f"Get resume with id {resume_id}", data={}, meta=api_reference
    )


@router.post("/process")
def process(
    job_description: str = Form(...),
    job_title: str = Form(...),
    company_name: Optional[str] = Form(None),
    classifier_version: str = Form(...),
    vectorizer_version: str = Form(...),
    files: List[UploadFile] = File(...),
):
    return classifierh.process_resumes(
        job_description,
        job_title,
        company_name,
        classifier_version,
        vectorizer_version,
        files,
    )
