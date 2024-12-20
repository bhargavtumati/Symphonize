from fastapi import APIRouter, HTTPException
import httpx

# Replace with your Firebase Web API Key
FIREBASE_API_KEY = "AIzaSyDZA2U_UyQ3vMBvrV2yZimR5Pkcu-BGzRc"
FIREBASE_AUTH_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

router = APIRouter()

@router.post("/login")
async def login(
    email: str = "bhargav.tumati15@gmail.com",  # Default email
    password: str = "Bhargav@1234"              # Default password
):
    """
    Authenticate the user using Firebase Authentication.
    """
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True  # Ensure secure token is returned
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(FIREBASE_AUTH_URL, json=payload)

    if response.status_code == 200:
        token_data = response.json()
        return {
            "idToken": token_data["idToken"],  # JWT for authenticated user
            "refreshToken": token_data["refreshToken"],  # Token to refresh the session
            "expiresIn": token_data["expiresIn"]  # Expiration time for the token
        }
    else:
        error_message = response.json().get("error", {}).get("message", "Authentication failed")
        raise HTTPException(status_code=response.status_code, detail=error_message)
