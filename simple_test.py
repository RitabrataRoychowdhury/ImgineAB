#!/usr/bin/env python3
"""
Simple test to verify basic functionality
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock

from src.services.answer_quality_enhancer import AnswerQualityEnhancer, QuestionComplexity, ExpertiseLevel
from src.services.production_monitor import ProductionMonitor
from src.models.enhanced import EnhancedResponse, ResponseType, ToneType
from src.models.document import Document
from src.storage.document_storage import DocumentStorage


def test_answer_quality_enhancer():
    """Test answer quality enhancer"""
    print("🧪 Testing Answer Quality Enhancer...")
    
    try:
        enhancer = AnswerQualityEnhancer()
        
        # Create sample document
        sample_doc = Document(
            id="test_doc",
            title="Test Document",
            file_type="pdf",
            file_size=1024,
            upload_timestamp=datetime.now(),
            original_text="This is a test contract with payment terms of $500."
        )
        
        # Create sample response
        response = EnhancedResponse(
            content="The payment terms are $500.",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.8,
            sources=["document"],
            suggestions=[],
            tone=ToneType.PROFESSIONAL,
            structured_format=None,
            context_used=[],
            timestamp=datetime.now()
        )
        
        # Test quality enhancement
        enhanced = enhancer.enhance_response_quality(
            response=response,
            document=sample_doc,
            question="What are the payment terms?",
            user_expertise=ExpertiseLevel.INTERMEDIATE
        )
        
        assert enhanced is not None
        print("   ✅ Answer quality enhancement works")
        
        # Test complexity assessment
        complexity = enhancer._assess_question_complexity("What are the payment terms?")
        assert complexity in QuestionComplexity
        print("   ✅ Question complexity assessment works")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_production_monitor():
    """Test production monitor"""
    print("🔍 Testing Production Monitor...")
    
    try:
        monitor = ProductionMonitor()
        
        # Test metric recording
        monitor.record_metric("test_metric", 42.0)
        print("   ✅ Metric recording works")
        
        # Test health status
        health = monitor.get_health_status()
        assert "overall_status" in health
        print("   ✅ Health status works")
        
        # Test performance metrics
        metrics = monitor.get_performance_metrics()
        assert "timestamp" in metrics
        print("   ✅ Performance metrics work")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_basic_imports():
    """Test that all imports work"""
    print("📦 Testing Basic Imports...")
    
    try:
        from src.services.enhanced_contract_system import EnhancedContractSystem
        from src.services.intelligent_response_formatter import IntelligentResponseFormatter
        from src.services.advanced_document_analyzer import AdvancedDocumentAnalyzer
        from src.services.comprehensive_test_suite import ComprehensiveTestSuite
        
        print("   ✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False


async def run_simple_tests():
    """Run simple tests"""
    print("🚀 Enhanced Contract Assistant - Simple Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(await test_basic_imports())
    
    # Test individual components
    results.append(test_answer_quality_enhancer())
    results.append(test_production_monitor())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 SIMPLE TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL SIMPLE TESTS PASSED!")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_simple_tests())
    exit(0 if success else 1)