from fastapi import APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from app.helpers import linkedin_helper as linkedinh
from app.helpers.firebase_helper import verify_firebase_token
from pydantic import BaseModel,ValidationError
from typing import Dict
import httpx

router = APIRouter()

class AuthCode(BaseModel):
    code: str

class LinkedInPostPayload(BaseModel):
    content: Dict

import logging

# Configure logging
logger = logging.getLogger(__name__)

LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"



api_reference: dict[str, str] = {
    "api_reference": "https://github.com/symphonize/persimmon-api"
}


@router.post("/access-token")
async def get_access_token(auth: AuthCode):
    token_data = await linkedinh.fetch_access_token(auth.code)
    return token_data

@router.get("/profile")
async def get_linkedin_profile(access_token: str):
    profile_data = await linkedinh.fetch_linkedin_profile(access_token)
    return profile_data


@router.post("/post-job")
async def post_linkedin_job(
    payload: LinkedInPostPayload,
    access_token: str,
    token: dict = Depends(verify_firebase_token)
):
    headers = await linkedinh.get_linkedin_headers(access_token)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(LINKEDIN_API_URL, json=payload.content, headers=headers)
            print("response is : ",response)
            response.raise_for_status()

            return {"message": "Job post successfully created", "response_data": response.json()}

    except httpx.HTTPStatusError as e:
        print(f"the except block 2 {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"LinkedIn API error: {e.response.text}"
        )

    except httpx.RequestError as e:
        print(f"the except block 3 {e}")
        raise HTTPException(status_code=500,detail=f"Request error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal Server Error {str(e)}")
