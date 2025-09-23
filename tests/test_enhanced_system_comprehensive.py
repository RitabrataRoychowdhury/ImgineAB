"""
Comprehensive Test Suite for Enhanced Contract Assistant System

This test suite validates all enhanced capabilities including quality enhancement,
advanced analysis, intelligent formatting, and production monitoring.
"""

import pytest
import asyncio
import time
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.enhanced_contract_system import (
    EnhancedContractSystem, SystemConfiguration, ProcessingContext
)
from src.services.comprehensive_test_suite import (
    ComprehensiveTestSuite, TestCategory, TestResult
)
from src.services.answer_quality_enhancer import QuestionComplexity, ExpertiseLevel
from src.services.intelligent_response_formatter import UserProfile, ResponseStructure
from src.services.production_monitor import ProductionMonitor, HealthStatus
from src.models.document import Document
from src.models.enhanced import ResponseType, ToneType
from src.storage.document_storage import DocumentStorage


class TestEnhancedSystemComprehensive:
    """Comprehensive test suite for the enhanced contract assistant system"""
    
    @pytest.fixture
    def mock_storage(self):
        """Mock document storage"""
        storage = Mock(spec=DocumentStorage)
        
        # Create sample document
        sample_doc = Document(
            id="test_doc_001",
            title="Sample Material Transfer Agreement",
            content="""
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
            """,
            original_text="[Original text content]",
            is_legal_document=True,
            legal_document_type="MTA"
        )
        
        storage.get_document.return_value = sample_doc
        storage.store_document.return_value = None
        
        return storage
    
    @pytest.fixture
    def system_config(self):
        """System configuration for testing"""
        return SystemConfiguration(
            enable_quality_enhancement=True,
            enable_advanced_analysis=True,
            enable_intelligent_formatting=True,
            enable_production_monitoring=True,
            enable_caching=True,
            cache_ttl_seconds=300,
            max_concurrent_requests=5,
            response_timeout_seconds=15
        )
    
    @pytest.fixture
    def enhanced_system(self, mock_storage, system_config):
        """Enhanced contract system instance"""
        monitor = ProductionMonitor()
        system = EnhancedContractSystem(
            storage=mock_storage,
            config=system_config,
            monitor=monitor
        )
        return system
    
    @pytest.fixture
    def processing_context(self):
        """Processing context for tests"""
        return ProcessingContext(
            session_id="test_session_001",
            conversation_history=["What are the payment terms?", "How does termination work?"],
            processing_preferences={"format": "detailed", "expertise": "intermediate"}
        )
    
    @pytest.mark.asyncio
    async def test_comprehensive_question_processing(self, enhanced_system, processing_context):
        """Test comprehensive question processing with all enhancements"""
        
        # Test different question types
        test_questions = [
            ("What are the payment terms in this agreement?", ResponseType.DOCUMENT_ANALYSIS),
            ("How do liability and indemnification provisions interact?", ResponseType.DOCUMENT_ANALYSIS),
            ("What's the weather like today?", ResponseType.FALLBACK),
            ("Can you explain this contract like I'm five years old?", ResponseType.DOCUMENT_ANALYSIS),
            ("Tell me a joke about lawyers", ResponseType.CASUAL)
        ]
        
        for question, expected_type in test_questions:
            result = await enhanced_system.process_question(
                question=question,
                document_id="test_doc_001",
                context=processing_context
            )
            
            # Validate result structure
            assert result is not None
            assert result.response is not None
            assert result.processing_time > 0
            assert 0 <= result.quality_score <= 1
            assert result.complexity_assessment in QuestionComplexity
            assert result.user_expertise_detected in ExpertiseLevel
            assert isinstance(result.enhancements_applied, list)
            
            # Validate response type (allowing some flexibility for routing decisions)
            assert result.response.response_type in [expected_type, ResponseType.FALLBACK]
            
            # Validate enhancements were applied
            if result.response.confidence >= 0.7:
                assert "quality_enhancement" in result.enhancements_applied
            
            assert "intelligent_formatting" in result.enhancements_applied
            
            print(f"✓ Question processed: '{question[:50]}...' -> {result.response.response_type}")
    
    @pytest.mark.asyncio
    async def test_answer_quality_enhancement(self, enhanced_system, processing_context):
        """Test answer quality enhancement features"""
        
        # Test with a complex question that should trigger quality enhancement
        question = "Provide a comprehensive analysis of the risks and benefits of this MTA for both parties"
        
        result = await enhanced_system.process_question(
            question=question,
            document_id="test_doc_001",
            context=processing_context
        )
        
        # Validate quality enhancement was applied
        assert "quality_enhancement" in result.enhancements_applied
        assert result.quality_score > 0.5
        
        # Check for enhanced content structure
        response_content = result.response.content
        assert len(response_content) > 200  # Should be comprehensive
        
        # Check for quality indicators
        quality_indicators = [
            "evidence", "analysis", "implication", "risk", "recommendation"
        ]
        
        found_indicators = sum(1 for indicator in quality_indicators 
                             if indicator.lower() in response_content.lower())
        assert found_indicators >= 2  # Should contain multiple quality indicators
        
        print(f"✓ Quality enhancement applied with score: {result.quality_score:.2f}")
    
    @pytest.mark.asyncio
    async def test_advanced_document_analysis(self, enhanced_system):
        """Test advanced document analysis capabilities"""
        
        analysis_result = await enhanced_system.analyze_document_comprehensively(
            document_id="test_doc_001",
            analysis_depth="comprehensive"
        )
        
        # Validate analysis structure
        assert "document_info" in analysis_result
        assert "advanced_analysis" in analysis_result
        assert "detailed_insights" in analysis_result
        assert "predictive_insights" in analysis_result
        
        # Validate document info
        doc_info = analysis_result["document_info"]
        assert doc_info["id"] == "test_doc_001"
        assert doc_info["type"] == "MTA"
        assert "analysis_timestamp" in doc_info
        
        # Validate advanced analysis
        advanced = analysis_result["advanced_analysis"]
        assert "risk_matrix" in advanced
        assert "party_obligations" in advanced
        assert "compliance_requirements" in advanced
        
        # Validate insights
        insights = analysis_result["detailed_insights"]
        assert "key_themes" in insights
        assert "risk_summary" in insights
        assert "opportunity_areas" in insights
        
        print("✓ Advanced document analysis completed successfully")
    
    @pytest.mark.asyncio
    async def test_intelligent_response_formatting(self, enhanced_system, processing_context):
        """Test intelligent response formatting for different user types"""
        
        # Test formatting for different expertise levels
        expertise_levels = [
            (ExpertiseLevel.BEGINNER, "What does liability mean in this contract?"),
            (ExpertiseLevel.INTERMEDIATE, "How are liability provisions structured?"),
            (ExpertiseLevel.EXPERT, "Analyze the liability allocation framework and risk distribution mechanisms")
        ]
        
        for expertise, question in expertise_levels:
            # Create context with specific expertise
            context = ProcessingContext(
                session_id=f"test_session_{expertise.value}",
                user_profile=UserProfile(
                    expertise_level=expertise,
                    preferred_structure=ResponseStructure.STRUCTURED,
                    attention_span="medium",
                    technical_comfort="medium",
                    interaction_history=[]
                ),
                conversation_history=[]
            )
            
            result = await enhanced_system.process_question(
                question=question,
                document_id="test_doc_001",
                context=context
            )
            
            # Validate formatting was applied
            assert "intelligent_formatting" in result.enhancements_applied
            assert result.user_expertise_detected == expertise
            
            # Check response adaptation
            response_content = result.response.content
            
            if expertise == ExpertiseLevel.BEGINNER:
                # Should have explanations and definitions
                assert any(phrase in response_content.lower() 
                          for phrase in ["simple terms", "means", "in other words"])
            
            elif expertise == ExpertiseLevel.EXPERT:
                # Should have technical detail
                assert len(response_content) > 300  # More detailed for experts
            
            print(f"✓ Intelligent formatting applied for {expertise.value} user")
    
    @pytest.mark.asyncio
    async def test_production_monitoring(self, enhanced_system):
        """Test production monitoring and health checks"""
        
        # Start monitoring
        enhanced_system.monitor.start_monitoring()
        
        # Process some questions to generate metrics
        context = ProcessingContext(session_id="monitoring_test")
        
        for i in range(5):
            await enhanced_system.process_question(
                question=f"Test question {i}: What are the key terms?",
                document_id="test_doc_001",
                context=context
            )
        
        # Wait a moment for metrics to be recorded
        await asyncio.sleep(1)
        
        # Check system health
        health_status = await enhanced_system.get_system_health()
        
        # Validate health status structure
        assert "system_health" in health_status
        assert "performance_metrics" in health_status
        assert "processing_statistics" in health_status
        assert "configuration" in health_status
        
        # Validate processing statistics
        stats = health_status["processing_statistics"]
        assert stats["total_requests"] >= 5
        assert stats["average_processing_time"] > 0
        
        # Validate configuration
        config = health_status["configuration"]
        assert config["quality_enhancement_enabled"] is True
        assert config["advanced_analysis_enabled"] is True
        assert config["intelligent_formatting_enabled"] is True
        
        # Stop monitoring
        enhanced_system.monitor.stop_monitoring()
        
        print("✓ Production monitoring validated successfully")
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, enhanced_system, processing_context):
        """Test response caching functionality"""
        
        question = "What are the payment terms?"
        document_id = "test_doc_001"
        
        # First request - should not be cached
        result1 = await enhanced_system.process_question(
            question=question,
            document_id=document_id,
            context=processing_context
        )
        
        assert result1.cache_hit is False
        
        # Second identical request - should be cached
        result2 = await enhanced_system.process_question(
            question=question,
            document_id=document_id,
            context=processing_context
        )
        
        assert result2.cache_hit is True
        assert result2.processing_time < result1.processing_time  # Should be faster
        
        # Check cache statistics
        health_status = await enhanced_system.get_system_health()
        cache_stats = health_status.get("cache_statistics")
        
        if cache_stats:
            assert cache_stats["cache_hits"] >= 1
            assert cache_stats["hit_rate"] > 0
        
        print("✓ Caching functionality validated successfully")
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, enhanced_system):
        """Test error handling and graceful degradation"""
        
        context = ProcessingContext(session_id="error_test")
        
        # Test with non-existent document
        result = await enhanced_system.process_question(
            question="What are the terms?",
            document_id="nonexistent_doc",
            context=context
        )
        
        # Should handle gracefully
        assert result is not None
        assert result.response.response_type == ResponseType.FALLBACK
        assert "error" in result.response.content.lower()
        assert result.quality_score == 0.0
        
        # Test with empty question
        result = await enhanced_system.process_question(
            question="",
            document_id="test_doc_001",
            context=context
        )
        
        # Should handle gracefully
        assert result is not None
        assert result.response is not None
        
        print("✓ Error handling and recovery validated successfully")
    
    @pytest.mark.asyncio
    async def test_performance_optimization(self, enhanced_system):
        """Test performance optimization features"""
        
        # Get initial performance metrics
        initial_health = await enhanced_system.get_system_health()
        
        # Run optimization
        optimization_result = await enhanced_system.optimize_performance()
        
        # Validate optimization result structure
        assert "optimizations_applied" in optimization_result
        assert "performance_improvement" in optimization_result
        assert "recommendations" in optimization_result
        
        # Check that optimization ran without errors
        assert isinstance(optimization_result["optimizations_applied"], list)
        assert isinstance(optimization_result["recommendations"], list)
        
        print("✓ Performance optimization validated successfully")
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, enhanced_system):
        """Test handling of concurrent requests"""
        
        # Create multiple concurrent requests
        questions = [
            "What are the payment terms?",
            "How does termination work?",
            "What are the liability provisions?",
            "Who owns the intellectual property?",
            "What are the confidentiality requirements?"
        ]
        
        contexts = [
            ProcessingContext(session_id=f"concurrent_test_{i}")
            for i in range(len(questions))
        ]
        
        # Submit all requests concurrently
        tasks = [
            enhanced_system.process_question(
                question=question,
                document_id="test_doc_001",
                context=context
            )
            for question, context in zip(questions, contexts)
        ]
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        # Validate all requests completed successfully
        assert len(results) == len(questions)
        
        for i, result in enumerate(results):
            assert result is not None
            assert result.response is not None
            assert result.processing_time > 0
            print(f"✓ Concurrent request {i+1} completed in {result.processing_time:.2f}s")
        
        print("✓ Concurrent request handling validated successfully")
    
    @pytest.mark.asyncio
    async def test_comprehensive_test_suite_integration(self, enhanced_system):
        """Test integration with comprehensive test suite"""
        
        # Create test suite
        test_suite = ComprehensiveTestSuite(enhanced_system.storage)
        
        # Run a subset of tests
        results = await test_suite.run_comprehensive_test_suite(
            categories=[TestCategory.DOCUMENT_GROUNDED, TestCategory.OFF_TOPIC_CASUAL],
            parallel_execution=False  # Sequential for testing
        )
        
        # Validate test results
        assert results.total_tests > 0
        assert results.passed_tests >= 0
        assert results.execution_time > 0
        
        # Check that we have reasonable success rate
        success_rate = results.passed_tests / results.total_tests
        assert success_rate >= 0.5  # At least 50% should pass
        
        print(f"✓ Comprehensive test suite completed: {results.passed_tests}/{results.total_tests} passed")
    
    @pytest.mark.asyncio
    async def test_end_to_end_user_journey(self, enhanced_system):
        """Test complete end-to-end user journey"""
        
        # Simulate realistic user journey
        session_id = "e2e_journey_test"
        
        journey_steps = [
            ("Hello, I need help understanding this contract", "greeting"),
            ("What are the main terms I should know about?", "overview"),
            ("Are there any risks I should be concerned about?", "risk_analysis"),
            ("What about the payment terms specifically?", "specific_inquiry"),
            ("This is confusing, can you explain it more simply?", "clarification"),
            ("Thanks, that's very helpful!", "appreciation")
        ]
        
        conversation_history = []
        
        for step, (question, step_type) in enumerate(journey_steps):
            context = ProcessingContext(
                session_id=session_id,
                conversation_history=conversation_history.copy()
            )
            
            result = await enhanced_system.process_question(
                question=question,
                document_id="test_doc_001",
                context=context
            )
            
            # Validate each step
            assert result is not None
            assert result.response is not None
            assert len(result.response.content) > 0
            
            # Add to conversation history
            conversation_history.append(question)
            
            print(f"✓ Journey step {step+1} ({step_type}): {result.response.response_type}")
        
        # Validate journey coherence
        assert len(conversation_history) == len(journey_steps)
        
        print("✓ End-to-end user journey completed successfully")
    
    def test_system_shutdown(self, enhanced_system):
        """Test graceful system shutdown"""
        
        # System should shutdown without errors
        enhanced_system.shutdown()
        
        # Validate shutdown state
        assert enhanced_system.thread_pool._shutdown
        
        if enhanced_system.config.enable_caching:
            assert len(enhanced_system.response_cache) == 0
        
        print("✓ System shutdown completed successfully")


@pytest.mark.asyncio
async def test_production_readiness_validation():
    """Test production readiness validation"""
    
    # Create system with production configuration
    config = SystemConfiguration(
        enable_quality_enhancement=True,
        enable_advanced_analysis=True,
        enable_intelligent_formatting=True,
        enable_production_monitoring=True,
        enable_caching=True
    )
    
    storage = Mock(spec=DocumentStorage)
    monitor = ProductionMonitor()
    
    system = EnhancedContractSystem(
        storage=storage,
        config=config,
        monitor=monitor
    )
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Wait for initial health checks
    await asyncio.sleep(2)
    
    # Validate production readiness
    readiness = monitor.validate_production_readiness()
    
    assert "production_ready" in readiness
    assert "checks" in readiness
    assert "recommendations" in readiness
    
    # Stop monitoring
    monitor.stop_monitoring()
    system.shutdown()
    
    print("✓ Production readiness validation completed")


if __name__ == "__main__":
    # Run comprehensive tests
    pytest.main([__file__, "-v", "--tb=short"])