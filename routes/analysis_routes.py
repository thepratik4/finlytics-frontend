# # update 1
# import os
# from flask import Blueprint, request, jsonify, current_app
# from flask_jwt_extended import jwt_required
# from services.ai_service import analyze_pdfs, ask_question

# # Create blueprint
# analysis_bp = Blueprint("analysis_bp", __name__)

# # ---------------------------------------------------------
# # Upload PDF documents
# # ---------------------------------------------------------
# @analysis_bp.route("/upload", methods=["POST"])
# @jwt_required()
# def upload_files():
#     """
#     Upload one or more PDF documents.
#     Expects form-data: files[] (multiple allowed)
#     Returns: list of saved filenames
#     """
#     if "files" not in request.files:
#         return jsonify({"error": "No files uploaded"}), 400

#     files = request.files.getlist("files")
#     upload_dir = current_app.config["UPLOAD_FOLDER"]
#     os.makedirs(upload_dir, exist_ok=True)

#     saved_files = []
#     for file in files:
#         if not file.filename.lower().endswith(".pdf"):
#             return jsonify({"error": f"File {file.filename} is not a PDF"}), 400

#         filepath = os.path.join(upload_dir, file.filename)
#         file.save(filepath)
#         saved_files.append(file.filename)

#     return jsonify({
#         "message": f"Uploaded {len(saved_files)} file(s) successfully",
#         "files": saved_files
#     }), 201


# # ---------------------------------------------------------
# # Analyze PDF documents
# # ---------------------------------------------------------
# @analysis_bp.route("/analyze", methods=["POST"])
# @jwt_required()
# def analyze_documents():
#     """
#     Run AI-powered analysis on uploaded PDFs.
#     Expects JSON: {"filenames": ["file1.pdf", "file2.pdf"]}
#     Returns structured analysis for each file.
#     """
#     data = request.get_json() or {}
#     filenames = data.get("filenames")

#     if not filenames or not isinstance(filenames, list):
#         return jsonify({"error": "Missing or invalid 'filenames' list"}), 400

#     try:
#         analysis_results = analyze_pdfs(filenames)
#         return jsonify({"analysis": analysis_results}), 200
#     except Exception as e:
#         return jsonify({"error 1": str(e)}), 500


# # ---------------------------------------------------------
# # Ask follow-up financial question
# # ---------------------------------------------------------
# @analysis_bp.route("/ask", methods=["POST"])
# @jwt_required()
# def ask_about_documents():
#     """
#     Ask an AI financial question across uploaded PDFs.
#     Expects JSON: {"question": "Your question here", "filenames": ["file1.pdf", ...]}
#     Returns structured multi-PDF response.
#     """
#     data = request.get_json() or {}
#     question = data.get("question")
#     filenames = data.get("filenames", [])

#     if not question:
#         return jsonify({"error": "Missing 'question'"}), 400

#     try:
#         response = ask_question(question, filenames)
#         return jsonify({"response": response}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# update 2
# routes/analysis_routes.py
import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.ai_service import analyze_pdfs, ask_question
from services.utils import get_upload_path, write_gridfs_to_temp, cleanup_temp_files
from mongo_models import pdf as pdf_model

analysis_bp = Blueprint("analysis_bp", __name__)

# Legacy upload kept (saves locally)
@analysis_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_files():
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    upload_dir = current_app.config.get("UPLOAD_FOLDER") or get_upload_path()
    os.makedirs(upload_dir, exist_ok=True)

    saved_files = []
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": f"File {file.filename} is not a PDF"}), 400

        filepath = os.path.join(upload_dir, file.filename)
        file.save(filepath)
        saved_files.append(file.filename)

    return jsonify({
        "message": f"Uploaded {len(saved_files)} file(s) successfully",
        "files": saved_files
    }), 201


# Analyze PDFs: expects pdf_meta_ids (preferred) or filenames (legacy)
@analysis_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze_documents():
    data = request.get_json() or {}
    pdf_meta_ids = data.get("pdf_meta_ids")         # list of pdf metadata ids (strings)
    filenames = data.get("filenames")               # legacy local filenames
    session_id = data.get("session_id")             # optional: can be used to fetch pdfs for session
    user_id = get_jwt_identity()

    # Build a list of inputs for ai_service.analyze_pdfs
    temp_paths = []
    inputs_for_ai = []

    try:
        if pdf_meta_ids:
            for pmid in pdf_meta_ids:
                meta = pdf_model.get_pdf(pmid)
                if not meta:
                    return jsonify({"error": f"PDF metadata {pmid} not found"}), 404
                # meta contains file_id (gridfs id)
                inputs_for_ai.append({"file_id": meta["file_id"]})
        elif session_id:
            # optional helper: load all pdfs for session
            pdfs = pdf_model.list_pdfs_for_session(session_id)
            if not pdfs:
                return jsonify({"error":"No PDFs found for session"}), 404
            for p in pdfs:
                inputs_for_ai.append({"file_id": p["file_id"]})
        elif filenames:
            for fn in filenames:
                inputs_for_ai.append(fn)
        else:
            return jsonify({"error":"No pdf_meta_ids, session_id or filenames provided"}), 400

        # Call ai service
        results = analyze_pdfs(inputs_for_ai)
        return jsonify({"analysis": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cleanup_temp_files(temp_paths)


# Ask question across PDFs (same input options)
@analysis_bp.route("/ask", methods=["POST"])
@jwt_required()
def ask_about_documents():
    data = request.get_json() or {}
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    pdf_meta_ids = data.get("pdf_meta_ids")
    filenames = data.get("filenames")
    session_id = data.get("session_id")
    inputs_for_ai = []

    try:
        if pdf_meta_ids:
            for pmid in pdf_meta_ids:
                meta = pdf_model.get_pdf(pmid)
                if not meta:
                    return jsonify({"error": f"PDF metadata {pmid} not found"}), 404
                inputs_for_ai.append({"file_id": meta["file_id"]})
        elif session_id:
            pdfs = pdf_model.list_pdfs_for_session(session_id)
            if not pdfs:
                return jsonify({"error":"No PDFs found for session"}), 404
            for p in pdfs:
                inputs_for_ai.append({"file_id": p["file_id"]})
        elif filenames:
            for fn in filenames:
                inputs_for_ai.append(fn)
        else:
            # default: ask across cached indexes (legacy)
            inputs_for_ai = None

        response = ask_question(question, inputs_for_ai)
        return jsonify({"response": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
