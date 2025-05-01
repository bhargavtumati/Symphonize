from typing import List
from pydantic import BaseModel, field_validator
from app.utils.validators import is_non_empty
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

    @field_validator('wati_api_endpoint')
    def validate_wati_api_endpoint(cls, wati_api_endpoint: str):
        is_non_empty(wati_api_endpoint,"wati_api_endpoint")
        return wati_api_endpoint

    @field_validator('wati_api_token')
    def validate_wati_api_token(cls, wati_api_token: str):
        is_non_empty(wati_api_token,"wati_api_token")
        return wati_api_token