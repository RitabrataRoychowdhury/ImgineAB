"""Unit tests for enhanced analysis components."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from src.models.document import (
    Document, RiskAssessment, Commitment, DeliverableDate, 
    AnalysisTemplate, ComprehensiveAnalysis
)
from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
from src.services.template_engine import TemplateEngine
from src.storage.document_storage import DocumentStorage


class TestEnhancedDataModels(unittest.TestCase):
    """Test enhanced analysis data models."""
    
    def test_risk_assessment_model(self):
        """Test RiskAssessment model creation and serialization."""
        risk = RiskAssessment(
            risk_id="test_risk_1",
            description="High financial liability risk",
            severity="High",
            category="Financial",
            affected_parties=["Company A", "Company B"],
            mitigation_suggestions=["Add liability cap", "Require insurance"],
            source_text="The parties shall be liable for unlimited damages...",
            confidence=0.85
        )
        
        # Test to_dict
        risk_dict = risk.to_dict()
        self.assertEqual(risk_dict['risk_id'], "test_risk_1")
        self.assertEqual(risk_dict['severity'], "High")
        self.assertIn("Company A", json.loads(risk_dict['affected_parties']))
        
        # Test from_dict
        reconstructed = RiskAssessment.from_dict(risk_dict)
        self.assertEqual(reconstructed.risk_id, risk.risk_id)
        self.assertEqual(reconstructed.affected_parties, risk.affected_parties)
    
    def test_commitment_model(self):
        """Test Commitment model creation and serialization."""
        deadline = datetime(2024, 12, 31, 23, 59, 59)
        commitment = Commitment(
            commitment_id="test_commitment_1",
            description="Deliver software by year end",
            obligated_party="Developer Corp",
            beneficiary_party="Client Inc",
            deadline=deadline,
            status="Active",
            source_text="Developer shall deliver the software by December 31, 2024",
            commitment_type="Deliverable"
        )
        
        # Test to_dict
        commitment_dict = commitment.to_dict()
        self.assertEqual(commitment_dict['commitment_id'], "test_commitment_1")
        self.assertEqual(commitment_dict['deadline'], deadline.isoformat())
        
        # Test from_dict
        reconstructed = Commitment.from_dict(commitment_dict)
        self.assertEqual(reconstructed.deadline, deadline)
        self.assertEqual(reconstructed.commitment_type, "Deliverable")
    
    def test_deliverable_date_model(self):
        """Test DeliverableDate model creation and serialization."""
        date = datetime(2024, 6, 15, 12, 0, 0)
        deliverable = DeliverableDate(
            date=date,
            description="First milestone delivery",
            responsible_party="Development Team",
            deliverable_type="Milestone",
            status="Pending",
            source_text="First milestone due June 15, 2024"
        )
        
        # Test to_dict
        deliverable_dict = deliverable.to_dict()
        self.assertEqual(deliverable_dict['date'], date.isoformat())
        self.assertEqual(deliverable_dict['deliverable_type'], "Milestone")
        
        # Test from_dict
        reconstructed = DeliverableDate.from_dict(deliverable_dict)
        self.assertEqual(reconstructed.date, date)
        self.assertEqual(reconstructed.responsible_party, "Development Team")
    
    def test_analysis_template_model(self):
        """Test AnalysisTemplate model creation and serialization."""
        template = AnalysisTemplate(
            template_id="test_template_1",
            name="Test Contract Analysis",
            description="Template for testing",
            document_types=["contract", "agreement"],
            analysis_sections=["overview", "risks"],
            custom_prompts={"risks": "Analyze risks carefully"},
            parameters={"detail_level": "high"},
            created_by="test_user",
            version="1.0",
            is_active=True
        )
        
        # Test to_dict
        template_dict = template.to_dict()
        self.assertEqual(template_dict['template_id'], "test_template_1")
        self.assertIn("contract", json.loads(template_dict['document_types']))
        
        # Test from_dict
        reconstructed = AnalysisTemplate.from_dict(template_dict)
        self.assertEqual(reconstructed.name, template.name)
        self.assertEqual(reconstructed.custom_prompts, template.custom_prompts)
    
    def test_comprehensive_analysis_model(self):
        """Test ComprehensiveAnalysis model with nested objects."""
        risk = RiskAssessment(
            risk_id="risk_1", description="Test risk", severity="High",
            category="Legal", affected_parties=["Party A"], 
            mitigation_suggestions=["Mitigate"], source_text="Source", confidence=0.8
        )
        
        commitment = Commitment(
            commitment_id="commit_1", description="Test commitment",
            obligated_party="Party A", beneficiary_party="Party B",
            deadline=None, status="Active", source_text="Source",
            commitment_type="Action"
        )
        
        analysis = ComprehensiveAnalysis(
            document_id="doc_1",
            analysis_id="analysis_1",
            document_overview="Test overview",
            key_findings=["Finding 1", "Finding 2"],
            critical_information=["Critical 1"],
            recommended_actions=["Action 1"],
            executive_recommendation="Proceed with caution",
            key_legal_terms=["Term 1"],
            risks=[risk],
            commitments=[commitment],
            deliverable_dates=[],
            template_used="template_1",
            confidence_score=0.85
        )
        
        # Test to_dict
        analysis_dict = analysis.to_dict()
        self.assertEqual(analysis_dict['document_id'], "doc_1")
        self.assertIn("Finding 1", json.loads(analysis_dict['key_findings']))
        
        # Test from_dict
        reconstructed = ComprehensiveAnalysis.from_dict(analysis_dict)
        self.assertEqual(len(reconstructed.risks), 1)
        self.assertEqual(reconstructed.risks[0].risk_id, "risk_1")
        self.assertEqual(len(reconstructed.commitments), 1)


class TestTemplateEngine(unittest.TestCase):
    """Test TemplateEngine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_storage = Mock(spec=DocumentStorage)
        self.template_engine = TemplateEngine(self.mock_storage)
    
    def test_get_predefined_templates(self):
        """Test getting predefined templates."""
        templates = self.template_engine.get_predefined_templates()
        
        self.assertGreater(len(templates), 0)
        
        # Check that contract analysis template exists
        contract_template = next((t for t in templates if t.name == "Contract Analysis"), None)
        self.assertIsNotNone(contract_template)
        self.assertIn("risk_assessment", contract_template.analysis_sections)
        self.assertIn("commitment_extraction", contract_template.analysis_sections)
    
    def test_create_custom_template(self):
        """Test creating a custom template."""
        template_spec = {
            'name': 'Custom Policy Analysis',
            'description': 'Custom template for policy documents',
            'document_types': ['policy', 'procedure'],
            'analysis_sections': ['overview', 'requirements'],
            'custom_prompts': {'overview': 'Analyze policy overview'},
            'parameters': {'focus': 'compliance'},
            'created_by': 'test_user'
        }
        
        template = self.template_engine.create_custom_template(template_spec)
        
        self.assertEqual(template.name, 'Custom Policy Analysis')
        self.assertIn('policy', template.document_types)
        self.assertEqual(template.custom_prompts['overview'], 'Analyze policy overview')
        self.assertTrue(template.is_active)
    
    def test_recommend_template_for_contract(self):
        """Test template recommendation for contract documents."""
        document = Document(
            id="test_doc",
            title="Service Agreement",
            file_type="pdf",
            file_size=1000,
            upload_timestamp=datetime.now(),
            is_legal_document=True,
            legal_document_type="Service Agreement"
        )
        
        recommended = self.template_engine.recommend_template(document)
        
        self.assertIsNotNone(recommended)
        self.assertEqual(recommended.name, "Contract Analysis")
    
    def test_recommend_template_for_nda(self):
        """Test template recommendation for NDA documents."""
        document = Document(
            id="test_doc",
            title="Non-Disclosure Agreement",
            file_type="pdf",
            file_size=1000,
            upload_timestamp=datetime.now(),
            is_legal_document=True,
            legal_document_type="NDA"
        )
        
        recommended = self.template_engine.recommend_template(document)
        
        self.assertIsNotNone(recommended)
        self.assertEqual(recommended.name, "NDA Analysis")
    
    def test_apply_template(self):
        """Test applying a template to generate prompts."""
        document = Document(
            id="test_doc",
            title="Test Contract",
            file_type="pdf",
            file_size=1000,
            upload_timestamp=datetime.now(),
            document_type="contract"
        )
        
        templates = self.template_engine.get_predefined_templates()
        contract_template = next(t for t in templates if t.name == "Contract Analysis")
        
        result = self.template_engine.apply_template(document, contract_template)
        
        self.assertIn('prompts', result)
        self.assertIn('template_id', result)
        self.assertEqual(result['template_name'], "Contract Analysis")
        self.assertIn('risk_assessment', result['prompts'])


class TestEnhancedSummaryAnalyzer(unittest.TestCase):
    """Test EnhancedSummaryAnalyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_storage = Mock(spec=DocumentStorage)
        self.api_key = "test_api_key"
        self.analyzer = EnhancedSummaryAnalyzer(self.mock_storage, self.api_key)
        
        # Create test document
        self.test_document = Document(
            id="test_doc_1",
            title="Test Service Agreement",
            file_type="pdf",
            file_size=5000,
            upload_timestamp=datetime.now(),
            original_text="This service agreement between Company A and Company B requires delivery of software by December 31, 2024. The liability shall not exceed $100,000. Company A must provide monthly reports.",
            is_legal_document=True,
            legal_document_type="Service Agreement"
        )
    
    @patch('requests.post')
    def test_identify_risks(self, mock_post):
        """Test risk identification functionality."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "risks": [{
                                "description": "Limited liability cap may not cover all damages",
                                "severity": "Medium",
                                "category": "Financial",
                                "affected_parties": ["Company A", "Company B"],
                                "mitigation_suggestions": ["Increase liability cap", "Add insurance requirement"],
                                "source_text": "The liability shall not exceed $100,000",
                                "confidence": 0.8
                            }]
                        })
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        risks = self.analyzer.identify_risks(self.test_document)
        
        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0].severity, "Medium")
        self.assertEqual(risks[0].category, "Financial")
        self.assertIn("Company A", risks[0].affected_parties)
    
    @patch('requests.post')
    def test_extract_commitments(self, mock_post):
        """Test commitment extraction functionality."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "commitments": [{
                                "description": "Deliver software by December 31, 2024",
                                "obligated_party": "Company A",
                                "beneficiary_party": "Company B",
                                "deadline": "2024-12-31",
                                "commitment_type": "Deliverable",
                                "status": "Active",
                                "source_text": "requires delivery of software by December 31, 2024"
                            }]
                        })
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        commitments = self.analyzer.extract_commitments(self.test_document)
        
        self.assertEqual(len(commitments), 1)
        self.assertEqual(commitments[0].commitment_type, "Deliverable")
        self.assertEqual(commitments[0].obligated_party, "Company A")
        self.assertIsNotNone(commitments[0].deadline)
    
    @patch('requests.post')
    def test_find_deliverable_dates(self, mock_post):
        """Test deliverable date extraction functionality."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "deliverable_dates": [{
                                "date": "2024-12-31",
                                "description": "Software delivery deadline",
                                "responsible_party": "Company A",
                                "deliverable_type": "Delivery",
                                "status": "Pending",
                                "source_text": "delivery of software by December 31, 2024"
                            }]
                        })
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        dates = self.analyzer.find_deliverable_dates(self.test_document)
        
        self.assertEqual(len(dates), 1)
        self.assertEqual(dates[0].deliverable_type, "Delivery")
        self.assertEqual(dates[0].responsible_party, "Company A")
        self.assertEqual(dates[0].date.year, 2024)
        self.assertEqual(dates[0].date.month, 12)
        self.assertEqual(dates[0].date.day, 31)
    
    @patch('src.services.enhanced_summary_analyzer.EnhancedSummaryAnalyzer.identify_risks')
    @patch('src.services.enhanced_summary_analyzer.EnhancedSummaryAnalyzer.extract_commitments')
    @patch('src.services.enhanced_summary_analyzer.EnhancedSummaryAnalyzer.find_deliverable_dates')
    @patch('requests.post')
    def test_analyze_document_comprehensive(self, mock_post, mock_dates, mock_commitments, mock_risks):
        """Test comprehensive document analysis."""
        # Mock component methods
        mock_risks.return_value = [
            RiskAssessment("risk_1", "Test risk", "High", "Legal", [], [], "source", 0.8)
        ]
        mock_commitments.return_value = [
            Commitment("commit_1", "Test commitment", "Party A", "Party B", None, "Active", "source", "Action")
        ]
        mock_dates.return_value = [
            DeliverableDate(datetime(2024, 12, 31), "Test date", "Party A", "Delivery", "Pending", "source")
        ]
        
        # Mock API responses for text generation
        mock_response = Mock()
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": "Generated analysis text"
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        analysis = self.analyzer.analyze_document_comprehensive(self.test_document)
        
        self.assertIsInstance(analysis, ComprehensiveAnalysis)
        self.assertEqual(analysis.document_id, "test_doc_1")
        self.assertEqual(len(analysis.risks), 1)
        self.assertEqual(len(analysis.commitments), 1)
        self.assertEqual(len(analysis.deliverable_dates), 1)
        self.assertGreater(analysis.confidence_score, 0.0)
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        risks = [RiskAssessment("r1", "desc", "High", "Legal", [], [], "source", 0.8)]
        commitments = [Commitment("c1", "desc", "A", "B", None, "Active", "source", "Action")]
        dates = [DeliverableDate(datetime.now(), "desc", "A", "Delivery", "Pending", "source")]
        
        score = self.analyzer._calculate_confidence_score(
            self.test_document, risks, commitments, dates
        )
        
        self.assertGreater(score, 0.7)  # Should be higher than base score
        self.assertLessEqual(score, 0.95)  # Should not exceed cap
    
    def test_summarize_risks(self):
        """Test risk summarization."""
        risks = [
            RiskAssessment("r1", "High risk", "High", "Legal", [], [], "source", 0.8),
            RiskAssessment("r2", "Medium risk", "Medium", "Financial", [], [], "source", 0.7),
            RiskAssessment("r3", "Low risk", "Low", "Operational", [], [], "source", 0.6)
        ]
        
        summary = self.analyzer._summarize_risks(risks)
        
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['by_severity']['High'], 1)
        self.assertEqual(summary['by_severity']['Medium'], 1)
        self.assertEqual(summary['by_severity']['Low'], 1)
        self.assertEqual(len(summary['top_risks']), 3)
        self.assertEqual(summary['top_risks'][0]['severity'], 'High')  # Should be sorted by severity


if __name__ == '__main__':
    unittest.main()