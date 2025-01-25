import PyPDF2
from fastapi import APIRouter, UploadFile
import pdfplumber
import os,io
from tika import parser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import aiofiles, tempfile, textwrap
from docx import Document
from io import BytesIO

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
            text += page.extract_text() + '\n'
    
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
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_path = temp_file.name
            await temp_file.write(await file.read())
        
        # Use Tika to parse the file content via file path
        #print(f"the file path is {temp_file_path}")
        parsed = parser.from_file(temp_file_path)
        print("this is the parsed ",parsed)
        text = parsed.get('content', '')
        if  text is None:
            return ""
        else:
            return text.strip()

    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
    finally:
        # Clean up the temporary file
        import os
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def convert_docx_to_pdf(text:str, output_path: str):
    try:
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        y = height - 40  # Start from the top of the page
        
        try : 
            for line in text.splitlines():  # Split text by lines to handle multi-line paragraphs
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

def convert_docx_to_pdf_stream(docx_data: bytes) -> BytesIO:
    """Converts DOCX file data to PDF and returns it as a BytesIO object."""
    document = Document(BytesIO(docx_data))

    pdf_output = BytesIO()
    c = canvas.Canvas(pdf_output, pagesize=letter)
    c.setFont("Helvetica", 12)

    width, height = letter  # Page size width and height
    y_position = height - 40  # Initial position to start drawing text on the PDF
    line_height = 14  # Space between lines
    margin = 30  # Left margin for text
    page_width = width - 2 * margin

    def draw_text(text, y_pos, font_name="Helvetica", font_size=12):
        """Helper function to draw wrapped text with custom font and size."""
        c.setFont(font_name, font_size)
        c.drawString(margin, y_pos, text)

    def wrap_text(text, max_width):
        """Wrap text to fit the specified width."""
        wrapped_lines = []
        wrapper = textwrap.TextWrapper(width=int(max_width / 6)) 
        lines = wrapper.wrap(text)
        wrapped_lines.extend(lines)
        return wrapped_lines

    for para in document.paragraphs:
        lines = wrap_text(para.text, page_width)

        for line in lines:
            if y_position <= line_height: 
                c.showPage()  
                c.setFont("Helvetica", 12)
                y_position = height - 40  

            is_bold = any(run.bold for run in para.runs if run.bold is not None)
            is_italic = any(run.italic for run in para.runs if run.italic is not None)

            if is_bold:
                draw_text(line, y_position, font_name="Helvetica-Bold", font_size=12)
            elif is_italic:
                draw_text(line, y_position, font_name="Helvetica-Oblique", font_size=12)
            else:
                draw_text(line, y_position)

            y_position -= line_height

        if para.text:  
            y_position -= 5 

    c.save()
    pdf_output.seek(0)  
    return pdf_output
