# update 1
# routes/pdf_routes.py
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from storage import gridfs_helper
from mongo_models import session as session_model, pdf as pdf_model
import io

bp = Blueprint('pdfs', __name__, url_prefix='/api/pdfs')

ALLOWED = {'application/pdf'}

@bp.route('/upload/<session_id>', methods=['POST'])
@jwt_required()
def upload_pdf(session_id):
    s = session_model.get_session(session_id)
    if not s: return jsonify({'message':'session not found'}), 404
    uid = get_jwt_identity()
    if s['user_id'] != uid: return jsonify({'message':'forbidden'}), 403
    if 'file' not in request.files: return jsonify({'message':'no file'}), 400
    file = request.files['file']
    if file.mimetype not in ALLOWED:
        return jsonify({'message':'only pdf allowed'}), 400
    filename = secure_filename(file.filename)
    file_id = gridfs_helper.save_file(file.stream, filename, file.mimetype)
    pdf_id = pdf_model.add_pdf(uid, session_id, filename, filename, file_id, file.content_length or 0, file.mimetype)
    return jsonify({'pdf_id': pdf_id}), 201

@bp.route('/session/<session_id>', methods=['GET'])
@jwt_required()
def list_pdfs(session_id):
    s = session_model.get_session(session_id)
    if not s: return jsonify({'message':'session not found'}), 404
    uid = get_jwt_identity()
    if s['user_id'] != uid: return jsonify({'message':'forbidden'}), 403
    pdfs = pdf_model.list_pdfs_for_session(session_id)
    return jsonify({'pdfs': pdfs})

@bp.route('/download/<pdf_id>', methods=['GET'])
@jwt_required()
def download_pdf(pdf_id):
    pdf = pdf_model.get_pdf(pdf_id)
    if not pdf: return jsonify({'message':'not found'}), 404
    uid = get_jwt_identity()
    if pdf['user_id'] != uid: return jsonify({'message':'forbidden'}), 403
    grid_out = gridfs_helper.get_file(pdf['file_id'])
    return send_file(io.BytesIO(grid_out.read()), download_name=pdf['originalname'], mimetype=pdf['mime'], as_attachment=True)

@bp.route('/<pdf_id>', methods=['DELETE'])
@jwt_required()
def delete_pdf(pdf_id):
    pdf = pdf_model.get_pdf(pdf_id)
    if not pdf: return jsonify({'message':'not found'}), 404
    uid = get_jwt_identity()
    if pdf['user_id'] != uid: return jsonify({'message':'forbidden'}), 403
    gridfs_helper.delete_file(pdf['file_id'])
    from bson import ObjectId
    pdf_model.pdfs_meta_coll.delete_one({'_id': ObjectId(pdf_id)})
    return jsonify({'deleted': True}), 200
