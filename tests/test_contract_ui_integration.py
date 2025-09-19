"""Integration tests for contract analysis UI capabilities."""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.ui.qa_interface import QAInterface
from src.ui.document_manager import DocumentManager
from src.models.document import Document
from src.services.contract_analyst_engine import ContractAnalystEngine


class TestContractUIIntegration:
    """Test contract analysis UI integration."""
    
    @pytest.fixture
    def mock_document(self):
        """Create a mock legal document."""
        return Document(
            id="test_doc_1",
            title="Test Material Transfer Agreement",
            file_type="pdf",
            file_size=1024000,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="This Material Transfer Agreement is entered into between Provider and Recipient for the transfer of research materials. The Provider grants the Recipient a license to use the materials for research purposes only. All intellectual property rights remain with the Provider.",
            document_type="Legal Document",
            is_legal_document=True,
            legal_document_type="MTA",
            legal_analysis_confidence=0.85
        )
    
    @pytest.fixture
    def mock_standard_document(self):
        """Create a mock non-legal document."""
        return Document(
            id="test_doc_2",
            title="Technical Documentation",
            file_type="pdf",
            file_size=512000,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="This is a technical document about system configuration and setup procedures.",
            document_type="Technical Documentation",
            is_legal_document=False
        )
    
    @pytest.fixture
    def qa_interface(self):
        """Create QA interface with mocked dependencies."""
        with patch('src.ui.qa_interface.DocumentStorage'), \
             patch('src.ui.qa_interface.create_qa_engine'), \
             patch('src.ui.qa_interface.create_contract_analyst_engine'), \
             patch('src.ui.qa_interface.config.get_gemini_api_key', return_value='test_key'):
            
            interface = QAInterface()
            interface.qa_engine = Mock()
            interface.contract_engine = Mock()
            return interface
    
    @pytest.fixture
    def document_manager(self):
        """Create document manager with mocked dependencies."""
        with patch('src.ui.document_manager.DocumentStorage'), \
             patch('src.ui.document_manager.create_contract_analyst_engine'), \
             patch('src.ui.document_manager.config.get_gemini_api_key', return_value='test_key'):
            
            manager = DocumentManager()
            manager.contract_engine = Mock()
            return manager
    
    def test_legal_document_detection_and_mode_switching(self, qa_interface, mock_document):
        """Test that legal documents are detected and switch to contract analysis mode."""
        # Mock the contract engine detection
        qa_interface.contract_engine.detect_legal_document.return_value = (True, "MTA", 0.85)
        qa_interface.contract_engine.extract_legal_terms.return_value = ["material transfer", "research use", "intellectual property"]
        
        # Initialize session state
        if 'legal_document_info' not in st.session_state:
            st.session_state.legal_document_info = {}
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'standard'
        
        # Test legal document detection
        qa_interface._detect_and_set_analysis_mode(mock_document)
        
        # Verify legal document was detected
        assert st.session_state.legal_document_info[mock_document.id]['is_legal'] == True
        assert st.session_state.legal_document_info[mock_document.id]['document_type'] == "MTA"
        assert st.session_state.legal_document_info[mock_document.id]['confidence'] == 0.85
        
        # Verify analysis mode was switched to contract
        assert st.session_state.analysis_mode == 'contract'
        
        # Verify contract engine was called
        qa_interface.contract_engine.detect_legal_document.assert_called_once_with(mock_document)
    
    def test_standard_document_keeps_standard_mode(self, qa_interface, mock_standard_document):
        """Test that non-legal documents stay in standard Q&A mode."""
        # Mock the contract engine detection
        qa_interface.contract_engine.detect_legal_document.return_value = (False, None, 0.1)
        
        # Initialize session state
        if 'legal_document_info' not in st.session_state:
            st.session_state.legal_document_info = {}
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'standard'
        
        # Test standard document detection
        qa_interface._detect_and_set_analysis_mode(mock_standard_document)
        
        # Verify document was not classified as legal
        assert st.session_state.legal_document_info[mock_standard_document.id]['is_legal'] == False
        assert st.session_state.legal_document_info[mock_standard_document.id]['document_type'] is None
        
        # Verify analysis mode remained standard
        assert st.session_state.analysis_mode == 'standard'
    
    def test_session_management_with_analysis_modes(self, qa_interface, mock_document):
        """Test that sessions are managed separately for different analysis modes."""
        # Initialize session state
        if 'qa_sessions' not in st.session_state:
            st.session_state.qa_sessions = {}
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'contract'
        
        # Mock engine session creation
        qa_interface.contract_engine.create_qa_session.return_value = "contract_session_123"
        qa_interface.qa_engine.create_qa_session.return_value = "standard_session_456"
        
        # Test contract session creation
        session_id = qa_interface._get_or_create_session(mock_document.id)
        assert session_id == "contract_session_123"
        assert f"session_{mock_document.id}_contract" in st.session_state.qa_sessions
        
        # Switch to standard mode
        st.session_state.analysis_mode = 'standard'
        session_id = qa_interface._get_or_create_session(mock_document.id)
        assert session_id == "standard_session_456"
        assert f"session_{mock_document.id}_standard" in st.session_state.qa_sessions
        
        # Verify both sessions exist
        assert len(st.session_state.qa_sessions) == 2
    
    def test_structured_response_rendering(self, qa_interface):
        """Test that structured contract responses are rendered correctly."""
        structured_response = {
            'direct_evidence': 'The agreement states that "Provider grants Recipient a license for research use only"',
            'plain_explanation': 'This means you can only use the materials for research, not commercial purposes',
            'implication_analysis': 'This benefits the Provider by maintaining control over commercial applications'
        }
        
        # Mock streamlit functions
        with patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.write') as mock_write:
            
            qa_interface._render_structured_response(structured_response)
            
            # Verify all sections were rendered
            assert mock_markdown.call_count == 3  # Three section headers
            assert mock_write.call_count == 3     # Three section contents
            
            # Verify correct headers were used
            markdown_calls = [call[0][0] for call in mock_markdown.call_args_list]
            assert "### 📋 Direct Evidence" in markdown_calls
            assert "### 💡 Plain-English Explanation" in markdown_calls
            assert "### ⚖️ Implication/Analysis" in markdown_calls
    
    def test_contract_question_processing(self, qa_interface, mock_document):
        """Test that contract questions are processed with the contract engine."""
        # Setup
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'contract'
        
        # Mock contract engine response
        mock_result = {
            'answer': 'Formatted contract analysis response',
            'structured_response': {
                'direct_evidence': 'Test evidence',
                'plain_explanation': 'Test explanation',
                'implication_analysis': 'Test analysis'
            },
            'sources': ['Section 1.1', 'Section 2.3'],
            'confidence': 0.9,
            'document_type': 'MTA',
            'legal_terms_found': ['material transfer', 'research use']
        }
        qa_interface.contract_engine.answer_question.return_value = mock_result
        
        # Mock streamlit functions
        with patch('streamlit.spinner'), \
             patch('streamlit.success'), \
             patch('streamlit.chat_message'), \
             patch('streamlit.rerun'), \
             patch.object(qa_interface, '_render_structured_response') as mock_render:
            
            qa_interface._process_question("Who are the parties?", mock_document, "session_123")
            
            # Verify contract engine was used
            qa_interface.contract_engine.answer_question.assert_called_once_with(
                "Who are the parties?", mock_document.id, "session_123"
            )
            
            # Verify structured response was rendered
            mock_render.assert_called_once_with(mock_result['structured_response'])
    
    def test_document_manager_legal_indicators(self, document_manager, mock_document):
        """Test that document manager shows legal document indicators."""
        # Mock legal document detection
        document_manager.contract_engine.detect_legal_document.return_value = (True, "MTA", 0.85)
        
        # Initialize session state
        if 'legal_document_cache' not in st.session_state:
            st.session_state.legal_document_cache = {}
        
        # Test legal document detection
        document_manager._detect_legal_document_if_needed(mock_document)
        
        # Verify legal document info was cached
        assert mock_document.id in st.session_state.legal_document_cache
        legal_info = st.session_state.legal_document_cache[mock_document.id]
        assert legal_info['is_legal'] == True
        assert legal_info['document_type'] == "MTA"
        assert legal_info['confidence'] == 0.85
    
    def test_example_questions_for_legal_documents(self, qa_interface, mock_document):
        """Test that appropriate example questions are shown for legal documents."""
        # Setup legal document mode
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'contract'
        if 'legal_document_info' not in st.session_state:
            st.session_state.legal_document_info = {}
        
        st.session_state.legal_document_info[mock_document.id] = {
            'is_legal': True,
            'document_type': 'MTA',
            'confidence': 0.85
        }
        
        # Mock streamlit functions
        with patch('streamlit.subheader'), \
             patch('streamlit.info'), \
             patch('streamlit.write'), \
             patch('streamlit.button', return_value=False) as mock_button:
            
            qa_interface._show_example_questions(mock_document)
            
            # Verify MTA-specific questions were shown
            button_calls = [call[0][0] for call in mock_button.call_args_list]
            mta_questions = [call for call in button_calls if "MTA" in call or "material" in call.lower()]
            assert len(mta_questions) > 0
            
            # Verify legal document questions were shown
            legal_questions = [call for call in button_calls if "parties" in call.lower() or "obligations" in call.lower()]
            assert len(legal_questions) > 0
    
    def test_session_continuity_across_mode_switches(self, qa_interface, mock_document):
        """Test that session context is maintained when switching between analysis modes."""
        # Initialize session state
        if 'qa_sessions' not in st.session_state:
            st.session_state.qa_sessions = {}
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'contract'
        
        # Mock engines
        qa_interface.contract_engine.create_qa_session.return_value = "contract_session"
        qa_interface.qa_engine.create_qa_session.return_value = "standard_session"
        
        # Create contract session
        contract_session_id = qa_interface._get_or_create_session(mock_document.id)
        assert contract_session_id == "contract_session"
        
        # Switch to standard mode
        st.session_state.analysis_mode = 'standard'
        standard_session_id = qa_interface._get_or_create_session(mock_document.id)
        assert standard_session_id == "standard_session"
        
        # Switch back to contract mode
        st.session_state.analysis_mode = 'contract'
        contract_session_id_2 = qa_interface._get_or_create_session(mock_document.id)
        assert contract_session_id_2 == "contract_session"  # Should reuse existing session
        
        # Verify sessions are maintained separately
        assert len(st.session_state.qa_sessions) == 2


if __name__ == "__main__":
    pytest.main([__file__])