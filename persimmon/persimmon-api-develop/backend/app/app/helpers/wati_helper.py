from app.helpers import applicant_helper as applicanth
from sqlalchemy.orm import Session
import requests, re, json
import uuid
from fastapi import HTTPException

def send_whatsapp_message_via_wati(applicant_uuids: list[uuid.UUID], wati_api_token, wati_api_endpoint, session: Session, body_params: list[str], params: list[dict], template_name: str):
    try:
        print("params",params)
        custom_param_names = {param["name"] for param in params}
        required_param_names = set(body_params)
        missing_params = required_param_names - custom_param_names
        
        if missing_params:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required parameters: {', '.join(missing_params)}"
            )

        headers = {
            "content-type": "application/json-patch+json",
            "Authorization": f"{wati_api_token}"
        }
        applicants_data = applicanth.get_applicants_data(applicant_uuids=applicant_uuids, session=session)
        if not applicants_data:
            raise HTTPException(status_code=404, detail="No applicants found")

        responses = []
        for applicant_uuid in applicant_uuids:
            applicant_data = applicants_data.get(str(applicant_uuid))

            if not applicant_data:
                responses.append({"applicant_id": applicant_uuid, "status": "failed", "reason": "Applicant not found"})
                continue

            params_dict = {param["name"]: param["value"] for param in params}  
        
            semi_custom_params = {}
            for param_name, field_name in params_dict.items():
                value = applicant_data.get("personal_information", {}).get(field_name, "N/A")
                semi_custom_params[param_name] = value
                
            final_custom_params = [{"name": k, "value": v} for k, v in semi_custom_params.items()]
            phone = applicant_data.get("personal_information", {}).get("phone", "Phone number not found")
            if phone == "Phone number not found":
                responses.append({"applicant_id": applicant_uuid, "status": "failed", "reason": "Phone number not found"})
                continue

            # Remove all non-numeric characters
            clean_phone = re.sub(r"\D", "", phone)
            if len(clean_phone) <= 10:
                responses.append({"applicant_id": applicant_uuid, "status": "failed", "reason": "Country code not found"})
                continue

            payload_dict = {
                "parameters": final_custom_params,
                "template_name": template_name,
                "broadcast_name": "whatsapp_broadcast"
                }

            payload = json.dumps(payload_dict, ensure_ascii=False)
            url = f"{wati_api_endpoint}/api/v1/sendTemplateMessage?whatsappNumber={clean_phone}"
            response =requests.post(url , data=payload, headers=headers)

            if response.status_code == 200:
                responses.append({"applicant_id": applicant_uuid, "status": "success", "response": response.json()})
            else:
                responses.append({"applicant_id":applicant_uuid, "status": "failed", "reason":response.text}) 

        return {"status": "completed", "results": responses}
    except HTTPException as e:
        raise e