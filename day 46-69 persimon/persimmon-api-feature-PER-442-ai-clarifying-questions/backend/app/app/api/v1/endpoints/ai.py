from app.helpers import ai_helper as aih 
from pydantic import BaseModel
from app.helpers.firebase_helper import verify_firebase_token
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

class JDRequest(BaseModel):
    input: str
    prompt: str

@router.post('/generate-job-description')
async def generate_job_description(
    jd: JDRequest,
    token: dict = Depends(verify_firebase_token)
):
    try:
        if jd.input is None or jd.prompt is None:
            raise HTTPException(status_code=400, detail="Input or prompt cannot be None")

        full_input = (
            (jd.input ) + '\n' +
            jd.prompt + '\n' +
            'Give me only text of length less than 2000 characters'
        )
        
        ai_response = aih.get_gemini_ai_response(full_input)
        print("ai response is"+ai_response)
        

        return {
            'job_description': ai_response
        }

    except Exception as e:
        
        raise HTTPException(status_code=500, detail=str(e))
