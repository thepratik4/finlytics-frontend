# storage/gridfs_helper.py
import os
from pymongo import MongoClient
import gridfs
from bson import ObjectId
from config import MONGO_URI

# Connect to MongoDB (Atlas SRV or local)
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client.get_default_database()  # uses DB name in URI, or default
fs = gridfs.GridFS(db, collection='pdfs')

def save_file(file_stream, filename, content_type):
    """Store file_stream (file-like) in GridFS. Returns str(file_id)."""
    data = file_stream.read()
    file_id = fs.put(data, filename=filename, contentType=content_type)
    return str(file_id)

def get_file(file_id):
    """Return GridOut for reading (.read())."""
    return fs.get(ObjectId(file_id))

def delete_file(file_id):
    try:
        fs.delete(ObjectId(file_id))
        return True
    except Exception:
        return False
