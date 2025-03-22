import fitz
import base64
import cv2
import numpy as np
from docx import Document
from io import BytesIO
from fastapi import HTTPException

def extract_first_face_from_pdf(image_bytes: BytesIO):
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
                        return base64.b64encode(image_data).decode("utf-8")

        return None 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting face image from PDF: {str(e)}")

def extract_first_face_from_docx(docx_path: BytesIO):
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
                    return base64.b64encode(image).decode("utf-8")

        return None  
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting face image from docx: {str(e)}")
    

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