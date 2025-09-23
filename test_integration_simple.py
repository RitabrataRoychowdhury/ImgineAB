#!/usr/bin/env python3
"""
Simple integration test to verify the UI fix works without external dependencies.
"""

import sys
import os
import tempfile
import sqlite3
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, 'src')

def test_qa_interface_initialization():
    """Test that QA interface can be initialized without errors."""
    print("🧪 Testing QA interface initialization...")
    
    try:
        # Mock streamlit to avoid import errors
        sys.modules['streamlit'] = Mock()
        
        # Mock other dependencies
        with patch('src.ui.qa_interface.DocumentStorage'), \
             patch('src.ui.qa_interface.enhanced_storage'), \
             patch('src.ui.qa_interface.migrator'):
            
            from src.ui.qa_interface import EnhancedQAInterface
            
            # Create interface
            interface = EnhancedQAInterface()
            
            # Test that fallback method exists and works
            assert hasattr(interface, '_generate_helpful_fallback_response')
            assert hasattr(interface, '_ensure_engines_initialized')
            assert hasattr(interface, '_create_basic_fallback_response')
            
            print("✅ QA interface initialized successfully")
            return True
            
    except Exception as e:
        print(f"❌ QA interface initialization failed: {e}")
        return False

def test_engine_initialization_logic():
    """Test the engine initialization logic."""
    print("🧪 Testing engine initialization logic...")
    
    try:
        # Mock streamlit and session state
        mock_st = Mock()
        mock_st.session_state = {
            'enhanced_mode_enabled': True
        }
        sys.modules['streamlit'] = mock_st
        
        # Mock other dependencies
        with patch('src.ui.qa_interface.DocumentStorage'), \
             patch('src.ui.qa_interface.enhanced_storage'), \
             patch('src.ui.qa_interface.migrator'), \
             patch('src.ui.qa_interface.get_logger'):
            
            from src.ui.qa_interface import EnhancedQAInterface
            
            interface = EnhancedQAInterface()
            
            # Mock the engines as None initially
            interface.qa_engine = None
            interface.contract_engine = None
            interface.enhanced_router = None
            
            # Mock the storage
            interface.storage = Mock()
            
            # Test engine initialization
            with patch('src.ui.qa_interface.QAEngine') as mock_qa_engine, \
                 patch('src.ui.qa_interface.ContractAnalystEngine') as mock_contract_engine, \
                 patch('src.ui.qa_interface.EnhancedResponseRouter') as mock_enhanced_router, \
                 patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
                
                interface._ensure_engines_initialized()
                
                # Verify engines were created
                mock_qa_engine.assert_called_once()
                mock_contract_engine.assert_called_once()
                mock_enhanced_router.assert_called_once()
            
            print("✅ Engine initialization logic works")
            return True
            
    except Exception as e:
        print(f"❌ Engine initialization test failed: {e}")
        return False

def test_error_handling_logic():
    """Test the error handling and fallback logic."""
    print("🧪 Testing error handling logic...")
    
    try:
        # Mock streamlit
        mock_st = Mock()
        mock_st.session_state = {
            'enhanced_mode_enabled': True
        }
        mock_st.chat_message.return_value.__enter__ = Mock()
        mock_st.chat_message.return_value.__exit__ = Mock()
        sys.modules['streamlit'] = mock_st
        
        # Mock other dependencies
        with patch('src.ui.qa_interface.DocumentStorage'), \
             patch('src.ui.qa_interface.enhanced_storage'), \
             patch('src.ui.qa_interface.migrator'), \
             patch('src.ui.qa_interface.get_logger'):
            
            from src.ui.qa_interface import EnhancedQAInterface
            from src.models.document import Document
            
            interface = EnhancedQAInterface()
            
            # Create a mock document
            document = Mock(spec=Document)
            document.id = "test_doc"
            document.title = "Test Document"
            
            # Test basic fallback response creation
            interface._create_basic_fallback_response("Test question")
            
            # Verify streamlit methods were called
            mock_st.chat_message.assert_called()
            
            # Test helpful fallback response
            response = interface._generate_helpful_fallback_response(
                "Who are the parties in this agreement?", 
                document
            )
            
            assert "parties involved" in response
            assert len(response) > 50
            
            print("✅ Error handling logic works")
            return True
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_question_processing_flow():
    """Test the question processing flow."""
    print("🧪 Testing question processing flow...")
    
    try:
        # Mock streamlit
        mock_st = Mock()
        mock_st.session_state = {
            'enhanced_mode_enabled': False,  # Start with enhanced mode disabled
            'analysis_mode': 'contract'
        }
        mock_st.spinner.return_value.__enter__ = Mock()
        mock_st.spinner.return_value.__exit__ = Mock()
        sys.modules['streamlit'] = mock_st
        
        # Mock other dependencies
        with patch('src.ui.qa_interface.DocumentStorage'), \
             patch('src.ui.qa_interface.enhanced_storage'), \
             patch('src.ui.qa_interface.migrator'), \
             patch('src.ui.qa_interface.get_logger'):
            
            from src.ui.qa_interface import EnhancedQAInterface
            from src.models.document import Document
            
            interface = EnhancedQAInterface()
            
            # Mock engines
            interface.contract_engine = Mock()
            interface.contract_engine.answer_question.return_value = {
                'answer': 'Test answer',
                'sources': ['Test source'],
                'confidence': 0.8
            }
            
            # Create mock document
            document = Mock(spec=Document)
            document.id = "test_doc"
            
            # Test standard question processing
            with patch.object(interface, '_ensure_engines_initialized'), \
                 patch.object(interface, '_process_standard_question') as mock_standard:
                
                interface._process_question("Test question", document, "session_1")
                
                # Should call standard processing when enhanced mode is disabled
                mock_standard.assert_called_once()
            
            print("✅ Question processing flow works")
            return True
            
    except Exception as e:
        print(f"❌ Question processing test failed: {e}")
        return False

def main():
    """Run integration tests."""
    print("🚀 Starting simple integration tests...")
    print("=" * 60)
    
    tests = [
        test_qa_interface_initialization,
        test_engine_initialization_logic,
        test_error_handling_logic,
        test_question_processing_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} integration tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! The UI fix should work.")
        print("\n📋 Summary of fixes:")
        print("   ✅ Added proper engine initialization")
        print("   ✅ Added graceful error handling with helpful fallbacks")
        print("   ✅ Fixed question pattern matching for better responses")
        print("   ✅ Added fallback to standard mode when enhanced mode fails")
        print("   ✅ Improved user experience with meaningful error messages")
        return True
    else:
        print("❌ Some integration tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)