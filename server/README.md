# Study Buddy Server

Flask-based backend for the Study Buddy application with RAG (Retrieval-Augmented Generation) capabilities.

## Features

- 📄 PDF and text document upload
- 🔍 RAG-powered question answering
- 📚 Document summarization
- 📝 Quiz generation
- 🗄️ Vector database storage with ChromaDB
- 🤖 OpenAI GPT integration

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if the API is running

### Documents
- `POST /api/documents/upload` - Upload a document (PDF/TXT/DOC/DOCX)
- `GET /api/documents/` - List all uploaded documents
- `DELETE /api/documents/<document_id>` - Delete a document

### Chat & Query
- `POST /api/chat/query` - Ask a question about your documents
  ```json
  {
    "question": "What is the main topic?",
    "document_id": "optional-document-id"
  }
  ```

- `POST /api/chat/summarize` - Get a summary
  ```json
  {
    "document_id": "optional-document-id",
    "topic": "optional-topic"
  }
  ```

- `POST /api/chat/generate-quiz` - Generate a quiz
  ```json
  {
    "topic": "optional-topic",
    "num_questions": 5,
    "document_id": "optional-document-id"
  }
  ```

## Project Structure

```
server/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── routes/               # API route handlers
│   ├── documents.py      # Document upload/management
│   └── chat.py          # RAG query endpoints
├── services/            # Business logic
│   ├── document_processor.py  # Document processing & vector storage
│   └── rag_service.py        # RAG implementation
├── utils/              # Utility functions
│   └── validators.py   # File validation helpers
├── uploads/           # Temporary file uploads (gitignored)
└── data/             # Vector database storage (gitignored)
    └── chroma/
```

## Technologies

- **Flask** - Web framework
- **LangChain** - RAG orchestration
- **ChromaDB** - Vector database
- **OpenAI** - LLM and embeddings
- **PyPDF** - PDF processing
