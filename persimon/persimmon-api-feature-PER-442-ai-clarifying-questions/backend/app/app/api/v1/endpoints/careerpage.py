from fastapi import APIRouter, HTTPException, Form, File, Depends, UploadFile
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.Customization import Customization
from app.helpers import db_helper as dbh
from app.helpers.firebase_helper import verify_firebase_token
from app.api.v1.endpoints.models.customizerequest import CustomizationCreate, CustomizationUpdate, CustomizationResponse
from app.utils.saveimage import save_image
import base64

router = APIRouter()

def encode_image_to_base64(file: UploadFile) -> str:
    """Encode an uploaded image file to a Base64 string."""
    try:
        file_content = file.file.read()  # Read file content
        file_size = len(file_content)

        # Validate file size (e.g., between 2MB and 5MB)
        if file_size < 2 * 1024 * 1024 or file_size > 5 * 1024 * 1024:
            raise ValueError("Image size must be between 2MB and 5MB.")

        # Convert to Base64 string
        return base64.b64encode(file_content).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error encoding image: {str(e)}")

@router.post("/customizations/{domain}")
async def create_or_update_customizations(
    domain: str,
    enable_cover_photo: bool = Form(False),  # Default to False
    heading: str = Form("Welcome to our Career Page"),  # Default heading
    description: str = Form("Explore amazing opportunities with us!"),  # Default description
    dark_mode: bool = Form(False),  # Default to False
    color_selected: str = Form("Blue"),  # Default color
    font: str = Form("Times New Roman"),  # Default font
    file: UploadFile = File(None),  # File is optional and defaults to None
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    """
    Update or create customization settings for a user's career page based on the domain.
    """
    email = token.get("email")  # Extract the user's email from the token
    
    # Encode image data if a file is uploaded
    image_data = None
    if file:
        image_data = encode_image_to_base64(file)

    # Prepare the data to validate with Pydantic
    form_data = {
        "domain": domain,
        "enable_cover_photo": enable_cover_photo,
        "heading": heading,
        "description": description,
        "dark_mode": dark_mode,
        "color_selected": color_selected,
        "font": font,
        "image_data": image_data,  # Include encoded image data as string
    }

    # Validate the data using the Pydantic model
    try:
        customization_data = CustomizationCreate(**form_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Fetch or initialize customization record
    customization = Customization.get_by_domain(session=session, domain=domain, email=email)

    try:
        # Update existing customization
        if customization:
            existing_colors = customization.settings.get("recently_used_colors", [])
            recently_used_colors = [color for color in [color_selected] + existing_colors if color.strip()]
            recently_used_colors = list(dict.fromkeys(recently_used_colors))[:10]

            # Prepare updated data
            updated_settings = {
                **customization.settings,
                "enable_cover_photo": customization_data.enable_cover_photo,
                "heading": customization_data.heading,
                "description": customization_data.description,
                "dark_mode": customization_data.dark_mode,
                "color_selected": customization_data.color_selected,
                "font": customization_data.font,
                "image_data": customization_data.image_data,
                "recently_used_colors": recently_used_colors,
            }
            customization.settings.update(updated_settings)
            customization.update(session=session)

        # Create a new customization
        else:
            default_colors = [color_selected, "Red", "Yellow", "Blue", "Green", "Purple"]
            recently_used_colors = [color for color in [color_selected] + default_colors if color.strip()]
            recently_used_colors = list(dict.fromkeys(recently_used_colors))[:10]

            customization = Customization(
                settings={
                    "domain": domain,
                    "enable_cover_photo": customization_data.enable_cover_photo,
                    "heading": customization_data.heading,
                    "description": customization_data.description,
                    "dark_mode": customization_data.dark_mode,
                    "color_selected": customization_data.color_selected,
                    "font": customization_data.font,
                    "image_data": customization_data.image_data,
                    "recently_used_colors": recently_used_colors,
                },
            )
            customization.create(session=session, created_by=token.get("email"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update customization: {str(e)}")

    # Return the response with the customization data
    return {
        "message": "Customization successfully created or updated.",
        "data": customization.settings,
    }

@router.get("/customizations/{domain}", response_model=CustomizationResponse)
def get_customization_by_domain(
    domain: str,
    token: dict = Depends(verify_firebase_token),
    session: Session = Depends(get_db),
):
    """
    Get customization settings for a user's career page based on the domain.
    """
    email = token.get("email")  # Extract the user's email from the token

    try:
        # Fetch the customization record using the `get_by_domain` method
        customization = Customization.get_by_domain(session=session, domain=domain, email=email)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching customization: {str(e)}",
        )

    if not customization:
        raise HTTPException(
            status_code=404,
            detail="Customization not found.",
        )

    # Retrieve and process settings
    settings = customization.settings

    # Validate and clean the data before returning
    image_data = settings.get("image_data")
    if image_data:
        try:
            # Ensure the image data is properly formatted as a base64 string
            base64.b64decode(image_data)  # Validate base64 encoding
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid image data: {str(e)}",
            )
    
    # Return the response with defaults for any missing fields
    return CustomizationResponse(
        domain=settings.get("domain", domain),
        enable_cover_photo=settings.get("enable_cover_photo", True),
        heading=settings.get("heading", "Join Us"),
        description=settings.get("description", "Explore opportunities."),
        dark_mode=settings.get("dark_mode", False),
        color_selected=settings.get("color_selected", "Blue"),
        font=settings.get("font", "Times New Roman"),
        image_data=image_data,
        recently_used_colors=settings.get("recently_used_colors", []),
    )

