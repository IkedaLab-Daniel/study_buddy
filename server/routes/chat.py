from flask import Blueprint, request, jsonify
from services.rag_service import RAGService

chat_bp = Blueprint('chat', __name__)

def get_rag_service():
    if not hasattr(get_rag_service, '_service'):
        get_rag_service._service = RAGService()
    return get_rag_service._service

@chat_bp.route('/query', methods=['POST'])
def query():
    """
    Query the RAG system with a question
    """
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data['question']
        document_id = data.get('document_id', None)  # Optional: filter by specific document
        
        # Get response from RAG system
        response = get_rag_service().query(question, document_id)
        
        return jsonify({
            'answer': response['answer'],
            'sources': response['sources']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    """
    Generate a quiz based on the uploaded documents
    """
    try:
        data = request.get_json()
        
        topic = data.get('topic', '')
        num_questions = data.get('num_questions', 5)
        document_id = data.get('document_id', None)
        
        quiz = get_rag_service().generate_quiz(topic, num_questions, document_id)
        
        return jsonify({'quiz': quiz}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/summarize', methods=['POST'])
def summarize():
    """
    Summarize a specific document or topic
    """
    try:
        data = request.get_json()
        
        document_id = data.get('document_id')
        topic = data.get('topic', '')
        
        if not document_id and not topic:
            return jsonify({'error': 'Either document_id or topic is required'}), 400
        
        summary = get_rag_service().summarize(document_id, topic)
        
        return jsonify({'summary': summary}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
