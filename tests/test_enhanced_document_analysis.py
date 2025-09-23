"""
Comprehensive unit tests for enhanced document analysis components.
Tests document parsing, classification, risk analysis, and summary generation.
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

# Import the components to test
from src.services.enhanced_document_analyzer import (
    EnhancedDocumentAnalyzer, DocumentAnalysis, KeyInformation, 
    Party, ImportantDate, FinancialTerm, Obligation
)
from src.services.document_type_classifier import (
    DocumentTypeClassifier, DocumentType, DocumentTypeResult
)
from src.services.risk_analysis_engine import (
    RiskAnalysisEngine, RiskAnalysis, Risk, RiskCategory, RiskSeverity
)
from src.services.summary_generator import SummaryGenerator, DocumentSummary
from src.services.document_index_manager import (
    DocumentIndexManager, IndexEntry, SearchQuery, FilterCriteria
)

class TestEnhancedDocumentAnalyzer(unittest.TestCase):
    """Test cases for EnhancedDocumentAnalyzer"""
    
    def setUp(self):
        self.analyzer = EnhancedDocumentAnalyzer()
        self.sample_contract_text = """
        SERVICE AGREEMENT
        
        This Service Agreement ("Agreement") is entered into on January 15, 2024,
        between TechCorp Inc. ("Provider") and ClientCorp LLC ("Client").
        
        The Provider shall deliver software development services for a total fee of $50,000.
        Payment is due within 30 days of invoice. The agreement expires on December 31, 2024.
        
        Provider shall indemnify Client against any third-party claims.
        This agreement shall be governed by the laws of California.
        """
    
    def test_text_extraction_from_string(self):
        """Test text extraction from string content"""
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_contract_text)
            temp_path = f.name
        
        try:
            extracted_text = self.analyzer._extract_text_from_file(temp_path)
            self.assertIn("SERVICE AGREEMENT", extracted_text)
            self.assertIn("TechCorp Inc.", extracted_text)
            self.assertIn("$50,000", extracted_text)
        finally:
            os.unlink(temp_path)
    
    def test_party_extraction(self):
        """Test extraction of parties from document content"""
        parties = self.analyzer._extract_parties(self.sample_contract_text)
        
        self.assertGreater(len(parties), 0)
        party_names = [p.name for p in parties]
        self.assertTrue(any("TechCorp" in name for name in party_names))
        self.assertTrue(any("ClientCorp" in name for name in party_names))
    
    def test_financial_term_extraction(self):
        """Test extraction of financial terms"""
        financial_terms = self.analyzer._extract_financial_terms(self.sample_contract_text)
        
        self.assertGreater(len(financial_terms), 0)
        # Should find the $50,000 amount
        amounts = [term.amount for term in financial_terms if term.amount]
        self.assertTrue(any(amount == 50000.0 for amount in amounts))
    
    def test_date_extraction(self):
        """Test extraction of important dates"""
        key_dates = self.analyzer._extract_key_dates(self.sample_contract_text)
        
        self.assertGreater(len(key_dates), 0)
        # Should find January 15, 2024 and December 31, 2024
        date_strings = [date.date.strftime("%Y-%m-%d") for date in key_dates]
        self.assertTrue(any("2024-01-15" in date_str for date_str in date_strings))
        self.assertTrue(any("2024-12-31" in date_str for date_str in date_strings))
    
    def test_obligation_extraction(self):
        """Test extraction of obligations"""
        obligations = self.analyzer._extract_obligations(self.sample_contract_text)
        
        self.assertGreater(len(obligations), 0)
        # Should find delivery and indemnification obligations
        descriptions = [ob.description.lower() for ob in obligations]
        self.assertTrue(any("deliver" in desc for desc in descriptions))
        self.assertTrue(any("indemnify" in desc for desc in descriptions))
    
    def test_comprehensive_analysis(self):
        """Test complete document analysis workflow"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_contract_text)
            temp_path = f.name
        
        try:
            analysis = self.analyzer.analyze_document_comprehensive(temp_path, "test_doc_001")
            
            # Verify analysis structure
            self.assertIsInstance(analysis, DocumentAnalysis)
            self.assertEqual(analysis.document_id, "test_doc_001")
            self.assertIsInstance(analysis.key_information, KeyInformation)
            self.assertGreater(len(analysis.extracted_text), 0)
            self.assertIn('overall', analysis.confidence_scores)
            
        finally:
            os.unlink(temp_path)

class TestDocumentTypeClassifier(unittest.TestCase):
    """Test cases for DocumentTypeClassifier"""
    
    def setUp(self):
        self.classifier = DocumentTypeClassifier()
    
    def test_contract_classification(self):
        """Test classification of contract documents"""
        contract_text = """
        SERVICE AGREEMENT
        This agreement is between Provider and Client.
        The parties agree to the following terms and conditions.
        Performance obligations include delivery of services.
        Termination may occur upon breach of contract.
        """
        
        result = self.classifier.classify_document_type(contract_text, "Service Agreement")
        
        self.assertIsInstance(result, DocumentTypeResult)
        self.assertEqual(result.document_type, DocumentType.CONTRACT)
        self.assertGreater(result.confidence, 0.3)
        self.assertIn("contract", result.suggested_template)
    
    def test_mta_classification(self):
        """Test classification of Material Transfer Agreement"""
        mta_text = """
        MATERIAL TRANSFER AGREEMENT
        This MTA governs the transfer of research materials from Provider to Recipient.
        The materials shall be used for research purposes only.
        Publication rights are subject to Provider approval.
        Recipient shall not use materials for commercial purposes.
        """
        
        result = self.classifier.classify_document_type(mta_text, "Material Transfer Agreement")
        
        self.assertEqual(result.document_type, DocumentType.MTA)
        self.assertGreater(result.confidence, 0.5)
        self.assertIn("mta", result.suggested_template)
    
    def test_purchase_agreement_classification(self):
        """Test classification of purchase agreements"""
        purchase_text = """
        PURCHASE AGREEMENT
        Buyer agrees to purchase goods from Seller for $100,000.
        Delivery shall occur within 30 days of purchase order.
        Payment terms are net 30 days from delivery.
        Goods must meet specified quality standards and warranties.
        """
        
        result = self.classifier.classify_document_type(purchase_text, "Purchase Agreement")
        
        self.assertEqual(result.document_type, DocumentType.PURCHASE_AGREEMENT)
        self.assertGreater(result.confidence, 0.4)
    
    def test_nda_classification(self):
        """Test classification of Non-Disclosure Agreements"""
        nda_text = """
        NON-DISCLOSURE AGREEMENT
        This confidentiality agreement protects proprietary information.
        Disclosing Party will share confidential information with Receiving Party.
        Receiving Party shall not disclose confidential information to third parties.
        Trade secrets must be returned upon termination.
        """
        
        result = self.classifier.classify_document_type(nda_text, "NDA")
        
        self.assertEqual(result.document_type, DocumentType.NDA)
        self.assertGreater(result.confidence, 0.4)
    
    def test_unknown_document_classification(self):
        """Test classification of unknown document types"""
        unknown_text = """
        RANDOM DOCUMENT
        This is some random text that doesn't match any specific document type.
        It contains general information without legal or contractual language.
        No specific patterns that would indicate document type.
        """
        
        result = self.classifier.classify_document_type(unknown_text, "Random Document")
        
        # Should classify as unknown due to low confidence
        self.assertTrue(result.document_type == DocumentType.UNKNOWN or result.confidence < 0.3)
    
    def test_subtype_identification(self):
        """Test identification of document subtypes"""
        employment_contract = """
        EMPLOYMENT AGREEMENT
        This employment contract is between Company and Employee.
        Employee shall perform job duties as assigned.
        Salary and benefits are specified in Schedule A.
        """
        
        subtypes = self.classifier.identify_document_subtypes("contract", employment_contract)
        self.assertIn("employment_contract", subtypes)

class TestRiskAnalysisEngine(unittest.TestCase):
    """Test cases for RiskAnalysisEngine"""
    
    def setUp(self):
        self.risk_engine = RiskAnalysisEngine()
        self.sample_content = """
        The Provider shall pay liquidated damages of $10,000 for each day of delay.
        Failure to deliver may result in termination and legal action.
        Provider shall indemnify Client against all third-party claims.
        Confidential information must be protected to avoid reputational damage.
        Regulatory compliance is required under federal law.
        """
    
    def test_risk_identification_by_category(self):
        """Test identification of risks by category"""
        risks = self.risk_engine._identify_risks_by_category(self.sample_content, "contract")
        
        self.assertGreater(len(risks), 0)
        
        # Check that different risk categories are identified
        categories = {risk.category for risk in risks}
        self.assertIn(RiskCategory.FINANCIAL, categories)
        self.assertIn(RiskCategory.LEGAL, categories)
    
    def test_financial_risk_detection(self):
        """Test detection of financial risks"""
        financial_content = """
        Late payment penalty of $5,000 applies after 30 days.
        Total contract value is $500,000 with payment milestones.
        Cost overruns may result in additional charges.
        """
        
        risks = self.risk_engine._find_category_risks(
            financial_content, financial_content.lower(), 
            RiskCategory.FINANCIAL, 
            self.risk_engine.risk_patterns[RiskCategory.FINANCIAL], 
            1
        )
        
        self.assertGreater(len(risks), 0)
        self.assertTrue(all(risk.category == RiskCategory.FINANCIAL for risk in risks))
    
    def test_legal_risk_detection(self):
        """Test detection of legal risks"""
        legal_content = """
        Breach of contract may result in litigation.
        Indemnification clause requires Provider to defend Client.
        Intellectual property infringement claims are possible.
        Regulatory violations may result in penalties.
        """
        
        risks = self.risk_engine._find_category_risks(
            legal_content, legal_content.lower(),
            RiskCategory.LEGAL,
            self.risk_engine.risk_patterns[RiskCategory.LEGAL],
            1
        )
        
        self.assertGreater(len(risks), 0)
        self.assertTrue(all(risk.category == RiskCategory.LEGAL for risk in risks))
    
    def test_risk_severity_assessment(self):
        """Test risk severity assessment"""
        # Create mock risks
        high_risk = Risk(
            risk_id="RISK_001",
            description="Critical system failure risk with $1M exposure",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.MEDIUM,  # Will be updated
            probability=0.7,
            impact_description="Significant financial loss",
            affected_parties=["Company"],
            materialization_timeframe="Immediate",
            source_sections=["critical system failure $1,000,000"]
        )
        
        risks = [high_risk]
        assessed_risks = self.risk_engine._assess_risk_severity(risks, self.sample_content, None)
        
        # Should be assessed as high or critical severity
        self.assertIn(assessed_risks[0].severity, [RiskSeverity.HIGH, RiskSeverity.CRITICAL])
    
    def test_mitigation_strategy_generation(self):
        """Test generation of mitigation strategies"""
        # Create sample risks
        financial_risk = Risk(
            risk_id="RISK_001",
            description="Payment default risk",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.HIGH,
            probability=0.6,
            impact_description="Loss of revenue",
            affected_parties=["Company"],
            materialization_timeframe="Short-term",
            source_sections=["payment default"]
        )
        
        strategies = self.risk_engine._generate_mitigation_strategies([financial_risk])
        
        self.assertGreater(len(strategies), 0)
        # Should have financial mitigation strategies
        financial_strategies = [s for s in strategies if "financial" in s.description.lower() or "payment" in s.description.lower()]
        self.assertGreater(len(financial_strategies), 0)
    
    def test_comprehensive_risk_analysis(self):
        """Test complete risk analysis workflow"""
        # Mock key information
        mock_key_info = Mock()
        mock_key_info.key_dates = []
        mock_key_info.financial_terms = []
        
        analysis = self.risk_engine.analyze_document_risks(
            self.sample_content, "contract", mock_key_info
        )
        
        self.assertIsInstance(analysis, RiskAnalysis)
        self.assertGreaterEqual(analysis.overall_risk_score, 0.0)
        self.assertLessEqual(analysis.overall_risk_score, 1.0)
        self.assertIsInstance(analysis.risk_categories, dict)
        self.assertGreater(len(analysis.recommendations), 0)

class TestSummaryGenerator(unittest.TestCase):
    """Test cases for SummaryGenerator"""
    
    def setUp(self):
        self.generator = SummaryGenerator()
        
        # Create mock analysis objects
        self.mock_document_analysis = self._create_mock_document_analysis()
        self.mock_classification = self._create_mock_classification()
        self.mock_risk_analysis = self._create_mock_risk_analysis()
    
    def _create_mock_document_analysis(self):
        """Create mock document analysis"""
        mock_analysis = Mock()
        mock_analysis.document_id = "test_doc_001"
        mock_analysis.extracted_text = "Sample contract text with payment terms and delivery obligations"
        
        # Mock metadata
        mock_metadata = Mock()
        mock_metadata.title = "Test Service Agreement"
        mock_metadata.word_count = 500
        mock_metadata.page_count = 2
        mock_analysis.metadata = mock_metadata
        
        # Mock key information
        mock_key_info = Mock()
        mock_key_info.parties = [
            Party("TechCorp Inc.", "provider"),
            Party("ClientCorp LLC", "client")
        ]
        mock_key_info.financial_terms = [
            FinancialTerm(50000.0, "USD", "Service fee", "payment")
        ]
        mock_key_info.key_dates = [
            ImportantDate(datetime(2024, 12, 31), "Contract expiration", "expiration", "high")
        ]
        mock_key_info.obligations = [
            Obligation("Provider", "Deliver services", None, "delivery", "high")
        ]
        mock_key_info.definitions = {"Services": "Software development services"}
        mock_key_info.governing_clauses = ["Governed by California law"]
        mock_analysis.key_information = mock_key_info
        
        mock_analysis.confidence_scores = {"overall": 0.8}
        
        return mock_analysis
    
    def _create_mock_classification(self):
        """Create mock classification result"""
        mock_classification = Mock()
        mock_classification.document_type = DocumentType.CONTRACT
        mock_classification.confidence = 0.85
        return mock_classification
    
    def _create_mock_risk_analysis(self):
        """Create mock risk analysis"""
        mock_risk_analysis = Mock()
        mock_risk_analysis.overall_risk_score = 0.6
        mock_risk_analysis.confidence_level = 0.7
        mock_risk_analysis.recommendations = ["Review payment terms", "Monitor delivery deadlines"]
        
        # Mock risk categories
        financial_risk = Risk(
            risk_id="RISK_001",
            description="Payment default risk",
            category=RiskCategory.FINANCIAL,
            severity=RiskSeverity.HIGH,
            probability=0.6,
            impact_description="Revenue loss",
            affected_parties=["Company"],
            materialization_timeframe="Short-term",
            source_sections=["payment terms"]
        )
        
        mock_risk_analysis.risk_categories = {
            RiskCategory.FINANCIAL: [financial_risk]
        }
        
        return mock_risk_analysis
    
    def test_summary_generation(self):
        """Test complete summary generation"""
        summary = self.generator.generate_summary(
            self.mock_document_analysis,
            self.mock_classification,
            self.mock_risk_analysis
        )
        
        self.assertIsInstance(summary, DocumentSummary)
        self.assertEqual(summary.document_id, "test_doc_001")
        self.assertEqual(summary.document_type, "contract")
        self.assertIn("Service Agreement", summary.overview)
        self.assertGreater(len(summary.key_terms), 0)
        self.assertGreater(len(summary.important_dates), 0)
        self.assertGreater(len(summary.parties_involved), 0)
        self.assertGreater(len(summary.recommended_actions), 0)
    
    def test_overview_generation(self):
        """Test overview section generation"""
        overview = self.generator._generate_overview(
            self.mock_document_analysis, self.mock_classification
        )
        
        self.assertIn("Contract", overview)
        self.assertIn("85.0%", overview)  # Confidence percentage
        self.assertIn("500 words", overview)
        self.assertIn("TechCorp", overview)
    
    def test_key_terms_extraction(self):
        """Test key terms section generation"""
        key_terms = self.generator._generate_key_terms(self.mock_document_analysis)
        
        self.assertIsInstance(key_terms, dict)
        self.assertGreater(len(key_terms), 0)
        # Should include definitions and financial terms
        self.assertTrue(any("Services" in key for key in key_terms.keys()))
    
    def test_important_dates_formatting(self):
        """Test important dates section generation"""
        dates = self.generator._generate_important_dates(self.mock_document_analysis)
        
        self.assertIsInstance(dates, list)
        self.assertGreater(len(dates), 0)
        
        date_item = dates[0]
        self.assertIn("date", date_item)
        self.assertIn("description", date_item)
        self.assertIn("type", date_item)
        self.assertIn("criticality", date_item)
    
    def test_risks_section_generation(self):
        """Test risks section generation"""
        risks = self.generator._generate_risks_section(self.mock_risk_analysis)
        
        self.assertIsInstance(risks, list)
        self.assertGreater(len(risks), 0)
        
        risk_item = risks[0]
        self.assertIn("description", risk_item)
        self.assertIn("category", risk_item)
        self.assertIn("severity", risk_item)
        self.assertEqual(risk_item["category"], "financial")
    
    def test_recommended_actions_generation(self):
        """Test recommended actions generation"""
        actions = self.generator._generate_recommended_actions(
            self.mock_document_analysis, self.mock_risk_analysis
        )
        
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
        # Should include risk-based and general recommendations
        self.assertTrue(any("risk" in action.lower() for action in actions))

class TestDocumentIndexManager(unittest.TestCase):
    """Test cases for DocumentIndexManager"""
    
    def setUp(self):
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.index_manager = DocumentIndexManager(self.temp_db.name)
        
        # Create mock analysis objects
        self.mock_document_analysis = self._create_mock_document_analysis()
        self.mock_classification = self._create_mock_classification()
        self.mock_risk_analysis = self._create_mock_risk_analysis()
    
    def tearDown(self):
        """Clean up temporary database"""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def _create_mock_document_analysis(self):
        """Create mock document analysis for testing"""
        mock_analysis = Mock()
        mock_analysis.document_id = "test_doc_001"
        
        # Mock metadata
        mock_metadata = Mock()
        mock_metadata.title = "Test Contract"
        mock_metadata.word_count = 1000
        mock_metadata.page_count = 3
        mock_metadata.file_format = ".pdf"
        mock_metadata.language = "en"
        mock_analysis.metadata = mock_metadata
        
        # Mock key information
        mock_key_info = Mock()
        mock_key_info.parties = [Party("Company A", "provider"), Party("Company B", "client")]
        mock_key_info.financial_terms = [FinancialTerm(25000.0, "USD", "Service fee", "payment")]
        mock_key_info.key_dates = [
            ImportantDate(datetime(2024, 6, 30), "Contract expiration", "expiration", "high")
        ]
        mock_key_info.obligations = [Obligation("Provider", "Deliver services", None, "delivery", "high")]
        mock_analysis.key_information = mock_key_info
        
        mock_analysis.confidence_scores = {"overall": 0.85}
        
        return mock_analysis
    
    def _create_mock_classification(self):
        """Create mock classification result"""
        mock_classification = Mock()
        mock_classification.document_type = DocumentType.CONTRACT
        mock_classification.confidence = 0.9
        return mock_classification
    
    def _create_mock_risk_analysis(self):
        """Create mock risk analysis"""
        mock_risk_analysis = Mock()
        mock_risk_analysis.overall_risk_score = 0.4
        mock_risk_analysis.confidence_level = 0.8
        
        # Mock risk categories
        mock_risk_analysis.risk_categories = {
            RiskCategory.FINANCIAL: [
                Risk("RISK_001", "Payment risk", RiskCategory.FINANCIAL, RiskSeverity.MEDIUM, 
                     0.5, "Payment delays", ["Company A"], "Short-term", ["payment clause"])
            ]
        }
        
        return mock_risk_analysis
    
    def test_add_document_to_index(self):
        """Test adding document to index"""
        entry = self.index_manager.add_document_to_index(
            self.mock_document_analysis,
            self.mock_classification,
            self.mock_risk_analysis,
            "/path/to/test_contract.pdf"
        )
        
        self.assertIsInstance(entry, IndexEntry)
        self.assertEqual(entry.document_id, "test_doc_001")
        self.assertEqual(entry.title, "Test Contract")
        self.assertEqual(entry.document_type, "contract")
        self.assertIn("Company A", entry.parties)
        self.assertIn("Company B", entry.parties)
    
    def test_search_documents(self):
        """Test document search functionality"""
        # First add a document
        self.index_manager.add_document_to_index(
            self.mock_document_analysis,
            self.mock_classification,
            self.mock_risk_analysis,
            "/path/to/test_contract.pdf"
        )
        
        # Test text search
        query = SearchQuery(text_query="Test Contract")
        results = self.index_manager.search_documents(query)
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].document_id, "test_doc_001")
        
        # Test document type search
        query = SearchQuery(document_type="contract")
        results = self.index_manager.search_documents(query)
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].document_type, "contract")
    
    def test_upcoming_deadlines(self):
        """Test upcoming deadlines functionality"""
        # Add document with deadline
        self.index_manager.add_document_to_index(
            self.mock_document_analysis,
            self.mock_classification,
            self.mock_risk_analysis,
            "/path/to/test_contract.pdf"
        )
        
        # Get upcoming deadlines
        deadlines = self.index_manager.get_upcoming_deadlines(timedelta(days=365))
        
        # Should find the expiration deadline
        self.assertGreater(len(deadlines), 0)
        deadline = deadlines[0]
        self.assertEqual(deadline.document_id, "test_doc_001")
        self.assertEqual(deadline.deadline_type, "expiration")
    
    def test_portfolio_summary(self):
        """Test portfolio summary generation"""
        # Add document
        self.index_manager.add_document_to_index(
            self.mock_document_analysis,
            self.mock_classification,
            self.mock_risk_analysis,
            "/path/to/test_contract.pdf"
        )
        
        # Generate portfolio summary
        summary = self.index_manager.generate_portfolio_summary()
        
        self.assertEqual(summary.total_documents, 1)
        self.assertIn("contract", summary.document_type_breakdown)
        self.assertEqual(summary.document_type_breakdown["contract"], 1)
        self.assertGreater(len(summary.recommendations), 0)
    
    def test_document_relationships(self):
        """Test document relationship management"""
        # Add document
        self.index_manager.add_document_to_index(
            self.mock_document_analysis,
            self.mock_classification,
            self.mock_risk_analysis,
            "/path/to/test_contract.pdf"
        )
        
        # Add relationships
        relationships = [
            ("test_doc_002", "amendment", "Amendment to original contract"),
            ("test_doc_003", "related", "Related service agreement")
        ]
        
        success = self.index_manager.update_document_relationships("test_doc_001", relationships)
        self.assertTrue(success)
        
        # Retrieve relationships
        retrieved_relationships = self.index_manager.get_document_relationships("test_doc_001")
        self.assertEqual(len(retrieved_relationships), 2)
    
    def test_document_status_update(self):
        """Test document status updates"""
        # Add document
        self.index_manager.add_document_to_index(
            self.mock_document_analysis,
            self.mock_classification,
            self.mock_risk_analysis,
            "/path/to/test_contract.pdf"
        )
        
        # Update status
        success = self.index_manager.update_document_status("test_doc_001", "expired")
        self.assertTrue(success)
        
        # Verify status update
        query = SearchQuery(document_id="test_doc_001")
        results = self.index_manager.search_documents(query)
        if results:
            self.assertEqual(results[0].status, "expired")

class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for the complete document analysis workflow"""
    
    def setUp(self):
        self.analyzer = EnhancedDocumentAnalyzer()
        self.classifier = DocumentTypeClassifier()
        self.risk_engine = RiskAnalysisEngine()
        self.summary_generator = SummaryGenerator()
        
        # Use temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.index_manager = DocumentIndexManager(self.temp_db.name)
        
        self.sample_contract = """
        SOFTWARE DEVELOPMENT AGREEMENT
        
        This Agreement is entered into on March 1, 2024, between
        TechSolutions Inc. ("Developer") and BusinessCorp LLC ("Client").
        
        Developer shall provide custom software development services for a total fee of $75,000.
        Payment schedule: $25,000 upon signing, $25,000 at 50% completion, $25,000 upon delivery.
        
        Project must be completed by September 30, 2024.
        Developer warrants that the software will be free from defects for 90 days.
        
        Either party may terminate this agreement with 30 days written notice.
        Developer shall indemnify Client against any IP infringement claims.
        
        This agreement is governed by the laws of New York.
        """
    
    def tearDown(self):
        """Clean up temporary files"""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_complete_workflow(self):
        """Test the complete document analysis workflow"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.sample_contract)
            temp_path = f.name
        
        try:
            # Step 1: Document Analysis
            document_analysis = self.analyzer.analyze_document_comprehensive(temp_path, "integration_test_001")
            
            self.assertIsInstance(document_analysis, DocumentAnalysis)
            self.assertEqual(document_analysis.document_id, "integration_test_001")
            self.assertGreater(len(document_analysis.key_information.parties), 0)
            self.assertGreater(len(document_analysis.key_information.financial_terms), 0)
            
            # Step 2: Document Classification
            classification_result = self.classifier.classify_document_type(
                document_analysis.extracted_text, 
                document_analysis.metadata.title
            )
            
            self.assertIsInstance(classification_result, DocumentTypeResult)
            # Should classify as contract or service agreement
            self.assertIn(classification_result.document_type, [DocumentType.CONTRACT, DocumentType.SERVICE_AGREEMENT])
            
            # Step 3: Risk Analysis
            risk_analysis = self.risk_engine.analyze_document_risks(
                document_analysis.extracted_text,
                classification_result.document_type.value,
                document_analysis.key_information
            )
            
            self.assertIsInstance(risk_analysis, RiskAnalysis)
            self.assertGreaterEqual(risk_analysis.overall_risk_score, 0.0)
            self.assertGreater(len(risk_analysis.risk_categories), 0)
            
            # Step 4: Summary Generation
            summary = self.summary_generator.generate_summary(
                document_analysis, classification_result, risk_analysis
            )
            
            self.assertIsInstance(summary, DocumentSummary)
            self.assertIn("TechSolutions", summary.overview)
            self.assertIn("BusinessCorp", summary.overview)
            self.assertGreater(len(summary.key_terms), 0)
            self.assertGreater(len(summary.important_dates), 0)
            
            # Step 5: Index Management
            index_entry = self.index_manager.add_document_to_index(
                document_analysis, classification_result, risk_analysis, temp_path
            )
            
            self.assertIsInstance(index_entry, IndexEntry)
            self.assertEqual(index_entry.document_id, "integration_test_001")
            
            # Step 6: Search and Retrieval
            search_query = SearchQuery(text_query="TechSolutions")
            search_results = self.index_manager.search_documents(search_query)
            
            self.assertGreater(len(search_results), 0)
            self.assertEqual(search_results[0].document_id, "integration_test_001")
            
            # Step 7: Portfolio Analysis
            portfolio_summary = self.index_manager.generate_portfolio_summary()
            
            self.assertEqual(portfolio_summary.total_documents, 1)
            self.assertGreater(len(portfolio_summary.recommendations), 0)
            
        finally:
            os.unlink(temp_path)
    
    def test_error_handling(self):
        """Test error handling in the workflow"""
        # Test with invalid file path
        try:
            self.analyzer.analyze_document_comprehensive("/nonexistent/file.txt", "error_test")
            self.fail("Should have raised an exception for nonexistent file")
        except Exception as e:
            self.assertIsInstance(e, (FileNotFoundError, ValueError))
        
        # Test with empty content
        empty_classification = self.classifier.classify_document_type("", "")
        self.assertEqual(empty_classification.document_type, DocumentType.UNKNOWN)
        
        # Test risk analysis with minimal content
        minimal_risk_analysis = self.risk_engine.analyze_document_risks("minimal content", "unknown", Mock())
        self.assertIsInstance(minimal_risk_analysis, RiskAnalysis)
        self.assertGreaterEqual(minimal_risk_analysis.overall_risk_score, 0.0)

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)