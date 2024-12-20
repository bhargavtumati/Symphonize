import base64
import binascii
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.Customization import Customization
from app.utils.saveimage import save_image
from app.helpers import db_helper as dbh

router = APIRouter()

@router.post("/customizations/{domain}")
def create_or_update_customizations(
    domain: str,
    enable_cover_photo: bool = Form(...),
    heading: Optional[str] = Form("Welcome to Career Page"),  # Default heading
    description: Optional[str] = Form("Here you can explore opportunities."),  # Default description
    dark_mode: bool = Form(False),
    color_selected: Optional[str] = Form("blue"),  # Allow empty value for colors
    font: Optional[str] = Form("Times New Roman"),  # Default font
    file: Optional[UploadFile] = None,
    db: Session = Depends(get_db),
):
    """
    Update customization settings for a user's career page based on the domain.
    """
    if enable_cover_photo and (not heading or not description or not file):
        raise HTTPException(
            status_code=422,
            detail="Cover photo, Heading, and description are required when cover photo is enabled.",
        )

    # Handle image upload
    image_data = None
    if file:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=422,
                detail="Invalid file type. Only JPEG and PNG images are supported.",
            )
        
        try:
            image_data = save_image(file, domain)
            if not image_data:
                raise ValueError("Image saving failed.")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error saving image: {str(e)}",
            )

    # Fetch or initialize customization record
    customization = db.query(Customization).filter(Customization.settings["domain"].astext == domain).first()

    # Default colors if no custom colors are provided
    

    try:
        if customization:
            # Update existing settings
           
            existing_colors = customization.settings.get("recently_used_colors", [])

            # Add the selected color and deduplicate while preserving order
            recently_used_colors = [color.lower() for color in [color_selected] + existing_colors if color.strip()]
            recently_used_colors = list(dict.fromkeys(recently_used_colors))[:10]
            
            # Ensure image_data is encoded if it exists
            if image_data:
                image_data = base64.b64encode(image_data).decode("latin1")
            
            # Update customization settings
            customization.settings.update({
                "domain": domain,
                "enable_cover_photo": enable_cover_photo,
                "heading": heading,
                "description": description,
                "dark_mode": dark_mode,
                "color_selected": color_selected,
                "font": font,
                "image_data": image_data,
                "recently_used_colors": recently_used_colors,
            })
        else:
            # Create a new customization record
            default_colors = [color_selected,"red", "yellow", "blue", "green", "purple"]
            recently_used_colors = [color.lower() for color in [color_selected] + default_colors if color.strip()]
            recently_used_colors = list(dict.fromkeys(recently_used_colors))[:10]
            
            customization = Customization(
                settings={
                    "domain": domain,
                    "enable_cover_photo": enable_cover_photo,
                    "heading": heading,
                    "description": description,
                    "dark_mode": dark_mode,
                    "color_selected": color_selected,
                    "font": font,
                    "image_data": image_data and base64.b64encode(image_data).decode("latin1"),
                    "recently_used_colors": recently_used_colors,  # Default colors if empty
                },
                meta=dbh.get_metadata(),
            )
            db.add(customization)
        
        db.commit()
        db.refresh(customization)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update customization: {str(e)}",
        )

    return customization.settings



@router.get("/customizations/{domain}")
def get_customization_by_domain(
    domain: str,
    db: Session = Depends(get_db),
):
    """
    Get customization settings for a user's career page based on the domain.
    """
    customization = db.query(Customization).filter(Customization.settings["domain"].astext == domain).first()
    
    if not customization:
        raise HTTPException(
            status_code=404,
            detail="Customization not found.",
        )
    
    # Decode image data if present
    settings = customization.settings
    if "image_data" in settings and settings["image_data"]:
        try:
            settings["image_data"] = base64.b64decode(settings["image_data"]).decode("latin1")
        except binascii.Error:
            raise HTTPException(
                status_code=500,
                detail="Error decoding image data.",
            )
    
    return settings

@router.delete("/customizations/{domain}")
def delete_customizations(
    domain: str,
    db: Session = Depends(get_db),
):
    """
    Delete customization settings for a user's career page based on the domain.
    """
    customization = db.query(Customization).filter(Customization.settings["domain"].astext == domain).first()

    if not customization:
        raise HTTPException(
            status_code=404,
            detail="Customization not found.",
        )

    try:
        db.delete(customization)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete customization: {str(e)}",
        )

    return {"success": True}
