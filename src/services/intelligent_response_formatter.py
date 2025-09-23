"""
Intelligent Response Formatting System for Enhanced Contract Assistant

This module provides dynamic response structuring based on question complexity,
user expertise level detection, progressive disclosure, visual formatting,
and adaptive explanation depth.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
import json

from src.models.enhanced import EnhancedResponse, ToneType
from src.services.answer_quality_enhancer import QuestionComplexity, ExpertiseLevel
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ResponseStructure(Enum):
    """Different response structure types"""
    SIMPLE = "simple"
    STRUCTURED = "structured"
    DETAILED = "detailed"
    PROGRESSIVE = "progressive"
    EXPERT = "expert"


class VisualElement(Enum):
    """Visual formatting elements"""
    HEADERS = "headers"
    BULLET_POINTS = "bullet_points"
    NUMBERED_LISTS = "numbered_lists"
    TABLES = "tables"
    CALLOUTS = "callouts"
    SECTIONS = "sections"
    EMPHASIS = "emphasis"


@dataclass
class FormattingRule:
    """Rule for formatting responses"""
    condition: str
    structure: ResponseStructure
    visual_elements: List[VisualElement]
    explanation_depth: str  # shallow, medium, deep
    include_examples: bool
    include_warnings: bool
    max_sections: int


@dataclass
class UserProfile:
    """User profile for adaptive formatting"""
    expertise_level: ExpertiseLevel
    preferred_structure: ResponseStructure
    attention_span: str  # short, medium, long
    technical_comfort: str  # low, medium, high
    interaction_history: List[str]


@dataclass
class ContentSection:
    """Structured content section"""
    title: str
    content: str
    section_type: str
    priority: int
    visual_elements: List[VisualElement]
    expandable: bool = False
    prerequisites: List[str] = None


class IntelligentResponseFormatter:
    """
    Intelligent response formatter that provides:
    - Dynamic response structuring based on question complexity
    - User expertise level detection and adaptation
    - Progressive disclosure for complex topics
    - Visual formatting with appropriate elements
    - Adaptive explanation depth based on user needs
    """
    
    def __init__(self):
        """Initialize the intelligent response formatter"""
        self.formatting_rules = self._initialize_formatting_rules()
        self.visual_templates = self._initialize_visual_templates()
        self.expertise_indicators = self._initialize_expertise_indicators()
        self.complexity_thresholds = self._initialize_complexity_thresholds()
        
    def format_intelligent_response(
        self,
        response: EnhancedResponse,
        question: str,
        question_complexity: QuestionComplexity,
        user_profile: Optional[UserProfile] = None,
        context_history: Optional[List[str]] = None
    ) -> EnhancedResponse:
        """
        Format response intelligently based on complexity and user profile
        
        Args:
            response: Original response to format
            question: Original user question
            question_complexity: Assessed complexity of the question
            user_profile: User profile for personalization
            context_history: Previous interaction history
            
        Returns:
            Enhanced response with intelligent formatting
        """
        try:
            # Detect user expertise if not provided
            if not user_profile:
                user_profile = self._detect_user_profile(question, context_history)
            
            # Determine optimal response structure
            response_structure = self._determine_response_structure(
                question_complexity, user_profile, question
            )
            
            # Parse and structure content
            content_sections = self._parse_content_into_sections(
                response.content, response_structure, user_profile
            )
            
            # Apply progressive disclosure if needed
            if response_structure == ResponseStructure.PROGRESSIVE:
                content_sections = self._apply_progressive_disclosure(
                    content_sections, user_profile
                )
            
            # Format with visual elements
            formatted_content = self._apply_visual_formatting(
                content_sections, response_structure, user_profile
            )
            
            # Add adaptive explanations
            formatted_content = self._add_adaptive_explanations(
                formatted_content, question_complexity, user_profile
            )
            
            # Add contextual enhancements
            formatted_content = self._add_contextual_enhancements(
                formatted_content, question, response, user_profile
            )
            
            # Update response
            response.content = formatted_content
            response.context_used.extend([
                "intelligent_formatting",
                f"structure_{response_structure.value}",
                f"expertise_{user_profile.expertise_level.value}"
            ])
            
            # Add formatting metadata
            if not hasattr(response, 'formatting_metadata'):
                response.formatting_metadata = {}
            
            response.formatting_metadata.update({
                'structure_used': response_structure.value,
                'user_expertise': user_profile.expertise_level.value,
                'sections_count': len(content_sections),
                'visual_elements_used': self._get_used_visual_elements(content_sections)
            })
            
            logger.info(f"Applied {response_structure.value} formatting for {user_profile.expertise_level.value} user")
            return response
            
        except Exception as e:
            logger.error(f"Error in intelligent response formatting: {e}")
            # Return original response if formatting fails
            return response
    
    def _detect_user_profile(
        self, 
        question: str, 
        context_history: Optional[List[str]] = None
    ) -> UserProfile:
        """Detect user profile from question and interaction history"""
        
        # Detect expertise level
        expertise_level = self._detect_expertise_level(question, context_history)
        
        # Determine preferred structure based on question style
        preferred_structure = self._infer_preferred_structure(question)
        
        # Assess attention span from question length and complexity
        attention_span = self._assess_attention_span(question, context_history)
        
        # Determine technical comfort
        technical_comfort = self._assess_technical_comfort(question, context_history)
        
        return UserProfile(
            expertise_level=expertise_level,
            preferred_structure=preferred_structure,
            attention_span=attention_span,
            technical_comfort=technical_comfort,
            interaction_history=context_history or []
        )
    
    def _detect_expertise_level(
        self, 
        question: str, 
        context_history: Optional[List[str]] = None
    ) -> ExpertiseLevel:
        """Detect user expertise level from question and history"""
        
        question_lower = question.lower()
        
        # Expert indicators
        expert_score = 0
        for indicator in self.expertise_indicators['expert']:
            if indicator in question_lower:
                expert_score += 1
        
        # Advanced indicators
        advanced_score = 0
        for indicator in self.expertise_indicators['advanced']:
            if indicator in question_lower:
                advanced_score += 1
        
        # Beginner indicators
        beginner_score = 0
        for indicator in self.expertise_indicators['beginner']:
            if indicator in question_lower:
                beginner_score += 1
        
        # Consider context history
        if context_history:
            history_text = ' '.join(context_history).lower()
            
            # Boost scores based on historical patterns
            if any(term in history_text for term in self.expertise_indicators['expert']):
                expert_score += 1
            if any(term in history_text for term in self.expertise_indicators['advanced']):
                advanced_score += 1
            if any(term in history_text for term in self.expertise_indicators['beginner']):
                beginner_score += 1
        
        # Determine expertise level
        if expert_score >= 2:
            return ExpertiseLevel.EXPERT
        elif advanced_score >= 2 or (advanced_score >= 1 and expert_score >= 1):
            return ExpertiseLevel.ADVANCED
        elif beginner_score >= 2:
            return ExpertiseLevel.BEGINNER
        else:
            return ExpertiseLevel.INTERMEDIATE
    
    def _determine_response_structure(
        self,
        question_complexity: QuestionComplexity,
        user_profile: UserProfile,
        question: str
    ) -> ResponseStructure:
        """Determine optimal response structure"""
        
        # Apply formatting rules
        for rule in self.formatting_rules:
            if self._rule_matches(rule, question_complexity, user_profile, question):
                return rule.structure
        
        # Default structure based on complexity and expertise
        if question_complexity == QuestionComplexity.EXPERT:
            return ResponseStructure.EXPERT
        elif question_complexity == QuestionComplexity.COMPLEX:
            if user_profile.expertise_level in [ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT]:
                return ResponseStructure.DETAILED
            else:
                return ResponseStructure.PROGRESSIVE
        elif question_complexity == QuestionComplexity.MODERATE:
            return ResponseStructure.STRUCTURED
        else:
            return ResponseStructure.SIMPLE
    
    def _parse_content_into_sections(
        self,
        content: str,
        structure: ResponseStructure,
        user_profile: UserProfile
    ) -> List[ContentSection]:
        """Parse content into structured sections"""
        
        sections = []
        
        # Split content by existing headers or create logical sections
        if '##' in content:
            # Content already has headers
            parts = content.split('##')
            for i, part in enumerate(parts):
                if part.strip():
                    lines = part.strip().split('\n', 1)
                    title = lines[0].strip() if lines else f"Section {i+1}"
                    section_content = lines[1].strip() if len(lines) > 1 else ""
                    
                    section = ContentSection(
                        title=title,
                        content=section_content,
                        section_type=self._classify_section_type(title, section_content),
                        priority=self._assess_section_priority(title, section_content),
                        visual_elements=self._determine_visual_elements(section_content, structure)
                    )
                    sections.append(section)
        else:
            # Create logical sections from unstructured content
            sections = self._create_logical_sections(content, structure, user_profile)
        
        # Sort sections by priority
        sections.sort(key=lambda s: s.priority, reverse=True)
        
        return sections
    
    def _apply_progressive_disclosure(
        self,
        sections: List[ContentSection],
        user_profile: UserProfile
    ) -> List[ContentSection]:
        """Apply progressive disclosure to complex content"""
        
        # Mark sections as expandable based on complexity and user profile
        for section in sections:
            if section.priority < 3 and user_profile.attention_span == "short":
                section.expandable = True
            elif len(section.content) > 500 and user_profile.expertise_level == ExpertiseLevel.BEGINNER:
                section.expandable = True
                # Create summary for expandable sections
                section.content = self._create_section_summary(section.content) + "\n\n[Click to expand for details]"
        
        return sections
    
    def _apply_visual_formatting(
        self,
        sections: List[ContentSection],
        structure: ResponseStructure,
        user_profile: UserProfile
    ) -> str:
        """Apply visual formatting to content sections"""
        
        formatted_parts = []
        
        for section in sections:
            formatted_section = self._format_section(section, structure, user_profile)
            formatted_parts.append(formatted_section)
        
        # Join sections with appropriate spacing
        if structure in [ResponseStructure.DETAILED, ResponseStructure.EXPERT]:
            return "\n\n---\n\n".join(formatted_parts)
        else:
            return "\n\n".join(formatted_parts)
    
    def _format_section(
        self,
        section: ContentSection,
        structure: ResponseStructure,
        user_profile: UserProfile
    ) -> str:
        """Format an individual content section"""
        
        formatted_content = []
        
        # Add section header
        if structure != ResponseStructure.SIMPLE:
            if VisualElement.HEADERS in section.visual_elements:
                if structure == ResponseStructure.EXPERT:
                    formatted_content.append(f"### {section.title}")
                else:
                    formatted_content.append(f"## {section.title}")
            else:
                formatted_content.append(f"**{section.title}**")
        
        # Format section content
        content = section.content
        
        # Apply bullet points if appropriate
        if VisualElement.BULLET_POINTS in section.visual_elements:
            content = self._convert_to_bullet_points(content)
        
        # Apply numbered lists if appropriate
        if VisualElement.NUMBERED_LISTS in section.visual_elements:
            content = self._convert_to_numbered_list(content)
        
        # Apply emphasis if appropriate
        if VisualElement.EMPHASIS in section.visual_elements:
            content = self._apply_emphasis(content)
        
        # Apply callouts if appropriate
        if VisualElement.CALLOUTS in section.visual_elements:
            content = self._apply_callouts(content, section.section_type)
        
        formatted_content.append(content)
        
        # Add expandable indicator if needed
        if section.expandable:
            formatted_content.append("\n*[Expandable section - click for more details]*")
        
        return "\n\n".join(formatted_content)
    
    def _add_adaptive_explanations(
        self,
        content: str,
        question_complexity: QuestionComplexity,
        user_profile: UserProfile
    ) -> str:
        """Add adaptive explanations based on complexity and user profile"""
        
        # Add explanations for beginners
        if user_profile.expertise_level == ExpertiseLevel.BEGINNER:
            content = self._add_beginner_explanations(content)
        
        # Add technical details for experts
        elif user_profile.expertise_level == ExpertiseLevel.EXPERT:
            content = self._add_expert_details(content)
        
        # Add context for complex questions
        if question_complexity in [QuestionComplexity.COMPLEX, QuestionComplexity.EXPERT]:
            content = self._add_complexity_context(content)
        
        return content
    
    def _add_contextual_enhancements(
        self,
        content: str,
        question: str,
        response: EnhancedResponse,
        user_profile: UserProfile
    ) -> str:
        """Add contextual enhancements based on question and response type"""
        
        enhancements = []
        
        # Add navigation hints for long responses
        if len(content) > 1000:
            enhancements.append(self._create_navigation_hint())
        
        # Add related topics for structured responses
        if response.response_type == "document_analysis":
            related_topics = self._generate_related_topics(question, content)
            if related_topics:
                enhancements.append(f"\n\n**Related Topics to Explore:**\n{related_topics}")
        
        # Add confidence indicators for uncertain responses
        if response.confidence < 0.7:
            enhancements.append(self._create_confidence_indicator(response.confidence))
        
        # Add learning resources for beginners
        if user_profile.expertise_level == ExpertiseLevel.BEGINNER:
            learning_resources = self._suggest_learning_resources(question, content)
            if learning_resources:
                enhancements.append(f"\n\n**Learn More:**\n{learning_resources}")
        
        return content + "\n".join(enhancements)
    
    def _create_logical_sections(
        self,
        content: str,
        structure: ResponseStructure,
        user_profile: UserProfile
    ) -> List[ContentSection]:
        """Create logical sections from unstructured content"""
        
        sections = []
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if structure == ResponseStructure.SIMPLE:
            # Single section for simple structure
            sections.append(ContentSection(
                title="Analysis",
                content=content,
                section_type="main",
                priority=5,
                visual_elements=[VisualElement.EMPHASIS]
            ))
        
        elif structure in [ResponseStructure.STRUCTURED, ResponseStructure.DETAILED]:
            # Create logical sections based on content patterns
            current_section = None
            current_content = []
            
            for paragraph in paragraphs:
                section_type = self._identify_paragraph_type(paragraph)
                
                if section_type != (current_section.section_type if current_section else None):
                    # Start new section
                    if current_section and current_content:
                        current_section.content = '\n\n'.join(current_content)
                        sections.append(current_section)
                    
                    current_section = ContentSection(
                        title=self._get_section_title_for_type(section_type),
                        content="",
                        section_type=section_type,
                        priority=self._get_priority_for_type(section_type),
                        visual_elements=self._get_visual_elements_for_type(section_type)
                    )
                    current_content = []
                
                current_content.append(paragraph)
            
            # Add final section
            if current_section and current_content:
                current_section.content = '\n\n'.join(current_content)
                sections.append(current_section)
        
        return sections
    
    def _initialize_formatting_rules(self) -> List[FormattingRule]:
        """Initialize formatting rules for different scenarios"""
        return [
            FormattingRule(
                condition="beginner_simple",
                structure=ResponseStructure.SIMPLE,
                visual_elements=[VisualElement.BULLET_POINTS, VisualElement.EMPHASIS],
                explanation_depth="shallow",
                include_examples=True,
                include_warnings=True,
                max_sections=3
            ),
            FormattingRule(
                condition="expert_complex",
                structure=ResponseStructure.EXPERT,
                visual_elements=[VisualElement.HEADERS, VisualElement.NUMBERED_LISTS, VisualElement.TABLES],
                explanation_depth="deep",
                include_examples=False,
                include_warnings=False,
                max_sections=8
            ),
            FormattingRule(
                condition="intermediate_moderate",
                structure=ResponseStructure.STRUCTURED,
                visual_elements=[VisualElement.HEADERS, VisualElement.BULLET_POINTS, VisualElement.CALLOUTS],
                explanation_depth="medium",
                include_examples=True,
                include_warnings=True,
                max_sections=5
            ),
            FormattingRule(
                condition="complex_progressive",
                structure=ResponseStructure.PROGRESSIVE,
                visual_elements=[VisualElement.SECTIONS, VisualElement.CALLOUTS, VisualElement.EMPHASIS],
                explanation_depth="medium",
                include_examples=True,
                include_warnings=True,
                max_sections=6
            )
        ]
    
    def _initialize_visual_templates(self) -> Dict[str, str]:
        """Initialize visual formatting templates"""
        return {
            'callout_warning': "⚠️ **Important:** {content}",
            'callout_tip': "💡 **Tip:** {content}",
            'callout_note': "📝 **Note:** {content}",
            'emphasis_strong': "**{content}**",
            'emphasis_italic': "*{content}*",
            'bullet_point': "• {content}",
            'numbered_item': "{number}. {content}",
            'section_divider': "---",
            'expandable_section': "<details><summary>{title}</summary>\n{content}\n</details>"
        }
    
    def _initialize_expertise_indicators(self) -> Dict[str, List[str]]:
        """Initialize indicators for different expertise levels"""
        return {
            'expert': [
                'derivative work', 'ip assignment', 'indemnification', 'liability cap',
                'force majeure', 'governing law', 'jurisdiction', 'arbitration',
                'severability', 'waiver', 'counterpart execution', 'choice of law'
            ],
            'advanced': [
                'liability', 'intellectual property', 'termination', 'breach',
                'confidentiality', 'warranty', 'indemnity', 'damages',
                'compliance', 'regulatory', 'audit', 'certification'
            ],
            'beginner': [
                'what is', 'what does', 'can you explain', 'i don\'t understand',
                'simple terms', 'basic question', 'new to this', 'help me understand',
                'clarify', 'confused', 'not sure', 'beginner'
            ]
        }
    
    def _initialize_complexity_thresholds(self) -> Dict[str, int]:
        """Initialize thresholds for complexity assessment"""
        return {
            'word_count_simple': 10,
            'word_count_moderate': 20,
            'word_count_complex': 35,
            'technical_terms_moderate': 2,
            'technical_terms_complex': 4,
            'clauses_complex': 2
        }
    
    def _rule_matches(
        self,
        rule: FormattingRule,
        complexity: QuestionComplexity,
        profile: UserProfile,
        question: str
    ) -> bool:
        """Check if a formatting rule matches the current context"""
        
        condition_map = {
            'beginner_simple': (
                profile.expertise_level == ExpertiseLevel.BEGINNER and
                complexity == QuestionComplexity.SIMPLE
            ),
            'expert_complex': (
                profile.expertise_level == ExpertiseLevel.EXPERT and
                complexity in [QuestionComplexity.COMPLEX, QuestionComplexity.EXPERT]
            ),
            'intermediate_moderate': (
                profile.expertise_level == ExpertiseLevel.INTERMEDIATE and
                complexity == QuestionComplexity.MODERATE
            ),
            'complex_progressive': (
                complexity == QuestionComplexity.COMPLEX and
                profile.attention_span == "short"
            )
        }
        
        return condition_map.get(rule.condition, False)
    
    def _classify_section_type(self, title: str, content: str) -> str:
        """Classify the type of a content section"""
        title_lower = title.lower()
        content_lower = content.lower()
        
        if 'evidence' in title_lower or 'direct' in title_lower:
            return 'evidence'
        elif 'explanation' in title_lower or 'plain english' in title_lower:
            return 'explanation'
        elif 'implication' in title_lower or 'analysis' in title_lower:
            return 'analysis'
        elif 'risk' in title_lower or 'warning' in title_lower:
            return 'risk'
        elif 'recommendation' in title_lower or 'action' in title_lower:
            return 'recommendation'
        elif 'example' in title_lower or 'context' in title_lower:
            return 'example'
        else:
            return 'general'
    
    def _assess_section_priority(self, title: str, content: str) -> int:
        """Assess the priority of a content section (1-5, 5 being highest)"""
        title_lower = title.lower()
        
        priority_map = {
            'evidence': 5,
            'explanation': 4,
            'analysis': 4,
            'risk': 5,
            'recommendation': 4,
            'example': 2,
            'general': 3
        }
        
        section_type = self._classify_section_type(title, content)
        return priority_map.get(section_type, 3)
    
    def _determine_visual_elements(
        self,
        content: str,
        structure: ResponseStructure
    ) -> List[VisualElement]:
        """Determine appropriate visual elements for content"""
        elements = []
        
        # Always include headers for structured responses
        if structure != ResponseStructure.SIMPLE:
            elements.append(VisualElement.HEADERS)
        
        # Add bullet points for lists
        if self._has_list_content(content):
            elements.append(VisualElement.BULLET_POINTS)
        
        # Add emphasis for important content
        if self._has_important_content(content):
            elements.append(VisualElement.EMPHASIS)
        
        # Add callouts for warnings or tips
        if self._has_warning_content(content):
            elements.append(VisualElement.CALLOUTS)
        
        return elements
    
    def _infer_preferred_structure(self, question: str) -> ResponseStructure:
        """Infer preferred structure from question style"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['step by step', 'detailed', 'comprehensive']):
            return ResponseStructure.DETAILED
        elif any(word in question_lower for word in ['simple', 'basic', 'quick']):
            return ResponseStructure.SIMPLE
        elif any(word in question_lower for word in ['explain', 'break down', 'understand']):
            return ResponseStructure.PROGRESSIVE
        else:
            return ResponseStructure.STRUCTURED
    
    def _assess_attention_span(
        self,
        question: str,
        context_history: Optional[List[str]] = None
    ) -> str:
        """Assess user's attention span from question and history"""
        
        # Short questions might indicate short attention span
        if len(question.split()) < 8:
            return "short"
        
        # Very long questions might indicate long attention span
        if len(question.split()) > 25:
            return "long"
        
        # Check for indicators in question
        if any(word in question.lower() for word in ['quick', 'brief', 'summary']):
            return "short"
        elif any(word in question.lower() for word in ['detailed', 'comprehensive', 'thorough']):
            return "long"
        
        return "medium"
    
    def _assess_technical_comfort(
        self,
        question: str,
        context_history: Optional[List[str]] = None
    ) -> str:
        """Assess user's technical comfort level"""
        
        question_lower = question.lower()
        
        # High comfort indicators
        if any(term in question_lower for term in self.expertise_indicators['expert']):
            return "high"
        
        # Low comfort indicators
        if any(phrase in question_lower for phrase in ['simple terms', 'layman', 'non-technical']):
            return "low"
        
        return "medium"
    
    def _convert_to_bullet_points(self, content: str) -> str:
        """Convert content to bullet point format where appropriate"""
        lines = content.split('\n')
        converted_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('•') and not line.startswith('-'):
                # Check if line looks like a list item
                if (line.startswith(('1.', '2.', '3.', '4.', '5.')) or
                    any(line.startswith(word) for word in ['First', 'Second', 'Third', 'Additionally', 'Furthermore'])):
                    converted_lines.append(f"• {line}")
                else:
                    converted_lines.append(line)
            else:
                converted_lines.append(line)
        
        return '\n'.join(converted_lines)
    
    def _convert_to_numbered_list(self, content: str) -> str:
        """Convert content to numbered list format where appropriate"""
        lines = content.split('\n')
        converted_lines = []
        counter = 1
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('1.', '2.', '3.')):
                # Check if line looks like a sequential item
                if any(line.startswith(word) for word in ['First', 'Second', 'Third', 'Next', 'Then', 'Finally']):
                    converted_lines.append(f"{counter}. {line}")
                    counter += 1
                else:
                    converted_lines.append(line)
            else:
                converted_lines.append(line)
        
        return '\n'.join(converted_lines)
    
    def _apply_emphasis(self, content: str) -> str:
        """Apply emphasis to important parts of content"""
        # Emphasize important legal terms
        important_terms = [
            'liability', 'indemnification', 'breach', 'termination',
            'confidential', 'proprietary', 'intellectual property'
        ]
        
        emphasized_content = content
        for term in important_terms:
            pattern = rf'\b{re.escape(term)}\b'
            emphasized_content = re.sub(
                pattern,
                f"**{term}**",
                emphasized_content,
                flags=re.IGNORECASE
            )
        
        return emphasized_content
    
    def _apply_callouts(self, content: str, section_type: str) -> str:
        """Apply callouts based on section type and content"""
        
        if section_type == 'risk':
            return f"⚠️ **Important Risk Consideration:**\n{content}"
        elif section_type == 'recommendation':
            return f"💡 **Recommended Action:**\n{content}"
        elif 'warning' in content.lower() or 'caution' in content.lower():
            return f"⚠️ **Warning:**\n{content}"
        elif 'tip' in content.lower() or 'suggestion' in content.lower():
            return f"💡 **Tip:**\n{content}"
        else:
            return content
    
    def _create_section_summary(self, content: str) -> str:
        """Create a summary for expandable sections"""
        # Simple summary - take first sentence or first 100 characters
        sentences = content.split('. ')
        if sentences:
            return sentences[0] + ('.' if not sentences[0].endswith('.') else '')
        else:
            return content[:100] + ('...' if len(content) > 100 else '')
    
    def _add_beginner_explanations(self, content: str) -> str:
        """Add explanations for beginners"""
        # Add glossary for technical terms
        technical_terms = re.findall(r'\b(?:liability|indemnification|breach|proprietary)\b', content, re.IGNORECASE)
        
        if technical_terms:
            glossary = "\n\n**Key Terms:**\n"
            term_definitions = {
                'liability': 'Legal responsibility for damages or losses',
                'indemnification': 'Protection from legal claims and costs',
                'breach': 'Failure to fulfill contract obligations',
                'proprietary': 'Privately owned and controlled'
            }
            
            for term in set(term.lower() for term in technical_terms):
                if term in term_definitions:
                    glossary += f"• **{term.title()}**: {term_definitions[term]}\n"
            
            content += glossary
        
        return content
    
    def _add_expert_details(self, content: str) -> str:
        """Add technical details for experts"""
        # Add technical context and legal precedents
        if 'liability' in content.lower():
            content += "\n\n*Technical Note: Consider interaction with insurance coverage and corporate structure for liability allocation.*"
        
        if 'intellectual property' in content.lower():
            content += "\n\n*Technical Note: Evaluate patent prosecution strategies and freedom-to-operate considerations.*"
        
        return content
    
    def _add_complexity_context(self, content: str) -> str:
        """Add context for complex questions"""
        context_note = "\n\n*This is a complex topic with multiple considerations. The analysis above covers the primary aspects, but additional factors may apply to your specific situation.*"
        return content + context_note
    
    def _create_navigation_hint(self) -> str:
        """Create navigation hint for long responses"""
        return "\n\n*📍 **Navigation Tip:** This is a comprehensive response. Use the section headers to jump to the information most relevant to your needs.*"
    
    def _generate_related_topics(self, question: str, content: str) -> str:
        """Generate related topics to explore"""
        question_lower = question.lower()
        content_lower = content.lower()
        
        related = []
        
        if 'liability' in question_lower or 'liability' in content_lower:
            related.append("• Indemnification provisions and risk allocation")
        
        if 'termination' in question_lower or 'termination' in content_lower:
            related.append("• Post-termination obligations and survival clauses")
        
        if 'intellectual property' in question_lower or 'ip' in content_lower:
            related.append("• Patent prosecution and licensing strategies")
        
        return '\n'.join(related) if related else ""
    
    def _create_confidence_indicator(self, confidence: float) -> str:
        """Create confidence indicator for uncertain responses"""
        if confidence < 0.5:
            return "\n\n*⚠️ **Confidence Note:** This analysis is based on limited information. Consider consulting with legal counsel for definitive guidance.*"
        elif confidence < 0.7:
            return "\n\n*📝 **Note:** This analysis covers the most likely interpretation. Additional context may affect the conclusions.*"
        else:
            return ""
    
    def _suggest_learning_resources(self, question: str, content: str) -> str:
        """Suggest learning resources for beginners"""
        resources = []
        
        if 'contract' in question.lower():
            resources.append("• Contract Law Basics: Understanding key terms and concepts")
        
        if 'liability' in content.lower():
            resources.append("• Risk Management: Understanding liability and insurance")
        
        if 'intellectual property' in content.lower():
            resources.append("• IP Fundamentals: Patents, copyrights, and trade secrets")
        
        return '\n'.join(resources) if resources else ""
    
    def _get_used_visual_elements(self, sections: List[ContentSection]) -> List[str]:
        """Get list of visual elements used in sections"""
        used_elements = set()
        for section in sections:
            used_elements.update(element.value for element in section.visual_elements)
        return list(used_elements)
    
    def _identify_paragraph_type(self, paragraph: str) -> str:
        """Identify the type of a paragraph"""
        paragraph_lower = paragraph.lower()
        
        if any(word in paragraph_lower for word in ['evidence', 'states', 'according to']):
            return 'evidence'
        elif any(word in paragraph_lower for word in ['means', 'in other words', 'simply put']):
            return 'explanation'
        elif any(word in paragraph_lower for word in ['implication', 'this means', 'therefore']):
            return 'analysis'
        elif any(word in paragraph_lower for word in ['risk', 'danger', 'warning', 'caution']):
            return 'risk'
        elif any(word in paragraph_lower for word in ['recommend', 'suggest', 'should', 'consider']):
            return 'recommendation'
        elif any(word in paragraph_lower for word in ['example', 'for instance', 'such as']):
            return 'example'
        else:
            return 'general'
    
    def _get_section_title_for_type(self, section_type: str) -> str:
        """Get appropriate title for section type"""
        title_map = {
            'evidence': '📋 Direct Evidence',
            'explanation': '💡 Plain English Explanation',
            'analysis': '🎯 Key Implications',
            'risk': '⚠️ Risk Assessment',
            'recommendation': '🎯 Recommendations',
            'example': '📚 Examples & Context',
            'general': '📄 Analysis'
        }
        return title_map.get(section_type, '📄 Information')
    
    def _get_priority_for_type(self, section_type: str) -> int:
        """Get priority for section type"""
        priority_map = {
            'evidence': 5,
            'explanation': 4,
            'analysis': 4,
            'risk': 5,
            'recommendation': 4,
            'example': 2,
            'general': 3
        }
        return priority_map.get(section_type, 3)
    
    def _get_visual_elements_for_type(self, section_type: str) -> List[VisualElement]:
        """Get appropriate visual elements for section type"""
        element_map = {
            'evidence': [VisualElement.HEADERS, VisualElement.EMPHASIS],
            'explanation': [VisualElement.HEADERS, VisualElement.BULLET_POINTS],
            'analysis': [VisualElement.HEADERS, VisualElement.BULLET_POINTS],
            'risk': [VisualElement.HEADERS, VisualElement.CALLOUTS],
            'recommendation': [VisualElement.HEADERS, VisualElement.NUMBERED_LISTS],
            'example': [VisualElement.HEADERS, VisualElement.BULLET_POINTS],
            'general': [VisualElement.HEADERS]
        }
        return element_map.get(section_type, [VisualElement.HEADERS])
    
    def _has_list_content(self, content: str) -> bool:
        """Check if content has list-like structure"""
        return (content.count('\n') >= 2 and 
                any(line.strip().startswith(('•', '-', '1.', '2.', 'First', 'Second')) 
                    for line in content.split('\n')))
    
    def _has_important_content(self, content: str) -> bool:
        """Check if content has important information that should be emphasized"""
        important_indicators = ['important', 'critical', 'essential', 'warning', 'note', 'caution']
        return any(indicator in content.lower() for indicator in important_indicators)
    
    def _has_warning_content(self, content: str) -> bool:
        """Check if content has warning or cautionary information"""
        warning_indicators = ['warning', 'caution', 'risk', 'danger', 'important', 'note']
        return any(indicator in content.lower() for indicator in warning_indicators)