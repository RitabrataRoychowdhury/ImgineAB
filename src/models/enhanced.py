"""
Enhanced data models for the contract assistant system.

This module contains data structures for enhanced conversational behavior,
question classification, response routing, and MTA-specific functionality.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ResponseType(Enum):
    """Types of responses the enhanced system can generate."""
    DOCUMENT_ANALYSIS = "document_analysis"
    FALLBACK = "fallback"
    GENERAL_KNOWLEDGE = "general_knowledge"
    CASUAL = "casual"


class IntentType(Enum):
    """Types of question intents the system can classify."""
    DOCUMENT_RELATED = "document_related"
    OFF_TOPIC = "off_topic"
    CONTRACT_GENERAL = "contract_general"
    CASUAL = "casual"


class ToneType(Enum):
    """Tone types for responses."""
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    PLAYFUL = "playful"


class HandlerType(Enum):
    """Types of handlers for processing questions."""
    EXISTING_CONTRACT = "existing_contract"
    FALLBACK = "fallback"
    GENERAL_KNOWLEDGE = "general_knowledge"
    CASUAL = "casual"


class CollaborationType(Enum):
    """Types of research collaboration for MTAs."""
    ACADEMIC = "academic"
    COMMERCIAL = "commercial"
    HYBRID = "hybrid"


class ExpertiseLevel(Enum):
    """User expertise levels for conversation context."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class FlowType(Enum):
    """Types of conversation flows."""
    LINEAR = "linear"
    EXPLORATORY = "exploratory"
    FOCUSED = "focused"
    CASUAL = "casual"


class ComplexityProgression(Enum):
    """Types of complexity progression in conversations."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"


@dataclass
class EnhancedResponse:
    """Enhanced response model with metadata and context."""
    content: str
    response_type: ResponseType
    confidence: float
    sources: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    tone: ToneType = ToneType.PROFESSIONAL
    structured_format: Optional[Dict[str, Any]] = None
    context_used: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate the response data after initialization."""
        if not isinstance(self.response_type, ResponseType):
            raise ValueError(f"response_type must be a ResponseType enum, got {type(self.response_type)}")
        if not isinstance(self.tone, ToneType):
            raise ValueError(f"tone must be a ToneType enum, got {type(self.tone)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.content.strip():
            raise ValueError("content cannot be empty")


@dataclass
class QuestionIntent:
    """Question intent classification with confidence scores."""
    primary_intent: IntentType
    confidence: float
    secondary_intents: List[IntentType] = field(default_factory=list)
    document_relevance_score: float = 0.0
    casualness_level: float = 0.0
    requires_mta_expertise: bool = False
    requires_fallback: bool = False
    
    def __post_init__(self):
        """Validate the intent data after initialization."""
        if not isinstance(self.primary_intent, IntentType):
            raise ValueError(f"primary_intent must be an IntentType enum, got {type(self.primary_intent)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not 0.0 <= self.document_relevance_score <= 1.0:
            raise ValueError(f"document_relevance_score must be between 0.0 and 1.0, got {self.document_relevance_score}")
        if not 0.0 <= self.casualness_level <= 1.0:
            raise ValueError(f"casualness_level must be between 0.0 and 1.0, got {self.casualness_level}")


@dataclass
class ResponseStrategy:
    """Strategy for generating responses based on question intent."""
    handler_type: HandlerType
    use_structured_format: bool = True
    include_suggestions: bool = True
    tone_preference: ToneType = ToneType.PROFESSIONAL
    fallback_options: List[str] = field(default_factory=list)
    context_requirements: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the strategy data after initialization."""
        if not isinstance(self.handler_type, HandlerType):
            raise ValueError(f"handler_type must be a HandlerType enum, got {type(self.handler_type)}")
        if not isinstance(self.tone_preference, ToneType):
            raise ValueError(f"tone_preference must be a ToneType enum, got {type(self.tone_preference)}")


@dataclass
class MTAContext:
    """Context information specific to Material Transfer Agreements."""
    document_id: str
    provider_entity: Optional[str] = None
    recipient_entity: Optional[str] = None
    material_types: List[str] = field(default_factory=list)
    research_purposes: List[str] = field(default_factory=list)
    ip_considerations: List[str] = field(default_factory=list)
    key_restrictions: List[str] = field(default_factory=list)
    collaboration_type: CollaborationType = CollaborationType.ACADEMIC
    
    def __post_init__(self):
        """Validate the MTA context data after initialization."""
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty")
        if not isinstance(self.collaboration_type, CollaborationType):
            raise ValueError(f"collaboration_type must be a CollaborationType enum, got {type(self.collaboration_type)}")


@dataclass
class MTAInsight:
    """Insights and expertise for MTA-specific questions."""
    concept_explanations: Dict[str, str] = field(default_factory=dict)
    research_implications: List[str] = field(default_factory=list)
    common_practices: List[str] = field(default_factory=list)
    risk_considerations: List[str] = field(default_factory=list)
    suggested_questions: List[str] = field(default_factory=list)


@dataclass
class ConversationTurn:
    """A single turn in a conversation (question + response)."""
    question: str
    response: EnhancedResponse
    intent: QuestionIntent
    strategy_used: ResponseStrategy
    user_satisfaction: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate the conversation turn data after initialization."""
        if not self.question.strip():
            raise ValueError("question cannot be empty")
        if self.user_satisfaction is not None and not 1 <= self.user_satisfaction <= 5:
            raise ValueError(f"user_satisfaction must be between 1 and 5, got {self.user_satisfaction}")


@dataclass
class ConversationContext:
    """Context for managing ongoing conversations."""
    session_id: str
    document_id: str
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    current_tone: ToneType = ToneType.PROFESSIONAL
    topic_progression: List[str] = field(default_factory=list)
    user_expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    preferred_response_style: str = "balanced"
    
    def __post_init__(self):
        """Validate the conversation context data after initialization."""
        if not self.session_id.strip():
            raise ValueError("session_id cannot be empty")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty")
        if not isinstance(self.current_tone, ToneType):
            raise ValueError(f"current_tone must be a ToneType enum, got {type(self.current_tone)}")
        if not isinstance(self.user_expertise_level, ExpertiseLevel):
            raise ValueError(f"user_expertise_level must be an ExpertiseLevel enum, got {type(self.user_expertise_level)}")
    
    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn to the history."""
        self.conversation_history.append(turn)
        
        # Update topic progression
        if turn.intent.primary_intent == IntentType.DOCUMENT_RELATED:
            # Extract topic from question (simplified)
            topic = turn.question[:50] + "..." if len(turn.question) > 50 else turn.question
            if topic not in self.topic_progression:
                self.topic_progression.append(topic)
    
    def get_recent_turns(self, count: int = 5) -> List[ConversationTurn]:
        """Get the most recent conversation turns."""
        return self.conversation_history[-count:] if self.conversation_history else []


@dataclass
class ConversationFlow:
    """Analysis of conversation flow patterns."""
    session_id: str
    flow_type: FlowType
    topic_coherence: float
    engagement_level: float
    complexity_progression: ComplexityProgression
    suggested_directions: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the conversation flow data after initialization."""
        if not self.session_id.strip():
            raise ValueError("session_id cannot be empty")
        if not isinstance(self.flow_type, FlowType):
            raise ValueError(f"flow_type must be a FlowType enum, got {type(self.flow_type)}")
        if not isinstance(self.complexity_progression, ComplexityProgression):
            raise ValueError(f"complexity_progression must be a ComplexityProgression enum, got {type(self.complexity_progression)}")
        if not 0.0 <= self.topic_coherence <= 1.0:
            raise ValueError(f"topic_coherence must be between 0.0 and 1.0, got {self.topic_coherence}")
        if not 0.0 <= self.engagement_level <= 1.0:
            raise ValueError(f"engagement_level must be between 0.0 and 1.0, got {self.engagement_level}")


@dataclass
class ConversationPattern:
    """Detected patterns in conversation behavior."""
    pattern_type: str
    frequency: int
    confidence: float
    description: str
    suggested_response: Optional[str] = None
    
    def __post_init__(self):
        """Validate the conversation pattern data after initialization."""
        if not self.pattern_type.strip():
            raise ValueError("pattern_type cannot be empty")
        if not self.description.strip():
            raise ValueError("description cannot be empty")
        if self.frequency < 0:
            raise ValueError(f"frequency must be non-negative, got {self.frequency}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be between 0.0 and 1.0, got {self.confidence}")