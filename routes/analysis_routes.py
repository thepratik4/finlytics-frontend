import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from services.ai_service import analyze_pdfs, ask_question

# Create blueprint
analysis_bp = Blueprint("analysis_bp", __name__)

# ---------------------------------------------------------
# Upload PDF documents
# ---------------------------------------------------------
@analysis_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_files():
    """
    Upload one or more PDF documents.
    Expects form-data: files[] (multiple allowed)
    Returns: list of saved filenames
    """
    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    upload_dir = current_app.config["UPLOAD_FOLDER"]
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


# ---------------------------------------------------------
# Analyze PDF documents
# ---------------------------------------------------------
@analysis_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze_documents():
    """
    Run AI-powered analysis on uploaded PDFs.
    Expects JSON: {"filenames": ["file1.pdf", "file2.pdf"]}
    Returns structured analysis for each file.
    """
    data = request.get_json() or {}
    filenames = data.get("filenames")

    if not filenames or not isinstance(filenames, list):
        return jsonify({"error": "Missing or invalid 'filenames' list"}), 400

    try:
        analysis_results = analyze_pdfs(filenames)
        return jsonify({"analysis": analysis_results}), 200
    except Exception as e:
        return jsonify({"error 1": str(e)}), 500


# ---------------------------------------------------------
# Ask follow-up financial question
# ---------------------------------------------------------
@analysis_bp.route("/ask", methods=["POST"])
@jwt_required()
def ask_about_documents():
    """
    Ask an AI financial question across uploaded PDFs.
    Expects JSON: {"question": "Your question here", "filenames": ["file1.pdf", ...]}
    Returns structured multi-PDF response.
    """
    data = request.get_json() or {}
    question = data.get("question")
    filenames = data.get("filenames", [])

    if not question:
        return jsonify({"error": "Missing 'question'"}), 400

    try:
        response = ask_question(question, filenames)
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
