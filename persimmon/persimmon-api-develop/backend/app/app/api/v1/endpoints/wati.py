from fastapi import APIRouter, HTTPException, Depends, Body, Query, status
from sqlalchemy.orm import session
import requests, re, os, json, uuid
from app.db.session import get_db 
from typing import Dict, List
from app.helpers.firebase_helper import verify_firebase_token
from sqlalchemy.orm import Session
from app.helpers import db_helper as dbh, regex_helper as regexh, wati_helper as watih
from app.models.company import Company
from app.models.integration import Integration, WhatsappIntegrationType
from app.api.v1.endpoints.models.whatsapp_model import WatiRequest, GetTemplateBody
from app.api.v1.endpoints.models.whatsapp_model import ParamRequest
from app.api.v1.endpoints.integration import whatsapp_integration
from app.helpers.firebase_helper import verify_firebase_token

router = APIRouter()

@router.get("/templates")
def get_templates(
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
         result=whatsapp_integration("wati",token,session)
         
         wati_api_token=result.get("wati_api_token")
         wati_api_endpoint=result.get("wati_api_endpoint")
         url = f"{wati_api_endpoint}/api/v1/getMessageTemplates?pageSize=10&pageNumber=1"
   
         headers = {
         "content-type": "application/json",
         "Authorization": f"{wati_api_token}"
         }
    
         response = requests.get(url, headers=headers)
    
         if response.status_code == 200:
             return {"status": status.HTTP_200_OK, "templates": response.json(), "message": "Templates fetched successfully"}
         else:
             raise HTTPException(status_code=response.status_code, detail=response.text)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@router.get("/available-params", summary="Get all available parameters")
def get_available_params(token: dict = Depends(verify_firebase_token)):
    """
    Returns a list of all available parameters that can be used for mapping.
    """
    AVAILABLE_PARAMS = [
    "full_name",
    "date_of_birth",
    "phone",
    "email",
    "address",
    "gender"
    ]

    return {
        "available_params": AVAILABLE_PARAMS,
        "status": status.HTTP_200_OK,
        "message": "Available parameters fetched successfully"
        }

@router.post("/template-body-params")
def get_template_body_params(request: GetTemplateBody, token: dict = Depends(verify_firebase_token)):
    """Extract required parameters from a given template."""
    try:
        params = re.findall(r"\{\{(.*?)\}\}", request.template_body) 
        return params if len(params) > 0 else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-whatsapp")
def send_bulk_whatsapp_messages(
    request: WatiRequest,
    params: List[ParamRequest] = Body([]),
    session: Session = Depends(get_db), 
    token: dict = Depends(verify_firebase_token)
):
    """Fetch template, fill params with applicant data & send messages to multiple applicants."""
    try:
        params_dict = [{"name":param.name,"value":param.value} for param in params]

        result=whatsapp_integration("wati",token,session)

        wati_api_token=result.get("wati_api_token")
        wati_api_endpoint=result.get("wati_api_endpoint")

        response = watih.send_whatsapp_message_via_wati(applicant_uuids=request.applicant_uuids, wati_api_token=wati_api_token, wati_api_endpoint=wati_api_endpoint, session=session, template_name=request.template_name, body_params=request.body_params, params=params_dict) 

        return {
            "response": response
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

