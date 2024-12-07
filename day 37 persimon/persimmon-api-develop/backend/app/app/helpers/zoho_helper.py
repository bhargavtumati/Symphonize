from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import httpx
from io import BytesIO
import pdfplumber
from pydantic import BaseModel


# Model to handle file requests
class FileRequest(BaseModel):
    candidate_id: str
    attachment_id: str


# Configuration
BASE_URL = "https://recruit.zoho.com/recruit/v2"
TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
CLIENT_ID = "1000.6NXSPI1WGR7ANR96XM65PMD9QM8JSZ"
CLIENT_SECRET = "22cfc18e369ab7bcadce2b3cc6bd44f7b360307d20"
REFRESH_TOKEN = "1000.c9e6d85fc38f074df5f9b0b31b75be82.16326882d52e6ad230224fc8dec6dace"

# Token cache
token_cache = {"access_token": None, "expires_at": datetime.utcnow()}


async def fetch_bearer_token() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": REFRESH_TOKEN,
                "grant_type": "refresh_token",
            },
        )
        if response.status_code == 200:
            token_data = response.json()
            token_cache["access_token"] = token_data.get("access_token")
            token_cache["expires_at"] = datetime.utcnow() + timedelta(
                seconds=token_data.get("expires_in", 3600) - 60
            )  # Refresh before expiration
            return token_cache["access_token"]
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to retrieve bearer token",
            )


async def get_bearer_token() -> str:
    if (
        token_cache["access_token"] is None
        or datetime.utcnow() >= token_cache["expires_at"]
    ):
        return await fetch_bearer_token()
    return token_cache["access_token"]


async def get_attachment_by_id(candidate_id, attachment_id):
    bearer_token = await get_bearer_token()
    url = f"{BASE_URL}/Candidates/{candidate_id}/Attachments/{attachment_id}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient() as client:
        file_response = await client.get(url, headers=headers)

        if file_response.status_code == 200:
            with pdfplumber.open(BytesIO(file_response.content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return {"attachment": {"id": attachment_id, "type": "resume", "text": text}}
        else:
            message = f"Retrieval for candidate: {candidate_id}, attachment: {attachment_id} failed."
            raise HTTPException(status_code=file_response.status_code, detail=message)


async def get_attachments(candidate_id):
    bearer_token = await get_bearer_token()
    url = f"{BASE_URL}/Candidates/{candidate_id}/Attachments"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    print(headers)
    print(url)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get attachments by candidate: {candidate_id}",
            )


async def download_attachment_by_id(candidate_id, attachment_id):
    bearer_token = await get_bearer_token()
    url = f"{BASE_URL}/Candidates/{candidate_id}/Attachments/{attachment_id}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient() as client:
        file_response = await client.get(url, headers=headers)

        if file_response.status_code == 200:
            filename = f"{candidate_id}.pdf"
            file_stream = BytesIO(file_response.content)
            return StreamingResponse(
                file_stream,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )
        else:
            raise HTTPException(
                status_code=file_response.status_code, detail="File download failed"
            )


async def get_job_by_id(job_id):
    bearer_token = await get_bearer_token()
    url = f"{BASE_URL}/JobOpenings/{job_id}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            job_detail = response.json()["data"][0]["Job_Description"]
            return {"job": {"id": job_id, "job_description": job_detail}}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get job description from job: {job_id}",
            )


async def get_applicant_by_id(applicant_id):
    bearer_token = await get_bearer_token()
    url = f"{BASE_URL}/Applications/{applicant_id}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get applicant details for: {applicant_id}",
            )


async def update_applicant_by_id(applicant_id, applicant_details):
    bearer_token = await get_bearer_token()
    url = f"{BASE_URL}/Applications/{applicant_id}"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.put(url, data=applicant_details, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to update applicant details for: {applicant_id}",
            )
