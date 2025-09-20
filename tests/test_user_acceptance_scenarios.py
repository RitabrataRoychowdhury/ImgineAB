"""User acceptance tests for enhanced Q&A capabilities."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime

from src.models.document import Document
from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
from src.services.conversational_ai_engine import ConversationalAIEngine
from src.services.excel_report_generator import ExcelReportGenerator
from src.services.template_engine import TemplateEngine


class TestUserAcceptanceScenarios:
    """User acceptance tests covering real-world usage scenarios."""
    
    @pytest.fixture
    def legal_professional_document(self):
        """Document that a legal professional might upload."""
        return Document(
            id="legal_contract_001",
            title="Master Service Agreement - TechCorp & LegalFirm",
            file_type="pdf",
            file_size=25000,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="""
            MASTER SERVICE AGREEMENT
            
            This Master Service Agreement ("Agreement") is entered into as of January 1, 2024,
            between TechCorp Inc., a Delaware corporation ("Client"), and LegalFirm LLC,
            a New York limited liability company ("Service Provider").
            
            1. SCOPE OF SERVICES
            Service Provider shall provide legal consulting services including:
            - Contract review and analysis
            - Regulatory compliance advice
            - Intellectual property guidance
            - Risk assessment and mitigation strategies
            
            2. TERM AND TERMINATION
            This Agreement shall commence on January 1, 2024, and continue for a period of
            two (2) years, unless terminated earlier in accordance with this Agreement.
            Either party may terminate this Agreement with sixty (60) days written notice.
            
            3. COMPENSATION
            Client shall pay Service Provider a monthly retainer of $15,000, due on the
            first day of each month. Additional services beyond the retainer scope shall
            be billed at $500 per hour.
            
            4. CONFIDENTIALITY
            Both parties acknowledge that they may have access to confidential information.
            Each party agrees to maintain the confidentiality of such information for a
            period of five (5) years following termination of this Agreement.
            
            5. LIABILITY AND INDEMNIFICATION
            Service Provider's liability under this Agreement shall not exceed the total
            amount paid by Client in the twelve (12) months preceding the claim.
            Client agrees to indemnify Service Provider against claims arising from
            Client's use of the services.
            
            6. GOVERNING LAW
            This Agreement shall be governed by the laws of the State of New York.
            Any disputes shall be resolved through binding arbitration in New York City.
            """,
            is_legal_document=True,
            legal_document_type="Service Agreement"
        )
    
    @pytest.fixture
    def business_analyst_document(self):
        """Document that a business analyst might upload."""
        return Document(
            id="business_proposal_001",
            title="Software Development Proposal - Q1 2024",
            file_type="pdf",
            file_size=18000,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="""
            SOFTWARE DEVELOPMENT PROPOSAL
            Q1 2024 PROJECT INITIATIVE
            
            EXECUTIVE SUMMARY
            This proposal outlines the development of a customer relationship management
            (CRM) system to improve sales efficiency and customer satisfaction.
            
            PROJECT SCOPE
            - Custom CRM application development
            - Integration with existing systems
            - User training and documentation
            - 6-month maintenance and support
            
            TIMELINE AND MILESTONES
            Phase 1: Requirements Analysis (January 15 - February 15, 2024)
            Phase 2: System Design (February 16 - March 15, 2024)
            Phase 3: Development (March 16 - May 15, 2024)
            Phase 4: Testing and Deployment (May 16 - June 30, 2024)
            
            BUDGET BREAKDOWN
            Development Team: $120,000
            Infrastructure: $25,000
            Third-party Licenses: $15,000
            Training and Documentation: $10,000
            Total Project Cost: $170,000
            
            RISK FACTORS
            - Potential delays in third-party API integration
            - Resource availability during peak business periods
            - Scope creep from additional feature requests
            - Data migration complexity from legacy systems
            
            SUCCESS METRICS
            - 25% improvement in sales team efficiency
            - 40% reduction in customer response time
            - 95% user adoption rate within 3 months
            - ROI of 200% within 18 months
            """,
            is_legal_document=False,
            document_type="Business Proposal"
        )
    
    def test_legal_professional_workflow(self, legal_professional_document):
        """Test complete workflow for a legal professional user."""
        
        # Mock storage and API
        mock_storage = Mock()
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Mock API responses for legal document analysis
        def legal_api_mock(prompt, max_tokens=1000):
            if "risk" in prompt.lower():
                return """{
                    "risks": [
                        {
                            "description": "Liability cap may be insufficient for high-value claims",
                            "severity": "High",
                            "category": "Legal",
                            "affected_parties": ["Client"],
                            "mitigation_suggestions": ["Consider additional insurance coverage", "Negotiate higher liability cap"],
                            "source_text": "Service Provider's liability shall not exceed the total amount paid by Client in the twelve months",
                            "confidence": 0.9
                        },
                        {
                            "description": "Arbitration requirement may limit legal remedies",
                            "severity": "Medium",
                            "category": "Legal",
                            "affected_parties": ["Both parties"],
                            "mitigation_suggestions": ["Review arbitration procedures", "Consider carve-outs for certain disputes"],
                            "source_text": "Any disputes shall be resolved through binding arbitration",
                            "confidence": 0.8
                        }
                    ]
                }"""
            elif "commitment" in prompt.lower():
                return """{
                    "commitments": [
                        {
                            "description": "Pay monthly retainer of $15,000",
                            "obligated_party": "Client",
                            "beneficiary_party": "Service Provider",
                            "deadline": null,
                            "commitment_type": "Payment",
                            "status": "Active",
                            "source_text": "Client shall pay Service Provider a monthly retainer of $15,000"
                        },
                        {
                            "description": "Maintain confidentiality for 5 years",
                            "obligated_party": "Both parties",
                            "beneficiary_party": "Both parties",
                            "deadline": "2029-01-01",
                            "commitment_type": "Compliance",
                            "status": "Active",
                            "source_text": "maintain the confidentiality of such information for a period of five (5) years"
                        }
                    ]
                }"""
            else:
                return "This is a comprehensive master service agreement between TechCorp Inc. and LegalFirm LLC for legal consulting services."
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=legal_api_mock):
            
            # Step 1: Legal professional uploads document and gets enhanced summary
            analysis = analyzer.analyze_document_comprehensive(legal_professional_document)
            
            # Verify legal professional gets relevant analysis
            assert len(analysis.risks) == 2
            assert any("liability" in risk.description.lower() for risk in analysis.risks)
            assert any("arbitration" in risk.description.lower() for risk in analysis.risks)
            
            # Verify high-risk items are identified
            high_risks = [r for r in analysis.risks if r.severity == "High"]
            assert len(high_risks) >= 1
            
            # Verify legal commitments are extracted
            assert len(analysis.commitments) == 2
            payment_commitments = [c for c in analysis.commitments if c.commitment_type == "Payment"]
            assert len(payment_commitments) == 1
            assert "$15,000" in payment_commitments[0].description
            
            # Step 2: Legal professional asks specific questions
            qa_engine = Mock()
            contract_engine = Mock()
            
            contract_engine.analyze_contract_query.return_value = {
                'answer': 'The liability is capped at the total amount paid by Client in the twelve months preceding the claim, which could be up to $180,000 annually.',
                'confidence': 0.9,
                'sources': ['liability_clause']
            }
            
            conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
            
            response = conv_engine.answer_conversational_question(
                "What is the liability limitation in this agreement?",
                legal_professional_document.id,
                "legal_session_001"
            )
            
            assert "liability" in response.answer.lower()
            assert "$180,000" in response.answer
            assert response.analysis_mode == "legal"
            assert response.confidence > 0.8
            
            # Step 3: Legal professional generates detailed report
            with tempfile.TemporaryDirectory() as temp_dir:
                generator = ExcelReportGenerator(mock_storage, temp_dir)
                mock_storage.get_document.return_value = legal_professional_document
                
                with patch.object(generator, '_extract_document_analysis_data') as mock_extract:
                    mock_extract.return_value = {
                        'summary': analysis.__dict__,
                        'risks': [risk.__dict__ for risk in analysis.risks],
                        'commitments': [commitment.__dict__ for commitment in analysis.commitments],
                        'deliverable_dates': []
                    }
                    
                    report = generator.generate_document_report(
                        legal_professional_document.id, 
                        "comprehensive"
                    )
                    
                    # Verify report is generated successfully
                    assert report.filename.endswith('.xlsx')
                    assert len(report.sheets) >= 3  # Summary, Risks, Commitments
                    
                    # Verify legal-specific sheets are included
                    sheet_names = [sheet.name for sheet in report.sheets]
                    assert "Risks" in sheet_names
                    assert "Commitments" in sheet_names
    
    def test_business_analyst_workflow(self, business_analyst_document):
        """Test complete workflow for a business analyst user."""
        
        mock_storage = Mock()
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Mock API responses for business document analysis
        def business_api_mock(prompt, max_tokens=1000):
            if "risk" in prompt.lower():
                return """{
                    "risks": [
                        {
                            "description": "Potential delays in third-party API integration",
                            "severity": "High",
                            "category": "Operational",
                            "affected_parties": ["Development Team", "Client"],
                            "mitigation_suggestions": ["Early API testing", "Backup integration options"],
                            "source_text": "Potential delays in third-party API integration",
                            "confidence": 0.85
                        },
                        {
                            "description": "Scope creep from additional feature requests",
                            "severity": "Medium",
                            "category": "Operational",
                            "affected_parties": ["Project Team"],
                            "mitigation_suggestions": ["Clear change control process", "Regular stakeholder reviews"],
                            "source_text": "Scope creep from additional feature requests",
                            "confidence": 0.8
                        }
                    ]
                }"""
            elif "date" in prompt.lower():
                return """{
                    "deliverable_dates": [
                        {
                            "date": "2024-02-15",
                            "description": "Requirements Analysis completion",
                            "responsible_party": "Development Team",
                            "deliverable_type": "Milestone",
                            "status": "Pending",
                            "source_text": "Phase 1: Requirements Analysis (January 15 - February 15, 2024)"
                        },
                        {
                            "date": "2024-06-30",
                            "description": "Testing and Deployment completion",
                            "responsible_party": "Development Team",
                            "deliverable_type": "Milestone",
                            "status": "Pending",
                            "source_text": "Phase 4: Testing and Deployment (May 16 - June 30, 2024)"
                        }
                    ]
                }"""
            else:
                return "This is a software development proposal for a CRM system with a budget of $170,000 and timeline through Q2 2024."
        
        with patch.object(analyzer, '_call_gemini_api', side_effect=business_api_mock):
            
            # Step 1: Business analyst uploads proposal and gets analysis
            analysis = analyzer.analyze_document_comprehensive(business_analyst_document)
            
            # Verify business-relevant analysis
            assert len(analysis.risks) == 2
            assert any("API integration" in risk.description for risk in analysis.risks)
            assert any("scope creep" in risk.description.lower() for risk in analysis.risks)
            
            # Verify project timeline extraction
            assert len(analysis.deliverable_dates) == 2
            milestone_dates = [d for d in analysis.deliverable_dates if d.deliverable_type == "Milestone"]
            assert len(milestone_dates) == 2
            
            # Step 2: Business analyst asks about budget and timeline
            qa_engine = Mock()
            contract_engine = Mock()
            
            qa_engine.answer_question.return_value = {
                'answer': 'The total project cost is $170,000, broken down as: Development Team ($120,000), Infrastructure ($25,000), Third-party Licenses ($15,000), and Training ($10,000).',
                'confidence': 0.9,
                'sources': ['budget_section']
            }
            
            conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
            
            response = conv_engine.answer_conversational_question(
                "What is the total budget and how is it broken down?",
                business_analyst_document.id,
                "business_session_001"
            )
            
            assert "$170,000" in response.answer
            assert "Development Team" in response.answer
            assert response.confidence > 0.8
            
            # Step 3: Business analyst generates project tracking report
            with tempfile.TemporaryDirectory() as temp_dir:
                generator = ExcelReportGenerator(mock_storage, temp_dir)
                mock_storage.get_document.return_value = business_analyst_document
                
                with patch.object(generator, '_extract_document_analysis_data') as mock_extract:
                    mock_extract.return_value = {
                        'summary': analysis.__dict__,
                        'risks': [risk.__dict__ for risk in analysis.risks],
                        'commitments': [],
                        'deliverable_dates': [date.__dict__ for date in analysis.deliverable_dates]
                    }
                    
                    report = generator.generate_document_report(
                        business_analyst_document.id,
                        "comprehensive"
                    )
                    
                    # Verify business-focused report
                    assert report.filename.endswith('.xlsx')
                    sheet_names = [sheet.name for sheet in report.sheets]
                    assert "Important Dates" in sheet_names
                    assert "Risks" in sheet_names
    
    def test_casual_user_workflow(self, business_analyst_document):
        """Test workflow for a casual user with simple questions."""
        
        qa_engine = Mock()
        contract_engine = Mock()
        
        # Mock simple responses for casual questions
        qa_engine.answer_question.return_value = {
            'answer': 'This document is about developing a CRM system. The project will cost $170,000 and take about 6 months to complete.',
            'confidence': 0.8,
            'sources': ['document_summary']
        }
        
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Casual conversation flow
        casual_questions = [
            "Hi, what is this document about?",
            "How much will this project cost?",
            "When will it be finished?",
            "What are the main risks?",
            "Thanks for the help!"
        ]
        
        responses = []
        session_id = "casual_session_001"
        
        for question in casual_questions:
            response = conv_engine.answer_conversational_question(
                question,
                business_analyst_document.id,
                session_id
            )
            responses.append(response)
            
            # Verify casual tone and helpful responses
            assert response.answer is not None
            assert len(response.answer) > 0
            
            # First question should get document overview
            if "what is this document" in question.lower():
                assert "CRM" in response.answer or "customer" in response.answer.lower()
        
        # Verify conversation context is maintained
        assert len(conv_engine.conversation_contexts[session_id].conversation_history) == len(casual_questions)
    
    def test_template_customization_workflow(self, legal_professional_document):
        """Test workflow for users creating custom analysis templates."""
        
        mock_storage = Mock()
        template_engine = TemplateEngine(mock_storage)
        
        # Step 1: User creates custom template for contract analysis
        custom_template_spec = {
            'name': 'Custom Contract Review Template',
            'description': 'Specialized template for service agreements',
            'document_types': ['Service Agreement', 'Consulting Agreement'],
            'analysis_sections': ['party_analysis', 'payment_terms', 'termination_clauses', 'liability_review'],
            'custom_prompts': {
                'party_analysis': 'Identify all parties and their roles in detail',
                'payment_terms': 'Extract all payment-related terms and schedules',
                'termination_clauses': 'Analyze termination conditions and notice requirements',
                'liability_review': 'Review liability limitations and indemnification clauses'
            },
            'parameters': {
                'focus_area': 'risk_assessment',
                'detail_level': 'high'
            }
        }
        
        # Mock template creation
        mock_storage.save_analysis_template.return_value = "custom_template_001"
        
        custom_template = template_engine.create_custom_template(custom_template_spec)
        
        # Verify template creation
        assert custom_template.name == 'Custom Contract Review Template'
        assert len(custom_template.analysis_sections) == 4
        assert 'liability_review' in custom_template.analysis_sections
        
        # Step 2: User applies custom template to document
        mock_storage.get_analysis_template.return_value = custom_template
        
        template_result = template_engine.apply_template(legal_professional_document, custom_template)
        
        # Verify template application
        assert 'prompts' in template_result
        assert 'party_analysis' in template_result['prompts']
        assert 'liability_review' in template_result['prompts']
        
        # Step 3: User gets template-specific analysis
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        with patch.object(analyzer, '_call_gemini_api', return_value="Template-specific analysis result"):
            template_analysis = analyzer.apply_custom_template(legal_professional_document, custom_template)
            
            assert template_analysis['template_name'] == 'Custom Contract Review Template'
            assert 'results' in template_analysis
    
    def test_error_recovery_user_experience(self, legal_professional_document):
        """Test user experience when errors occur and system recovers gracefully."""
        
        mock_storage = Mock()
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        # Simulate API failure for enhanced analysis
        with patch.object(analyzer, '_call_gemini_api', side_effect=Exception("API temporarily unavailable")):
            
            # User should still get basic analysis
            analysis = analyzer.analyze_document_comprehensive(legal_professional_document)
            
            # Verify graceful degradation
            assert analysis.document_id == legal_professional_document.id
            assert analysis.confidence_score < 0.8  # Lower confidence due to failures
            
            # Basic sections should still be populated with fallback content
            assert analysis.document_overview is not None
            assert len(analysis.document_overview) > 0
        
        # Test Excel generation fallback
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ExcelReportGenerator(mock_storage, temp_dir)
            mock_storage.get_document.return_value = legal_professional_document
            
            # Simulate Excel generation failure
            with patch.object(generator, '_create_excel_file', side_effect=Exception("Excel library error")):
                with patch.object(generator, '_extract_document_analysis_data', return_value={}):
                    
                    # Should generate fallback report
                    report = generator.generate_document_report(legal_professional_document.id)
                    
                    # User gets alternative format
                    assert report.filename.endswith('.csv')
                    assert os.path.exists(report.file_path)
    
    def test_multi_document_comparison_workflow(self, legal_professional_document, business_analyst_document):
        """Test workflow for comparing multiple documents."""
        
        mock_storage = Mock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = ExcelReportGenerator(mock_storage, temp_dir)
            
            # Mock document retrieval
            def mock_get_document(doc_id):
                if doc_id == legal_professional_document.id:
                    return legal_professional_document
                elif doc_id == business_analyst_document.id:
                    return business_analyst_document
                return None
            
            mock_storage.get_document.side_effect = mock_get_document
            
            # Mock analysis data for both documents
            def mock_analysis_data(doc_id):
                if "legal" in doc_id:
                    return {
                        'risks': [{'severity': 'High', 'category': 'Legal'}],
                        'commitments': [{'commitment_type': 'Payment'}],
                        'deliverable_dates': []
                    }
                else:
                    return {
                        'risks': [{'severity': 'Medium', 'category': 'Operational'}],
                        'commitments': [],
                        'deliverable_dates': [{'deliverable_type': 'Milestone'}]
                    }
            
            with patch.object(generator, '_extract_document_analysis_data', side_effect=mock_analysis_data):
                
                # Generate comparative report
                document_ids = [legal_professional_document.id, business_analyst_document.id]
                report = generator.generate_comparative_report(document_ids)
                
                # Verify comparative analysis
                assert report.filename.startswith('comparative_report')
                assert '2docs' in report.filename
                
                sheet_names = [sheet.name for sheet in report.sheets]
                assert "Comparative Summary" in sheet_names
                assert "All Risks" in sheet_names
    
    def test_accessibility_and_usability(self, legal_professional_document):
        """Test accessibility and usability features."""
        
        # Test that error messages are user-friendly
        mock_storage = Mock()
        analyzer = EnhancedSummaryAnalyzer(mock_storage, "test_api_key")
        
        qa_engine = Mock()
        contract_engine = Mock()
        conv_engine = ConversationalAIEngine(qa_engine, contract_engine)
        
        # Test error message clarity
        qa_engine.answer_question.side_effect = Exception("Internal error")
        
        response = conv_engine._handle_casual_question(
            "What is this about?",
            legal_professional_document.id,
            "test_session"
        )
        
        # Error message should be user-friendly
        assert "try asking it differently" in response.answer.lower()
        assert len(response.follow_up_suggestions) > 0
        
        # Test that follow-up suggestions are helpful
        helpful_suggestions = [
            "Try asking about specific parts of the document",
            "Ask about key terms or concepts",
            "Request a summary of the document"
        ]
        
        for suggestion in response.follow_up_suggestions:
            assert any(keyword in suggestion.lower() 
                      for keyword in ['specific', 'terms', 'summary', 'document'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])