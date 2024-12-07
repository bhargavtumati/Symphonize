# import boto3
from io import BytesIO

# from joblib import load
import os
from google.cloud import storage
from google.oauth2 import service_account

SA_KEY = {
    "type": os.getenv("CLOUD_STORAGE_TYPE"),
    "project_id": os.getenv("CLOUD_STORAGE_PROJECT_ID"),
    "private_key_id": os.getenv("CLOUD_STORAGE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("CLOUD_STORAGE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("CLOUD_STORAGE_CLIENT_EMAIL"),
    "client_id": os.getenv("CLOUD_STORAGE_CLIENT_ID"),
    "auth_uri": os.getenv("CLOUD_STORAGE_AUTH_URI"),
    "token_uri": os.getenv("CLOUD_STORAGE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv(
        "CLOUD_STORAGE_AUTH_PROVIDER_X509_CERT_URL"
    ),
    "client_x509_cert_url": os.getenv("CLOUD_STORAGE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("CLOUD_STORAGE_UNIVERSE_DOMAIN"),
}


def load_model_from_s3(bucket_name, model_key):
    """Loads a model from an S3 bucket.

    Args:
      bucket_name: The name of the S3 bucket.
      model_key: The path to the model file within the bucket.

    Returns:
      The loaded model.
    """


# s3 = boto3.client('s3')
# obj = s3.get_object(Bucket=bucket_name, Key=model_key)
# model_bytes = obj['Body'].read()
# model = load(BytesIO(model_bytes))
# return model


async def upload_to_gcp(bucket_name: str, source_file, destination_path: str) -> str:
    credentials = service_account.Credentials.from_service_account_info(SA_KEY)
    storage_client = storage.Client(
        credentials=credentials, project=SA_KEY["project_id"]
    )

    # Initialize the bucket at the start
    bucket = storage_client.bucket(bucket_name)
    print("this is the storage bucket")
    try:
        if isinstance(source_file, str):
            if not os.path.exists(source_file):
                print(f"File path '{source_file}' does not exist.")
                return
            with open(source_file, "rb") as f:
                blob = bucket.blob(destination_path)
                blob.upload_from_file(f)
        elif hasattr(source_file, "read"):
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
            gcp_uri = f"gs://{bucket_name}/{destination_path}"
            print(f"File successfully uploaded to {gcp_uri}.")
            return gcp_uri
        else:
            raise ValueError("Upload verification failed.")
    except Exception as e:
        print(f"Unexpected error within the if-else block: {e}")
        return f"The file is unable to upload {destination_path}"
