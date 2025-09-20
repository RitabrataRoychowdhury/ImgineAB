"""Integration tests for enhanced analysis components."""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.models.document import Document
from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
from src.services.template_engine import TemplateEngine
from src.storage.document_storage import DocumentStorage


class TestEnhancedAnalysisIntegration(unittest.TestCase):
    """Integration tests for enhanced analysis workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_storage = Mock(spec=DocumentStorage)
        self.api_key = "test_api_key"
        self.analyzer = EnhancedSummaryAnalyzer(self.mock_storage, self.api_key)
        
        # Create test document
        self.test_document = Document(
            id="integration_test_doc",
            title="Test Integration Contract",
            file_type="pdf",
            file_size=5000,
            upload_timestamp=datetime.now(),
            original_text="This is a test contract between Company A and Company B. Company A shall deliver software by December 31, 2024. The total liability is limited to $50,000. Monthly reports are required.",
            is_legal_document=True,
            legal_document_type="Service Agreement"
        )
    
    def test_template_engine_integration(self):
        """Test that TemplateEngine integrates properly with EnhancedSummaryAnalyzer."""
        # Test template recommendation
        template = self.analyzer.template_engine.recommend_template(self.test_document)
        
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "Contract Analysis")
        
        # Test template application
        template_result = self.analyzer.template_engine.apply_template(self.test_document, template)
        
        self.assertIn('prompts', template_result)
        self.assertIn('risk_assessment', template_result['prompts'])
        self.assertIn('commitment_extraction', template_result['prompts'])
    
    def test_data_model_serialization_roundtrip(self):
        """Test that all data models can be serialized and deserialized correctly."""
        from src.models.document import RiskAssessment, Commitment, DeliverableDate, ComprehensiveAnalysis
        
        # Create test objects
        risk = RiskAssessment(
            risk_id="test_risk",
            description="Test risk description",
            severity="High",
            category="Legal",
            affected_parties=["Party A", "Party B"],
            mitigation_suggestions=["Suggestion 1", "Suggestion 2"],
            source_text="Source text from document",
            confidence=0.85
        )
        
        commitment = Commitment(
            commitment_id="test_commitment",
            description="Test commitment description",
            obligated_party="Company A",
            beneficiary_party="Company B",
            deadline=datetime(2024, 12, 31),
            status="Active",
            source_text="Commitment source text",
            commitment_type="Deliverable"
        )
        
        deliverable = DeliverableDate(
            date=datetime(2024, 6, 15),
            description="Milestone delivery",
            responsible_party="Development Team",
            deliverable_type="Milestone",
            status="Pending",
            source_text="Milestone source text"
        )
        
        analysis = ComprehensiveAnalysis(
            document_id=self.test_document.id,
            analysis_id="test_analysis",
            document_overview="Test overview",
            key_findings=["Finding 1", "Finding 2"],
            critical_information=["Critical info 1"],
            recommended_actions=["Action 1", "Action 2"],
            executive_recommendation="Executive recommendation",
            key_legal_terms=["Term 1", "Term 2"],
            risks=[risk],
            commitments=[commitment],
            deliverable_dates=[deliverable],
            template_used="contract_analysis_v1",
            confidence_score=0.88
        )
        
        # Test serialization
        analysis_dict = analysis.to_dict()
        
        # Test deserialization
        reconstructed = ComprehensiveAnalysis.from_dict(analysis_dict)
        
        # Verify all data is preserved
        self.assertEqual(reconstructed.document_id, analysis.document_id)
        self.assertEqual(reconstructed.analysis_id, analysis.analysis_id)
        self.assertEqual(len(reconstructed.risks), 1)
        self.assertEqual(len(reconstructed.commitments), 1)
        self.assertEqual(len(reconstructed.deliverable_dates), 1)
        
        # Verify nested objects
        self.assertEqual(reconstructed.risks[0].risk_id, risk.risk_id)
        self.assertEqual(reconstructed.risks[0].severity, risk.severity)
        self.assertEqual(reconstructed.commitments[0].commitment_id, commitment.commitment_id)
        self.assertEqual(reconstructed.deliverable_dates[0].date, deliverable.date)
    
    def test_template_engine_predefined_templates_completeness(self):
        """Test that all predefined templates have required components."""
        templates = self.analyzer.template_engine.get_predefined_templates()
        
        required_templates = ["Contract Analysis", "NDA Analysis", "General Legal Analysis", "General Analysis"]
        
        template_names = [t.name for t in templates]
        
        for required in required_templates:
            self.assertIn(required, template_names, f"Missing required template: {required}")
        
        # Test contract analysis template specifically
        contract_template = next(t for t in templates if t.name == "Contract Analysis")
        
        required_sections = ["risk_assessment", "commitment_extraction", "deliverable_dates"]
        for section in required_sections:
            self.assertIn(section, contract_template.analysis_sections, 
                         f"Contract template missing section: {section}")
        
        # Verify custom prompts exist for key sections
        self.assertIn("risk_assessment", contract_template.custom_prompts)
        self.assertIn("commitment_extraction", contract_template.custom_prompts)
    
    def test_analyzer_component_initialization(self):
        """Test that EnhancedSummaryAnalyzer initializes all components correctly."""
        # Verify analyzer has all required components
        self.assertIsNotNone(self.analyzer.storage)
        self.assertIsNotNone(self.analyzer.api_key)
        self.assertIsNotNone(self.analyzer.template_engine)
        
        # Verify template engine is properly initialized
        self.assertIsInstance(self.analyzer.template_engine, TemplateEngine)
        
        # Verify predefined templates are loaded
        templates = self.analyzer.template_engine.get_predefined_templates()
        self.assertGreater(len(templates), 0)


if __name__ == '__main__':
    unittest.main()