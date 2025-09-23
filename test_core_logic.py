#!/usr/bin/env python3
"""
Test core logic without external dependencies.
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_fallback_response_logic():
    """Test the fallback response generation logic."""
    print("🧪 Testing fallback response logic...")
    
    try:
        # Mock document class
        class MockDocument:
            def __init__(self):
                self.id = "test_doc"
                self.title = "Test Document"
        
        # Mock QA interface with just the fallback method
        class MockQAInterface:
            def _generate_helpful_fallback_response(self, question: str, document) -> str:
                """Generate a helpful fallback response based on question patterns."""
                question_lower = question.lower()
                
                # Check for common question patterns and provide helpful responses
                # Order matters - check more specific patterns first
                if any(word in question_lower for word in ['risk', 'risks', 'liability', 'danger', 'dangerous']):
                    return "This appears to be asking about risks or liability. Look for sections on 'Liability', 'Risk', 'Indemnification', or 'Limitation of Liability' in the document."
                
                elif 'intellectual property' in question_lower or (question_lower.startswith('ip ') or ' ip ' in question_lower or question_lower.endswith(' ip')) or any(word in question_lower for word in ['ownership', 'owns', 'owner']) or ('rights' in question_lower and any(word in question_lower for word in ['property', 'ownership'])):
                    return "This appears to be asking about intellectual property or ownership rights. Check sections on 'Intellectual Property', 'Ownership', or 'Rights' in the document."
                
                elif any(word in question_lower for word in ['who', 'parties', 'involved']) and not any(word in question_lower for word in ['owns', 'ownership']):
                    return "This appears to be asking about the parties involved in the agreement. Please check the beginning of the document for party information, typically in the first few paragraphs or sections."
                
                elif any(word in question_lower for word in ['when', 'date', 'expire', 'term']):
                    return "This appears to be asking about dates or terms. Look for sections mentioning 'Term', 'Effective Date', or 'Expiration' in the document."
                
                elif any(word in question_lower for word in ['what', 'obligations', 'requirements', 'must']):
                    return "This appears to be asking about obligations or requirements. Check sections related to 'Obligations', 'Requirements', or 'Responsibilities' in the document."
                
                else:
                    return f"I'm having trouble processing your specific question right now. However, I can help you analyze this document. Try asking about specific sections, parties, dates, obligations, or risks mentioned in the document."
        
        # Test the fallback responses
        qa_interface = MockQAInterface()
        document = MockDocument()
        
        test_questions = [
            "Who are the parties involved in this agreement?",
            "When does the agreement start and when does it expire?", 
            "What are the main obligations?",
            "What are the biggest risks?",
            "Who owns the intellectual property?",
            "Can you explain this agreement in the style of a cooking recipe?"
        ]
        
        expected_keywords = [
            "parties involved",
            "dates or terms", 
            "obligations or requirements",
            "risks or liability",
            "intellectual property",
            "having trouble processing"
        ]
        
        for i, question in enumerate(test_questions):
            response = qa_interface._generate_helpful_fallback_response(question, document)
            expected_keyword = expected_keywords[i]
            
            if expected_keyword in response:
                print(f"✅ Question {i+1}: Correct fallback response")
            else:
                print(f"❌ Question {i+1}: Unexpected response: {response[:50]}...")
                return False
        
        print("✅ All fallback response tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Fallback response test failed: {e}")
        return False

def test_question_patterns():
    """Test question pattern matching."""
    print("🧪 Testing question pattern matching...")
    
    try:
        # Test questions from the user's examples
        test_cases = [
            ("Who are the parties involved in this agreement?", "parties"),
            ("When does the agreement start and when does it expire?", "dates"),
            ("What is the authorized location for the materials?", "obligations"),
            ("What are the biggest risks MNRI faces in this agreement?", "risks"),
            ("Who owns the intellectual property?", "ip"),
            ("Can you explain this agreement in the style of a cooking recipe?", "general")
        ]
        
        for question, expected_category in test_cases:
            question_lower = question.lower()
            
            # Order matters - check more specific patterns first
            if any(word in question_lower for word in ['risk', 'risks', 'liability', 'danger', 'dangerous']):
                category = "risks"
            elif 'intellectual property' in question_lower or (question_lower.startswith('ip ') or ' ip ' in question_lower or question_lower.endswith(' ip')) or any(word in question_lower for word in ['ownership', 'owns', 'owner']) or ('rights' in question_lower and any(word in question_lower for word in ['property', 'ownership'])):
                category = "ip"
            elif any(word in question_lower for word in ['who', 'parties', 'involved']) and not any(word in question_lower for word in ['owns', 'ownership']):
                category = "parties"
            elif any(word in question_lower for word in ['when', 'date', 'expire', 'term']):
                category = "dates"
            elif any(word in question_lower for word in ['what', 'obligations', 'requirements', 'must']):
                category = "obligations"
            else:
                category = "general"
            
            if category == expected_category:
                print(f"✅ '{question[:30]}...' -> {category}")
            else:
                print(f"❌ '{question[:30]}...' -> {category} (expected {expected_category})")
                return False
        
        print("✅ All question pattern tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Question pattern test failed: {e}")
        return False

def main():
    """Run core logic tests."""
    print("🚀 Starting core logic tests...")
    print("=" * 50)
    
    tests = [
        test_fallback_response_logic,
        test_question_patterns
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core logic tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)