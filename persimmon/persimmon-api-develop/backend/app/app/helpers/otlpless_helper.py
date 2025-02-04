import requests, os
from fastapi import HTTPException, Header, Depends

# Replace these with your actual API keys
OTPLESS_CLIENT_ID = os.getenv("OTPLESS_CLIENT_ID")
OTPLESS_CLIENT_SECRET = os.getenv("OTPLESS_CLIENT_SECRET")
OTPLESS_VERIFY_URL = "https://user-auth.otpless.app/auth/v1/validate/token"

async def verify_otpless_token(token: str = Header(...,description="Authentication token for Otpless")) -> None:
    """
    Dependency to verify token from Otpless.
    Raises HTTPException if token is invalid.
    """
    headers = {
        "clientId": OTPLESS_CLIENT_ID,
        "clientSecret": OTPLESS_CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    payload = {"token": token}

    try:
        response = requests.post(OTPLESS_VERIFY_URL, headers=headers, json=payload)
        response_data = response.json()
        print('response',response,response_data)
        if response_data.get("status") != "SUCCESS":
            raise HTTPException(
                status_code=response.status_code,
                detail=response_data.get("description","Something went wrong"),
            )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Otpless API: {str(e)}"
        )
