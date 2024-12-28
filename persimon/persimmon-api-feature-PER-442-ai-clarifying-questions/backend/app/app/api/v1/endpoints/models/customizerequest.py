from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from app.utils.validators import (
    is_non_empty,
    validate_length,
    has_proper_characters,
    validate_letters_and_numbers
)
import base64
import imghdr
from io import BytesIO

class CustomizationBase(BaseModel):
    domain: str = Field(..., description="The domain of the career page")
    enable_cover_photo: bool = Field(..., description="Flag to enable or disable the cover photo")
    heading: Optional[str] = Field("Welcome to Career Page", description="The heading for the career page")
    description: Optional[str] = Field("Here you can explore opportunities.", description="Description for the career page")
    dark_mode: bool = Field(False, description="Flag to enable or disable dark mode")
    color_selected: Optional[str] = Field("Blue", description="The primary selected color")
    font: Optional[str] = Field("Times New Roman", description="The font for the career page")
    image_data: Optional[str] = Field(None, description="Base64-encoded image data for the cover photo")
    recently_used_colors: Optional[List[str]] = Field(default=[], description="List of recently used colors")

    # Validate heading
    @field_validator("heading")
    def validate_heading(cls, heading):
        is_non_empty(value=heading, field_name="Heading")
        has_proper_characters(value=heading, field_name="Heading")
        validate_letters_and_numbers(value=heading, field_name="Heading")
        return validate_length(value=heading, min_len=0, max_len=50, field_name="Heading")

    # Validate description
    @field_validator("description")
    def validate_description(cls, description):
        is_non_empty(value=description, field_name="Description")
        has_proper_characters(value=description, field_name="Description")
        return validate_length(value=description, min_len=0, max_len=250, field_name="Description")

    # Validate image size and type (Base64 encoded image data)
    @field_validator("image_data")
    def validate_image_size_and_type(cls, image_data):
        if image_data:
            try:
                # Decode the Base64 image data
                decoded_image = base64.b64decode(image_data)
                image_size_in_mb = len(decoded_image) / (1024 * 1024)  # Convert bytes to MB

                # Check size constraints (between 2MB and 5MB)
                if not (2 <= image_size_in_mb <= 5):
                    raise ValueError("Image size must be between 2MB and 5MB. "+str(image_size_in_mb))
                
                # Check the image type (JPEG or PNG)
                image_type = imghdr.what(None, decoded_image)
                if image_type not in ['jpeg', 'png']:
                    raise ValueError("Image must be of type JPEG or PNG.")
            except Exception as e:
                raise ValueError(f"Invalid image data: {e}")
        return image_data

# Create customization model for creating a new customization
class CustomizationCreate(CustomizationBase):
    file: Optional[str] = Field(None, description="The uploaded image file (Base64-encoded for now)")

# Customization model for updating an existing customization
class CustomizationUpdate(CustomizationBase):
    pass

# Customization response model (for API responses)
class CustomizationResponse(CustomizationBase):
    pass
