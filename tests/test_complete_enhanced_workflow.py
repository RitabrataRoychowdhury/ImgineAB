"""Complete enhanced Q&A workflow integration tests."""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.models.document import Document, ComprehensiveAnalysis, RiskAssessment, Commitment
from src.models.conversational import ConversationContext, ConversationalResponse
from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
from src.services.conversational_ai_engine import ConversationalAIEngine
from src.services.excel_report_generator import ExcelReportGenerator
from src.services.template_engine import TemplateEngine
from src.storage.enhanced_storage import EnhancedDocumentStorage
from src.utils.error_handling import graceful_degradation


class TestCompleteEnhancedWorkflow:
    """Test complete enhanced Q&A workflow from document upload to report generation."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def temp_reports_dir(self):
        """Create temporary reports directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def enhanced_storage(self, temp_db):
        """Create enhanced storage with test database."""
        storage = EnhancedDocumentStorage()
        # Initialize with test database
        from src.storage.database import DatabaseManager
        storage.db_manager = DatabaseManager(temp_db)
        return storage
    
    @pytest.fixture
    def sample_contract_document(self):
        """Create sample contract document for testing."""
        return Document(
            id="contract_001",
            title="Software Development Agreement",
            file_type="pdf",
            file_size=15000,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="""
            SOFTWARE DEVELOPMENT AGREEMENT
            
            This Agreement is entered into between TechCorp Inc. ("Client") and DevStudio LLC ("Developer").
            
            1. SCOPE OF WORK
            Developer shall deliver a complete web application by December 31, 2024.
            The application must include user authentication, data management, and reporting features.
            
            2. PAYMENT TERMS
            Total project cost: $50,000
            Payment schedule: 50% upfront, 50% upon completion
            Late payment penalty: 2% per month
            
            3. DELIVERABLES
            - Technical specification: Due November 15, 2024
            - Beta version: Due December 15, 2024
            - Final version: Due December 31, 2024
            - Documentation: Due January 5, 2025
            
            4. LIABILITY
            Developer's liability is limited to the total contract amount.
            Client assumes responsibility for data backup and security.
            
            5. TERMINATION
            Either party may terminate with 30 days written notice.
            Upon termination, Client pays for work completed.
            """,
            is_legal_document=True,
            legal_document_type="Service Agreement"
        )
    
    @pytest.fixture
    def mock_gemini_api(self):
        """Mock Gemini API responses for testing."""
        def mock_api_call(prompt, max_tokens=1000):
            if "risk" in prompt.lower():
                return json.dumps({
                    "risks": [
                        {
                            "description": "Late delivery penalty risk",
                            "severity": "High",
                            "category": "Financial",
                            "affected_parties": ["Developer"],
                            "mitigation_suggestions": ["Set realistic timelines", "Add buffer time"],
                            "source_text": "Final version: Due December 31, 2024",
                            "confidence": 0.9
                        },
                        {
                            "description": "Limited liability exposure",
                            "severity": "Medium",
                            "category": "Legal",
                            "affected_parties": ["Client"],
                            "mitigation_suggestions": ["Consider additional insurance"],
                            "source_text": "Developer's liability is limited to the total contract amount",
                            "confidence": 0.8
                        }
                    ]
                })
            elif "commitment" in prompt.lower():
                return json.dumps({
                    "commitments": [
                        {
                            "description": "Deliver complete web application",
                            "obligated_party": "Developer",
                            "beneficiary_party": "Client",
                            "deadline": "2024-12-31",
                            "commitment_type": "Deliverable",
                            "status": "Active",
                            "source_text": "Developer shall deliver a complete web application by December 31, 2024"
                        },
                        {
                            "description": "Pay 50% upfront payment",
                            "obligated_party": "Client",
                            "beneficiary_party": "Developer",
                            "deadline": null,
                            "commitment_type": "Payment",
                            "status": "Active",
                            "source_text": "Payment schedule: 50% upfront, 50% upon completion"
                        }
                    ]
                })
            elif "date" in prompt.lower():
                return json.dumps({
                    "deliverable_dates": [
                        {
                            "date": "2024-11-15",
                            "description": "Technical specification delivery",
                            "responsible_party": "Developer",
                            "deliverable_type": "Documentation",
                            "status": "Pending",
                            "source_text": "Technical specification: Due November 15, 2024"
                        },
                        {
                            "date": "2024-12-31",
                            "description": "Final version delivery",
                            "responsible_party": "Developer",
                            "deliverable_type": "Software",
                            "status": "Pending",
                            "source_text": "Final version: Due December 31, 2024"
                        }
                    ]
                })
            else:
                return "This is a software development agreement between TechCorp Inc. and DevStudio LLC for building a web application."
        
        return mock_api_call
    
    def test_complete_document_analysis_workflow(self, enhanced_storage, sample_contract_document, mock_gemini_api):
        """Test complete document analysis from upload to comprehensive analysis."""
        
        # Initialize analyzer with mocked API
        analyzer = EnhancedSummaryAnalyzer(enhanced_storage, "test_api_key")
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=mock_gemini_api):
            # Perform comprehensive analysis
            analysis = analyzer.analyze_document_comprehensive(sample_contract_document)
            
            # Verify analysis completeness
            assert analysis.document_id == sample_contract_document.id
            assert len(analysis.risks) == 2
            assert len(analysis.commitments) == 2
            assert len(analysis.deliverable_dates) == 2
            
            # Verify risk analysis
            high_risks = [r for r in analysis.risks if r.severity == "High"]
            assert len(high_risks) == 1
            assert "Late delivery" in high_risks[0].description
            
            # Verify commitment extraction
            developer_commitments = [c for c in analysis.commitments if c.obligated_party == "Developer"]
            assert len(developer_commitments) == 1
            assert "web application" in developer_commitments[0].description
            
            # Verify date extraction
            future_dates = [d for d in analysis.deliverable_dates if d.date > datetime.now()]
            assert len(future_dates) >= 1
    
    def test_conversational_ai_workflow(self, enhanced_storage, sample_contract_document):
        """Test conversational AI workflow with context management."""
        
        # Mock engines
        qa_engine = Mock()
        contract_engine = Mock()
        
        # Set up mock responses
        qa_engine.answer_question.return_value = {
            'answer': 'The contract is between TechCorp Inc. and DevStudio LLC.',
            'confidence': 0.8,
            'sources': ['contract_text']
        }
        
        contract_engine.analyze_contract_query.return_value = {
            'answer': 'The liability is limited to the total contract amount of $50,000.',
            'confidence': 0.9,
            'sources': ['liability_clause']
        }
        
        # Initialize conversational engine
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Test conversation flow
        session_id = "test_session_001"
        document_id = sample_contract_document.id
        
        # First question - casual
        response1 = conv_engine.answer_conversational_question(
            "Who are the parties in this contract?",
            document_id,
            session_id
        )
        
        assert "TechCorp Inc." in response1.answer
        assert response1.analysis_mode in ["casual", "legal"]
        
        # Second question - legal
        response2 = conv_engine.answer_conversational_question(
            "What is the liability limitation in this agreement?",
            document_id,
            session_id
        )
        
        assert "$50,000" in response2.answer
        assert response2.analysis_mode == "legal"
        
        # Verify context is maintained
        assert session_id in conv_engine.conversation_contexts
        context = conv_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 2
    
    def test_excel_report_generation_workflow(self, enhanced_storage, temp_reports_dir, sample_contract_document):
        """Test Excel report generation workflow."""
        
        # Initialize report generator
        generator = ExcelReportGenerator(enhanced_storage, temp_reports_dir)
        
        # Mock document storage
        enhanced_storage.get_document = Mock(return_value=sample_contract_document)
        
        # Mock analysis data
        mock_analysis_data = {
            'summary': {
                'document_overview': 'Software development agreement',
                'key_findings': ['Payment terms defined', 'Delivery dates specified'],
                'executive_recommendation': 'Review liability limitations'
            },
            'risks': [
                {
                    'risk_id': 'R001',
                    'description': 'Late delivery penalty',
                    'severity': 'High',
                    'category': 'Financial'
                }
            ],
            'commitments': [
                {
                    'commitment_id': 'C001',
                    'description': 'Deliver web application',
                    'obligated_party': 'Developer',
                    'deadline': '2024-12-31'
                }
            ],
            'deliverable_dates': [
                {
                    'date': '2024-12-31',
                    'description': 'Final delivery',
                    'responsible_party': 'Developer'
                }
            ]
        }
        
        with patch.object(generator, '_extract_document_analysis_data', return_value=mock_analysis_data):
            # Generate comprehensive report
            report = generator.generate_document_report(sample_contract_document.id, "comprehensive")
            
            # Verify report creation
            assert report.report_id is not None
            assert report.filename.endswith('.xlsx')
            assert os.path.exists(report.file_path)
            assert len(report.sheets) > 0
            
            # Verify sheet content
            sheet_names = [sheet.name for sheet in report.sheets]
            assert "Summary" in sheet_names
            assert "Risks" in sheet_names
            assert "Commitments" in sheet_names
    
    def test_template_engine_integration(self, enhanced_storage, sample_contract_document):
        """Test template engine integration with analysis workflow."""
        
        # Initialize template engine
        template_engine = TemplateEngine(enhanced_storage)
        
        # Test template recommendation
        recommended_template = template_engine.recommend_template(sample_contract_document)
        
        assert recommended_template is not None
        assert recommended_template.name == "Contract Analysis"
        assert "risk_assessment" in recommended_template.analysis_sections
        
        # Test template application
        template_result = template_engine.apply_template(sample_contract_document, recommended_template)
        
        assert 'prompts' in template_result
        assert 'parameters' in template_result
        assert len(template_result['prompts']) > 0
    
    def test_error_handling_integration(self, enhanced_storage, sample_contract_document):
        """Test error handling across integrated components."""
        
        # Initialize components
        analyzer = EnhancedSummaryAnalyzer(enhanced_storage, "test_api_key")
        
        # Test API failure handling
        with patch.object(analyzer, '_call_gemini_api', side_effect=Exception("API Error")):
            # Should handle error gracefully
            analysis = analyzer.analyze_document_comprehensive(sample_contract_document)
            
            # Should have basic analysis even with API failure
            assert analysis.document_id == sample_contract_document.id
            assert analysis.confidence_score < 0.8  # Lower confidence due to failures
    
    def test_performance_with_large_document(self, enhanced_storage):
        """Test system performance with large documents."""
        
        # Create large document
        large_content = "This is a test contract. " * 1000  # Simulate large document
        large_document = Document(
            id="large_doc_001",
            title="Large Contract Document",
            file_type="pdf",
            file_size=len(large_content),
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text=large_content,
            is_legal_document=True
        )
        
        # Initialize analyzer
        analyzer = EnhancedSummaryAnalyzer(enhanced_storage, "test_api_key")
        
        # Mock API with timeout simulation
        def slow_api_call(prompt, max_tokens=1000):
            import time
            time.sleep(0.1)  # Simulate API delay
            return '{"risks": [], "commitments": [], "deliverable_dates": []}'
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=slow_api_call):
            start_time = datetime.now()
            
            # Perform analysis
            analysis = analyzer.analyze_document_comprehensive(large_document)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Verify reasonable processing time (should be under 10 seconds for test)
            assert processing_time < 10
            assert analysis.document_id == large_document.id
    
    def test_concurrent_analysis_handling(self, enhanced_storage, sample_contract_document):
        """Test handling of concurrent analysis requests."""
        
        # This would test concurrent processing capabilities
        # For now, just verify basic functionality
        analyzer = EnhancedSummaryAnalyzer(enhanced_storage, "test_api_key")
        
        with patch.object(analyzer, '_call_gemini_api', return_value='{"risks": []}'):
            # Simulate multiple concurrent requests
            analyses = []
            for i in range(3):
                doc = Document(
                    id=f"doc_{i}",
                    title=f"Document {i}",
                    file_type="pdf",
                    file_size=1000,
                    upload_timestamp=datetime.now(),
                    processing_status="completed",
                    original_text=f"Content for document {i}",
                    is_legal_document=True
                )
                
                analysis = analyzer.analyze_document_comprehensive(doc)
                analyses.append(analysis)
            
            # Verify all analyses completed
            assert len(analyses) == 3
            for i, analysis in enumerate(analyses):
                assert analysis.document_id == f"doc_{i}"
    
    def test_data_consistency_across_components(self, enhanced_storage, sample_contract_document, temp_reports_dir):
        """Test data consistency between analysis, conversation, and reporting components."""
        
        # Perform analysis
        analyzer = EnhancedSummaryAnalyzer(enhanced_storage, "test_api_key")
        
        mock_risks = [
            RiskAssessment(
                risk_id="R001",
                description="Test risk",
                severity="High",
                category="Legal",
                affected_parties=["Party A"],
                mitigation_suggestions=["Suggestion 1"],
                source_text="Source text",
                confidence=0.9
            )
        ]
        
        with patch.object(analyzer, 'identify_risks', return_value=mock_risks):
            with patch.object(analyzer, 'extract_commitments', return_value=[]):
                with patch.object(analyzer, 'find_deliverable_dates', return_value=[]):
                    
                    analysis = analyzer.analyze_document_comprehensive(sample_contract_document)
                    
                    # Store analysis
                    enhanced_storage.save_comprehensive_analysis = Mock(return_value=analysis.analysis_id)
                    enhanced_storage.get_comprehensive_analysis = Mock(return_value=analysis)
                    
                    # Generate report based on same analysis
                    generator = ExcelReportGenerator(enhanced_storage, temp_reports_dir)
                    enhanced_storage.get_document = Mock(return_value=sample_contract_document)
                    
                    with patch.object(generator, '_extract_document_analysis_data') as mock_extract:
                        mock_extract.return_value = {
                            'risks': [risk.__dict__ for risk in analysis.risks],
                            'commitments': [],
                            'deliverable_dates': []
                        }
                        
                        report = generator.generate_document_report(sample_contract_document.id)
                        
                        # Verify data consistency
                        assert report.report_id is not None
                        # Risk data should be consistent between analysis and report
                        mock_extract.assert_called_once()
    
    def test_user_acceptance_scenarios(self, enhanced_storage, sample_contract_document):
        """Test user acceptance scenarios for enhanced Q&A features."""
        
        # Scenario 1: User uploads contract and gets enhanced summary
        analyzer = EnhancedSummaryAnalyzer(enhanced_storage, "test_api_key")
        
        with patch.object(analyzer, '_call_gemini_api', return_value='{"risks": [], "commitments": []}'):
            summary = analyzer.generate_enhanced_summary(sample_contract_document)
            
            # User should see enhanced summary sections
            expected_sections = [
                'document_overview', 'key_findings', 'critical_information',
                'recommended_actions', 'executive_recommendation'
            ]
            
            for section in expected_sections:
                assert section in summary
        
        # Scenario 2: User asks conversational questions
        qa_engine = Mock()
        contract_engine = Mock()
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        qa_engine.answer_question.return_value = {
            'answer': 'The payment terms are 50% upfront and 50% upon completion.',
            'confidence': 0.8,
            'sources': []
        }
        
        response = conv_engine.answer_conversational_question(
            "What are the payment terms?",
            sample_contract_document.id,
            "user_session_1"
        )
        
        # User should get natural conversational response
        assert "payment terms" in response.answer.lower()
        assert response.confidence > 0.5
        
        # Scenario 3: User requests Excel report
        generator = ExcelReportGenerator(enhanced_storage, "/tmp")
        enhanced_storage.get_document = Mock(return_value=sample_contract_document)
        
        with patch.object(generator, '_extract_document_analysis_data', return_value={}):
            with patch.object(generator, '_create_excel_file'):
                report = generator.generate_document_report(sample_contract_document.id)
                
                # User should get downloadable report
                assert report.download_url is not None
                assert report.filename.endswith('.xlsx')


if __name__ == "__main__":
    pytest.main([__file__])