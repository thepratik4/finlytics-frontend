# import os
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()


# def get_env(key: str, default=None):
#     """
#     Fetch environment variables safely with a default fallback.
#     Example:
#         get_env("GOOGLE_API_KEY")
#     """
#     return os.getenv(key, default)


# def get_upload_path() -> str:
#     """
#     Returns the absolute path to the folder where uploaded PDF statements are stored.
#     Creates the directory if missing.
#     """
#     path = os.path.join(os.getcwd(), "uploads", "statements")
#     os.makedirs(path, exist_ok=True)
#     return path


# def list_uploaded_files() -> list:
#     """
#     Lists all uploaded PDF files in the uploads/statements directory.
#     """
#     path = get_upload_path()
#     return [f for f in os.listdir(path) if f.lower().endswith(".pdf")]

# # update 1

# import os
# import tempfile
# from dotenv import load_dotenv

# # If you're using GridFS, this import must match your helper path
# # storage/gridfs_helper.py should define get_file(file_id)
# from storage.gridfs_helper import get_file

# # Load environment variables from .env
# load_dotenv()


# def get_env(key: str, default=None):
#     """
#     Fetch environment variables safely with a default fallback.
#     Example:
#         get_env("GOOGLE_API_KEY")
#     """
#     return os.getenv(key, default)


# def get_upload_path() -> str:
#     """
#     Returns the absolute path to the folder where uploaded PDF statements are stored.
#     Creates the directory if missing.
#     (Mainly useful if you're still supporting local file uploads.)
#     """
#     path = os.path.join(os.getcwd(), "uploads", "statements")
#     os.makedirs(path, exist_ok=True)
#     return path


# def list_uploaded_files() -> list:
#     """
#     Lists all uploaded PDF files in the uploads/statements directory.
#     """
#     path = get_upload_path()
#     return [f for f in os.listdir(path) if f.lower().endswith(".pdf")]


# def write_gridfs_to_temp(file_id: str) -> str:
#     """
#     Fetches a file from GridFS and writes it to a temporary file on disk.
#     Returns the path to the temp file.

#     IMPORTANT:
#         The caller is responsible for deleting the file when done, e.g.:

#             tmp_path = write_gridfs_to_temp(file_id)
#             ... use tmp_path ...
#             os.remove(tmp_path)
#     """
#     grid_out = get_file(file_id)          # get_file comes from storage/gridfs_helper.py
#     tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
#     tmp.write(grid_out.read())
#     tmp.flush()
#     tmp.close()
#     return tmp.name

# update 2

# services/utils.py
import os
from dotenv import load_dotenv
import tempfile
from storage.gridfs_helper import get_file
import traceback

# Load environment variables from .env
load_dotenv()

def get_env(key: str, default=None):
    return os.getenv(key, default)

def get_upload_path() -> str:
    path = os.path.join(os.getcwd(), "uploads", "statements")
    os.makedirs(path, exist_ok=True)
    return path

def list_uploaded_files() -> list:
    path = get_upload_path()
    return [f for f in os.listdir(path) if f.lower().endswith(".pdf")]

# -------------------------
# GridFS -> temp file helpers
# -------------------------
def write_gridfs_to_temp(file_id):
    """
    Reads a GridFS file (by file_id) and writes to a temp file.
    Returns the temp filepath. Caller must remove the file when done.
    """
    tmp_path = None
    try:
        grid_out = get_file(file_id)
        suffix = '.pdf'
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(grid_out.read())
        tmp.flush()
        tmp.close()
        tmp_path = tmp.name
        return tmp_path
    except Exception as e:
        print("Error writing gridfs file to temp:", str(e))
        print(traceback.format_exc())
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
        raise

def cleanup_temp_files(paths):
    """
    Remove a list of temp files (silently ignore missing).
    """
    for p in paths or []:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass
