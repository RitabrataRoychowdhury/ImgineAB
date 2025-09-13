"""Q&A Engine for document question answering using processed document context."""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
import requests
from datetime import datetime

from src.models.document import Document, QASession
from src.storage.document_storage import DocumentStorage
from src.utils.logging_config import get_logger
from src.utils.error_handling import QAError, APIError, handle_errors

logger = get_logger(__name__)


class QAEngine:
    """Q&A Engine that uses processed document context for question answering."""
    
    def __init__(self, storage: DocumentStorage, api_key: str):
        self.storage = storage
        self.api_key = api_key
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    def answer_question(self, question: str, document_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Answer a question about a specific document.
        
        Args:
            question: The user's question
            document_id: ID of the document to query
            session_id: Optional session ID for conversation tracking
            
        Returns:
            Dictionary containing answer, sources, and metadata
        """
        try:
            # Get the document
            document = self.storage.get_document_with_embeddings(document_id)
            if not document:
                return {
                    'answer': "Sorry, I couldn't find that document or it hasn't been processed yet.",
                    'sources': [],
                    'confidence': 0.0,
                    'error': 'Document not found or not processed'
                }
            
            # Get relevant context from the document
            context_sections = self.get_relevant_context(question, document)
            
            if not context_sections:
                return {
                    'answer': "I couldn't find relevant information in the document to answer your question.",
                    'sources': [],
                    'confidence': 0.2,
                    'error': 'No relevant context found'
                }
            
            # Generate answer using Gemini
            answer = self.generate_answer(question, context_sections, document)
            
            # Extract source references
            sources = self._extract_sources(context_sections)
            
            # Store the Q&A interaction
            if session_id:
                self.storage.add_qa_interaction(session_id, question, answer, sources)
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': 0.8,  # Could be improved with actual confidence scoring
                'document_title': document.title,
                'document_type': document.document_type
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                'answer': "I'm sorry, I encountered an error while processing your question. Please try again.",
                'sources': [],
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_relevant_context(self, question: str, document: Document) -> List[Dict[str, Any]]:
        """
        Find relevant document sections for the question.
        
        Args:
            question: The user's question
            document: The document to search
            
        Returns:
            List of relevant context sections with metadata
        """
        context_sections = []
        
        # Extract key terms from the question
        question_terms = self._extract_key_terms(question.lower())
        
        # Search in different parts of the document
        sections_to_search = [
            ('original_text', document.original_text, 'Document Content'),
            ('extracted_info', json.dumps(document.extracted_info or {}, indent=2), 'Extracted Information'),
            ('analysis', document.analysis, 'Analysis'),
            ('summary', document.summary, 'Summary')
        ]
        
        for section_name, content, display_name in sections_to_search:
            if not content:
                continue
                
            # Find relevant passages
            relevant_passages = self._find_relevant_passages(question_terms, content, display_name)
            context_sections.extend(relevant_passages)
        
        # Sort by relevance score and return top sections
        context_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        return context_sections[:5]  # Return top 5 most relevant sections
    
    def generate_answer(self, question: str, context_sections: List[Dict[str, Any]], document: Document) -> str:
        """
        Generate an answer using Gemini API with the provided context.
        
        Args:
            question: The user's question
            context_sections: Relevant context from the document
            document: The source document
            
        Returns:
            Generated answer string
        """
        # Prepare context for the prompt
        context_text = "\n\n".join([
            f"**{section['source']}:**\n{section['text']}"
            for section in context_sections
        ])
        
        prompt = f"""
        You are a helpful assistant that answers questions about documents. Use only the provided context to answer the question. If the context doesn't contain enough information to answer the question, say so clearly.

        Document Title: {document.title}
        Document Type: {document.document_type or 'Unknown'}

        Context from the document:
        {context_text}

        Question: {question}

        Instructions:
        1. Answer based only on the provided context
        2. Be specific and cite relevant parts of the context
        3. If the context doesn't contain the answer, say "The document doesn't contain enough information to answer this question"
        4. Keep your answer concise but complete
        5. Use a helpful, professional tone

        Answer:
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=500)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return "I'm sorry, I encountered an error while generating the answer. Please try again."
    
    def create_qa_session(self, document_id: str) -> str:
        """
        Create a new Q&A session for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Session ID
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        session = QASession(
            session_id=session_id,
            document_id=document_id
        )
        
        self.storage.create_qa_session(session)
        return session_id
    
    def get_qa_session(self, session_id: str) -> Optional[QASession]:
        """Get a Q&A session by ID."""
        return self.storage.get_qa_session(session_id)
    
    def get_document_qa_sessions(self, document_id: str) -> List[QASession]:
        """Get all Q&A sessions for a document."""
        return self.storage.list_qa_sessions(document_id)
    
    def _extract_key_terms(self, question: str) -> List[str]:
        """Extract key terms from a question for context matching."""
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'was', 'were',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'this', 'that',
            'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'can', 'could', 'should', 'would', 'will',
            'shall', 'may', 'might', 'must', 'do', 'does', 'did', 'have', 'has', 'had'
        }
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', question.lower())
        
        # Filter out stop words and short words
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def _find_relevant_passages(self, question_terms: List[str], content: str, source_name: str) -> List[Dict[str, Any]]:
        """Find relevant passages in content based on question terms."""
        if not content or not question_terms:
            return []
        
        content_lower = content.lower()
        passages = []
        
        # Split content into sentences/paragraphs
        sentences = re.split(r'[.!?]\s+', content)
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 20:  # Skip very short sentences
                continue
                
            sentence_lower = sentence.lower()
            
            # Calculate relevance score based on term matches
            matches = sum(1 for term in question_terms if term in sentence_lower)
            
            if matches > 0:
                # Calculate relevance score (could be improved with TF-IDF or other methods)
                relevance_score = matches / len(question_terms)
                
                # Add context around the sentence
                start_idx = max(0, i - 1)
                end_idx = min(len(sentences), i + 2)
                context = '. '.join(sentences[start_idx:end_idx]).strip()
                
                passages.append({
                    'text': context,
                    'source': source_name,
                    'relevance_score': relevance_score,
                    'matches': matches
                })
        
        return passages
    
    def _extract_sources(self, context_sections: List[Dict[str, Any]]) -> List[str]:
        """Extract source references from context sections."""
        sources = []
        for section in context_sections:
            source_info = f"{section['source']}"
            if section.get('matches', 0) > 0:
                source_info += f" (relevance: {section['relevance_score']:.2f})"
            sources.append(source_info)
        
        return list(set(sources))  # Remove duplicates
    
    def _call_gemini_api(self, prompt: str, max_tokens: int = 500) -> str:
        """Make API call to Gemini."""
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.3  # Lower temperature for more focused answers
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"Gemini API error: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response format: {e}")
            raise Exception(f"Unexpected API response format: {str(e)}")


def create_qa_engine(api_key: str, storage: Optional[DocumentStorage] = None) -> QAEngine:
    """Factory function to create a Q&A engine."""
    if storage is None:
        storage = DocumentStorage()
    
    return QAEngine(storage, api_key)