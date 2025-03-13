from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests, os

router = APIRouter()

class ConnectAccount(BaseModel):
    apiToken: str   #Issued by Whatchimp to authenticate the application using their API.
    user_id: str   #User ID of WhatsApp account owner
    whatsapp_business_account_id: str  #META Business Manager
    access_token: str  #Issued to the user  (or obtained on behalf of the user) by whatsapp to prove their identity and permissions. 

class SendMessage(BaseModel):
    apiToken: str
    phone_number_id: str
    message: str
    phone_number: str

class GetConversation(BaseModel):
    apiToken: str
    phone_number_id: str
    phone_number: str
    limit: int
    offset: int = 0

@router.post("/whatsapp/account/connect")
async def connect_account(data: ConnectAccount):
    data_dict = {
        "apiToken": os.getenv("WATCHI_API_TOKEN"),
        "user_id": os.getenv("WATCHI_USER_ID"),
        "whatsapp_business_account_id": os.getenv("WATCHI_BUSI_ACC"),
        "access_token": os.getenv("WATCHI_ACCESS_TOKEN")
    }
    response = requests.post(
        "https://app.whatchimp.com/api/v1/whatsapp/account/connect",
        data=data_dict
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.post("/whatsapp/send")
async def send_message(data: SendMessage, message):
    data_dict = {
        "apiToken": os.getenv("WATCHI_API_TOKEN"),
        "phone_number_id": os.getenv("WATCHI_PHONE_NUMBERID"),
        "message": "hello",
        "phone_number": os.getenv("WATCHI_PHONENUMBER")
    }
    response = requests.post(
        "https://app.whatchimp.com/api/v1/whatsapp/send",
        data=data_dict
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.post("/whatsapp/get/conversation")
async def get_conversation(data: GetConversation):
    data_dict = {
        "apiToken": os.getenv("WATCHI_API_TOKEN"),
        "phone_number_id": os.getenv("WATCHI_PHONE_NUMBERID"),
        "phone_number": os.getenv("WATCHI_PHONENUMBER"),
        "limit": data.limit,     # get only these number of messages
        "offset": data.offset    #skip first few number of messages
    }
    response = requests.post(
        "https://app.whatchimp.com/api/v1/whatsapp/get/conversation",
        data=data_dict
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
