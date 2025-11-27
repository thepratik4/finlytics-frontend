# # routes/auth_routes_sqlalchemy_backup.py

# from flask import Blueprint, request, jsonify, current_app
# from flask_jwt_extended import create_access_token
# from extensions import db, bcrypt
# from models.user_model import User

# # Create a Flask Blueprint
# auth_bp = Blueprint("auth_bp", __name__)

# # --------------------------------------
# # USER SIGNUP
# # --------------------------------------
# @auth_bp.route("/signup", methods=["POST"])
# def signup():
#     """
#     Registers a new user.
#     Expects JSON: {"email": "user@example.com", "password": "yourpassword"}
#     """
#     data = request.get_json() or {}

#     email = data.get("email")
#     password = data.get("password")

#     if not email or not password:
#         return jsonify({"error": "Email and password required"}), 400

#     # Check if email already registered
#     existing_user = User.query.filter_by(email=email).first()
#     if existing_user:
#         return jsonify({"error": "Email already exists"}), 400

#     # Hash the password securely
#     hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

#     # Create and store user
#     user = User(email=email, password=hashed_pw)
#     db.session.add(user)
#     db.session.commit()

#     return jsonify({
#         "message": "User created successfully",
#         "user": user.to_dict()
#     }), 201


# # --------------------------------------
# # USER LOGIN
# # --------------------------------------
# @auth_bp.route("/login", methods=["POST"])
# def login():
#     """
#     Authenticates a user and returns a JWT token.
#     Expects JSON: {"email": "user@example.com", "password": "yourpassword"}
#     """
#     data = request.get_json() or {}

#     email = data.get("email")
#     password = data.get("password")

#     if not email or not password:
#         return jsonify({"error": "Email and password required"}), 400

#     user = User.query.filter_by(email=email).first()
#     if not user or not bcrypt.check_password_hash(user.password, password):
#         return jsonify({"error": "Invalid email or password"}), 401

#     # Create access token
#     access_token = create_access_token(identity=str(user.id))

#     return jsonify({
#         "message": "Login successful",
#         "access_token": access_token,
#         "user": user.to_dict()
#     }), 200


# routes/auth_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from mongo_models import user as user_model

auth_bp = Blueprint("auth_bp", __name__, url_prefix='/api/auth')

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    print(f"DEBUG: Signup attempt for {data.get('email')}")
    email = data.get("email")
    password = data.get("password")
    name = data.get("name") or ""
    if not email or not password: return jsonify({"error": "Email and password required"}), 400
    try:
        user_id = user_model.create_user(name, email, password)
        print(f"DEBUG: User created {user_id}")
        access_token = create_access_token(identity=str(user_id))
        return jsonify({"message":"User created", "user": {"id": user_id, "email": email, "name": name}, "token": access_token}), 201
    except ValueError as e:
        print(f"DEBUG: Signup error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"DEBUG: Signup exception: {e}")
        return jsonify({"error":"Server error"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    print(f"DEBUG: Login attempt for {data.get('email')}")
    email = data.get("email")
    password = data.get("password")
    if not email or not password: return jsonify({"error":"Email and password required"}), 400
    user = user_model.find_by_email(email)
    if not user:
        print("DEBUG: User not found")
        return jsonify({"error":"Invalid credentials"}), 401
    import bcrypt
    print(f"DEBUG: User found, checking password. Hash type: {type(user['password_hash'])}")
    try:
        if not bcrypt.checkpw(password.encode('utf8'), user['password_hash']):
            print("DEBUG: Password check failed")
            return jsonify({"error":"Invalid credentials"}), 401
    except Exception as e:
        print(f"DEBUG: Password check error: {e}")
        return jsonify({"error":"Invalid credentials"}), 401
        
    print("DEBUG: Login successful")
    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({"message":"Login successful","token":access_token,"user":{"id":str(user['_id']),"email":user['email']}}), 200
