"""
Question Classification and Intent Detection System.

This module provides intelligent question classification for the enhanced contract assistant,
including intent detection, document relevance scoring, and conversational tone assessment.
"""

import re
import math
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from collections import Counter

from src.models.enhanced import QuestionIntent, IntentType, ConversationContext
from src.models.document import Document
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ClassificationFeatures:
    """Features extracted from a question for classification."""
    word_count: int
    question_words: List[str]
    legal_terms: List[str]
    mta_terms: List[str]
    casual_indicators: List[str]
    contract_concepts: List[str]
    document_keywords: List[str]
    sentiment_score: float
    formality_score: float


class QuestionClassifier:
    """
    Intelligent question classifier for enhanced contract assistant.
    
    Classifies questions into intents and provides confidence scores for routing decisions.
    """
    
    # Legal and contract-related terms
    LEGAL_TERMS = {
        'general': [
            'agreement', 'contract', 'terms', 'conditions', 'liability', 
            'intellectual property', 'confidential', 'proprietary', 'obligations',
            'rights', 'responsibilities', 'breach', 'termination', 'governing law',
            'jurisdiction', 'dispute', 'arbitration', 'indemnification', 'warranty',
            'clause', 'provision', 'section', 'article', 'paragraph', 'subsection',
            'legal', 'law', 'attorney', 'lawyer', 'counsel', 'litigation',
            'compliance', 'regulation', 'statute', 'precedent', 'case law'
        ],
        'mta': [
            'material transfer', 'research use', 'derivatives', 'publication',
            'recipient', 'provider', 'original material', 'modifications',
            'research purposes', 'commercial use', 'third party', 'ownership',
            'improvements', 'inventions', 'patent rights', 'licensing',
            'academic', 'university', 'institution', 'researcher', 'scientist',
            'laboratory', 'study', 'experiment', 'data', 'results', 'findings',
            'collaboration', 'joint research', 'sponsored research',
            'intellectual property'  # Added since IP is crucial in MTAs
        ],
        'contract_concepts': [
            'force majeure', 'consideration', 'damages', 'remedy', 'cure',
            'notice', 'consent', 'approval', 'assignment', 'delegation',
            'severability', 'waiver', 'amendment', 'modification', 'renewal',
            'extension', 'expiration', 'effective date', 'execution',
            'counterpart', 'signature', 'witness', 'notarization'
        ]
    }
    
    # Casual and conversational indicators
    CASUAL_INDICATORS = {
        'informal_greetings': ['hi', 'hello', 'hey', 'sup', 'yo'],
        'casual_language': [
            'cool', 'awesome', 'sweet', 'nice', 'great', 'perfect',
            'yeah', 'yep', 'nope', 'ok', 'okay', 'sure', 'gotcha',
            'thanks', 'thx', 'ty', 'appreciate', 'cheers'
        ],
        'conversational_fillers': [
            'um', 'uh', 'well', 'so', 'like', 'you know', 'i mean',
            'basically', 'actually', 'honestly', 'frankly'
        ],
        'playful_language': [
            'lol', 'haha', 'hehe', 'funny', 'joke', 'kidding',
            'silly', 'crazy', 'weird', 'strange', 'odd', 'vibe',
            'style of', 'like a', 'as if', 'pretend', 'imagine',
            'mouse', 'recipe', 'cooking'
        ],
        'questions_about_system': [
            'who are you', 'what are you', 'how do you work', 'tell me about yourself',
            'what can you do', 'help me', 'how does this work'
        ]
    }
    
    # Question words and patterns
    QUESTION_PATTERNS = {
        'what': r'\bwhat\b',
        'how': r'\bhow\b',
        'why': r'\bwhy\b',
        'when': r'\bwhen\b',
        'where': r'\bwhere\b',
        'who': r'\bwho\b',
        'which': r'\bwhich\b',
        'can': r'\bcan\b',
        'could': r'\bcould\b',
        'would': r'\bwould\b',
        'should': r'\bshould\b',
        'is': r'\bis\b',
        'are': r'\bare\b',
        'does': r'\bdoes\b',
        'do': r'\bdo\b'
    }
    
    # Off-topic indicators
    OFF_TOPIC_PATTERNS = [
        r'\b(weather|sports|food|music|movie|tv|game|politics)\b',
        r'\b(recipe|cooking|restaurant|travel|vacation)\b',
        r'\b(birthday|holiday|weekend|party|celebration)\b',
        r'\b(health|doctor|medicine|exercise|fitness)\b',
        r'\b(technology|computer|phone|internet|social media)\b',
        r'\b(style of|in the style|like a|as if|pretend|imagine)\b',
        r'\b(joke|funny|humor|laugh|comedy)\b',
        r'\b(vibe|feeling|mood|atmosphere)\b',
        r'\b(mouse|animal|pet|creature)\b'
    ]
    
    def __init__(self):
        """Initialize the question classifier."""
        self._compile_patterns()
        logger.info("QuestionClassifier initialized")
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        self.question_patterns = {
            key: re.compile(pattern, re.IGNORECASE)
            for key, pattern in self.QUESTION_PATTERNS.items()
        }
        
        self.off_topic_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.OFF_TOPIC_PATTERNS
        ]
    
    def classify_intent(self, question: str, context: Optional[ConversationContext] = None) -> QuestionIntent:
        """
        Classify the intent of a question.
        
        Args:
            question: The user's question
            context: Optional conversation context for better classification
            
        Returns:
            QuestionIntent with classification results
        """
        try:
            # Extract features from the question
            features = self._extract_features(question, context)
            
            # Calculate intent scores
            intent_scores = self._calculate_intent_scores(features, context, question)
            
            # Determine primary intent
            primary_intent = max(intent_scores.items(), key=lambda x: x[1])
            primary_intent_type = IntentType(primary_intent[0])
            confidence = primary_intent[1]
            
            # Determine secondary intents (above threshold)
            secondary_threshold = 0.3
            secondary_intents = [
                IntentType(intent) for intent, score in intent_scores.items()
                if score >= secondary_threshold and intent != primary_intent[0]
            ]
            
            # Calculate document relevance score
            document_relevance = self._calculate_document_relevance_score(features)
            
            # Assess casualness level
            casualness_level = self._assess_casualness_level(features)
            
            # Determine if MTA expertise is needed
            requires_mta_expertise = self._requires_mta_expertise(features)
            
            # Determine if fallback is needed
            requires_fallback = primary_intent_type in [IntentType.OFF_TOPIC, IntentType.CASUAL]
            
            return QuestionIntent(
                primary_intent=primary_intent_type,
                confidence=confidence,
                secondary_intents=secondary_intents,
                document_relevance_score=document_relevance,
                casualness_level=casualness_level,
                requires_mta_expertise=requires_mta_expertise,
                requires_fallback=requires_fallback
            )
            
        except Exception as e:
            logger.error(f"Error classifying question intent: {e}")
            # Return safe fallback classification
            return QuestionIntent(
                primary_intent=IntentType.DOCUMENT_RELATED,
                confidence=0.5,
                document_relevance_score=0.5,
                casualness_level=0.0,
                requires_fallback=False
            )
    
    def detect_document_relevance(self, question: str, document: Document) -> float:
        """
        Detect how relevant a question is to a specific document.
        
        Args:
            question: The user's question
            document: The document to check relevance against
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        try:
            if not document or not document.original_text:
                return 0.0
            
            question_lower = question.lower()
            document_text = document.original_text.lower()
            document_title = document.title.lower()
            
            # Extract keywords from question
            question_words = self._extract_keywords(question_lower)
            
            # Calculate keyword overlap with document
            keyword_matches = 0
            total_keywords = len(question_words)
            
            if total_keywords == 0:
                return 0.0
            
            for word in question_words:
                if len(word) > 2:  # Skip very short words
                    if word in document_text or word in document_title:
                        keyword_matches += 1
            
            keyword_relevance = keyword_matches / total_keywords
            
            # Boost relevance for legal terms if document is legal
            legal_boost = 0.0
            if document.is_legal_document:
                legal_terms_in_question = self._find_legal_terms(question_lower)
                if legal_terms_in_question:
                    legal_boost = min(len(legal_terms_in_question) * 0.1, 0.3)
            
            # Calculate final relevance score
            relevance_score = min(keyword_relevance + legal_boost, 1.0)
            
            logger.debug(f"Document relevance for question '{question[:50]}...': {relevance_score}")
            return relevance_score
            
        except Exception as e:
            logger.error(f"Error detecting document relevance: {e}")
            return 0.5  # Safe fallback
    
    def identify_contract_concepts(self, question: str) -> List[str]:
        """
        Identify contract-related concepts in a question.
        
        Args:
            question: The user's question
            
        Returns:
            List of contract concepts found
        """
        question_lower = question.lower()
        concepts = []
        
        # Check for legal terms
        for category, terms in self.LEGAL_TERMS.items():
            for term in terms:
                if term in question_lower:
                    concepts.append(term)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_concepts = []
        for concept in concepts:
            if concept not in seen:
                seen.add(concept)
                unique_concepts.append(concept)
        
        return unique_concepts
    
    def assess_casualness_level(self, question: str) -> float:
        """
        Assess the casualness level of a question.
        
        Args:
            question: The user's question
            
        Returns:
            Casualness score between 0.0 (formal) and 1.0 (very casual)
        """
        features = self._extract_features(question)
        return self._assess_casualness_level(features)
    
    def detect_mta_specificity(self, question: str, document: Document) -> bool:
        """
        Detect if a question requires MTA-specific expertise.
        
        Args:
            question: The user's question
            document: The document being analyzed
            
        Returns:
            True if MTA expertise is needed
        """
        # Check if document is MTA
        if document and document.legal_document_type == "MTA":
            return True
        
        # Check for MTA-specific terms in question
        question_lower = question.lower()
        mta_terms_found = 0
        
        for term in self.LEGAL_TERMS['mta']:
            if term in question_lower:
                mta_terms_found += 1
        
        # Require at least 1 MTA term for MTA expertise
        return mta_terms_found >= 1
    
    def _extract_features(self, question: str, context: Optional[ConversationContext] = None) -> ClassificationFeatures:
        """Extract classification features from a question."""
        question_lower = question.lower()
        words = question_lower.split()
        
        # Extract various feature types
        question_words = [word for word in words if any(pattern.search(word) for pattern in self.question_patterns.values())]
        legal_terms = self._find_legal_terms(question_lower)
        mta_terms = self._find_mta_terms(question_lower)
        casual_indicators = self._find_casual_indicators(question_lower)
        contract_concepts = self.identify_contract_concepts(question)
        
        # Store the full question text separately for off-topic detection
        # Don't add it to casual_indicators as it affects casualness scoring
        
        # Calculate sentiment and formality scores
        sentiment_score = self._calculate_sentiment_score(question_lower)
        formality_score = self._calculate_formality_score(question_lower, words)
        
        return ClassificationFeatures(
            word_count=len(words),
            question_words=question_words,
            legal_terms=legal_terms,
            mta_terms=mta_terms,
            casual_indicators=casual_indicators,
            contract_concepts=contract_concepts,
            document_keywords=[],  # Will be populated if document context is available
            sentiment_score=sentiment_score,
            formality_score=formality_score
        )
    
    def _calculate_intent_scores(self, features: ClassificationFeatures, context: Optional[ConversationContext], question: str) -> Dict[str, float]:
        """Calculate scores for each intent type."""
        scores = {
            'document_related': 0.0,
            'off_topic': 0.0,
            'contract_general': 0.0,
            'casual': 0.0
        }
        
        # Off-topic scoring (check first to catch obvious off-topic questions)
        question_text = question.lower()
        off_topic_matches = sum(1 for pattern in self.off_topic_patterns if pattern.search(question_text))
        
        # Also check for common off-topic words directly
        off_topic_words = ['weather', 'sports', 'food', 'music', 'movie', 'tv', 'game', 'politics',
                          'recipe', 'cooking', 'cook', 'restaurant', 'travel', 'vacation', 'birthday',
                          'holiday', 'weekend', 'party', 'celebration', 'health', 'doctor',
                          'medicine', 'exercise', 'fitness', 'technology', 'computer', 'phone',
                          'internet', 'social media', 'pasta', 'dinner', 'lunch', 'breakfast']
        
        # Check for playful/creative request patterns
        playful_patterns = [
            'style of', 'in the style', 'like a', 'as if', 'pretend', 'imagine',
            'joke', 'funny', 'humor', 'vibe', 'feeling', 'mouse', 'animal'
        ]
        
        off_topic_word_matches = sum(1 for word in off_topic_words if word in question_text.lower())
        
        # Check for playful patterns
        playful_matches = sum(1 for pattern in playful_patterns if pattern in question_text.lower())
        
        # Special handling for "style of" questions - these are almost always playful/off-topic
        has_style_request = 'style of' in question_text.lower() or 'in the style' in question_text.lower()
        
        # Strong off-topic scoring for obvious cases
        if off_topic_matches > 0 or off_topic_word_matches > 0 or playful_matches > 0 or has_style_request:
            total_off_topic_score = off_topic_matches + off_topic_word_matches + (playful_matches * 2)  # Weight playful higher
            
            # Extra boost for style requests - these are almost always off-topic
            if has_style_request:
                total_off_topic_score += 5  # Strong boost
            
            scores['off_topic'] += min(total_off_topic_score * 0.4, 0.98)
        
        # Casual scoring - but don't override strong off-topic signals
        casualness_level = self._assess_casualness_level(features)
        if casualness_level > 0.3 and scores['off_topic'] < 0.5:  # Only if not strongly off-topic
            scores['casual'] += casualness_level * 0.8
        
        # Document-related scoring
        is_definition_question = any(phrase in question_text.lower() for phrase in 
                                   ['what is', 'what does', 'define', 'meaning of'])
        is_asking_about_provisions = any(word in question_text.lower() for word in 
                                       ['provisions', 'clauses', 'terms', 'sections', 'articles'])
        
        # "What are" questions about provisions/clauses are usually document-related
        if 'what are' in question_text.lower() and is_asking_about_provisions:
            is_definition_question = False
        
        if not is_definition_question:
            # Don't boost document_related if there are strong off-topic signals
            if (features.legal_terms or features.contract_concepts) and scores['off_topic'] < 0.5:
                scores['document_related'] += 0.5
            if features.question_words and (features.legal_terms or features.contract_concepts) and scores['off_topic'] < 0.5:
                scores['document_related'] += 0.3
        else:
            # For definition questions, only boost if document-specific and not off-topic
            document_specific_words = ['this', 'the contract', 'the agreement', 'document', 'here', 'above', 'below']
            is_document_specific = any(word in question_text.lower() for word in document_specific_words)
            if is_document_specific and (features.legal_terms or features.contract_concepts) and scores['off_topic'] < 0.5:
                scores['document_related'] += 0.4
        
        if features.formality_score > 0.6 and scores['off_topic'] < 0.5:
            scores['document_related'] += 0.2
        
        # Contract general scoring (legal terms but not document-specific)
        # Questions asking "what is X" about legal concepts should be contract_general
        question_text_lower = question_text.lower()
        is_definition_question = any(phrase in question_text_lower for phrase in 
                                   ['what is', 'what are', 'what does', 'define', 'explain', 'meaning of'])
        
        # Check for general legal/contract terms that suggest general knowledge questions
        general_legal_terms = ['mta', 'nda', 'liability clause', 'intellectual property', 'contract', 'agreement']
        has_general_legal_term = any(term in question_text_lower for term in general_legal_terms)
        
        if is_definition_question and (features.legal_terms or features.contract_concepts or has_general_legal_term):
            # Check if it's asking about the document specifically
            document_specific_words = ['this', 'the contract', 'the agreement', 'document', 'here', 'above', 'below']
            is_document_specific = any(word in question_text_lower for word in document_specific_words)
            
            if not is_document_specific:
                scores['contract_general'] += 0.8  # Increased confidence for general knowledge
            else:
                scores['document_related'] += 0.3
        
        # General legal knowledge questions
        if features.legal_terms and not is_definition_question:
            scores['contract_general'] += 0.2
        if features.contract_concepts and features.formality_score > 0.5:
            scores['contract_general'] += 0.2
        
        # Boost document_related if we have strong legal indicators and no off-topic signals
        if (features.legal_terms or features.contract_concepts) and scores['off_topic'] < 0.3:
            # Reduce boost if there are playful elements or style requests
            playful_reduction = playful_matches * 0.1
            if has_style_request:
                playful_reduction += 0.3  # Strong reduction for style requests
            
            boost = max(0.0, 0.2 - playful_reduction)
            if boost > 0:
                scores['document_related'] += boost
        
        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v / total_score for k, v in scores.items()}
        else:
            # Default to document_related if no clear signals
            scores['document_related'] = 1.0
        
        return scores
    
    def _calculate_document_relevance_score(self, features: ClassificationFeatures) -> float:
        """Calculate document relevance score from features."""
        relevance = 0.0
        
        # Legal terms indicate document relevance
        if features.legal_terms:
            relevance += min(len(features.legal_terms) * 0.1, 0.4)
        
        # Contract concepts strongly indicate document relevance
        if features.contract_concepts:
            relevance += min(len(features.contract_concepts) * 0.15, 0.5)
        
        # Question words indicate information seeking
        if features.question_words:
            relevance += 0.2
        
        # Formal language suggests document-related inquiry
        if features.formality_score > 0.6:
            relevance += 0.2
        
        return min(relevance, 1.0)
    
    def _assess_casualness_level(self, features: ClassificationFeatures) -> float:
        """Assess casualness level from features."""
        casualness = 0.0
        
        # Count casual indicators
        total_casual_indicators = len(features.casual_indicators)
        if total_casual_indicators > 0:
            casualness += min(total_casual_indicators * 0.2, 0.6)
        
        # Low formality indicates casualness
        casualness += (1.0 - features.formality_score) * 0.4
        
        # Short questions tend to be more casual
        if features.word_count < 5:
            casualness += 0.2
        
        return min(casualness, 1.0)
    
    def _requires_mta_expertise(self, features: ClassificationFeatures) -> bool:
        """Determine if MTA expertise is required."""
        # Lower threshold - even 1 MTA term can indicate need for expertise
        return len(features.mta_terms) >= 1
    
    def _find_legal_terms(self, text: str) -> List[str]:
        """Find legal terms in text."""
        terms = []
        for category in ['general', 'contract_concepts']:
            for term in self.LEGAL_TERMS[category]:
                if term in text:
                    terms.append(term)
        return terms
    
    def _find_mta_terms(self, text: str) -> List[str]:
        """Find MTA-specific terms in text."""
        terms = []
        for term in self.LEGAL_TERMS['mta']:
            if term in text:
                terms.append(term)
        return terms
    
    def _find_casual_indicators(self, text: str) -> List[str]:
        """Find casual language indicators in text."""
        indicators = []
        words = [word.strip('.,!?;:').lower() for word in text.split()]
        
        for category, terms in self.CASUAL_INDICATORS.items():
            for term in terms:
                # Check if the term appears as a whole word
                if term in words:
                    indicators.append(term)
                # Also check for multi-word terms
                elif ' ' in term and term in text.lower():
                    indicators.append(term)
        return indicators
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction - remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate basic sentiment score."""
        positive_words = ['good', 'great', 'excellent', 'perfect', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'wrong', 'problem', 'issue', 'error']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count + negative_count == 0:
            return 0.5  # Neutral
        
        return positive_count / (positive_count + negative_count)
    
    def _calculate_formality_score(self, text: str, words: List[str]) -> float:
        """Calculate formality score based on language patterns."""
        formality = 0.5  # Start neutral
        
        # Formal indicators
        formal_patterns = [
            r'\b(please|kindly|would you|could you|may I)\b',
            r'\b(regarding|concerning|pursuant to|in accordance with)\b',
            r'\b(therefore|furthermore|moreover|however|nevertheless)\b'
        ]
        
        for pattern in formal_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                formality += 0.1
        
        # Informal indicators reduce formality
        informal_count = len([word for word in words if word in ['yeah', 'ok', 'cool', 'awesome']])
        formality -= informal_count * 0.1
        
        # Longer sentences tend to be more formal
        if len(words) > 10:
            formality += 0.1
        
        return max(0.0, min(1.0, formality))