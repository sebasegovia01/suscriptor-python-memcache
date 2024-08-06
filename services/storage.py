import asyncio
import logging
from google.cloud import storage
from google.oauth2 import service_account
from os import getenv
from dotenv import load_dotenv

# Configure logging to output detailed logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables from a .env file.
load_dotenv()

# Load credentials and bucket name from environment variables.
credentials_path = getenv("GCP_CREDENTIALS")
bucket_name = getenv("BUCKET_NAME")

# Initialize the Google Cloud Storage client with the specified credentials.
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = storage.Client(credentials=credentials, project=credentials.project_id)
bucket = client.bucket(bucket_name)


async def upload_file(file_content: bytes, file_name: str, content_type: str) -> str:
    """
    Asynchronously uploads a file to Google Cloud Storage.
    Args:
        file_content (bytes): The content of the file.
        file_name (str): The name of the file to save.
        content_type (str): MIME type of the file.

    Returns:
        str: The name of the file after it has been uploaded.
    """
    blob = bucket.blob(file_name)
    loop = asyncio.get_running_loop()
    func = lambda: blob.upload_from_string(file_content, content_type)
    await loop.run_in_executor(None, func)
    return file_name


def download_file(file_path: str) -> bytes:
    """
    Downloads a file from Google Cloud Storage.
    Args:
        file_path (str): The full path of the file in the bucket.
        bucket_name (str): The name of the bucket containing the file. Defaults to BUCKET_NAME from env.

    Returns:
        bytes: The content of the file, or None if the file does not exist.
    """
    try:
        blob = bucket.blob(file_path)

        logging.info(
            f"Attempting to download blob: {file_path} from bucket: {bucket_name}"
        )

        if not blob.exists():
            logging.error(f"Blob {file_path} does not exist in bucket {bucket_name}.")
            return None

        logging.info(f"Blob {file_path} exists in bucket {bucket_name}. Downloading...")
        file_bytes = blob.download_as_bytes()
        logging.info(
            f"File {file_path} downloaded successfully from bucket {bucket_name}."
        )
        return file_bytes
    except Exception as e:
        logging.error(
            f"An error occurred while downloading {file_path} from bucket {bucket_name}: {str(e)}",
            exc_info=True,
        )
        return None


def list_files() -> list:
    """
    Lists all files stored in the specified Google Cloud Storage bucket.

    Returns:
        list: A list of file names in the bucket.
    """
    blobs = bucket.list_blobs(bucket_name)
    return [blob.name for blob in blobs]
