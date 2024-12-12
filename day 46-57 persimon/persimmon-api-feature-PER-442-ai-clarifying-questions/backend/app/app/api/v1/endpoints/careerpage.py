from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, Form
from typing import Optional
from pydantic import BaseModel, Field
import os


# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

# Data Models
class CustomizeRequest(BaseModel):
    enable_cover_photo: bool = Field(..., description="Toggle for cover photo")
    heading: Optional[str] = Field("Join Us", max_length=15, description="Custom heading")
    description: Optional[str] = Field(
        "Explore opportunities that empower you to grow, innovate, and make an impact. Join a team where your talents are valued, your ideas are heard, and your career aspirations become a reality. Let’s build the future together!",
        max_length=250,
        description="Custom description",
    )
    dark_mode: bool = Field(False, description="Toggle for dark mode")
    primary_color: Optional[str] = Field(None, description="Primary color for CTA buttons")
    font: Optional[str] = Field(None, description="Font style from Google fonts")

class CancelRequest(BaseModel):
    confirm: bool = Field(..., description="Confirmation to cancel changes")

# In-memory database for simplicity (can be replaced with actual DB integration)
user_customizations = {}

# Helper Functions
def save_image(file: UploadFile, user_id: str) -> str:
    if not file.filename.endswith((".png", ".jpg")):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PNG and JPG are allowed.")

    upload_dir = f"uploads/{user_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return file_path

# Routes
@router.get("/customizations/{user_id}")
def get_customizations(user_id: str):
    """Fetch the customization settings for a user."""
    customization = user_customizations.get(user_id)
    if not customization:
        raise HTTPException(status_code=404, detail="Customization settings not found.")
    return customization

@router.post("/customizations/{user_id}")
def update_customizations(
    user_id: str,
    enable_cover_photo: bool = Form(...),
    heading: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    dark_mode: bool = Form(False),
    primary_color: Optional[str] = Form(None),
    font: Optional[str] = Form(None),
    file: Optional[UploadFile] = None,
):
    """Update customization settings for a user."""
    if enable_cover_photo:
        if not heading or not description:
            raise HTTPException(
                status_code=400, detail="Heading and description are required when cover photo is enabled."
            )

    image_path = None
    if file:
        image_path = save_image(file, user_id)

    user_customizations[user_id] = {
        "enable_cover_photo": enable_cover_photo,
        "heading": heading,
        "description": description,
        "dark_mode": dark_mode,
        "primary_color": primary_color,
        "font": font,
        "image_path": image_path,
    }

    return {"message": "Customization updated successfully.", "data": user_customizations[user_id]}

@router.delete("/customizations/{user_id}")
def delete_customizations(user_id: str):
    """Delete customization settings for a user."""
    if user_id in user_customizations:
        del user_customizations[user_id]
        return {"message": "Customization deleted successfully."}
    raise HTTPException(status_code=404, detail="Customization settings not found.")

@router.post("/customizations/{user_id}/cancel")
def cancel_customizations(user_id: str, cancel_request: CancelRequest):
    """Cancel customization changes for a user."""
    if cancel_request.confirm:
        if user_id in user_customizations:
            del user_customizations[user_id]
        return {"message": "Customization changes discarded successfully."}
    raise HTTPException(status_code=400, detail="Cancellation not confirmed.")

@router.post("/customizations/{user_id}/submit")
def submit_customizations(user_id: str):
    """Submit customization settings for a user."""
    customization = user_customizations.get(user_id)
    if not customization:
        raise HTTPException(status_code=404, detail="No customization settings found to submit.")

    # Simulate saving the customizations permanently (e.g., to a database)
    return {"message": "Customization changes submitted successfully.", "data": customization}

# Add router to app
app.include_router(router)