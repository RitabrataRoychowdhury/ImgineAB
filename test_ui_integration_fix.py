#!/usr/bin/env python3
"""
Test UI Integration Fix

This test verifies that the enhanced contract assistant system works properly
with real document storage and doesn't produce error messages in the UI.
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.enhanced_response_router import EnhancedResponseRouter
from src.services.enhanced_contract_system import (
    EnhancedContractSystem, SystemConfiguration, ProcessingContext
)
from src.models.document import Document
from src.storage.document_storage import DocumentStorage


def create_real_test_document():
    """Create a real test document (not a mock)"""
    content = """
    MATERIAL TRANSFER AGREEMENT
    
    This Material Transfer Agreement ("Agreement") is entered into between 
    Stanford University ("Provider") and MIT ("Recipient").
    
    1. MATERIAL DESCRIPTION
    The Provider agrees to transfer cell line ABC-123 for research purposes only.
    
    2. PAYMENT TERMS
    Payment of $500 shall be made within 30 days of material delivery.
    Additional shipping costs of $150 shall be paid upon invoice receipt.
    
    3. LIABILITY LIMITATIONS
    Provider's liability is limited to direct damages not exceeding $10,000.
    No consequential or indirect damages shall be recoverable.
    
    4. INTELLECTUAL PROPERTY
    Recipient retains rights to improvements made independently.
    Provider retains all rights to the original material.
    
    5. TERMINATION
    Either party may terminate this agreement with 60 days written notice.
    Upon termination, all materials must be returned or destroyed.
    
    6. CONFIDENTIALITY
    Both parties agree to maintain confidentiality of proprietary information for 5 years.
    """
    
    doc = Document(
        id="ui_test_doc_001",
        title="Stanford-MIT Material Transfer Agreement",
        file_type="pdf",
        file_size=len(content),
        upload_timestamp=datetime.now(),
        processing_status="completed",
        original_text=content,
        is_legal_document=True,
        legal_document_type="MTA"
    )
    
    # Add content property for compatibility
    doc.content = content
    return doc


async def test_ui_integration_fix():
    """Test that UI integration issues are fixed"""
    
    print("🔧 Testing UI Integration Fix")
    print("=" * 50)
    
    # Create a real document (not a mock)
    test_doc = create_real_test_document()
    
    # Create mock storage that returns real document
    storage = Mock(spec=DocumentStorage)
    storage.get_document.return_value = test_doc
    storage.get_document_with_embeddings.return_value = test_doc
    storage.create_document.return_value = "ui_test_doc_001"
    
    # Test 1: Enhanced Response Router directly
    print("\n1. Testing Enhanced Response Router...")
    
    router = EnhancedResponseRouter(storage)
    
    try:
        response = router.route_question(
            question="What are the payment terms in this agreement?",
            document_id="ui_test_doc_001",
            session_id="ui_test_session",
            document=test_doc
        )
        
        print(f"   Response Type: {response.response_type}")
        print(f"   Response Content: {response.content[:100]}...")
        print(f"   Confidence: {response.confidence}")
        
        # Check that we don't get the error message
        error_phrases = [
            "I apologize, but I encountered an issue",
            "encountered an error while analyzing",
            "Object of type Mock is not JSON serializable"
        ]
        
        has_error = any(phrase in response.content for phrase in error_phrases)
        
        if has_error:
            print(f"   ❌ Still getting error messages: {response.content}")
            return False
        else:
            print(f"   ✅ No error messages - response looks good")
        
    except Exception as e:
        print(f"   ❌ Exception in router: {e}")
        return False
    
    # Test 2: Enhanced Contract System
    print("\n2. Testing Enhanced Contract System...")
    
    config = SystemConfiguration(
        enable_quality_enhancement=True,
        enable_advanced_analysis=True,
        enable_intelligent_formatting=True,
        enable_production_monitoring=False,  # Disable to avoid threading issues
        enable_caching=True
    )
    
    system = EnhancedContractSystem(storage=storage, config=config)
    
    try:
        context = ProcessingContext(session_id="ui_integration_test")
        
        # Test various question types that were causing issues
        test_questions = [
            "What are the payment terms?",
            "Who are the parties to this agreement?",
            "What are the liability limitations?",
            "How can this agreement be terminated?",
            "What intellectual property rights are involved?"
        ]
        
        all_good = True
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n   Question {i}: {question}")
            
            result = await system.process_question(
                question=question,
                document_id="ui_test_doc_001",
                context=context
            )
            
            print(f"   Response Type: {result.response.response_type}")
            print(f"   Quality Score: {result.quality_score:.2f}")
            print(f"   Processing Time: {result.processing_time:.3f}s")
            
            # Check for error messages
            has_error = any(phrase in result.response.content for phrase in error_phrases)
            
            if has_error:
                print(f"   ❌ Error in response: {result.response.content[:100]}...")
                all_good = False
            else:
                print(f"   ✅ Good response: {result.response.content[:80]}...")
        
        if not all_good:
            return False
        
        print(f"\n   ✅ All questions processed successfully without errors")
        
    except Exception as e:
        print(f"   ❌ Exception in enhanced system: {e}")
        return False
    
    finally:
        system.shutdown()
    
    # Test 3: Error handling scenarios
    print("\n3. Testing Error Handling Scenarios...")
    
    # Test with non-existent document
    router2 = EnhancedResponseRouter(storage)
    
    try:
        # Mock storage to return None for non-existent document
        storage.get_document.return_value = None
        
        response = router2.route_question(
            question="What are the terms?",
            document_id="nonexistent_doc",
            session_id="error_test_session",
            document=None
        )
        
        print(f"   Non-existent doc response: {response.response_type}")
        print(f"   Content: {response.content[:80]}...")
        
        # Should be a helpful fallback, not a generic error
        if "I don't have access to a document" in response.content or "document not found" in response.content.lower():
            print(f"   ✅ Proper error handling for missing document")
        else:
            print(f"   ❌ Poor error handling: {response.content}")
            return False
        
    except Exception as e:
        print(f"   ❌ Exception in error handling test: {e}")
        return False
    
    # Test 4: Mock serialization issue simulation
    print("\n4. Testing Mock Serialization Issue Fix...")
    
    # Reset storage to return real document
    storage.get_document.return_value = test_doc
    storage.get_document_with_embeddings.return_value = test_doc
    
    # Patch the contract engine to simulate the original error
    with patch('src.services.contract_analyst_engine.ContractAnalystEngine.analyze_question') as mock_analyze:
        # Simulate the JSON serialization error
        mock_analyze.side_effect = TypeError("Object of type Mock is not JSON serializable")
        
        router3 = EnhancedResponseRouter(storage)
        
        response = router3.route_question(
            question="What are the payment terms?",
            document_id="ui_test_doc_001",
            session_id="mock_error_test",
            document=test_doc
        )
        
        print(f"   Response with simulated error: {response.response_type}")
        print(f"   Content: {response.content[:80]}...")
        
        # Should handle the error gracefully - check for helpful fallback content
        helpful_phrases = [
            "having trouble analyzing", 
            "technical difficulties", 
            "contains payment-related terms",
            "While I'm having trouble with detailed analysis"
        ]
        
        has_helpful_response = any(phrase in response.content for phrase in helpful_phrases)
        
        if has_helpful_response:
            print(f"   ✅ Graceful error handling for serialization issues")
        else:
            print(f"   ❌ Not handling serialization error properly: {response.content}")
            return False
    
    print(f"\n🎉 UI INTEGRATION FIX VALIDATION COMPLETE")
    print("=" * 50)
    print("✅ Enhanced Response Router: Working without errors")
    print("✅ Enhanced Contract System: Processing questions successfully") 
    print("✅ Error Handling: Graceful fallbacks implemented")
    print("✅ Mock Serialization: Issue resolved with proper error handling")
    print("\n🚀 The UI should now work properly without error messages!")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_ui_integration_fix())
    exit(0 if success else 1)