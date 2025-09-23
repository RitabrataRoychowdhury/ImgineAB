"""
Integration tests for enhanced contract assistant system.

Tests the integration between the enhanced response router, contract analyst engine,
and Q&A interface to ensure backward compatibility and proper functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.enhanced_response_router import EnhancedResponseRouter
from src.services.contract_analyst_engine import ContractAnalystEngine
from src.ui.qa_interface import EnhancedQAInterface
from src.models.enhanced import EnhancedResponse, QuestionIntent, IntentType, ToneType
from src.models.document import Document
from src.storage.document_storage import DocumentStorage


class TestEnhancedIntegration:
    """Test enhanced system integration with existing components."""
    
    @pytest.fixture
    def mock_storage(self):
        """Create mock storage for testing."""
        storage = Mock(spec=DocumentStorage)
        
        # Mock document
        mock_document = Mock(spec=Document)
        mock_document.id = "test_doc_1"
        mock_document.title = "Test Contract"
        mock_document.content = "This is a test contract with liability and termination clauses."
        mock_document.original_text = mock_document.content
        mock_document.is_legal_document = True
        mock_document.legal_document_type = "Contract"
        
        storage.get_document_with_embeddings.return_value = mock_document
        storage.add_qa_interaction.return_value = None
        
        return storage
    
    @pytest.fixture
    def enhanced_router(self, mock_storage):
        """Create enhanced response router for testing."""
        return EnhancedResponseRouter(mock_storage, "test_api_key")
    
    @pytest.fixture
    def contract_engine(self, mock_storage):
        """Create contract analyst engine for testing."""
        return ContractAnalystEngine(mock_storage, "test_api_key")
    
    def test_enhanced_router_initialization(self, enhanced_router):
        """Test that enhanced router initializes properly."""
        assert enhanced_router is not None
        assert enhanced_router.question_classifier is not None
        assert enhanced_router.fallback_generator is not None
        assert enhanced_router.mta_specialist is not None
        assert enhanced_router.context_manager is not None
        assert enhanced_router.contract_engine is not None
    
    def test_contract_engine_analyze_question_method(self, contract_engine, mock_storage):
        """Test that contract engine has the new analyze_question method."""
        # Mock the necessary methods
        with patch.object(contract_engine, 'find_legal_context') as mock_context, \
             patch.object(contract_engine, 'generate_contract_analysis') as mock_analysis:
            
            # Setup mocks
            mock_context.return_value = [{'text': 'test context', 'relevance_score': 0.8}]
            
            mock_analysis_result = Mock()
            mock_analysis_result.direct_evidence = "Test evidence"
            mock_analysis_result.plain_explanation = "Test explanation"
            mock_analysis_result.implication_analysis = "Test analysis"
            mock_analysis_result.sources = ["Test source"]
            mock_analysis_result.confidence = 0.8
            mock_analysis_result.document_type = "Contract"
            mock_analysis_result.legal_terms_found = ["liability"]
            
            mock_analysis.return_value = mock_analysis_result
            
            # Test the method
            result = contract_engine.analyze_question("What is the liability clause?", "test_doc_1")
            
            # Verify result structure
            assert 'response' in result
            assert 'direct_evidence' in result
            assert 'plain_explanation' in result
            assert 'sources' in result
            assert 'confidence' in result
            assert result['confidence'] == 0.8
    
    def test_enhanced_router_document_related_question(self, enhanced_router, mock_storage):
        """Test enhanced router handling document-related questions."""
        # Mock document
        mock_document = mock_storage.get_document_with_embeddings.return_value
        
        # Mock contract engine response
        with patch.object(enhanced_router.contract_engine, 'analyze_question') as mock_analyze:
            mock_analyze.return_value = {
                'response': 'Test contract analysis response',
                'direct_evidence': 'Test evidence',
                'plain_explanation': 'Test explanation',
                'sources': ['Test source'],
                'confidence': 0.8
            }
            
            # Test routing
            response = enhanced_router.route_question(
                "What are the liability terms?",
                "test_doc_1",
                "test_session_1",
                mock_document
            )
            
            # Verify response
            assert isinstance(response, EnhancedResponse)
            assert response.content is not None
            assert response.response_type == "document_analysis"
            assert response.confidence > 0
            assert len(response.sources) > 0
    
    def test_enhanced_router_off_topic_question(self, enhanced_router, mock_storage):
        """Test enhanced router handling off-topic questions."""
        mock_document = mock_storage.get_document_with_embeddings.return_value
        
        # Test off-topic question
        response = enhanced_router.route_question(
            "What's the weather like today?",
            "test_doc_1",
            "test_session_1",
            mock_document
        )
        
        # Verify fallback response
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "fallback"
        assert "weather" in response.content.lower() or "topic" in response.content.lower()
        assert len(response.suggestions) > 0
    
    def test_enhanced_router_casual_question(self, enhanced_router, mock_storage):
        """Test enhanced router handling casual questions."""
        mock_document = mock_storage.get_document_with_embeddings.return_value
        
        # Test casual question
        response = enhanced_router.route_question(
            "Hi there! How are you doing?",
            "test_doc_1",
            "test_session_1",
            mock_document
        )
        
        # Verify casual response
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "casual"
        assert response.tone == "conversational"
        assert len(response.suggestions) > 0
    
    def test_enhanced_router_general_knowledge_question(self, enhanced_router, mock_storage):
        """Test enhanced router handling general legal knowledge questions."""
        mock_document = mock_storage.get_document_with_embeddings.return_value
        
        # Test general knowledge question
        response = enhanced_router.route_question(
            "What is a liability clause?",
            "test_doc_1",
            "test_session_1",
            mock_document
        )
        
        # Verify general knowledge response
        assert isinstance(response, EnhancedResponse)
        assert response.response_type in ["general_knowledge", "document_analysis"]
        assert "liability" in response.content.lower()
    
    def test_enhanced_router_mta_expertise(self, enhanced_router, mock_storage):
        """Test enhanced router MTA expertise."""
        # Mock MTA document
        mock_document = mock_storage.get_document_with_embeddings.return_value
        mock_document.content = "Material Transfer Agreement between Provider and Recipient for research use only"
        mock_document.legal_document_type = "MTA"
        
        # Mock contract engine response
        with patch.object(enhanced_router.contract_engine, 'analyze_question') as mock_analyze:
            mock_analyze.return_value = {
                'response': 'MTA analysis response',
                'sources': ['MTA source'],
                'confidence': 0.8
            }
            
            # Test MTA-specific question
            response = enhanced_router.route_question(
                "What are the permitted uses of the materials?",
                "test_doc_1",
                "test_session_1",
                mock_document
            )
            
            # Verify MTA expertise was applied
            assert isinstance(response, EnhancedResponse)
            assert response.confidence > 0
            assert "mta_specialist" in response.sources or "mta_expertise" in response.context_used
    
    def test_enhanced_router_conversation_context(self, enhanced_router, mock_storage):
        """Test enhanced router conversation context management."""
        mock_document = mock_storage.get_document_with_embeddings.return_value
        session_id = "test_session_context"
        
        # First question
        response1 = enhanced_router.route_question(
            "What are the main terms?",
            "test_doc_1",
            session_id,
            mock_document
        )
        
        # Second question (follow-up)
        response2 = enhanced_router.route_question(
            "Can you explain that in simpler terms?",
            "test_doc_1",
            session_id,
            mock_document
        )
        
        # Verify context is maintained
        assert isinstance(response1, EnhancedResponse)
        assert isinstance(response2, EnhancedResponse)
        
        # Check that context manager has the session
        assert session_id in enhanced_router.context_manager.conversations
    
    def test_enhanced_router_error_handling(self, enhanced_router, mock_storage):
        """Test enhanced router error handling and graceful degradation."""
        # Mock document that will cause an error
        mock_storage.get_document_with_embeddings.return_value = None
        
        # Test with missing document
        response = enhanced_router.route_question(
            "What are the terms?",
            "nonexistent_doc",
            "test_session_error",
            None
        )
        
        # Verify graceful error handling
        assert isinstance(response, EnhancedResponse)
        assert response.response_type in ["error_fallback", "fallback"]
        assert "error" in response.content.lower() or "sorry" in response.content.lower()
    
    def test_backward_compatibility_with_existing_engine(self, contract_engine, mock_storage):
        """Test that enhanced integration maintains backward compatibility."""
        # Mock the existing methods
        with patch.object(contract_engine, 'find_legal_context') as mock_context, \
             patch.object(contract_engine, 'generate_contract_analysis') as mock_analysis:
            
            # Setup mocks
            mock_context.return_value = [{'text': 'test context', 'relevance_score': 0.8}]
            
            mock_analysis_result = Mock()
            mock_analysis_result.direct_evidence = "Test evidence"
            mock_analysis_result.plain_explanation = "Test explanation"
            mock_analysis_result.sources = ["Test source"]
            mock_analysis_result.confidence = 0.8
            mock_analysis_result.document_type = "Contract"
            mock_analysis_result.legal_terms_found = ["liability"]
            
            mock_analysis.return_value = mock_analysis_result
            
            # Test existing answer_question method still works
            result = contract_engine.answer_question("What is liability?", "test_doc_1", "test_session")
            
            # Verify backward compatibility
            assert 'answer' in result
            assert 'sources' in result
            assert 'confidence' in result
            assert result['analysis_mode'] == 'contract'
    
    @patch('streamlit.session_state', {})
    def test_qa_interface_enhanced_mode_toggle(self):
        """Test Q&A interface enhanced mode configuration."""
        # Mock streamlit session state
        import streamlit as st
        
        # Initialize interface
        interface = EnhancedQAInterface()
        
        # Test that enhanced mode is enabled by default
        assert st.session_state.get('enhanced_mode_enabled', True) == True
        
        # Test conversation context persistence initialization
        assert 'conversation_context_persistence' in st.session_state
    
    def test_enhanced_response_validation(self, enhanced_router):
        """Test enhanced response validation."""
        # Create valid enhanced response
        valid_response = EnhancedResponse(
            content="Test response",
            response_type="document_analysis",
            confidence=0.8,
            sources=["test_source"],
            suggestions=["test_suggestion"],
            tone="professional",
            structured_format=None,
            context_used=["test_context"],
            timestamp=datetime.now()
        )
        
        # Test validation (would need to access private method through interface)
        # This tests the structure we expect
        assert hasattr(valid_response, 'content')
        assert hasattr(valid_response, 'response_type')
        assert hasattr(valid_response, 'confidence')
        assert hasattr(valid_response, 'sources')
        assert hasattr(valid_response, 'suggestions')
        assert valid_response.content.strip() != ""
    
    def test_enhanced_router_with_structured_response(self, enhanced_router, mock_storage):
        """Test enhanced router preserving structured response format."""
        mock_document = mock_storage.get_document_with_embeddings.return_value
        
        # Mock contract engine with structured response
        with patch.object(enhanced_router.contract_engine, 'analyze_question') as mock_analyze:
            mock_analyze.return_value = {
                'response': 'Formatted response',
                'direct_evidence': 'Test evidence',
                'plain_explanation': 'Test explanation',
                'implication_analysis': 'Test analysis',
                'sources': ['Test source'],
                'confidence': 0.8
            }
            
            # Test document-related question
            response = enhanced_router.route_question(
                "What are the liability terms?",
                "test_doc_1",
                "test_session_structured",
                mock_document
            )
            
            # Verify structured format is preserved
            assert isinstance(response, EnhancedResponse)
            assert response.structured_format is not None
            assert isinstance(response.structured_format, dict)
    
    def test_integration_with_multiple_question_types(self, enhanced_router, mock_storage):
        """Test integration handling multiple question types in sequence."""
        mock_document = mock_storage.get_document_with_embeddings.return_value
        session_id = "test_session_multi"
        
        # Mock contract engine
        with patch.object(enhanced_router.contract_engine, 'analyze_question') as mock_analyze:
            mock_analyze.return_value = {
                'response': 'Contract analysis',
                'sources': ['Contract source'],
                'confidence': 0.8
            }
            
            # Test sequence of different question types
            questions_and_expected_types = [
                ("What are the main terms?", "document_analysis"),
                ("Hi, how are you?", "casual"),
                ("What's the weather like?", "fallback"),
                ("What is a liability clause?", ["general_knowledge", "document_analysis"])
            ]
            
            for question, expected_type in questions_and_expected_types:
                response = enhanced_router.route_question(
                    question, "test_doc_1", session_id, mock_document
                )
                
                assert isinstance(response, EnhancedResponse)
                if isinstance(expected_type, list):
                    assert response.response_type in expected_type
                else:
                    assert response.response_type == expected_type
    
    def test_error_recovery_and_graceful_degradation(self, enhanced_router, mock_storage):
        """Test error recovery and graceful degradation."""
        mock_document = mock_storage.get_document_with_embeddings.return_value
        
        # Mock contract engine to raise an error
        with patch.object(enhanced_router.contract_engine, 'analyze_question') as mock_analyze:
            mock_analyze.side_effect = Exception("Test error")
            
            # Test that error is handled gracefully
            response = enhanced_router.route_question(
                "What are the terms?",
                "test_doc_1",
                "test_session_error_recovery",
                mock_document
            )
            
            # Verify graceful error handling
            assert isinstance(response, EnhancedResponse)
            assert response.response_type in ["fallback", "error_fallback"]
            assert response.content is not None
            assert len(response.content.strip()) > 0


if __name__ == "__main__":
    pytest.main([__file__])