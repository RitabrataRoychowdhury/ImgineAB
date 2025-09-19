"""Contract Analyst Engine for specialized legal document analysis."""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from src.services.qa_engine import QAEngine
from src.models.document import Document, QASession
from src.storage.document_storage import DocumentStorage
from src.utils.logging_config import get_logger
from src.utils.error_handling import QAError

logger = get_logger(__name__)


@dataclass
class ContractAnalysisResponse:
    """Structured response for contract analysis."""
    direct_evidence: str
    plain_explanation: str
    implication_analysis: Optional[str] = None
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    document_type: str = "unknown"
    legal_terms_found: List[str] = field(default_factory=list)


@dataclass
class ContractAnalysisSession(QASession):
    """Enhanced QA session for legal document analysis."""
    analysis_mode: str = "contract"  # "contract" or "standard"
    legal_document_type: Optional[str] = None
    structured_responses: List[ContractAnalysisResponse] = field(default_factory=list)


class ContractAnalystEngine(QAEngine):
    """Enhanced Q&A Engine specialized for legal document analysis."""
    
    # Legal document keywords for classification
    LEGAL_KEYWORDS = {
        'general': [
            'agreement', 'contract', 'terms', 'conditions', 'liability', 
            'intellectual property', 'confidential', 'proprietary', 'obligations',
            'rights', 'responsibilities', 'breach', 'termination', 'governing law',
            'jurisdiction', 'dispute', 'arbitration', 'indemnification', 'warranty'
        ],
        'mta': [
            'material transfer', 'research use', 'derivatives', 'publication',
            'recipient', 'provider', 'original material', 'modifications',
            'research purposes', 'commercial use', 'third party', 'ownership',
            'improvements', 'inventions', 'patent rights', 'licensing'
        ],
        'nda': [
            'non-disclosure', 'confidentiality', 'proprietary information',
            'trade secrets', 'confidential information', 'receiving party',
            'disclosing party', 'permitted use', 'return of information'
        ]
    }
    
    # Legal terms that should be weighted higher in context matching
    LEGAL_TERM_WEIGHTS = {
        'high': ['liability', 'indemnification', 'intellectual property', 'ownership', 'breach'],
        'medium': ['obligations', 'rights', 'responsibilities', 'termination', 'warranty'],
        'low': ['agreement', 'contract', 'terms', 'conditions']
    }
    
    def __init__(self, storage: DocumentStorage, api_key: str):
        super().__init__(storage, api_key)
        self.contract_prompt_template = self._get_contract_analysis_prompt()
    
    def detect_legal_document(self, document: Document) -> Tuple[bool, Optional[str], float]:
        """
        Detect if a document is a legal document and classify its type.
        
        Args:
            document: Document to analyze
            
        Returns:
            Tuple of (is_legal, document_type, confidence_score)
        """
        if not document.original_text:
            return False, None, 0.0
        
        text_lower = document.original_text.lower()
        title_lower = document.title.lower()
        
        # Count keyword matches
        legal_score = 0
        mta_score = 0
        nda_score = 0
        
        # Check general legal keywords
        for keyword in self.LEGAL_KEYWORDS['general']:
            if keyword in text_lower or keyword in title_lower:
                legal_score += 1
        
        # Check MTA-specific keywords
        for keyword in self.LEGAL_KEYWORDS['mta']:
            if keyword in text_lower or keyword in title_lower:
                mta_score += 1
        
        # Check NDA-specific keywords
        for keyword in self.LEGAL_KEYWORDS['nda']:
            if keyword in text_lower or keyword in title_lower:
                nda_score += 1
        
        # Calculate confidence scores
        total_keywords = len(self.LEGAL_KEYWORDS['general'])
        legal_confidence = min(legal_score / total_keywords, 1.0)
        
        # Determine document type with lower thresholds for better detection
        if legal_confidence < 0.15:  # Lowered threshold
            return False, None, legal_confidence
        
        # Classify specific legal document type with lower thresholds
        if mta_score >= 2:  # Lowered from 3 to 2
            return True, "MTA", min(legal_confidence + (mta_score / len(self.LEGAL_KEYWORDS['mta'])), 1.0)
        elif nda_score >= 2:  # Lowered from 3 to 2
            return True, "NDA", min(legal_confidence + (nda_score / len(self.LEGAL_KEYWORDS['nda'])), 1.0)
        elif legal_score >= 3:  # Lowered from 5 to 3
            return True, "Legal Contract", legal_confidence
        
        return False, None, legal_confidence
    
    def extract_legal_terms(self, question: str) -> List[str]:
        """
        Extract legal terms from a question for enhanced context matching.
        
        Args:
            question: User's question
            
        Returns:
            List of legal terms found in the question
        """
        question_lower = question.lower()
        legal_terms = []
        
        # Check all legal keywords
        for category, keywords in self.LEGAL_KEYWORDS.items():
            for keyword in keywords:
                if keyword in question_lower:
                    legal_terms.append(keyword)
        
        return legal_terms
    
    def find_legal_context(self, question: str, document: Document) -> List[Dict[str, Any]]:
        """
        Find relevant context with legal term weighting.
        
        Args:
            question: User's question
            document: Document to search
            
        Returns:
            List of relevant context sections with enhanced legal scoring
        """
        # Get base context from parent class
        base_context = self.get_relevant_context(question, document)
        
        # Extract legal terms from question
        legal_terms = self.extract_legal_terms(question)
        
        # Enhance scoring with legal term weights
        for context in base_context:
            legal_boost = 0
            text_lower = context['text'].lower()
            
            # Apply legal term weights
            for term in legal_terms:
                # Check for exact match or word variations
                term_found = term in text_lower
                if not term_found and term == 'liability':
                    # Check for variations like "liable", "liabilities"
                    term_found = 'liable' in text_lower or 'liabilities' in text_lower
                
                if term_found:
                    if term in self.LEGAL_TERM_WEIGHTS['high']:
                        legal_boost += 0.3
                    elif term in self.LEGAL_TERM_WEIGHTS['medium']:
                        legal_boost += 0.2
                    elif term in self.LEGAL_TERM_WEIGHTS['low']:
                        legal_boost += 0.1
            
            # Also check for any legal keywords in the text for additional boost
            for keyword in self.LEGAL_KEYWORDS['general']:
                keyword_found = keyword in text_lower
                if not keyword_found and keyword == 'liability':
                    keyword_found = 'liable' in text_lower or 'liabilities' in text_lower
                
                if keyword_found and keyword not in legal_terms:
                    legal_boost += 0.1
                    break
            
            # Update relevance score with legal boost
            context['relevance_score'] = min(context['relevance_score'] + legal_boost, 1.0)
            context['legal_terms_found'] = legal_terms
        
        # Re-sort by enhanced relevance score
        base_context.sort(key=lambda x: x['relevance_score'], reverse=True)
        return base_context
    
    def generate_contract_analysis(self, question: str, context_sections: List[Dict[str, Any]], document: Document) -> ContractAnalysisResponse:
        """
        Generate structured contract analysis using specialized prompts.
        
        Args:
            question: User's question
            context_sections: Relevant context sections
            document: Source document
            
        Returns:
            Structured contract analysis response
        """
        # Detect document type if not already done
        is_legal, doc_type, confidence = self.detect_legal_document(document)
        
        # Prepare context for the prompt
        context_text = "\n\n".join([
            f"**{section['source']}:**\n{section['text']}"
            for section in context_sections
        ])
        
        # Use contract-specific prompt
        prompt = self.contract_prompt_template.format(
            document_title=document.title,
            document_type=doc_type or document.document_type or 'Legal Document',
            context_text=context_text,
            question=question
        )
        
        try:
            # Generate response using Gemini API
            raw_response = self._call_gemini_api(prompt, max_tokens=800)
            
            # Parse structured response
            structured_response = self.format_structured_response(raw_response)
            
            # Extract sources and legal terms
            sources = self._extract_sources(context_sections)
            legal_terms = []
            for section in context_sections:
                legal_terms.extend(section.get('legal_terms_found', []))
            
            return ContractAnalysisResponse(
                direct_evidence=structured_response['direct_evidence'],
                plain_explanation=structured_response['plain_explanation'],
                implication_analysis=structured_response.get('implication_analysis'),
                sources=sources,
                confidence=confidence,
                document_type=doc_type or 'Legal Document',
                legal_terms_found=list(set(legal_terms))
            )
            
        except Exception as e:
            logger.error(f"Error generating contract analysis: {e}")
            # Fallback to standard analysis
            fallback_answer = self.generate_answer(question, context_sections, document)
            return ContractAnalysisResponse(
                direct_evidence=fallback_answer,
                plain_explanation="Analysis could not be structured due to processing error.",
                implication_analysis=None,
                sources=self._extract_sources(context_sections),
                confidence=0.5,
                document_type=doc_type or 'Legal Document'
            )
    
    def format_structured_response(self, raw_response: str) -> Dict[str, str]:
        """
        Parse AI response into structured three-part format.
        
        Args:
            raw_response: Raw response from AI
            
        Returns:
            Dictionary with structured response parts
        """
        # Initialize response parts
        response_parts = {
            'direct_evidence': '',
            'plain_explanation': '',
            'implication_analysis': ''
        }
        
        # Try to parse structured response
        try:
            # Look for section headers
            sections = {
                'direct_evidence': [
                    r'\*\*Direct Evidence\*\*:?\s*(.*?)(?=\*\*|$)',
                    r'1\.\s*\*\*Direct Evidence\*\*:?\s*(.*?)(?=2\.|$)',
                    r'Direct Evidence:?\s*(.*?)(?=Plain|$)'
                ],
                'plain_explanation': [
                    r'\*\*Plain-English Explanation\*\*:?\s*(.*?)(?=\*\*|$)',
                    r'2\.\s*\*\*Plain-English Explanation\*\*:?\s*(.*?)(?=3\.|$)',
                    r'Plain-English Explanation:?\s*(.*?)(?=Implication|$)'
                ],
                'implication_analysis': [
                    r'\*\*Implication[/\s]*Analysis\*\*:?\s*(.*?)(?=\*\*|$)',
                    r'3\.\s*\*\*Implication[/\s]*Analysis\*\*:?\s*(.*?)$',
                    r'Implication[/\s]*Analysis:?\s*(.*?)$'
                ]
            }
            
            # Extract each section using regex patterns
            for section_name, patterns in sections.items():
                for pattern in patterns:
                    match = re.search(pattern, raw_response, re.DOTALL | re.IGNORECASE)
                    if match:
                        content = match.group(1).strip()
                        if content:
                            response_parts[section_name] = content
                            break
            
            # If structured parsing failed, try to split by numbered sections
            if not any(response_parts.values()):
                lines = raw_response.split('\n')
                current_section = None
                current_content = []
                
                for line in lines:
                    line = line.strip()
                    if re.match(r'^1\.', line) or 'direct evidence' in line.lower():
                        if current_section and current_content:
                            response_parts[current_section] = '\n'.join(current_content).strip()
                        current_section = 'direct_evidence'
                        current_content = [re.sub(r'^1\.\s*', '', line, flags=re.IGNORECASE)]
                    elif re.match(r'^2\.', line) or 'plain-english' in line.lower():
                        if current_section and current_content:
                            response_parts[current_section] = '\n'.join(current_content).strip()
                        current_section = 'plain_explanation'
                        current_content = [re.sub(r'^2\.\s*', '', line, flags=re.IGNORECASE)]
                    elif re.match(r'^3\.', line) or 'implication' in line.lower():
                        if current_section and current_content:
                            response_parts[current_section] = '\n'.join(current_content).strip()
                        current_section = 'implication_analysis'
                        current_content = [re.sub(r'^3\.\s*', '', line, flags=re.IGNORECASE)]
                    elif current_section and line:
                        current_content.append(line)
                
                # Add the last section
                if current_section and current_content:
                    response_parts[current_section] = '\n'.join(current_content).strip()
            
            # If still no structured content, use the entire response as direct evidence
            if not any(response_parts.values()):
                response_parts['direct_evidence'] = raw_response.strip()
                response_parts['plain_explanation'] = "The response could not be automatically structured."
            
        except Exception as e:
            logger.error(f"Error parsing structured response: {e}")
            response_parts['direct_evidence'] = raw_response.strip()
            response_parts['plain_explanation'] = "Response parsing encountered an error."
        
        return response_parts
    
    def answer_question(self, question: str, document_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced answer_question that uses contract analysis for legal documents.
        
        Args:
            question: The user's question
            document_id: ID of the document to query
            session_id: Optional session ID for conversation tracking
            
        Returns:
            Dictionary containing structured answer, sources, and metadata
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
            
            # Detect if this is a legal document
            is_legal, doc_type, legal_confidence = self.detect_legal_document(document)
            
            if is_legal:
                # Use contract analysis mode
                context_sections = self.find_legal_context(question, document)
                
                if not context_sections:
                    return {
                        'answer': "I couldn't find relevant information in the legal document to answer your question.",
                        'sources': [],
                        'confidence': 0.2,
                        'error': 'No relevant context found',
                        'analysis_mode': 'contract',
                        'document_type': doc_type
                    }
                
                # Generate structured contract analysis
                analysis = self.generate_contract_analysis(question, context_sections, document)
                
                # Format the structured response
                formatted_answer = self._format_contract_response(analysis)
                
                # Store the interaction
                if session_id:
                    self.storage.add_qa_interaction(session_id, question, formatted_answer, analysis.sources)
                
                return {
                    'answer': formatted_answer,
                    'sources': analysis.sources,
                    'confidence': analysis.confidence,
                    'document_title': document.title,
                    'document_type': analysis.document_type,
                    'analysis_mode': 'contract',
                    'legal_terms_found': analysis.legal_terms_found,
                    'structured_response': {
                        'direct_evidence': analysis.direct_evidence,
                        'plain_explanation': analysis.plain_explanation,
                        'implication_analysis': analysis.implication_analysis
                    }
                }
            else:
                # Fall back to standard Q&A mode
                result = super().answer_question(question, document_id, session_id)
                result['analysis_mode'] = 'standard'
                return result
                
        except Exception as e:
            logger.error(f"Error in contract analysis: {e}")
            return {
                'answer': "I'm sorry, I encountered an error while analyzing this legal document. Please try again.",
                'sources': [],
                'confidence': 0.0,
                'error': str(e),
                'analysis_mode': 'error'
            }
    
    def _format_contract_response(self, analysis: ContractAnalysisResponse) -> str:
        """Format the structured contract analysis into a readable response."""
        formatted_parts = []
        
        if analysis.direct_evidence:
            formatted_parts.append(f"**Direct Evidence:**\n{analysis.direct_evidence}")
        
        if analysis.plain_explanation:
            formatted_parts.append(f"**Plain-English Explanation:**\n{analysis.plain_explanation}")
        
        if analysis.implication_analysis:
            formatted_parts.append(f"**Implication/Analysis:**\n{analysis.implication_analysis}")
        
        return "\n\n".join(formatted_parts)
    
    def _get_contract_analysis_prompt(self) -> str:
        """Get the specialized contract analysis prompt template."""
        return """
You are a contract analyst chatbot that helps users understand legal and research agreements. 
Your primary reference is the provided document. 

### Guidelines:
- Always ground answers in the text of the document. Quote specific clauses or exhibits when possible.
- If a question is subjective (e.g., "who benefits more?"), provide balanced reasoning using evidence from the agreement. 
- Do NOT say "the document doesn't say"; instead, infer from ownership, IP, liability, or restrictions.
- Structure answers in this format:

1. **Direct Evidence**: Cite or paraphrase relevant parts of the agreement.
2. **Plain-English Explanation**: Explain what it means in simple language.
3. **Implication / Analysis** (if applicable): Who it benefits, what risk it creates, what actions are required.

### Style:
- Be clear, conversational, and professional.
- Avoid legalese unless quoting directly.
- If multiple sections are relevant, summarize across them instead of giving a single-clause answer.

Document: {document_title}
Document Type: {document_type}

Context: {context_text}

Question: {question}

Provide your analysis:
"""


def create_contract_analyst_engine(api_key: str, storage: Optional[DocumentStorage] = None) -> ContractAnalystEngine:
    """Factory function to create a contract analyst engine."""
    if storage is None:
        storage = DocumentStorage()
    
    return ContractAnalystEngine(storage, api_key)