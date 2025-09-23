"""
Enhanced Context Manager for Contract Assistant

Manages conversation context and history to provide contextually aware responses.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from dataclasses import asdict
from src.models.enhanced import (
    ConversationContext, ConversationTurn, ConversationFlow, 
    EnhancedResponse, QuestionIntent, ResponseStrategy,
    ToneType, ExpertiseLevel, FlowType, ComplexityProgression
)


class EnhancedContextManager:
    """Manages conversation context and history for enhanced responses"""
    
    def __init__(self, max_history_length: int = 50, context_retention_hours: int = 24):
        self.conversations: Dict[str, ConversationContext] = {}
        self.max_history_length = max_history_length
        self.context_retention_hours = context_retention_hours
        
    def update_conversation_context(
        self, 
        session_id: str, 
        question: str, 
        response: EnhancedResponse,
        intent: Optional[QuestionIntent] = None,
        strategy: Optional[ResponseStrategy] = None
    ) -> None:
        """Update conversation context with new turn"""
        
        # Create conversation turn
        turn = ConversationTurn(
            question=question,
            response=response,
            intent=intent,
            strategy_used=strategy,
            user_satisfaction=None,  # Can be updated later with feedback
            timestamp=datetime.now()
        )
        
        # Get or create conversation context
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationContext(
                session_id=session_id,
                document_id="default",  # Default document ID, can be updated later
                conversation_history=[],
                current_tone=ToneType.PROFESSIONAL,
                topic_progression=[],
                user_expertise_level=ExpertiseLevel.INTERMEDIATE,
                preferred_response_style="structured"
            )
        
        context = self.conversations[session_id]
        
        # Add turn to history
        context.conversation_history.append(turn)
        
        # Maintain history length limit
        if len(context.conversation_history) > self.max_history_length:
            context.conversation_history = context.conversation_history[-self.max_history_length:]
        
        # Update current tone based on response
        if response.tone:
            # Convert string tone to enum
            tone_mapping = {
                "professional": ToneType.PROFESSIONAL,
                "conversational": ToneType.CONVERSATIONAL,
                "playful": ToneType.PLAYFUL
            }
            context.current_tone = tone_mapping.get(response.tone, ToneType.PROFESSIONAL)
        
        # Update topic progression
        self._update_topic_progression(context, question, response)
        
        # Infer user expertise level from questions
        self._update_user_expertise_level(context, question)
        
        # Update preferred response style
        self._update_response_style_preference(context, response)
        
        # Clean up old conversations
        self._cleanup_old_conversations()
    
    def get_conversation_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get conversation context for a session"""
        return self.conversations.get(session_id)
    
    def analyze_conversation_flow(self, session_id: str) -> Optional[ConversationFlow]:
        """Analyze conversation flow patterns"""
        context = self.conversations.get(session_id)
        if not context or len(context.conversation_history) < 2:
            return None
        
        # Analyze flow characteristics
        flow_type = self._determine_flow_type(context)
        topic_coherence = self._calculate_topic_coherence(context)
        engagement_level = self._assess_engagement_level(context)
        complexity_progression = self._analyze_complexity_progression(context)
        suggested_directions = self._suggest_conversation_directions(context)
        
        return ConversationFlow(
            session_id=session_id,
            flow_type=flow_type,
            topic_coherence=topic_coherence,
            engagement_level=engagement_level,
            complexity_progression=complexity_progression,
            suggested_directions=suggested_directions
        )
    
    def suggest_context_aware_responses(
        self, 
        question: str, 
        context: ConversationContext
    ) -> List[str]:
        """Suggest context-aware response approaches"""
        suggestions = []
        
        # Analyze recent conversation patterns
        recent_turns = context.conversation_history[-5:] if context.conversation_history else []
        
        # Check for repetitive patterns
        if self._detect_repetitive_questions(recent_turns, question):
            suggestions.append("Acknowledge repetition and offer new perspective")
            suggestions.append("Suggest exploring related but different aspects")
        
        # Check for increasing complexity
        if self._detect_complexity_increase(recent_turns):
            suggestions.append("Provide more detailed technical explanation")
            suggestions.append("Include relevant examples and analogies")
        
        # Check for casual tone shift
        if self._detect_tone_shift_to_casual(recent_turns):
            suggestions.append("Match conversational tone while maintaining professionalism")
            suggestions.append("Include light, engaging elements in response")
        
        # Check for expertise level indicators
        if context.user_expertise_level == "expert":
            suggestions.append("Use technical terminology and detailed analysis")
        elif context.user_expertise_level == "beginner":
            suggestions.append("Provide clear explanations with basic terminology")
        
        # Topic-based suggestions
        if self._detect_topic_shift(context, question):
            suggestions.append("Acknowledge topic change and provide smooth transition")
        
        return suggestions
    
    def detect_conversation_patterns(self, session_id: str) -> List[str]:
        """Detect patterns in conversation for better response generation"""
        context = self.conversations.get(session_id)
        if not context:
            return []
        
        patterns = []
        history = context.conversation_history
        
        if len(history) < 2:
            return patterns
        
        # Pattern: Increasing question complexity
        if self._detect_complexity_increase(history[-3:]):
            patterns.append("increasing_complexity")
        
        # Pattern: Topic jumping
        if self._detect_topic_jumping(history[-5:]):
            patterns.append("topic_jumping")
        
        # Pattern: Repetitive questioning
        if self._detect_repetitive_pattern(history[-4:]):
            patterns.append("repetitive_questioning")
        
        # Pattern: Casual conversation drift
        if self._detect_casual_drift(history[-3:]):
            patterns.append("casual_drift")
        
        # Pattern: Deep dive into specific topic
        if self._detect_deep_dive_pattern(history[-4:]):
            patterns.append("deep_dive")
        
        # Pattern: Satisfaction indicators
        if self._detect_satisfaction_pattern(history[-3:]):
            patterns.append("high_satisfaction")
        elif self._detect_frustration_pattern(history[-3:]):
            patterns.append("potential_frustration")
        
        return patterns
    
    def get_contextual_tone_suggestion(self, session_id: str, question: str) -> str:
        """Suggest appropriate tone based on conversation context"""
        context = self.conversations.get(session_id)
        if not context:
            return "professional"
        
        # Analyze recent tone patterns
        recent_tones = [turn.response.tone for turn in context.conversation_history[-3:] 
                       if turn.response and turn.response.tone]
        
        # Check question characteristics
        question_lower = question.lower()
        casual_indicators = ['thanks', 'cool', 'awesome', 'lol', 'haha', '😊', '👍']
        formal_indicators = ['please', 'kindly', 'would you', 'could you']
        
        is_casual = any(indicator in question_lower for indicator in casual_indicators)
        is_formal = any(indicator in question_lower for indicator in formal_indicators)
        
        # Determine appropriate tone
        if is_casual and context.current_tone in [ToneType.CONVERSATIONAL, ToneType.PLAYFUL]:
            return "conversational"
        elif is_formal or not recent_tones:
            return "professional"
        elif len(set(recent_tones)) == 1:
            # Maintain consistent tone
            return recent_tones[-1]
        else:
            # Default to professional for mixed patterns
            return "professional"
    
    def _update_topic_progression(
        self, 
        context: ConversationContext, 
        question: str, 
        response: EnhancedResponse
    ) -> None:
        """Update topic progression tracking"""
        # Extract key topics from question and response
        question_topics = self._extract_topics(question)
        response_topics = self._extract_topics(response.content)
        
        all_topics = list(set(question_topics + response_topics))
        
        # Add new topics to progression
        for topic in all_topics:
            if topic not in context.topic_progression:
                context.topic_progression.append(topic)
        
        # Limit topic progression length
        if len(context.topic_progression) > 20:
            context.topic_progression = context.topic_progression[-20:]
    
    def _update_user_expertise_level(self, context: ConversationContext, question: str) -> None:
        """Update user expertise level based on question complexity"""
        question_lower = question.lower()
        
        # Expert indicators
        expert_terms = [
            'derivative work', 'ip assignment', 'indemnification', 'liability cap',
            'force majeure', 'governing law', 'jurisdiction', 'arbitration'
        ]
        
        # Beginner indicators
        beginner_terms = [
            'what does this mean', 'can you explain', 'i don\'t understand',
            'simple terms', 'basic question', 'new to this'
        ]
        
        expert_score = sum(1 for term in expert_terms if term in question_lower)
        beginner_score = sum(1 for term in beginner_terms if term in question_lower)
        
        if expert_score > beginner_score and expert_score > 0:
            context.user_expertise_level = ExpertiseLevel.EXPERT
        elif beginner_score > expert_score and beginner_score > 0:
            context.user_expertise_level = ExpertiseLevel.BEGINNER
        # Otherwise keep current level
    
    def _update_response_style_preference(
        self, 
        context: ConversationContext, 
        response: EnhancedResponse
    ) -> None:
        """Update preferred response style based on response type"""
        if response.response_type == "document_analysis" and response.structured_format:
            context.preferred_response_style = "structured"
        elif response.response_type in ["casual", "conversational"]:
            context.preferred_response_style = "conversational"
        elif response.response_type == "fallback":
            context.preferred_response_style = "helpful_redirection"
    
    def _cleanup_old_conversations(self) -> None:
        """Remove conversations older than retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.context_retention_hours)
        
        sessions_to_remove = []
        for session_id, context in self.conversations.items():
            if context.conversation_history:
                last_activity = context.conversation_history[-1].timestamp
                if last_activity < cutoff_time:
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.conversations[session_id]
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text"""
        # Simple topic extraction based on keywords
        contract_topics = [
            'liability', 'indemnification', 'termination', 'intellectual property',
            'confidentiality', 'payment', 'delivery', 'warranty', 'dispute',
            'governing law', 'force majeure', 'assignment', 'modification'
        ]
        
        mta_topics = [
            'material transfer', 'research use', 'derivatives', 'publication',
            'commercial use', 'provider', 'recipient', 'original material'
        ]
        
        all_topics = contract_topics + mta_topics
        text_lower = text.lower()
        
        found_topics = [topic for topic in all_topics if topic in text_lower]
        return found_topics
    
    def _determine_flow_type(self, context: ConversationContext) -> FlowType:
        """Determine the type of conversation flow"""
        history = context.conversation_history
        
        if len(history) < 3:
            return FlowType.EXPLORATORY
        
        # Analyze topic consistency
        topics = []
        for turn in history[-5:]:
            topics.extend(self._extract_topics(turn.question))
        
        unique_topics = set(topics)
        
        if len(unique_topics) <= 2:
            return FlowType.FOCUSED
        elif len(unique_topics) > 4:
            return FlowType.EXPLORATORY
        else:
            return FlowType.LINEAR
    
    def _calculate_topic_coherence(self, context: ConversationContext) -> float:
        """Calculate how coherent the topic progression is"""
        history = context.conversation_history[-10:]  # Last 10 turns
        
        if len(history) < 2:
            return 1.0
        
        # Count topic transitions
        all_topics = []
        for turn in history:
            all_topics.extend(self._extract_topics(turn.question))
        
        if not all_topics:
            return 0.5  # Neutral coherence for no identifiable topics
        
        # Calculate coherence as ratio of repeated topics to total topics
        unique_topics = set(all_topics)
        coherence = 1.0 - (len(unique_topics) / len(all_topics)) if all_topics else 0.5
        
        return max(0.0, min(1.0, coherence))
    
    def _assess_engagement_level(self, context: ConversationContext) -> float:
        """Assess user engagement level based on conversation patterns"""
        history = context.conversation_history[-5:]  # Last 5 turns
        
        if not history:
            return 0.5
        
        engagement_score = 0.0
        
        # Factors that increase engagement
        for turn in history:
            question_length = len(turn.question.split())
            
            # Longer questions indicate higher engagement
            if question_length > 10:
                engagement_score += 0.2
            elif question_length > 5:
                engagement_score += 0.1
            
            # Follow-up questions indicate engagement
            if any(word in turn.question.lower() for word in ['also', 'additionally', 'furthermore', 'what about']):
                engagement_score += 0.1
            
            # Casual elements indicate comfort/engagement
            if turn.response and turn.response.tone in ["conversational", "playful"]:
                engagement_score += 0.1
        
        return max(0.0, min(1.0, engagement_score))
    
    def _analyze_complexity_progression(self, context: ConversationContext) -> ComplexityProgression:
        """Analyze how question complexity changes over time"""
        history = context.conversation_history[-5:]
        
        if len(history) < 2:
            return ComplexityProgression.STABLE
        
        complexity_scores = []
        for turn in history:
            # Simple complexity scoring based on question characteristics
            score = 0
            question = turn.question.lower()
            
            # Technical terms increase complexity
            technical_terms = ['liability', 'indemnification', 'derivative', 'ip', 'jurisdiction']
            score += sum(1 for term in technical_terms if term in question)
            
            # Question length indicates complexity
            score += len(question.split()) / 10
            
            # Multiple clauses indicate complexity
            score += question.count(',') + question.count(';')
            
            complexity_scores.append(score)
        
        # Analyze trend
        if len(complexity_scores) < 2:
            return ComplexityProgression.STABLE
        
        first_half_avg = sum(complexity_scores[:len(complexity_scores)//2]) / (len(complexity_scores)//2)
        second_half_avg = sum(complexity_scores[len(complexity_scores)//2:]) / (len(complexity_scores) - len(complexity_scores)//2)
        
        if second_half_avg > first_half_avg * 1.2:
            return ComplexityProgression.INCREASING
        elif second_half_avg < first_half_avg * 0.8:
            return ComplexityProgression.DECREASING
        else:
            return ComplexityProgression.STABLE
    
    def _suggest_conversation_directions(self, context: ConversationContext) -> List[str]:
        """Suggest potential conversation directions"""
        suggestions = []
        
        # Based on topic progression
        recent_topics = set()
        for turn in context.conversation_history[-3:]:
            recent_topics.update(self._extract_topics(turn.question))
        
        if 'liability' in recent_topics:
            suggestions.append("Explore indemnification and risk allocation")
        
        if 'intellectual property' in recent_topics:
            suggestions.append("Discuss ownership and licensing terms")
        
        if 'termination' in recent_topics:
            suggestions.append("Review post-termination obligations")
        
        # Based on user expertise level
        if context.user_expertise_level == ExpertiseLevel.BEGINNER:
            suggestions.append("Provide foundational contract concepts")
        elif context.user_expertise_level == ExpertiseLevel.EXPERT:
            suggestions.append("Dive into advanced legal implications")
        
        # Default suggestions if none specific
        if not suggestions:
            suggestions.extend([
                "Explore key risk factors in the agreement",
                "Discuss practical implementation considerations",
                "Review compliance and monitoring requirements"
            ])
        
        return suggestions[:3]
    
    def _detect_repetitive_questions(self, recent_turns: List[ConversationTurn], current_question: str) -> bool:
        """Detect if current question is repetitive"""
        if not recent_turns:
            return False
        
        current_words = set(current_question.lower().split())
        
        for turn in recent_turns:
            turn_words = set(turn.question.lower().split())
            overlap = len(current_words.intersection(turn_words))
            
            # If more than 60% word overlap, consider repetitive
            if overlap / len(current_words) > 0.6:
                return True
        
        return False
    
    def _detect_complexity_increase(self, turns: List[ConversationTurn]) -> bool:
        """Detect if questions are becoming more complex"""
        if len(turns) < 2:
            return False
        
        # Simple heuristic: later questions are longer and contain more technical terms
        first_question = turns[0].question
        last_question = turns[-1].question
        
        return len(last_question.split()) > len(first_question.split()) * 1.5
    
    def _detect_tone_shift_to_casual(self, turns: List[ConversationTurn]) -> bool:
        """Detect shift toward casual conversation"""
        if not turns:
            return False
        
        casual_indicators = ['thanks', 'cool', 'awesome', 'great', 'nice']
        recent_question = turns[-1].question.lower()
        
        return any(indicator in recent_question for indicator in casual_indicators)
    
    def _detect_topic_shift(self, context: ConversationContext, current_question: str) -> bool:
        """Detect if there's a significant topic shift"""
        if not context.conversation_history:
            return False
        
        recent_topics = set()
        for turn in context.conversation_history[-2:]:
            recent_topics.update(self._extract_topics(turn.question))
        
        current_topics = set(self._extract_topics(current_question))
        
        # If no overlap in topics, it's a shift
        return len(recent_topics.intersection(current_topics)) == 0 and recent_topics and current_topics
    
    def _detect_topic_jumping(self, turns: List[ConversationTurn]) -> bool:
        """Detect if user is jumping between topics"""
        if len(turns) < 3:
            return False
        
        topics_per_turn = []
        for turn in turns:
            topics_per_turn.append(set(self._extract_topics(turn.question)))
        
        # Count topic transitions
        transitions = 0
        for i in range(1, len(topics_per_turn)):
            if not topics_per_turn[i].intersection(topics_per_turn[i-1]):
                transitions += 1
        
        return transitions >= len(turns) - 1  # Almost every turn changes topic
    
    def _detect_repetitive_pattern(self, turns: List[ConversationTurn]) -> bool:
        """Detect repetitive questioning patterns"""
        if len(turns) < 3:
            return False
        
        # Check for similar question structures
        question_patterns = []
        for turn in turns:
            # Simple pattern: first few words
            words = turn.question.lower().split()[:3]
            question_patterns.append(' '.join(words))
        
        # If more than half the patterns are similar, it's repetitive
        unique_patterns = set(question_patterns)
        return len(unique_patterns) < len(question_patterns) / 2
    
    def _detect_casual_drift(self, turns: List[ConversationTurn]) -> bool:
        """Detect drift toward casual conversation"""
        if not turns:
            return False
        
        casual_count = 0
        for turn in turns:
            if turn.response and turn.response.tone in ["conversational", "playful"]:
                casual_count += 1
        
        return casual_count >= len(turns) / 2
    
    def _detect_deep_dive_pattern(self, turns: List[ConversationTurn]) -> bool:
        """Detect deep dive into specific topic"""
        if len(turns) < 3:
            return False
        
        # Check if all turns focus on similar topics
        all_topics = []
        for turn in turns:
            all_topics.extend(self._extract_topics(turn.question))
        
        if not all_topics:
            return False
        
        # If most topics are the same, it's a deep dive
        unique_topics = set(all_topics)
        return len(unique_topics) <= 2 and len(all_topics) >= 3
    
    def _detect_satisfaction_pattern(self, turns: List[ConversationTurn]) -> bool:
        """Detect indicators of user satisfaction"""
        if not turns:
            return False
        
        satisfaction_indicators = ['thank', 'great', 'helpful', 'perfect', 'exactly', 'clear']
        
        for turn in turns:
            question_lower = turn.question.lower()
            if any(indicator in question_lower for indicator in satisfaction_indicators):
                return True
        
        return False
    
    def _detect_frustration_pattern(self, turns: List[ConversationTurn]) -> bool:
        """Detect indicators of user frustration"""
        if not turns:
            return False
        
        frustration_indicators = ['still confused', 'not clear', 'don\'t understand', 'unclear', 'confusing']
        
        for turn in turns:
            question_lower = turn.question.lower()
            if any(indicator in question_lower for indicator in frustration_indicators):
                return True
        
        return False