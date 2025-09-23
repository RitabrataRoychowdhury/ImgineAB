#!/usr/bin/env python3
"""
Test script to verify UI integration fix.
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def test_basic_qa_interface():
    """Test basic QA interface functionality."""
    print("🧪 Testing basic QA interface functionality...")
    
    try:
        # Import required modules
        from src.ui.qa_interface import EnhancedQAInterface
        from src.models.document import Document
        from src.storage.document_storage import DocumentStorage
        
        # Create a temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Initialize storage with temporary database
        storage = DocumentStorage(db_path)
        
        # Create a test document
        test_doc = Document(
            id="test_doc_1",
            title="Test MTA Agreement",
            original_text="This is a Material Transfer Agreement between Party A and Party B. The agreement covers the transfer of research materials for scientific purposes.",
            file_path="test_mta.txt",
            upload_date=None,
            is_legal_document=True,
            legal_document_type="MTA"
        )
        
        # Save document to storage
        storage.save_document(test_doc)
        
        # Initialize QA interface
        qa_interface = EnhancedQAInterface()
        qa_interface.storage = storage
        
        # Test engine initialization
        qa_interface._ensure_engines_initialized()
        
        print("✅ Basic QA interface initialization successful")
        
        # Test fallback response generation
        fallback_response = qa_interface._generate_helpful_fallback_response(
            "Who are the parties in this agreement?", 
            test_doc
        )
        
        print(f"✅ Fallback response generated: {fallback_response[:100]}...")
        
        # Clean up
        os.unlink(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_contract_engine_basic():
    """Test basic contract engine functionality."""
    print("🧪 Testing basic contract engine functionality...")
    
    try:
        from src.services.contract_analyst_engine import ContractAnalystEngine
        from src.storage.document_storage import DocumentStorage
        from src.models.document import Document
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        storage = DocumentStorage(db_path)
        
        # Create test document
        test_doc = Document(
            id="test_doc_2",
            title="Test Contract",
            original_text="""
            MATERIAL TRANSFER AGREEMENT
            
            This agreement is between ImaginAb Inc. and MedicaNova Research Institute.
            
            1. PARTIES
            Provider: ImaginAb Inc., a Delaware corporation
            Recipient: MedicaNova Research Institute, a UK research organization
            
            2. MATERIALS
            The materials being transferred include research antibodies for imaging studies.
            
            3. PERMITTED USE
            Materials are for research use only, not for use in humans.
            """,
            file_path="test_contract.txt",
            upload_date=None
        )
        
        storage.save_document(test_doc)
        
        # Initialize contract engine
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        engine = ContractAnalystEngine(storage, api_key)
        
        # Test question answering
        result = engine.answer_question(
            "Who are the parties in this agreement?",
            test_doc.id
        )
        
        print(f"✅ Contract engine response: {result.get('answer', 'No answer')[:100]}...")
        
        # Clean up
        os.unlink(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Contract engine test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting UI integration fix tests...")
    print("=" * 50)
    
    tests = [
        test_basic_qa_interface,
        test_contract_engine_basic
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
        print("🎉 All tests passed! UI integration fix appears to be working.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)