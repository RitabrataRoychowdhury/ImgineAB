"""
Comprehensive tests for the Excel Export Engine with never-fail guarantee.
Tests document upload → summary generation → risk analysis → Excel export workflow.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from src.services.excel_export_engine import ExcelExportEngine, ExportRequest, ExportResult
from src.services.request_analyzer import RequestAnalyzer, RequestType
from src.services.data_formatter import DataFormatter
from src.storage.document_storage import DocumentStorage
from src.models.document import Document


class TestExcelExportEngine:
    """Test suite for Excel Export Engine."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test exports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_storage(self):
        """Mock document storage."""
        storage = Mock(spec=DocumentStorage)
        return storage
    
    @pytest.fixture
    def export_engine(self, mock_storage, temp_dir):
        """Create export engine with temporary directory."""
        return ExcelExportEngine(mock_storage, temp_dir)
    
    @pytest.fixture
    def sample_document(self):
        """Create sample document for testing."""
        return Document(
            id="test-doc-1",
            title="Test Contract",
            file_type="pdf",
            file_size=1024,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            summary="Test contract summary"
        )
    
    def test_never_fail_guarantee_excel_success(self, export_engine):
        """Test that primary Excel export works correctly."""
        request = ExportRequest(
            data={'test': 'data'},
            format_preferences=['excel'],
            template_type='generic',
            metadata={'test': True},
            user_request='Test export'
        )
        
        result = export_engine.export_data(request)
        
        assert result.success
        assert result.format_type == 'excel'
        assert result.filename.endswith('.xlsx')
        assert os.path.exists(result.file_path)
        assert not result.fallback_used
    
    def test_never_fail_guarantee_fallback_to_csv(self, export_engine):
        """Test fallback to CSV when Excel fails."""
        # Mock Excel generation to fail
        with patch.object(export_engine, '_try_primary_export', side_effect=Exception("Excel failed")):
            with patch.object(export_engine, '_try_basic_excel_export', side_effect=Exception("Basic Excel failed")):
                request = ExportRequest(
                    data={'test': 'data'},
                    format_preferences=['excel'],
                    template_type='generic',
                    metadata={'test': True},
                    user_request='Test export'
                )
                
                result = export_engine.export_data(request)
                
                assert result.success
                assert result.format_type == 'csv'
                assert result.filename.endswith('.csv')
                assert os.path.exists(result.file_path)
                assert result.fallback_used
    
    def test_never_fail_guarantee_final_fallback(self, export_engine):
        """Test final fallback to text when all else fails."""
        # Mock all export methods to fail except text
        with patch.object(export_engine, '_try_primary_export', side_effect=Exception("Excel failed")):
            with patch.object(export_engine, '_try_basic_excel_export', side_effect=Exception("Basic Excel failed")):
                with patch.object(export_engine, '_try_csv_export', side_effect=Exception("CSV failed")):
                    request = ExportRequest(
                        data={'test': 'data'},
                        format_preferences=['excel'],
                        template_type='generic',
                        metadata={'test': True},
                        user_request='Test export'
                    )
                    
                    result = export_engine.export_data(request)
                    
                    assert result.success
                    assert result.format_type == 'text'
                    assert result.filename.endswith('.txt')
                    assert os.path.exists(result.file_path)
                    assert result.fallback_used 
   
    def test_risk_analysis_report_generation(self, export_engine):
        """Test risk analysis report generation."""
        risk_data = {
            'risks': [
                {
                    'risk_id': 'R001',
                    'description': 'Test risk',
                    'severity': 'High',
                    'category': 'Legal',
                    'probability': 0.8,
                    'impact_description': 'High impact',
                    'affected_parties': ['Party A'],
                    'mitigation_strategies': ['Strategy 1'],
                    'materialization_timeframe': '6 months'
                }
            ]
        }
        
        document_info = {'title': 'Test Document', 'id': 'test-1'}
        
        result = export_engine.generate_risk_analysis_report(risk_data, document_info)
        
        assert result.success
        assert result.format_type == 'excel'
        assert 'risk_analysis' in result.filename
        assert os.path.exists(result.file_path)
    
    def test_document_summary_export(self, export_engine):
        """Test document summary export generation."""
        summary_data = {
            'overview': 'Test document overview',
            'document_type': 'Contract',
            'key_terms': {'Term 1': 'Definition 1', 'Term 2': 'Definition 2'},
            'important_dates': [
                {'date': '2024-12-31', 'description': 'Expiration', 'type': 'Deadline'}
            ]
        }
        
        result = export_engine.generate_document_summary_export(summary_data)
        
        assert result.success
        assert result.format_type == 'excel'
        assert 'document_summary' in result.filename
        assert os.path.exists(result.file_path)
    
    def test_portfolio_analysis_report(self, export_engine):
        """Test portfolio analysis report generation."""
        portfolio_data = [
            {
                'title': 'Document 1',
                'document_type': 'Contract',
                'upload_date': '2024-01-01',
                'status': 'Active',
                'risks': [],
                'key_terms': ['Term 1', 'Term 2']
            },
            {
                'title': 'Document 2',
                'document_type': 'MTA',
                'upload_date': '2024-01-02',
                'status': 'Active',
                'risks': [],
                'key_terms': ['Term 3', 'Term 4']
            }
        ]
        
        result = export_engine.generate_portfolio_analysis_report(portfolio_data)
        
        assert result.success
        assert result.format_type == 'excel'
        assert 'portfolio_analysis' in result.filename
        assert os.path.exists(result.file_path)
    
    def test_tabular_data_export_with_auto_detection(self, export_engine):
        """Test automatic tabular data export with template detection."""
        # Test with risk-related data
        risk_data = [
            {'risk': 'Risk 1', 'severity': 'High', 'mitigation': 'Strategy 1'},
            {'risk': 'Risk 2', 'severity': 'Medium', 'mitigation': 'Strategy 2'}
        ]
        
        result = export_engine.export_tabular_data(
            risk_data, 
            "Show me all risks in a table",
            ['excel', 'csv']
        )
        
        assert result.success
        assert result.format_type == 'excel'
        assert os.path.exists(result.file_path)
    
    def test_file_cleanup_on_initialization(self, mock_storage, temp_dir):
        """Test that expired files are cleaned up on initialization."""
        # Create an old file
        old_file = os.path.join(temp_dir, 'old_export.xlsx')
        with open(old_file, 'w') as f:
            f.write('old content')
        
        # Set file modification time to 25 hours ago
        old_time = datetime.now() - timedelta(hours=25)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
        
        # Initialize engine (should trigger cleanup)
        engine = ExcelExportEngine(mock_storage, temp_dir)
        
        # File should be cleaned up
        assert not os.path.exists(old_file)
    
    def test_download_info_retrieval(self, export_engine):
        """Test download information retrieval."""
        # Generate an export first
        request = ExportRequest(
            data={'test': 'data'},
            format_preferences=['excel'],
            template_type='generic',
            metadata={},
            user_request='Test'
        )
        
        result = export_engine.export_data(request)
        
        # Get download info
        download_info = export_engine.get_download_info(result.filename)
        
        assert download_info is not None
        assert download_info['filename'] == result.filename
        assert download_info['file_path'] == result.file_path
        assert 'size' in download_info
        assert 'created' in download_info
        assert 'download_url' in download_info
    
    def test_complex_data_structure_handling(self, export_engine):
        """Test handling of complex nested data structures."""
        complex_data = {
            'summary': {
                'title': 'Complex Document',
                'type': 'Multi-section Contract'
            },
            'sections': [
                {'name': 'Section 1', 'content': 'Content 1'},
                {'name': 'Section 2', 'content': 'Content 2'}
            ],
            'metadata': {
                'created': '2024-01-01',
                'version': '1.0'
            }
        }
        
        result = export_engine.export_tabular_data(
            complex_data,
            "Export this complex data structure",
            ['excel']
        )
        
        assert result.success
        assert os.path.exists(result.file_path)
    
    def test_empty_data_handling(self, export_engine):
        """Test handling of empty or null data."""
        empty_data_cases = [
            None,
            {},
            [],
            "",
            {'empty': None}
        ]
        
        for empty_data in empty_data_cases:
            result = export_engine.export_tabular_data(
                empty_data,
                "Export empty data",
                ['excel', 'csv', 'text']
            )
            
            # Should still succeed due to never-fail guarantee
            assert result.success
            assert os.path.exists(result.file_path)


class TestRequestAnalyzer:
    """Test suite for Request Analyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create request analyzer."""
        return RequestAnalyzer()
    
    def test_direct_export_request_detection(self, analyzer):
        """Test detection of direct export requests."""
        export_requests = [
            "Can you export this to Excel?",
            "I need a CSV file with this data",
            "Generate a report for download",
            "Create an Excel spreadsheet",
            "Give me a table with all the information"
        ]
        
        for request in export_requests:
            analysis = analyzer.analyze_request(request)
            assert analysis.should_generate_export
            assert analysis.confidence >= 0.7
            assert analysis.request_type in [RequestType.EXPORT_REQUEST, RequestType.TABULAR_DATA_REQUEST]
    
    def test_tabular_data_request_detection(self, analyzer):
        """Test detection of tabular data requests."""
        tabular_requests = [
            "List all the risks in this document",
            "Show me all parties involved",
            "What are the key terms?",
            "Break down the obligations by party",
            "Organize the dates in chronological order"
        ]
        
        for request in tabular_requests:
            analysis = analyzer.analyze_request(request)
            assert analysis.should_generate_export
            assert analysis.confidence >= 0.4
    
    def test_standard_qa_request_detection(self, analyzer):
        """Test detection of standard Q&A requests."""
        qa_requests = [
            "What is this document about?",
            "Who wrote this document?",
            "When was this created?",
            "Explain the main concept",
            "What does this mean?"
        ]
        
        for request in qa_requests:
            analysis = analyzer.analyze_request(request)
            assert analysis.request_type == RequestType.STANDARD_QA
            # Should not automatically generate exports for simple Q&A
            assert not analysis.should_generate_export or analysis.confidence < 0.5
    
    def test_format_preference_detection(self, analyzer):
        """Test detection of format preferences."""
        format_tests = [
            ("Export to Excel", ["excel"]),
            ("Give me a CSV file", ["csv"]),
            ("I need this in JSON format", ["json"]),
            ("Create a PDF report", ["pdf"]),
            ("Export as spreadsheet", ["excel"])
        ]
        
        for request, expected_formats in format_tests:
            analysis = analyzer.analyze_request(request)
            for expected_format in expected_formats:
                assert expected_format in analysis.export_format_preferences
    
    def test_template_type_detection(self, analyzer):
        """Test detection of appropriate template types."""
        template_tests = [
            ("Analyze the risks", "risk_analysis"),
            ("Summarize this document", "document_summary"),
            ("Compare all documents", "comparative_analysis"),
            ("Show conversation history", "qa_history"),
            ("Portfolio analysis", "portfolio_analysis")
        ]
        
        for request, expected_template in template_tests:
            analysis = analyzer.analyze_request(request)
            assert analysis.template_type == expected_template


class TestDataFormatter:
    """Test suite for Data Formatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create data formatter."""
        return DataFormatter()
    
    def test_text_response_formatting(self, formatter):
        """Test formatting of text responses."""
        text_response = """
        Summary: This is a test document
        Key Points:
        • Point 1
        • Point 2
        • Point 3
        
        Important Dates:
        - 2024-12-31: Expiration date
        - 2024-06-30: Review date
        
        Financial Terms: $100,000 total value
        """
        
        result = formatter.format_response_for_export(text_response, 'text')
        
        assert result.export_ready
        assert result.format_type == 'text'
        assert 'extracted_data' in result.structured_data
        assert 'tabular_data' in result.structured_data
        
        # Check that dates were extracted
        extracted_data = result.structured_data['extracted_data']
        assert 'dates' in extracted_data
        assert len(extracted_data['dates']) > 0
    
    def test_structured_response_formatting(self, formatter):
        """Test formatting of structured responses."""
        structured_response = {
            'summary': 'Document summary',
            'risks': [
                {'risk': 'Risk 1', 'severity': 'High'},
                {'risk': 'Risk 2', 'severity': 'Medium'}
            ],
            'parties': ['Party A', 'Party B'],
            'key_terms': {'Term 1': 'Definition 1'}
        }
        
        result = formatter.format_response_for_export(structured_response, 'structured')
        
        assert result.export_ready
        assert result.format_type == 'structured'
        assert 'tabular_data' in result.structured_data
        
        # Check that tabular data was created
        tabular_data = result.structured_data['tabular_data']
        assert len(tabular_data) > 0
        
        # Should have separate sheets for risks and other data
        sheet_names = [sheet['sheet_name'] for sheet in tabular_data]
        assert 'Risks' in sheet_names
    
    def test_qa_history_formatting(self, formatter):
        """Test formatting of Q&A history."""
        qa_history = [
            {
                'question': 'What is this document?',
                'answer': 'This is a test document',
                'timestamp': '2024-01-01T10:00:00',
                'analysis_mode': 'contract',
                'confidence': 0.9,
                'sources': ['Page 1', 'Page 2']
            },
            {
                'question': 'Who are the parties?',
                'answer': 'Party A and Party B',
                'timestamp': '2024-01-01T10:05:00',
                'analysis_mode': 'contract',
                'confidence': 0.8,
                'sources': ['Page 3']
            }
        ]
        
        result = formatter.format_response_for_export(qa_history, 'qa_history')
        
        assert result.export_ready
        assert result.format_type == 'qa_history'
        assert 'qa_history' in result.structured_data
        assert 'session_summary' in result.structured_data
        assert 'tabular_data' in result.structured_data
        
        # Check Q&A data structure
        qa_data = result.structured_data['qa_history']
        assert len(qa_data) == 2
        assert 'Question_Number' in qa_data[0]
        assert 'Question' in qa_data[0]
        assert 'Answer' in qa_data[0]
    
    def test_contract_analysis_formatting(self, formatter):
        """Test formatting of contract analysis results."""
        contract_data = {
            'document_type': 'Service Agreement',
            'effective_date': '2024-01-01',
            'parties': ['Company A', 'Company B'],
            'key_terms': {
                'Payment Terms': '30 days',
                'Termination': '30 days notice'
            },
            'obligations': [
                {'party': 'Company A', 'obligation': 'Provide services'},
                {'party': 'Company B', 'obligation': 'Make payments'}
            ],
            'risks': [
                {'risk': 'Payment default', 'severity': 'High'}
            ]
        }
        
        result = formatter.format_response_for_export(contract_data, 'contract_analysis')
        
        assert result.export_ready
        assert result.format_type == 'contract_analysis'
        assert 'contract_overview' in result.structured_data
        assert 'parties' in result.structured_data
        assert 'key_terms' in result.structured_data
        assert 'tabular_data' in result.structured_data
        
        # Check tabular data structure
        tabular_data = result.structured_data['tabular_data']
        sheet_names = [sheet['sheet_name'] for sheet in tabular_data]
        assert 'Contract Overview' in sheet_names
        assert 'Parties' in sheet_names
        assert 'Key Terms' in sheet_names
    
    def test_fallback_formatting(self, formatter):
        """Test fallback formatting when normal formatting fails."""
        # Create a problematic data structure
        problematic_data = object()  # Non-serializable object
        
        result = formatter.format_response_for_export(problematic_data, 'unknown_type')
        
        # Should still succeed with fallback
        assert result.export_ready
        assert result.format_type == 'fallback'
        assert len(result.warnings) > 0
        assert 'fallback_content' in result.structured_data
    
    def test_empty_data_formatting(self, formatter):
        """Test formatting of empty or null data."""
        empty_cases = [None, {}, [], ""]
        
        for empty_data in empty_cases:
            result = formatter.format_response_for_export(empty_data, 'generic')
            
            assert result.export_ready
            assert 'tabular_data' in result.structured_data
            # Should create at least one table even for empty data
            assert len(result.structured_data['tabular_data']) >= 1


class TestEndToEndWorkflow:
    """End-to-end integration tests for the complete workflow."""
    
    @pytest.fixture
    def complete_system(self, temp_dir):
        """Set up complete system for end-to-end testing."""
        mock_storage = Mock(spec=DocumentStorage)
        export_engine = ExcelExportEngine(mock_storage, temp_dir)
        request_analyzer = RequestAnalyzer()
        data_formatter = DataFormatter()
        
        return {
            'storage': mock_storage,
            'export_engine': export_engine,
            'analyzer': request_analyzer,
            'formatter': data_formatter
        }
    
    def test_complete_document_analysis_to_export_workflow(self, complete_system):
        """Test complete workflow from document upload to Excel export."""
        # Simulate document upload and analysis
        document_data = {
            'title': 'Test Contract',
            'content': 'This is a test contract with risks and obligations.',
            'analysis_results': {
                'risks': [
                    {'risk': 'Payment default', 'severity': 'High'},
                    {'risk': 'Delivery delay', 'severity': 'Medium'}
                ],
                'parties': ['Company A', 'Company B'],
                'key_terms': {'Payment': '30 days', 'Delivery': '60 days'}
            }
        }
        
        # Step 1: Analyze user request
        user_request = "Generate a risk analysis report for this contract"
        analysis = complete_system['analyzer'].analyze_request(user_request)
        
        assert analysis.should_generate_export
        assert analysis.template_type == 'risk_analysis'
        
        # Step 2: Format the data
        formatted_data = complete_system['formatter'].format_response_for_export(
            document_data['analysis_results'],
            'contract_analysis'
        )
        
        assert formatted_data.export_ready
        
        # Step 3: Generate export
        export_result = complete_system['export_engine'].export_tabular_data(
            formatted_data.structured_data,
            user_request,
            analysis.export_format_preferences
        )
        
        assert export_result.success
        assert os.path.exists(export_result.file_path)
        assert export_result.format_type in ['excel', 'csv', 'text']  # Any format is acceptable
    
    def test_concurrent_export_requests(self, complete_system):
        """Test handling of concurrent export requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def generate_export(request_id):
            try:
                data = {'test_data': f'Request {request_id}', 'id': request_id}
                result = complete_system['export_engine'].export_tabular_data(
                    data,
                    f"Export request {request_id}",
                    ['excel', 'csv']
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=generate_export, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert len(results) == 5
        
        # All exports should be successful
        for result in results:
            assert result.success
            assert os.path.exists(result.file_path)
    
    def test_large_data_export_performance(self, complete_system):
        """Test export performance with large datasets."""
        # Create large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                'id': i,
                'name': f'Item {i}',
                'description': f'Description for item {i}' * 10,  # Make it longer
                'category': f'Category {i % 10}',
                'value': i * 1.5,
                'date': f'2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'
            })
        
        start_time = time.time()
        
        result = complete_system['export_engine'].export_tabular_data(
            large_data,
            "Export large dataset",
            ['excel']
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert processing_time < 30  # 30 seconds max
        assert result.success
        assert os.path.exists(result.file_path)
        
        # Verify file is not empty
        file_size = os.path.getsize(result.file_path)
        assert file_size > 1000  # Should be substantial size
    
    def test_real_world_document_scenarios(self, complete_system):
        """Test with realistic document analysis scenarios."""
        scenarios = [
            {
                'name': 'MTA Analysis',
                'data': {
                    'document_type': 'Material Transfer Agreement',
                    'parties': ['University A', 'Company B'],
                    'materials': ['Cell lines', 'Reagents'],
                    'restrictions': ['No commercial use', 'Publication review required'],
                    'ip_rights': 'Retained by provider'
                },
                'user_request': 'Create an MTA analysis report'
            },
            {
                'name': 'Service Contract Risk Analysis',
                'data': {
                    'risks': [
                        {'risk': 'Service interruption', 'severity': 'High', 'probability': 0.3},
                        {'risk': 'Cost overrun', 'severity': 'Medium', 'probability': 0.6},
                        {'risk': 'Quality issues', 'severity': 'Medium', 'probability': 0.4}
                    ],
                    'mitigation_strategies': [
                        'Implement SLA monitoring',
                        'Regular quality reviews',
                        'Cost control measures'
                    ]
                },
                'user_request': 'Generate risk analysis with mitigation strategies'
            },
            {
                'name': 'Multi-Document Portfolio',
                'data': {
                    'documents': [
                        {'title': 'Contract 1', 'type': 'Service', 'risk_score': 7.5},
                        {'title': 'Contract 2', 'type': 'Purchase', 'risk_score': 4.2},
                        {'title': 'MTA 1', 'type': 'Research', 'risk_score': 3.8}
                    ],
                    'portfolio_metrics': {
                        'total_value': 500000,
                        'average_risk': 5.17,
                        'high_risk_count': 1
                    }
                },
                'user_request': 'Create portfolio analysis dashboard'
            }
        ]
        
        for scenario in scenarios:
            # Analyze request
            analysis = complete_system['analyzer'].analyze_request(scenario['user_request'])
            
            # Format data
            formatted_data = complete_system['formatter'].format_response_for_export(
                scenario['data'],
                'structured'
            )
            
            # Generate export
            result = complete_system['export_engine'].export_tabular_data(
                formatted_data.structured_data,
                scenario['user_request'],
                ['excel', 'csv']
            )
            
            assert result.success, f"Failed for scenario: {scenario['name']}"
            assert os.path.exists(result.file_path), f"File not created for scenario: {scenario['name']}"
            
            # Verify file has content
            file_size = os.path.getsize(result.file_path)
            assert file_size > 100, f"File too small for scenario: {scenario['name']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])