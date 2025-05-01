from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.helpers.firebase_helper import verify_firebase_token
from app.models.master_data import MasterData
from app.api.v1.endpoints.models.company_model import CreateMetadata

router = APIRouter()

ALLOWED_TYPES = ["job-title", "job title"]

@router.post("/{type}")
async def insert_metadata_by_type(
    type: str,
    payload: CreateMetadata,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        if type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid path parameter type. Allowed values are: {ALLOWED_TYPES}"
            )
        type = type.replace("-", " ")
        new_data = MasterData(value={"name": payload.name}, type = type)
        existing_record = new_data.get_existing_record(session=session, key="name")

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{type} already exists"
            )
        
        new_data.create(session=session)
        result = MasterData.get_all_by_type(
            session=session, type=type
        )
        data = [row[0] for row in result]

        return {
            "status": status.HTTP_200_OK,
            "message": f"{type} added successfully",
            "data": data
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}"
        )
    

@router.get("/{type}")  
async def get_all_metadata_names_by_type(
    type: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db)
):
    try:
        if type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid path parameter type. Allowed values are: {ALLOWED_TYPES}"
            )
        result = MasterData.get_all_by_type(
            session=session, type=type.replace("-", " ")
        )
        data = [row[0] for row in result]
        return {
            "status": status.HTTP_200_OK,
            "data": data
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during database call {str(e)}"
        )