from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from services.document_processor import DocumentProcessor
from utils.validators import allowed_file

documents_bp = Blueprint('documents', __name__)

def get_processor():
    if not hasattr(get_processor, '_processor'):
        get_processor._processor = DocumentProcessor()
    return get_processor._processor

@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Upload and process a document (PDF/TXT)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            return jsonify({'error': 'File type not allowed. Only PDF, TXT, DOC, DOCX are supported'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process document and add to vector store
        doc_id = get_processor().process_and_store(filepath, filename)
        
        return jsonify({
            'message': 'Document uploaded and processed successfully',
            'document_id': doc_id,
            'filename': filename
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/', methods=['GET'])
def list_documents():
    """
    List all processed documents
    """
    try:
        documents = get_processor().list_documents()
        return jsonify({'documents': documents}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@documents_bp.route('/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Delete a document from the vector store
    """
    try:
        success = get_processor().delete_document(document_id)
        if success:
            return jsonify({'message': 'Document deleted successfully'}), 200
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
