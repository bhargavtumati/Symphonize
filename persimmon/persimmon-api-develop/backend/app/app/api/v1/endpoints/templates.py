from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.models.resume_model import EmailTemplate
from app.helpers.firebase_helper import verify_firebase_token
from app.db.session import get_db
from app.models.company import Company
from app.models.template import Template
from app.helpers import email_helper as emailh

router = APIRouter()

@router.patch("/update")
def add_template(
    domain: str,
    payload: EmailTemplate,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    """
    API endpoint to store a template in the database.
    
    Args:
        payload (TemplatePayload): The JSON payload containing the template, to, and from fields.
        db (Session): Database session.
 
    Returns:
        dict: A success message with the created template ID.
    """
    try:
        company = Company.get_by_domain(session=session, domain=domain)
        if not company:
            raise HTTPException(status_code=404, detail="domain not found")
        
        template: Template = Template.get_by_company_id(session=session, id=company.id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        if payload.is_edited:  
            template.template_data.update(emailh.update_email_templates(templates=template.template_data, payload=payload))
            template.update(session=session)
        else:
            template.template_data.update(emailh.add_email_template(templates=template.template_data, payload=payload))
            template.update(session=session)
        return {
            "message": "Template updated successfully" if payload.is_edited else "Template added successfully",
            "status": status.HTTP_200_OK,
            "data": {
                "template_data": template.template_data
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add template: {str(e)}")
    

@router.get("/")
async def get_template(
    domain: str,
    session: Session = Depends(get_db),
    token: dict = Depends(verify_firebase_token)
):
    try:
        company = Company.get_by_domain(session=session, domain=domain)
        if not company:
            raise HTTPException(status_code=404, detail="domain not found")
        
        template_exists: Template = Template.get_by_company_id(session=session, id=company.id)

        if not template_exists:
            raise HTTPException(status_code=404, detail="Template not found")

        return {
            "message": "Template details retrieved successfully",
            "status": status.HTTP_200_OK,
            "data": {
                "id": template_exists.id,
                "company_id": template_exists.company_id,
                "template_data": template_exists.template_data
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
