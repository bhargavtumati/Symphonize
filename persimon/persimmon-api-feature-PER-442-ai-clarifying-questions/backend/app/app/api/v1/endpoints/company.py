from fastapi import APIRouter
from pydantic import BaseModel
from fastapi import Depends, HTTPException
from app.helpers.firebase_helper import verify_firebase_token
from app.models.company import Company as CompanyModel
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()

api_reference: dict[str, str] = {"api_reference": "https://github.com/symphonize/persimmon-api"}

@router.get("")
def get_company_by_domain(
    domain: str,  # The domain will be passed as a query parameter
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        # Step 1: Retrieve company details by domain
        company_record = CompanyModel.get_by_domain(session=session, domain=domain)
        
        if not company_record:
            raise HTTPException(status_code=404, detail="Company not found")

        # Step 2: Return company details
        return {
            "id": company_record.id,
            "name": company_record.name,
            "website": company_record.website,
            "number_of_employees": company_record.number_of_employees,
            "industry_type": company_record.industry_type,
            "linkedin": company_record.linkedin,
            "domain": company_record.domain,
            "type": company_record.type.name
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
