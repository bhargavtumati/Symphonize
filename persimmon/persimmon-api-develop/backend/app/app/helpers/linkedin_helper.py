from fastapi import HTTPException
from typing import Dict
import httpx
import os
from dotenv import load_dotenv


load_dotenv()


CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URL')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')


async def get_linkedin_headers(access_token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }


async def fetch_access_token(code: str):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "PostmanRuntime/7.32.0",  # Mimic Postman
        }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)
        print("resosne : ",response.text,response)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch access token")
        return response.json()

async def fetch_linkedin_profile(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        profile_response = await client.get("https://api.linkedin.com/v2/userinfo", headers=headers)
        # print("profile response is : ",profile_response.text)
        if profile_response.status_code != 200:
            raise HTTPException(status_code=profile_response.status_code, detail="Failed to fetch profile")
        
        
        profile_data = profile_response.json()
        # print("the profile data is : ",profile_data['email'])
        
        return profile_data