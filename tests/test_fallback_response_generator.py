"""
Tests for the FallbackResponseGenerator class.

This module tests the fallback response generation system for appropriateness,
tone consistency, and proper handling of different question types.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.fallback_response_generator import FallbackResponseGenerator, ResponseTemplate
from src.models.enhanced import (
    EnhancedResponse, ResponseType, ToneType, QuestionIntent, IntentType
)
from src.models.document import Document


class TestFallbackResponseGenerator:
    """Test cases for the FallbackResponseGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = FallbackResponseGenerator()
        
        # Mock document for testing
        self.mock_document = Mock(spec=Document)
        self.mock_document.content = """
        This Material Transfer Agreement governs the transfer of research materials
        between Provider and Recipient. Payment terms require monthly fees.
        Termination may occur with 30 days notice. Confidentiality obligations
        apply to all shared information.
        """
        self.mock_document.id = "test_doc_123"
    
    def test_generate_off_topic_response_basic(self):
        """Test basic off-topic response generation."""
        question = "What's the weather like today?"
        
        response = self.generator.generate_off_topic_response(question)
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.FALLBACK
        assert response.confidence == 0.8
        assert len(response.suggestions) > 0
        assert response.tone in [ToneType.PROFESSIONAL, ToneType.CONVERSATIONAL]
        assert "weather" in response.content.lower() or "that topic" in response.content.lower()
        assert "contract" in response.content.lower() or "document" in response.content.lower()
    
    def test_generate_off_topic_response_with_document(self):
        """Test off-topic response generation with document context."""
        question = "How do I cook pasta?"
        
        response = self.generator.generate_off_topic_response(question, self.mock_document)
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.FALLBACK
        assert len(response.suggestions) > 0
        assert any("payment" in suggestion.lower() for suggestion in response.suggestions)
        assert "cook" in response.content.lower() or "pasta" in response.content.lower()
    
    def test_create_playful_response_greeting(self):
        """Test playful response for greeting questions."""
        question = "Hello there!"
        
        response = self.generator.create_playful_response(question)
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.CASUAL
        assert response.confidence == 0.9
        assert response.tone == ToneType.CONVERSATIONAL
        assert len(response.suggestions) > 0
        assert "hello" in response.content.lower() or "greeting" in response.content.lower()
        assert "document" in response.content.lower() or "contract" in response.content.lower()
    
    def test_create_playful_response_humor(self):
        """Test playful response for humorous questions."""
        question = "Tell me a joke!"
        
        response = self.generator.create_playful_response(question)
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.CASUAL
        assert response.tone == ToneType.CONVERSATIONAL
        assert "joke" in response.content.lower() or "humor" in response.content.lower()
        assert len(response.suggestions) > 0
    
    def test_create_playful_response_casual(self):
        """Test playful response for general casual questions."""
        question = "How are you doing?"
        
        response = self.generator.create_playful_response(question)
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.CASUAL
        assert response.tone == ToneType.CONVERSATIONAL
        assert len(response.suggestions) > 0
        assert any("document" in suggestion.lower() for suggestion in response.suggestions)
    
    def test_suggest_relevant_questions_no_document(self):
        """Test question suggestions without document context."""
        suggestions = self.generator.suggest_relevant_questions()
        
        assert isinstance(suggestions, list)
        assert len(suggestions) == 5
        assert all(isinstance(s, str) for s in suggestions)
        assert any("terms" in s.lower() for s in suggestions)
        assert any("obligations" in s.lower() for s in suggestions)
    
    def test_suggest_relevant_questions_with_document(self):
        """Test question suggestions with document context."""
        suggestions = self.generator.suggest_relevant_questions(self.mock_document)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) == 5
        assert any("payment" in s.lower() for s in suggestions)
        assert any("terminat" in s.lower() for s in suggestions)  # matches both "termination" and "terminated"
        assert any("confidential" in s.lower() for s in suggestions)
    
    def test_suggest_relevant_questions_mta_document(self):
        """Test question suggestions for MTA documents."""
        mta_doc = Mock(spec=Document)
        mta_doc.content = """
        Material Transfer Agreement for research materials.
        Intellectual property rights reserved by Provider.
        """
        
        suggestions = self.generator.suggest_relevant_questions(mta_doc)
        
        assert len(suggestions) == 5
        assert any("material" in s.lower() for s in suggestions)
        assert any("intellectual property" in s.lower() for s in suggestions)
    
    def test_generate_redirection_response(self):
        """Test redirection response generation."""
        question = "I'm confused about this whole thing"
        suggestions = ["What are the key terms?", "Who are the parties involved?"]
        
        response = self.generator.generate_redirection_response(question, suggestions)
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.FALLBACK
        assert response.confidence == 0.7
        assert response.suggestions == suggestions
        assert "confused" in response.content.lower()
        assert len(response.suggestions) > 0
    
    def test_create_general_knowledge_response(self):
        """Test general knowledge response generation."""
        question = "What are typical payment terms?"
        topic = "payment"
        
        response = self.generator.create_general_knowledge_response(question, topic)
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.GENERAL_KNOWLEDGE
        assert response.confidence == 0.6
        assert response.tone == ToneType.PROFESSIONAL
        assert "payment" in response.content.lower()
        # Check for either template's transparency language
        assert ("uploaded agreement does not cover" in response.content.lower() or 
                "can't see specific details" in response.content.lower())
        assert len(response.suggestions) > 0
    
    def test_determine_fallback_strategy_casual(self):
        """Test fallback strategy determination for casual questions."""
        intent = QuestionIntent(
            primary_intent=IntentType.CASUAL,
            confidence=0.8,
            casualness_level=0.9
        )
        
        strategy = self.generator.determine_fallback_strategy(intent, "Hey there!")
        
        assert strategy == "playful_response"
    
    def test_determine_fallback_strategy_off_topic(self):
        """Test fallback strategy determination for off-topic questions."""
        intent = QuestionIntent(
            primary_intent=IntentType.OFF_TOPIC,
            confidence=0.7,
            document_relevance_score=0.1
        )
        
        strategy = self.generator.determine_fallback_strategy(intent, "What's for lunch?")
        
        assert strategy == "graceful_acknowledgment"
    
    def test_determine_fallback_strategy_contract_general(self):
        """Test fallback strategy determination for general contract questions."""
        intent = QuestionIntent(
            primary_intent=IntentType.CONTRACT_GENERAL,
            confidence=0.6
        )
        
        strategy = self.generator.determine_fallback_strategy(intent, "What are force majeure clauses?")
        
        assert strategy == "general_knowledge_response"
    
    def test_response_tone_consistency(self):
        """Test that responses maintain consistent tone within categories."""
        # Test multiple off-topic responses
        off_topic_questions = [
            "What's the weather?",
            "How do I cook dinner?",
            "What's your favorite movie?"
        ]
        
        tones = []
        for question in off_topic_questions:
            response = self.generator.generate_off_topic_response(question)
            tones.append(response.tone)
        
        # All off-topic responses should use professional or conversational tone
        assert all(tone in [ToneType.PROFESSIONAL, ToneType.CONVERSATIONAL] for tone in tones)
    
    def test_response_appropriateness_professional_context(self):
        """Test that responses are appropriate for professional legal context."""
        question = "This contract is stupid"
        
        response = self.generator.generate_off_topic_response(question)
        
        # Response should remain professional despite negative input
        assert response.tone in [ToneType.PROFESSIONAL, ToneType.CONVERSATIONAL]
        assert "stupid" not in response.content.lower()
        assert len(response.suggestions) > 0
    
    def test_suggestion_quality_and_relevance(self):
        """Test that suggestions are high-quality and relevant."""
        suggestions = self.generator.suggest_relevant_questions(self.mock_document)
        
        # All suggestions should be questions
        assert all(s.endswith('?') for s in suggestions)
        
        # Suggestions should be relevant to contracts
        contract_terms = ['terms', 'obligations', 'payment', 'termination', 'liability', 'rights']
        assert any(any(term in s.lower() for term in contract_terms) for s in suggestions)
        
        # Suggestions should be actionable
        assert all(len(s.split()) >= 4 for s in suggestions)  # Reasonable length
    
    def test_graceful_handling_of_empty_inputs(self):
        """Test graceful handling of edge cases and empty inputs."""
        # Empty question
        response = self.generator.generate_off_topic_response("")
        assert isinstance(response, EnhancedResponse)
        assert len(response.content) > 0
        
        # Very short question
        response = self.generator.create_playful_response("Hi")
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.CASUAL
    
    def test_context_tracking_in_responses(self):
        """Test that responses include appropriate context information."""
        question = "What's for dinner?"
        
        response = self.generator.generate_off_topic_response(question, self.mock_document)
        
        assert "off_topic_handling" in response.context_used
        assert isinstance(response.context_used, list)
        assert len(response.context_used) > 0
    
    def test_template_variety(self):
        """Test that the generator uses variety in response templates."""
        question = "What's the weather?"
        responses = []
        
        # Generate multiple responses to test template variety
        for _ in range(10):
            response = self.generator.generate_off_topic_response(question)
            responses.append(response.content)
        
        # Should have some variety in responses (not all identical)
        unique_responses = set(responses)
        assert len(unique_responses) > 1  # At least some variety
    
    def test_mta_specific_suggestions(self):
        """Test that MTA documents get MTA-specific suggestions."""
        mta_doc = Mock(spec=Document)
        mta_doc.content = "Material Transfer Agreement between Provider and Recipient"
        
        suggestions = self.generator.suggest_relevant_questions(mta_doc)
        
        mta_keywords = ['material', 'transfer', 'research', 'publication']
        assert any(any(keyword in s.lower() for keyword in mta_keywords) for s in suggestions)
    
    def test_response_length_appropriateness(self):
        """Test that responses are appropriately sized - not too short or too long."""
        question = "Hello there, how are you doing today?"
        
        response = self.generator.create_playful_response(question)
        
        # Response should be substantial but not overwhelming
        word_count = len(response.content.split())
        assert 10 <= word_count <= 100  # Reasonable range
        
        # Should include suggestions
        assert len(response.suggestions) >= 2
    
    def test_error_handling_malformed_input(self):
        """Test handling of malformed or unusual input."""
        unusual_inputs = [
            "???",
            "123456789",
            "!@#$%^&*()",
            "a" * 1000,  # Very long input
        ]
        
        for unusual_input in unusual_inputs:
            response = self.generator.generate_off_topic_response(unusual_input)
            assert isinstance(response, EnhancedResponse)
            assert len(response.content) > 0
            assert response.response_type == ResponseType.FALLBACK


class TestResponseTemplate:
    """Test cases for the ResponseTemplate class."""
    
    def test_response_template_creation(self):
        """Test ResponseTemplate creation and attributes."""
        template = ResponseTemplate(
            template="Hello {name}!",
            tone=ToneType.CONVERSATIONAL,
            include_suggestions=True,
            redirect_to_document=False
        )
        
        assert template.template == "Hello {name}!"
        assert template.tone == ToneType.CONVERSATIONAL
        assert template.include_suggestions is True
        assert template.redirect_to_document is False
    
    def test_response_template_defaults(self):
        """Test ResponseTemplate default values."""
        template = ResponseTemplate(
            template="Test template",
            tone=ToneType.PROFESSIONAL
        )
        
        assert template.include_suggestions is True
        assert template.redirect_to_document is True


class TestFallbackResponseIntegration:
    """Integration tests for fallback response generation."""
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.generator = FallbackResponseGenerator()
    
    def test_end_to_end_off_topic_flow(self):
        """Test complete off-topic question handling flow."""
        question = "What's the best pizza place in town?"
        
        # Simulate the complete flow
        response = self.generator.generate_off_topic_response(question)
        
        # Verify complete response structure
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == ResponseType.FALLBACK
        assert response.confidence > 0
        assert len(response.suggestions) > 0
        assert response.tone in [ToneType.PROFESSIONAL, ToneType.CONVERSATIONAL]
        assert isinstance(response.context_used, list)
        assert len(response.context_used) > 0
        
        # Verify content quality
        assert "pizza" in response.content.lower() or "that topic" in response.content.lower()
        assert any("contract" in response.content.lower() or "document" in response.content.lower() 
                  for _ in [response.content])
    
    def test_end_to_end_playful_flow(self):
        """Test complete playful question handling flow."""
        question = "Hey! How's it going? 😊"
        
        response = self.generator.create_playful_response(question)
        
        # Verify response appropriateness
        assert response.response_type == ResponseType.CASUAL
        assert response.tone == ToneType.CONVERSATIONAL
        assert len(response.suggestions) >= 2
        
        # Verify professional transition
        assert any("document" in s.lower() or "contract" in s.lower() 
                  for s in response.suggestions)
    
    def test_strategy_determination_accuracy(self):
        """Test that strategy determination works correctly for various intents."""
        test_cases = [
            (IntentType.CASUAL, 0.8, "playful_response"),
            (IntentType.OFF_TOPIC, 0.1, "graceful_acknowledgment"),
            (IntentType.CONTRACT_GENERAL, 0.6, "general_knowledge_response"),
        ]
        
        for intent_type, relevance_score, expected_strategy in test_cases:
            intent = QuestionIntent(
                primary_intent=intent_type,
                confidence=0.7,
                document_relevance_score=relevance_score,
                casualness_level=0.8 if intent_type == IntentType.CASUAL else 0.2
            )
            
            strategy = self.generator.determine_fallback_strategy(intent, "test question")
            assert strategy == expected_strategy