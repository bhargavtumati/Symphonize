from fastapi import APIRouter, HTTPException, Depends, Request
import requests, os
from typing import List
from pydantic import BaseModel

router = APIRouter()

# Replace with your Meta credentials
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0"
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER")
BUSINESS_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Request models
class TemplateMessage(BaseModel):
    template_name: str
    language_code: str = "en_US"
    recipients: List[str]

class CustomMessage(BaseModel):
    to: str
    message: str

class CreateTemplate(BaseModel):
    name: str
    category: str
    language: str
    components: list  # Should follow WhatsApp's template structure


# 1️⃣ **Get all WhatsApp message templates**
@router.get("/whatsapp/templates")
def get_templates():
    url = f"{WHATSAPP_API_URL}/{BUSINESS_ID}/message_templates"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


# 2️⃣ **Create a new message template**
@router.post("/whatsapp/templates")
def create_template(data: CreateTemplate):
    url = f"{WHATSAPP_API_URL}/{BUSINESS_ID}/message_templates"
    response = requests.post(url, json=data.model_dump(), headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


# 3️⃣ **Send a message template to multiple WhatsApp numbers**
@router.post("/whatsapp/send-template")
def send_template(data: TemplateMessage):
    url = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    for number in data.recipients:
        payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "template",
            "template": {
                "name": data.template_name,
                "language": {"code": data.language_code}
            }
        }
        response = requests.post(url, json=payload, headers=HEADERS)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
    return {"message": "Template sent successfully"}


# 4️⃣ **Send a custom text message**
@router.post("/whatsapp/send-message")
def send_message(data: CustomMessage):
    url = f"{WHATSAPP_API_URL}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": data.to,
        "type": "text",
        "text": {"body": data.message}
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.json())


# 5️⃣ **Webhook to receive incoming messages from WhatsApp**
@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    print("Received Webhook Data:", payload)  # Store or process as needed
    return {"status": "received"}
