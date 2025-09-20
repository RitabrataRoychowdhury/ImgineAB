"""
Tests for ExcelReportGenerator functionality.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.excel_report_generator import ExcelReportGenerator
from src.models.conversational import ExcelReport, ExcelSheet
from src.models.document import Document


class TestExcelReportGenerator:
    """Test suite for ExcelReportGenerator."""
    
    @pytest.fixture
    def mock_document_storage(self):
        """Mock document storage."""
        storage = Mock()
        
        # Mock document
        mock_doc = Document(
            id="doc123",
            title="test_contract.pdf",
            file_type="pdf",
            file_size=1024,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="Test contract content"
        )
        
        storage.get_document.return_value = mock_doc
        return storage
    
    @pytest.fixture
    def temp_reports_dir(self):
        """Create temporary directory for reports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def excel_generator(self, mock_document_storage, temp_reports_dir):
        """Create ExcelReportGenerator instance."""
        return ExcelReportGenerator(mock_document_storage, temp_reports_dir)

    def test_generate_document_report_comprehensive(self, excel_generator):
        """Test generating comprehensive document report."""
        document_id = "doc123"
        report_type = "comprehensive"
        
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.return_value = {
                'summary': {
                    'document_overview': 'Test overview',
                    'key_findings': ['Finding 1', 'Finding 2'],
                    'executive_recommendation': 'Test recommendation'
                },
                'risks': [
                    {
                        'risk_id': 'R001',
                        'description': 'Test risk',
                        'severity': 'High',
                        'category': 'Legal',
                        'affected_parties': ['Party A'],
                        'mitigation_suggestions': ['Mitigation 1'],
                        'confidence': 0.8
                    }
                ],
                'commitments': [
                    {
                        'commitment_id': 'C001',
                        'description': 'Test commitment',
                        'obligated_party': 'Party A',
                        'beneficiary_party': 'Party B',
                        'deadline': '2024-12-31',
                        'status': 'Active',
                        'commitment_type': 'Deliverable'
                    }
                ],
                'deliverable_dates': [
                    {
                        'date': '2024-12-31',
                        'description': 'Test deliverable',
                        'responsible_party': 'Party A',
                        'deliverable_type': 'Report',
                        'status': 'Pending'
                    }
                ],
                'key_terms': ['Term 1', 'Term 2']
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                report = excel_generator.generate_document_report(document_id, report_type)
        
        assert isinstance(report, ExcelReport)
        assert report.report_id
        assert report.filename
        assert report.file_path
        assert report.download_url
        assert len(report.sheets) == 5  # Summary, Risks, Commitments, Dates, Terms
        assert report.created_at
        assert report.expires_at > report.created_at
        
        # Verify _create_excel_file was called
        mock_create.assert_called_once()

    def test_generate_document_report_risks_only(self, excel_generator):
        """Test generating risks-only document report."""
        document_id = "doc123"
        report_type = "risks_only"
        
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.return_value = {
                'risks': [
                    {
                        'risk_id': 'R001',
                        'description': 'Test risk',
                        'severity': 'High',
                        'category': 'Legal'
                    }
                ]
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                report = excel_generator.generate_document_report(document_id, report_type)
        
        assert isinstance(report, ExcelReport)
        assert len(report.sheets) == 1  # Only risks sheet
        assert report.sheets[0].name == "Risks"

    def test_generate_conversation_report(self, excel_generator):
        """Test generating conversation report."""
        session_id = "session123"
        
        with patch.object(excel_generator, '_extract_conversation_data') as mock_extract:
            mock_extract.return_value = {
                'session_summary': 'Test conversation summary',
                'turns': [
                    {
                        'question': 'Test question',
                        'response': 'Test response',
                        'timestamp': datetime.now(),
                        'analysis_mode': 'legal'
                    }
                ],
                'topics': ['Topic 1', 'Topic 2']
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                report = excel_generator.generate_conversation_report(session_id)
        
        assert isinstance(report, ExcelReport)
        assert len(report.sheets) == 3  # Summary, Q&A History, Topics
        assert any(sheet.name == "Conversation Summary" for sheet in report.sheets)
        assert any(sheet.name == "Q&A History" for sheet in report.sheets)
        assert any(sheet.name == "Topics" for sheet in report.sheets)

    def test_generate_comparative_report(self, excel_generator):
        """Test generating comparative report."""
        document_ids = ["doc123", "doc456"]
        
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.return_value = {
                'summary': {'document_overview': 'Test overview'},
                'risks': [{'risk_id': 'R001', 'severity': 'High'}],
                'commitments': [{'commitment_id': 'C001'}],
                'key_terms': ['Term 1']
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                report = excel_generator.generate_comparative_report(document_ids)
        
        assert isinstance(report, ExcelReport)
        assert len(report.sheets) == 4  # Comparative summary, risks, commitments, metrics
        assert any("Comparative" in sheet.name for sheet in report.sheets)

    def test_generate_comparative_report_insufficient_documents(self, excel_generator):
        """Test error when insufficient documents for comparative report."""
        document_ids = ["doc123"]  # Only one document
        
        with pytest.raises(ValueError, match="At least 2 documents required"):
            excel_generator.generate_comparative_report(document_ids)

    def test_create_custom_report(self, excel_generator):
        """Test creating custom report."""
        data_specification = {
            'document_ids': ['doc123', 'doc456'],
            'include_sections': ['summary', 'risks'],
            'filters': {'risk_severity': ['High', 'Medium']}
        }
        
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.return_value = {
                'summary': {'document_overview': 'Test overview'},
                'risks': [
                    {'risk_id': 'R001', 'severity': 'High'},
                    {'risk_id': 'R002', 'severity': 'Low'}  # Should be filtered out
                ]
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                report = excel_generator.create_custom_report(data_specification)
        
        assert isinstance(report, ExcelReport)
        assert len(report.sheets) == 2  # Summary and risks only

    def test_create_summary_sheet(self, excel_generator, mock_document_storage):
        """Test creating summary sheet."""
        document = mock_document_storage.get_document("doc123")
        analysis_data = {
            'summary': {
                'document_overview': 'Test overview',
                'executive_recommendation': 'Test recommendation',
                'key_findings': ['Finding 1', 'Finding 2']
            }
        }
        
        sheet = excel_generator._create_summary_sheet(document, analysis_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Summary"
        assert len(sheet.data) >= 4  # Document name, date, overview, recommendation
        assert any(item['Section'] == 'Document Name' for item in sheet.data)
        assert any(item['Section'] == 'Document Overview' for item in sheet.data)

    def test_create_risks_sheet(self, excel_generator):
        """Test creating risks sheet."""
        risks_data = [
            {
                'risk_id': 'R001',
                'description': 'Test risk description',
                'severity': 'High',
                'category': 'Legal',
                'affected_parties': ['Party A', 'Party B'],
                'mitigation_suggestions': ['Mitigation 1'],
                'confidence': 0.8
            },
            {
                'risk_id': 'R002',
                'description': 'Another risk',
                'severity': 'Medium',
                'category': 'Financial',
                'affected_parties': ['Party C'],
                'mitigation_suggestions': ['Mitigation 2'],
                'confidence': 0.7
            }
        ]
        
        sheet = excel_generator._create_risks_sheet(risks_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Risks"
        assert len(sheet.data) == 2
        assert sheet.data[0]['Risk ID'] == 'R001'
        assert sheet.data[0]['Severity'] == 'High'
        assert sheet.data[1]['Risk ID'] == 'R002'
        assert len(sheet.charts) == 1  # Should have risk distribution chart

    def test_create_commitments_sheet(self, excel_generator):
        """Test creating commitments sheet."""
        commitments_data = [
            {
                'commitment_id': 'C001',
                'description': 'Test commitment',
                'obligated_party': 'Party A',
                'beneficiary_party': 'Party B',
                'deadline': '2024-12-31',
                'status': 'Active',
                'commitment_type': 'Deliverable'
            }
        ]
        
        sheet = excel_generator._create_commitments_sheet(commitments_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Commitments"
        assert len(sheet.data) == 1
        assert sheet.data[0]['Commitment ID'] == 'C001'
        assert sheet.data[0]['Obligated Party'] == 'Party A'

    def test_create_dates_sheet(self, excel_generator):
        """Test creating deliverable dates sheet."""
        dates_data = [
            {
                'date': '2024-12-31',
                'description': 'Test deliverable',
                'responsible_party': 'Party A',
                'deliverable_type': 'Report',
                'status': 'Pending'
            }
        ]
        
        sheet = excel_generator._create_dates_sheet(dates_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Important Dates"
        assert len(sheet.data) == 1
        assert sheet.data[0]['Date'] == '2024-12-31'
        assert sheet.data[0]['Responsible Party'] == 'Party A'

    def test_create_terms_sheet(self, excel_generator):
        """Test creating key terms sheet."""
        terms_data = ['Term 1', 'Term 2', 'Term 3']
        
        sheet = excel_generator._create_terms_sheet(terms_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Key Terms"
        assert len(sheet.data) == 3
        assert sheet.data[0]['Term'] == 'Term 1'
        assert all(item['Frequency'] == 1 for item in sheet.data)

    def test_create_conversation_summary_sheet(self, excel_generator):
        """Test creating conversation summary sheet."""
        conversation_data = {
            'session_summary': 'Test session summary',
            'turns': [{'question': 'Q1'}, {'question': 'Q2'}],
            'topics': ['Topic 1', 'Topic 2']
        }
        
        sheet = excel_generator._create_conversation_summary_sheet(conversation_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Conversation Summary"
        assert len(sheet.data) == 3  # Summary, total questions, topics
        assert any(item['Metric'] == 'Session Summary' for item in sheet.data)
        assert any(item['Value'] == 2 for item in sheet.data)  # Total questions

    def test_create_qa_history_sheet(self, excel_generator):
        """Test creating Q&A history sheet."""
        turns_data = [
            {
                'question': 'Test question 1',
                'response': 'Test response 1',
                'timestamp': datetime.now(),
                'analysis_mode': 'legal'
            },
            {
                'question': 'Test question 2',
                'response': 'Test response 2',
                'timestamp': datetime.now(),
                'analysis_mode': 'casual'
            }
        ]
        
        sheet = excel_generator._create_qa_history_sheet(turns_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Q&A History"
        assert len(sheet.data) == 2
        assert sheet.data[0]['Turn'] == 1
        assert sheet.data[0]['Question'] == 'Test question 1'
        assert sheet.data[1]['Turn'] == 2
        assert sheet.data[1]['Analysis Mode'] == 'casual'

    def test_create_comparative_summary_sheet(self, excel_generator, mock_document_storage):
        """Test creating comparative summary sheet."""
        documents_data = [
            {
                'document': mock_document_storage.get_document("doc123"),
                'analysis': {
                    'risks': [{'risk_id': 'R001'}],
                    'commitments': [{'commitment_id': 'C001'}],
                    'key_terms': ['Term1', 'Term2']
                }
            },
            {
                'document': mock_document_storage.get_document("doc123"),  # Same mock doc
                'analysis': {
                    'risks': [{'risk_id': 'R002'}, {'risk_id': 'R003'}],
                    'commitments': [],
                    'key_terms': ['Term3']
                }
            }
        ]
        
        sheet = excel_generator._create_comparative_summary_sheet(documents_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Comparative Summary"
        assert len(sheet.data) == 2
        assert sheet.data[0]['Risk Count'] == 1
        assert sheet.data[1]['Risk Count'] == 2
        assert sheet.data[0]['Commitment Count'] == 1
        assert sheet.data[1]['Commitment Count'] == 0

    def test_create_comparative_metrics_sheet(self, excel_generator, mock_document_storage):
        """Test creating comparative metrics sheet."""
        documents_data = [
            {
                'document': mock_document_storage.get_document("doc123"),
                'analysis': {
                    'risks': [
                        {'severity': 'High'},
                        {'severity': 'Medium'},
                        {'severity': 'Low'}
                    ]
                }
            }
        ]
        
        sheet = excel_generator._create_comparative_metrics_sheet(documents_data)
        
        assert isinstance(sheet, ExcelSheet)
        assert sheet.name == "Risk Metrics"
        assert len(sheet.data) == 1
        assert sheet.data[0]['Total Risks'] == 3
        assert sheet.data[0]['High Risk Count'] == 1
        assert sheet.data[0]['Medium Risk Count'] == 1
        assert sheet.data[0]['Low Risk Count'] == 1
        assert sheet.data[0]['Risk Score'] == 6  # (1*3) + (1*2) + (1*1)

    def test_apply_custom_filters_risk_severity(self, excel_generator):
        """Test applying custom filters for risk severity."""
        analysis_data = {
            'risks': [
                {'risk_id': 'R001', 'severity': 'High'},
                {'risk_id': 'R002', 'severity': 'Medium'},
                {'risk_id': 'R003', 'severity': 'Low'}
            ]
        }
        
        filters = {'risk_severity': ['High', 'Medium']}
        
        filtered_data = excel_generator._apply_custom_filters(analysis_data, filters)
        
        assert len(filtered_data['risks']) == 2
        assert all(risk['severity'] in ['High', 'Medium'] for risk in filtered_data['risks'])

    def test_extract_document_analysis_data_mock(self, excel_generator):
        """Test document analysis data extraction (mock implementation)."""
        document_id = "doc123"
        
        analysis_data = excel_generator._extract_document_analysis_data(document_id)
        
        assert isinstance(analysis_data, dict)
        assert 'summary' in analysis_data
        assert 'risks' in analysis_data
        assert 'commitments' in analysis_data
        assert 'deliverable_dates' in analysis_data
        assert 'key_terms' in analysis_data

    def test_extract_conversation_data_mock(self, excel_generator):
        """Test conversation data extraction (mock implementation)."""
        session_id = "session123"
        
        conversation_data = excel_generator._extract_conversation_data(session_id)
        
        assert isinstance(conversation_data, dict)
        assert 'session_summary' in conversation_data
        assert 'turns' in conversation_data
        assert 'topics' in conversation_data

    def test_error_handling_document_not_found(self, excel_generator, mock_document_storage):
        """Test error handling when document is not found."""
        mock_document_storage.get_document.return_value = None
        
        with pytest.raises(ValueError, match="Document doc123 not found"):
            excel_generator.generate_document_report("doc123")

    def test_error_handling_in_report_generation(self, excel_generator):
        """Test error handling during report generation."""
        document_id = "doc123"
        
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.side_effect = Exception("Analysis error")
            
            with pytest.raises(Exception):
                excel_generator.generate_document_report(document_id)

    def test_create_excel_file(self, excel_generator):
        """Test Excel file creation (basic functionality test)."""
        sheets = [
            ExcelSheet(
                name="Test Sheet",
                data=[{'Column1': 'Value1', 'Column2': 'Value2'}],
                formatting={'header_style': 'bold'},
                charts=[]
            )
        ]
        
        # Test with a temporary file path
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            file_path = tmp_file.name
        
        try:
            # This should not raise an exception
            excel_generator._create_excel_file(sheets, file_path)
            
            # Verify file was created
            import os
            assert os.path.exists(file_path)
            
        finally:
            # Clean up
            import os
            if os.path.exists(file_path):
                os.unlink(file_path)

    def test_reports_directory_creation(self, mock_document_storage):
        """Test that reports directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reports_dir = os.path.join(temp_dir, "new_reports_dir")
            
            # Directory shouldn't exist initially
            assert not os.path.exists(reports_dir)
            
            # Create generator (should create directory)
            excel_generator = ExcelReportGenerator(mock_document_storage, reports_dir)
            
            # Directory should now exist
            assert os.path.exists(reports_dir)