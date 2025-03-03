import fitz
import base64
from docx import Document
from io import BytesIO
from fastapi import HTTPException

def extract_first_image_from_pdf(image_bytes: BytesIO):
    try:
        pdf_document = fitz.open(stream=image_bytes, filetype="pdf")
        
        if len(pdf_document) > 0:
            page = pdf_document.load_page(0)  
            image_list = page.get_images(full=True)

            if image_list:  
                xref = image_list[0][0] 
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                return base64.b64encode(image_bytes).decode("utf-8") 

        return None 
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error extracting image from PDF")

def extract_first_image_from_docx(docx_path: BytesIO):
    try:
        doc = Document(docx_path)
        
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref: 
                image = rel.target_part.blob  
                return base64.b64encode(image).decode("utf-8") 

        return None  
    except Exception as e:
        print(e)
