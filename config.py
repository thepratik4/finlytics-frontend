# config.py
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/finlytics")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))
JWT_ACCESS_EXPIRES = int(os.getenv("JWT_ACCESS_EXPIRES_SEC", 7*24*3600))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 30))
