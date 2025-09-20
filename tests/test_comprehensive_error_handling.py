"""Comprehensive error handling tests for enhanced Q&A capabilities."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.utils.error_handling import (
    EnhancedAnalysisError, ConversationalAIError, ExcelGenerationError,
    TemplateError, ContextManagementError, graceful_degradation,
    alternative_formats, ErrorType
)
from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
from src.services.conversational_ai_engine import ConversationalAIEngine
from src.services.excel_report_generator import ExcelReportGenerator
from src.models.document import Document


class TestEnhancedAnalysisErrorHandling:
    """Test error handling in enhanced analysis components."""
    
    @pytest.fixture
    def mock_storage(self):
        return Mock()
    
    @pytest.fixture
    def sample_document(self):
        return Document(
            id="test_doc_1",
            title="Test Document",
            file_type="pdf",
            file_size=1024,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="Test document content for analysis.",
            is_legal_document=True
        )
    
    def test_enhanced_analyzer_api_failure_handling(self, mock_storage, sample_document):
        """Test enhanced analyzer handles API failures gracefully."""
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_key")
        
        # Mock API call to raise exception
        with patch.object(analyzer, '_call_gemini_api', side_effect=Exception("API Error")):
            # Should handle error gracefully and return empty results
            risks = analyzer._safe_generate_section(
                lambda: analyzer.identify_risks(sample_document),
                []
            )
            assert risks == []
    
    def test_enhanced_analyzer_partial_failure_recovery(self, mock_storage, sample_document):
        """Test analyzer continues with partial results when some operations fail."""
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_key")
        
        # Mock successful and failing operations
        with patch.object(analyzer, '_generate_document_overview', return_value="Overview"):
            with patch.object(analyzer, 'identify_risks', side_effect=Exception("Risk analysis failed")):
                with patch.object(analyzer, 'extract_commitments', return_value=[]):
                    with patch.object(analyzer, 'find_deliverable_dates', return_value=[]):
                        
                        # Should complete analysis with partial results
                        analysis = analyzer.analyze_document_comprehensive(sample_document)
                        
                        assert analysis.document_overview == "Overview"
                        assert analysis.risks == []  # Failed operation returns empty list
                        assert analysis.commitments == []
                        assert analysis.deliverable_dates == []
    
    def test_template_error_fallback(self, mock_storage, sample_document):
        """Test template errors fall back to default analysis."""
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_key")
        
        # Mock template engine to raise error
        with patch.object(analyzer.template_engine, 'recommend_template', 
                         side_effect=TemplateError("Template not found")):
            with patch.object(analyzer, '_generate_document_overview', return_value="Overview"):
                with patch.object(analyzer, 'identify_risks', return_value=[]):
                    with patch.object(analyzer, 'extract_commitments', return_value=[]):
                        with patch.object(analyzer, 'find_deliverable_dates', return_value=[]):
                            
                            # Should complete analysis without template
                            analysis = analyzer.analyze_document_comprehensive(sample_document)
                            assert analysis.template_used is None
    
    def test_json_parsing_error_recovery(self, mock_storage, sample_document):
        """Test recovery from JSON parsing errors in API responses."""
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_key")
        
        # Mock API to return invalid JSON
        with patch.object(analyzer, '_call_gemini_api', return_value="Invalid JSON response"):
            # Should handle parsing error gracefully
            result = analyzer._parse_json_response("Invalid JSON response")
            assert result == {}


class TestConversationalAIErrorHandling:
    """Test error handling in conversational AI engine."""
    
    @pytest.fixture
    def mock_engines(self):
        qa_engine = Mock()
        contract_engine = Mock()
        return qa_engine, contract_engine
    
    def test_legal_analysis_fallback_to_basic(self, mock_engines):
        """Test fallback from legal analysis to basic Q&A when legal engine fails."""
        qa_engine, contract_engine = mock_engines
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Mock contract engine to fail
        contract_engine.analyze_contract_query.side_effect = Exception("Legal analysis failed")
        
        # Mock basic QA engine to succeed
        qa_engine.answer_question.return_value = {
            'answer': 'Basic answer',
            'confidence': 0.7,
            'sources': ['source1']
        }
        
        # Should fall back to basic Q&A
        response = conv_engine._handle_legal_question("legal question", "doc1", "session1")
        
        assert "Basic answer" in response.answer
        assert response.analysis_mode == "basic_fallback"
        assert response.confidence < 0.7  # Reduced confidence for fallback
    
    def test_context_management_error_recovery(self, mock_engines):
        """Test recovery from context management errors."""
        qa_engine, contract_engine = mock_engines
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Mock context storage to fail
        with patch.object(conv_engine, 'conversation_contexts', side_effect=Exception("Context error")):
            # Should handle context error gracefully
            try:
                conv_engine.manage_conversation_context("session1", "question", "response")
                # Should not raise exception
            except ContextManagementError:
                pytest.fail("Should handle context management errors gracefully")
    
    def test_compound_question_partial_failure(self, mock_engines):
        """Test handling of compound questions when some parts fail."""
        qa_engine, contract_engine = mock_engines
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Mock one part to succeed, one to fail
        qa_engine.answer_question.side_effect = [
            {'answer': 'Answer 1', 'confidence': 0.8, 'sources': []},
            Exception("Second part failed")
        ]
        
        # Should handle partial failure
        response = conv_engine.handle_compound_question(
            "What is X and what is Y?", "doc1", "session1"
        )
        
        assert len(response.individual_responses) == 2
        assert response.individual_responses[0]['mode'] != 'error'
        assert response.individual_responses[1]['mode'] == 'error'


class TestExcelGenerationErrorHandling:
    """Test error handling in Excel report generation."""
    
    @pytest.fixture
    def mock_storage(self):
        return Mock()
    
    @pytest.fixture
    def temp_reports_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_excel_generation_fallback_to_csv(self, mock_storage, temp_reports_dir):
        """Test fallback to CSV when Excel generation fails."""
        generator = ExcelReportGenerator(mock_storage, temp_reports_dir)
        
        # Mock document storage
        mock_storage.get_document.return_value = Mock(
            id="doc1", title="Test Doc", upload_timestamp=datetime.now()
        )
        
        # Mock Excel creation to fail
        with patch.object(generator, '_create_excel_file', side_effect=Exception("Excel failed")):
            with patch.object(generator, '_extract_document_analysis_data', return_value={}):
                
                # Should generate fallback report
                report = generator.generate_document_report("doc1")
                
                assert report.filename.endswith('.csv')
                assert os.path.exists(report.file_path)
    
    def test_data_extraction_error_handling(self, mock_storage, temp_reports_dir):
        """Test handling of data extraction errors."""
        generator = ExcelReportGenerator(mock_storage, temp_reports_dir)
        
        # Mock document storage to fail
        mock_storage.get_document.side_effect = Exception("Document not found")
        
        # Should raise ExcelGenerationError
        with pytest.raises(ExcelGenerationError):
            generator.generate_document_report("nonexistent_doc")
    
    def test_file_save_error_handling(self, mock_storage, temp_reports_dir):
        """Test handling of file save errors."""
        generator = ExcelReportGenerator(mock_storage, temp_reports_dir)
        
        # Create read-only directory to cause save failure
        readonly_dir = os.path.join(temp_reports_dir, "readonly")
        os.makedirs(readonly_dir, mode=0o444)
        
        generator.reports_dir = readonly_dir
        
        # Mock successful data extraction
        mock_storage.get_document.return_value = Mock(
            id="doc1", title="Test Doc", upload_timestamp=datetime.now()
        )
        
        with patch.object(generator, '_extract_document_analysis_data', return_value={}):
            # Should handle file save error
            with pytest.raises(ExcelGenerationError):
                generator.generate_document_report("doc1")


class TestGracefulDegradation:
    """Test graceful degradation utilities."""
    
    def test_enhanced_with_basic_fallback_decorator(self):
        """Test enhanced feature fallback to basic functionality."""
        
        def enhanced_function():
            raise EnhancedAnalysisError("Enhanced feature failed")
        
        def basic_function():
            return "Basic result"
        
        # Apply graceful degradation
        @graceful_degradation.enhanced_with_basic_fallback(enhanced_function, basic_function)
        def test_function():
            pass
        
        result = test_function()
        assert result == "Basic result"
    
    def test_safe_enhanced_operation(self):
        """Test safe execution of enhanced operations."""
        
        def failing_operation():
            raise EnhancedAnalysisError("Operation failed")
        
        result, success = graceful_degradation.safe_enhanced_operation(
            failing_operation, 
            fallback_result="Fallback"
        )
        
        assert result == "Fallback"
        assert success is False
    
    def test_safe_enhanced_operation_success(self):
        """Test safe execution with successful operation."""
        
        def successful_operation():
            return "Success"
        
        result, success = graceful_degradation.safe_enhanced_operation(successful_operation)
        
        assert result == "Success"
        assert success is True


class TestAlternativeFormats:
    """Test alternative format generation."""
    
    def test_excel_to_csv_fallback(self):
        """Test conversion of data to CSV format."""
        data = [
            {'name': 'Item 1', 'value': 100},
            {'name': 'Item 2', 'value': 200}
        ]
        
        csv_result = alternative_formats.excel_to_csv_fallback(data, "test.csv")
        
        assert 'name,value' in csv_result
        assert 'Item 1,100' in csv_result
        assert 'Item 2,200' in csv_result
    
    def test_excel_to_json_fallback(self):
        """Test conversion of data to JSON format."""
        data = [
            {'name': 'Item 1', 'value': 100},
            {'name': 'Item 2', 'value': 200}
        ]
        
        json_result = alternative_formats.excel_to_json_fallback(data)
        
        assert '"name": "Item 1"' in json_result
        assert '"value": 100' in json_result
    
    def test_create_fallback_report_text_format(self):
        """Test creation of fallback report in text format."""
        data = {
            'summary': 'Test summary',
            'risks': ['Risk 1', 'Risk 2'],
            'commitments': ['Commitment 1']
        }
        
        text_result = alternative_formats.create_fallback_report(data, "text")
        
        assert 'SUMMARY:' in text_result
        assert 'RISKS:' in text_result
        assert 'Risk 1' in text_result
        assert 'Commitment 1' in text_result


class TestSystemIntegration:
    """Test integration between enhanced components with error handling."""
    
    def test_end_to_end_error_recovery(self):
        """Test end-to-end error recovery across all components."""
        # This would test the complete workflow with various failure points
        # and verify that the system maintains functionality
        pass
    
    def test_performance_under_error_conditions(self):
        """Test system performance when errors occur frequently."""
        # This would test that error handling doesn't significantly impact performance
        pass
    
    def test_error_logging_and_monitoring(self):
        """Test that errors are properly logged for monitoring."""
        # This would verify error logging functionality
        pass


if __name__ == "__main__":
    pytest.main([__file__])