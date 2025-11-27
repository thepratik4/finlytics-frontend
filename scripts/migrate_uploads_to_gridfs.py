
# scripts/migrate_uploads_to_gridfs.py
import os
from storage.gridfs_helper import save_file
from mongo_models.pdf import add_pdf

UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads', 'statements')
DEFAULT_USER_ID = "<paste-a-user-id-or-ask>"   # set mapping logic
DEFAULT_SESSION_ID = "<paste-session-id>"

for fname in os.listdir(UPLOAD_DIR):
    path = os.path.join(UPLOAD_DIR, fname)
    if not os.path.isfile(path): continue
    with open(path, "rb") as fh:
        file_id = save_file(fh, fname, "application/pdf")
    size = os.path.getsize(path)
    add_pdf(DEFAULT_USER_ID, DEFAULT_SESSION_ID, fname, fname, file_id, size, "application/pdf")
    print("migrated", fname, "->", file_id)
