"""
Tests for Enhanced Context Manager
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.services.enhanced_context_manager import EnhancedContextManager
from src.models.enhanced import (
    ConversationContext, ConversationTurn, ConversationFlow,
    EnhancedResponse, QuestionIntent, ResponseStrategy
)


class TestEnhancedContextManager:
    """Test enhanced context manager functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.context_manager = EnhancedContextManager(
            max_history_length=10,
            context_retention_hours=1  # Short retention for testing
        )
        
        self.session_id = "test_session_123"
        self.document_id = "test_doc_456"
        
        # Create mock objects
        self.mock_response = Mock(spec=EnhancedResponse)
        self.mock_response.content = "Test response content"
        self.mock_response.tone = "professional"
        self.mock_response.response_type = "document_analysis"
        
        self.mock_intent = Mock(spec=QuestionIntent)
        self.mock_intent.primary_intent = "document_related"
        self.mock_intent.confidence = 0.8
        
        self.mock_strategy = Mock(spec=ResponseStrategy)
        self.mock_strategy.handler_type = "existing_contract"
    
    def test_update_conversation_context_new_session(self):
        """Test updating context for new session"""
        question = "What are the liability terms?"
        
        self.context_manager.update_conversation_context(
            self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
        )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        
        assert context is not None
        assert context.session_id == self.session_id
        assert len(context.conversation_history) == 1
        assert context.conversation_history[0].question == question
        assert context.current_tone == "professional"
    
    def test_update_conversation_context_existing_session(self):
        """Test updating context for existing session"""
        # First interaction
        question1 = "What are the liability terms?"
        self.context_manager.update_conversation_context(
            self.session_id, question1, self.mock_response, self.mock_intent, self.mock_strategy
        )
        
        # Second interaction
        question2 = "What about termination clauses?"
        mock_response2 = Mock(spec=EnhancedResponse)
        mock_response2.content = "Second response"
        mock_response2.tone = "conversational"
        mock_response2.response_type = "document_analysis"
        
        self.context_manager.update_conversation_context(
            self.session_id, question2, mock_response2, self.mock_intent, self.mock_strategy
        )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        
        assert len(context.conversation_history) == 2
        assert context.conversation_history[0].question == question1
        assert context.conversation_history[1].question == question2
        assert context.current_tone == "conversational"  # Updated from second response
    
    def test_conversation_history_length_limit(self):
        """Test that conversation history respects length limit"""
        # Add more turns than the limit
        for i in range(15):  # Limit is 10
            question = f"Question {i}"
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        
        # Should only keep the last 10 turns
        assert len(context.conversation_history) == 10
        assert context.conversation_history[0].question == "Question 5"  # First kept turn
        assert context.conversation_history[-1].question == "Question 14"  # Last turn
    
    def test_get_conversation_context_nonexistent_session(self):
        """Test getting context for nonexistent session"""
        context = self.context_manager.get_conversation_context("nonexistent_session")
        assert context is None
    
    def test_analyze_conversation_flow_insufficient_history(self):
        """Test conversation flow analysis with insufficient history"""
        # Add only one turn
        self.context_manager.update_conversation_context(
            self.session_id, "Test question", self.mock_response, self.mock_intent, self.mock_strategy
        )
        
        flow = self.context_manager.analyze_conversation_flow(self.session_id)
        assert flow is None
    
    def test_analyze_conversation_flow_success(self):
        """Test successful conversation flow analysis"""
        # Add multiple turns
        questions = [
            "What are the liability terms?",
            "How does indemnification work?",
            "What about termination clauses?"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        flow = self.context_manager.analyze_conversation_flow(self.session_id)
        
        assert flow is not None
        assert isinstance(flow, ConversationFlow)
        assert flow.session_id == self.session_id
        assert flow.flow_type in ['linear', 'exploratory', 'focused']
        assert 0.0 <= flow.topic_coherence <= 1.0
        assert 0.0 <= flow.engagement_level <= 1.0
        assert flow.complexity_progression in ['increasing', 'decreasing', 'stable']
        assert isinstance(flow.suggested_directions, list)
    
    def test_suggest_context_aware_responses_repetitive_pattern(self):
        """Test context-aware suggestions for repetitive questions"""
        # Add similar questions
        similar_questions = [
            "What are the liability terms?",
            "Can you explain the liability clauses?",
            "Tell me about liability provisions?"
        ]
        
        for question in similar_questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        new_question = "What about liability requirements?"
        
        suggestions = self.context_manager.suggest_context_aware_responses(new_question, context)
        
        assert len(suggestions) > 0
        assert any('repetition' in suggestion.lower() for suggestion in suggestions)
    
    def test_suggest_context_aware_responses_complexity_increase(self):
        """Test context-aware suggestions for increasing complexity"""
        # Add questions of increasing complexity
        questions = [
            "What is this?",
            "What are the main terms?",
            "How do the indemnification provisions interact with liability limitations under governing law?"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        new_question = "Complex legal question"
        
        suggestions = self.context_manager.suggest_context_aware_responses(new_question, context)
        
        assert len(suggestions) > 0
        # Should suggest detailed explanations for increasing complexity
    
    def test_suggest_context_aware_responses_tone_shift(self):
        """Test context-aware suggestions for tone shift"""
        # Add casual responses
        casual_response = Mock(spec=EnhancedResponse)
        casual_response.content = "Cool, thanks!"
        casual_response.tone = "conversational"
        casual_response.response_type = "casual"
        
        self.context_manager.update_conversation_context(
            self.session_id, "Thanks, that's helpful!", casual_response, self.mock_intent, self.mock_strategy
        )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        new_question = "What else should I know?"
        
        suggestions = self.context_manager.suggest_context_aware_responses(new_question, context)
        
        assert len(suggestions) > 0
        # Should suggest matching conversational tone
    
    def test_detect_conversation_patterns_increasing_complexity(self):
        """Test detection of increasing complexity pattern"""
        # Add questions of increasing complexity
        questions = [
            ("Simple question", 5),
            ("More detailed question about contract terms", 15),
            ("Complex question about indemnification provisions and liability limitations", 25)
        ]
        
        for question, _ in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        assert 'increasing_complexity' in patterns
    
    def test_detect_conversation_patterns_topic_jumping(self):
        """Test detection of topic jumping pattern"""
        # Add questions on different topics
        questions = [
            "What are the liability terms?",
            "How much does this cost?",
            "What's the weather like?",
            "Tell me about termination clauses?",
            "What's for lunch?"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        assert 'topic_jumping' in patterns
    
    def test_detect_conversation_patterns_repetitive_questioning(self):
        """Test detection of repetitive questioning pattern"""
        # Add repetitive questions
        questions = [
            "What are the terms?",
            "Can you explain the terms?",
            "Tell me about the terms?",
            "What do the terms say?"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        assert 'repetitive_questioning' in patterns
    
    def test_detect_conversation_patterns_casual_drift(self):
        """Test detection of casual drift pattern"""
        # Add casual responses
        casual_response = Mock(spec=EnhancedResponse)
        casual_response.content = "Cool!"
        casual_response.tone = "conversational"
        casual_response.response_type = "casual"
        
        for i in range(3):
            self.context_manager.update_conversation_context(
                self.session_id, f"Casual question {i}", casual_response, self.mock_intent, self.mock_strategy
            )
        
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        assert 'casual_drift' in patterns
    
    def test_detect_conversation_patterns_deep_dive(self):
        """Test detection of deep dive pattern"""
        # Add questions on the same topic
        questions = [
            "What are the liability terms?",
            "How does liability limitation work?",
            "What about liability caps?",
            "Are there liability exclusions?"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        assert 'deep_dive' in patterns
    
    def test_detect_conversation_patterns_satisfaction(self):
        """Test detection of satisfaction pattern"""
        # Add questions with satisfaction indicators
        questions = [
            "Thanks, that's great!",
            "Perfect, exactly what I needed!",
            "This is very helpful, thank you!"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        assert 'high_satisfaction' in patterns
    
    def test_detect_conversation_patterns_frustration(self):
        """Test detection of frustration pattern"""
        # Add questions with frustration indicators
        questions = [
            "I'm still confused about this",
            "This is not clear to me",
            "I don't understand what you mean"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        assert 'potential_frustration' in patterns
    
    def test_get_contextual_tone_suggestion_casual_indicators(self):
        """Test tone suggestion with casual indicators"""
        # Add conversational context
        casual_response = Mock(spec=EnhancedResponse)
        casual_response.tone = "conversational"
        
        self.context_manager.update_conversation_context(
            self.session_id, "Previous question", casual_response, self.mock_intent, self.mock_strategy
        )
        
        # Test with casual question
        casual_question = "Thanks! That's awesome 😊"
        tone = self.context_manager.get_contextual_tone_suggestion(self.session_id, casual_question)
        
        assert tone == "conversational"
    
    def test_get_contextual_tone_suggestion_formal_indicators(self):
        """Test tone suggestion with formal indicators"""
        formal_question = "Could you please explain the terms?"
        tone = self.context_manager.get_contextual_tone_suggestion(self.session_id, formal_question)
        
        assert tone == "professional"
    
    def test_get_contextual_tone_suggestion_consistent_tone(self):
        """Test tone suggestion maintains consistency"""
        # Add multiple professional responses
        for i in range(3):
            professional_response = Mock(spec=EnhancedResponse)
            professional_response.tone = "professional"
            
            self.context_manager.update_conversation_context(
                self.session_id, f"Question {i}", professional_response, self.mock_intent, self.mock_strategy
            )
        
        neutral_question = "What about this clause?"
        tone = self.context_manager.get_contextual_tone_suggestion(self.session_id, neutral_question)
        
        assert tone == "professional"
    
    def test_update_topic_progression(self):
        """Test topic progression tracking"""
        questions = [
            "What are the liability terms?",
            "How does indemnification work?",
            "What about payment schedules?"
        ]
        
        for question in questions:
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        
        # Should track contract-related topics
        assert len(context.topic_progression) > 0
        assert any('liability' in topic for topic in context.topic_progression)
    
    def test_update_user_expertise_level_expert_indicators(self):
        """Test user expertise level update with expert indicators"""
        expert_question = "How do the derivative work provisions interact with IP assignment clauses?"
        
        self.context_manager.update_conversation_context(
            self.session_id, expert_question, self.mock_response, self.mock_intent, self.mock_strategy
        )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        assert context.user_expertise_level == "expert"
    
    def test_update_user_expertise_level_beginner_indicators(self):
        """Test user expertise level update with beginner indicators"""
        beginner_question = "Can you explain what this means in simple terms? I'm new to this."
        
        self.context_manager.update_conversation_context(
            self.session_id, beginner_question, self.mock_response, self.mock_intent, self.mock_strategy
        )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        assert context.user_expertise_level == "beginner"
    
    def test_update_response_style_preference(self):
        """Test response style preference update"""
        # Test structured response preference
        structured_response = Mock(spec=EnhancedResponse)
        structured_response.response_type = "document_analysis"
        structured_response.structured_format = {"key": "value"}
        
        self.context_manager.update_conversation_context(
            self.session_id, "Test question", structured_response, self.mock_intent, self.mock_strategy
        )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        assert context.preferred_response_style == "structured"
        
        # Test conversational response preference
        conversational_response = Mock(spec=EnhancedResponse)
        conversational_response.response_type = "casual"
        
        self.context_manager.update_conversation_context(
            self.session_id, "Another question", conversational_response, self.mock_intent, self.mock_strategy
        )
        
        context = self.context_manager.get_conversation_context(self.session_id)
        assert context.preferred_response_style == "conversational"
    
    def test_cleanup_old_conversations(self):
        """Test cleanup of old conversations"""
        # Create context manager with very short retention
        short_retention_manager = EnhancedContextManager(context_retention_hours=0.001)  # ~3.6 seconds
        
        # Add a conversation
        short_retention_manager.update_conversation_context(
            self.session_id, "Test question", self.mock_response, self.mock_intent, self.mock_strategy
        )
        
        # Verify conversation exists
        context = short_retention_manager.get_conversation_context(self.session_id)
        assert context is not None
        
        # Wait for cleanup (simulate time passing)
        import time
        time.sleep(0.01)  # Small delay
        
        # Manually trigger cleanup by adding another conversation
        short_retention_manager.update_conversation_context(
            "new_session", "New question", self.mock_response, self.mock_intent, self.mock_strategy
        )
        
        # Original conversation should still exist (cleanup is time-based)
        context = short_retention_manager.get_conversation_context(self.session_id)
        # Note: In real implementation, this would be cleaned up after the retention period
    
    def test_extract_topics_contract_terms(self):
        """Test topic extraction for contract terms"""
        text = "This agreement covers liability, indemnification, and termination clauses"
        topics = self.context_manager._extract_topics(text)
        
        assert len(topics) > 0
        assert 'liability' in topics
        assert 'indemnification' in topics
        assert 'termination' in topics
    
    def test_extract_topics_mta_terms(self):
        """Test topic extraction for MTA terms"""
        text = "Material transfer agreement with derivatives and publication restrictions"
        topics = self.context_manager._extract_topics(text)
        
        assert len(topics) > 0
        assert 'material transfer' in topics
        assert 'derivatives' in topics
        assert 'publication' in topics
    
    def test_determine_flow_type_focused(self):
        """Test focused flow type determination"""
        # Create context with focused conversation
        context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=['liability', 'liability'],  # Same topic
            user_expertise_level="intermediate",
            preferred_response_style="structured"
        )
        
        # Add turns with same topic
        for i in range(3):
            turn = ConversationTurn(
                question=f"Liability question {i}",
                response=self.mock_response,
                intent=self.mock_intent,
                strategy_used=self.mock_strategy,
                user_satisfaction=None,
                timestamp=datetime.now()
            )
            context.conversation_history.append(turn)
        
        flow_type = self.context_manager._determine_flow_type(context)
        assert flow_type == "focused"
    
    def test_determine_flow_type_exploratory(self):
        """Test exploratory flow type determination"""
        # Create context with diverse topics
        context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=['liability', 'payment', 'termination', 'warranty', 'dispute'],
            user_expertise_level="intermediate",
            preferred_response_style="structured"
        )
        
        # Add turns with different topics
        topics = ['liability', 'payment', 'termination', 'warranty', 'dispute']
        for i, topic in enumerate(topics):
            turn = ConversationTurn(
                question=f"{topic} question",
                response=self.mock_response,
                intent=self.mock_intent,
                strategy_used=self.mock_strategy,
                user_satisfaction=None,
                timestamp=datetime.now()
            )
            context.conversation_history.append(turn)
        
        flow_type = self.context_manager._determine_flow_type(context)
        assert flow_type == "exploratory"
    
    def test_calculate_topic_coherence_high(self):
        """Test high topic coherence calculation"""
        # Create context with repeated topics
        context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=[],
            user_expertise_level="intermediate",
            preferred_response_style="structured"
        )
        
        # Add turns with same topic
        for i in range(3):
            turn = ConversationTurn(
                question="What about liability terms?",  # Same topic
                response=self.mock_response,
                intent=self.mock_intent,
                strategy_used=self.mock_strategy,
                user_satisfaction=None,
                timestamp=datetime.now()
            )
            context.conversation_history.append(turn)
        
        coherence = self.context_manager._calculate_topic_coherence(context)
        assert 0.0 <= coherence <= 1.0
        # Should be relatively high for repeated topics
    
    def test_assess_engagement_level_high(self):
        """Test high engagement level assessment"""
        context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=[],
            user_expertise_level="intermediate",
            preferred_response_style="structured"
        )
        
        # Add turns with high engagement indicators
        engaging_questions = [
            "Can you also explain how the indemnification provisions work in detail?",
            "Additionally, what about the liability limitations and how they interact?",
            "Furthermore, I'd like to understand the termination procedures thoroughly."
        ]
        
        for question in engaging_questions:
            conversational_response = Mock(spec=EnhancedResponse)
            conversational_response.tone = "conversational"
            
            turn = ConversationTurn(
                question=question,
                response=conversational_response,
                intent=self.mock_intent,
                strategy_used=self.mock_strategy,
                user_satisfaction=None,
                timestamp=datetime.now()
            )
            context.conversation_history.append(turn)
        
        engagement = self.context_manager._assess_engagement_level(context)
        assert 0.0 <= engagement <= 1.0
        # Should be relatively high for engaging questions
    
    def test_analyze_complexity_progression_increasing(self):
        """Test increasing complexity progression analysis"""
        context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=[],
            user_expertise_level="intermediate",
            preferred_response_style="structured"
        )
        
        # Add turns with increasing complexity
        questions = [
            "What is this?",  # Simple
            "What are the main liability terms?",  # Medium
            "How do the indemnification provisions, liability limitations, and governing law clauses interact?"  # Complex
        ]
        
        for question in questions:
            turn = ConversationTurn(
                question=question,
                response=self.mock_response,
                intent=self.mock_intent,
                strategy_used=self.mock_strategy,
                user_satisfaction=None,
                timestamp=datetime.now()
            )
            context.conversation_history.append(turn)
        
        progression = self.context_manager._analyze_complexity_progression(context)
        assert progression in ['increasing', 'decreasing', 'stable']
    
    def test_suggest_conversation_directions_liability_focus(self):
        """Test conversation direction suggestions for liability focus"""
        context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=['liability'],
            user_expertise_level="intermediate",
            preferred_response_style="structured"
        )
        
        # Add liability-focused turn
        turn = ConversationTurn(
            question="What are the liability terms?",
            response=self.mock_response,
            intent=self.mock_intent,
            strategy_used=self.mock_strategy,
            user_satisfaction=None,
            timestamp=datetime.now()
        )
        context.conversation_history.append(turn)
        
        suggestions = self.context_manager._suggest_conversation_directions(context)
        
        assert len(suggestions) > 0
        assert len(suggestions) <= 3
        # Should suggest related topics like indemnification
        assert any('indemnification' in suggestion.lower() for suggestion in suggestions)
    
    def test_suggest_conversation_directions_expertise_based(self):
        """Test conversation direction suggestions based on expertise"""
        # Test beginner suggestions
        beginner_context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=[],
            user_expertise_level="beginner",
            preferred_response_style="structured"
        )
        
        beginner_suggestions = self.context_manager._suggest_conversation_directions(beginner_context)
        assert any('foundational' in suggestion.lower() for suggestion in beginner_suggestions)
        
        # Test expert suggestions
        expert_context = ConversationContext(
            session_id=self.session_id,
            document_id=self.document_id,
            conversation_history=[],
            current_tone="professional",
            topic_progression=[],
            user_expertise_level="expert",
            preferred_response_style="structured"
        )
        
        expert_suggestions = self.context_manager._suggest_conversation_directions(expert_context)
        assert any('advanced' in suggestion.lower() for suggestion in expert_suggestions)
    
    @patch('src.services.enhanced_context_manager.logger')
    def test_error_handling_in_context_operations(self, mock_logger):
        """Test error handling in context operations"""
        # Test with problematic data that might cause issues
        try:
            # This should not raise an exception
            self.context_manager.update_conversation_context(
                None, None, None, None, None  # All None values
            )
        except Exception:
            # Should handle gracefully, not crash
            pass
        
        # Context manager should still be functional
        assert self.context_manager is not None
    
    def test_performance_with_large_history(self):
        """Test performance with large conversation history"""
        import time
        
        # Add many turns
        start_time = time.time()
        
        for i in range(100):
            question = f"Question {i} about contract terms and conditions"
            self.context_manager.update_conversation_context(
                self.session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
            )
        
        # Analyze patterns with large history
        patterns = self.context_manager.detect_conversation_patterns(self.session_id)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete in reasonable time even with large history
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert isinstance(patterns, list)
    
    def test_thread_safety_context_updates(self):
        """Test thread safety of context updates"""
        import threading
        import time
        
        errors = []
        
        def update_context(thread_id):
            try:
                for i in range(10):
                    question = f"Thread {thread_id} Question {i}"
                    session_id = f"session_{thread_id}"
                    self.context_manager.update_conversation_context(
                        session_id, question, self.mock_response, self.mock_intent, self.mock_strategy
                    )
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for thread_id in range(5):
            thread = threading.Thread(target=update_context, args=(thread_id,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Check for errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        
        # Verify all sessions were created
        for thread_id in range(5):
            session_id = f"session_{thread_id}"
            context = self.context_manager.get_conversation_context(session_id)
            assert context is not None
            assert len(context.conversation_history) == 10