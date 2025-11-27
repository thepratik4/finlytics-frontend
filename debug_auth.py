from pymongo import MongoClient
from config import MONGO_URI
import bcrypt

client = MongoClient(MONGO_URI)
db = client.get_default_database()
users = db['users']

print("--- Users ---")
for u in users.find():
    print(f"Email: {u.get('email')}")
    print(f"Hash Type: {type(u.get('password_hash'))}")
    print(f"Hash: {u.get('password_hash')}")
    
    # Try to verify a test password if you know it, or just check format
    # print(bcrypt.checkpw(b"test", u['password_hash']))
