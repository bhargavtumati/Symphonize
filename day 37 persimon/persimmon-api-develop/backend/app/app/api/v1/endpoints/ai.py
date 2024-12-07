from app.helpers import ai_helper as aih
from pydantic import BaseModel

# from app.helpers.firebase_helper import verify_firebase_token
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


class JDRequest(BaseModel):
    input: Optional[str] = None
    prompt: str


@router.post("/generate-job-description")
async def generate_job_description(
    jd: JDRequest,
    # token: dict = Depends(verify_firebase_token)
):
    try:
        full_input = (
            (jd.input or "")
            + "\n"
            + jd.prompt
            + "\n"
            + "Give me only text of length less than 2000 characters"
        )

        ai_response = aih.get_gemini_ai_response(input=full_input)

        return {"job_description": ai_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
