# mongo_models/user.py
from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI
import bcrypt, datetime

client = MongoClient(MONGO_URI)
db = client.get_default_database()
users_coll = db['users']
users_coll.create_index('email', unique=True)

def create_user(name, email, password_plain):
    if users_coll.find_one({'email': email.lower()}):
        raise ValueError("Email already exists")
    pw_hash = bcrypt.hashpw(password_plain.encode('utf8'), bcrypt.gensalt())
    res = users_coll.insert_one({
        'name': name,
        'email': email.lower(),
        'password_hash': pw_hash,
        'created_at': datetime.datetime.utcnow()
    })
    return str(res.inserted_id)

def find_by_email(email):
    return users_coll.find_one({'email': email.lower()})

def find_by_id(user_id):
    return users_coll.find_one({'_id': ObjectId(user_id)})
