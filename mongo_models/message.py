# mongo_models/message.py
from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI
import datetime

client = MongoClient(MONGO_URI)
db = client.get_default_database()
messages_coll = db['messages']
messages_coll.create_index([('session_id', 1), ('created_at', 1)])

def create_message(session_id, user_id, role, text, metadata=None):
    doc = {'session_id': ObjectId(session_id), 'user_id': ObjectId(user_id), 'role': role, 'text': text, 'metadata': metadata or {}, 'created_at': datetime.datetime.utcnow()}
    res = messages_coll.insert_one(doc)
    return str(res.inserted_id)

def list_messages(session_id, limit=100):
    cur = messages_coll.find({'session_id': ObjectId(session_id)}).sort('created_at', 1).limit(limit)
    out = []
    for m in cur:
        m['_id'] = str(m['_id']); m['session_id'] = str(m['session_id']); m['user_id']=str(m['user_id'])
        out.append(m)
    return out

def delete_messages_for_session(session_id):
    res = messages_coll.delete_many({'session_id': ObjectId(session_id)})
    return res.deleted_count
