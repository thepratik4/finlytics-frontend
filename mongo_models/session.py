# mongo_models/session.py
from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI
import datetime

client = MongoClient(MONGO_URI)
db = client.get_default_database()
sessions_coll = db['sessions']
sessions_coll.create_index([('user_id', 1), ('updated_at', -1)])

def create_session(user_id, title='New Chat'):
    doc = {'user_id': ObjectId(user_id), 'title': title, 'created_at': datetime.datetime.utcnow(), 'updated_at': datetime.datetime.utcnow()}
    res = sessions_coll.insert_one(doc)
    return str(res.inserted_id)

def list_sessions(user_id):
    cur = sessions_coll.find({'user_id': ObjectId(user_id)}).sort('updated_at', -1)
    out = []
    for s in cur:
        s['_id'] = str(s['_id']); s['user_id'] = str(s['user_id'])
        out.append(s)
    return out

def get_session(session_id):
    s = sessions_coll.find_one({'_id': ObjectId(session_id)})
    if not s: return None
    s['_id'] = str(s['_id']); s['user_id'] = str(s['user_id'])
    return s

def delete_session(session_id):
    res = sessions_coll.delete_one({'_id': ObjectId(session_id)})
    return res.deleted_count == 1

def touch_session(session_id):
    sessions_coll.update_one({'_id': ObjectId(session_id)}, {'$set': {'updated_at': datetime.datetime.utcnow()}})
