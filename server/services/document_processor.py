import os
import uuid
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = os.getenv('CHROMA_PERSIST_DIR', 'data/chroma')
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def load_document(self, filepath: str) -> List:
        """
        Load a document based on its file extension
        """
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        if ext == '.pdf':
            loader = PyPDFLoader(filepath)
        elif ext == '.txt':
            loader = TextLoader(filepath)
        elif ext in ['.doc', '.docx']:
            loader = Docx2txtLoader(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        return loader.load()
    
    def process_and_store(self, filepath: str, filename: str) -> str:
        """
        Process a document and store it in the vector database
        """
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Load document
        documents = self.load_document(filepath)
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata['document_id'] = doc_id
            chunk.metadata['filename'] = filename
            chunk.metadata['source'] = filepath
        
        # Add to vector store
        self.vector_store.add_documents(chunks)
        
        # Clean up uploaded file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return doc_id
    
    def list_documents(self) -> List[dict]:
        """
        List all documents in the vector store
        """
        # Get all documents from the collection
        collection = self.vector_store._collection
        results = collection.get()
        
        # Extract unique documents
        documents = {}
        if results and 'metadatas' in results:
            for metadata in results['metadatas']:
                if metadata and 'document_id' in metadata:
                    doc_id = metadata['document_id']
                    if doc_id not in documents:
                        documents[doc_id] = {
                            'document_id': doc_id,
                            'filename': metadata.get('filename', 'Unknown')
                        }
        
        return list(documents.values())
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector store
        """
        try:
            collection = self.vector_store._collection
            results = collection.get(where={"document_id": document_id})
            
            if results and 'ids' in results and len(results['ids']) > 0:
                collection.delete(ids=results['ids'])
                return True
            return False
        except Exception:
            return False
    
    def get_retriever(self, document_id: str = None):
        """
        Get a retriever for searching documents
        """
        if document_id:
            # Filter by specific document
            return self.vector_store.as_retriever(
                search_kwargs={
                    'filter': {'document_id': document_id},
                    'k': 4
                }
            )
        else:
            # Search all documents
            return self.vector_store.as_retriever(search_kwargs={'k': 4})
