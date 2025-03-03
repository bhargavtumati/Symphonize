from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from app.utils.validators import (
    is_non_empty,
    validate_length,
    has_proper_characters,
    validate_letters_and_numbers,
    validate_list_len
)
import base64
import imghdr

class CustomizationModel(BaseModel):
    career_page_url: Optional[str] = None
    enable_cover_photo: Optional[bool] = Field(default=True)
    heading: Optional[str] = Field(default="Join Us")
    description: Optional[str] = Field(default='''Explore opportunities that empower you to grow, innovate, and make an impact. 
    Join a team where your talents are valued, your ideas are heard, and your career aspirations become a reality. Let’s build the future together!''')
    enable_dark_mode: Optional[bool] = Field(default=False)
    color_selected: Optional[str] = None
    primary_colors: Optional[List[str]] = None
    selected_header_color: Optional[str] = None
    header_colors: Optional[List[str]] = None
    font_style: Optional[str] = None
    image_data: Optional[str] = None
    logo_data: Optional[str] = None

    @field_validator("heading")
    def validate_heading(cls, heading):
        is_non_empty(value=heading, field_name="Heading")
        has_proper_characters(value=heading, field_name="Heading")
        validate_letters_and_numbers(value=heading, field_name="Heading")
        return validate_length(value=heading, min_len=0, max_len=15, field_name="Heading")

    @field_validator("description")
    def validate_description(cls, description):
        is_non_empty(value=description, field_name="Description")
        has_proper_characters(value=description, field_name="Description")
        return validate_length(value=description, min_len=0, max_len=250, field_name="Description")

    @staticmethod
    def decode_and_validate_image(image_data):
        if image_data:
            try:
                decoded_image = base64.b64decode(image_data)
                image_size_in_mb = len(decoded_image) / (1024 * 1024)

                if not (image_size_in_mb <= 2):
                    raise ValueError("Image size must be less than or equal to 2MB.")

                image_type = imghdr.what(None, decoded_image)
                if image_type not in ['jpeg', 'png']:
                    # Check for SVG explicitly
                    if not (decoded_image.strip().startswith(b'<?xml') and b'<svg' in decoded_image):
                        raise ValueError("Image must be of type JPEG, PNG, or SVG.")
            except Exception as e:
                raise ValueError(f"Invalid image data: {e}")
        return image_data

    @field_validator("image_data")
    def validate_image_data(cls, image_data):
        return cls.decode_and_validate_image(image_data)

    @field_validator("logo_data")
    def validate_logo_data(cls, logo_data):
         return cls.decode_and_validate_image(logo_data)

    @field_validator("primary_colors")
    def validate_primary_colors(cls, primary_colors):
         return validate_list_len(primary_colors, 10, "colors")

    @field_validator("header_colors")
    def validate_header_colors(cls, header_colors):
         return validate_list_len(header_colors, 10, "colors")
