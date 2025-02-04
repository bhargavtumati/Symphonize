from typing import Annotated
from fastapi import APIRouter, Query
from asyncer import asyncify, create_task_group, syncify
from app.core.config import settings
from app.schemas.response_schema import GetResponseBase, create_response
from app.helpers import zoho_helper

router = APIRouter()

api_reference: dict[str, str] = {
    "api_reference": "https://github.com/symphonize/persimmon-api"
}

@router.get("/")
def get_candidates() -> GetResponseBase:
    return create_response(message=f"Get all candidates", data={}, meta=api_reference)


@router.post("/{candidate_id}")
def create_candidate() -> GetResponseBase:
    return create_response(
        message="Successfully created candidate", data={}, meta=api_reference
    )


@router.get("/{candidate_id}/attachments/{attachment_id}")
async def get_attachment_by_id(
    candidate_id: str, attachment_id: str
) -> GetResponseBase:
    data = await zoho_helper.get_attachment_by_id(
        candidate_id=candidate_id, attachment_id=attachment_id
    )
    return create_response(
        message="Successfully retrieved and converted attachment", data=data, meta=api_reference
    )


@router.get("/{candidate_id}/attachments/{attachment_id}/download")
async def download_attachment_by_id(candidate_id: str, attachment_id: str):
    return await zoho_helper.download_attachment_by_id(
        candidate_id=candidate_id, attachment_id=attachment_id
    )
