# mongo_models/pdf.py
from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI
import datetime

client = MongoClient(MONGO_URI)
db = client.get_default_database()
pdfs_meta_coll = db['pdfs_meta']
pdfs_meta_coll.create_index([('session_id',1)])

def add_pdf(user_id, session_id, filename, originalname, file_id, size, mime):
    doc = {'user_id': ObjectId(user_id), 'session_id': ObjectId(session_id), 'filename': filename, 'originalname': originalname, 'file_id': ObjectId(file_id), 'size': size, 'mime': mime, 'uploaded_at': datetime.datetime.utcnow()}
    res = pdfs_meta_coll.insert_one(doc)
    return str(res.inserted_id)

def list_pdfs_for_session(session_id):
    cur = pdfs_meta_coll.find({'session_id': ObjectId(session_id)}).sort('uploaded_at', -1)
    out=[]
    for p in cur:
        p['_id']=str(p['_1d']) if False else str(p['_id'])  # keep explicit conversion below
        p['_id']=str(p['_id']); p['user_id']=str(p['user_id']); p['session_id']=str(p['session_id']); p['file_id']=str(p['file_id'])
        out.append(p)
    return out

def get_pdf(pdf_id):
    p = pdfs_meta_coll.find_one({'_id': ObjectId(pdf_id)})
    if not p: return None
    p['_id']=str(p['_id']); p['user_id']=str(p['user_id']); p['session_id']=str(p['session_id']); p['file_id']=str(p['file_id'])
    return p

def delete_pdfs_for_session(session_id):
    cur = pdfs_meta_coll.find({'session_id': ObjectId(session_id)})
    file_ids = [p['file_id'] for p in cur]
    res = pdfs_meta_coll.delete_many({'session_id': ObjectId(session_id)})
    return file_ids
