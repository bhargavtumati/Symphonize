from fastapi import APIRouter, HTTPException, Form, File, Depends, UploadFile, status
from pydantic import ValidationError
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.customization import Customization
from app.helpers import db_helper as dbh
from app.helpers.firebase_helper import verify_firebase_token
from app.api.v1.endpoints.models.customization_model import CustomizationModel
from app.models.company import Company
import base64,traceback
import json

router = APIRouter()

@router.get('/extract-settings/domain/{name}')
def get_customization_settings(
    name: str,
    session: Session = Depends(get_db),
):
    try:
        company: Company = Company.get_by_domain(session=session, domain=name)
        if not company:
            raise HTTPException(status_code=404, detail="Domain is invalid")
        
        customization_settings: Customization = Customization.get_customization_settings(session=session, company_id=company.id)
        if not customization_settings.settings.get('website_url'):
            customization_settings.settings['website_url'] = company.website

        if not customization_settings:
            raise HTTPException(status_code=404, detail="Customization settings not found")

        return {
            "message": "Settings data retrieved successfully",
            "data": customization_settings.settings,
            "status": status.HTTP_200_OK
        }
    except HTTPException as e:
        traceback.print_exc()
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customization/domain/{name}")
async def create_or_update_customization(
    name: str,
    career_page_url: Optional[str] = Form(None),
    enable_cover_photo: Optional[bool] = Form(True),
    heading: Optional[str] = Form("Join Us"),
    description: Optional[str] = Form(
        "Explore opportunities that empower you to grow, innovate, and make an impact. Join a team where your talents are valued, your ideas are heard, and your career aspirations become a reality. Let’s build the future together!"
    ),
    enable_dark_mode: Optional[bool] = Form(False),
    color_selected: Optional[str] = Form(None),
    primary_colors: Optional[str] = Form(None),
    selected_header_color: Optional[str] = Form(None),
    header_colors: Optional[str] = Form(None),
    font_style: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    icon: Optional[UploadFile] = File(None),
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    """
    Update or create customization settings for a career page based on the company domain.
    """
    email = token.get("email")
    index = email.find(name)
    if index == -1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied")
    company: Company = Company.get_by_domain(session=session, domain=name)

    def validate_colors(colors,field_name):
        if not isinstance(colors, list):
            raise ValueError(f'{field_name} must be a list')

    primary_colors_list = []
    header_colors_list = []   
    try:
        if primary_colors:
            primary_colors_list = json.loads(primary_colors)
            validate_colors(primary_colors_list,"Primary colors of CTA'S")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid primary color list")

    try:
        if header_colors:
            header_colors_list = json.loads(header_colors)
            validate_colors(header_colors_list,"Header colors")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid header color list")
    
    image_base64 = None
    if image:
        image_data = await image.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
    logo_base64 = None
    if icon:
        logo_data = await icon.read()
        logo_base64 = base64.b64encode(logo_data).decode("utf-8")

    form_data = {
        "career_page_url": career_page_url,
        "enable_cover_photo": enable_cover_photo,
        "heading": heading,
        "description": description,
        "enable_dark_mode": enable_dark_mode,
        "color_selected": color_selected,
        "selected_header_color": selected_header_color,
        "primary_colors": primary_colors_list,
        "header_colors": header_colors_list,
        "font_style": font_style
    }

    if image_base64:
        form_data['image_data'] = image_base64

    if logo_base64:
        form_data['logo_data'] = logo_base64

    try:
        customization_data = CustomizationModel(**form_data)  
    except ValidationError as e:
        error_messages = [
            {
                "loc"   : ["body", error["loc"][0]], 
                "msg"   : error["msg"][13:], 
                "input" : error["input"]
            } for error in e.errors()
        ]
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail = error_messages
        )

    customization = Customization.get_customization_settings(session=session, company_id=company.id)

    try:
        settings = {
            "career_page_url": customization_data.career_page_url,
            "enable_cover_photo": customization_data.enable_cover_photo,
            "heading": customization_data.heading,
            "description": customization_data.description,
            "enable_dark_mode": customization_data.enable_dark_mode,
            "color_selected": customization_data.color_selected,
            "font_style": customization_data.font_style,
            "primary_colors": customization_data.primary_colors,
            "selected_header_color": customization_data.selected_header_color,
            "header_colors": customization_data.header_colors
            }
        
        if customization:
            updated_settings = settings
            if customization_data.image_data:
                updated_settings['image_data'] = customization_data.image_data
            else:
                updated_settings['image_data'] = customization.settings['image_data']

            if customization_data.logo_data:
                updated_settings['logo_data'] = customization_data.logo_data
            else:
                updated_settings['logo_data'] = customization.settings['logo_data']
            customization.settings.update(updated_settings)
            customization.meta.update(dbh.update_meta(meta=customization.meta, email=email))
            customization_data = customization.update(session=session)

        else:
            if image_base64:
                settings['image_data'] = image_base64
            if logo_base64:
                settings['logo_data'] = logo_base64
            customization = Customization(
                company_id=company.id,
                settings=settings
            )
            customization_data = customization.create(session=session, created_by=email)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException as e:
        traceback.print_exc()
        raise e

    return {
        "message": "Customization settings created/modified successfully",
        "data": customization_data,
        "status": status.HTTP_200_OK
    }

@router.get('/customization/domain/{name}')
def get_customization_settings(
    name: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    try:
        email: str = token.get("email")
        if email.find(name) == -1:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied")
        company: Company = Company.get_by_domain(session=session, domain=name)
        if not company:
            raise HTTPException(status_code=404, detail="Domain is invalid")
        
        customization_settings: Customization = Customization.get_customization_settings(session=session, company_id=company.id)

        if not customization_settings.settings.get('website_url'):
            customization_settings.settings['website_url'] = company.website
        if not customization_settings:
            raise HTTPException(status_code=404, detail="Customization settings not found")

        return {
            "message": "Settings data retrieved successfully",
            "data": customization_settings.settings
        }
    except HTTPException as e:
        traceback.print_exc()
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))