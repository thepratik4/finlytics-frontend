# # extensions.py
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# jwt = JWTManager()

# #1 update
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# jwt = JWTManager()

#2 update
# extensions.py

from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# We no longer use SQLAlchemy here – MongoDB is handled via pymongo in mongo_models
bcrypt = Bcrypt()
jwt = JWTManager()
