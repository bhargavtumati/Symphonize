from pydantic import BaseModel
from typing import List, Optional

class ResumeParseRequest(BaseModel):
    payload: str  
    original_resume: str

# Request model
class FilePathPayload(BaseModel):
    file_paths: List[str]

class EmailTemplate(BaseModel):
    uuid: Optional[str] = None
    name: str
    subject : str
    body: str
    is_edited: bool = False