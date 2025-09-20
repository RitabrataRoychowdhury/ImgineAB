"""
Integration tests for conversational AI and Excel generation capabilities.
"""

import pytest
import tempfile
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.conversational_ai_engine import ConversationalAIEngine
from src.services.excel_report_generator import ExcelReportGenerator
from src.models.conversational import ConversationalResponse, ExcelReport
from src.models.document import Document


class TestConversationalExcelIntegration:
    """Integration tests for conversational AI and Excel generation."""
    
    @pytest.fixture
    def mock_qa_engine(self):
        """Mock QA engine."""
        engine = Mock()
        engine.answer_question.return_value = {
            'answer': 'Based on the document analysis, here are the key findings...',
            'sources': ['document_section_1', 'document_section_2'],
            'confidence': 0.85
        }
        return engine
    
    @pytest.fixture
    def mock_contract_engine(self):
        """Mock contract analyst engine."""
        engine = Mock()
        engine.analyze_contract_query.return_value = {
            'answer': 'The contract contains several liability clauses...',
            'sources': ['clause_5.2', 'clause_8.1'],
            'confidence': 0.92
        }
        return engine
    
    @pytest.fixture
    def mock_document_storage(self):
        """Mock document storage."""
        storage = Mock()
        
        mock_doc = Document(
            id="doc123",
            title="sample_contract.pdf",
            file_type="pdf",
            file_size=2048,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="This is a sample contract with various clauses..."
        )
        
        storage.get_document.return_value = mock_doc
        return storage
    
    @pytest.fixture
    def temp_reports_dir(self):
        """Create temporary directory for reports."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def conversational_engine(self, mock_qa_engine, mock_contract_engine):
        """Create ConversationalAIEngine instance."""
        return ConversationalAIEngine(mock_qa_engine, mock_contract_engine)
    
    @pytest.fixture
    def excel_generator(self, mock_document_storage, temp_reports_dir):
        """Create ExcelReportGenerator instance."""
        return ExcelReportGenerator(mock_document_storage, temp_reports_dir)

    def test_conversational_flow_with_excel_generation_request(self, conversational_engine, excel_generator):
        """Test complete flow from conversation to Excel generation."""
        document_id = "doc123"
        session_id = "session123"
        
        # Simulate conversation leading to Excel request
        questions_and_expected_modes = [
            ("Hello, can you help me analyze this contract?", "casual"),
            ("What are the main liability clauses?", "legal"),
            ("Can you generate an Excel report with all the risks and commitments?", "casual")
        ]
        
        conversation_responses = []
        
        for question, expected_mode in questions_and_expected_modes:
            response = conversational_engine.answer_conversational_question(
                question, document_id, session_id
            )
            
            assert isinstance(response, ConversationalResponse)
            assert response.answer
            conversation_responses.append(response)
        
        # Verify conversation context was maintained
        assert session_id in conversational_engine.conversation_contexts
        context = conversational_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 3
        
        # Now generate Excel report based on conversation
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.return_value = {
                'summary': {
                    'document_overview': 'Contract analysis summary',
                    'key_findings': ['Liability clauses present', 'Payment terms defined'],
                    'executive_recommendation': 'Review liability sections carefully'
                },
                'risks': [
                    {
                        'risk_id': 'R001',
                        'description': 'High liability exposure in section 5',
                        'severity': 'High',
                        'category': 'Legal',
                        'affected_parties': ['Company A'],
                        'mitigation_suggestions': ['Add liability caps'],
                        'confidence': 0.9
                    }
                ],
                'commitments': [
                    {
                        'commitment_id': 'C001',
                        'description': 'Monthly reporting requirement',
                        'obligated_party': 'Company A',
                        'beneficiary_party': 'Company B',
                        'deadline': '2024-12-31',
                        'status': 'Active',
                        'commitment_type': 'Reporting'
                    }
                ],
                'deliverable_dates': [],
                'key_terms': ['liability', 'indemnification', 'breach']
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                excel_report = excel_generator.generate_document_report(document_id, "comprehensive")
        
        assert isinstance(excel_report, ExcelReport)
        assert excel_report.filename
        assert len(excel_report.sheets) == 5  # Summary, Risks, Commitments, Dates, Terms

    def test_compound_question_with_excel_generation(self, conversational_engine, excel_generator):
        """Test handling compound questions that request Excel generation."""
        document_id = "doc123"
        session_id = "session456"
        
        compound_question = ("What are the main risks in this contract and can you also "
                           "generate an Excel report with all commitments and deadlines?")
        
        # Handle compound question
        compound_response = conversational_engine.handle_compound_question(
            compound_question, document_id, session_id
        )
        
        assert len(compound_response.question_parts) >= 2
        assert compound_response.synthesized_response
        assert "legal" in compound_response.analysis_modes_used or "casual" in compound_response.analysis_modes_used
        
        # Generate Excel report for commitments as requested
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.return_value = {
                'commitments': [
                    {
                        'commitment_id': 'C001',
                        'description': 'Quarterly review meetings',
                        'obligated_party': 'Vendor',
                        'beneficiary_party': 'Client',
                        'deadline': '2024-03-31',
                        'status': 'Active',
                        'commitment_type': 'Meeting'
                    },
                    {
                        'commitment_id': 'C002',
                        'description': 'Annual compliance audit',
                        'obligated_party': 'Client',
                        'beneficiary_party': 'Regulatory Body',
                        'deadline': '2024-12-31',
                        'status': 'Pending',
                        'commitment_type': 'Audit'
                    }
                ]
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                excel_report = excel_generator.generate_document_report(document_id, "commitments_only")
        
        assert isinstance(excel_report, ExcelReport)
        assert len(excel_report.sheets) == 1
        assert excel_report.sheets[0].name == "Commitments"

    def test_conversation_context_influences_excel_report(self, conversational_engine, excel_generator):
        """Test that conversation context influences Excel report generation."""
        document_id = "doc123"
        session_id = "session789"
        
        # Build conversation context focused on risks
        risk_focused_questions = [
            "What are the highest priority risks in this document?",
            "Are there any financial risks I should be concerned about?",
            "What about operational risks?"
        ]
        
        for question in risk_focused_questions:
            conversational_engine.answer_conversational_question(question, document_id, session_id)
        
        # Verify context was built
        context = conversational_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 3
        
        # Generate conversation report that includes the risk-focused discussion
        with patch.object(excel_generator, '_extract_conversation_data') as mock_extract:
            mock_extract.return_value = {
                'session_summary': 'Risk-focused analysis discussion',
                'turns': [
                    {
                        'question': q,
                        'response': f'Analysis response for: {q}',
                        'timestamp': datetime.now(),
                        'analysis_mode': 'legal'
                    } for q in risk_focused_questions
                ],
                'topics': ['risks', 'financial', 'operational', 'priority']
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                conversation_report = excel_generator.generate_conversation_report(session_id)
        
        assert isinstance(conversation_report, ExcelReport)
        assert len(conversation_report.sheets) == 3  # Summary, Q&A History, Topics
        
        # Verify the conversation report captures the risk focus
        qa_history_sheet = next(sheet for sheet in conversation_report.sheets if sheet.name == "Q&A History")
        assert len(qa_history_sheet.data) == 3
        assert all('risk' in turn['Question'].lower() for turn in qa_history_sheet.data)

    def test_mode_switching_during_excel_workflow(self, conversational_engine, excel_generator):
        """Test analysis mode switching during Excel generation workflow."""
        document_id = "doc123"
        session_id = "session101"
        
        # Start with casual conversation
        casual_response = conversational_engine.answer_conversational_question(
            "Hi, I need help with document analysis", document_id, session_id
        )
        assert casual_response.analysis_mode == "casual"
        
        # Switch to legal analysis
        legal_response = conversational_engine.answer_conversational_question(
            "What are the indemnification clauses in this contract?", document_id, session_id
        )
        assert legal_response.analysis_mode == "legal"
        
        # Request Excel generation (casual mode)
        excel_request_response = conversational_engine.answer_conversational_question(
            "Can you create an Excel report with all this information?", document_id, session_id
        )
        assert excel_request_response.analysis_mode == "casual"
        
        # Verify mode switching was tracked in context
        context = conversational_engine.conversation_contexts[session_id]
        modes_used = [turn.analysis_mode for turn in context.conversation_history]
        assert "casual" in modes_used
        assert "legal" in modes_used

    def test_comparative_analysis_conversation_flow(self, conversational_engine, excel_generator):
        """Test conversation flow leading to comparative analysis Excel report."""
        document_ids = ["doc123", "doc456"]
        session_id = "session202"
        
        # Simulate conversation about multiple documents
        multi_doc_questions = [
            "I have two contracts I need to compare",
            "What are the main differences in risk profiles between these documents?",
            "Can you generate a comparative Excel report?"
        ]
        
        for question in multi_doc_questions:
            response = conversational_engine.answer_conversational_question(
                question, document_ids[0], session_id  # Use first doc as primary
            )
            assert isinstance(response, ConversationalResponse)
        
        # Generate comparative Excel report
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            # Mock different analysis results for each document
            def mock_analysis_side_effect(doc_id):
                if doc_id == "doc123":
                    return {
                        'risks': [{'risk_id': 'R001', 'severity': 'High'}],
                        'commitments': [{'commitment_id': 'C001'}],
                        'key_terms': ['liability', 'breach']
                    }
                else:  # doc456
                    return {
                        'risks': [{'risk_id': 'R002', 'severity': 'Medium'}],
                        'commitments': [{'commitment_id': 'C002'}, {'commitment_id': 'C003'}],
                        'key_terms': ['warranty', 'performance']
                    }
            
            mock_extract.side_effect = mock_analysis_side_effect
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                comparative_report = excel_generator.generate_comparative_report(document_ids)
        
        assert isinstance(comparative_report, ExcelReport)
        assert "comparative" in comparative_report.filename.lower()
        assert len(comparative_report.sheets) == 4  # Summary, risks, commitments, metrics

    def test_error_handling_in_integrated_workflow(self, conversational_engine, excel_generator):
        """Test error handling throughout the integrated workflow."""
        document_id = "doc123"
        session_id = "session303"
        
        # Test conversation error handling
        with patch.object(conversational_engine.qa_engine, 'answer_question') as mock_qa:
            mock_qa.side_effect = Exception("QA Engine Error")
            
            response = conversational_engine.answer_conversational_question(
                "What are the key points?", document_id, session_id
            )
            
            assert response.confidence == 0.0
            assert "trouble" in response.answer.lower()
        
        # Test Excel generation error handling
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.side_effect = Exception("Analysis extraction error")
            
            with pytest.raises(Exception):
                excel_generator.generate_document_report(document_id)

    def test_custom_excel_report_from_conversation_specification(self, conversational_engine, excel_generator):
        """Test generating custom Excel report based on conversation specifications."""
        document_id = "doc123"
        session_id = "session404"
        
        # Simulate conversation specifying custom report requirements
        specification_question = (
            "I need a custom Excel report that only includes high-severity risks "
            "and active commitments from the last quarter"
        )
        
        response = conversational_engine.answer_conversational_question(
            specification_question, document_id, session_id
        )
        
        # Extract specification from conversation (in real implementation, 
        # this would use NLP to parse requirements)
        custom_specification = {
            'document_ids': [document_id],
            'include_sections': ['risks', 'commitments'],
            'filters': {
                'risk_severity': ['High'],
                'commitment_status': ['Active'],
                'date_range': {
                    'start': '2024-01-01',
                    'end': '2024-03-31'
                }
            }
        }
        
        with patch.object(excel_generator, '_extract_document_analysis_data') as mock_extract:
            mock_extract.return_value = {
                'risks': [
                    {'risk_id': 'R001', 'severity': 'High'},
                    {'risk_id': 'R002', 'severity': 'Low'}  # Should be filtered out
                ],
                'commitments': [
                    {'commitment_id': 'C001', 'status': 'Active'},
                    {'commitment_id': 'C002', 'status': 'Completed'}  # Should be filtered out
                ]
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                custom_report = excel_generator.create_custom_report(custom_specification)
        
        assert isinstance(custom_report, ExcelReport)
        assert "custom" in custom_report.filename.lower()

    def test_follow_up_questions_after_excel_generation(self, conversational_engine, excel_generator):
        """Test handling follow-up questions after Excel report generation."""
        document_id = "doc123"
        session_id = "session505"
        
        # Initial Excel generation request
        initial_response = conversational_engine.answer_conversational_question(
            "Generate an Excel report with document analysis", document_id, session_id
        )
        
        # Follow-up questions about the report
        follow_up_questions = [
            "Can you explain the risk scoring methodology used in the Excel report?",
            "What additional sheets could be added to make the report more comprehensive?",
            "How can I customize the formatting of the generated Excel file?"
        ]
        
        for question in follow_up_questions:
            follow_up_response = conversational_engine.answer_conversational_question(
                question, document_id, session_id
            )
            
            assert isinstance(follow_up_response, ConversationalResponse)
            assert follow_up_response.answer
            assert len(follow_up_response.follow_up_suggestions) > 0
        
        # Verify conversation context includes all interactions
        context = conversational_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 4  # Initial + 3 follow-ups
        
        # Verify context summary reflects Excel-related discussion
        assert "excel" in context.context_summary.lower() or "report" in context.context_summary.lower()

    def test_performance_with_large_conversation_history(self, conversational_engine, excel_generator):
        """Test performance and memory management with large conversation history."""
        document_id = "doc123"
        session_id = "session606"
        
        # Generate large conversation history
        for i in range(60):  # More than the 50-turn limit
            question = f"Question number {i} about document analysis"
            conversational_engine.answer_conversational_question(question, document_id, session_id)
        
        # Verify history is properly limited
        context = conversational_engine.conversation_contexts[session_id]
        assert len(context.conversation_history) == 50
        
        # Verify Excel generation still works with large context
        with patch.object(excel_generator, '_extract_conversation_data') as mock_extract:
            mock_extract.return_value = {
                'session_summary': 'Long conversation session',
                'turns': [
                    {
                        'question': f'Question {i}',
                        'response': f'Response {i}',
                        'timestamp': datetime.now(),
                        'analysis_mode': 'casual'
                    } for i in range(50)  # Match the limited history
                ],
                'topics': ['analysis', 'document', 'questions']
            }
            
            with patch.object(excel_generator, '_create_excel_file') as mock_create:
                conversation_report = excel_generator.generate_conversation_report(session_id)
        
        assert isinstance(conversation_report, ExcelReport)
        
        # Verify Q&A history sheet handles large dataset
        qa_sheet = next(sheet for sheet in conversation_report.sheets if sheet.name == "Q&A History")
        assert len(qa_sheet.data) == 50