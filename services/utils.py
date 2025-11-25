import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def get_env(key: str, default=None):
    """
    Fetch environment variables safely with a default fallback.
    Example:
        get_env("GOOGLE_API_KEY")
    """
    return os.getenv(key, default)


def get_upload_path() -> str:
    """
    Returns the absolute path to the folder where uploaded PDF statements are stored.
    Creates the directory if missing.
    """
    path = os.path.join(os.getcwd(), "uploads", "statements")
    os.makedirs(path, exist_ok=True)
    return path


def list_uploaded_files() -> list:
    """
    Lists all uploaded PDF files in the uploads/statements directory.
    """
    path = get_upload_path()
    return [f for f in os.listdir(path) if f.lower().endswith(".pdf")]
