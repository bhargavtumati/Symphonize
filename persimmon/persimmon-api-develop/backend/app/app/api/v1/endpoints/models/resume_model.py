from pydantic import BaseModel, field_validator
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

class FilePath(BaseModel):
    file_path: str

    @field_validator("file_path")
    def validate_file_path(cls, file_path):
        if not file_path:
            raise ValueError("File path is required")
        return file_path