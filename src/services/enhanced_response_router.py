"""
Enhanced Response Router for Contract Assistant

Main orchestration component that routes questions to appropriate handlers
and coordinates response generation with context awareness.

Now includes guaranteed structured response patterns with never-fail logic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import traceback
from src.models.enhanced import (
    EnhancedResponse, QuestionIntent, ResponseStrategy, 
    ConversationContext, MTAContext, MTAInsight,
    IntentType, HandlerType, ToneType, ResponseType
)
from src.models.document import Document
from src.services.question_classifier import QuestionClassifier
from src.services.fallback_response_generator import FallbackResponseGenerator
from src.services.mta_specialist import MTASpecialistModule
from src.services.enhanced_context_manager import EnhancedContextManager
from src.services.contract_analyst_engine import ContractAnalystEngine
from src.services.structured_response_system import StructuredResponseSystem
from src.storage.document_storage import DocumentStorage
import os
# Error handling will be done with try-catch blocks


logger = logging.getLogger(__name__)


class EnhancedResponseRouter:
    """
    Main orchestration component for enhanced contract assistant responses.
    
    Now includes guaranteed structured response patterns with never-fail logic
    that ensures EVERY input receives a meaningful, structured response.
    """
    
    def __init__(self, storage: DocumentStorage = None, api_key: str = None):
        self.question_classifier = QuestionClassifier()
        self.fallback_generator = FallbackResponseGenerator()
        self.mta_specialist = MTASpecialistModule()
        self.context_manager = EnhancedContextManager()
        
        # Initialize structured response system for guaranteed responses
        self.structured_response_system = StructuredResponseSystem()
        
        # Initialize contract engine with proper dependencies
        if storage is None:
            storage = DocumentStorage()
        
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        
        self.contract_engine = ContractAnalystEngine(storage, api_key)
        
    def route_question(
        self, 
        question: str, 
        document_id: str, 
        session_id: str,
        document: Optional[Document] = None
    ) -> EnhancedResponse:
        """
        Route question to appropriate handler and generate enhanced response.
        
        This method now uses the structured response system to guarantee
        meaningful output regardless of input quality or system errors.
        """
        
        try:
            # NEVER-FAIL GUARANTEE: Use structured response system as primary handler
            document_content = None
            if document:
                document_content = getattr(document, 'content', None) or getattr(document, 'original_text', '')
            
            # Get conversation context for additional context
            conversation_context = None
            try:
                conversation_context = self.context_manager.get_conversation_context(session_id)
            except Exception as context_error:
                logger.warning(f"Could not get conversation context: {context_error}")
            
            # Prepare context dictionary
            context_dict = {
                'session_id': session_id,
                'document_id': document_id,
                'conversation_context': conversation_context
            }
            
            # Generate guaranteed structured response
            response = self.structured_response_system.process_input_with_guaranteed_response(
                user_input=question,
                document_content=document_content,
                context=context_dict
            )
            
            # Try to enhance with existing systems (but don't fail if they error)
            try:
                response = self._enhance_with_existing_systems(
                    response, question, document, session_id, conversation_context
                )
            except Exception as enhancement_error:
                logger.warning(f"Enhancement failed but continuing with structured response: {enhancement_error}")
            
            # Try to update conversation context (but don't fail if it errors)
            try:
                if conversation_context:
                    # Create a basic intent for context tracking
                    intent = QuestionIntent(
                        primary_intent=IntentType.DOCUMENT_RELATED,
                        confidence=response.confidence,
                        secondary_intents=[],
                        document_relevance_score=0.7,
                        casualness_level=0.3,
                        requires_mta_expertise=False,
                        requires_fallback=False
                    )
                    
                    strategy = ResponseStrategy(
                        handler_type=HandlerType.EXISTING_CONTRACT,
                        use_structured_format=True,
                        include_suggestions=True,
                        tone_preference=response.tone,
                        fallback_options=[],
                        context_requirements=[]
                    )
                    
                    self.context_manager.update_conversation_context(
                        session_id, question, response, intent, strategy
                    )
            except Exception as context_update_error:
                logger.warning(f"Context update failed: {context_update_error}")
            
            logger.info(f"Successfully generated structured response for question: {question[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Critical error in route_question: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Ultimate fallback - this should never fail
            return self.structured_response_system._create_ultimate_fallback_response(question, str(e))
    
    def classify_question_intent(
        self, 
        question: str, 
        document: Optional[Document] = None,
        context: Optional[ConversationContext] = None
    ) -> QuestionIntent:
        """Classify question intent using context awareness"""
        
        try:
            # Use question classifier with context
            intent = self.question_classifier.classify_intent(question, context)
            
            # Enhance with MTA-specific detection if document suggests MTA
            if document and self._is_mta_document(document):
                intent.requires_mta_expertise = True
                
                # Adjust confidence for MTA-specific questions
                if self._contains_mta_terms(question):
                    intent.confidence = min(1.0, intent.confidence + 0.1)
            
            return intent
            
        except Exception as e:
            logger.error(f"Error in classify_question_intent: {str(e)}")
            # Return safe default intent
            return QuestionIntent(
                primary_intent="document_related",
                confidence=0.5,
                secondary_intents=[],
                document_relevance_score=0.5,
                casualness_level=0.0,
                requires_mta_expertise=False,
                requires_fallback=True
            )
    
    def determine_response_strategy(
        self, 
        intent: QuestionIntent, 
        document: Optional[Document] = None,
        context: Optional[ConversationContext] = None
    ) -> ResponseStrategy:
        """Determine the best response strategy based on intent and context"""
        
        # Default strategy
        strategy = ResponseStrategy(
            handler_type=HandlerType.EXISTING_CONTRACT,
            use_structured_format=True,
            include_suggestions=True,
            tone_preference=ToneType.PROFESSIONAL,
            fallback_options=[],
            context_requirements=[]
        )
        
        # Adjust strategy based on intent
        if intent.primary_intent == IntentType.DOCUMENT_RELATED and intent.confidence > 0.7:
            strategy.handler_type = HandlerType.EXISTING_CONTRACT
            strategy.use_structured_format = True
            
            if intent.requires_mta_expertise:
                strategy.context_requirements.append("mta_expertise")
                
        elif intent.primary_intent == IntentType.CONTRACT_GENERAL:
            strategy.handler_type = HandlerType.GENERAL_KNOWLEDGE
            strategy.use_structured_format = False
            strategy.fallback_options.append("document_redirection")
            
        elif intent.primary_intent == IntentType.OFF_TOPIC:
            strategy.handler_type = HandlerType.FALLBACK
            strategy.use_structured_format = False
            strategy.include_suggestions = True
            strategy.fallback_options.extend(["redirection", "suggestions"])
            
        elif intent.primary_intent == IntentType.CASUAL:
            strategy.handler_type = HandlerType.CASUAL
            strategy.use_structured_format = False
            strategy.tone_preference = ToneType.CONVERSATIONAL
            strategy.fallback_options.append("gentle_redirection")
        
        # Adjust tone based on context and casualness
        if context and context.current_tone == ToneType.CONVERSATIONAL:
            strategy.tone_preference = ToneType.CONVERSATIONAL
        elif intent.casualness_level > 0.6:
            strategy.tone_preference = ToneType.CONVERSATIONAL
        
        # Add context-aware adjustments
        if context:
            patterns = self.context_manager.detect_conversation_patterns(context.session_id)
            
            if "repetitive_questioning" in patterns:
                strategy.fallback_options.append("pattern_acknowledgment")
            
            if "increasing_complexity" in patterns:
                strategy.context_requirements.append("detailed_explanation")
            
            if "casual_drift" in patterns:
                strategy.tone_preference = ToneType.CONVERSATIONAL
        
        return strategy
    
    def coordinate_fallback_response(
        self, 
        question: str, 
        intent: QuestionIntent,
        document: Optional[Document] = None
    ) -> EnhancedResponse:
        """Coordinate fallback response generation"""
        
        try:
            # Generate appropriate fallback response
            if intent.primary_intent == IntentType.OFF_TOPIC:
                fallback_response = self.fallback_generator.generate_off_topic_response(question, document)
                content = fallback_response.content if hasattr(fallback_response, 'content') else str(fallback_response)
                suggestions = self.fallback_generator.suggest_relevant_questions(document) if document else []
                
            elif intent.primary_intent == IntentType.CASUAL:
                fallback_response = self.fallback_generator.create_playful_response(question)
                content = fallback_response.content if hasattr(fallback_response, 'content') else str(fallback_response)
                suggestions = self.fallback_generator.suggest_relevant_questions(document) if document else []
                
            elif intent.primary_intent == IntentType.CONTRACT_GENERAL:
                fallback_response = self.fallback_generator.create_general_knowledge_response(question, "contract")
                content = fallback_response.content if hasattr(fallback_response, 'content') else str(fallback_response)
                suggestions = []
                
            else:
                # Default fallback
                fallback_response = self.fallback_generator.generate_off_topic_response(question, document)
                content = fallback_response.content if hasattr(fallback_response, 'content') else str(fallback_response)
                suggestions = []
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.FALLBACK,
                confidence=intent.confidence,
                sources=["fallback_generator"],
                suggestions=suggestions,
                tone=ToneType.CONVERSATIONAL if intent.casualness_level > 0.5 else ToneType.PROFESSIONAL,
                structured_format=None,
                context_used=[],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error in coordinate_fallback_response: {str(e)}")
            return self._create_simple_fallback_response(question)
    
    def _generate_response(
        self,
        question: str,
        intent: QuestionIntent,
        strategy: ResponseStrategy,
        document: Optional[Document],
        context: Optional[ConversationContext]
    ) -> EnhancedResponse:
        """Generate response based on determined strategy"""
        
        if strategy.handler_type == HandlerType.EXISTING_CONTRACT:
            return self._handle_document_related_question(question, document, intent, strategy, context)
            
        elif strategy.handler_type == HandlerType.GENERAL_KNOWLEDGE:
            return self._handle_general_knowledge_question(question, intent, strategy, document)
            
        elif strategy.handler_type == HandlerType.FALLBACK:
            return self.coordinate_fallback_response(question, intent, document)
            
        elif strategy.handler_type == HandlerType.CASUAL:
            return self._handle_casual_question(question, intent, strategy, document)
            
        else:
            # Default to existing contract engine
            return self._handle_document_related_question(question, document, intent, strategy, context)
    
    def _handle_document_related_question(
        self,
        question: str,
        document: Optional[Document],
        intent: QuestionIntent,
        strategy: ResponseStrategy,
        context: Optional[ConversationContext]
    ) -> EnhancedResponse:
        """Handle document-related questions using existing contract engine"""
        
        try:
            if not document:
                return self._create_document_not_found_response(question, intent)
            
            # Use existing contract analyst engine with better error handling
            try:
                contract_response = self.contract_engine.analyze_question(question, document.id)
                
                # Check if we got a valid response
                if contract_response and contract_response.get('response'):
                    response_content = contract_response.get('response', '')
                else:
                    # If no valid response, create a helpful fallback
                    response_content = self._create_document_analysis_fallback(question, document)
                    contract_response = {'response': response_content}
                
            except Exception as engine_error:
                logger.error(f"Contract engine error: {str(engine_error)}")
                # Create a meaningful response based on the document content
                response_content = self._create_document_analysis_fallback(question, document)
                contract_response = {'response': response_content}
            
            # Create enhanced response
            response = EnhancedResponse(
                content=response_content,
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=intent.confidence,
                sources=["contract_analyst_engine"],
                suggestions=[],
                tone=strategy.tone_preference,
                structured_format=contract_response,  # Preserve original structure
                context_used=[],
                timestamp=datetime.now()
            )
            
            # Add MTA expertise if required
            if intent.requires_mta_expertise and "mta_expertise" in strategy.context_requirements:
                response = self._enhance_with_mta_expertise(response, question, document, context)
            
            # Add suggestions if requested
            if strategy.include_suggestions:
                response.suggestions = self._generate_contextual_suggestions(question, document, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling document-related question: {str(e)}")
            return self._create_error_recovery_response(question, intent, str(e))
    
    def _handle_general_knowledge_question(
        self,
        question: str,
        intent: QuestionIntent,
        strategy: ResponseStrategy,
        document: Optional[Document]
    ) -> EnhancedResponse:
        """Handle general contract knowledge questions"""
        
        try:
            # Generate general knowledge response with transparency
            fallback_response = self.fallback_generator.create_general_knowledge_response(question, "contract")
            content = fallback_response.content if hasattr(fallback_response, 'content') else str(fallback_response)
            
            # Add transparency prefix
            transparency_prefix = "The uploaded agreement does not cover this, but typically: "
            if not content.startswith(transparency_prefix):
                content = transparency_prefix + content
            
            suggestions = []
            if document:
                suggestions = self.fallback_generator.suggest_relevant_questions(document)
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.GENERAL_KNOWLEDGE,
                confidence=intent.confidence,
                sources=["general_legal_knowledge"],
                suggestions=suggestions,
                tone=strategy.tone_preference,
                structured_format=None,
                context_used=["general_knowledge"],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error handling general knowledge question: {str(e)}")
            return self._create_simple_fallback_response(question)
    
    def _handle_casual_question(
        self,
        question: str,
        intent: QuestionIntent,
        strategy: ResponseStrategy,
        document: Optional[Document]
    ) -> EnhancedResponse:
        """Handle casual/playful questions"""
        
        try:
            # Get playful response from fallback generator
            fallback_response = self.fallback_generator.create_playful_response(question)
            content = fallback_response.content if hasattr(fallback_response, 'content') else str(fallback_response)
            
            # Add gentle redirection if document is available
            if document and "gentle_redirection" in strategy.fallback_options:
                redirection = f"\n\nIf you have questions about your contract, I'm here to help analyze it!"
                content += redirection
            
            suggestions = []
            if document:
                suggestions = self.fallback_generator.suggest_relevant_questions(document)[:2]
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.CASUAL,
                confidence=intent.confidence,
                sources=["conversational_responder"],
                suggestions=suggestions,
                tone=ToneType.CONVERSATIONAL,
                structured_format=None,
                context_used=["casual_interaction"],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error handling casual question: {str(e)}")
            return self._create_simple_fallback_response(question)
    
    def _enhance_with_mta_expertise(
        self,
        response: EnhancedResponse,
        question: str,
        document: Document,
        context: Optional[ConversationContext]
    ) -> EnhancedResponse:
        """Enhance response with MTA-specific expertise"""
        
        try:
            # Get MTA context
            mta_context = self.mta_specialist.analyze_mta_context(document)
            
            # Get MTA insights
            mta_insight = self.mta_specialist.provide_mta_expertise(question, mta_context)
            
            # Enhance response content with MTA insights
            enhanced_content = response.content
            
            # Add MTA-specific explanations if relevant
            if mta_insight.concept_explanations:
                enhanced_content += "\n\n**MTA Context:**\n"
                for concept, explanation in mta_insight.concept_explanations.items():
                    enhanced_content += f"- **{concept.title()}**: {explanation}\n"
            
            # Add research implications
            if mta_insight.research_implications:
                enhanced_content += "\n**Research Implications:**\n"
                for implication in mta_insight.research_implications:
                    enhanced_content += f"- {implication}\n"
            
            # Add MTA suggestions to response suggestions
            response.suggestions.extend(mta_insight.suggested_questions[:2])
            
            # Update response
            response.content = enhanced_content
            response.sources.append("mta_specialist")
            response.context_used.append("mta_expertise")
            
            return response
            
        except Exception as e:
            logger.error(f"Error enhancing with MTA expertise: {str(e)}")
            return response  # Return original response if enhancement fails
    
    def _enhance_response_with_context(
        self,
        response: EnhancedResponse,
        context: Optional[ConversationContext],
        document: Optional[Document]
    ) -> EnhancedResponse:
        """Add contextual enhancements to response"""
        
        if not context:
            return response
        
        try:
            # Detect conversation patterns
            patterns = self.context_manager.detect_conversation_patterns(context.session_id)
            
            # Add pattern-specific enhancements
            if "repetitive_questioning" in patterns:
                response.content += "\n\n*I notice you're asking similar questions. Would you like me to approach this from a different angle?*"
            
            if "increasing_complexity" in patterns and context.user_expertise_level == "beginner":
                response.content += "\n\n*Let me know if you'd like me to explain any of these concepts in simpler terms.*"
            
            if "high_satisfaction" in patterns:
                response.tone = "conversational"
            
            # Add conversation flow suggestions
            flow = self.context_manager.analyze_conversation_flow(context.session_id)
            if flow and flow.suggested_directions:
                if len(response.suggestions) < 3:
                    response.suggestions.extend(flow.suggested_directions[:2])
            
            response.context_used.append("conversation_patterns")
            
            return response
            
        except Exception as e:
            logger.error(f"Error enhancing response with context: {str(e)}")
            return response
    
    def _generate_contextual_suggestions(
        self,
        question: str,
        document: Optional[Document],
        context: Optional[ConversationContext]
    ) -> List[str]:
        """Generate contextual suggestions based on question and conversation"""
        
        suggestions = []
        
        try:
            # Get base suggestions from fallback generator
            if document:
                base_suggestions = self.fallback_generator.suggest_relevant_questions(document)
                suggestions.extend(base_suggestions[:2])
            
            # Add context-aware suggestions
            if context:
                context_suggestions = self.context_manager.suggest_context_aware_responses(question, context)
                # Convert response suggestions to question suggestions
                for suggestion in context_suggestions[:1]:
                    if "explore" in suggestion.lower():
                        suggestions.append(f"Can you help me {suggestion.lower()}?")
            
            # Add MTA-specific suggestions if relevant
            if document and self._is_mta_document(document):
                mta_context = self.mta_specialist.analyze_mta_context(document)
                mta_suggestions = self.mta_specialist.suggest_mta_considerations(question)
                suggestions.extend([f"What about {s.lower()}?" for s in mta_suggestions[:1]])
            
            # Remove duplicates and limit
            unique_suggestions = []
            seen = set()
            for suggestion in suggestions:
                if suggestion.lower() not in seen:
                    unique_suggestions.append(suggestion)
                    seen.add(suggestion.lower())
            
            return unique_suggestions[:3]
            
        except Exception as e:
            logger.error(f"Error generating contextual suggestions: {str(e)}")
            return suggestions[:3] if suggestions else []
    
    def _is_mta_document(self, document: Document) -> bool:
        """Check if document is likely an MTA"""
        content_lower = document.content.lower()
        mta_indicators = [
            'material transfer', 'mta', 'research material', 'biological material',
            'provider', 'recipient', 'original material', 'research use only'
        ]
        
        return any(indicator in content_lower for indicator in mta_indicators)
    
    def _contains_mta_terms(self, question: str) -> bool:
        """Check if question contains MTA-specific terms"""
        question_lower = question.lower()
        mta_terms = [
            'derivative', 'modification', 'research use', 'commercial use',
            'provider', 'recipient', 'original material', 'publication'
        ]
        
        return any(term in question_lower for term in mta_terms)
    
    def _create_error_fallback_response(self, question: str, error_message: str) -> EnhancedResponse:
        """Create a fallback response for errors"""
        content = "I apologize, but I encountered an issue processing your question. Let me try to help in a different way."
        
        # Add basic redirection
        content += "\n\nCould you try rephrasing your question, or ask about a specific aspect of the contract?"
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.FALLBACK,
            confidence=0.3,
            sources=["error_handler"],
            suggestions=[
                "What are the key terms in this contract?",
                "Are there any liability limitations?",
                "What are the termination conditions?"
            ],
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=["error_handling"],
            timestamp=datetime.now()
        )
    
    def _create_simple_fallback_response(self, question: str) -> EnhancedResponse:
        """Create a simple fallback response"""
        content = "I understand you're asking about the contract, but I need a bit more context to provide a helpful response."
        content += "\n\nCould you ask about a specific clause or aspect of the agreement?"
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.FALLBACK,
            confidence=0.4,
            sources=["simple_fallback"],
            suggestions=[
                "What does this clause mean?",
                "Are there any risks I should know about?",
                "What are my obligations under this agreement?"
            ],
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=["simple_fallback"],
            timestamp=datetime.now()
        )
    
    def _create_document_not_found_response(self, question: str, intent: QuestionIntent) -> EnhancedResponse:
        """Create response when document is not found"""
        content = "I don't have access to a document to analyze for your question. Please make sure a document has been uploaded and processed."
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.FALLBACK,
            confidence=0.3,
            sources=["document_not_found"],
            suggestions=[
                "Please upload a document first",
                "Check if the document has finished processing",
                "Try asking a general legal question instead"
            ],
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=["document_not_found"],
            timestamp=datetime.now()
        )
    
    def _create_document_analysis_fallback(self, question: str, document: Document) -> str:
        """Create a meaningful fallback response based on document content"""
        try:
            # Get document content
            content = getattr(document, 'content', None) or getattr(document, 'original_text', '')
            
            if not content:
                return "I have access to the document, but I'm having trouble analyzing its content. Could you try asking about a specific section or term?"
            
            # Simple keyword-based analysis
            question_lower = question.lower()
            content_lower = content.lower()
            
            # Look for key terms in the question
            if 'payment' in question_lower or 'pay' in question_lower:
                if 'payment' in content_lower or '$' in content or 'fee' in content_lower:
                    return "I can see this document contains payment-related terms. While I'm having trouble with detailed analysis right now, you might want to look for sections mentioning payments, fees, or financial obligations."
            
            if 'termination' in question_lower or 'terminate' in question_lower:
                if 'termination' in content_lower or 'terminate' in content_lower:
                    return "This document appears to have termination provisions. Look for sections that discuss how the agreement can be ended or what happens when it expires."
            
            if 'liability' in question_lower:
                if 'liability' in content_lower or 'damages' in content_lower:
                    return "The document contains liability-related language. Check for sections discussing damages, limitations of liability, or indemnification."
            
            if 'party' in question_lower or 'parties' in question_lower:
                return "This document involves multiple parties. Look at the beginning of the document for party definitions and throughout for their respective obligations."
            
            # Generic helpful response
            return f"I can see this is a {getattr(document, 'legal_document_type', 'legal')} document. While I'm having trouble with detailed analysis, I can help you understand specific sections if you point me to particular clauses or terms you're interested in."
            
        except Exception as e:
            logger.error(f"Error creating document analysis fallback: {e}")
            return "I'm having trouble analyzing this document right now. Could you try asking about a specific section or rephrase your question?"
    
    def _enhance_with_existing_systems(
        self,
        response: EnhancedResponse,
        question: str,
        document: Optional[Document],
        session_id: str,
        conversation_context: Optional[ConversationContext]
    ) -> EnhancedResponse:
        """
        Enhance structured response with existing systems (MTA, context, etc.).
        This method can fail without breaking the overall response.
        """
        try:
            # Try to add MTA expertise if relevant
            if document and self._is_mta_document(document):
                try:
                    mta_context = self.mta_specialist.analyze_mta_context(document)
                    mta_insight = self.mta_specialist.provide_mta_expertise(question, mta_context)
                    
                    if mta_insight.concept_explanations or mta_insight.research_implications:
                        response.content += "\n\n**MTA-Specific Context:**"
                        
                        for concept, explanation in mta_insight.concept_explanations.items():
                            response.content += f"\n- **{concept.title()}**: {explanation}"
                        
                        if mta_insight.research_implications:
                            response.content += "\n\n**Research Implications:**"
                            for implication in mta_insight.research_implications:
                                response.content += f"\n- {implication}"
                        
                        response.sources.append("mta_specialist")
                        response.context_used.append("mta_expertise")
                        
                        # Add MTA suggestions
                        response.suggestions.extend(mta_insight.suggested_questions[:2])
                        
                except Exception as mta_error:
                    logger.warning(f"MTA enhancement failed: {mta_error}")
            
            # Try to add conversation context enhancements
            if conversation_context:
                try:
                    patterns = self.context_manager.detect_conversation_patterns(session_id)
                    
                    if "repetitive_questioning" in patterns:
                        response.content += "\n\n*I notice you're exploring similar topics. Would you like me to approach this differently?*"
                    
                    if "increasing_complexity" in patterns and conversation_context.user_expertise_level == "beginner":
                        response.content += "\n\n*Let me know if you'd like me to explain any of these concepts in simpler terms.*"
                    
                    response.context_used.append("conversation_patterns")
                    
                except Exception as context_error:
                    logger.warning(f"Context enhancement failed: {context_error}")
            
            # Try to enhance suggestions with existing systems
            try:
                if document:
                    additional_suggestions = self.fallback_generator.suggest_relevant_questions(document)
                    # Add unique suggestions
                    for suggestion in additional_suggestions[:2]:
                        if suggestion not in response.suggestions:
                            response.suggestions.append(suggestion)
                    
                    # Limit total suggestions
                    response.suggestions = response.suggestions[:5]
                    
            except Exception as suggestion_error:
                logger.warning(f"Suggestion enhancement failed: {suggestion_error}")
            
            return response
            
        except Exception as e:
            logger.warning(f"Overall enhancement failed: {e}")
            return response
    
    def _create_error_recovery_response(self, question: str, intent: QuestionIntent, error_msg: str) -> EnhancedResponse:
        """Create an error recovery response that's helpful to users"""
        
        # Don't expose technical error details to users
        user_friendly_content = "I'm having some technical difficulties analyzing your question right now. Let me try to help in a different way."
        
        # Add helpful suggestions based on the question type
        suggestions = []
        question_lower = question.lower()
        
        if any(term in question_lower for term in ['payment', 'pay', 'fee', 'cost']):
            suggestions.extend([
                "What are the payment terms?",
                "When are payments due?",
                "Are there any late payment penalties?"
            ])
        elif any(term in question_lower for term in ['termination', 'terminate', 'end']):
            suggestions.extend([
                "How can this agreement be terminated?",
                "What notice is required for termination?",
                "What happens after termination?"
            ])
        elif any(term in question_lower for term in ['liability', 'damages', 'risk']):
            suggestions.extend([
                "What are the liability limitations?",
                "Who is responsible for damages?",
                "Are there any indemnification provisions?"
            ])
        else:
            suggestions.extend([
                "What are the key terms in this agreement?",
                "Who are the parties to this contract?",
                "What are the main obligations?"
            ])
        
        user_friendly_content += "\n\nHere are some questions I can definitely help with:"
        
        return EnhancedResponse(
            content=user_friendly_content,
            response_type=ResponseType.FALLBACK,
            confidence=0.5,
            sources=["error_recovery"],
            suggestions=suggestions,
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=["error_recovery"],
            timestamp=datetime.now()
        )    

    def _enhance_with_existing_systems(
        self, response: EnhancedResponse, question: str, document: Optional[Document], 
        session_id: str, conversation_context: Optional[ConversationContext]
    ) -> EnhancedResponse:
        """Enhance structured response with existing system capabilities."""
        try:
            # Add MTA expertise if applicable
            if document and self._is_mta_document(document):
                response = self._enhance_with_mta_expertise(response, question, document, conversation_context)
            
            # Add contextual enhancements
            if conversation_context:
                response = self._enhance_response_with_context(response, conversation_context, document)
            
            # Ensure suggestions are populated
            if not response.suggestions and document:
                response.suggestions = self._generate_contextual_suggestions(question, document, conversation_context)
            
            return response
            
        except Exception as e:
            logger.warning(f"Error enhancing with existing systems: {e}")
            return response