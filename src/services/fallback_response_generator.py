"""
Fallback Response Generator for Enhanced Contract Assistant.

This module provides graceful handling of off-topic, irrelevant, or playful questions
while maintaining professional tone and providing helpful redirection.
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from ..models.enhanced import (
    EnhancedResponse, ResponseType, ToneType, QuestionIntent, IntentType
)
from ..models.document import Document


@dataclass
class ResponseTemplate:
    """Template for generating fallback responses."""
    template: str
    tone: ToneType
    include_suggestions: bool = True
    redirect_to_document: bool = True


class FallbackResponseGenerator:
    """
    Generates helpful fallback responses for off-topic, irrelevant, or playful questions.
    
    This class handles questions that don't directly relate to document analysis by:
    - Gracefully acknowledging off-topic questions
    - Providing conversational responses to casual/playful questions
    - Redirecting users to relevant document topics
    - Maintaining professional tone while being helpful
    """
    
    def __init__(self):
        """Initialize the fallback response generator with templates and strategies."""
        self._off_topic_templates = self._initialize_off_topic_templates()
        self._playful_templates = self._initialize_playful_templates()
        self._redirection_templates = self._initialize_redirection_templates()
        self._general_knowledge_templates = self._initialize_general_knowledge_templates()
        
        # Common document-related question suggestions
        self._common_suggestions = [
            "What are the key terms and conditions in this agreement?",
            "What are the main obligations for each party?",
            "Are there any termination clauses I should be aware of?",
            "What are the payment terms and conditions?",
            "Are there any liability limitations or exclusions?",
            "What intellectual property rights are addressed?",
            "Are there any confidentiality or non-disclosure provisions?",
            "What are the dispute resolution mechanisms?"
        ]
    
    def generate_off_topic_response(self, question: str, document: Optional[Document] = None) -> EnhancedResponse:
        """
        Generate a graceful response for off-topic questions.
        
        Args:
            question: The off-topic question asked by the user
            document: Optional document context for generating relevant suggestions
            
        Returns:
            EnhancedResponse with graceful acknowledgment and redirection
        """
        template = random.choice(self._off_topic_templates)
        
        # Generate relevant suggestions based on document
        suggestions = self.suggest_relevant_questions(document) if document else self._common_suggestions[:3]
        
        # Format the response
        content = template.template.format(
            question_topic=self._extract_topic_from_question(question),
            suggestions_text=self._format_suggestions_text(suggestions)
        )
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.FALLBACK,
            confidence=0.8,
            suggestions=suggestions,
            tone=template.tone,
            context_used=["off_topic_handling"]
        )
    
    def create_playful_response(self, question: str) -> EnhancedResponse:
        """
        Generate a conversational response for casual or playful questions.
        
        Args:
            question: The casual/playful question asked by the user
            
        Returns:
            EnhancedResponse with appropriate conversational tone
        """
        template = random.choice(self._playful_templates)
        
        # Determine if question is a greeting, joke, or general casual comment
        question_type = self._classify_playful_question(question)
        
        # Select appropriate template based on question type
        if question_type == "greeting":
            template = next((t for t in self._playful_templates if "greeting" in t.template.lower()), template)
        elif question_type == "joke":
            template = next((t for t in self._playful_templates if "humor" in t.template.lower()), template)
        
        content = template.template.format(
            user_comment=question.strip(),
            transition_phrase=self._get_transition_phrase()
        )
        
        suggestions = [
            "Let's dive into your document - what would you like to know?",
            "I'm ready to help analyze your agreement. What's your main concern?",
            "What specific aspects of the contract are you most interested in?"
        ]
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.CASUAL,
            confidence=0.9,
            suggestions=suggestions,
            tone=ToneType.CONVERSATIONAL,
            context_used=["playful_handling", question_type]
        )
    
    def suggest_relevant_questions(self, document: Optional[Document] = None) -> List[str]:
        """
        Generate relevant document-related question suggestions.
        
        Args:
            document: Optional document to analyze for specific suggestions
            
        Returns:
            List of suggested questions relevant to the document
        """
        if not document:
            return self._common_suggestions[:5]
        
        suggestions = []
        
        # Analyze document content for specific suggestions
        if hasattr(document, 'content') and document.content:
            content_lower = document.content.lower()
            
            # Contract-specific suggestions based on content
            if 'payment' in content_lower or 'fee' in content_lower:
                suggestions.append("What are the payment terms and schedule?")
            
            if 'termination' in content_lower or 'terminate' in content_lower:
                suggestions.append("Under what conditions can this agreement be terminated?")
            
            if 'liability' in content_lower or 'damages' in content_lower:
                suggestions.append("What liability protections are included?")
            
            if 'intellectual property' in content_lower or 'ip' in content_lower:
                suggestions.append("How are intellectual property rights handled?")
            
            if 'confidential' in content_lower or 'non-disclosure' in content_lower:
                suggestions.append("What confidentiality obligations are specified?")
            
            if 'material transfer' in content_lower or 'mta' in content_lower:
                suggestions.extend([
                    "What materials are being transferred under this agreement?",
                    "What are the permitted uses of the transferred materials?",
                    "Are there any restrictions on publication or sharing of results?"
                ])
            
            # Ensure we have termination suggestion if the word appears
            if 'termination' in content_lower and not any('termination' in s.lower() for s in suggestions):
                suggestions.append("What are the termination clauses in this agreement?")
        
        # Fill remaining slots with common suggestions
        remaining_slots = 5 - len(suggestions)
        if remaining_slots > 0:
            common_to_add = [s for s in self._common_suggestions if s not in suggestions]
            suggestions.extend(common_to_add[:remaining_slots])
        
        return suggestions[:5]
    
    def generate_redirection_response(self, question: str, suggestions: List[str]) -> EnhancedResponse:
        """
        Generate a response that redirects users to relevant topics.
        
        Args:
            question: The original question that needs redirection
            suggestions: List of suggested questions to redirect to
            
        Returns:
            EnhancedResponse with helpful redirection
        """
        template = random.choice(self._redirection_templates)
        
        content = template.template.format(
            original_question=question.strip(),
            suggestions_text=self._format_suggestions_text(suggestions)
        )
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.FALLBACK,
            confidence=0.7,
            suggestions=suggestions,
            tone=template.tone,
            context_used=["redirection_handling"]
        )
    
    def create_general_knowledge_response(self, question: str, topic: str) -> EnhancedResponse:
        """
        Generate a response with general legal/contract knowledge.
        
        Args:
            question: The question asking for general knowledge
            topic: The identified topic area
            
        Returns:
            EnhancedResponse with general knowledge and transparency
        """
        template = random.choice(self._general_knowledge_templates)
        
        # Generate general knowledge based on topic
        general_info = self._get_general_knowledge(topic)
        
        content = template.template.format(
            topic=topic,
            general_info=general_info
        )
        
        suggestions = [
            f"Does your document address {topic} specifically?",
            "What specific clauses in your agreement relate to this topic?",
            "Would you like me to search for related terms in your document?"
        ]
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.GENERAL_KNOWLEDGE,
            confidence=0.6,
            suggestions=suggestions,
            tone=ToneType.PROFESSIONAL,
            context_used=["general_knowledge", topic]
        )
    
    def determine_fallback_strategy(self, intent: QuestionIntent, question: str) -> str:
        """
        Determine the best fallback strategy based on question intent.
        
        Args:
            intent: Classified intent of the question
            question: The original question text
            
        Returns:
            Strategy name for handling the fallback
        """
        if intent.primary_intent == IntentType.CASUAL:
            if intent.casualness_level > 0.7:
                return "playful_response"
            else:
                return "conversational_response"
        
        elif intent.primary_intent == IntentType.OFF_TOPIC:
            if intent.document_relevance_score > 0.3:
                return "redirection_with_suggestions"
            else:
                return "graceful_acknowledgment"
        
        elif intent.primary_intent == IntentType.CONTRACT_GENERAL:
            return "general_knowledge_response"
        
        else:
            return "default_redirection"
    
    def _initialize_off_topic_templates(self) -> List[ResponseTemplate]:
        """Initialize templates for off-topic responses."""
        return [
            ResponseTemplate(
                template="I appreciate your question about {question_topic}, but I'm specifically designed to help analyze contracts and legal documents. Let me suggest some questions that might be more relevant to your uploaded document:\n\n{suggestions_text}",
                tone=ToneType.PROFESSIONAL
            ),
            ResponseTemplate(
                template="That's an interesting question about {question_topic}! While I focus on contract analysis, I'd be happy to help you explore your document instead. Here are some questions I can definitely help with:\n\n{suggestions_text}",
                tone=ToneType.CONVERSATIONAL
            ),
            ResponseTemplate(
                template="I understand you're curious about {question_topic}, but my expertise is in analyzing legal agreements and contracts. I'd love to help you understand your document better with questions like:\n\n{suggestions_text}",
                tone=ToneType.PROFESSIONAL
            )
        ]
    
    def _initialize_playful_templates(self) -> List[ResponseTemplate]:
        """Initialize templates for playful/casual responses."""
        return [
            ResponseTemplate(
                template="Hello there! I appreciate the friendly greeting. I'm here and ready to help you analyze your contract or legal document. {transition_phrase}",
                tone=ToneType.CONVERSATIONAL
            ),
            ResponseTemplate(
                template="I enjoy a bit of humor too! While I might not be the best at jokes, I'm quite good at breaking down complex legal language. {transition_phrase}",
                tone=ToneType.CONVERSATIONAL
            ),
            ResponseTemplate(
                template="Thanks for the casual chat! I'm designed to be helpful with contract analysis, so let's put my skills to good use. {transition_phrase}",
                tone=ToneType.CONVERSATIONAL
            ),
            ResponseTemplate(
                template="I appreciate the friendly conversation! Now, let's focus on what I do best - helping you understand your legal documents. {transition_phrase}",
                tone=ToneType.CONVERSATIONAL
            )
        ]
    
    def _initialize_redirection_templates(self) -> List[ResponseTemplate]:
        """Initialize templates for redirection responses."""
        return [
            ResponseTemplate(
                template="I understand you're asking about '{original_question}', but I can provide more valuable insights by focusing on your document. Here are some questions that would help us dive deeper:\n\n{suggestions_text}",
                tone=ToneType.PROFESSIONAL
            ),
            ResponseTemplate(
                template="While '{original_question}' is a valid concern, I can offer more specific help by analyzing your actual document. Let's explore these relevant questions:\n\n{suggestions_text}",
                tone=ToneType.PROFESSIONAL
            )
        ]
    
    def _initialize_general_knowledge_templates(self) -> List[ResponseTemplate]:
        """Initialize templates for general knowledge responses."""
        return [
            ResponseTemplate(
                template="The uploaded agreement does not cover this specifically, but typically {general_info}\n\nFor your specific situation, I'd recommend checking your document directly. Here are some targeted questions that might help:",
                tone=ToneType.PROFESSIONAL
            ),
            ResponseTemplate(
                template="While I can't see specific details about {topic} in your uploaded document, I can share that generally {general_info}\n\nTo get more precise information about your agreement:",
                tone=ToneType.PROFESSIONAL
            )
        ]
    
    def _extract_topic_from_question(self, question: str) -> str:
        """Extract the main topic from a question for response formatting."""
        # Simple topic extraction - could be enhanced with NLP
        question_lower = question.lower().strip()
        
        # Remove question words and common words
        stop_words = ['what', 'how', 'why', 'when', 'where', 'who', 'is', 'are', 'can', 'could', 'would', 'should', 'the', 'a', 'an', 'this', 'that']
        
        # Filter out inappropriate or negative words
        inappropriate_words = ['stupid', 'dumb', 'idiotic', 'terrible', 'awful', 'horrible', 'bad', 'worst', 'hate', 'sucks']
        
        words = question_lower.split()
        
        # Filter out stop words, inappropriate words, and keep meaningful words
        meaningful_words = [word for word in words 
                          if word not in stop_words 
                          and word not in inappropriate_words 
                          and len(word) > 2]
        
        # Take first few meaningful words, or fall back to generic topic
        if meaningful_words:
            topic = ' '.join(meaningful_words[:3])
            # If the topic is still problematic, use generic fallback
            if any(bad_word in topic for bad_word in inappropriate_words):
                return "that topic"
            return topic
        else:
            return "that topic"
    
    def _format_suggestions_text(self, suggestions: List[str]) -> str:
        """Format a list of suggestions into readable text."""
        if not suggestions:
            return "• What are the key terms in this agreement?"
        
        formatted = []
        for i, suggestion in enumerate(suggestions[:5], 1):
            formatted.append(f"• {suggestion}")
        
        return '\n'.join(formatted)
    
    def _classify_playful_question(self, question: str) -> str:
        """Classify the type of playful question."""
        question_lower = question.lower().strip()
        
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(greeting in question_lower for greeting in greetings):
            return "greeting"
        
        humor_indicators = ['joke', 'funny', 'laugh', 'haha', 'lol', '😄', '😊', '🙂']
        if any(indicator in question_lower for indicator in humor_indicators):
            return "joke"
        
        return "casual"
    
    def _get_transition_phrase(self) -> str:
        """Get a random transition phrase for moving to document analysis."""
        phrases = [
            "What would you like to know about your document?",
            "Let's explore your agreement together.",
            "I'm ready to help analyze your contract.",
            "What aspects of your document interest you most?",
            "How can I help you understand your agreement better?"
        ]
        return random.choice(phrases)
    
    def _get_general_knowledge(self, topic: str) -> str:
        """Get general knowledge information for a given topic."""
        knowledge_base = {
            "payment": "payment terms usually specify amounts, due dates, and acceptable payment methods",
            "termination": "termination clauses typically outline conditions for ending the agreement and notice requirements",
            "liability": "liability provisions often include limitations, exclusions, and indemnification terms",
            "intellectual property": "IP clauses address ownership, licensing, and protection of intellectual property rights",
            "confidentiality": "confidentiality provisions establish obligations to protect sensitive information",
            "dispute resolution": "dispute resolution mechanisms commonly include negotiation, mediation, or arbitration procedures",
            "force majeure": "force majeure clauses excuse performance when extraordinary circumstances prevent fulfillment",
            "governing law": "governing law provisions specify which jurisdiction's laws apply to the agreement"
        }
        
        topic_lower = topic.lower()
        for key, info in knowledge_base.items():
            if key in topic_lower:
                return info
        
        return f"agreements commonly address {topic} through specific contractual provisions"