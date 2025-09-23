#!/usr/bin/env python3
"""
Simple test runner to verify enhanced contract assistant functionality
"""

import asyncio
import time
from datetime import datetime
from unittest.mock import Mock

from src.services.enhanced_contract_system import (
    EnhancedContractSystem, SystemConfiguration, ProcessingContext
)
from src.services.answer_quality_enhancer import QuestionComplexity, ExpertiseLevel
from src.services.production_monitor import ProductionMonitor
from src.models.document import Document
from src.storage.document_storage import DocumentStorage


def create_mock_storage():
    """Create mock storage with sample document"""
    storage = Mock(spec=DocumentStorage)
    
    sample_content = """
        MATERIAL TRANSFER AGREEMENT
        
        This Material Transfer Agreement ("Agreement") is entered into between 
        Provider University ("Provider") and Recipient Institution ("Recipient").
        
        1. MATERIAL
        The Provider agrees to transfer cell line ABC-123 for research purposes only.
        
        2. PAYMENT TERMS
        Payment of $500 shall be made within 30 days of material delivery.
        
        3. TERMINATION
        Either party may terminate this agreement with 60 days written notice.
        
        4. LIABILITY
        Provider's liability is limited to direct damages not exceeding $10,000.
        
        5. INTELLECTUAL PROPERTY
        Recipient retains rights to improvements made independently. 
        Provider retains rights to original material.
        
        6. CONFIDENTIALITY
        Both parties agree to maintain confidentiality of proprietary information.
        """
    
    sample_doc = Document(
        id="test_doc_001",
        title="Sample Material Transfer Agreement",
        file_type="pdf",
        file_size=1024,
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
    
    return storage


async def test_basic_functionality():
    """Test basic enhanced system functionality"""
    print("🧪 Testing Basic Enhanced System Functionality")
    print("-" * 50)
    
    # Create system
    storage = create_mock_storage()
    config = SystemConfiguration(
        enable_quality_enhancement=True,
        enable_advanced_analysis=True,
        enable_intelligent_formatting=True,
        enable_production_monitoring=True,
        enable_caching=True
    )
    
    system = EnhancedContractSystem(storage=storage, config=config)
    
    try:
        # Test 1: Basic question processing
        print("\n1. Testing basic question processing...")
        context = ProcessingContext(session_id="test_session")
        
        result = await system.process_question(
            question="What are the payment terms in this agreement?",
            document_id="test_doc_001",
            context=context
        )
        
        assert result is not None, "Result should not be None"
        assert result.response is not None, "Response should not be None"
        assert result.processing_time > 0, "Processing time should be positive"
        assert 0 <= result.quality_score <= 1, "Quality score should be between 0 and 1"
        print("   ✅ Basic question processing works")
        
        # Test 2: Quality enhancement
        print("\n2. Testing quality enhancement...")
        complex_result = await system.process_question(
            question="Provide a comprehensive analysis of the risks in this MTA",
            document_id="test_doc_001",
            context=context
        )
        
        assert complex_result is not None, "Complex result should not be None"
        assert len(complex_result.enhancements_applied) > 0, "Should have enhancements applied"
        print("   ✅ Quality enhancement works")
        
        # Test 3: Advanced document analysis
        print("\n3. Testing advanced document analysis...")
        analysis = await system.analyze_document_comprehensively(
            document_id="test_doc_001",
            analysis_depth="standard"
        )
        
        assert "document_info" in analysis, "Should have document info"
        assert "advanced_analysis" in analysis, "Should have advanced analysis"
        print("   ✅ Advanced document analysis works")
        
        # Test 4: System health monitoring
        print("\n4. Testing system health monitoring...")
        health = await system.get_system_health()
        
        assert "system_health" in health, "Should have system health"
        assert "processing_statistics" in health, "Should have processing statistics"
        print("   ✅ System health monitoring works")
        
        # Test 5: Caching functionality
        print("\n5. Testing caching functionality...")
        # First request
        start_time = time.time()
        result1 = await system.process_question(
            question="What are the termination conditions?",
            document_id="test_doc_001",
            context=context
        )
        time1 = time.time() - start_time
        
        # Second identical request (should be cached)
        start_time = time.time()
        result2 = await system.process_question(
            question="What are the termination conditions?",
            document_id="test_doc_001",
            context=context
        )
        time2 = time.time() - start_time
        
        assert result2.cache_hit is True, "Second request should be cached"
        print("   ✅ Caching functionality works")
        
        # Test 6: Error handling
        print("\n6. Testing error handling...")
        error_result = await system.process_question(
            question="Test question",
            document_id="nonexistent_doc",
            context=context
        )
        
        assert error_result is not None, "Should handle errors gracefully"
        assert error_result.response is not None, "Should provide error response"
        print("   ✅ Error handling works")
        
        print("\n🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    finally:
        system.shutdown()


async def test_production_monitoring():
    """Test production monitoring functionality"""
    print("\n🔍 Testing Production Monitoring")
    print("-" * 50)
    
    try:
        monitor = ProductionMonitor()
        
        # Test health checks
        print("\n1. Testing health checks...")
        monitor.start_monitoring()
        
        # Wait a moment for monitoring to start
        await asyncio.sleep(1)
        
        health_status = monitor.get_health_status()
        assert "overall_status" in health_status, "Should have overall status"
        assert "checks" in health_status, "Should have individual checks"
        print("   ✅ Health checks work")
        
        # Test metrics recording
        print("\n2. Testing metrics recording...")
        monitor.record_metric("test_metric", 42.0)
        monitor.record_response_time(1.5, "test_endpoint")
        
        metrics = monitor.get_performance_metrics(5)  # Last 5 minutes
        assert "metrics" in metrics, "Should have metrics"
        print("   ✅ Metrics recording works")
        
        # Test production readiness
        print("\n3. Testing production readiness validation...")
        readiness = monitor.validate_production_readiness()
        assert "production_ready" in readiness, "Should have production ready status"
        assert "checks" in readiness, "Should have readiness checks"
        assert "recommendations" in readiness, "Should have recommendations"
        print("   ✅ Production readiness validation works")
        
        monitor.stop_monitoring()
        print("\n🎉 All production monitoring tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Production monitoring test failed: {e}")
        return False


async def test_answer_quality_enhancement():
    """Test answer quality enhancement features"""
    print("\n🎯 Testing Answer Quality Enhancement")
    print("-" * 50)
    
    try:
        from src.services.answer_quality_enhancer import AnswerQualityEnhancer
        from src.models.enhanced import EnhancedResponse, ResponseType, ToneType
        from datetime import datetime
        
        enhancer = AnswerQualityEnhancer()
        storage = create_mock_storage()
        document = storage.get_document("test_doc_001")
        
        # Create sample response
        sample_response = EnhancedResponse(
            content="The payment terms require $500 within 30 days of delivery.",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.8,
            sources=["document"],
            suggestions=["What about late payment penalties?"],
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=["document_analysis"],
            timestamp=datetime.now()
        )
        
        print("\n1. Testing quality enhancement...")
        enhanced_response = enhancer.enhance_response_quality(
            response=sample_response,
            document=document,
            question="What are the payment terms?",
            user_expertise=ExpertiseLevel.INTERMEDIATE
        )
        
        assert enhanced_response is not None, "Enhanced response should not be None"
        assert len(enhanced_response.content) >= len(sample_response.content), "Enhanced content should be longer or equal"
        print("   ✅ Quality enhancement works")
        
        print("\n2. Testing complexity assessment...")
        complexity = enhancer._assess_question_complexity("What are the payment terms?")
        assert complexity in QuestionComplexity, "Should return valid complexity"
        print("   ✅ Complexity assessment works")
        
        print("\n🎉 All answer quality enhancement tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Answer quality enhancement test failed: {e}")
        return False


async def test_intelligent_formatting():
    """Test intelligent response formatting"""
    print("\n🎨 Testing Intelligent Response Formatting")
    print("-" * 50)
    
    try:
        from src.services.intelligent_response_formatter import IntelligentResponseFormatter
        from src.models.enhanced import EnhancedResponse, ResponseType, ToneType
        from datetime import datetime
        
        formatter = IntelligentResponseFormatter()
        
        # Create sample response
        sample_response = EnhancedResponse(
            content="The liability provisions limit damages to $10,000 in direct damages only.",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.8,
            sources=["document"],
            suggestions=[],
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=["document_analysis"],
            timestamp=datetime.now()
        )
        
        print("\n1. Testing expertise detection...")
        expertise = formatter._detect_expertise_level("What does liability mean?", [])
        assert expertise in ExpertiseLevel, "Should return valid expertise level"
        print("   ✅ Expertise detection works")
        
        print("\n2. Testing response formatting...")
        formatted_response = formatter.format_intelligent_response(
            response=sample_response,
            question="What are the liability provisions?",
            question_complexity=QuestionComplexity.MODERATE
        )
        
        assert formatted_response is not None, "Formatted response should not be None"
        assert hasattr(formatted_response, 'formatting_metadata'), "Should have formatting metadata"
        print("   ✅ Response formatting works")
        
        print("\n🎉 All intelligent formatting tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Intelligent formatting test failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("🚀 Enhanced Contract Assistant System - Test Suite")
    print("=" * 60)
    
    test_results = []
    
    # Run individual test suites
    test_results.append(await test_basic_functionality())
    test_results.append(await test_production_monitoring())
    test_results.append(await test_answer_quality_enhancement())
    test_results.append(await test_intelligent_formatting())
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is working correctly.")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} test suite(s) failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)