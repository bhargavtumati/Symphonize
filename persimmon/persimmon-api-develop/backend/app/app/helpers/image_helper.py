import logging
from pathlib import Path
import os
import uuid
import fitz
import base64
import cv2
import numpy as np
from docx import Document
from io import BytesIO
from fastapi import HTTPException

from app.helpers.data_helper import read_any_file


PERSIMMON_IMAGES_BUCKET = os.getenv("PERSIMMON_IMAGES_BUCKET")
ENVIRONMENT = os.getenv("ENVIRONMENT")


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d (%(funcName)s): %(message)s"
)

logger = logging.getLogger(__name__)

def extract_first_face_from_pdf(image_bytes: BytesIO, file_name: str):
    try:
        pdf_document = fitz.open(stream=image_bytes, filetype="pdf")
        
        if len(pdf_document) > 0:
            page = pdf_document.load_page(0)  
            image_list = page.get_images(full=True)

            if image_list:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                
                for img in image_list:
                    xref = img[0] 
                    base_image = pdf_document.extract_image(xref)
                    image_data = base_image["image"]
                    
                    # Convert image to OpenCV format
                    np_img = np.frombuffer(image_data, dtype=np.uint8)
                    img_cv = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

                    # Detect faces
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                    if len(faces) > 0:
                        main_path = f"/{PERSIMMON_IMAGES_BUCKET}/{ENVIRONMENT}/applicant/profile-images"

                        unique_id = uuid.uuid4()

                        # Generate unique filename
                        file_name = f"{unique_id}_{file_name}.jpg"
                        file_path = Path(main_path) / file_name

                        # Save the extracted face image
                        cv2.imwrite(str(file_path), img_cv)

                        return str(file_path)

        return None 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting face image from PDF: {str(e)}")

def extract_first_face_from_docx(docx_path: BytesIO,file_name: str):
    try:
        doc = Document(docx_path)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                image = rel.target_part.blob  

                # Convert image to OpenCV format
                np_img = np.frombuffer(image, dtype=np.uint8)
                img_cv = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

                # Convert to grayscale for face detection
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                if len(faces) > 0: 
                    main_path = f"/{PERSIMMON_IMAGES_BUCKET}/{ENVIRONMENT}/applicant/profile-images"

                    unique_id = uuid.uuid4()

                    # Generate unique filename
                    file_name = f"{unique_id}_{file_name}.jpg"
                    file_path = Path(main_path) / file_name

                    # Save the extracted face image
                    cv2.imwrite(str(file_path), img_cv)

                    return str(file_path)  
                
        return None  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting face image from docx: {str(e)}")
    

def save_image_to_destination(file, main_path) -> str:
    if not file.content_type.startswith("image/"):
        raise ValueError("Only image files are allowed.")
    
    unique_id = uuid.uuid4()
    original_file_name = f"{unique_id}_{file.filename}"
    destination = Path(main_path) / original_file_name

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        content = file.file.read()
        with open(destination, 'wb') as writer:
            writer.write(content)
        print(f"Image saved at: {destination}")
        return destination.as_posix()  # Convert to forward slashes

    except Exception as e:
        raise IOError(f"Failed to save image: {e}")
    

async def get_base64_image(file_path: str):
    try:
        content = await read_any_file(file_path=file_path)
        return binary_to_base64(content)
    except Exception as e:
        logger.error(f"Failed to get base64 image: {e}")
        return None


def binary_to_base64(binary_data: bytes) -> str:
    """
    Converts raw binary data to Base64 encoded string.

    Args:
        binary_data: The raw binary data (bytes).

    Returns:
        The Base64 encoded string.
    """
    base64_encoded = base64.b64encode(binary_data).decode('utf-8')
    return base64_encoded


def get_initials(name):
    parts = name.split()  # Split by spaces
   
    first_initial = parts[0][0].upper()  # First letter of first name
    last_initial = parts[-1][0].upper()  # First letter of last name
    return first_initial + last_initial