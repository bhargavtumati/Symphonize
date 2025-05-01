from pydantic import BaseModel, field_validator

from app.utils.validators import is_non_empty

class IntegrationModel(BaseModel):
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str

    @field_validator('client_id')
    def validate_client_id(cls, client_id: str):
        is_non_empty(client_id,"client_id")
        return client_id

    @field_validator('client_secret')
    def validate_client_secret(cls, client_secret: str):
        is_non_empty(client_secret,"client_secret")
        return client_secret

    @field_validator('code')
    def validate_code(cls, code: str):
        is_non_empty(code,"code")
        return code

    @field_validator('redirect_uri')
    def validate_redirect_uri(cls, redirect_uri: str):
        is_non_empty(redirect_uri,"redirect_uri")
        return redirect_uri


class APIKeyModel(BaseModel):
    api_key: str

class GoogleMeetModel(BaseModel):
    code: str