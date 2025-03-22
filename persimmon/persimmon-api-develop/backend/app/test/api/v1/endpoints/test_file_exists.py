from google.cloud import storage
from google.oauth2 import service_account
import os


SA_KEY = {
    "type": os.getenv("CLOUD_STORAGE_TYPE"),
    "project_id": os.getenv("CLOUD_STORAGE_PROJECT_ID"),
    "private_key_id": os.getenv("CLOUD_STORAGE_PRIVATE_KEY_ID"),
    # "private_key": os.getenv("CLOUD_STORAGE_PRIVATE_KEY").replace("\\n", "\n"), 
    "client_email": os.getenv("CLOUD_STORAGE_CLIENT_EMAIL"),
    "client_id": os.getenv("CLOUD_STORAGE_CLIENT_ID"),
    "auth_uri": os.getenv("CLOUD_STORAGE_AUTH_URI"),
    "token_uri": os.getenv("CLOUD_STORAGE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("CLOUD_STORAGE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLOUD_STORAGE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("CLOUD_STORAGE_UNIVERSE_DOMAIN"),
}


def download_file_from_gcp(bucket_name, source_blob_name, destination_file_name):
    """Downloads a file from the GCP bucket."""
    # Initialize a storage client
    credentials = service_account.Credentials.from_service_account_info(SA_KEY)
    storage_client = storage.Client(credentials=credentials, project=SA_KEY["project_id"])

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Get the blob (file) from the bucket
    blob = bucket.blob(source_blob_name)

    # Download the file to the destination
    blob.download_to_filename(destination_file_name)

    print(f"File {source_blob_name} downloaded to {destination_file_name}.")

if __name__ == "__main__":


    download_file_from_gcp("Bucket Name","file name" ,"destination file name")