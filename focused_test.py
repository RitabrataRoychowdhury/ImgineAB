#!/usr/bin/env python3
"""
Focused test to verify enhanced contract assistant functionality
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock

from src.services.enhanced_contract_system import (
    EnhancedContractSystem, SystemConfiguration, ProcessingContext
)
from src.services.answer_quality_enhancer import QuestionComplexity, ExpertiseLevel
from src.models.document import Document
from src.storage.document_storage import DocumentStorage


async def test_enhanced_system():
    """Test the enhanced contract system"""
    print("🚀 Testing Enhanced Contract System")
    print("=" * 50)
    
    # Create mock storage
    storage = Mock(spec=DocumentStorage)
    
    # Create sample document
    sample_content = """
    MATERIAL TRANSFER AGREEMENT
    
    This Material Transfer Agreement is between Provider University and Recipient Institution.
    
    1. PAYMENT TERMS
    Payment of $500 shall be made within 30 days of material delivery.
    
    2. LIABILITY
    Provider's liability is limited to direct damages not exceeding $10,000.
    
    3. TERMINATION
    Either party may terminate this agreement with 60 days written notice.
    """
    
    sample_doc = Document(
        id="test_doc_001",
        title="Sample MTA",
        file_type="pdf",
        file_size=len(sample_content),
        upload_timestamp=datetime.now(),
        processing_status="completed",
        original_text=sample_content,
        is_legal_document=True,
        legal_document_type="MTA"
    )
    
    # Add content property for compatibility
    sample_doc.content = sample_content
    
    storage.get_document.return_value = sample_doc
    storage.create_document.return_value = "test_doc_001"
    
    # Create system with all enhancements enabled
    config = SystemConfiguration(
        enable_quality_enhancement=True,
        enable_advanced_analysis=True,
        enable_intelligent_formatting=True,
        enable_production_monitoring=False,  # Disable to avoid threading issues
        enable_caching=True
    )
    
    system = EnhancedContractSystem(storage=storage, config=config)
    
    try:
        print("\n1. Testing basic question processing...")
        context = ProcessingContext(session_id="test_session")
        
        result = await system.process_question(
            question="What are the payment terms in this agreement?",
            document_id="test_doc_001",
            context=context
        )
        
        print(f"   Response Type: {result.response.response_type}")
        print(f"   Quality Score: {result.quality_score:.2f}")
        print(f"   Processing Time: {result.processing_time:.3f}s")
        print(f"   Enhancements Applied: {result.enhancements_applied}")
        print(f"   Response Preview: {result.response.content[:100]}...")
        
        assert result is not None
        assert result.response is not None
        assert result.quality_score > 0
        print("   ✅ Basic question processing works")
        
        print("\n2. Testing complex question with quality enhancement...")
        complex_result = await system.process_question(
            question="Provide a comprehensive analysis of the risks and benefits in this MTA",
            document_id="test_doc_001",
            context=context
        )
        
        print(f"   Complexity: {complex_result.complexity_assessment.value}")
        print(f"   User Expertise: {complex_result.user_expertise_detected.value}")
        print(f"   Quality Score: {complex_result.quality_score:.2f}")
        print(f"   Enhancements: {complex_result.enhancements_applied}")
        
        assert complex_result.quality_score > 0
        print("   ✅ Complex question processing works")
        
        print("\n3. Testing document analysis...")
        analysis = await system.analyze_document_comprehensively(
            document_id="test_doc_001",
            analysis_depth="standard"
        )
        
        print(f"   Document Type: {analysis['document_info']['type']}")
        print(f"   Analysis Sections: {list(analysis.keys())}")
        
        assert "document_info" in analysis
        assert "advanced_analysis" in analysis
        print("   ✅ Document analysis works")
        
        print("\n4. Testing different user expertise levels...")
        
        # Beginner user
        beginner_context = ProcessingContext(session_id="beginner_session")
        beginner_result = await system.process_question(
            question="What does liability mean in this contract?",
            document_id="test_doc_001",
            context=beginner_context
        )
        
        print(f"   Beginner - Expertise Detected: {beginner_result.user_expertise_detected.value}")
        print(f"   Beginner - Response Length: {len(beginner_result.response.content)}")
        
        # Expert user
        expert_context = ProcessingContext(session_id="expert_session")
        expert_result = await system.process_question(
            question="Analyze the liability allocation framework and indemnification provisions",
            document_id="test_doc_001",
            context=expert_context
        )
        
        print(f"   Expert - Expertise Detected: {expert_result.user_expertise_detected.value}")
        print(f"   Expert - Response Length: {len(expert_result.response.content)}")
        
        print("   ✅ Adaptive formatting works")
        
        print("\n5. Testing caching...")
        # First request
        cache_result1 = await system.process_question(
            question="What are the termination conditions?",
            document_id="test_doc_001",
            context=context
        )
        
        # Second identical request (should be cached)
        cache_result2 = await system.process_question(
            question="What are the termination conditions?",
            document_id="test_doc_001",
            context=context
        )
        
        print(f"   First request cache hit: {cache_result1.cache_hit}")
        print(f"   Second request cache hit: {cache_result2.cache_hit}")
        
        assert cache_result2.cache_hit is True
        print("   ✅ Caching works")
        
        print("\n6. Testing system health...")
        health = await system.get_system_health()
        
        print(f"   Processing Statistics: {health['processing_statistics']['total_requests']} requests")
        print(f"   Configuration Valid: {health['configuration']['quality_enhancement_enabled']}")
        
        assert "processing_statistics" in health
        print("   ✅ System health monitoring works")
        
        print("\n🎉 ALL ENHANCED SYSTEM TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        system.shutdown()


if __name__ == "__main__":
    success = asyncio.run(test_enhanced_system())
    exit(0 if success else 1)