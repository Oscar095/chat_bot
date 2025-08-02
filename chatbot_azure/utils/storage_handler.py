from azure.storage.blob import BlobServiceClient
import os

def list_files(container_name):
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = service_client.get_container_client(container_name)

    files = [blob.name for blob in container_client.list_blobs()]
    return files
