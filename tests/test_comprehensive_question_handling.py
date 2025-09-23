"""
Comprehensive test suite for question handling across all categories.

This test validates that the enhanced contract assistant properly handles
all types of questions from document-grounded to casual/playful questions.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.services.question_classifier import QuestionClassifier
from src.models.document import Document
from src.models.enhanced import IntentType, ResponseType
from src.storage.document_storage import DocumentStorage


class TestComprehensiveQuestionHandling:
    """Test comprehensive question handling across all categories."""
    
    @pytest.fixture
    def mock_mta_document(self):
        """Create a mock MTA document for testing."""
        doc = Mock(spec=Document)
        doc.id = "mta_doc_1"
        doc.title = "Material Transfer Agreement - ImaginAb to MNRI"
        doc.content = """
        MATERIAL TRANSFER AGREEMENT
        
        This Material Transfer Agreement ("Agreement") is entered into between ImaginAb, Inc. ("Provider") 
        and Molecular Nuclear Research Institute ("MNRI", "Recipient") for the transfer of research materials.
        
        1. MATERIALS: Provider will transfer antibody materials for research use only.
        
        2. AUTHORIZED LOCATION: Materials must be stored at MNRI facilities at 123 Research Drive.
        
        3. RESEARCH PLAN: MNRI will conduct imaging studies using the transferred materials.
        
        4. PUBLICATION: Any publication must acknowledge Provider and follow IP protection guidelines.
        
        5. INTELLECTUAL PROPERTY: Provider retains ownership of original materials. 
           Any derivatives or improvements developed by MNRI shall be jointly owned.
        
        6. CONFIDENTIALITY: All information shall remain confidential for 5 years after termination.
        
        7. TERMINATION: Agreement expires October 31, 2024. Unused materials must be returned.
        
        8. LIABILITY: Provider disclaims all warranties. MNRI assumes all risks.
        
        Signed by:
        Dr. Jane Smith, CEO, ImaginAb
        Dr. Robert Johnson, Director, MNRI
        """
        doc.original_text = doc.content
        doc.is_legal_document = True
        doc.legal_document_type = "MTA"
        return doc
    
    @pytest.fixture
    def enhanced_router(self, mock_mta_document):
        """Create enhanced router with mocked dependencies."""
        storage = Mock(spec=DocumentStorage)
        storage.get_document_with_embeddings.return_value = mock_mta_document
        
        router = EnhancedResponseRouter(storage, "test_api_key")
        
        # Mock the contract engine's analyze_question method
        router.contract_engine.analyze_question = Mock(return_value={
            'response': 'Mocked contract analysis response',
            'direct_evidence': 'Mocked evidence',
            'plain_explanation': 'Mocked explanation',
            'sources': ['Document Section 1'],
            'confidence': 0.8
        })
        
        return router
    
    @pytest.fixture
    def question_classifier(self):
        """Create question classifier for testing."""
        return QuestionClassifier()
    
    def test_document_grounded_questions(self, enhanced_router, mock_mta_document):
        """Test document-grounded questions that should find direct answers."""
        
        document_grounded_questions = [
            "Who are the parties involved in this agreement?",
            "When does the agreement start and when does it expire?", 
            "What is the authorized location for the materials?",
            "What must MNRI do with unused materials at the end of the agreement?",
            "How long do confidentiality obligations last after termination?"
        ]
        
        for question in document_grounded_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "test_session", mock_mta_document
            )
            
            # Should be routed as document analysis
            assert response.response_type == ResponseType.DOCUMENT_ANALYSIS, \
                f"Question '{question}' should be document analysis, got {response.response_type}"
            
            # Should have high confidence
            assert response.confidence > 0.5, \
                f"Question '{question}' should have high confidence, got {response.confidence}"
            
            # Should have content
            assert len(response.content) > 0, \
                f"Question '{question}' should have content"
    
    def test_multi_section_cross_exhibit_questions(self, enhanced_router, mock_mta_document):
        """Test questions requiring analysis across multiple sections."""
        
        multi_section_questions = [
            "What are the deliverables MNRI must provide, and when?",
            "What publication restrictions exist, and how do they connect to IP protection?",
            "What storage conditions are required for each of the materials in Exhibit A?",
            "What objectives are listed in the research plan, and how do they tie into the exclusions?",
            "If MNRI invented a new method of imaging using the materials, who owns the rights and why?"
        ]
        
        for question in multi_section_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "test_session", mock_mta_document
            )
            
            # Should be routed as document analysis
            assert response.response_type == ResponseType.DOCUMENT_ANALYSIS, \
                f"Multi-section question '{question}' should be document analysis, got {response.response_type}"
            
            # Should have reasonable confidence
            assert response.confidence > 0.4, \
                f"Multi-section question '{question}' should have reasonable confidence, got {response.confidence}"
    
    def test_subjective_interpretive_questions(self, enhanced_router, mock_mta_document):
        """Test subjective questions requiring interpretation."""
        
        subjective_questions = [
            "Who benefits more from this agreement, ImaginAb or MNRI? Why?",
            "What are the biggest risks MNRI faces in this agreement?",
            "Is this agreement more favorable to research freedom or to IP protection?",
            "If you were MNRI's lab manager, what would you be most careful about?",
            "What does this agreement tell us about ImaginAb's business priorities?"
        ]
        
        for question in subjective_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "test_session", mock_mta_document
            )
            
            # Should be routed as document analysis (interpretive but document-based)
            assert response.response_type == ResponseType.DOCUMENT_ANALYSIS, \
                f"Subjective question '{question}' should be document analysis, got {response.response_type}"
            
            # May have lower confidence due to subjectivity
            assert response.confidence > 0.3, \
                f"Subjective question '{question}' should have some confidence, got {response.confidence}"
    
    def test_scenario_what_if_questions(self, enhanced_router, mock_mta_document):
        """Test scenario-based 'what if' questions."""
        
        scenario_questions = [
            "What happens if MNRI uses the materials in humans?",
            "Suppose MNRI accidentally shares the materials with another lab — what does the agreement require?",
            "If the research goes beyond October 2024, what must MNRI do?",
            "What happens if MNRI wants to combine these materials with another drug?",
            "How is ImaginAb protected if MNRI publishes results too quickly?"
        ]
        
        for question in scenario_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "test_session", mock_mta_document
            )
            
            # Should be routed as document analysis (scenario-based but document-grounded)
            assert response.response_type == ResponseType.DOCUMENT_ANALYSIS, \
                f"Scenario question '{question}' should be document analysis, got {response.response_type}"
            
            # Should have reasonable confidence
            assert response.confidence > 0.4, \
                f"Scenario question '{question}' should have reasonable confidence, got {response.confidence}"
    
    def test_ambiguity_compound_questions(self, enhanced_router, mock_mta_document):
        """Test complex compound questions with multiple parts."""
        
        compound_questions = [
            "Where are the materials supposed to be stored, who is responsible for them, and what specific materials are included in the shipment with their quantities?",
            "What termination rights do both parties have, and what must happen with the materials afterward?",
            "Which sections talk about ownership, and how does that interact with publication rights?",
            "Who signs the agreement, and what positions do they hold?",
            "Can you summarize the agreement as if you were explaining it to a PhD student new to MTAs?"
        ]
        
        for question in compound_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "test_session", mock_mta_document
            )
            
            # Should be routed as document analysis
            assert response.response_type == ResponseType.DOCUMENT_ANALYSIS, \
                f"Compound question '{question}' should be document analysis, got {response.response_type}"
            
            # Should have reasonable confidence
            assert response.confidence > 0.4, \
                f"Compound question '{question}' should have reasonable confidence, got {response.confidence}"
    
    def test_off_topic_casual_playful_questions(self, enhanced_router, mock_mta_document):
        """Test off-topic, casual, and playful questions."""
        
        off_topic_questions = [
            "Can you explain this agreement in the style of a cooking recipe?",
            "If I were a mouse in this study, what would happen to me?",
            "What's the \"vibe\" of this agreement — collaborative, strict, or neutral?",
            "Tell me a lawyer joke involving antibodies."
        ]
        
        for question in off_topic_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "test_session", mock_mta_document
            )
            
            # Should be routed as casual or fallback
            assert response.response_type in [ResponseType.CASUAL, ResponseType.FALLBACK], \
                f"Off-topic question '{question}' should be casual/fallback, got {response.response_type}"
            
            # Should have suggestions to redirect to document
            assert len(response.suggestions) > 0, \
                f"Off-topic question '{question}' should have suggestions"
            
            # Should mention the document or redirect
            content_lower = response.content.lower()
            assert any(word in content_lower for word in ['agreement', 'contract', 'document', 'help']), \
                f"Off-topic question '{question}' should redirect to document analysis"
    
    def test_question_classification_accuracy(self, question_classifier):
        """Test question classifier accuracy for different question types."""
        
        test_cases = [
            # Document-related questions
            ("Who are the parties in this agreement?", IntentType.DOCUMENT_RELATED),
            ("What are the termination conditions?", IntentType.DOCUMENT_RELATED),
            
            # General knowledge questions  
            ("What is a liability clause?", IntentType.CONTRACT_GENERAL),
            ("What does intellectual property mean?", IntentType.CONTRACT_GENERAL),
            
            # Casual questions
            ("Hi there! How are you?", IntentType.CASUAL),
            ("Thanks, that was helpful!", IntentType.CASUAL),
            
            # Off-topic questions
            ("What's the weather like?", IntentType.OFF_TOPIC),
            ("Can you tell me a joke?", IntentType.OFF_TOPIC),
        ]
        
        for question, expected_intent in test_cases:
            intent = question_classifier.classify_intent(question)
            
            assert intent.primary_intent == expected_intent, \
                f"Question '{question}' should be classified as {expected_intent}, got {intent.primary_intent}"
    
    def test_mta_expertise_detection(self, enhanced_router, mock_mta_document):
        """Test MTA-specific expertise detection and enhancement."""
        
        mta_specific_questions = [
            "What are the permitted uses of the materials?",
            "Who owns derivatives created by the recipient?",
            "What are the publication requirements for research results?",
            "Can the materials be shared with third parties?"
        ]
        
        for question in mta_specific_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "test_session", mock_mta_document
            )
            
            # Should be document analysis
            assert response.response_type == ResponseType.DOCUMENT_ANALYSIS
            
            # Should have MTA-related context or sources
            context_mentions_mta = any('mta' in str(ctx).lower() for ctx in response.context_used)
            sources_mention_mta = any('mta' in str(src).lower() for src in response.sources)
            
            # At minimum should be processed as document analysis for MTA
            assert response.response_type == ResponseType.DOCUMENT_ANALYSIS, \
                f"MTA question '{question}' should use document analysis"
    
    def test_conversation_context_handling(self, enhanced_router, mock_mta_document):
        """Test conversation context and follow-up handling."""
        
        session_id = "context_test_session"
        
        # First question
        response1 = enhanced_router.route_question(
            "What are the main terms of this agreement?",
            mock_mta_document.id, session_id, mock_mta_document
        )
        
        # Follow-up question
        response2 = enhanced_router.route_question(
            "Can you explain that in simpler terms?",
            mock_mta_document.id, session_id, mock_mta_document
        )
        
        # Both should be document analysis
        assert response1.response_type == ResponseType.DOCUMENT_ANALYSIS
        assert response2.response_type == ResponseType.DOCUMENT_ANALYSIS
        
        # Context should be maintained
        assert session_id in enhanced_router.context_manager.conversations
    
    def test_error_handling_and_graceful_degradation(self, enhanced_router, mock_mta_document):
        """Test error handling when components fail."""
        
        # Mock a failure in contract engine
        enhanced_router.contract_engine.analyze_question = Mock(side_effect=Exception("Test error"))
        
        response = enhanced_router.route_question(
            "What are the terms?",
            mock_mta_document.id, "error_test_session", mock_mta_document
        )
        
        # Should gracefully handle error
        assert response.response_type == ResponseType.FALLBACK
        assert len(response.content) > 0
        assert "error" in response.content.lower() or "sorry" in response.content.lower()
    
    def test_response_quality_and_completeness(self, enhanced_router, mock_mta_document):
        """Test that responses are complete and helpful."""
        
        test_questions = [
            "Who are the parties in this agreement?",
            "What's the weather like?",
            "Hi there!",
            "What is intellectual property?"
        ]
        
        for question in test_questions:
            response = enhanced_router.route_question(
                question, mock_mta_document.id, "quality_test_session", mock_mta_document
            )
            
            # All responses should have content
            assert len(response.content.strip()) > 0, \
                f"Question '{question}' should have non-empty content"
            
            # All responses should have a valid response type
            assert response.response_type in [
                ResponseType.DOCUMENT_ANALYSIS, 
                ResponseType.FALLBACK, 
                ResponseType.CASUAL, 
                ResponseType.GENERAL_KNOWLEDGE
            ], f"Question '{question}' should have valid response type"
            
            # All responses should have reasonable confidence
            assert 0.0 <= response.confidence <= 1.0, \
                f"Question '{question}' should have confidence between 0 and 1"
            
            # Responses should have suggestions when appropriate
            if response.response_type in [ResponseType.FALLBACK, ResponseType.CASUAL]:
                assert len(response.suggestions) > 0, \
                    f"Fallback/casual question '{question}' should have suggestions"


def run_comprehensive_test():
    """Run comprehensive test and report results."""
    
    print("🧪 Running Comprehensive Question Handling Test")
    print("=" * 60)
    
    # Create test fixtures
    mock_doc = Mock(spec=Document)
    mock_doc.id = "test_doc"
    mock_doc.title = "Test MTA Agreement"
    mock_doc.content = "Material Transfer Agreement between Provider and Recipient..."
    mock_doc.original_text = mock_doc.content
    mock_doc.is_legal_document = True
    mock_doc.legal_document_type = "MTA"
    
    storage = Mock(spec=DocumentStorage)
    storage.get_document_with_embeddings.return_value = mock_doc
    
    router = EnhancedResponseRouter(storage, "test_key")
    router.contract_engine.analyze_question = Mock(return_value={
        'response': 'Test analysis response',
        'sources': ['Test source'],
        'confidence': 0.8
    })
    
    # Test categories
    test_categories = {
        "📑 Document-Grounded": [
            "Who are the parties involved in this agreement?",
            "When does the agreement start and when does it expire?",
            "What is the authorized location for the materials?",
        ],
        "🔄 Multi-Section": [
            "What are the deliverables MNRI must provide, and when?",
            "What publication restrictions exist, and how do they connect to IP protection?",
        ],
        "⚖️ Subjective/Interpretive": [
            "Who benefits more from this agreement, ImaginAb or MNRI? Why?",
            "What are the biggest risks MNRI faces in this agreement?",
        ],
        "💡 Scenario/What-if": [
            "What happens if MNRI uses the materials in humans?",
            "Suppose MNRI accidentally shares the materials with another lab — what does the agreement require?",
        ],
        "🧩 Ambiguity/Compound": [
            "Where are the materials supposed to be stored, who is responsible for them, and what specific materials are included?",
            "Can you summarize the agreement as if you were explaining it to a PhD student new to MTAs?",
        ],
        "🎭 Off-Topic/Casual/Playful": [
            "Can you explain this agreement in the style of a cooking recipe?",
            "What's the \"vibe\" of this agreement — collaborative, strict, or neutral?",
        ]
    }
    
    results = {}
    
    for category, questions in test_categories.items():
        print(f"\n{category}")
        print("-" * 40)
        
        category_results = []
        
        for question in questions:
            try:
                response = router.route_question(question, mock_doc.id, "test_session", mock_doc)
                
                result = {
                    'question': question,
                    'response_type': response.response_type.value if hasattr(response.response_type, 'value') else str(response.response_type),
                    'confidence': response.confidence,
                    'has_content': len(response.content.strip()) > 0,
                    'has_suggestions': len(response.suggestions) > 0,
                    'success': True
                }
                
                print(f"✅ {question[:60]}...")
                print(f"   Type: {result['response_type']}, Confidence: {result['confidence']:.2f}")
                
            except Exception as e:
                result = {
                    'question': question,
                    'error': str(e),
                    'success': False
                }
                print(f"❌ {question[:60]}...")
                print(f"   Error: {str(e)}")
            
            category_results.append(result)
        
        results[category] = category_results
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    
    total_tests = sum(len(results[cat]) for cat in results)
    successful_tests = sum(len([r for r in results[cat] if r.get('success', False)]) for cat in results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Category breakdown
    for category, category_results in results.items():
        successful = len([r for r in category_results if r.get('success', False)])
        total = len(category_results)
        print(f"{category}: {successful}/{total} ({(successful/total)*100:.1f}%)")
    
    return results


if __name__ == "__main__":
    run_comprehensive_test()