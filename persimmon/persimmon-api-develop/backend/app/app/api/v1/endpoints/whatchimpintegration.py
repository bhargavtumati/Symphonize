from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests, os

router = APIRouter()

class ConnectAccount(BaseModel):
    apiToken: str = os.getenv("WHATCHIMP_API_TOKEN")   #Issued by Whatchimp to authenticate the application using their API.
    user_id: str =  os.getenv("WHATSAPP_USER_ID")   #whatsapp user id
    whatsapp_business_account_id: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")  #META Business Manager
    access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN")   #whatsapp business api access token
    
class SendMessage(BaseModel):
    apiToken: str = os.getenv("WHATCHIMP_API_TOKEN")
    phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    message: str = "HELLO HELLO"
    phone_number: str = os.getenv("WHATSAPP_PHONE_NUMBER")

class GetConversation(BaseModel):
    apiToken: str = os.getenv("WHATCHIMP_API_TOKEN") 
    phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    phone_number: str = os.getenv("WHATSAPP_PHONE_NUMBER")
    limit: int =  10
    offset: int = 1

@router.post("/whatsapp/account/connect")
async def connect_account(data: ConnectAccount):
    data_dict = {
        "apiToken": data.apiToken,
        "user_id": data.user_id,
        "whatsapp_business_account_id": data.whatsapp_business_account_id,
        "access_token": data.access_token
    }
    response = requests.post(
        "https://app.whatchimp.com/api/v1/whatsapp/account/connect",
        json=data_dict
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.post("/whatsapp/send")
async def send_message(data: SendMessage):
    data_dict = {
        "apiToken": data.apiToken,
        "phone_number_id": data.phone_number_id,
        "message": data.message,
        "phone_number": data.phone_number
    }
    response = requests.post(
        "https://app.whatchimp.com/api/v1/whatsapp/send",
        json=data_dict
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.post("/whatsapp/get/conversation")
async def get_conversation(data: GetConversation):
    data_dict = {
        "apiToken": data.apiToken,
        "phone_number_id": data.phone_number_id,
        "phone_number": data.phone_number,
        "limit": data.limit,
        "offset": data.offset
    }
    response = requests.post(
        "https://app.whatchimp.com/api/v1/whatsapp/get/conversation",
        json=data_dict
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    

#https://app.whatchimp.com/dashboard
#https://app.whatchimp.com/api/developer/console