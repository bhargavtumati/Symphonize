import os
from google.cloud import storage, pubsub_v1
from google.oauth2 import service_account
from fastapi.responses import StreamingResponse
from fastapi import HTTPException
import json
from io import BytesIO
from app.helpers import pdf_helper as pdfh

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
    print("this is the type of the source file ",type(source_file))
    # Initialize the bucket at the start
    bucket = storage_client.bucket(bucket_name)
    print("this is the storage bucket")
    try:
        if isinstance(source_file, str):
            print("Entered the if block...")
            if not os.path.exists(source_file):
                print(f"File path '{source_file}' does not exist.")
                return
            with open(source_file, "rb") as f:
                blob = bucket.blob(destination_path)
                blob.upload_from_file(f)
        elif hasattr(source_file, 'read'):
            print("Entered the elif block...")
            if source_file.closed:
                print("source_file is closed. Attempting to reopen...")
                raise ValueError("The source file is closed and cannot be uploaded.")
            else:
                # Ensure the file pointer is at the beginning before upload
                source_file.seek(0)  # Reset the pointer to the start
                blob = bucket.blob(destination_path)
                blob.upload_from_file(source_file)
        else:
            print("Neither 'if' nor 'elif' was executed. Unexpected source_file type.")
            return
        
        print("Finished upload check...")
        
        # Verify the upload
        if blob.exists():
            # gcp_uri = f"gs://{bucket_name}/{destination_path}"
            gcp_uri = f"{destination_path}"
            print(f"File successfully uploaded to {gcp_uri}.")
            return gcp_uri
        else:
            raise ValueError("Upload verification failed.")
    except Exception as e:
        print(f"Unexpected error within the if-else block: {e}")
        raise ValueError(f"The file is unable to upload {destination_path}")

def retrieve_from_gcp(bucket_name: str, file_path: str, download_filename: str, action: str):
    try:
        credentials = service_account.Credentials.from_service_account_info(SA_KEY)
        storage_client = storage.Client(credentials=credentials, project=SA_KEY["project_id"])
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)

        if not blob.exists():
            raise HTTPException(status_code=404, detail="File not found")

        file_data = blob.download_as_bytes()
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == ".docx":
            pdf_file = pdfh.convert_docx_to_pdf_stream(file_data)
        elif file_extension == ".pdf":
            pdf_file = BytesIO(file_data)
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        headers = {}
        if action == "download":
            headers["Content-Disposition"] = f'attachment; filename="{download_filename}"'
            headers["Access-Control-Expose-Headers"] = "Content-Disposition"
            headers["Access-Control-Allow-Origin"] = "*"
        else:
            headers["Content-Disposition"] = f'inline; filename="{download_filename}"'

        return StreamingResponse(
            pdf_file,  
            media_type="application/pdf",  
            headers=headers
        )
    except HTTPException as e:
        raise e
    


async def send_message_to_pubsub(message_data: dict,topic_name:str) -> dict:
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

    topic_name = topic_name
    
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

# async def download_from_gcp(bucket_name: str, source_blob_name: str, destination_file_name: str) -> str:
#     """
#     Downloads a file from the Google Cloud Storage bucket and saves it to a local file.

#     Args:
#         bucket_name (str): The name of the Google Cloud Storage bucket.
#         source_blob_name (str): The name of the object to download in the bucket.
#         destination_file_name (str): The name of the file to save the object as.

#     Returns:
#         str: The path to the downloaded file.
#     """
#     # Initialize the Google Cloud Storage Client
#     credentials = service_account.Credentials.from_service_account_info(SA_KEY)
#     storage_client = storage.Client(credentials=credentials, project=SA_KEY["project_id"])

#     # Initialize the bucket at the start
#     bucket = storage_client.bucket(bucket_name)

#     # Download the file
#     blob = bucket.blob(source_blob_name)
#     blob.download_to_filename(destination_file_name)

#     with open(destination_file_name, 'rb') as f:
#         return f.read()
    
async def download_from_gcp(bucket_name: str, source_blob_name: str, destination_file_name: str) -> str:
    """
    Downloads a file from the Google Cloud Storage bucket and saves it to a local file.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket.
        source_blob_name (str): The name of the object to download in the bucket.
        destination_file_name (str): The name of the file to save the object as.

    Returns:
        str: The path to the downloaded file.
    """
    # Initialize the Google Cloud Storage Client
    credentials = service_account.Credentials.from_service_account_info(SA_KEY)
    storage_client = storage.Client(credentials=credentials, project=SA_KEY["project_id"])

    # Initialize the bucket at the start
    bucket = storage_client.bucket(bucket_name)

    # Download the file
    blob = bucket.blob(source_blob_name)
    file_content = blob.download_as_bytes()
    return BytesIO(file_content)
