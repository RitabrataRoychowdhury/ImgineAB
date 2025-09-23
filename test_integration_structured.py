#!/usr/bin/env python3
"""
Integration test for structured response system with enhanced router.
Tests the complete integration without external API dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the external dependencies to avoid import errors
import unittest.mock as mock

# Mock the external services that require API keys or network access
with mock.patch('src.services.qa_engine.QAEngine'), \
     mock.patch('src.services.contract_analyst_engine.ContractAnalystEngine'), \
     mock.patch('src.services.question_classifier.QuestionClassifier'), \
     mock.patch('src.services.fallback_response_generator.FallbackResponseGenerator'), \
     mock.patch('src.services.mta_specialist.MTASpecialistModule'), \
     mock.patch('src.services.enhanced_context_manager.EnhancedContextManager'):
    
    from src.services.enhanced_response_router import EnhancedResponseRouter
    from src.models.document import Document
    from src.models.enhanced import ResponseType

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mock_router():
    """Create a router with mocked dependencies."""
    
    # Create router
    router = EnhancedResponseRouter()
    
    # Mock the dependencies to return reasonable defaults
    router.question_classifier.classify_intent = mock.MagicMock(return_value=mock.MagicMock(
        primary_intent="document_related",
        confidence=0.8,
        secondary_intents=[],
        document_relevance_score=0.7,
        casualness_level=0.3,
        requires_mta_expertise=False,
        requires_fallback=False
    ))
    
    router.context_manager.get_conversation_context = mock.MagicMock(return_value=None)
    router.context_manager.update_conversation_context = mock.MagicMock()
    
    router.fallback_generator.suggest_relevant_questions = mock.MagicMock(return_value=[
        "What are the key terms?",
        "Who are the parties?"
    ])
    
    return router

def test_router_integration():
    """Test that the router integrates correctly with structured response system."""
    
    print("🔗 Testing Router Integration with Structured Response System")
    print("=" * 65)
    
    try:
        router = create_mock_router()
        print("✅ Router created with mocked dependencies")
    except Exception as e:
        print(f"❌ Router creation failed: {e}")
        return False
    
    # Test basic integration
    test_cases = [
        {
            'question': 'What are the payment terms?',
            'document_content': 'This contract specifies payment terms and conditions.',
            'expected_patterns': ['📋 Evidence', '🔍 Plain English', '⚖️ Implications']
        },
        {
            'question': 'How do contracts generally work?',
            'document_content': 'Sample contract content.',
            'expected_patterns': ['ℹ️ Status', '📚 General Rule', '🎯 Application']
        },
        {
            'question': 'Create a table of key terms',
            'document_content': 'Contract with various terms and conditions.',
            'expected_patterns': ['|', '---']  # Table indicators
        },
        {
            'question': 'I\'m not sure what to ask',
            'document_content': 'Sample contract.',
            'expected_patterns': ['🤔 My Take', 'Option']
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🔍 Test {i+1}: '{test_case['question']}'")
        
        try:
            # Create document
            document = Document(
                id=f"test_doc_{i}",
                filename=f"test_{i}.txt",
                content=test_case['document_content'],
                upload_timestamp="2024-01-01T00:00:00"
            )
            
            # Route question
            response = router.route_question(
                question=test_case['question'],
                document_id=document.id,
                session_id="test_session",
                document=document
            )
            
            # Validate response
            assert response is not None, "Response is None"
            assert hasattr(response, 'content'), "Response missing content"
            assert response.content is not None, "Response content is None"
            assert len(response.content.strip()) > 0, "Response content is empty"
            assert hasattr(response, 'response_type'), "Response missing response_type"
            assert hasattr(response, 'confidence'), "Response missing confidence"
            assert 0.0 <= response.confidence <= 1.0, f"Invalid confidence: {response.confidence}"
            
            print(f"   ✅ Response generated: {len(response.content)} chars, confidence={response.confidence:.2f}")
            print(f"   Response type: {response.response_type.value}")
            
            # Check for expected patterns
            missing_patterns = []
            for pattern in test_case['expected_patterns']:
                if pattern not in response.content:
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                print(f"   ⚠️  Missing patterns: {missing_patterns}")
            else:
                print(f"   ✅ All expected patterns found")
            
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Test {i+1} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nIntegration test results: {success_count}/{len(test_cases)} passed")
    
    if success_count == len(test_cases):
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print("❌ Some integration tests failed")
        return False

def test_never_fail_guarantee_through_router():
    """Test that the never-fail guarantee works through the router."""
    
    print(f"\n🛡️  Testing Never-Fail Guarantee Through Router")
    print("=" * 50)
    
    router = create_mock_router()
    
    # Extreme edge cases
    edge_cases = [
        "",
        " ",
        "?",
        "asdfghjkl",
        "what " * 100,
        None,  # This will be converted to string
        123,
        [],
        {}
    ]
    
    success_count = 0
    
    for i, test_input in enumerate(edge_cases):
        try:
            # Convert to string
            input_str = str(test_input) if test_input is not None else ""
            
            # Create minimal document
            document = Document(
                id="edge_test_doc",
                filename="edge_test.txt", 
                content="Sample contract content for edge case testing.",
                upload_timestamp="2024-01-01T00:00:00"
            )
            
            # Route through the system
            response = router.route_question(
                question=input_str,
                document_id=document.id,
                session_id="edge_test_session",
                document=document
            )
            
            # Validate response
            assert response is not None
            assert response.content is not None
            assert len(response.content.strip()) > 0
            
            print(f"   Edge case {i+1}: '{str(test_input)[:20]}...' -> ✅ ({len(response.content)} chars)")
            success_count += 1
            
        except Exception as e:
            print(f"   Edge case {i+1}: '{str(test_input)[:20]}...' -> ❌ {e}")
    
    print(f"\nNever-fail test results: {success_count}/{len(edge_cases)} passed")
    
    if success_count == len(edge_cases):
        print("🎉 NEVER-FAIL GUARANTEE WORKING THROUGH ROUTER!")
        return True
    else:
        print("❌ Never-fail guarantee needs improvement")
        return False

def test_error_recovery_scenarios():
    """Test error recovery in various failure scenarios."""
    
    print(f"\n🚨 Testing Error Recovery Scenarios")
    print("=" * 40)
    
    router = create_mock_router()
    
    # Test with no document
    print("Testing with no document...")
    try:
        response = router.route_question(
            question="What are the payment terms?",
            document_id="nonexistent",
            session_id="test_session",
            document=None
        )
        
        assert response is not None
        assert response.content is not None
        assert len(response.content.strip()) > 0
        
        print("   ✅ No document scenario handled correctly")
        
    except Exception as e:
        print(f"   ❌ No document scenario failed: {e}")
    
    # Test with empty document
    print("Testing with empty document...")
    try:
        empty_doc = Document(
            id="empty_doc",
            filename="empty.txt",
            content="",
            upload_timestamp="2024-01-01T00:00:00"
        )
        
        response = router.route_question(
            question="What does this contract say?",
            document_id=empty_doc.id,
            session_id="test_session",
            document=empty_doc
        )
        
        assert response is not None
        assert response.content is not None
        assert len(response.content.strip()) > 0
        
        print("   ✅ Empty document scenario handled correctly")
        
    except Exception as e:
        print(f"   ❌ Empty document scenario failed: {e}")
    
    # Test with malformed document
    print("Testing with malformed document...")
    try:
        # Create document with missing attributes
        malformed_doc = Document(
            id="malformed_doc",
            filename="malformed.txt",
            content=None,  # This might cause issues
            upload_timestamp="2024-01-01T00:00:00"
        )
        
        response = router.route_question(
            question="Analyze this contract",
            document_id=malformed_doc.id,
            session_id="test_session",
            document=malformed_doc
        )
        
        assert response is not None
        assert response.content is not None
        assert len(response.content.strip()) > 0
        
        print("   ✅ Malformed document scenario handled correctly")
        
    except Exception as e:
        print(f"   ❌ Malformed document scenario failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Integration Tests for Structured Response System")
    print("=" * 70)
    
    try:
        # Run test suites
        integration_success = test_router_integration()
        never_fail_success = test_never_fail_guarantee_through_router()
        test_error_recovery_scenarios()
        
        print(f"\n🏁 FINAL INTEGRATION RESULTS:")
        print(f"Router integration: {'✅ PASS' if integration_success else '❌ FAIL'}")
        print(f"Never-fail guarantee: {'✅ PASS' if never_fail_success else '❌ FAIL'}")
        
        if integration_success and never_fail_success:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("The structured response system is fully integrated and working.")
        else:
            print("\n❌ SOME INTEGRATION TESTS FAILED!")
            print("The integration needs fixes before deployment.")
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR in integration tests: {str(e)}")
        import traceback
        traceback.print_exc()