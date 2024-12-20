from fastapi import UploadFile
from typing import Optional

def save_image(file: UploadFile, domain: str) -> Optional[bytes]:
    """Save the uploaded image as binary data (blob)."""
    try:
        # Read the uploaded file content as binary
        image_data = file.file.read()
        return image_data  # Return the binary data
    except Exception as e:
        print(f"Error saving image: {e}")
        return None
