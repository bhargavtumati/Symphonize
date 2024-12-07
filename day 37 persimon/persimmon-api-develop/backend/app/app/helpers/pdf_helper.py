import PyPDF2
from fastapi import APIRouter, UploadFile
import pdfplumber
import os, io
from tika import parser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import aiofiles
import tempfile


def get_text_from_stream(stream):
    text = ""
    pdf_reader = PyPDF2.PdfReader(stream)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


async def extract_text_from_pdf(uploaded_file: UploadFile):
    # Read the contents of the uploaded file
    file_contents = await uploaded_file.read()

    # Use pdfplumber to extract text
    text = ""

    with pdfplumber.open(io.BytesIO(file_contents)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    return text


async def extract_text_from_file(file) -> str:
    """
    Extracts text from a DOCX or PDF file by saving it temporarily
    and passing the file path to Apache Tika for reliable processing.

    :param file: A file-like object (e.g., UploadFile).
    :return: Extracted text as a string.
    """
    try:
        # Create a temporary file to save the uploaded file content
        async with aiofiles.tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file.filename.split('.')[-1]}"
        ) as temp_file:
            temp_file_path = temp_file.name
            await temp_file.write(await file.read())

        # Use Tika to parse the file content via file path
        # print(f"the file path is {temp_file_path}")
        parsed = parser.from_file(temp_file_path)
        text = parsed.get("content", "").strip()

        return text

    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
    finally:
        # Clean up the temporary file
        import os

        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def convert_docx_to_pdf(text: str, output_path: str):
    try:

        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        y = height - 40  # Start from the top of the page

        try:
            for (
                line
            ) in (
                text.splitlines()
            ):  # Split text by lines to handle multi-line paragraphs
                c.drawString(40, y, line.strip())  # Write each line to the PDF
                y -= 15
                if y < 40:  # Move to a new page if necessary
                    c.showPage()
                    y = height - 40
        except Exception as e:
            print(f"the exception is with the line ")
        c.save()  # Save the PDF file
        return output_path

    except Exception as e:
        print(f"Failed to convert given in the pdf conversion function to PDF: {e}")
        return None
