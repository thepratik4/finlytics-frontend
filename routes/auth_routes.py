from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db, bcrypt 
from models.user_model import User
from flask import current_app


# Create a Flask Blueprint
auth_bp = Blueprint("auth_bp", __name__)

# --------------------------------------
# USER SIGNUP
# --------------------------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Registers a new user.
    Expects JSON: {"email": "user@example.com", "password": "yourpassword"}
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")


    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    

    # return jsonify({
    #     "message": "User created successfully"
    # })
    # Check if email already registered
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    # Hash the password securely
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    # Create and store user
    user = User(email=email, password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": user.to_dict()
    }), 201


# --------------------------------------
# USER LOGIN
# --------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user and returns a JWT token.
    Expects JSON: {"email": "user@example.com", "password": "yourpassword"}
    """
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create access token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200
