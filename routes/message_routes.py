# routes/message_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongo_models import session as session_model, message as message_model

bp = Blueprint('messages', __name__, url_prefix='/api/messages')

@bp.route('/<session_id>', methods=['GET'])
@jwt_required()
def list_messages(session_id):
    s = session_model.get_session(session_id)
    if not s: return jsonify({'message':'Not found'}), 404
    uid = get_jwt_identity()
    if s['user_id'] != uid: return jsonify({'message':'forbidden'}), 403
    msgs = message_model.list_messages(session_id)
    return jsonify({'messages': msgs})

@bp.route('/<session_id>', methods=['POST'])
@jwt_required()
def add_message(session_id):
    s = session_model.get_session(session_id)
    if not s: return jsonify({'message':'Not found'}), 404
    uid = get_jwt_identity()
    if s['user_id'] != uid: return jsonify({'message':'forbidden'}), 403
    data = request.json or {}
    role = data.get('role','user')
    text = data.get('text','')
    meta = data.get('metadata', {})
    mid = message_model.create_message(session_id, uid, role, text, metadata=meta)
    session_model.touch_session(session_id)
    return jsonify({'id': mid}), 201
