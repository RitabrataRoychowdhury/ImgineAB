"""
Tests for ConversationalAIEngine functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.conversational_ai_engine import ConversationalAIEngine
from src.models.conversational import (
    QuestionType, CompoundResponse, ConversationalResponse,
    ConversationContext, ConversationTurn
)


class TestConversationalAIEngine:
    """Test suite for ConversationalAIEngine."""
    
    @pytest.fixture
    def mock_qa_engine(self):
        """Mock QA engine."""
        engine = Mock()
        engine.answer_question.return_value = {
            'answer': 'Test answer',
            'sources': ['source1'],
            'confidence': 0.8
        }
        return engine
    
    @pytest.fixture
    def mock_contract_engine(self):
        """Mock contract analyst engine."""
        engine = Mock()
        engine.analyze_contract_query.return_value = {
            'answer': 'Legal analysis answer',
            'sources': ['legal_source1'],
            'confidence': 0.9
        }
        return engine
    
    @pytest.fixture
    def conversational_engine(self, mock_qa_engine, mock_contract_engine):
        """Create ConversationalAIEngine instance."""
        return ConversationalAIEngine(mock_qa_engine, mock_contract_engine)

    def test_classify_question_type_casual(self, conversational_engine):
        """Test classification of casual questions."""
        question = "Hello, how are you today?"
        question_type = conversational_engine.classify_question_type(question, [])
        
        assert question_type.primary_type == "casual"
        assert question_type.confidence > 0.4
        assert "casual" in question_type.sub_types
        assert not question_type.requires_legal_analysis

    def test_classify_question_type_legal(self, conversational_engine):
        """Test classification of legal questions."""
        question = "What are the liability clauses in this contract?"
        question_type = conversational_engine.classify_question_type(question, [])
        
        assert question_type.primary_type == "legal"
        assert question_type.confidence > 0.5
        assert "legal" in question_type.sub_types
        assert question_type.requires_legal_analysis

    def test_classify_question_type_compound(self, conversational_engine):
        """Test classification of compound questions."""
        question = "What are the risks and what are the commitments and also tell me about the deadlines?"
        question_type = conversational_engine.classify_question_type(question, [])
        
        assert question_type.primary_type == "compound"
        assert question_type.confidence > 0.6
        assert "compound" in question_type.sub_types

    def test_handle_compound_question(self, conversational_engine):
        """Test handling of compound questions."""
        question = "What are the risks and what are the key terms?"
        document_id = "doc123"
        session_id = "session123"
        
        response = conversational_engine.handle_compound_question(question, document_id, session_id)
        
        assert isinstance(response, CompoundResponse)
        assert len(response.question_parts) >= 2
        assert len(response.individual_responses) >= 2
        assert response.synthesized_response
        assert isinstance(response.sources, list)
        assert isinstance(response.analysis_modes_used, list)

    def test_manage_conversation_context_new_session(self, conversational_engine):
        """Test conversation context management for new session."""
        session_id = "new_session"
        question = "Hello"
        response = "Hi there!"
        
        conversational_engine.manage_conversation_context(session_id, question, response)
        
        assert session_id in conversational_engine.conversation_contexts
        context = conversational_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 1
        assert context.conversation_history[0].question == question
        assert context.conversation_history[0].response == response

    def test_manage_conversation_context_existing_session(self, conversational_engine):
        """Test conversation context management for existing session."""
        session_id = "existing_session"
        
        # Add initial context
        conversational_engine.conversation_contexts[session_id] = ConversationContext(
            session_id=session_id,
            document_id="doc123",
            conversation_history=[],
            current_topic="",
            analysis_mode="casual",
            user_preferences={},
            context_summary=""
        )
        
        question = "What about the risks?"
        response = "Here are the risks..."
        
        conversational_engine.manage_conversation_context(session_id, question, response)
        
        context = conversational_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 1
        assert context.current_topic  # Should be updated with keywords

    def test_generate_clarification_request(self, conversational_engine):
        """Test clarification request generation."""
        ambiguous_question = "What about this?"
        
        clarification = conversational_engine.generate_clarification_request(ambiguous_question)
        
        assert isinstance(clarification, str)
        assert len(clarification) > 0
        assert "?" in clarification

    def test_switch_analysis_mode_to_legal(self, conversational_engine):
        """Test switching to legal analysis mode."""
        current_mode = "casual"
        question = "What are the contract obligations?"
        document = Mock()
        
        new_mode = conversational_engine.switch_analysis_mode(current_mode, question, document)
        
        assert new_mode == "legal"

    def test_switch_analysis_mode_to_casual(self, conversational_engine):
        """Test switching to casual analysis mode."""
        current_mode = "legal"
        question = "Thanks for the help!"
        document = Mock()
        
        new_mode = conversational_engine.switch_analysis_mode(current_mode, question, document)
        
        assert new_mode == "casual"

    def test_answer_conversational_question_casual(self, conversational_engine, mock_qa_engine):
        """Test answering casual conversational questions."""
        question = "Hello, can you help me?"
        document_id = "doc123"
        session_id = "session123"
        
        response = conversational_engine.answer_conversational_question(question, document_id, session_id)
        
        assert isinstance(response, ConversationalResponse)
        assert response.answer
        assert response.conversation_tone in ["professional", "casual", "technical"]
        assert response.analysis_mode
        assert isinstance(response.confidence, float)
        assert isinstance(response.follow_up_suggestions, list)
        
        # Verify QA engine was called (may be called multiple times for compound questions)
        assert mock_qa_engine.answer_question.call_count >= 1

    def test_answer_conversational_question_legal(self, conversational_engine, mock_contract_engine):
        """Test answering legal conversational questions."""
        question = "What are the liability clauses in this contract?"
        document_id = "doc123"
        session_id = "session123"
        
        response = conversational_engine.answer_conversational_question(question, document_id, session_id)
        
        assert isinstance(response, ConversationalResponse)
        assert response.answer
        assert response.analysis_mode == "legal"
        
        # Verify contract engine was called
        mock_contract_engine.analyze_contract_query.assert_called_once()

    def test_answer_conversational_question_compound(self, conversational_engine):
        """Test answering compound conversational questions."""
        question = "What are the risks and what are the key commitments and also tell me about the deadlines?"
        document_id = "doc123"
        session_id = "session123"
        
        response = conversational_engine.answer_conversational_question(question, document_id, session_id)
        
        assert isinstance(response, ConversationalResponse)
        assert response.answer
        assert response.analysis_mode == "compound"

    def test_context_history_limit(self, conversational_engine):
        """Test that conversation history is limited to prevent memory issues."""
        session_id = "test_session"
        
        # Add many conversation turns
        for i in range(60):  # More than the 50 limit
            question = f"Question {i}"
            response = f"Response {i}"
            conversational_engine.manage_conversation_context(session_id, question, response)
        
        context = conversational_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 50  # Should be limited to 50

    def test_extract_keywords(self, conversational_engine):
        """Test keyword extraction from text."""
        text = "What are the contract liability clauses and warranty terms?"
        
        keywords = conversational_engine._extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 3  # Should return max 3 keywords
        # Should contain relevant words, not stop words
        for keyword in keywords:
            assert keyword not in ['what', 'are', 'the', 'and']

    def test_generate_context_summary_empty_history(self, conversational_engine):
        """Test context summary generation with empty history."""
        context = ConversationContext(
            session_id="test",
            document_id="doc123",
            conversation_history=[],
            current_topic="",
            analysis_mode="casual",
            user_preferences={},
            context_summary=""
        )
        
        summary = conversational_engine._generate_context_summary(context)
        
        assert summary == "New conversation"

    def test_generate_context_summary_with_history(self, conversational_engine):
        """Test context summary generation with conversation history."""
        turns = [
            ConversationTurn(
                turn_id="1",
                question="What are the contract terms?",
                response="Here are the terms...",
                question_type=QuestionType("legal", 0.8, ["legal"], True, False),
                analysis_mode="legal",
                sources_used=[],
                timestamp=datetime.now()
            )
        ]
        
        context = ConversationContext(
            session_id="test",
            document_id="doc123",
            conversation_history=turns,
            current_topic="",
            analysis_mode="legal",
            user_preferences={},
            context_summary=""
        )
        
        summary = conversational_engine._generate_context_summary(context)
        
        assert "Recent topics:" in summary
        assert "contract" in summary.lower()

    def test_error_handling_in_legal_question(self, conversational_engine, mock_contract_engine):
        """Test error handling when legal analysis fails."""
        mock_contract_engine.analyze_contract_query.side_effect = Exception("API Error")
        
        question = "What are the legal obligations?"
        document_id = "doc123"
        session_id = "session123"
        
        response = conversational_engine._handle_legal_question(question, document_id, session_id)
        
        assert isinstance(response, ConversationalResponse)
        assert response.analysis_mode == "legal"
        assert response.confidence == 0.0
        assert "issue" in response.answer.lower()

    def test_error_handling_in_casual_question(self, conversational_engine, mock_qa_engine):
        """Test error handling when casual analysis fails."""
        mock_qa_engine.answer_question.side_effect = Exception("Engine Error")
        
        question = "Hello there"
        document_id = "doc123"
        session_id = "session123"
        
        response = conversational_engine._handle_casual_question(question, document_id, session_id)
        
        assert isinstance(response, ConversationalResponse)
        assert response.analysis_mode == "casual"
        assert response.confidence == 0.0
        assert "trouble" in response.answer.lower()

    def test_synthesize_compound_response_empty(self, conversational_engine):
        """Test synthesizing compound response with empty input."""
        individual_responses = []
        
        result = conversational_engine._synthesize_compound_response(individual_responses)
        
        assert "wasn't able to process" in result

    def test_synthesize_compound_response_multiple(self, conversational_engine):
        """Test synthesizing compound response with multiple parts."""
        individual_responses = [
            {
                'question': 'What are the risks?',
                'response': 'Here are the risks...',
                'mode': 'legal',
                'confidence': 0.8
            },
            {
                'question': 'What are the terms?',
                'response': 'Here are the terms...',
                'mode': 'legal',
                'confidence': 0.9
            }
        ]
        
        result = conversational_engine._synthesize_compound_response(individual_responses)
        
        assert "Here's what I found for each part" in result
        assert "1. Regarding 'What are the risks?'" in result
        assert "2. Regarding 'What are the terms?'" in result
        assert "Let me know if you'd like me to elaborate" in result

    def test_follow_up_suggestions_generation(self, conversational_engine):
        """Test generation of follow-up suggestions."""
        question = "What are the contract terms?"
        
        # Test general follow-ups
        general_suggestions = conversational_engine._generate_follow_up_suggestions(question)
        assert isinstance(general_suggestions, list)
        assert len(general_suggestions) > 0
        
        # Test legal follow-ups
        legal_suggestions = conversational_engine._generate_legal_follow_ups(question)
        assert isinstance(legal_suggestions, list)
        assert any("legal" in suggestion.lower() for suggestion in legal_suggestions)
        
        # Test casual follow-ups
        casual_suggestions = conversational_engine._generate_casual_follow_ups(question)
        assert isinstance(casual_suggestions, list)
        assert len(casual_suggestions) > 0