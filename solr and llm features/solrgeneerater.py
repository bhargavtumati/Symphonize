from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os
import json
from docx import Document as DocxDocument

app = FastAPI()

# Ensure a directory to store the .txt and .json files
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Function to extract text from a .docx file
def extract_text_from_docx(docx_file):
    doc = DocxDocument(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

# Endpoint to upload document
@app.post("/upload_document/")
async def upload_document(file: UploadFile = File(...), title: str = "", author: str = "", published_date: str = ""):
    try:
        # Save the uploaded file temporarily
        file_location = f"downloads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        # Extract text from the uploaded document
        extracted_text = extract_text_from_docx(file_location)

        # Create JSON object
        document_data = {
            "title": title,
            "author": author,
            "published_date": published_date,
            "content": extracted_text
        }

        # Save the extracted text as a .txt file
        txt_file_location = f"downloads/{file.filename}.txt"
        with open(txt_file_location, "w") as txt_file:
            txt_file.write(extracted_text)

        # Save the document data as a .json file
        json_file_location = f"downloads/{file.filename}.json"
        with open(json_file_location, "w") as json_file:
            json.dump(document_data, json_file, indent=4)

        return {
            "message": "Document uploaded, text extracted, and saved as both .txt and .json!",
            "download_txt_link": f"/download/{file.filename}.txt",
            "download_json_link": f"/download/{file.filename}.json"
        }

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

# Endpoint to download the .txt or .json file
@app.get("/download/{filename}")
async def download_file(filename: str):
    txt_file_path = f"downloads/{filename}"
    if os.path.exists(txt_file_path):
        return FileResponse(txt_file_path)
    return {"error": "File not found"}
