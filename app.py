# import os
# from datetime import timedelta
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from dotenv import load_dotenv
# from extensions import db, bcrypt, jwt

# # Load environment variables from .env (if present)
# load_dotenv()

# # -----------------------------
# # App factory
# # -----------------------------
# def create_app():
#     """
#     Create and configure the Flask application.
#     - Initializes DB, Bcrypt, JWT
#     - Registers blueprints from routes/
#     - Ensures upload and instance folders exist
#     """
#     app = Flask(__name__, instance_relative_config=True)
#     CORS(app)
    

#     # Basic configuration (can be overridden by .env or instance config)
#     app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecret")
#     # JWT config
#     app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])
#     # Example: tokens expire after 1 day by default (adjust as needed)
#     app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=int(os.getenv("JWT_EXP_DAYS", "1")))

#     # Prepare instance path (where sqlite DB will be stored)
#     try:
#         os.makedirs(app.instance_path, exist_ok=True)
#     except Exception:
#         # In some environments instance_path creation might fail; ignore safely
#         pass

#     # SQLite DB path stored inside instance folder
#     db_path = os.path.join(app.instance_path, "users.db")
#     app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#     print("INSTANCE PATH:", app.instance_path)
#     print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])

#     # Upload folder for PDFs
#     upload_folder = os.path.join(os.getcwd(), "uploads", "statements")
#     os.makedirs(upload_folder, exist_ok=True)
#     app.config["UPLOAD_FOLDER"] = upload_folder

#     # Initialize extensions with app
#     db.init_app(app)
#     bcrypt.init_app(app)
#     jwt.init_app(app)

#     # Import models BEFORE creating tables (IMPORTANT!)
#     from models.user_model import User
    
#     # Create tables
#     with app.app_context():
#         db.create_all()
#         print("✅ Database tables created successfully!")

#     # Register blueprints (import inside factory to avoid circular imports)
#     from routes.auth_routes import auth_bp
#     from routes.analysis_routes import analysis_bp

#     app.register_blueprint(auth_bp, url_prefix="/auth")
#     app.register_blueprint(analysis_bp, url_prefix="/analysis")
    

#     return app


# # Allow running with `python app.py`
# if __name__ == "__main__":
#     # Use environment variable to toggle debug mode
#     debug_mode = os.getenv("FLASK_DEBUG", "1") == "1"
#     app = create_app()
#     # Bind to 0.0.0.0 for container friendliness; change to 127.0.0.1 if needed
#     app.run(host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
#             port=int(os.getenv("FLASK_RUN_PORT", "5000")),
#             debug=debug_mode)

# #1 update
# # app.py
# import os
# from datetime import timedelta
# from flask import Flask
# from flask_cors import CORS
# from dotenv import load_dotenv
# from extensions import db, bcrypt, jwt
# import config

# # Load .env
# load_dotenv()

# def create_app():
#     app = Flask(__name__, instance_relative_config=True)
#     CORS(app)

#     # Config
#     app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecret")
#     app.config["JWT_SECRET_KEY"] = config.JWT_SECRET
#     app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=int(config.JWT_ACCESS_EXPIRES))
#     app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024

#     # Instance path & upload folder
#     try:
#         os.makedirs(app.instance_path, exist_ok=True)
#     except Exception:
#         pass

#     # Keep SQLite for now (legacy) but not used for auth
#     db_path = os.path.join(app.instance_path, "users.db")
#     app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#     # Upload folder for legacy local storage (we will migrate)
#     upload_folder = os.path.join(os.getcwd(), "uploads", "statements")
#     os.makedirs(upload_folder, exist_ok=True)
#     app.config["UPLOAD_FOLDER"] = upload_folder

#     # Init extensions
#     db.init_app(app)
#     bcrypt.init_app(app)
#     jwt.init_app(app)

#     # Import models and create tables (legacy)
#     from models.user_model import User
#     with app.app_context():
#         db.create_all()

#     # Register blueprints
#     from routes.auth_routes import auth_bp
#     from routes.session_routes import bp as sessions_bp
#     from routes.message_routes import bp as messages_bp
#     from routes.pdf_routes import bp as pdf_bp
#     from routes.analysis_routes import analysis_bp  # keep for AI logic, but we will adapt it

#     app.register_blueprint(auth_bp)
#     app.register_blueprint(sessions_bp)
#     app.register_blueprint(messages_bp)
#     app.register_blueprint(pdf_bp)
#     # keep analysis blueprint under same prefix
#     app.register_blueprint(analysis_bp, url_prefix='/analysis')

#     @app.route('/')
#     def health():
#         return {'status': 'ok'}

#     return app

# if __name__ == "__main__":
#     debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
#     app = create_app()
#     app.run(host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
#             port=int(os.getenv("FLASK_RUN_PORT", "5000")),
#             debug=debug_mode)

#2 update
# app.py
import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import bcrypt, jwt   # ✅ removed db import
import config

# Load .env
load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    # Basic config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecret")
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=int(config.JWT_ACCESS_EXPIRES))
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_MB * 1024 * 1024

    # Instance path (still safe to keep, even without SQLite)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        pass

    # Upload folder for legacy local storage (even if you move to GridFS)
    upload_folder = os.path.join(os.getcwd(), "uploads", "statements")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = upload_folder

    # Init extensions (bcrypt + JWT only)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # ⛔️ REMOVED: SQLAlchemy db + User model + db.create_all()
    # from models.user_model import User
    # with app.app_context():
    #     db.create_all()

    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.session_routes import bp as sessions_bp
    from routes.message_routes import bp as messages_bp
    from routes.pdf_routes import bp as pdf_bp
    from routes.analysis_routes import analysis_bp  # AI logic

    app.register_blueprint(auth_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(analysis_bp, url_prefix='/analysis')

    @app.route('/')
    def health():
        return {'status': 'ok'}

    return app

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app = create_app()
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000")),
        debug=debug_mode
    )
