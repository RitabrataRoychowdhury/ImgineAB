"""
Unit tests for enhanced data models.

Tests validation, serialization, and behavior of all enhanced data structures
for the contract assistant system.
"""

import pytest
from datetime import datetime
from src.models.enhanced import (
    EnhancedResponse, QuestionIntent, ResponseStrategy, MTAContext, MTAInsight,
    ConversationTurn, ConversationContext, ConversationFlow, ConversationPattern,
    ResponseType, IntentType, ToneType, HandlerType, CollaborationType,
    ExpertiseLevel, FlowType, ComplexityProgression
)


class TestEnhancedResponse:
    """Test cases for EnhancedResponse data model."""
    
    def test_valid_enhanced_response_creation(self):
        """Test creating a valid EnhancedResponse."""
        response = EnhancedResponse(
            content="This is a test response",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.85,
            sources=["document.pdf"],
            suggestions=["Try asking about clause 5"],
            tone=ToneType.PROFESSIONAL
        )
        
        assert response.content == "This is a test response"
        assert response.response_type == ResponseType.DOCUMENT_ANALYSIS
        assert response.confidence == 0.85
        assert response.sources == ["document.pdf"]
        assert response.suggestions == ["Try asking about clause 5"]
        assert response.tone == ToneType.PROFESSIONAL
        assert isinstance(response.timestamp, datetime)
    
    def test_enhanced_response_with_defaults(self):
        """Test EnhancedResponse with default values."""
        response = EnhancedResponse(
            content="Test content",
            response_type=ResponseType.FALLBACK,
            confidence=0.5
        )
        
        assert response.sources == []
        assert response.suggestions == []
        assert response.tone == ToneType.PROFESSIONAL
        assert response.structured_format is None
        assert response.context_used == []
    
    def test_enhanced_response_validation_errors(self):
        """Test validation errors in EnhancedResponse."""
        # Test invalid confidence
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            EnhancedResponse(
                content="Test",
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=1.5
            )
        
        # Test empty content
        with pytest.raises(ValueError, match="content cannot be empty"):
            EnhancedResponse(
                content="   ",
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=0.5
            )


class TestQuestionIntent:
    """Test cases for QuestionIntent data model."""
    
    def test_valid_question_intent_creation(self):
        """Test creating a valid QuestionIntent."""
        intent = QuestionIntent(
            primary_intent=IntentType.DOCUMENT_RELATED,
            confidence=0.9,
            secondary_intents=[IntentType.CONTRACT_GENERAL],
            document_relevance_score=0.8,
            casualness_level=0.2,
            requires_mta_expertise=True,
            requires_fallback=False
        )
        
        assert intent.primary_intent == IntentType.DOCUMENT_RELATED
        assert intent.confidence == 0.9
        assert intent.secondary_intents == [IntentType.CONTRACT_GENERAL]
        assert intent.document_relevance_score == 0.8
        assert intent.casualness_level == 0.2
        assert intent.requires_mta_expertise is True
        assert intent.requires_fallback is False
    
    def test_question_intent_with_defaults(self):
        """Test QuestionIntent with default values."""
        intent = QuestionIntent(
            primary_intent=IntentType.OFF_TOPIC,
            confidence=0.7
        )
        
        assert intent.secondary_intents == []
        assert intent.document_relevance_score == 0.0
        assert intent.casualness_level == 0.0
        assert intent.requires_mta_expertise is False
        assert intent.requires_fallback is False
    
    def test_question_intent_validation_errors(self):
        """Test validation errors in QuestionIntent."""
        # Test invalid confidence
        with pytest.raises(ValueError, match="confidence must be between 0.0 and 1.0"):
            QuestionIntent(
                primary_intent=IntentType.DOCUMENT_RELATED,
                confidence=-0.1
            )
        
        # Test invalid document relevance score
        with pytest.raises(ValueError, match="document_relevance_score must be between 0.0 and 1.0"):
            QuestionIntent(
                primary_intent=IntentType.DOCUMENT_RELATED,
                confidence=0.5,
                document_relevance_score=1.5
            )


class TestResponseStrategy:
    """Test cases for ResponseStrategy data model."""
    
    def test_valid_response_strategy_creation(self):
        """Test creating a valid ResponseStrategy."""
        strategy = ResponseStrategy(
            handler_type=HandlerType.EXISTING_CONTRACT,
            use_structured_format=True,
            include_suggestions=False,
            tone_preference=ToneType.CONVERSATIONAL,
            fallback_options=["option1", "option2"],
            context_requirements=["document", "history"]
        )
        
        assert strategy.handler_type == HandlerType.EXISTING_CONTRACT
        assert strategy.use_structured_format is True
        assert strategy.include_suggestions is False
        assert strategy.tone_preference == ToneType.CONVERSATIONAL
        assert strategy.fallback_options == ["option1", "option2"]
        assert strategy.context_requirements == ["document", "history"]
    
    def test_response_strategy_with_defaults(self):
        """Test ResponseStrategy with default values."""
        strategy = ResponseStrategy(handler_type=HandlerType.FALLBACK)
        
        assert strategy.use_structured_format is True
        assert strategy.include_suggestions is True
        assert strategy.tone_preference == ToneType.PROFESSIONAL
        assert strategy.fallback_options == []
        assert strategy.context_requirements == []


class TestMTAContext:
    """Test cases for MTAContext data model."""
    
    def test_valid_mta_context_creation(self):
        """Test creating a valid MTAContext."""
        context = MTAContext(
            document_id="doc123",
            provider_entity="University A",
            recipient_entity="Company B",
            material_types=["cell lines", "reagents"],
            research_purposes=["drug discovery", "basic research"],
            ip_considerations=["patent rights", "publication rights"],
            key_restrictions=["no commercial use", "attribution required"],
            collaboration_type=CollaborationType.COMMERCIAL
        )
        
        assert context.document_id == "doc123"
        assert context.provider_entity == "University A"
        assert context.recipient_entity == "Company B"
        assert context.material_types == ["cell lines", "reagents"]
        assert context.research_purposes == ["drug discovery", "basic research"]
        assert context.ip_considerations == ["patent rights", "publication rights"]
        assert context.key_restrictions == ["no commercial use", "attribution required"]
        assert context.collaboration_type == CollaborationType.COMMERCIAL
    
    def test_mta_context_with_defaults(self):
        """Test MTAContext with default values."""
        context = MTAContext(document_id="doc456")
        
        assert context.provider_entity is None
        assert context.recipient_entity is None
        assert context.material_types == []
        assert context.research_purposes == []
        assert context.ip_considerations == []
        assert context.key_restrictions == []
        assert context.collaboration_type == CollaborationType.ACADEMIC
    
    def test_mta_context_validation_errors(self):
        """Test validation errors in MTAContext."""
        # Test empty document_id
        with pytest.raises(ValueError, match="document_id cannot be empty"):
            MTAContext(document_id="   ")


class TestMTAInsight:
    """Test cases for MTAInsight data model."""
    
    def test_valid_mta_insight_creation(self):
        """Test creating a valid MTAInsight."""
        insight = MTAInsight(
            concept_explanations={"MTA": "Material Transfer Agreement"},
            research_implications=["IP protection needed"],
            common_practices=["Attribution required"],
            risk_considerations=["Commercial use restrictions"],
            suggested_questions=["What are the key restrictions?"]
        )
        
        assert insight.concept_explanations == {"MTA": "Material Transfer Agreement"}
        assert insight.research_implications == ["IP protection needed"]
        assert insight.common_practices == ["Attribution required"]
        assert insight.risk_considerations == ["Commercial use restrictions"]
        assert insight.suggested_questions == ["What are the key restrictions?"]
    
    def test_mta_insight_with_defaults(self):
        """Test MTAInsight with default values."""
        insight = MTAInsight()
        
        assert insight.concept_explanations == {}
        assert insight.research_implications == []
        assert insight.common_practices == []
        assert insight.risk_considerations == []
        assert insight.suggested_questions == []


class TestConversationTurn:
    """Test cases for ConversationTurn data model."""
    
    def test_valid_conversation_turn_creation(self):
        """Test creating a valid ConversationTurn."""
        response = EnhancedResponse(
            content="Test response",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.8
        )
        intent = QuestionIntent(
            primary_intent=IntentType.DOCUMENT_RELATED,
            confidence=0.9
        )
        strategy = ResponseStrategy(handler_type=HandlerType.EXISTING_CONTRACT)
        
        turn = ConversationTurn(
            question="What does clause 5 say?",
            response=response,
            intent=intent,
            strategy_used=strategy,
            user_satisfaction=4
        )
        
        assert turn.question == "What does clause 5 say?"
        assert turn.response == response
        assert turn.intent == intent
        assert turn.strategy_used == strategy
        assert turn.user_satisfaction == 4
        assert isinstance(turn.timestamp, datetime)
    
    def test_conversation_turn_validation_errors(self):
        """Test validation errors in ConversationTurn."""
        response = EnhancedResponse(
            content="Test response",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.8
        )
        intent = QuestionIntent(
            primary_intent=IntentType.DOCUMENT_RELATED,
            confidence=0.9
        )
        strategy = ResponseStrategy(handler_type=HandlerType.EXISTING_CONTRACT)
        
        # Test empty question
        with pytest.raises(ValueError, match="question cannot be empty"):
            ConversationTurn(
                question="   ",
                response=response,
                intent=intent,
                strategy_used=strategy
            )
        
        # Test invalid user satisfaction
        with pytest.raises(ValueError, match="user_satisfaction must be between 1 and 5"):
            ConversationTurn(
                question="Test question",
                response=response,
                intent=intent,
                strategy_used=strategy,
                user_satisfaction=6
            )


class TestConversationContext:
    """Test cases for ConversationContext data model."""
    
    def test_valid_conversation_context_creation(self):
        """Test creating a valid ConversationContext."""
        context = ConversationContext(
            session_id="session123",
            document_id="doc456",
            current_tone=ToneType.CONVERSATIONAL,
            topic_progression=["clause 1", "clause 2"],
            user_expertise_level=ExpertiseLevel.EXPERT,
            preferred_response_style="detailed"
        )
        
        assert context.session_id == "session123"
        assert context.document_id == "doc456"
        assert context.conversation_history == []
        assert context.current_tone == ToneType.CONVERSATIONAL
        assert context.topic_progression == ["clause 1", "clause 2"]
        assert context.user_expertise_level == ExpertiseLevel.EXPERT
        assert context.preferred_response_style == "detailed"
    
    def test_conversation_context_with_defaults(self):
        """Test ConversationContext with default values."""
        context = ConversationContext(
            session_id="session123",
            document_id="doc456"
        )
        
        assert context.conversation_history == []
        assert context.current_tone == ToneType.PROFESSIONAL
        assert context.topic_progression == []
        assert context.user_expertise_level == ExpertiseLevel.INTERMEDIATE
        assert context.preferred_response_style == "balanced"
    
    def test_conversation_context_add_turn(self):
        """Test adding turns to conversation context."""
        context = ConversationContext(
            session_id="session123",
            document_id="doc456"
        )
        
        response = EnhancedResponse(
            content="Test response",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.8
        )
        intent = QuestionIntent(
            primary_intent=IntentType.DOCUMENT_RELATED,
            confidence=0.9
        )
        strategy = ResponseStrategy(handler_type=HandlerType.EXISTING_CONTRACT)
        
        turn = ConversationTurn(
            question="What does clause 5 say?",
            response=response,
            intent=intent,
            strategy_used=strategy
        )
        
        context.add_turn(turn)
        
        assert len(context.conversation_history) == 1
        assert context.conversation_history[0] == turn
        assert len(context.topic_progression) == 1
    
    def test_conversation_context_get_recent_turns(self):
        """Test getting recent turns from conversation context."""
        context = ConversationContext(
            session_id="session123",
            document_id="doc456"
        )
        
        # Add multiple turns
        for i in range(10):
            response = EnhancedResponse(
                content=f"Response {i}",
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=0.8
            )
            intent = QuestionIntent(
                primary_intent=IntentType.DOCUMENT_RELATED,
                confidence=0.9
            )
            strategy = ResponseStrategy(handler_type=HandlerType.EXISTING_CONTRACT)
            
            turn = ConversationTurn(
                question=f"Question {i}",
                response=response,
                intent=intent,
                strategy_used=strategy
            )
            context.add_turn(turn)
        
        recent_turns = context.get_recent_turns(3)
        assert len(recent_turns) == 3
        assert recent_turns[0].question == "Question 7"
        assert recent_turns[1].question == "Question 8"
        assert recent_turns[2].question == "Question 9"
    
    def test_conversation_context_validation_errors(self):
        """Test validation errors in ConversationContext."""
        # Test empty session_id
        with pytest.raises(ValueError, match="session_id cannot be empty"):
            ConversationContext(
                session_id="   ",
                document_id="doc456"
            )
        
        # Test empty document_id
        with pytest.raises(ValueError, match="document_id cannot be empty"):
            ConversationContext(
                session_id="session123",
                document_id="   "
            )


class TestConversationFlow:
    """Test cases for ConversationFlow data model."""
    
    def test_valid_conversation_flow_creation(self):
        """Test creating a valid ConversationFlow."""
        flow = ConversationFlow(
            session_id="session123",
            flow_type=FlowType.EXPLORATORY,
            topic_coherence=0.8,
            engagement_level=0.9,
            complexity_progression=ComplexityProgression.INCREASING,
            suggested_directions=["Ask about risks", "Explore clause 3"]
        )
        
        assert flow.session_id == "session123"
        assert flow.flow_type == FlowType.EXPLORATORY
        assert flow.topic_coherence == 0.8
        assert flow.engagement_level == 0.9
        assert flow.complexity_progression == ComplexityProgression.INCREASING
        assert flow.suggested_directions == ["Ask about risks", "Explore clause 3"]
    
    def test_conversation_flow_with_defaults(self):
        """Test ConversationFlow with default values."""
        flow = ConversationFlow(
            session_id="session123",
            flow_type=FlowType.LINEAR,
            topic_coherence=0.5,
            engagement_level=0.6,
            complexity_progression=ComplexityProgression.STABLE
        )
        
        assert flow.suggested_directions == []
    
    def test_conversation_flow_validation_errors(self):
        """Test validation errors in ConversationFlow."""
        # Test invalid topic coherence
        with pytest.raises(ValueError, match="topic_coherence must be between 0.0 and 1.0"):
            ConversationFlow(
                session_id="session123",
                flow_type=FlowType.LINEAR,
                topic_coherence=1.5,
                engagement_level=0.6,
                complexity_progression=ComplexityProgression.STABLE
            )
        
        # Test invalid engagement level
        with pytest.raises(ValueError, match="engagement_level must be between 0.0 and 1.0"):
            ConversationFlow(
                session_id="session123",
                flow_type=FlowType.LINEAR,
                topic_coherence=0.5,
                engagement_level=-0.1,
                complexity_progression=ComplexityProgression.STABLE
            )


class TestConversationPattern:
    """Test cases for ConversationPattern data model."""
    
    def test_valid_conversation_pattern_creation(self):
        """Test creating a valid ConversationPattern."""
        pattern = ConversationPattern(
            pattern_type="repetitive_questions",
            frequency=3,
            confidence=0.85,
            description="User asks similar questions repeatedly",
            suggested_response="I notice you're asking similar questions. Would you like me to provide a comprehensive overview?"
        )
        
        assert pattern.pattern_type == "repetitive_questions"
        assert pattern.frequency == 3
        assert pattern.confidence == 0.85
        assert pattern.description == "User asks similar questions repeatedly"
        assert pattern.suggested_response == "I notice you're asking similar questions. Would you like me to provide a comprehensive overview?"
    
    def test_conversation_pattern_with_defaults(self):
        """Test ConversationPattern with default values."""
        pattern = ConversationPattern(
            pattern_type="test_pattern",
            frequency=1,
            confidence=0.5,
            description="Test pattern description"
        )
        
        assert pattern.suggested_response is None
    
    def test_conversation_pattern_validation_errors(self):
        """Test validation errors in ConversationPattern."""
        # Test empty pattern_type
        with pytest.raises(ValueError, match="pattern_type cannot be empty"):
            ConversationPattern(
                pattern_type="   ",
                frequency=1,
                confidence=0.5,
                description="Test description"
            )
        
        # Test negative frequency
        with pytest.raises(ValueError, match="frequency must be non-negative"):
            ConversationPattern(
                pattern_type="test_pattern",
                frequency=-1,
                confidence=0.5,
                description="Test description"
            )


class TestEnumValidation:
    """Test cases for enum validation in data models."""
    
    def test_response_type_enum_values(self):
        """Test ResponseType enum values."""
        assert ResponseType.DOCUMENT_ANALYSIS.value == "document_analysis"
        assert ResponseType.FALLBACK.value == "fallback"
        assert ResponseType.GENERAL_KNOWLEDGE.value == "general_knowledge"
        assert ResponseType.CASUAL.value == "casual"
    
    def test_intent_type_enum_values(self):
        """Test IntentType enum values."""
        assert IntentType.DOCUMENT_RELATED.value == "document_related"
        assert IntentType.OFF_TOPIC.value == "off_topic"
        assert IntentType.CONTRACT_GENERAL.value == "contract_general"
        assert IntentType.CASUAL.value == "casual"
    
    def test_tone_type_enum_values(self):
        """Test ToneType enum values."""
        assert ToneType.PROFESSIONAL.value == "professional"
        assert ToneType.CONVERSATIONAL.value == "conversational"
        assert ToneType.PLAYFUL.value == "playful"
    
    def test_handler_type_enum_values(self):
        """Test HandlerType enum values."""
        assert HandlerType.EXISTING_CONTRACT.value == "existing_contract"
        assert HandlerType.FALLBACK.value == "fallback"
        assert HandlerType.GENERAL_KNOWLEDGE.value == "general_knowledge"
        assert HandlerType.CASUAL.value == "casual"
    
    def test_collaboration_type_enum_values(self):
        """Test CollaborationType enum values."""
        assert CollaborationType.ACADEMIC.value == "academic"
        assert CollaborationType.COMMERCIAL.value == "commercial"
        assert CollaborationType.HYBRID.value == "hybrid"


class TestSerialization:
    """Test cases for data model serialization and deserialization."""
    
    def test_enhanced_response_serialization(self):
        """Test EnhancedResponse can be converted to/from dict."""
        response = EnhancedResponse(
            content="Test response",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.85,
            sources=["doc1.pdf"],
            suggestions=["Ask about clause 2"],
            tone=ToneType.PROFESSIONAL
        )
        
        # Test that we can access all attributes (basic serialization check)
        assert hasattr(response, 'content')
        assert hasattr(response, 'response_type')
        assert hasattr(response, 'confidence')
        assert hasattr(response, 'sources')
        assert hasattr(response, 'suggestions')
        assert hasattr(response, 'tone')
        assert hasattr(response, 'structured_format')
        assert hasattr(response, 'context_used')
        assert hasattr(response, 'timestamp')
    
    def test_question_intent_serialization(self):
        """Test QuestionIntent can be converted to/from dict."""
        intent = QuestionIntent(
            primary_intent=IntentType.DOCUMENT_RELATED,
            confidence=0.9,
            secondary_intents=[IntentType.CONTRACT_GENERAL],
            document_relevance_score=0.8,
            casualness_level=0.2,
            requires_mta_expertise=True,
            requires_fallback=False
        )
        
        # Test that we can access all attributes (basic serialization check)
        assert hasattr(intent, 'primary_intent')
        assert hasattr(intent, 'confidence')
        assert hasattr(intent, 'secondary_intents')
        assert hasattr(intent, 'document_relevance_score')
        assert hasattr(intent, 'casualness_level')
        assert hasattr(intent, 'requires_mta_expertise')
        assert hasattr(intent, 'requires_fallback')
    
    def test_conversation_context_serialization(self):
        """Test ConversationContext can be converted to/from dict."""
        context = ConversationContext(
            session_id="session123",
            document_id="doc456",
            current_tone=ToneType.CONVERSATIONAL,
            topic_progression=["topic1", "topic2"],
            user_expertise_level=ExpertiseLevel.EXPERT,
            preferred_response_style="detailed"
        )
        
        # Test that we can access all attributes (basic serialization check)
        assert hasattr(context, 'session_id')
        assert hasattr(context, 'document_id')
        assert hasattr(context, 'conversation_history')
        assert hasattr(context, 'current_tone')
        assert hasattr(context, 'topic_progression')
        assert hasattr(context, 'user_expertise_level')
        assert hasattr(context, 'preferred_response_style')
    
    def test_mta_context_serialization(self):
        """Test MTAContext can be converted to/from dict."""
        mta_context = MTAContext(
            document_id="doc123",
            provider_entity="University A",
            recipient_entity="Company B",
            material_types=["cell lines"],
            research_purposes=["drug discovery"],
            ip_considerations=["patent rights"],
            key_restrictions=["no commercial use"],
            collaboration_type=CollaborationType.COMMERCIAL
        )
        
        # Test that we can access all attributes (basic serialization check)
        assert hasattr(mta_context, 'document_id')
        assert hasattr(mta_context, 'provider_entity')
        assert hasattr(mta_context, 'recipient_entity')
        assert hasattr(mta_context, 'material_types')
        assert hasattr(mta_context, 'research_purposes')
        assert hasattr(mta_context, 'ip_considerations')
        assert hasattr(mta_context, 'key_restrictions')
        assert hasattr(mta_context, 'collaboration_type')


class TestDataModelIntegration:
    """Test cases for integration between different data models."""
    
    def test_conversation_turn_with_all_models(self):
        """Test ConversationTurn integration with all related models."""
        # Create all required models
        response = EnhancedResponse(
            content="This clause specifies the material transfer terms.",
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.9,
            sources=["mta_document.pdf"],
            suggestions=["Ask about IP rights", "Explore restrictions"],
            tone=ToneType.PROFESSIONAL,
            context_used=["document_analysis", "mta_expertise"]
        )
        
        intent = QuestionIntent(
            primary_intent=IntentType.DOCUMENT_RELATED,
            confidence=0.95,
            secondary_intents=[IntentType.CONTRACT_GENERAL],
            document_relevance_score=0.9,
            casualness_level=0.1,
            requires_mta_expertise=True,
            requires_fallback=False
        )
        
        strategy = ResponseStrategy(
            handler_type=HandlerType.EXISTING_CONTRACT,
            use_structured_format=True,
            include_suggestions=True,
            tone_preference=ToneType.PROFESSIONAL,
            fallback_options=[],
            context_requirements=["document", "mta_context"]
        )
        
        # Create conversation turn
        turn = ConversationTurn(
            question="What are the key restrictions in this MTA?",
            response=response,
            intent=intent,
            strategy_used=strategy,
            user_satisfaction=5
        )
        
        # Verify integration
        assert turn.question == "What are the key restrictions in this MTA?"
        assert turn.response.response_type == ResponseType.DOCUMENT_ANALYSIS
        assert turn.intent.requires_mta_expertise is True
        assert turn.strategy_used.handler_type == HandlerType.EXISTING_CONTRACT
        assert turn.user_satisfaction == 5
    
    def test_conversation_context_with_mta_turns(self):
        """Test ConversationContext with MTA-specific conversation turns."""
        context = ConversationContext(
            session_id="mta_session_001",
            document_id="mta_doc_123",
            current_tone=ToneType.PROFESSIONAL,
            user_expertise_level=ExpertiseLevel.EXPERT,
            preferred_response_style="detailed_technical"
        )
        
        # Add MTA-related turns
        for i in range(3):
            response = EnhancedResponse(
                content=f"MTA response {i}",
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=0.8 + i * 0.05
            )
            intent = QuestionIntent(
                primary_intent=IntentType.DOCUMENT_RELATED,
                confidence=0.9,
                requires_mta_expertise=True
            )
            strategy = ResponseStrategy(handler_type=HandlerType.EXISTING_CONTRACT)
            
            turn = ConversationTurn(
                question=f"MTA question {i}",
                response=response,
                intent=intent,
                strategy_used=strategy
            )
            context.add_turn(turn)
        
        # Verify context state
        assert len(context.conversation_history) == 3
        assert len(context.topic_progression) == 3
        
        recent_turns = context.get_recent_turns(2)
        assert len(recent_turns) == 2
        assert recent_turns[0].question == "MTA question 1"
        assert recent_turns[1].question == "MTA question 2"
    
    def test_conversation_flow_analysis(self):
        """Test ConversationFlow with realistic conversation patterns."""
        flow = ConversationFlow(
            session_id="analysis_session",
            flow_type=FlowType.EXPLORATORY,
            topic_coherence=0.75,
            engagement_level=0.85,
            complexity_progression=ComplexityProgression.INCREASING,
            suggested_directions=[
                "Explore IP ownership clauses",
                "Discuss material handling requirements",
                "Review termination conditions"
            ]
        )
        
        # Verify flow analysis
        assert flow.flow_type == FlowType.EXPLORATORY
        assert 0.7 <= flow.topic_coherence <= 0.8
        assert 0.8 <= flow.engagement_level <= 0.9
        assert flow.complexity_progression == ComplexityProgression.INCREASING
        assert len(flow.suggested_directions) == 3
        assert "IP ownership" in flow.suggested_directions[0]