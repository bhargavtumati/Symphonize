from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
import requests, os

router = APIRouter()

WATI_API_ENDPOINT = os.getenv("WATI_API_ENDPOINT")
WATI_API_TOKEN = os.getenv("WATI_API_TOKEN")

class Message(BaseModel):
    message: str

@router.post("/sendSessionMessage/{whatsapp_number}")
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


@router.get("/getMessagesByWhatsappNumber/{whatsapp_number}")
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



