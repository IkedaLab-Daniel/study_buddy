import os
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from services.document_processor import DocumentProcessor
from dotenv import load_dotenv

load_dotenv()

class RAGService:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.llm = ChatOpenAI(
            model=os.getenv('LLM_MODEL', 'gpt-4-turbo-preview'),
            temperature=float(os.getenv('TEMPERATURE', 0.7)),
            max_tokens=int(os.getenv('MAX_TOKENS', 1000))
        )
        
        # QA prompt template
        self.qa_template = """You are a helpful study assistant. Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Answer: """
        
        self.qa_prompt = PromptTemplate(
            template=self.qa_template,
            input_variables=["context", "question"]
        )
    
    def query(self, question: str, document_id: str = None) -> Dict:
        """
        Query the RAG system with a question
        """
        # Get retriever
        retriever = self.document_processor.get_retriever(document_id)
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.qa_prompt}
        )
        
        # Get response
        result = qa_chain({"query": question})
        
        # Format sources
        sources = []
        for doc in result['source_documents']:
            sources.append({
                'filename': doc.metadata.get('filename', 'Unknown'),
                'content': doc.page_content[:200] + '...'  # Preview
            })
        
        return {
            'answer': result['result'],
            'sources': sources
        }
    
    def generate_quiz(self, topic: str, num_questions: int = 5, document_id: str = None) -> List[Dict]:
        """
        Generate a quiz based on the uploaded documents
        """
        retriever = self.document_processor.get_retriever(document_id)
        
        # Get relevant context
        if topic:
            docs = retriever.get_relevant_documents(topic)
        else:
            docs = retriever.get_relevant_documents("main concepts and key information")
        
        context = "\n\n".join([doc.page_content for doc in docs[:3]])
        
        quiz_prompt = f"""Based on the following study material, generate {num_questions} multiple-choice questions.
Each question should have 4 options (A, B, C, D) with only one correct answer.
Format the output as a JSON array of objects with 'question', 'options' (array), and 'correct_answer' (letter) fields.

Study Material:
{context}

Generate the quiz:"""
        
        response = self.llm.invoke(quiz_prompt)
        
        # Parse and return quiz (you might want to add proper JSON parsing)
        return {
            'quiz': response.content,
            'topic': topic or 'General'
        }
    
    def summarize(self, document_id: str = None, topic: str = '') -> str:
        """
        Summarize documents or a specific topic
        """
        retriever = self.document_processor.get_retriever(document_id)
        
        # Get relevant documents
        query = topic if topic else "summarize the main points and key concepts"
        docs = retriever.get_relevant_documents(query)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        
        summary_prompt = f"""Provide a comprehensive summary of the following study material.
Highlight the main points, key concepts, and important details.

Study Material:
{context}

Summary:"""
        
        response = self.llm.invoke(summary_prompt)
        
        return response.content
