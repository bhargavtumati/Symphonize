from pydantic import BaseModel

class IntegrationModel(BaseModel):
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str

class APIKeyModel(BaseModel):
    api_key: str