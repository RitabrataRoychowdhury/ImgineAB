"""Performance and stress tests for enhanced Q&A capabilities."""

import pytest
import time
import threading
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.models.document import Document
from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
from src.services.conversational_ai_engine import ConversationalAIEngine
from src.services.excel_report_generator import ExcelReportGenerator
from src.storage.enhanced_storage import EnhancedDocumentStorage


class TestEnhancedPerformance:
    """Performance tests for enhanced Q&A system."""
    
    @pytest.fixture
    def mock_storage(self):
        return Mock(spec=EnhancedDocumentStorage)
    
    @pytest.fixture
    def large_document(self):
        """Create a large document for performance testing."""
        # Generate large content (approximately 50KB)
        large_content = """
        COMPREHENSIVE SOFTWARE DEVELOPMENT AGREEMENT
        
        This Agreement is entered into between TechCorp Inc. and DevStudio LLC.
        """ * 500  # Repeat to create large document
        
        return Document(
            id="large_perf_doc",
            title="Large Performance Test Document",
            file_type="pdf",
            file_size=len(large_content),
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text=large_content,
            is_legal_document=True,
            legal_document_type="Service Agreement"
        )
    
    @pytest.fixture
    def multiple_documents(self):
        """Create multiple documents for concurrent testing."""
        documents = []
        for i in range(10):
            content = f"Document {i} content. " * 100  # Moderate size documents
            doc = Document(
                id=f"perf_doc_{i}",
                title=f"Performance Test Document {i}",
                file_type="pdf",
                file_size=len(content),
                upload_timestamp=datetime.now(),
                processing_status="completed",
                original_text=content,
                is_legal_document=True
            )
            documents.append(doc)
        return documents
    
    def test_large_document_analysis_performance(self, mock_storage, large_document):
        """Test performance of enhanced analysis with large documents."""
        
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Mock API calls to return quickly
        def fast_api_mock(prompt, max_tokens=1000):
            return '{"risks": [], "commitments": [], "deliverable_dates": []}'
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=fast_api_mock):
            start_time = time.time()
            
            # Perform comprehensive analysis
            analysis = analyzer.analyze_document_comprehensive(large_document)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time (5 seconds for large document)
            assert processing_time < 5.0, f"Analysis took {processing_time:.2f}s, expected < 5.0s"
            assert analysis.document_id == large_document.id
            
            print(f"Large document analysis completed in {processing_time:.2f}s")
    
    def test_concurrent_document_analysis(self, mock_storage, multiple_documents):
        """Test concurrent analysis of multiple documents."""
        
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Mock API calls
        def concurrent_api_mock(prompt, max_tokens=1000):
            time.sleep(0.1)  # Simulate API delay
            return '{"risks": [], "commitments": [], "deliverable_dates": []}'
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=concurrent_api_mock):
            
            def analyze_document(doc):
                return analyzer.analyze_document_comprehensive(doc)
            
            start_time = time.time()
            
            # Analyze documents concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(analyze_document, doc) for doc in multiple_documents[:5]]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Concurrent processing should be faster than sequential
            # With 5 documents and 0.1s API delay each, concurrent should be ~0.1s + overhead
            # Sequential would be ~0.5s + overhead
            assert total_time < 1.0, f"Concurrent analysis took {total_time:.2f}s, expected < 1.0s"
            assert len(results) == 5
            
            print(f"Concurrent analysis of 5 documents completed in {total_time:.2f}s")
    
    def test_conversational_ai_response_time(self, mock_storage):
        """Test response time of conversational AI engine."""
        
        qa_engine = Mock()
        contract_engine = Mock()
        
        # Mock engines to respond quickly
        qa_engine.answer_question.return_value = {
            'answer': 'Quick response',
            'confidence': 0.8,
            'sources': []
        }
        
        contract_engine.analyze_contract_query.return_value = {
            'answer': 'Quick legal response',
            'confidence': 0.9,
            'sources': []
        }
        
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Test multiple question types
        questions = [
            "What is this document about?",
            "What are the legal implications?",
            "Who are the parties involved?",
            "What are the payment terms and delivery dates?",  # Compound question
            "Hello, can you help me understand this contract?"  # Casual
        ]
        
        response_times = []
        
        for question in questions:
            start_time = time.time()
            
            response = conv_engine.answer_conversational_question(
                question, "test_doc", "test_session"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # Each response should be under 1 second
            assert response_time < 1.0, f"Response took {response_time:.2f}s for: {question}"
            assert response.answer is not None
        
        avg_response_time = sum(response_times) / len(response_times)
        print(f"Average conversational response time: {avg_response_time:.3f}s")
        
        # Average should be well under 0.5 seconds
        assert avg_response_time < 0.5
    
    def test_excel_generation_performance(self, mock_storage):
        """Test Excel report generation performance."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ExcelReportGenerator(mock_storage, temp_dir)
            
            # Mock document
            test_doc = Document(
                id="excel_perf_doc",
                title="Excel Performance Test",
                file_type="pdf",
                file_size=1000,
                upload_timestamp=datetime.now(),
                processing_status="completed",
                original_text="Test content",
                is_legal_document=True
            )
            
            mock_storage.get_document.return_value = test_doc
            
            # Mock large analysis data
            large_analysis_data = {
                'summary': {'document_overview': 'Large test document'},
                'risks': [{'risk_id': f'R{i:03d}', 'description': f'Risk {i}', 'severity': 'Medium'} 
                         for i in range(100)],  # 100 risks
                'commitments': [{'commitment_id': f'C{i:03d}', 'description': f'Commitment {i}'} 
                               for i in range(50)],  # 50 commitments
                'deliverable_dates': [{'date': '2024-12-31', 'description': f'Date {i}'} 
                                     for i in range(25)]  # 25 dates
            }
            
            with patch.object(generator, '_extract_document_analysis_data', 
                            return_value=large_analysis_data):
                
                start_time = time.time()
                
                # Generate comprehensive report
                report = generator.generate_document_report("excel_perf_doc", "comprehensive")
                
                end_time = time.time()
                generation_time = end_time - start_time
                
                # Should generate report within reasonable time
                assert generation_time < 10.0, f"Excel generation took {generation_time:.2f}s"
                assert os.path.exists(report.file_path)
                
                # Check file size is reasonable (should have content)
                file_size = os.path.getsize(report.file_path)
                assert file_size > 1000, "Generated file seems too small"
                
                print(f"Excel report with 175 data items generated in {generation_time:.2f}s")
    
    def test_memory_usage_with_large_datasets(self, mock_storage):
        """Test memory usage with large datasets."""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Create very large document
        huge_content = "Large document content. " * 10000  # ~250KB
        huge_document = Document(
            id="memory_test_doc",
            title="Memory Test Document",
            file_type="pdf",
            file_size=len(huge_content),
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text=huge_content,
            is_legal_document=True
        )
        
        # Mock API to return large datasets
        def large_dataset_mock(prompt, max_tokens=1000):
            if "risk" in prompt.lower():
                risks = [{"risk_id": f"R{i}", "description": f"Risk {i}", "severity": "Medium"} 
                        for i in range(1000)]
                return f'{{"risks": {risks}}}'
            return '{"commitments": [], "deliverable_dates": []}'
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=large_dataset_mock):
            # Perform analysis
            analysis = analyzer.analyze_document_comprehensive(huge_document)
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            # Memory increase should be reasonable (less than 100MB for this test)
            assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB"
            
            # Verify analysis completed
            assert analysis.document_id == huge_document.id
            
            print(f"Memory usage increased by {memory_increase:.1f}MB for large dataset analysis")
    
    def test_error_handling_performance_impact(self, mock_storage, multiple_documents):
        """Test that error handling doesn't significantly impact performance."""
        
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Test with 50% failure rate
        call_count = 0
        def intermittent_failure_mock(prompt, max_tokens=1000):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Fail every other call
                raise Exception("Simulated API failure")
            return '{"risks": [], "commitments": [], "deliverable_dates": []}'
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=intermittent_failure_mock):
            
            start_time = time.time()
            
            # Analyze multiple documents with failures
            successful_analyses = 0
            for doc in multiple_documents[:5]:
                try:
                    analysis = analyzer.analyze_document_comprehensive(doc)
                    successful_analyses += 1
                except Exception:
                    pass  # Expected failures
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should complete within reasonable time even with errors
            assert total_time < 5.0, f"Analysis with errors took {total_time:.2f}s"
            
            # Should have some successful analyses despite failures
            assert successful_analyses > 0
            
            print(f"Analysis with 50% failure rate completed in {total_time:.2f}s")
            print(f"Successful analyses: {successful_analyses}/5")
    
    def test_conversation_context_scalability(self, mock_storage):
        """Test conversation context management with many sessions."""
        
        qa_engine = Mock()
        contract_engine = Mock()
        
        qa_engine.answer_question.return_value = {
            'answer': 'Response',
            'confidence': 0.8,
            'sources': []
        }
        
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Create many conversation sessions
        num_sessions = 100
        start_time = time.time()
        
        for i in range(num_sessions):
            session_id = f"session_{i}"
            
            # Multiple questions per session
            for j in range(5):
                question = f"Question {j} in session {i}"
                conv_engine.answer_conversational_question(
                    question, "test_doc", session_id
                )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle many sessions efficiently
        assert total_time < 10.0, f"Context management took {total_time:.2f}s for {num_sessions} sessions"
        
        # Verify all sessions are tracked
        assert len(conv_engine.conversation_contexts) == num_sessions
        
        # Check memory usage of contexts
        total_turns = sum(len(ctx.conversation_history) 
                         for ctx in conv_engine.conversation_contexts.values())
        assert total_turns == num_sessions * 5
        
        print(f"Managed {num_sessions} sessions with {total_turns} total turns in {total_time:.2f}s")


class TestStressTests:
    """Stress tests for enhanced Q&A system."""
    
    def test_high_concurrency_stress(self, mock_storage=None):
        """Test system under high concurrent load."""
        
        if mock_storage is None:
            mock_storage = Mock(spec=EnhancedDocumentStorage)
        
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Mock API with variable delay
        def variable_delay_mock(prompt, max_tokens=1000):
            import random
            time.sleep(random.uniform(0.05, 0.2))  # 50-200ms delay
            return '{"risks": [], "commitments": [], "deliverable_dates": []}'
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=variable_delay_mock):
            
            def stress_analysis(doc_id):
                doc = Document(
                    id=doc_id,
                    title=f"Stress Test Doc {doc_id}",
                    file_type="pdf",
                    file_size=1000,
                    upload_timestamp=datetime.now(),
                    processing_status="completed",
                    original_text="Stress test content",
                    is_legal_document=True
                )
                return analyzer.analyze_document_comprehensive(doc)
            
            # High concurrency test
            num_concurrent = 20
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(stress_analysis, f"stress_doc_{i}") 
                          for i in range(num_concurrent)]
                
                results = []
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=30)  # 30 second timeout
                        results.append(result)
                    except Exception as e:
                        print(f"Stress test failure: {e}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Should handle high concurrency
            success_rate = len(results) / num_concurrent
            assert success_rate > 0.8, f"Success rate {success_rate:.2f} too low"
            
            print(f"High concurrency test: {len(results)}/{num_concurrent} succeeded in {total_time:.2f}s")
    
    def test_memory_leak_detection(self, mock_storage=None):
        """Test for memory leaks during extended operation."""
        
        if mock_storage is None:
            mock_storage = Mock(spec=EnhancedDocumentStorage)
        
        import psutil
        import gc
        
        process = psutil.Process(os.getpid())
        
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        def quick_mock(prompt, max_tokens=1000):
            return '{"risks": [], "commitments": [], "deliverable_dates": []}'
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=quick_mock):
            
            # Baseline memory
            gc.collect()
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform many operations
            for i in range(100):
                doc = Document(
                    id=f"leak_test_{i}",
                    title=f"Leak Test {i}",
                    file_type="pdf",
                    file_size=1000,
                    upload_timestamp=datetime.now(),
                    processing_status="completed",
                    original_text=f"Content {i}",
                    is_legal_document=True
                )
                
                analysis = analyzer.analyze_document_comprehensive(doc)
                
                # Periodically check memory
                if i % 20 == 0:
                    gc.collect()
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_growth = current_memory - baseline_memory
                    
                    # Memory growth should be reasonable
                    assert memory_growth < 50, f"Excessive memory growth: {memory_growth:.1f}MB after {i} operations"
            
            # Final memory check
            gc.collect()
            final_memory = process.memory_info().rss / 1024 / 1024
            total_growth = final_memory - baseline_memory
            
            print(f"Memory growth after 100 operations: {total_growth:.1f}MB")
            
            # Should not have significant memory leak
            assert total_growth < 100, f"Potential memory leak: {total_growth:.1f}MB growth"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])