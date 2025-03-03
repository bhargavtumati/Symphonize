import requests, os
from fastapi import HTTPException, Header, Depends, status

# Replace these with your actual API keys
OTPLESS_CLIENT_ID = os.getenv("OTPLESS_CLIENT_ID")
OTPLESS_CLIENT_SECRET = os.getenv("OTPLESS_CLIENT_SECRET")
OTPLESS_VERIFY_URL = "https://user-auth.otpless.app/v1/sessions/validate-session"

async def verify_otpless_token(token: str = Header(...,description="Session token for Otpless")) -> None:
    """
    Dependency to verify session token from Otpless.
    Raises HTTPException if token is invalid.
    """
    headers = {
        "clientId": OTPLESS_CLIENT_ID,
        "clientSecret": OTPLESS_CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    payload = {"sessionToken": token}

    try:
        response = requests.post(OTPLESS_VERIFY_URL, headers=headers, json=payload)
        response_data = response.json()
        print('response',response,response_data)
        if response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]:
            raise HTTPException(
                status_code=response.status_code,
                detail=response_data.get("description")
            )
        if response.status_code == status.HTTP_200_OK:
            return response_data

    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again!"
        )
