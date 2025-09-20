"""
Conversational AI Engine for enhanced Q&A capabilities.
Handles natural conversation flow while maintaining specialized analysis capabilities.
"""

import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from src.utils.error_handling import (
    ConversationalAIError, ContextManagementError, handle_errors, 
    graceful_degradation, ErrorType
)
from src.models.conversational import (
    QuestionType, CompoundResponse, ConversationalResponse,
    ConversationContext, ConversationTurn
)
from src.models.document import Document
from src.services.qa_engine import QAEngine
from src.services.contract_analyst_engine import ContractAnalystEngine


class ConversationalAIEngine:
    """
    Manages conversational interactions with context awareness and mode switching.
    """
    
    def __init__(self, qa_engine: QAEngine, contract_engine: ContractAnalystEngine):
        self.qa_engine = qa_engine
        self.contract_engine = contract_engine
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.logger = logging.getLogger(__name__)
        
        # Question classification patterns
        self.casual_patterns = [
            r'\b(hello|hi|hey|thanks|thank you|goodbye|bye)\b',
            r'\b(how are you|what\'s up|nice to meet)\b',
            r'\b(please|could you|would you mind)\b'
        ]
        
        self.legal_patterns = [
            r'\b(contract|agreement|clause|liability|obligation)\b',
            r'\b(legal|law|regulation|compliance|breach)\b',
            r'\b(terms|conditions|warranty|indemnity)\b',
            r'\b(jurisdiction|governing law|dispute)\b'
        ]
        
        self.compound_indicators = [
            r'\band\b', r'\bor\b', r'\balso\b', r'\badditionally\b',
            r'\bfurthermore\b', r'\bmoreover\b', r';'
        ]

    def classify_question_type(self, question: str, conversation_history: List[Dict]) -> QuestionType:
        """
        Classify the type of question to determine appropriate response mode.
        """
        question_lower = question.lower()
        
        # Check for compound question indicators
        compound_score = sum(1 for pattern in self.compound_indicators 
                           if re.search(pattern, question_lower))
        
        # Check for casual conversation patterns
        casual_score = sum(1 for pattern in self.casual_patterns 
                          if re.search(pattern, question_lower))
        
        # Check for legal/technical patterns
        legal_score = sum(1 for pattern in self.legal_patterns 
                         if re.search(pattern, question_lower))
        
        # Determine primary type - prioritize casual and legal over compound
        if casual_score > 0 and legal_score == 0:
            primary_type = "casual"
            confidence = min(0.8, 0.4 + (casual_score * 0.1))
        elif legal_score > casual_score:
            primary_type = "legal"
            confidence = min(0.9, 0.5 + (legal_score * 0.1))
        elif compound_score >= 2:  # Higher threshold for compound detection
            primary_type = "compound"
            confidence = min(0.9, 0.6 + (compound_score * 0.1))
        elif casual_score > 0:
            primary_type = "casual"
            confidence = min(0.8, 0.4 + (casual_score * 0.1))
        else:
            primary_type = "technical"
            confidence = 0.6
        
        # Determine sub-types and requirements
        sub_types = []
        if casual_score > 0:
            sub_types.append("casual")
        if legal_score > 0:
            sub_types.append("legal")
        if compound_score > 0:
            sub_types.append("compound")
        
        requires_legal_analysis = legal_score > 0 or primary_type == "legal"
        requires_context_switching = len(sub_types) > 1
        
        return QuestionType(
            primary_type=primary_type,
            confidence=confidence,
            sub_types=sub_types,
            requires_legal_analysis=requires_legal_analysis,
            requires_context_switching=requires_context_switching
        )

    def handle_compound_question(self, question: str, document_id: str, session_id: str) -> CompoundResponse:
        """
        Break down and handle compound questions with multiple parts.
        """
        # Split question into parts using common separators
        separators = [' and ', ' or ', '; ', ', ', ' also ', ' additionally ']
        question_parts = [question]
        
        for separator in separators:
            new_parts = []
            for part in question_parts:
                new_parts.extend(part.split(separator))
            question_parts = new_parts
        
        # Clean and filter parts
        question_parts = [part.strip() for part in question_parts if part.strip()]
        
        individual_responses = []
        analysis_modes_used = []
        all_sources = []
        
        # Process each part
        for i, part in enumerate(question_parts):
            try:
                # Classify each part
                part_type = self.classify_question_type(part, [])
                
                # Choose appropriate analysis mode
                if part_type.requires_legal_analysis:
                    mode = "legal"
                    response = self._handle_legal_question(part, document_id, session_id)
                else:
                    mode = "casual"
                    response = self._handle_casual_question(part, document_id, session_id)
                
                individual_responses.append({
                    'question': part,
                    'response': response.answer,
                    'mode': mode,
                    'confidence': response.confidence
                })
                
                analysis_modes_used.append(mode)
                all_sources.extend(response.context_used)
                
            except Exception as e:
                self.logger.error(f"Error processing question part '{part}': {str(e)}")
                individual_responses.append({
                    'question': part,
                    'response': f"I encountered an issue processing this part: {part}",
                    'mode': "error",
                    'confidence': 0.0
                })
        
        # Synthesize comprehensive response
        synthesized_response = self._synthesize_compound_response(individual_responses)
        
        return CompoundResponse(
            question_parts=question_parts,
            individual_responses=individual_responses,
            synthesized_response=synthesized_response,
            sources=list(set(all_sources)),
            analysis_modes_used=list(set(analysis_modes_used))
        )

    @handle_errors(ErrorType.CONTEXT_MANAGEMENT_ERROR)
    def manage_conversation_context(self, session_id: str, question: str, response: str) -> None:
        """
        Update conversation context with new turn information.
        """
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = ConversationContext(
                session_id=session_id,
                document_id="",
                conversation_history=[],
                current_topic="",
                analysis_mode="casual",
                user_preferences={},
                context_summary=""
            )
        
        context = self.conversation_contexts[session_id]
        
        # Create new conversation turn
        turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            question=question,
            response=response,
            question_type=self.classify_question_type(question, []),
            analysis_mode=context.analysis_mode,
            sources_used=[],
            timestamp=datetime.now()
        )
        
        # Add to history
        context.conversation_history.append(turn)
        
        # Update current topic (simple keyword extraction)
        keywords = self._extract_keywords(question)
        if keywords:
            context.current_topic = keywords[0]
        
        # Limit history size
        if len(context.conversation_history) > 50:
            context.conversation_history = context.conversation_history[-50:]
        
        # Update context summary
        context.context_summary = self._generate_context_summary(context)

    def generate_clarification_request(self, ambiguous_question: str) -> str:
        """
        Generate clarification requests for ambiguous questions.
        """
        clarification_templates = [
            "Could you provide more specific details about what you're looking for?",
            "I want to make sure I understand correctly. Are you asking about [topic] in relation to [context]?",
            "To give you the most accurate answer, could you clarify which aspect interests you most?",
            "I notice your question could be interpreted in several ways. Could you be more specific?"
        ]
        
        # Simple selection based on question length and content
        if len(ambiguous_question.split()) < 5:
            return clarification_templates[0]
        elif any(word in ambiguous_question.lower() for word in ['this', 'that', 'it']):
            return clarification_templates[1]
        else:
            return clarification_templates[2]

    def switch_analysis_mode(self, current_mode: str, question: str, document: Document) -> str:
        """
        Determine if analysis mode should be switched based on question context.
        """
        question_type = self.classify_question_type(question, [])
        
        if question_type.requires_legal_analysis and current_mode != "legal":
            return "legal"
        elif not question_type.requires_legal_analysis and current_mode == "legal":
            return "casual"
        
        return current_mode

    @handle_errors(ErrorType.CONVERSATIONAL_AI_ERROR)
    def answer_conversational_question(self, question: str, document_id: str, session_id: str) -> ConversationalResponse:
        """
        Main entry point for answering conversational questions.
        """
        try:
            # Get or create conversation context
            if session_id not in self.conversation_contexts:
                self.conversation_contexts[session_id] = ConversationContext(
                    session_id=session_id,
                    document_id=document_id,
                    conversation_history=[],
                    current_topic="",
                    analysis_mode="casual",
                    user_preferences={},
                    context_summary=""
                )
            
            context = self.conversation_contexts[session_id]
            question_type = self.classify_question_type(question, context.conversation_history)
            
            # Handle compound questions
            if question_type.primary_type == "compound":
                compound_response = self.handle_compound_question(question, document_id, session_id)
                response = ConversationalResponse(
                    answer=compound_response.synthesized_response,
                    conversation_tone="professional",
                    context_used=compound_response.sources,
                    follow_up_suggestions=self._generate_follow_up_suggestions(question),
                    analysis_mode="compound",
                    confidence=0.8
                )
            elif question_type.requires_legal_analysis:
                response = self._handle_legal_question(question, document_id, session_id)
            else:
                response = self._handle_casual_question(question, document_id, session_id)
            
            # Update conversation context
            self.manage_conversation_context(session_id, question, response.answer)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in conversational question handling: {str(e)}")
            raise ConversationalAIError(
                f"Failed to process conversational question: {question[:100]}...",
                {"question": question, "document_id": document_id, "session_id": session_id},
                e
            )

    def _handle_legal_question(self, question: str, document_id: str, session_id: str) -> ConversationalResponse:
        """Handle legal-specific questions using contract analyst engine."""
        try:
            # Use contract analyst engine for legal questions
            result = self.contract_engine.answer_question(question, document_id, session_id)
            
            return ConversationalResponse(
                answer=result.get('answer', 'No legal analysis available.'),
                conversation_tone="professional",
                context_used=result.get('sources', []),
                follow_up_suggestions=self._generate_legal_follow_ups(question),
                analysis_mode="legal",
                confidence=result.get('confidence', 0.7)
            )
        except Exception as e:
            self.logger.error(f"Error in legal question handling: {str(e)}")
            # Graceful degradation to basic Q&A
            try:
                basic_result = self.qa_engine.answer_question(question, document_id)
                return ConversationalResponse(
                    answer=f"Legal analysis unavailable. Basic answer: {basic_result.get('answer', 'No answer available.')}",
                    conversation_tone="professional",
                    context_used=basic_result.get('sources', []),
                    follow_up_suggestions=["Would you like to try a simpler question?"],
                    analysis_mode="basic_fallback",
                    confidence=basic_result.get('confidence', 0.5) * 0.7  # Reduced confidence for fallback
                )
            except Exception as fallback_error:
                self.logger.error(f"Fallback also failed: {str(fallback_error)}")
                return ConversationalResponse(
                    answer="I'm having trouble analyzing this legal question. Could you try rephrasing it more simply?",
                    conversation_tone="professional",
                    context_used=[],
                    follow_up_suggestions=["Try asking about specific terms or clauses"],
                    analysis_mode="error_fallback",
                    confidence=0.0
                )

    def _handle_casual_question(self, question: str, document_id: str, session_id: str) -> ConversationalResponse:
        """Handle casual conversational questions."""
        try:
            # Use standard QA engine for casual questions
            result = self.qa_engine.answer_question(question, document_id)
            
            return ConversationalResponse(
                answer=result.get('answer', 'I\'m not sure how to answer that question.'),
                conversation_tone="casual",
                context_used=result.get('sources', []),
                follow_up_suggestions=self._generate_casual_follow_ups(question),
                analysis_mode="casual",
                confidence=result.get('confidence', 0.6)
            )
        except Exception as e:
            self.logger.error(f"Error in casual question handling: {str(e)}")
            # Provide a helpful fallback response
            return ConversationalResponse(
                answer="I'm having trouble with that question right now. Could you try asking it differently or be more specific about what you'd like to know?",
                conversation_tone="casual",
                context_used=[],
                follow_up_suggestions=[
                    "Try asking about specific parts of the document",
                    "Ask about key terms or concepts",
                    "Request a summary of the document"
                ],
                analysis_mode="error_fallback",
                confidence=0.0
            )

    def _synthesize_compound_response(self, individual_responses: List[Dict[str, Any]]) -> str:
        """Synthesize individual responses into a coherent compound response."""
        if not individual_responses:
            return "I wasn't able to process your compound question."
        
        synthesis = "Here's what I found for each part of your question:\n\n"
        
        for i, response in enumerate(individual_responses, 1):
            synthesis += f"{i}. Regarding '{response['question']}': {response['response']}\n\n"
        
        synthesis += "Let me know if you'd like me to elaborate on any of these points!"
        
        return synthesis

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key topics from text for context tracking."""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Filter out common words
        stop_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were', 'said', 'what', 'are', 'the', 'and'}
        keywords = [word for word in words if word not in stop_words]
        return keywords[:3]  # Return top 3 keywords

    def _generate_context_summary(self, context: ConversationContext) -> str:
        """Generate a summary of the conversation context."""
        if not context.conversation_history:
            return "New conversation"
        
        recent_topics = []
        for turn in context.conversation_history[-5:]:  # Last 5 turns
            keywords = self._extract_keywords(turn.question)
            recent_topics.extend(keywords)
        
        if recent_topics:
            return f"Recent topics: {', '.join(set(recent_topics[:5]))}"
        else:
            return "General conversation"

    def _generate_follow_up_suggestions(self, question: str) -> List[str]:
        """Generate relevant follow-up question suggestions."""
        return [
            "Would you like me to elaborate on any specific point?",
            "Are there other aspects of this topic you'd like to explore?",
            "Do you need more detailed analysis on this matter?"
        ]

    def _generate_legal_follow_ups(self, question: str) -> List[str]:
        """Generate legal-specific follow-up suggestions."""
        return [
            "Would you like me to analyze the legal implications in more detail?",
            "Should I look for related clauses or provisions?",
            "Do you need information about compliance requirements?"
        ]

    def _generate_casual_follow_ups(self, question: str) -> List[str]:
        """Generate casual follow-up suggestions."""
        return [
            "Is there anything else you'd like to know?",
            "Would you like me to explain this differently?",
            "Are there related topics you're curious about?"
        ]