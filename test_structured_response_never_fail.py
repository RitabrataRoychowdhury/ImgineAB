#!/usr/bin/env python3
"""
Comprehensive test for structured response system never-fail logic.

Tests extreme edge cases to ensure the system ALWAYS provides meaningful responses.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.structured_response_system import StructuredResponseSystem
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.models.document import Document
from src.models.enhanced import ResponseType
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_extreme_edge_cases():
    """Test extreme edge cases to ensure never-fail logic."""
    
    print("🧪 Testing Structured Response System - Never-Fail Logic")
    print("=" * 60)
    
    # Initialize systems
    structured_system = StructuredResponseSystem()
    router = EnhancedResponseRouter()
    
    # Test cases - extreme edge cases
    edge_cases = [
        # Empty and minimal inputs
        "",
        " ",
        "?",
        "a",
        "help",
        
        # Gibberish inputs
        "asdfghjkl",
        "xyzxyzxyz",
        "123456789",
        "!@#$%^&*()",
        "ñáéíóú",
        
        # Ambiguous inputs
        "what",
        "how maybe",
        "I don't know what to ask",
        "this is confusing",
        "help me understand",
        
        # Very long inputs
        "what " * 100,
        "This is a very long question that goes on and on and repeats itself many times to test how the system handles extremely verbose inputs that might cause processing issues or memory problems or other technical difficulties that could potentially break the response generation system",
        
        # Mixed content
        "What about payment terms? Also liability. And termination. Plus general stuff.",
        "Contract??? Help!!! What does this mean?!?!",
        "payment liability termination parties obligations risks",
        
        # Special characters and encoding
        "What about émojis 😀 and spëcial chars?",
        "Contract\n\nwith\twhitespace\r\neverywhere",
        "Question with 'quotes' and \"double quotes\" and `backticks`",
        
        # Potentially problematic inputs
        None,  # This will be converted to string
        123,   # This will be converted to string
        [],    # This will be converted to string
        {},    # This will be converted to string
    ]
    
    # Test with and without document content
    test_documents = [
        None,
        "",
        "This is a simple contract between Party A and Party B.",
        "A" * 10000,  # Very long document
    ]
    
    total_tests = 0
    successful_responses = 0
    
    for i, test_input in enumerate(edge_cases):
        for j, doc_content in enumerate(test_documents):
            total_tests += 1
            
            print(f"\n🔍 Test {total_tests}: Input='{str(test_input)[:50]}{'...' if len(str(test_input)) > 50 else ''}', Doc={'Yes' if doc_content else 'No'}")
            
            try:
                # Convert input to string if it's not already
                input_str = str(test_input) if test_input is not None else ""
                
                # Test structured response system directly
                response = structured_system.process_input_with_guaranteed_response(
                    user_input=input_str,
                    document_content=doc_content
                )
                
                # Validate response
                assert response is not None, "Response is None"
                assert hasattr(response, 'content'), "Response missing content attribute"
                assert response.content is not None, "Response content is None"
                assert len(response.content.strip()) > 0, "Response content is empty"
                assert hasattr(response, 'response_type'), "Response missing response_type"
                assert hasattr(response, 'confidence'), "Response missing confidence"
                assert 0.0 <= response.confidence <= 1.0, f"Invalid confidence: {response.confidence}"
                assert hasattr(response, 'suggestions'), "Response missing suggestions"
                assert isinstance(response.suggestions, list), "Suggestions not a list"
                
                print(f"   ✅ Structured System: {response.response_type.value}, confidence={response.confidence:.2f}")
                print(f"      Content length: {len(response.content)} chars")
                print(f"      Suggestions: {len(response.suggestions)}")
                
                successful_responses += 1
                
            except Exception as e:
                print(f"   ❌ FAILED: {str(e)}")
                print(f"      This should NEVER happen - system must be fixed!")
                continue
            
            # Also test through the router
            try:
                document = None
                if doc_content:
                    document = Document(
                        id="test_doc",
                        filename="test.txt",
                        content=doc_content,
                        upload_timestamp="2024-01-01T00:00:00"
                    )
                
                router_response = router.route_question(
                    question=input_str,
                    document_id="test_doc" if document else "no_doc",
                    session_id="test_session",
                    document=document
                )
                
                # Validate router response
                assert router_response is not None, "Router response is None"
                assert hasattr(router_response, 'content'), "Router response missing content"
                assert router_response.content is not None, "Router response content is None"
                assert len(router_response.content.strip()) > 0, "Router response content is empty"
                
                print(f"   ✅ Router: {router_response.response_type.value}, confidence={router_response.confidence:.2f}")
                
            except Exception as e:
                print(f"   ❌ Router FAILED: {str(e)}")
                print(f"      This should NEVER happen - router must be fixed!")
    
    print(f"\n📊 RESULTS:")
    print(f"Total tests: {total_tests}")
    print(f"Successful responses: {successful_responses}")
    print(f"Success rate: {(successful_responses/total_tests)*100:.1f}%")
    
    if successful_responses == total_tests:
        print("🎉 ALL TESTS PASSED - Never-fail logic is working!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Never-fail logic needs fixes!")
        return False

def test_specific_response_patterns():
    """Test that specific response patterns are generated correctly."""
    
    print("\n🎯 Testing Specific Response Patterns")
    print("=" * 40)
    
    structured_system = StructuredResponseSystem()
    
    # Test cases for specific patterns
    pattern_tests = [
        {
            'input': 'What does this clause mean?',
            'expected_pattern': 'document',
            'should_contain': ['📋 Evidence', '🔍 Plain English', '⚖️ Implications']
        },
        {
            'input': 'How do contracts typically work?',
            'expected_pattern': 'general_legal',
            'should_contain': ['ℹ️ Status', '📚 General Rule', '🎯 Application']
        },
        {
            'input': 'Can you create a table of payment terms?',
            'expected_pattern': 'data_table',
            'should_contain': ['📥 Export', '|', '---']
        },
        {
            'input': 'I\'m not sure what I\'m asking about',
            'expected_pattern': 'ambiguous',
            'should_contain': ['🤔 My Take', 'Option A', 'Option B']
        }
    ]
    
    for test_case in pattern_tests:
        print(f"\n🔍 Testing: '{test_case['input']}'")
        
        try:
            response = structured_system.process_input_with_guaranteed_response(
                user_input=test_case['input'],
                document_content="This is a sample contract with payment terms and liability clauses."
            )
            
            print(f"   Pattern detected: {response.structured_format.get('pattern', 'unknown') if response.structured_format else 'none'}")
            print(f"   Content length: {len(response.content)} chars")
            
            # Check for expected content
            missing_elements = []
            for element in test_case['should_contain']:
                if element not in response.content:
                    missing_elements.append(element)
            
            if missing_elements:
                print(f"   ⚠️  Missing elements: {missing_elements}")
            else:
                print(f"   ✅ All expected elements present")
            
            # Show first 200 chars of response
            print(f"   Preview: {response.content[:200]}...")
            
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")

def test_data_export_generation():
    """Test automatic data export generation."""
    
    print("\n📊 Testing Data Export Generation")
    print("=" * 35)
    
    structured_system = StructuredResponseSystem()
    
    export_test_cases = [
        "Create a table of contract parties",
        "Show me payment terms in a table",
        "Generate a risk assessment matrix",
        "Export the key dates and deadlines",
        "List all the obligations in CSV format"
    ]
    
    for test_input in export_test_cases:
        print(f"\n🔍 Testing: '{test_input}'")
        
        try:
            response = structured_system.process_input_with_guaranteed_response(
                user_input=test_input,
                document_content="Sample contract with parties, payment terms, and obligations."
            )
            
            # Check for export indicators
            has_table = '|' in response.content and '---' in response.content
            has_export_link = '📥' in response.content or 'Export' in response.content
            
            print(f"   Has table: {has_table}")
            print(f"   Has export link: {has_export_link}")
            print(f"   Response type: {response.response_type.value}")
            
            if has_table and has_export_link:
                print(f"   ✅ Export functionality working")
            else:
                print(f"   ⚠️  Export functionality may need improvement")
                
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")

def test_error_handling_robustness():
    """Test error handling with system failures."""
    
    print("\n🛡️  Testing Error Handling Robustness")
    print("=" * 40)
    
    # This would test scenarios where internal components fail
    # For now, we'll test with problematic inputs that might cause issues
    
    problematic_inputs = [
        "What about " + "very " * 1000 + "long questions?",  # Memory stress
        "\x00\x01\x02\x03",  # Control characters
        "SELECT * FROM contracts WHERE id = 1; DROP TABLE contracts;",  # SQL injection attempt
        "<script>alert('xss')</script>",  # XSS attempt
        "../../etc/passwd",  # Path traversal attempt
        "What about\nline\nbreaks\neverywhere?",  # Line break handling
    ]
    
    structured_system = StructuredResponseSystem()
    
    for test_input in problematic_inputs:
        print(f"\n🔍 Testing problematic input: '{test_input[:50]}...'")
        
        try:
            response = structured_system.process_input_with_guaranteed_response(
                user_input=test_input,
                document_content="Sample contract content"
            )
            
            # Validate that response is safe and meaningful
            assert response is not None
            assert response.content is not None
            assert len(response.content.strip()) > 0
            
            # Check that response doesn't contain the problematic input verbatim
            # (to prevent reflection attacks)
            if len(test_input) > 20 and test_input in response.content:
                print(f"   ⚠️  Response contains problematic input verbatim")
            else:
                print(f"   ✅ Response is safe and meaningful")
                
        except Exception as e:
            print(f"   ❌ FAILED: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Never-Fail Logic Tests")
    print("=" * 60)
    
    try:
        # Run all test suites
        success1 = test_extreme_edge_cases()
        test_specific_response_patterns()
        test_data_export_generation()
        test_error_handling_robustness()
        
        print(f"\n🏁 FINAL RESULT:")
        if success1:
            print("✅ Never-fail logic is working correctly!")
            print("The system provides meaningful responses for ALL inputs.")
        else:
            print("❌ Never-fail logic needs improvement!")
            print("Some edge cases are not handled properly.")
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR in test suite: {str(e)}")
        print("This indicates a fundamental problem that must be fixed!")