from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, Query, Request
from pydantic import BaseModel
import requests, os, json, httpx

router = APIRouter()

WATI_API_ENDPOINT = os.getenv("WATI_API_ENDPOINT")
WATI_API_TOKEN = os.getenv("WATI_API_TOKEN")
WATI_WEBHOOK_SECRET = os.getenv("WATI_WEBHOOK_SECRET")  #notification
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")


class Message(BaseModel):
    message: str

class Button(BaseModel):
    type: str  # Example: "QUICK_REPLY" or "URL"
    text: str  # Button text
    url: Optional[str] = None  # Required only for URL buttons

class Component(BaseModel):
    type: str  # HEADER, BODY, FOOTER, BUTTONS
    format: Optional[str] = None  # Needed for headers (TEXT, IMAGE, VIDEO, DOCUMENT)
    text: Optional[str] = None  # For HEADER, BODY, and FOOTER
    buttons: Optional[List[Button]] = None  # For BUTTONS type

class TemplateRequest(BaseModel):
    name: str
    category: str
    language: str
    components: List[Component]  # Multiple components like header, body, footer, buttons

PABBLY_WEBHOOK_URL = "https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjUwNTZiMDYzZTA0M2M1MjZlNTUzNDUxMzMi_pc"

@router.get("/Templates")
async def get_templates():
    url = f"{WATI_API_ENDPOINT}/api/v1/getMessageTemplates?pageSize=10&pageNumber=1"
   
    headers = {
        "content-type": "application/json",
        "Authorization": f"{WATI_API_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return {"status": "success", "templates": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@router.post("/send_template1_message_list/")
async def send_template1_message(whatsapp_numbers: list[str]):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{WATI_API_TOKEN}"
    }

    payload = {
        "template_name": "welcome_wati_v2",
        "broadcast_name": "send message",
        "parameters": [{"name": "name", "value": "User"}]  # Adding custom parameters
    }

    responses = []
    
    async with httpx.AsyncClient() as client:
        for number in whatsapp_numbers:
            url = f"{WATI_API_ENDPOINT}/api/v1/sendTemplateMessage?whatsappNumber={number}"
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    responses.append({"number": number, "status": "success", "response": response.json()})
                else:
                    responses.append({"number": number, "status": "failed", "error": response.text})
            except Exception as e:
                responses.append({"number": number, "status": "failed", "error": str(e)})

    return {"results": responses}

@router.post("/send_template2_message_list/")
async def send_template2_message(whatsapp_numbers: list[str]):  # Accepting a list of numbers

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"{WATI_API_TOKEN}"
    }

    payload = json.dumps({
            "template_name":  "rcrtr_bj_1",
            "broadcast_name": "hireAspirants"
        })
    
    responses = []

    for number in whatsapp_numbers:
        
        url =f"{WATI_API_ENDPOINT}/api/v1/sendTemplateMessage?whatsappNumber={number}"
    
        response = requests.post(url, data=payload, headers=headers)
        
        if response.status_code == 200:
            responses.append({"number": number, "status": "success", "response": response.json()})
        else:
            responses.append({"number": number, "status": "failed", "error": response.text})

    return {"results": responses}


@router.post("/send_template3_message_list/")  #
async def send_template2_message(whatsapp_numbers: list[str]):
    
    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"{WATI_API_TOKEN}"
    }

    payload = json.dumps({
                          "template_name": "ts_message5ab",
                          "broadcast_name": "joinbitlabs",
                          "parameters": [],
                          "media": {
                          "type": "video",
                          "mediaId": "356821423953271"
                           },
                         "buttons": [
                          {
                            "type": "url",
                            "text": "Join Now",
                            "url": "https://jobs.bitlabs.in/candidate?&&utm_source=wati-ts-5ab&utm_medium=social-msg-5ab&utm_campaign=promo-5ab&utm_content=jnw&utm_term=rabb-turt"
                          }
                                     ]
                          })
    responses = []    
    for whatsapp_number in whatsapp_numbers:
             url = f"{WATI_API_ENDPOINT}/api/v1/sendTemplateMessage?whatsappNumber={whatsapp_number}"

             # Sending request to Wati API
             response = requests.post(url, data=payload, headers=headers)

             if response.status_code == 200:
                responses.append({"number": whatsapp_number, "status": "success", "response": response.json()})
             else:
                responses.append({"number": whatsapp_number, "status": "failed", "error": response.text})

    return {"results": responses}

@router.post("/sendSessionMessage/{whatsapp_number}")  #if applicant replied during last 24 hrs
def send_message(whatsapp_number: str, messageText: str):
    url = f"{WATI_API_ENDPOINT}/api/v1/sendSessionMessage/{whatsapp_number}"
    headers = {
        "content-type": "application/json-patch+json",
        "Authorization": f"{WATI_API_TOKEN}"
    }
    params = {
        "messageText": messageText
    }
    response = requests.post(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return {"status": "success", "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    
@router.get("/getMessagesByWhatsappNumber/{whatsapp_number}") #if added to contacts and interacted 24 hrs ago
async def get_messages_by_whatsapp_number(
    whatsapp_number: str,
    page_size: int = Query(default=10),
    page_number: int = Query(default=1)
):
    url = f"{WATI_API_ENDPOINT}/api/v1/getMessages/{whatsapp_number}"
    headers = {
        "content-type": "application/json-patch+json",
        "Authorization": f"{WATI_API_TOKEN}"
    }
    params = {
        "pageSize": page_size,
        "pageNumber": page_number
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return {"status": "success", "response": response.json()}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
@router.post("/receive-message")
async def receive_message(request: Request):
    data = await request.json()  # Receive data from Pabbly
    print("Received Data:", data)  # Log the data
    
    # Optional: Forward the data back to Pabbly if needed
    async with httpx.AsyncClient() as client:
        response = await client.post(PABBLY_WEBHOOK_URL, json=data)
    
    return {"message": "Webhook received", "status": "success"}



#https://app.wati.io/api-docs
#https://docs.wati.io/reference/get_api-v1-getcontacts
#https://app.wati.io/teamInbox/67c69e8c2a31ecb6f243cade?filter={%22filterType%22:2}&search={%22searchOptionType%22:1}
""" <script>

                var url = 'https://wati-integration-prod-service.clare.ai/v2/watiWidget.js?11717';
                var s = document.createElement('script');
                s.type = 'text/javascript';
                s.async = true;
                s.src = url;
                var options = {
                "enabled":true,
                "chatButtonSetting":{
                    "backgroundColor":"#00e785",
                    "ctaText":"Chat with us",
                    "borderRadius":"25",
                    "marginLeft": "0",
                    "marginRight": "20",
                    "marginBottom": "20",
                    "ctaIconWATI":false,
                    "position":"right"
                },
                "brandSetting":{
                    "brandName":"Wati",
                    "brandSubTitle":"undefined",
                    "brandImg":"https://www.wati.io/wp-content/uploads/2023/04/Wati-logo.svg",
                    "welcomeText":"Hi there!\nHow can I help you?",
                    "messageText":"Hello, %0A I have a question about {{page_link}}",
                    "backgroundColor":"#00e785",
                    "ctaText":"Chat with us",
                    "borderRadius":"25",
                    "autoShow":false,
                    "phoneNumber":"919566151115"
                }
                };
                s.onload = function() {
                    CreateWhatsappChatWidget(options);
                };
                var x = document.getElementsByTagName('script')[0];
                x.parentNode.insertBefore(s, x);

</script> """



