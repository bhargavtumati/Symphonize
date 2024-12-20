from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class CustomizationBase(BaseModel):
    domain: str = Field(..., description="The domain of the career page")
    enable_cover_photo: bool = Field(..., description="Flag to enable or disable the cover photo")
    heading: Optional[str] = Field("Welcome to Career Page", description="The heading for the career page")
    description: Optional[str] = Field("Here you can explore opportunities.", description="Description for the career page")
    dark_mode: bool = Field(False, description="Flag to enable or disable dark mode")
    color_selected: Optional[str] = Field("blue", description="The primary selected color")
    font: Optional[str] = Field("Times New Roman", description="The font for the career page")
    image_data: Optional[str] = Field(None, description="Base64-encoded image data for the cover photo")
    recently_used_colors: Optional[List[str]] = Field(default=[], description="List of recently used colors")


class CustomizationCreate(CustomizationBase):
    file: Optional[str] = Field(None, description="The uploaded image file (Base64-encoded for now)")


class CustomizationUpdate(CustomizationBase):
    pass


class CustomizationResponse(CustomizationBase):
    pass
