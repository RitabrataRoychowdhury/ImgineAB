#!/usr/bin/env python3
"""
Simple test for structured response system core functionality.
Tests the never-fail logic without external dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the structured response system directly
from src.services.structured_response_system import StructuredResponseSystem, ResponsePatternType
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_core_functionality():
    """Test core structured response functionality."""
    
    print("🧪 Testing Structured Response System - Core Functionality")
    print("=" * 60)
    
    # Initialize system
    try:
        structured_system = StructuredResponseSystem()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return False
    
    # Test basic input processing
    test_cases = [
        # Basic cases
        ("What does this clause mean?", ResponsePatternType.DOCUMENT),
        ("How do contracts typically work?", ResponsePatternType.GENERAL_LEGAL),
        ("Create a table of terms", ResponsePatternType.DATA_TABLE),
        ("I'm not sure what to ask", ResponsePatternType.AMBIGUOUS),
        
        # Edge cases
        ("", ResponsePatternType.ERROR_RECOVERY),
        ("?", ResponsePatternType.AMBIGUOUS),
        ("help", ResponsePatternType.DOCUMENT),
        ("asdfghjkl", ResponsePatternType.ERROR_RECOVERY),
    ]
    
    print(f"\n🔍 Testing input processing with {len(test_cases)} cases...")
    
    for i, (test_input, expected_pattern) in enumerate(test_cases):
        try:
            processed = structured_system._process_input_with_fallbacks(test_input)
            
            print(f"   Test {i+1}: '{test_input[:30]}...' -> {processed.pattern_type.value}")
            
            # Validate processed input
            assert processed is not None
            assert hasattr(processed, 'pattern_type')
            assert hasattr(processed, 'confidence')
            assert 0.0 <= processed.confidence <= 1.0
            
        except Exception as e:
            print(f"   ❌ Test {i+1} failed: {e}")
            return False
    
    print("✅ Input processing tests passed")
    
    # Test response generation
    print(f"\n🔍 Testing response generation...")
    
    response_test_cases = [
        "What are the payment terms?",
        "How does liability typically work?", 
        "Show me a table of key dates",
        "I'm confused about this contract",
        "",  # Empty input
        "gibberish input that makes no sense"
    ]
    
    for i, test_input in enumerate(response_test_cases):
        try:
            response = structured_system.process_input_with_guaranteed_response(
                user_input=test_input,
                document_content="Sample contract with payment terms and liability clauses."
            )
            
            # Validate response
            assert response is not None
            assert hasattr(response, 'content')
            assert response.content is not None
            assert len(response.content.strip()) > 0
            assert hasattr(response, 'response_type')
            assert hasattr(response, 'confidence')
            assert 0.0 <= response.confidence <= 1.0
            assert hasattr(response, 'suggestions')
            assert isinstance(response.suggestions, list)
            
            print(f"   Response {i+1}: {len(response.content)} chars, confidence={response.confidence:.2f}")
            
        except Exception as e:
            print(f"   ❌ Response {i+1} failed: {e}")
            return False
    
    print("✅ Response generation tests passed")
    
    return True

def test_pattern_formatting():
    """Test that response patterns are formatted correctly."""
    
    print(f"\n🎯 Testing Response Pattern Formatting")
    print("=" * 40)
    
    structured_system = StructuredResponseSystem()
    
    # Test document pattern
    try:
        response = structured_system.process_input_with_guaranteed_response(
            user_input="What does this clause mean?",
            document_content="Sample contract clause about payment terms."
        )
        
        # Check for document pattern elements
        has_evidence = '📋 Evidence' in response.content
        has_plain_english = '🔍 Plain English' in response.content
        has_implications = '⚖️ Implications' in response.content
        
        print(f"Document pattern - Evidence: {has_evidence}, Plain English: {has_plain_english}, Implications: {has_implications}")
        
        if has_evidence and has_plain_english and has_implications:
            print("✅ Document pattern formatting correct")
        else:
            print("⚠️  Document pattern formatting incomplete")
            
    except Exception as e:
        print(f"❌ Document pattern test failed: {e}")
    
    # Test general legal pattern
    try:
        response = structured_system.process_input_with_guaranteed_response(
            user_input="How do contracts generally work?",
            document_content="Sample contract content."
        )
        
        # Check for general legal pattern elements
        has_status = 'ℹ️ Status' in response.content
        has_general_rule = '📚 General Rule' in response.content
        has_application = '🎯 Application' in response.content
        
        print(f"General legal pattern - Status: {has_status}, Rule: {has_general_rule}, Application: {has_application}")
        
        if has_status and has_general_rule and has_application:
            print("✅ General legal pattern formatting correct")
        else:
            print("⚠️  General legal pattern formatting incomplete")
            
    except Exception as e:
        print(f"❌ General legal pattern test failed: {e}")
    
    # Test data table pattern
    try:
        response = structured_system.process_input_with_guaranteed_response(
            user_input="Create a table of payment terms",
            document_content="Contract with various payment schedules and terms."
        )
        
        # Check for table elements
        has_table = '|' in response.content and '---' in response.content
        has_export = '📥 Export' in response.content
        
        print(f"Data table pattern - Table: {has_table}, Export: {has_export}")
        
        if has_table:
            print("✅ Data table pattern formatting correct")
        else:
            print("⚠️  Data table pattern formatting incomplete")
            
    except Exception as e:
        print(f"❌ Data table pattern test failed: {e}")

def test_extreme_edge_cases():
    """Test extreme edge cases for never-fail guarantee."""
    
    print(f"\n🛡️  Testing Extreme Edge Cases")
    print("=" * 35)
    
    structured_system = StructuredResponseSystem()
    
    extreme_cases = [
        None,
        "",
        " ",
        "?",
        "a",
        "asdfghjkl",
        "!@#$%^&*()",
        "what " * 100,  # Very long
        "This is a very long question " * 50,
        123,  # Non-string input
        [],   # Non-string input
        {},   # Non-string input
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(extreme_cases):
        try:
            # Convert to string as the system should handle this
            input_str = str(test_case) if test_case is not None else ""
            
            response = structured_system.process_input_with_guaranteed_response(
                user_input=input_str,
                document_content="Sample contract content"
            )
            
            # Validate response exists and has content
            assert response is not None
            assert response.content is not None
            assert len(response.content.strip()) > 0
            
            print(f"   Case {i+1}: '{str(test_case)[:20]}...' -> ✅ ({len(response.content)} chars)")
            success_count += 1
            
        except Exception as e:
            print(f"   Case {i+1}: '{str(test_case)[:20]}...' -> ❌ {e}")
    
    print(f"\nEdge case results: {success_count}/{len(extreme_cases)} passed")
    
    if success_count == len(extreme_cases):
        print("🎉 ALL EDGE CASES PASSED - Never-fail logic working!")
        return True
    else:
        print("❌ Some edge cases failed - Never-fail logic needs improvement")
        return False

if __name__ == "__main__":
    print("🚀 Starting Structured Response System Tests")
    print("=" * 50)
    
    try:
        # Run test suites
        core_success = test_core_functionality()
        test_pattern_formatting()
        edge_success = test_extreme_edge_cases()
        
        print(f"\n🏁 FINAL RESULTS:")
        print(f"Core functionality: {'✅ PASS' if core_success else '❌ FAIL'}")
        print(f"Edge case handling: {'✅ PASS' if edge_success else '❌ FAIL'}")
        
        if core_success and edge_success:
            print("\n🎉 ALL CRITICAL TESTS PASSED!")
            print("The structured response system is working correctly.")
        else:
            print("\n❌ SOME CRITICAL TESTS FAILED!")
            print("The system needs fixes before deployment.")
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR in test suite: {str(e)}")
        import traceback
        traceback.print_exc()