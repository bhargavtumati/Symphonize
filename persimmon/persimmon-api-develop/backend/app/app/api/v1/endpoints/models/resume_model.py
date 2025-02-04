from pydantic import BaseModel
from typing import List


class ResumeParseRequest(BaseModel):
    payload: str  
    original_resume: str

# Request model
class FilePathPayload(BaseModel):
    file_paths: List[str]