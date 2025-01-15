import os
from google.cloud import storage
from google.oauth2 import service_account
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import textwrap

SA_KEY = {
    "type": os.getenv("CLOUD_STORAGE_TYPE"),
    "project_id": os.getenv("CLOUD_STORAGE_PROJECT_ID"),
    "private_key_id": os.getenv("CLOUD_STORAGE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("CLOUD_STORAGE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("CLOUD_STORAGE_CLIENT_EMAIL"),
    "client_id": os.getenv("CLOUD_STORAGE_CLIENT_ID"),
    "auth_uri": os.getenv("CLOUD_STORAGE_AUTH_URI"),
    "token_uri": os.getenv("CLOUD_STORAGE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("CLOUD_STORAGE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLOUD_STORAGE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("CLOUD_STORAGE_UNIVERSE_DOMAIN"),
}

async def upload_to_gcp(bucket_name: str, source_file, destination_path: str) -> str:
    credentials = service_account.Credentials.from_service_account_info(SA_KEY)
    storage_client = storage.Client(credentials=credentials, project=SA_KEY["project_id"])
    bucket = storage_client.bucket(bucket_name)
    try:
        if isinstance(source_file, str):
            if not os.path.exists(source_file):
                return
            with open(source_file, "rb") as f:
                blob = bucket.blob(destination_path)
                blob.upload_from_file(f)
        elif hasattr(source_file, 'read'):
            if source_file.closed:
                raise ValueError("The source file is closed and cannot be uploaded.")
            else:
                source_file.seek(0)  # Reset the pointer to the start
                blob = bucket.blob(destination_path)
                blob.upload_from_file(source_file)
        else:
            return
        
        if blob.exists():
            gcp_uri = f"gs://{bucket_name}/{destination_path}"
            return gcp_uri
        else:
            raise ValueError("Upload verification failed.")
    except Exception as e:
        raise ValueError(f"The file is unable to upload {destination_path}")

def docx_to_pdf(docx_data: bytes) -> BytesIO:
    """Converts DOCX file data to PDF and returns it as a BytesIO object."""
    document = Document(BytesIO(docx_data))

    # Create a BytesIO buffer for the PDF
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
        wrapper = textwrap.TextWrapper(width=int(max_width / 6))  # Approximate character count per line
        lines = wrapper.wrap(text)
        wrapped_lines.extend(lines)
        return wrapped_lines

    # Iterate through the paragraphs in the DOCX file and add them to the PDF
    for para in document.paragraphs:
        # Wrap the text to fit the page width
        lines = wrap_text(para.text, page_width)

        # Check for bold and italic styles (if any)
        for line in lines:
            if y_position <= line_height:  # Check if we are too close to the bottom of the page
                c.showPage()  # Create a new page in the PDF
                c.setFont("Helvetica", 12)
                y_position = height - 40  # Reset the y position

            # Set font style based on paragraph's formatting
            if para.style.font.bold:
                draw_text(line, y_position, font_name="Helvetica-Bold", font_size=12)
            elif para.style.font.italic:
                draw_text(line, y_position, font_name="Helvetica-Oblique", font_size=12)
            else:
                draw_text(line, y_position)

            y_position -= line_height  # Move to the next line with spacing

        # Handle paragraph spacing (space between paragraphs)
        if para.text:  # If the paragraph is not empty, add extra space after it
            y_position -= 5  # Adjust this value for the desired spacing between paragraphs

    # Save the PDF into the BytesIO object
    c.save()
    pdf_output.seek(0)  # Rewind the BytesIO object to the beginning
    return pdf_output


def wrap_text(text, max_width):
    """Wrap text to fit the specified width."""
    wrapped_lines = []
    wrapper = textwrap.TextWrapper(width=int(max_width / 6))  # Approximate character count per line
    lines = wrapper.wrap(text)
    
    # Add wrapped lines to the list
    wrapped_lines.extend(lines)
    return wrapped_lines

def retrieve_from_gcp(bucket_name: str, file_path: str, download_filename: str, action: str):
    try:
        credentials = service_account.Credentials.from_service_account_info(SA_KEY)
        storage_client = storage.Client(credentials=credentials, project=SA_KEY["project_id"])
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        if not blob.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Download the file data
        file_data = blob.download_as_bytes()

        # Check file extension
        file_extension = os.path.splitext(file_path)[1].lower()

        # If the file is DOCX, convert it to PDF
        if file_extension == ".docx":
            pdf_file = docx_to_pdf(file_data)
            content_type = "application/pdf"
        elif file_extension == ".pdf":
            # If the file is already a PDF, use it as-is
            pdf_file = BytesIO(file_data)  # Use the existing file data as a PDF
            content_type = "application/pdf"
        else:
            # Unsupported file type
            raise HTTPException(status_code=415, detail="Unsupported file type")

        # Set headers for download or inline viewing
        headers = {}
        if action == "download":
            headers["Content-Disposition"] = f'attachment; filename="{download_filename}"'
            headers["Access-Control-Expose-Headers"] = "Content-Disposition"
            headers["Access-Control-Allow-Origin"] = "*"
        else:
            headers["Content-Disposition"] = f'inline; filename="{download_filename}"'

        # Return the file as a streaming response
        return StreamingResponse(
            pdf_file,  # Streaming PDF content
            media_type=content_type,  # Return PDF file
            headers=headers
        )
    except HTTPException as e:
        raise e


async def send_message_to_pubsub(message_data: dict, topic_name: str) -> dict:
    """
    Publishes a message to the Google Cloud Pub/Sub topic and generates a response.
    
    Args:
        message_data (dict): The data to be sent as a message.
        
    Returns:
        dict: A response containing the Pub/Sub message ID and status.
        
    Raises:
        Exception: If any error occurs during publishing.
    """
    # Initialize the Pub/Sub Publisher Client
    credentials = service_account.Credentials.from_service_account_info(SA_KEY)
    publisher = pubsub_v1.PublisherClient(credentials=credentials)

    # Configure your Google Cloud project and topic
    project_id = os.getenv("CLOUD_STORAGE_PROJECT_ID")
    topic_path = publisher.topic_path(project_id, topic_name)
    
    try:
        # Convert the dictionary data to a JSON string
        json_message = json.dumps(message_data)

        # Convert the JSON string to bytes (Pub/Sub expects bytes)
        data = json_message.encode("utf-8")

        # Publish the message to the Pub/Sub topic
        future = publisher.publish(topic_path, data=data)

        # Wait for the publish to complete and return the response
        message_id = future.result()
        return {"topic": topic_path, "message_id": message_id, "data": data, "status": "Message sent successfully"}
    except Exception as e:
        raise Exception(f"Failed to send message: {e}")
