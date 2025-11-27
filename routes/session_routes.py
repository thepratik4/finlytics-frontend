# routes/session_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongo_models import session as session_model, message as message_model, pdf as pdf_model
from storage import gridfs_helper

bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')

@bp.route('', methods=['POST'])
@jwt_required()
def create_session():
    uid = get_jwt_identity()
    title = (request.json or {}).get('title') or 'New Chat'
    sid = session_model.create_session(uid, title)
    return jsonify({'id': sid, 'title': title}), 201

@bp.route('', methods=['GET'])
@jwt_required()
def list_sessions():
    uid = get_jwt_identity()
    sessions = session_model.list_sessions(uid)
    return jsonify({'sessions': sessions})

@bp.route('/<session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    s = session_model.get_session(session_id)
    if not s: return jsonify({'message':'Not found'}), 404
    return jsonify({'session': s})

@bp.route('/<session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    s = session_model.get_session(session_id)
    uid = get_jwt_identity()
    if not s or s['user_id'] != uid:
        return jsonify({'message':'Not found or forbidden'}), 404
    # delete messages
    message_model.delete_messages_for_session(session_id)
    # delete pdf metadata and collect gridfs file_ids
    file_ids = pdf_model.delete_pdfs_for_session(session_id)
    # delete files from GridFS
    for fid in file_ids:
        try:
            gridfs_helper.delete_file(fid)
        except:
            pass
    # delete session record
    session_model.delete_session(session_id)
    return jsonify({'deleted': True}), 200
