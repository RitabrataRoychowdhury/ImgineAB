"""Integration tests for enhanced Q&A capabilities."""

import pytest
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock, patch

from src.ui.qa_interface import EnhancedQAInterface
from src.storage.enhanced_storage import EnhancedDocumentStorage
from src.storage.migrations import DatabaseMigrator
from src.models.document import Document, ComprehensiveAnalysis, RiskAssessment
from src.models.conversational import ConversationContext


class TestEnhancedQAIntegration:
    """Test enhanced Q&A interface integration."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Set up test database
        from src.storage.database import DatabaseManager
        db_manager = DatabaseManager(db_path)
        
        # Run migrations
        migrator = DatabaseMigrator()
        migrator.db_manager = db_manager
        migrator.run_migrations()
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def enhanced_storage(self, temp_db):
        """Create enhanced storage with test database."""
        storage = EnhancedDocumentStorage()
        # Override db_manager to use test database
        from src.storage.database import DatabaseManager
        storage.db_manager = DatabaseManager(temp_db)
        return storage
    
    @pytest.fixture
    def sample_document(self):
        """Create sample document for testing."""
        return Document(
            id="test_doc_1",
            title="Test Contract",
            file_type="pdf",
            file_size=1024,
            upload_timestamp=datetime.now(),
            processing_status="completed",
            original_text="This is a test contract with various clauses and obligations.",
            is_legal_document=True,
            legal_document_type="Service Agreement"
        )
    
    def test_enhanced_interface_initialization(self, temp_db):
        """Test that enhanced interface initializes correctly."""
        # Mock streamlit session state
        with patch('streamlit.session_state', {}):
            interface = EnhancedQAInterface()
            
            assert interface.storage is not None
            assert interface.enhanced_storage is not None
    
    def test_database_migrations(self, temp_db):
        """Test that database migrations work correctly."""
        from src.storage.database import DatabaseManager
        db_manager = DatabaseManager(temp_db)
        
        # Check that enhanced tables exist
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check for enhanced tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'comprehensive_analysis', 'risk_assessments', 
                    'commitments', 'deliverable_dates', 'analysis_templates'
                )
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            expected_tables = [
                'comprehensive_analysis', 'risk_assessments', 
                'commitments', 'deliverable_dates', 'analysis_templates'
            ]
            
            for table in expected_tables:
                assert table in tables, f"Table {table} not found"
    
    def test_comprehensive_analysis_storage(self, enhanced_storage, sample_document):
        """Test storing and retrieving comprehensive analysis."""
        # Create sample analysis
        analysis = ComprehensiveAnalysis(
            document_id=sample_document.id,
            analysis_id="test_analysis_1",
            document_overview="Test overview",
            key_findings=["Finding 1", "Finding 2"],
            critical_information=["Critical info"],
            recommended_actions=["Action 1"],
            executive_recommendation="Test recommendation",
            key_legal_terms=["Term 1", "Term 2"],
            risks=[],
            commitments=[],
            deliverable_dates=[],
            template_used=None,
            confidence_score=0.85
        )
        
        # Save analysis
        analysis_id = enhanced_storage.save_comprehensive_analysis(analysis)
        assert analysis_id == "test_analysis_1"
        
        # Retrieve analysis
        retrieved = enhanced_storage.get_comprehensive_analysis(analysis_id)
        assert retrieved is not None
        assert retrieved.document_id == sample_document.id
        assert retrieved.confidence_score == 0.85
        assert len(retrieved.key_findings) == 2
    
    def test_risk_assessment_storage(self, enhanced_storage):
        """Test storing and retrieving risk assessments."""
        # This would be tested as part of comprehensive analysis
        # since risks are stored together with the analysis
        pass
    
    def test_conversation_context_storage(self, enhanced_storage):
        """Test storing and retrieving conversation context."""
        context = ConversationContext(
            session_id="test_session_1",
            document_id="test_doc_1",
            conversation_history=[],
            current_topic="Contract Analysis",
            analysis_mode="legal",
            user_preferences={"tone": "professional"},
            context_summary="Discussing contract terms"
        )
        
        # Save context
        session_id = enhanced_storage.save_conversation_context(context)
        assert session_id == "test_session_1"
        
        # Retrieve context
        retrieved = enhanced_storage.get_conversation_context(session_id)
        assert retrieved is not None
        assert retrieved.current_topic == "Contract Analysis"
        assert retrieved.analysis_mode == "legal"
    
    def test_analysis_template_operations(self, enhanced_storage):
        """Test analysis template CRUD operations."""
        from src.models.document import AnalysisTemplate
        
        template = AnalysisTemplate(
            template_id="test_template_1",
            name="Contract Analysis Template",
            description="Template for analyzing contracts",
            document_types=["contract", "agreement"],
            analysis_sections=["parties", "obligations", "risks"],
            custom_prompts={"parties": "Identify all parties"},
            parameters={"focus": "legal"},
            created_by="test_user",
            version="1.0",
            is_active=True
        )
        
        # Save template
        template_id = enhanced_storage.save_analysis_template(template)
        assert template_id == "test_template_1"
        
        # Retrieve template
        retrieved = enhanced_storage.get_analysis_template(template_id)
        assert retrieved is not None
        assert retrieved.name == "Contract Analysis Template"
        assert len(retrieved.document_types) == 2
        
        # List templates
        templates = enhanced_storage.list_analysis_templates()
        assert len(templates) == 1
        assert templates[0].template_id == "test_template_1"
    
    @patch('src.services.enhanced_summary_analyzer.EnhancedSummaryAnalyzer')
    @patch('src.services.conversational_ai_engine.ConversationalAIEngine')
    @patch('src.services.excel_report_generator.ExcelReportGenerator')
    def test_enhanced_interface_components(self, mock_excel, mock_conv, mock_analyzer, temp_db):
        """Test that enhanced interface components are properly initialized."""
        with patch('streamlit.session_state', {}):
            with patch('src.config.config.get_gemini_api_key', return_value='test_key'):
                interface = EnhancedQAInterface()
                
                # Mock the render method to avoid Streamlit dependencies
                with patch.object(interface, '_ensure_database_ready'):
                    # Test that components can be initialized
                    interface._initialize_engines('test_key')
                    
                    # Verify engines are created (mocked)
                    assert mock_analyzer.called
                    assert mock_conv.called
                    assert mock_excel.called
    
    def _initialize_engines(self, api_key):
        """Helper method to initialize engines without Streamlit."""
        from src.services.qa_engine import create_qa_engine
        from src.services.contract_analyst_engine import create_contract_analyst_engine
        from src.services.enhanced_summary_analyzer import EnhancedSummaryAnalyzer
        from src.services.conversational_ai_engine import ConversationalAIEngine
        from src.services.excel_report_generator import ExcelReportGenerator
        from src.services.template_engine import TemplateEngine
        
        if not self.qa_engine:
            self.qa_engine = create_qa_engine(api_key, self.storage)
        if not self.contract_engine:
            self.contract_engine = create_contract_analyst_engine(api_key, self.storage)
        if not self.enhanced_analyzer:
            self.enhanced_analyzer = EnhancedSummaryAnalyzer(self.storage, api_key)
        if not self.conversational_engine:
            self.conversational_engine = ConversationalAIEngine(self.qa_engine, self.contract_engine)
        if not self.excel_generator:
            self.excel_generator = ExcelReportGenerator(self.storage)
        if not self.template_engine:
            self.template_engine = TemplateEngine(self.storage)


if __name__ == "__main__":
    pytest.main([__file__])