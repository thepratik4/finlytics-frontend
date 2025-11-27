# routes/message_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongo_models import session as session_model, message as message_model, pdf as pdf_model
from services.ai_service import ask_question
import json

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
    
    # 1. Save User Message
    user_mid = message_model.create_message(session_id, uid, role, text, metadata=meta)
    session_model.touch_session(session_id)
    
    # 2. Trigger AI Response (if user message)
    ai_mid = None
    if role == 'user':
        # Fetch PDFs for this session
        pdfs = pdf_model.list_pdfs_for_session(session_id)
        if pdfs:
            # Prepare input for AI (list of dicts with file_id and filename)
            inputs = [{'file_id': p['file_id'], 'filename': p['originalname']} for p in pdfs]
            
            try:
                ai_response_json_str = ask_question(text, inputs)
                
                # Try to parse it to ensure it's valid JSON, though ask_question returns string
                try:
                    ai_data = json.loads(ai_response_json_str)
                    # We can store the raw JSON string in text, or a summary. 
                    # Let's store the JSON string in 'text' and the parsed object in 'metadata' for future proofing
                    # Or better: Store a user-friendly summary in 'text' and full data in 'metadata'
                    # For now, to keep frontend simple, we'll store the JSON string in 'text' 
                    # and let frontend parse it.
                    ai_text = ai_response_json_str
                    ai_meta = {'is_structured': True, 'data': ai_data}
                except json.JSONDecodeError:
                    # Fallback if not valid JSON
                    ai_text = ai_response_json_str
                    ai_meta = {'is_structured': False}

                # Save AI Message
                ai_mid = message_model.create_message(session_id, uid, 'ai', ai_text, metadata=ai_meta)
            except Exception as e:
                print(f"Error generating AI response: {e}")
                # Optionally save an error message or just pass
                # ai_mid = message_model.create_message(session_id, uid, 'ai', "Sorry, I encountered an error analyzing the documents.")

    return jsonify({'id': user_mid, 'ai_message_id': ai_mid}), 201
