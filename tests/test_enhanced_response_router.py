"""
Tests for Enhanced Response Router
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.services.enhanced_response_router import EnhancedResponseRouter
from src.models.enhanced import (
    EnhancedResponse, QuestionIntent, ResponseStrategy,
    ConversationContext, MTAContext, MTAInsight
)
from src.models.document import Document


class TestEnhancedResponseRouter:
    """Test enhanced response router functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.router = EnhancedResponseRouter()
        
        # Mock dependencies
        self.router.question_classifier = Mock()
        self.router.fallback_generator = Mock()
        self.router.mta_specialist = Mock()
        self.router.context_manager = Mock()
        self.router.contract_engine = Mock()
        
        # Test data
        self.session_id = "test_session_123"
        self.document_id = "test_doc_456"
        self.question = "What are the liability terms?"
        
        # Create mock document
        self.mock_document = Mock(spec=Document)
        self.mock_document.id = self.document_id
        self.mock_document.content = "Test contract content with liability and indemnification terms"
        
        # Create mock intent
        self.mock_intent = QuestionIntent(
            primary_intent="document_related",
            confidence=0.8,
            secondary_intents=[],
            document_relevance_score=0.9,
            casualness_level=0.1,
            requires_mta_expertise=False,
            requires_fallback=False
        )
        
        # Create mock strategy
        self.mock_strategy = ResponseStrategy(
            handler_type="existing_contract",
            use_structured_format=True,
            include_suggestions=True,
            tone_preference="professional",
            fallback_options=[],
            context_requirements=[]
        )
        
        # Create mock conversation context
        self.mock_context = Mock(spec=ConversationContext)
        self.mock_context.session_id = self.session_id
        self.mock_context.current_tone = "professional"
        self.mock_context.user_expertise_level = "intermediate"
    
    def test_route_question_document_related_success(self):
        """Test successful routing of document-related question"""
        # Setup mocks
        self.router.context_manager.get_conversation_context.return_value = self.mock_context
        self.router.question_classifier.classify_intent.return_value = self.mock_intent
        
        # Mock contract engine response
        contract_response = {
            'response': 'Test contract analysis response',
            'confidence': 0.9
        }
        self.router.contract_engine.analyze_question.return_value = contract_response
        
        # Execute
        response = self.router.route_question(
            self.question, self.document_id, self.session_id, self.mock_document
        )
        
        # Verify
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "document_analysis"
        assert response.content == 'Test contract analysis response'
        assert response.confidence == self.mock_intent.confidence
        
        # Verify method calls
        self.router.context_manager.get_conversation_context.assert_called_once_with(self.session_id)
        self.router.question_classifier.classify_intent.assert_called_once()
        self.router.contract_engine.analyze_question.assert_called_once_with(self.question, self.document_id)
        self.router.context_manager.update_conversation_context.assert_called_once()
    
    def test_route_question_fallback_success(self):
        """Test successful routing to fallback handler"""
        # Setup for off-topic question
        off_topic_intent = QuestionIntent(
            primary_intent="off_topic",
            confidence=0.7,
            secondary_intents=[],
            document_relevance_score=0.1,
            casualness_level=0.3,
            requires_mta_expertise=False,
            requires_fallback=True
        )
        
        fallback_strategy = ResponseStrategy(
            handler_type="fallback",
            use_structured_format=False,
            include_suggestions=True,
            tone_preference="professional",
            fallback_options=["redirection", "suggestions"],
            context_requirements=[]
        )
        
        # Setup mocks
        self.router.context_manager.get_conversation_context.return_value = self.mock_context
        self.router.question_classifier.classify_intent.return_value = off_topic_intent
        
        # Mock fallback response
        self.router.fallback_generator.generate_off_topic_response.return_value = "I understand this is off-topic..."
        self.router.fallback_generator.suggest_relevant_questions.return_value = ["What are the key terms?"]
        
        # Execute
        response = self.router.route_question(
            "What's the weather like?", self.document_id, self.session_id, self.mock_document
        )
        
        # Verify
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "fallback"
        assert "off-topic" in response.content
        assert len(response.suggestions) > 0
        
        # Verify fallback generator was called
        self.router.fallback_generator.generate_off_topic_response.assert_called_once()
    
    def test_route_question_mta_expertise_required(self):
        """Test routing with MTA expertise requirement"""
        # Setup MTA-specific intent
        mta_intent = QuestionIntent(
            primary_intent="document_related",
            confidence=0.8,
            secondary_intents=[],
            document_relevance_score=0.9,
            casualness_level=0.1,
            requires_mta_expertise=True,
            requires_fallback=False
        )
        
        mta_strategy = ResponseStrategy(
            handler_type="existing_contract",
            use_structured_format=True,
            include_suggestions=True,
            tone_preference="professional",
            fallback_options=[],
            context_requirements=["mta_expertise"]
        )
        
        # Setup mocks
        self.router.context_manager.get_conversation_context.return_value = self.mock_context
        self.router.question_classifier.classify_intent.return_value = mta_intent
        
        # Mock MTA document
        mta_document = Mock(spec=Document)
        mta_document.id = self.document_id
        mta_document.content = "Material Transfer Agreement with derivatives and research use only"
        
        # Mock contract engine response
        contract_response = {'response': 'MTA analysis response'}
        self.router.contract_engine.analyze_question.return_value = contract_response
        
        # Mock MTA specialist
        mta_context = Mock(spec=MTAContext)
        mta_insight = Mock(spec=MTAInsight)
        mta_insight.concept_explanations = {"derivatives": "Materials created from original"}
        mta_insight.research_implications = ["Consider IP ownership"]
        mta_insight.suggested_questions = ["What about commercial use?"]
        
        self.router.mta_specialist.analyze_mta_context.return_value = mta_context
        self.router.mta_specialist.provide_mta_expertise.return_value = mta_insight
        
        # Execute
        response = self.router.route_question(
            "What about derivatives?", self.document_id, self.session_id, mta_document
        )
        
        # Verify
        assert isinstance(response, EnhancedResponse)
        assert "mta_specialist" in response.sources
        assert "MTA Context:" in response.content
        assert len(response.suggestions) > 0
        
        # Verify MTA specialist was called
        self.router.mta_specialist.analyze_mta_context.assert_called_once_with(mta_document)
        self.router.mta_specialist.provide_mta_expertise.assert_called_once()
    
    def test_route_question_error_handling(self):
        """Test error handling in route_question"""
        # Setup mocks to raise exception
        self.router.context_manager.get_conversation_context.side_effect = Exception("Test error")
        
        # Execute
        response = self.router.route_question(
            self.question, self.document_id, self.session_id, self.mock_document
        )
        
        # Verify error fallback response
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "error_fallback"
        assert "encountered an issue" in response.content
        assert len(response.suggestions) > 0
    
    def test_classify_question_intent_success(self):
        """Test successful question intent classification"""
        # Setup mock
        self.router.question_classifier.classify_intent.return_value = self.mock_intent
        
        # Execute
        intent = self.router.classify_question_intent(self.question, self.mock_document, self.mock_context)
        
        # Verify
        assert isinstance(intent, QuestionIntent)
        assert intent.primary_intent == "document_related"
        assert intent.confidence == 0.8
        
        # Verify classifier was called with context
        self.router.question_classifier.classify_intent.assert_called_once_with(self.question, self.mock_context)
    
    def test_classify_question_intent_mta_enhancement(self):
        """Test MTA enhancement in intent classification"""
        # Setup MTA document
        mta_document = Mock(spec=Document)
        mta_document.content = "Material Transfer Agreement with research use only"
        
        # Setup mock
        base_intent = QuestionIntent(
            primary_intent="document_related",
            confidence=0.7,
            secondary_intents=[],
            document_relevance_score=0.8,
            casualness_level=0.1,
            requires_mta_expertise=False,
            requires_fallback=False
        )
        self.router.question_classifier.classify_intent.return_value = base_intent
        
        # Execute with MTA-related question
        mta_question = "What about derivatives and commercial use?"
        intent = self.router.classify_question_intent(mta_question, mta_document, self.mock_context)
        
        # Verify MTA expertise is required
        assert intent.requires_mta_expertise == True
        assert intent.confidence >= 0.7  # Should be enhanced
    
    def test_classify_question_intent_error_handling(self):
        """Test error handling in intent classification"""
        # Setup mock to raise exception
        self.router.question_classifier.classify_intent.side_effect = Exception("Classification error")
        
        # Execute
        intent = self.router.classify_question_intent(self.question, self.mock_document, self.mock_context)
        
        # Verify safe default intent
        assert isinstance(intent, QuestionIntent)
        assert intent.primary_intent == "document_related"
        assert intent.confidence == 0.5
        assert intent.requires_fallback == True
    
    def test_determine_response_strategy_document_related(self):
        """Test response strategy determination for document-related questions"""
        strategy = self.router.determine_response_strategy(self.mock_intent, self.mock_document, self.mock_context)
        
        assert isinstance(strategy, ResponseStrategy)
        assert strategy.handler_type == "existing_contract"
        assert strategy.use_structured_format == True
        assert strategy.include_suggestions == True
    
    def test_determine_response_strategy_contract_general(self):
        """Test response strategy for general contract questions"""
        general_intent = QuestionIntent(
            primary_intent="contract_general",
            confidence=0.7,
            secondary_intents=[],
            document_relevance_score=0.3,
            casualness_level=0.2,
            requires_mta_expertise=False,
            requires_fallback=False
        )
        
        strategy = self.router.determine_response_strategy(general_intent, self.mock_document, self.mock_context)
        
        assert strategy.handler_type == "general_knowledge"
        assert strategy.use_structured_format == False
        assert "document_redirection" in strategy.fallback_options
    
    def test_determine_response_strategy_off_topic(self):
        """Test response strategy for off-topic questions"""
        off_topic_intent = QuestionIntent(
            primary_intent="off_topic",
            confidence=0.8,
            secondary_intents=[],
            document_relevance_score=0.1,
            casualness_level=0.3,
            requires_mta_expertise=False,
            requires_fallback=True
        )
        
        strategy = self.router.determine_response_strategy(off_topic_intent, self.mock_document, self.mock_context)
        
        assert strategy.handler_type == "fallback"
        assert strategy.use_structured_format == False
        assert strategy.include_suggestions == True
        assert "redirection" in strategy.fallback_options
        assert "suggestions" in strategy.fallback_options
    
    def test_determine_response_strategy_casual(self):
        """Test response strategy for casual questions"""
        casual_intent = QuestionIntent(
            primary_intent="casual",
            confidence=0.9,
            secondary_intents=[],
            document_relevance_score=0.1,
            casualness_level=0.8,
            requires_mta_expertise=False,
            requires_fallback=False
        )
        
        strategy = self.router.determine_response_strategy(casual_intent, self.mock_document, self.mock_context)
        
        assert strategy.handler_type == "casual"
        assert strategy.use_structured_format == False
        assert strategy.tone_preference == "conversational"
        assert "gentle_redirection" in strategy.fallback_options
    
    def test_determine_response_strategy_context_patterns(self):
        """Test response strategy adjustment based on context patterns"""
        # Setup context with patterns
        self.router.context_manager.detect_conversation_patterns.return_value = [
            "repetitive_questioning", "increasing_complexity", "casual_drift"
        ]
        
        strategy = self.router.determine_response_strategy(self.mock_intent, self.mock_document, self.mock_context)
        
        # Verify pattern-based adjustments
        assert "pattern_acknowledgment" in strategy.fallback_options
        assert "detailed_explanation" in strategy.context_requirements
        assert strategy.tone_preference == "conversational"  # Due to casual_drift
    
    def test_coordinate_fallback_response_off_topic(self):
        """Test fallback response coordination for off-topic questions"""
        off_topic_intent = QuestionIntent(
            primary_intent="off_topic",
            confidence=0.7,
            secondary_intents=[],
            document_relevance_score=0.1,
            casualness_level=0.3,
            requires_mta_expertise=False,
            requires_fallback=True
        )
        
        # Setup mocks
        self.router.fallback_generator.generate_off_topic_response.return_value = "I understand this is off-topic..."
        self.router.fallback_generator.suggest_relevant_questions.return_value = ["What are the key terms?"]
        
        # Execute
        response = self.router.coordinate_fallback_response("What's the weather?", off_topic_intent, self.mock_document)
        
        # Verify
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "fallback"
        assert response.content == "I understand this is off-topic..."
        assert len(response.suggestions) > 0
        assert response.tone == "professional"  # Low casualness level
    
    def test_coordinate_fallback_response_casual(self):
        """Test fallback response coordination for casual questions"""
        casual_intent = QuestionIntent(
            primary_intent="casual",
            confidence=0.9,
            secondary_intents=[],
            document_relevance_score=0.1,
            casualness_level=0.8,
            requires_mta_expertise=False,
            requires_fallback=False
        )
        
        # Setup mocks
        self.router.fallback_generator.create_playful_response.return_value = "That's a fun question!"
        self.router.fallback_generator.suggest_relevant_questions.return_value = ["What about the contract?"]
        
        # Execute
        response = self.router.coordinate_fallback_response("Tell me a joke!", casual_intent, self.mock_document)
        
        # Verify
        assert response.response_type == "fallback"
        assert response.content == "That's a fun question!"
        assert response.tone == "conversational"  # High casualness level
    
    def test_coordinate_fallback_response_error_handling(self):
        """Test error handling in fallback response coordination"""
        # Setup mock to raise exception
        self.router.fallback_generator.generate_off_topic_response.side_effect = Exception("Fallback error")
        
        off_topic_intent = QuestionIntent(
            primary_intent="off_topic",
            confidence=0.7,
            secondary_intents=[],
            document_relevance_score=0.1,
            casualness_level=0.3,
            requires_mta_expertise=False,
            requires_fallback=True
        )
        
        # Execute
        response = self.router.coordinate_fallback_response("Test question", off_topic_intent, self.mock_document)
        
        # Verify simple fallback response
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "simple_fallback"
        assert "need a bit more context" in response.content
    
    def test_handle_document_related_question_success(self):
        """Test handling of document-related questions"""
        # Setup mock contract engine response
        contract_response = {
            'response': 'Detailed liability analysis',
            'confidence': 0.9,
            'evidence': 'Section 5.1 states...'
        }
        self.router.contract_engine.analyze_question.return_value = contract_response
        
        # Execute
        response = self.router._handle_document_related_question(
            self.question, self.mock_document, self.mock_intent, self.mock_strategy, self.mock_context
        )
        
        # Verify
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "document_analysis"
        assert response.content == 'Detailed liability analysis'
        assert response.structured_format == contract_response
        assert "contract_analyst_engine" in response.sources
    
    def test_handle_document_related_question_no_document(self):
        """Test handling document-related question without document"""
        # Setup fallback mock
        self.router.fallback_generator.generate_off_topic_response.return_value = "No document available"
        
        # Execute
        response = self.router._handle_document_related_question(
            self.question, None, self.mock_intent, self.mock_strategy, self.mock_context
        )
        
        # Verify fallback response
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "fallback"
    
    def test_handle_general_knowledge_question(self):
        """Test handling of general knowledge questions"""
        # Setup mock
        self.router.fallback_generator.create_general_knowledge_response.return_value = "Generally, liability terms..."
        self.router.fallback_generator.suggest_relevant_questions.return_value = ["What about your contract?"]
        
        # Execute
        response = self.router._handle_general_knowledge_question(
            "What is liability?", self.mock_intent, self.mock_strategy, self.mock_document
        )
        
        # Verify
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "general_knowledge"
        assert response.content.startswith("The uploaded agreement does not cover this, but typically:")
        assert "general_legal_knowledge" in response.sources
        assert len(response.suggestions) > 0
    
    def test_handle_casual_question(self):
        """Test handling of casual questions"""
        # Setup mock
        self.router.fallback_generator.create_playful_response.return_value = "That's interesting!"
        self.router.fallback_generator.suggest_relevant_questions.return_value = ["Contract question?"]
        
        casual_strategy = ResponseStrategy(
            handler_type="casual",
            use_structured_format=False,
            include_suggestions=True,
            tone_preference="conversational",
            fallback_options=["gentle_redirection"],
            context_requirements=[]
        )
        
        # Execute
        response = self.router._handle_casual_question(
            "How's your day?", self.mock_intent, casual_strategy, self.mock_document
        )
        
        # Verify
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "casual"
        assert response.tone == "conversational"
        assert "contract" in response.content  # Should include redirection
        assert len(response.suggestions) > 0
    
    def test_enhance_with_mta_expertise(self):
        """Test MTA expertise enhancement"""
        # Create base response
        base_response = EnhancedResponse(
            content="Basic contract analysis",
            response_type="document_analysis",
            confidence=0.8,
            sources=["contract_analyst_engine"],
            suggestions=[],
            tone="professional",
            structured_format=None,
            context_used=[],
            timestamp=datetime.now()
        )
        
        # Setup MTA mocks
        mta_context = Mock(spec=MTAContext)
        mta_insight = Mock(spec=MTAInsight)
        mta_insight.concept_explanations = {"derivatives": "Materials created from original"}
        mta_insight.research_implications = ["Consider IP ownership"]
        mta_insight.suggested_questions = ["What about commercial use?"]
        
        self.router.mta_specialist.analyze_mta_context.return_value = mta_context
        self.router.mta_specialist.provide_mta_expertise.return_value = mta_insight
        
        # Execute
        enhanced_response = self.router._enhance_with_mta_expertise(
            base_response, "What about derivatives?", self.mock_document, self.mock_context
        )
        
        # Verify enhancement
        assert "MTA Context:" in enhanced_response.content
        assert "derivatives" in enhanced_response.content
        assert "Research Implications:" in enhanced_response.content
        assert "mta_specialist" in enhanced_response.sources
        assert "mta_expertise" in enhanced_response.context_used
        assert len(enhanced_response.suggestions) > 0
    
    def test_enhance_response_with_context_patterns(self):
        """Test response enhancement with context patterns"""
        # Setup base response
        base_response = EnhancedResponse(
            content="Basic response",
            response_type="document_analysis",
            confidence=0.8,
            sources=["test"],
            suggestions=[],
            tone="professional",
            structured_format=None,
            context_used=[],
            timestamp=datetime.now()
        )
        
        # Setup context manager mocks
        self.router.context_manager.detect_conversation_patterns.return_value = [
            "repetitive_questioning", "high_satisfaction"
        ]
        
        mock_flow = Mock(spec=ConversationFlow)
        mock_flow.suggested_directions = ["Explore termination clauses", "Review payment terms"]
        self.router.context_manager.analyze_conversation_flow.return_value = mock_flow
        
        # Execute
        enhanced_response = self.router._enhance_response_with_context(
            base_response, self.mock_context, self.mock_document
        )
        
        # Verify enhancements
        assert "similar questions" in enhanced_response.content  # Repetitive pattern
        assert enhanced_response.tone == "conversational"  # High satisfaction pattern
        assert len(enhanced_response.suggestions) > 0  # Flow suggestions added
        assert "conversation_patterns" in enhanced_response.context_used
    
    def test_generate_contextual_suggestions(self):
        """Test contextual suggestion generation"""
        # Setup mocks
        self.router.fallback_generator.suggest_relevant_questions.return_value = [
            "What are the key terms?", "Are there any risks?"
        ]
        
        context_suggestions = ["Explore liability provisions"]
        self.router.context_manager.suggest_context_aware_responses.return_value = context_suggestions
        
        # Setup MTA document
        mta_document = Mock(spec=Document)
        mta_document.content = "Material Transfer Agreement"
        
        mta_considerations = ["Consider IP ownership"]
        self.router.mta_specialist.analyze_mta_context.return_value = Mock()
        self.router.mta_specialist.suggest_mta_considerations.return_value = mta_considerations
        
        # Execute
        suggestions = self.router._generate_contextual_suggestions(
            "What about liability?", mta_document, self.mock_context
        )
        
        # Verify
        assert len(suggestions) > 0
        assert len(suggestions) <= 3  # Should limit suggestions
        
        # Should include base suggestions
        assert any("key terms" in suggestion for suggestion in suggestions)
        
        # Should include MTA-specific suggestions
        assert any("ip ownership" in suggestion.lower() for suggestion in suggestions)
    
    def test_is_mta_document_true(self):
        """Test MTA document detection - positive case"""
        mta_document = Mock(spec=Document)
        mta_document.content = "Material Transfer Agreement between Provider and Recipient for research use only"
        
        result = self.router._is_mta_document(mta_document)
        assert result == True
    
    def test_is_mta_document_false(self):
        """Test MTA document detection - negative case"""
        regular_document = Mock(spec=Document)
        regular_document.content = "Service Agreement for consulting services with payment terms"
        
        result = self.router._is_mta_document(regular_document)
        assert result == False
    
    def test_contains_mta_terms_true(self):
        """Test MTA terms detection - positive case"""
        mta_question = "What about derivatives and commercial use restrictions?"
        
        result = self.router._contains_mta_terms(mta_question)
        assert result == True
    
    def test_contains_mta_terms_false(self):
        """Test MTA terms detection - negative case"""
        regular_question = "What are the payment terms and delivery schedule?"
        
        result = self.router._contains_mta_terms(regular_question)
        assert result == False
    
    def test_create_error_fallback_response(self):
        """Test error fallback response creation"""
        response = self.router._create_error_fallback_response("Test question", "Test error")
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "error_fallback"
        assert "encountered an issue" in response.content
        assert "rephrasing" in response.content
        assert len(response.suggestions) > 0
        assert response.confidence == 0.3
        assert "error_handler" in response.sources
    
    def test_create_simple_fallback_response(self):
        """Test simple fallback response creation"""
        response = self.router._create_simple_fallback_response("Test question")
        
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "simple_fallback"
        assert "need a bit more context" in response.content
        assert "specific clause" in response.content
        assert len(response.suggestions) > 0
        assert response.confidence == 0.4
        assert "simple_fallback" in response.sources
    
    @patch('src.services.enhanced_response_router.logger')
    def test_comprehensive_error_handling(self, mock_logger):
        """Test comprehensive error handling throughout the router"""
        # Test various error scenarios
        error_scenarios = [
            ("context_manager.get_conversation_context", Exception("Context error")),
            ("question_classifier.classify_intent", Exception("Classification error")),
            ("contract_engine.analyze_question", Exception("Analysis error")),
            ("fallback_generator.generate_off_topic_response", Exception("Fallback error"))
        ]
        
        for method_path, error in error_scenarios:
            # Reset router
            router = EnhancedResponseRouter()
            
            # Setup error
            method_parts = method_path.split('.')
            obj = getattr(router, method_parts[0])
            setattr(obj, method_parts[1], Mock(side_effect=error))
            
            # Execute - should not raise exception
            try:
                response = router.route_question(
                    "Test question", self.document_id, self.session_id, self.mock_document
                )
                assert isinstance(response, EnhancedResponse)
            except Exception as e:
                pytest.fail(f"Router should handle {method_path} error gracefully: {e}")
    
    def test_performance_with_complex_routing(self):
        """Test performance with complex routing scenarios"""
        import time
        
        # Setup complex scenario with all features
        mta_document = Mock(spec=Document)
        mta_document.id = self.document_id
        mta_document.content = "Material Transfer Agreement" * 100  # Large content
        
        complex_context = Mock(spec=ConversationContext)
        complex_context.conversation_history = [Mock() for _ in range(50)]  # Large history
        
        # Setup mocks for performance test
        self.router.context_manager.get_conversation_context.return_value = complex_context
        self.router.question_classifier.classify_intent.return_value = self.mock_intent
        self.router.contract_engine.analyze_question.return_value = {'response': 'Test response'}
        self.router.context_manager.detect_conversation_patterns.return_value = []
        self.router.context_manager.analyze_conversation_flow.return_value = None
        
        # Measure performance
        start_time = time.time()
        
        response = self.router.route_question(
            "Complex question about derivatives and liability", 
            self.document_id, 
            self.session_id, 
            mta_document
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance and functionality
        assert processing_time < 2.0  # Should complete within 2 seconds
        assert isinstance(response, EnhancedResponse)
    
    def test_thread_safety_routing(self):
        """Test thread safety of routing operations"""
        import threading
        import time
        
        results = []
        errors = []
        
        def route_question_thread(thread_id):
            try:
                # Setup mocks for thread
                self.router.context_manager.get_conversation_context.return_value = self.mock_context
                self.router.question_classifier.classify_intent.return_value = self.mock_intent
                self.router.contract_engine.analyze_question.return_value = {'response': f'Response {thread_id}'}
                
                response = self.router.route_question(
                    f"Question from thread {thread_id}",
                    self.document_id,
                    f"session_{thread_id}",
                    self.mock_document
                )
                results.append(response)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=route_question_thread, args=(thread_id,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify results
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) == 5
        
        # All results should be valid
        for result in results:
            assert isinstance(result, EnhancedResponse)
    
    def test_integration_with_all_components(self):
        """Test integration with all router components"""
        # Setup realistic scenario
        mta_question = "What are the restrictions on derivatives in this MTA?"
        
        mta_document = Mock(spec=Document)
        mta_document.id = self.document_id
        mta_document.content = "Material Transfer Agreement with derivatives and research use only"
        
        # Setup all component mocks
        self.router.context_manager.get_conversation_context.return_value = self.mock_context
        
        mta_intent = QuestionIntent(
            primary_intent="document_related",
            confidence=0.9,
            secondary_intents=[],
            document_relevance_score=0.95,
            casualness_level=0.1,
            requires_mta_expertise=True,
            requires_fallback=False
        )
        self.router.question_classifier.classify_intent.return_value = mta_intent
        
        contract_response = {'response': 'Derivatives are restricted to research use only'}
        self.router.contract_engine.analyze_question.return_value = contract_response
        
        mta_context = Mock(spec=MTAContext)
        mta_insight = Mock(spec=MTAInsight)
        mta_insight.concept_explanations = {"derivatives": "Materials created from original"}
        mta_insight.research_implications = ["Consider IP ownership"]
        mta_insight.suggested_questions = ["What about commercial use?"]
        
        self.router.mta_specialist.analyze_mta_context.return_value = mta_context
        self.router.mta_specialist.provide_mta_expertise.return_value = mta_insight
        
        self.router.context_manager.detect_conversation_patterns.return_value = []
        self.router.context_manager.analyze_conversation_flow.return_value = None
        
        # Execute full integration
        response = self.router.route_question(
            mta_question, self.document_id, self.session_id, mta_document
        )
        
        # Verify comprehensive integration
        assert isinstance(response, EnhancedResponse)
        assert response.response_type == "document_analysis"
        assert "derivatives" in response.content.lower()
        assert "MTA Context:" in response.content
        assert "Research Implications:" in response.content
        assert "contract_analyst_engine" in response.sources
        assert "mta_specialist" in response.sources
        assert len(response.suggestions) > 0
        
        # Verify all components were called
        self.router.context_manager.get_conversation_context.assert_called_once()
        self.router.question_classifier.classify_intent.assert_called_once()
        self.router.contract_engine.analyze_question.assert_called_once()
        self.router.mta_specialist.analyze_mta_context.assert_called_once()
        self.router.mta_specialist.provide_mta_expertise.assert_called_once()
        self.router.context_manager.update_conversation_context.assert_called_once()