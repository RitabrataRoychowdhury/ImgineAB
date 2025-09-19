"""Unit tests for the Contract Analyst Engine."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.contract_analyst_engine import (
    ContractAnalystEngine, 
    ContractAnalysisResponse,
    create_contract_analyst_engine
)
from src.models.document import Document
from src.storage.document_storage import DocumentStorage


@pytest.fixture
def mock_storage():
    """Create a mock storage instance."""
    return Mock(spec=DocumentStorage)


@pytest.fixture
def engine(mock_storage):
    """Create a ContractAnalystEngine instance for testing."""
    return ContractAnalystEngine(mock_storage, "test-api-key")


@pytest.fixture
def sample_mta_document():
    """Create a sample MTA document for testing."""
    return Document(
        id="test-mta-1",
        title="Material Transfer Agreement - Research Collaboration",
        file_type="pdf",
        file_size=50000,
        upload_timestamp=datetime.now(),
        processing_status="completed",
        original_text="""
        MATERIAL TRANSFER AGREEMENT
        
        This Material Transfer Agreement ("Agreement") is entered into between Provider and Recipient
        for the transfer of research materials. The Provider owns all intellectual property rights
        in the Original Material. The Recipient may use the Material solely for research purposes
        and may not distribute to third parties without written consent.
        
        INTELLECTUAL PROPERTY:
        The Provider retains ownership of the Original Material. Any derivatives or modifications
        created by the Recipient shall be owned by the Recipient, but the Provider retains rights
        to the Original Material. The Recipient agrees to report any inventions or discoveries
        to the Provider within 60 days.
        
        LIABILITY:
        The Provider makes no warranties and shall not be liable for any damages arising from
        the use of the Material. The Recipient assumes all risks and liability.
        
        TERMINATION:
        This Agreement may be terminated by either party with 30 days written notice.
        Upon termination, the Recipient shall return or destroy all Material.
        """,
        document_type="Legal Document",
        summary="Material Transfer Agreement for research collaboration"
    )


@pytest.fixture
def sample_regular_document():
    """Create a sample non-legal document for testing."""
    return Document(
        id="test-doc-1",
        title="Research Paper on Climate Change",
        file_type="pdf",
        file_size=30000,
        upload_timestamp=datetime.now(),
        processing_status="completed",
        original_text="""
        Climate Change Research Paper
        
        This paper discusses the effects of climate change on global ecosystems.
        The research methodology involved collecting data from various weather stations
        and analyzing temperature trends over the past century.
        
        Results show a significant increase in global temperatures, with particular
        impact on polar ice caps and sea level rise.
        """,
        document_type="Research Paper"
    )


class TestContractAnalystEngine:
    """Test cases for ContractAnalystEngine class."""


class TestLegalDocumentDetection:
    """Test legal document detection functionality."""
    
    def test_detect_mta_document(self, engine, sample_mta_document):
        """Test detection of MTA documents."""
        is_legal, doc_type, confidence = engine.detect_legal_document(sample_mta_document)
        
        assert is_legal is True
        assert doc_type == "MTA"
        assert confidence > 0.5
    
    def test_detect_regular_document(self, engine, sample_regular_document):
        """Test that regular documents are not classified as legal."""
        is_legal, doc_type, confidence = engine.detect_legal_document(sample_regular_document)
        
        assert is_legal is False
        assert doc_type is None
        assert confidence < 0.3
    
    def test_detect_nda_document(self, engine):
        """Test detection of NDA documents."""
        nda_doc = Document(
            id="test-nda-1",
            title="Non-Disclosure Agreement",
            file_type="pdf",
            file_size=25000,
            upload_timestamp=datetime.now(),
            original_text="""
            NON-DISCLOSURE AGREEMENT
            
            This Non-Disclosure Agreement is between the Disclosing Party and Receiving Party.
            The Receiving Party agrees to maintain confidentiality of all proprietary information
            and trade secrets disclosed by the Disclosing Party. Confidential information
            includes technical data, business plans, and any proprietary information.
            """,
            processing_status="completed"
        )
        
        is_legal, doc_type, confidence = engine.detect_legal_document(nda_doc)
        
        assert is_legal is True
        assert doc_type == "NDA"
        assert confidence > 0.5
    
    def test_detect_general_legal_document(self, engine):
        """Test detection of general legal documents."""
        legal_doc = Document(
            id="test-legal-1",
            title="Service Agreement",
            file_type="pdf",
            file_size=40000,
            upload_timestamp=datetime.now(),
            original_text="""
            SERVICE AGREEMENT
            
            This Agreement governs the terms and conditions between the parties.
            The Provider agrees to deliver services subject to the terms herein.
            Liability is limited as specified in this contract. Either party may
            terminate this agreement with proper notice. Governing law shall apply.
            """,
            processing_status="completed"
        )
        
        is_legal, doc_type, confidence = engine.detect_legal_document(legal_doc)
        
        assert is_legal is True
        assert doc_type == "Legal Contract"
        assert confidence > 0.3
    
    def test_detect_document_without_text(self, engine):
        """Test detection with document that has no text."""
        empty_doc = Document(
            id="test-empty-1",
            title="Empty Document",
            file_type="pdf",
            file_size=1000,
            upload_timestamp=datetime.now(),
            original_text=None,
            processing_status="pending"
        )
        
        is_legal, doc_type, confidence = engine.detect_legal_document(empty_doc)
        
        assert is_legal is False
        assert doc_type is None
        assert confidence == 0.0


class TestLegalTermExtraction:
    """Test legal term extraction functionality."""
    
    def test_extract_legal_terms_from_question(self, engine):
        """Test extraction of legal terms from user questions."""
        question = "What are the liability and intellectual property provisions?"
        legal_terms = engine.extract_legal_terms(question)
        
        assert "liability" in legal_terms
        assert "intellectual property" in legal_terms
    
    def test_extract_mta_specific_terms(self, engine):
        """Test extraction of MTA-specific terms."""
        question = "Who owns the derivatives and what are the publication requirements?"
        legal_terms = engine.extract_legal_terms(question)
        
        assert "derivatives" in legal_terms
        assert "publication" in legal_terms
    
    def test_extract_no_legal_terms(self, engine):
        """Test extraction when no legal terms are present."""
        question = "What is the weather like today?"
        legal_terms = engine.extract_legal_terms(question)
        
        assert len(legal_terms) == 0
    
    def test_extract_case_insensitive_terms(self, engine):
        """Test that term extraction is case insensitive."""
        question = "What are the LIABILITY and INTELLECTUAL PROPERTY terms?"
        legal_terms = engine.extract_legal_terms(question)
        
        assert "liability" in legal_terms
        assert "intellectual property" in legal_terms


class TestLegalContextMatching:
    """Test enhanced legal context matching."""
    
    def test_find_legal_context_with_weighting(self, engine, sample_mta_document):
        """Test that legal context matching applies proper weighting."""
        question = "What are the liability provisions?"
        
        # Mock the parent class method
        with patch.object(engine, 'get_relevant_context') as mock_context:
            mock_context.return_value = [
                {
                    'text': 'The Provider makes no warranties and shall not be liable for any damages.',
                    'source': 'Document Content',
                    'relevance_score': 0.5,
                    'matches': 1
                }
            ]
            
            context = engine.find_legal_context(question, sample_mta_document)
            
            assert len(context) > 0
            assert context[0]['relevance_score'] > 0.5  # Should be boosted due to legal terms
            assert 'legal_terms_found' in context[0]
    
    def test_find_legal_context_sorts_by_relevance(self, engine, sample_mta_document):
        """Test that legal context is sorted by enhanced relevance score."""
        question = "What are the intellectual property and liability terms?"
        
        with patch.object(engine, 'get_relevant_context') as mock_context:
            mock_context.return_value = [
                {
                    'text': 'General contract terms apply.',
                    'source': 'Document Content',
                    'relevance_score': 0.3,
                    'matches': 1
                },
                {
                    'text': 'The Provider makes no warranties and shall not be liable for damages.',
                    'source': 'Document Content',
                    'relevance_score': 0.4,
                    'matches': 1
                }
            ]
            
            context = engine.find_legal_context(question, sample_mta_document)
            
            # Should be sorted by relevance score (descending)
            assert context[0]['relevance_score'] >= context[1]['relevance_score']


class TestStructuredResponseFormatting:
    """Test structured response parsing and formatting."""
    
    def test_format_well_structured_response(self, engine):
        """Test parsing of properly structured AI response."""
        raw_response = """
        **Direct Evidence:**
        The agreement states that "Provider retains ownership of the Original Material."
        
        **Plain-English Explanation:**
        This means the original provider keeps all rights to the materials they're sharing.
        
        **Implication/Analysis:**
        This protects the provider's intellectual property while allowing research use.
        """
        
        structured = engine.format_structured_response(raw_response)
        
        assert 'direct_evidence' in structured
        assert 'plain_explanation' in structured
        assert 'implication_analysis' in structured
        assert "Provider retains ownership" in structured['direct_evidence']
        assert "original provider keeps all rights" in structured['plain_explanation']
        assert "protects the provider's intellectual property" in structured['implication_analysis']
    
    def test_format_numbered_response(self, engine):
        """Test parsing of numbered response format."""
        raw_response = """
        1. **Direct Evidence:** The contract specifies liability limitations.
        2. **Plain-English Explanation:** The provider won't be responsible for damages.
        3. **Implication/Analysis:** This shifts risk to the recipient organization.
        """
        
        structured = engine.format_structured_response(raw_response)
        
        assert "liability limitations" in structured['direct_evidence']
        assert "won't be responsible" in structured['plain_explanation']
        assert "shifts risk" in structured['implication_analysis']
    
    def test_format_incomplete_response(self, engine):
        """Test handling of incomplete structured response."""
        raw_response = """
        **Direct Evidence:**
        The agreement mentions intellectual property rights.
        """
        
        structured = engine.format_structured_response(raw_response)
        
        assert "intellectual property rights" in structured['direct_evidence']
        assert structured['plain_explanation'] == ""
        assert structured['implication_analysis'] == ""
    
    def test_format_unstructured_response(self, engine):
        """Test handling of completely unstructured response."""
        raw_response = "This is just a regular response without any structure."
        
        structured = engine.format_structured_response(raw_response)
        
        assert structured['direct_evidence'] == raw_response
        assert "could not be automatically structured" in structured['plain_explanation'].lower()


class TestContractAnalysisGeneration:
    """Test contract analysis generation."""
    
    @patch('src.services.contract_analyst_engine.ContractAnalystEngine._call_gemini_api')
    def test_generate_contract_analysis_success(self, mock_api, engine, sample_mta_document):
        """Test successful contract analysis generation."""
        mock_api.return_value = """
        **Direct Evidence:**
        The MTA states "Provider retains ownership of Original Material."
        
        **Plain-English Explanation:**
        The original owner keeps their rights to the shared materials.
        
        **Implication/Analysis:**
        This protects the provider while enabling research collaboration.
        """
        
        context_sections = [
            {
                'text': 'Provider retains ownership of Original Material.',
                'source': 'Document Content',
                'relevance_score': 0.8,
                'legal_terms_found': ['ownership']
            }
        ]
        
        analysis = engine.generate_contract_analysis(
            "Who owns the original material?", 
            context_sections, 
            sample_mta_document
        )
        
        assert isinstance(analysis, ContractAnalysisResponse)
        assert "Provider retains ownership" in analysis.direct_evidence
        assert "original owner keeps their rights" in analysis.plain_explanation
        assert "protects the provider" in analysis.implication_analysis
        assert analysis.document_type == "MTA"
        assert len(analysis.sources) > 0
    
    @patch('src.services.contract_analyst_engine.ContractAnalystEngine._call_gemini_api')
    def test_generate_contract_analysis_api_error(self, mock_api, engine, sample_mta_document):
        """Test contract analysis generation with API error."""
        mock_api.side_effect = Exception("API Error")
        
        context_sections = [
            {
                'text': 'Some legal text.',
                'source': 'Document Content',
                'relevance_score': 0.5
            }
        ]
        
        # Should not raise exception, but return fallback response
        analysis = engine.generate_contract_analysis(
            "Test question", 
            context_sections, 
            sample_mta_document
        )
        
        assert isinstance(analysis, ContractAnalysisResponse)
        assert analysis.confidence == 0.5  # Fallback confidence
        assert "processing error" in analysis.plain_explanation.lower()


class TestEnhancedAnswerQuestion:
    """Test the enhanced answer_question method."""
    
    def test_answer_question_legal_document(self, engine, sample_mta_document, mock_storage):
        """Test answer_question with legal document uses contract analysis."""
        mock_storage.get_document_with_embeddings.return_value = sample_mta_document
        
        with patch.object(engine, 'generate_contract_analysis') as mock_analysis, \
             patch.object(engine, 'find_legal_context') as mock_context:
            
            # Mock context sections
            mock_context.return_value = [
                {
                    'text': 'Test legal context',
                    'source': 'Document Content',
                    'relevance_score': 0.8
                }
            ]
            
            mock_analysis.return_value = ContractAnalysisResponse(
                direct_evidence="Test evidence",
                plain_explanation="Test explanation",
                implication_analysis="Test analysis",
                sources=["Document Content"],
                confidence=0.8,
                document_type="MTA"
            )
            
            result = engine.answer_question("Test question", "test-mta-1")
            
            assert result['analysis_mode'] == 'contract'
            assert result['document_type'] == 'MTA'
            assert 'structured_response' in result
            assert result['confidence'] == 0.8
    
    def test_answer_question_regular_document(self, engine, sample_regular_document, mock_storage):
        """Test answer_question with regular document uses standard analysis."""
        mock_storage.get_document_with_embeddings.return_value = sample_regular_document
        
        with patch.object(engine, 'generate_answer') as mock_generate:
            mock_generate.return_value = "Standard answer"
            with patch.object(engine, 'get_relevant_context') as mock_context:
                mock_context.return_value = [{'text': 'context', 'source': 'test', 'relevance_score': 0.5}]
                
                result = engine.answer_question("Test question", "test-doc-1")
                
                # Should fall back to parent class behavior
                assert 'analysis_mode' not in result or result.get('analysis_mode') != 'contract'
    
    def test_answer_question_document_not_found(self, engine, mock_storage):
        """Test answer_question when document is not found."""
        mock_storage.get_document_with_embeddings.return_value = None
        
        result = engine.answer_question("Test question", "nonexistent-doc")
        
        assert "couldn't find that document" in result['answer']
        assert result['confidence'] == 0.0
        assert 'error' in result


class TestFactoryFunction:
    """Test the factory function."""
    
    def test_create_contract_analyst_engine_with_storage(self):
        """Test factory function with provided storage."""
        mock_storage = Mock(spec=DocumentStorage)
        engine = create_contract_analyst_engine("test-key", mock_storage)
        
        assert isinstance(engine, ContractAnalystEngine)
        assert engine.storage == mock_storage
        assert engine.api_key == "test-key"
    
    def test_create_contract_analyst_engine_without_storage(self):
        """Test factory function without provided storage."""
        with patch('src.services.contract_analyst_engine.DocumentStorage') as mock_storage_class:
            mock_storage_instance = Mock()
            mock_storage_class.return_value = mock_storage_instance
            
            engine = create_contract_analyst_engine("test-key")
            
            assert isinstance(engine, ContractAnalystEngine)
            assert engine.api_key == "test-key"
            mock_storage_class.assert_called_once()


class TestContractAnalysisResponse:
    """Test ContractAnalysisResponse dataclass."""
    
    def test_contract_analysis_response_creation(self):
        """Test creating ContractAnalysisResponse with all fields."""
        response = ContractAnalysisResponse(
            direct_evidence="Test evidence",
            plain_explanation="Test explanation",
            implication_analysis="Test analysis",
            sources=["Source 1", "Source 2"],
            confidence=0.85,
            document_type="MTA",
            legal_terms_found=["liability", "ownership"]
        )
        
        assert response.direct_evidence == "Test evidence"
        assert response.plain_explanation == "Test explanation"
        assert response.implication_analysis == "Test analysis"
        assert len(response.sources) == 2
        assert response.confidence == 0.85
        assert response.document_type == "MTA"
        assert "liability" in response.legal_terms_found
    
    def test_contract_analysis_response_defaults(self):
        """Test ContractAnalysisResponse with default values."""
        response = ContractAnalysisResponse(
            direct_evidence="Test evidence",
            plain_explanation="Test explanation"
        )
        
        assert response.implication_analysis is None
        assert response.sources == []
        assert response.confidence == 0.0
        assert response.document_type == "unknown"
        assert response.legal_terms_found == []


if __name__ == "__main__":
    pytest.main([__file__])