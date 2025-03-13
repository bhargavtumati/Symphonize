from fastapi import APIRouter, status
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from app.helpers.firebase_helper import verify_firebase_token
from app.models.company import Company as CompanyModel
from sqlalchemy.orm import Session
from app.db.session import get_db
import base64
from fastapi.responses import JSONResponse

router = APIRouter()

api_reference: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

def encode_image(image_data):
    return base64.b64encode(image_data).decode("utf-8") if image_data else None


@router.get("")
def get_company_by_domain(
    domain: str,  
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        company_record = CompanyModel.get_by_domain(session=session, domain=domain)
        
        if not company_record:
            raise HTTPException(status_code=404, detail="Company not found")

        # Convert binary images to Base64
        logo_base64 = encode_image(company_record.logo)
        company_images_base64 = [
            encode_image(img) for img in company_record.company_images or []
        ]
        company_type = company_record.company_type.name if company_record.company_type else None
        business_type = company_record.business_type.name if company_record.business_type else None

        return JSONResponse(content={
            "id": company_record.id,
            "name": company_record.name,
            "website": company_record.website,
            "number_of_employees": company_record.number_of_employees,
            "industry_type": company_record.industry_type,
            "about": company_record.about,
            "tagline": company_record.tagline,
            "domain": company_record.domain,
            "company_type": company_type,
            "business_type": business_type,
            "instagram_url": company_record.instagram_url,
            "facebook_url": company_record.facebook_url,
            "x_url": company_record.x_url,
            "linkedin_url": company_record.linkedin_url,
            "logo_base64": logo_base64,
            "company_images_base64": company_images_base64,
            "status": status.HTTP_200_OK,
            "message": "Company details retrieved successfully"
        })
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
