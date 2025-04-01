from typing import List
from pydantic import BaseModel
import uuid

class WatiRequest(BaseModel):
    applicant_uuids: List[uuid.UUID] 
    template_name: str
    body_params: List[str]
    
class ParamRequest(BaseModel):
    name: str
    value: str
    
class GetTemplateBody(BaseModel):
    template_body: str

class WatiKeyModel(BaseModel):
    wati_api_endpoint: str
    wati_api_token: str

