"""
Answer Quality Enhancement System for Enhanced Contract Assistant

This module provides comprehensive answer quality enhancement with rich evidence citation,
multi-layered explanations, contextual examples, risk assessments, and actionable recommendations.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import re
import json
from enum import Enum

from src.models.enhanced import EnhancedResponse, ResponseType, ToneType
from src.models.document import Document
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class QuestionComplexity(Enum):
    """Question complexity levels for adaptive response formatting"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


class ExpertiseLevel(Enum):
    """User expertise levels for response adaptation"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class EvidenceCitation:
    """Structured evidence citation with source tracking"""
    text: str
    section: str
    page_number: Optional[int]
    confidence: float
    context: str
    relevance_score: float


@dataclass
class RiskAssessment:
    """Risk assessment for contract provisions"""
    risk_level: str  # low, medium, high, critical
    risk_category: str
    description: str
    potential_impact: str
    mitigation_strategies: List[str]
    likelihood: str


@dataclass
class ActionableRecommendation:
    """Actionable recommendations for contract provisions"""
    priority: str  # low, medium, high, urgent
    category: str
    action: str
    rationale: str
    timeline: str
    stakeholders: List[str]


@dataclass
class EnhancedAnalysis:
    """Comprehensive enhanced analysis structure"""
    direct_evidence: List[EvidenceCitation]
    plain_english_explanation: str
    implications: List[str]
    contextual_examples: List[str]
    risk_assessments: List[RiskAssessment]
    recommendations: List[ActionableRecommendation]
    cross_references: List[str]
    compliance_requirements: List[str]


class AnswerQualityEnhancer:
    """
    Comprehensive answer quality enhancement system that provides:
    - Rich evidence citation with comprehensive source tracking
    - Multi-layered explanations (direct evidence + plain English + implications)
    - Contextual examples and analogies
    - Risk assessments and mitigation strategies
    - Actionable recommendations with priority levels
    """
    
    def __init__(self):
        """Initialize the answer quality enhancer"""
        self.risk_keywords = self._initialize_risk_keywords()
        self.compliance_frameworks = self._initialize_compliance_frameworks()
        self.example_templates = self._initialize_example_templates()
        
    def enhance_response_quality(
        self,
        response: EnhancedResponse,
        document: Document,
        question: str,
        user_expertise: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE,
        question_complexity: Optional[QuestionComplexity] = None
    ) -> EnhancedResponse:
        """
        Enhance response quality with comprehensive analysis and formatting
        
        Args:
            response: Original response to enhance
            document: Source document for analysis
            question: Original user question
            user_expertise: User's expertise level for response adaptation
            question_complexity: Complexity level of the question
            
        Returns:
            Enhanced response with rich analysis and formatting
        """
        try:
            # Determine question complexity if not provided
            if question_complexity is None:
                question_complexity = self._assess_question_complexity(question)
            
            # Extract and enhance evidence
            enhanced_analysis = self._create_enhanced_analysis(
                response, document, question, user_expertise, question_complexity
            )
            
            # Format response based on complexity and expertise
            enhanced_content = self._format_enhanced_response(
                enhanced_analysis, user_expertise, question_complexity
            )
            
            # Generate contextual suggestions
            enhanced_suggestions = self._generate_enhanced_suggestions(
                question, enhanced_analysis, document
            )
            
            # Update response with enhancements
            response.content = enhanced_content
            response.suggestions = enhanced_suggestions
            response.context_used.extend([
                "quality_enhancement",
                f"expertise_{user_expertise.value}",
                f"complexity_{question_complexity.value}"
            ])
            
            # Add metadata for quality tracking
            if not hasattr(response, 'quality_metrics'):
                response.quality_metrics = {}
            
            response.quality_metrics.update({
                'evidence_citations': len(enhanced_analysis.direct_evidence),
                'risk_assessments': len(enhanced_analysis.risk_assessments),
                'recommendations': len(enhanced_analysis.recommendations),
                'cross_references': len(enhanced_analysis.cross_references),
                'enhancement_timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"Enhanced response quality with {len(enhanced_analysis.direct_evidence)} evidence citations")
            return response
            
        except Exception as e:
            logger.error(f"Error enhancing response quality: {e}")
            # Return original response if enhancement fails
            return response
    
    def _create_enhanced_analysis(
        self,
        response: EnhancedResponse,
        document: Document,
        question: str,
        user_expertise: ExpertiseLevel,
        question_complexity: QuestionComplexity
    ) -> EnhancedAnalysis:
        """Create comprehensive enhanced analysis"""
        
        # Extract evidence citations from response and document
        evidence_citations = self._extract_evidence_citations(response, document)
        
        # Generate plain English explanation
        plain_english = self._generate_plain_english_explanation(
            response.content, user_expertise
        )
        
        # Extract and enhance implications
        implications = self._extract_and_enhance_implications(
            response.content, document, question
        )
        
        # Generate contextual examples
        contextual_examples = self._generate_contextual_examples(
            question, response.content, document
        )
        
        # Perform risk assessment
        risk_assessments = self._perform_risk_assessment(
            response.content, document, question
        )
        
        # Generate actionable recommendations
        recommendations = self._generate_actionable_recommendations(
            response.content, document, question, risk_assessments
        )
        
        # Find cross-references
        cross_references = self._find_cross_references(
            response.content, document
        )
        
        # Identify compliance requirements
        compliance_requirements = self._identify_compliance_requirements(
            response.content, document
        )
        
        return EnhancedAnalysis(
            direct_evidence=evidence_citations,
            plain_english_explanation=plain_english,
            implications=implications,
            contextual_examples=contextual_examples,
            risk_assessments=risk_assessments,
            recommendations=recommendations,
            cross_references=cross_references,
            compliance_requirements=compliance_requirements
        )
    
    def _extract_evidence_citations(
        self,
        response: EnhancedResponse,
        document: Document
    ) -> List[EvidenceCitation]:
        """Extract and enhance evidence citations"""
        citations = []
        
        # Parse existing response for evidence
        content = response.content
        
        # Look for quoted text or specific references
        quoted_patterns = [
            r'"([^"]+)"',  # Text in quotes
            r'states that "([^"]+)"',  # Explicit statements
            r'according to the (?:agreement|contract|document)[,:]?\s*"([^"]+)"'
        ]
        
        for pattern in quoted_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                quoted_text = match.group(1)
                
                # Find this text in the document
                section_info = self._find_text_in_document(quoted_text, document)
                
                if section_info:
                    citation = EvidenceCitation(
                        text=quoted_text,
                        section=section_info.get('section', 'Unknown'),
                        page_number=section_info.get('page', None),
                        confidence=0.9,  # High confidence for direct quotes
                        context=section_info.get('context', ''),
                        relevance_score=0.8
                    )
                    citations.append(citation)
        
        # If no direct citations found, create general document citations
        if not citations and document:
            # Extract key phrases from response that might be in document
            key_phrases = self._extract_key_phrases(content)
            
            for phrase in key_phrases[:3]:  # Limit to top 3
                if self._phrase_in_document(phrase, document):
                    citation = EvidenceCitation(
                        text=phrase,
                        section="Document Content",
                        page_number=None,
                        confidence=0.7,
                        context="Referenced in contract analysis",
                        relevance_score=0.6
                    )
                    citations.append(citation)
        
        return citations
    
    def _generate_plain_english_explanation(
        self,
        content: str,
        user_expertise: ExpertiseLevel
    ) -> str:
        """Generate plain English explanation adapted to user expertise"""
        
        # Extract technical terms and legal jargon
        technical_terms = self._identify_technical_terms(content)
        
        explanation_parts = []
        
        if user_expertise in [ExpertiseLevel.BEGINNER, ExpertiseLevel.INTERMEDIATE]:
            explanation_parts.append("In simple terms:")
            
            # Simplify complex legal concepts
            simplified_content = self._simplify_legal_language(content)
            explanation_parts.append(simplified_content)
            
            # Add term definitions for beginners
            if user_expertise == ExpertiseLevel.BEGINNER and technical_terms:
                explanation_parts.append("\n**Key Terms:**")
                for term in technical_terms[:3]:  # Limit to 3 most important
                    definition = self._get_term_definition(term)
                    explanation_parts.append(f"- **{term}**: {definition}")
        
        else:  # Advanced/Expert users
            # Provide more technical detail and context
            explanation_parts.append("Technical Analysis:")
            explanation_parts.append(self._enhance_technical_detail(content))
        
        return "\n".join(explanation_parts)
    
    def _extract_and_enhance_implications(
        self,
        content: str,
        document: Document,
        question: str
    ) -> List[str]:
        """Extract and enhance implications with deeper analysis"""
        implications = []
        
        # Look for existing implications in content
        implication_patterns = [
            r'[Tt]his means that ([^.]+)',
            r'[Tt]he implication is ([^.]+)',
            r'[Aa]s a result[,]? ([^.]+)',
            r'[Tt]herefore[,]? ([^.]+)'
        ]
        
        for pattern in implication_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                implications.append(match.group(1).strip())
        
        # Generate additional implications based on content analysis
        content_lower = content.lower()
        
        # Contract-specific implications
        if 'liability' in content_lower:
            implications.append("This affects your potential financial exposure and risk management strategy")
        
        if 'termination' in content_lower:
            implications.append("Consider the practical steps needed to wind down the relationship if this clause is triggered")
        
        if 'intellectual property' in content_lower or 'ip' in content_lower:
            implications.append("This impacts ownership and commercialization rights for any innovations or improvements")
        
        if 'confidentiality' in content_lower:
            implications.append("This creates ongoing obligations that extend beyond the contract term")
        
        # MTA-specific implications
        if 'material transfer' in content_lower or 'research use' in content_lower:
            implications.append("This affects your ability to share materials with collaborators and publish research results")
        
        # Business implications
        if 'payment' in content_lower or 'fee' in content_lower:
            implications.append("Consider the cash flow impact and budget allocation for these financial obligations")
        
        # Remove duplicates and limit
        unique_implications = []
        seen = set()
        for impl in implications:
            if impl.lower() not in seen:
                unique_implications.append(impl)
                seen.add(impl.lower())
        
        return unique_implications[:5]  # Limit to 5 most important
    
    def _generate_contextual_examples(
        self,
        question: str,
        content: str,
        document: Document
    ) -> List[str]:
        """Generate contextual examples and analogies"""
        examples = []
        
        question_lower = question.lower()
        content_lower = content.lower()
        
        # Contract-specific examples
        if 'liability' in question_lower or 'liability' in content_lower:
            examples.append(
                "For example, if a software defect causes $100,000 in damages, "
                "a liability cap of $50,000 would limit your maximum exposure to that amount."
            )
        
        if 'termination' in question_lower:
            examples.append(
                "For instance, if the contract requires 30 days notice for termination, "
                "you must provide written notice by March 1st to terminate by March 31st."
            )
        
        if 'intellectual property' in question_lower or 'ip' in question_lower:
            examples.append(
                "As an analogy, think of IP ownership like property ownership - "
                "the contract determines who 'owns' any innovations created during the collaboration."
            )
        
        # MTA-specific examples
        if 'material transfer' in question_lower or 'research use' in question_lower:
            examples.append(
                "For example, if you receive cell lines for research, you typically cannot "
                "share them with other labs without the provider's permission."
            )
        
        if 'derivative' in question_lower:
            examples.append(
                "Think of derivatives like a recipe modification - if you receive a basic recipe (original material) "
                "and create an improved version, the contract determines who owns that improvement."
            )
        
        # Business context examples
        if 'payment' in question_lower:
            examples.append(
                "For instance, if payments are due 'net 30', you have 30 days from the invoice date to pay, "
                "not 30 days from when you receive the invoice."
            )
        
        return examples[:3]  # Limit to 3 most relevant examples
    
    def _perform_risk_assessment(
        self,
        content: str,
        document: Document,
        question: str
    ) -> List[RiskAssessment]:
        """Perform comprehensive risk assessment"""
        risks = []
        content_lower = content.lower()
        
        # Financial risks
        if any(term in content_lower for term in ['unlimited liability', 'no liability cap', 'full damages']):
            risks.append(RiskAssessment(
                risk_level="high",
                risk_category="financial",
                description="Unlimited financial liability exposure",
                potential_impact="Could result in significant financial losses exceeding contract value",
                mitigation_strategies=[
                    "Negotiate liability caps",
                    "Obtain appropriate insurance coverage",
                    "Consider indemnification provisions"
                ],
                likelihood="medium"
            ))
        
        # IP risks
        if any(term in content_lower for term in ['broad ip assignment', 'all improvements', 'derivative ownership']):
            risks.append(RiskAssessment(
                risk_level="medium",
                risk_category="intellectual_property",
                description="Broad intellectual property assignment or claims",
                potential_impact="Loss of ownership rights to innovations and improvements",
                mitigation_strategies=[
                    "Negotiate carve-outs for background IP",
                    "Limit assignment to specific improvements",
                    "Retain rights to independently developed IP"
                ],
                likelihood="high"
            ))
        
        # Operational risks
        if any(term in content_lower for term in ['exclusive', 'sole source', 'no alternatives']):
            risks.append(RiskAssessment(
                risk_level="medium",
                risk_category="operational",
                description="Dependency on single provider or exclusive arrangements",
                potential_impact="Business disruption if provider fails to perform",
                mitigation_strategies=[
                    "Negotiate performance guarantees",
                    "Include termination rights for non-performance",
                    "Develop backup supplier relationships"
                ],
                likelihood="low"
            ))
        
        # Compliance risks
        if any(term in content_lower for term in ['regulatory', 'compliance', 'government approval']):
            risks.append(RiskAssessment(
                risk_level="medium",
                risk_category="compliance",
                description="Regulatory compliance requirements",
                potential_impact="Potential fines, penalties, or business restrictions",
                mitigation_strategies=[
                    "Establish compliance monitoring procedures",
                    "Regular legal review of regulatory changes",
                    "Maintain documentation and audit trails"
                ],
                likelihood="medium"
            ))
        
        return risks
    
    def _generate_actionable_recommendations(
        self,
        content: str,
        document: Document,
        question: str,
        risk_assessments: List[RiskAssessment]
    ) -> List[ActionableRecommendation]:
        """Generate actionable recommendations with priorities"""
        recommendations = []
        content_lower = content.lower()
        
        # High-priority recommendations based on risks
        for risk in risk_assessments:
            if risk.risk_level in ["high", "critical"]:
                recommendations.append(ActionableRecommendation(
                    priority="high",
                    category=risk.risk_category,
                    action=f"Address {risk.description.lower()} through contract negotiation",
                    rationale=f"Mitigate {risk.risk_level} risk with {risk.potential_impact.lower()}",
                    timeline="Before contract execution",
                    stakeholders=["Legal team", "Business owner"]
                ))
        
        # Contract-specific recommendations
        if 'liability' in content_lower:
            recommendations.append(ActionableRecommendation(
                priority="medium",
                category="risk_management",
                action="Review and negotiate liability limitations",
                rationale="Protect against excessive financial exposure",
                timeline="During contract negotiation",
                stakeholders=["Legal counsel", "Risk management", "Finance"]
            ))
        
        if 'termination' in content_lower:
            recommendations.append(ActionableRecommendation(
                priority="medium",
                category="contract_management",
                action="Establish termination procedures and timeline tracking",
                rationale="Ensure compliance with notice requirements and smooth contract exit",
                timeline="Within 30 days of contract execution",
                stakeholders=["Contract manager", "Operations team"]
            ))
        
        if 'intellectual property' in content_lower:
            recommendations.append(ActionableRecommendation(
                priority="high",
                category="intellectual_property",
                action="Conduct IP audit and establish protection protocols",
                rationale="Protect valuable intellectual property assets and innovations",
                timeline="Before sharing any proprietary information",
                stakeholders=["IP counsel", "R&D team", "Business development"]
            ))
        
        # MTA-specific recommendations
        if 'material transfer' in content_lower:
            recommendations.append(ActionableRecommendation(
                priority="medium",
                category="research_compliance",
                action="Establish material handling and tracking procedures",
                rationale="Ensure compliance with transfer restrictions and usage limitations",
                timeline="Before material receipt",
                stakeholders=["Research team", "Compliance officer", "Lab manager"]
            ))
        
        return recommendations[:5]  # Limit to 5 most important
    
    def _find_cross_references(
        self,
        content: str,
        document: Document
    ) -> List[str]:
        """Find cross-references to other sections or documents"""
        cross_refs = []
        
        # Look for section references
        section_patterns = [
            r'[Ss]ection (\d+(?:\.\d+)*)',
            r'[Aa]rticle (\d+(?:\.\d+)*)',
            r'[Pp]aragraph (\d+(?:\.\d+)*)',
            r'[Cc]lause (\d+(?:\.\d+)*)'
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                cross_refs.append(f"See Section {match.group(1)}")
        
        # Look for exhibit references
        exhibit_patterns = [
            r'[Ee]xhibit ([A-Z])',
            r'[Aa]ppendix ([A-Z])',
            r'[Ss]chedule (\d+)'
        ]
        
        for pattern in exhibit_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                cross_refs.append(f"Reference to Exhibit {match.group(1)}")
        
        return list(set(cross_refs))  # Remove duplicates
    
    def _identify_compliance_requirements(
        self,
        content: str,
        document: Document
    ) -> List[str]:
        """Identify compliance requirements and regulatory obligations"""
        requirements = []
        content_lower = content.lower()
        
        # Common compliance areas
        if 'gdpr' in content_lower or 'data protection' in content_lower:
            requirements.append("GDPR compliance for personal data processing")
        
        if 'hipaa' in content_lower or 'health information' in content_lower:
            requirements.append("HIPAA compliance for protected health information")
        
        if 'sox' in content_lower or 'sarbanes' in content_lower:
            requirements.append("Sarbanes-Oxley compliance for financial reporting")
        
        if 'export control' in content_lower or 'itar' in content_lower:
            requirements.append("Export control and ITAR compliance requirements")
        
        if 'environmental' in content_lower:
            requirements.append("Environmental compliance and reporting obligations")
        
        # Research-specific compliance
        if 'irb' in content_lower or 'institutional review' in content_lower:
            requirements.append("IRB approval for human subjects research")
        
        if 'iacuc' in content_lower or 'animal care' in content_lower:
            requirements.append("IACUC approval for animal research protocols")
        
        return requirements
    
    def _format_enhanced_response(
        self,
        analysis: EnhancedAnalysis,
        user_expertise: ExpertiseLevel,
        question_complexity: QuestionComplexity
    ) -> str:
        """Format enhanced response based on user expertise and question complexity"""
        
        sections = []
        
        # Direct Evidence Section
        if analysis.direct_evidence:
            sections.append("## 📋 Direct Evidence")
            for i, evidence in enumerate(analysis.direct_evidence[:3], 1):
                sections.append(f"**{i}.** \"{evidence.text}\"")
                if evidence.section != "Unknown":
                    sections.append(f"   *Source: {evidence.section}*")
        
        # Plain English Explanation
        if analysis.plain_english_explanation:
            sections.append("## 💡 Plain English Explanation")
            sections.append(analysis.plain_english_explanation)
        
        # Implications and Analysis
        if analysis.implications:
            sections.append("## 🎯 Key Implications")
            for impl in analysis.implications:
                sections.append(f"• {impl}")
        
        # Contextual Examples (for complex questions or beginner users)
        if analysis.contextual_examples and (
            question_complexity in [QuestionComplexity.COMPLEX, QuestionComplexity.EXPERT] or
            user_expertise == ExpertiseLevel.BEGINNER
        ):
            sections.append("## 📚 Examples & Context")
            for example in analysis.contextual_examples:
                sections.append(f"• {example}")
        
        # Risk Assessment (for intermediate+ users)
        if analysis.risk_assessments and user_expertise != ExpertiseLevel.BEGINNER:
            sections.append("## ⚠️ Risk Assessment")
            for risk in analysis.risk_assessments:
                sections.append(f"**{risk.risk_category.title()} Risk ({risk.risk_level.upper()}):** {risk.description}")
                if risk.mitigation_strategies:
                    sections.append("   *Mitigation strategies:*")
                    for strategy in risk.mitigation_strategies[:2]:
                        sections.append(f"   - {strategy}")
        
        # Actionable Recommendations
        if analysis.recommendations:
            sections.append("## 🎯 Actionable Recommendations")
            high_priority = [r for r in analysis.recommendations if r.priority == "high"]
            medium_priority = [r for r in analysis.recommendations if r.priority == "medium"]
            
            if high_priority:
                sections.append("**High Priority:**")
                for rec in high_priority:
                    sections.append(f"• {rec.action}")
                    sections.append(f"  *Timeline: {rec.timeline}*")
            
            if medium_priority and user_expertise in [ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT]:
                sections.append("**Medium Priority:**")
                for rec in medium_priority[:2]:
                    sections.append(f"• {rec.action}")
        
        # Cross-references (for expert users)
        if analysis.cross_references and user_expertise == ExpertiseLevel.EXPERT:
            sections.append("## 🔗 Cross-References")
            for ref in analysis.cross_references:
                sections.append(f"• {ref}")
        
        # Compliance Requirements
        if analysis.compliance_requirements:
            sections.append("## 📋 Compliance Requirements")
            for req in analysis.compliance_requirements:
                sections.append(f"• {req}")
        
        return "\n\n".join(sections)
    
    def _generate_enhanced_suggestions(
        self,
        question: str,
        analysis: EnhancedAnalysis,
        document: Document
    ) -> List[str]:
        """Generate enhanced contextual suggestions"""
        suggestions = []
        
        # Based on risk assessments
        for risk in analysis.risk_assessments:
            if risk.risk_level in ["high", "critical"]:
                suggestions.append(f"How can I mitigate the {risk.risk_category} risks identified?")
        
        # Based on recommendations
        for rec in analysis.recommendations:
            if rec.priority == "high":
                suggestions.append(f"What are the next steps for {rec.category} management?")
        
        # Based on cross-references
        for ref in analysis.cross_references[:2]:
            suggestions.append(f"Can you explain {ref.lower()}?")
        
        # Generic follow-up questions
        if not suggestions:
            suggestions.extend([
                "What are the most critical risks in this agreement?",
                "Are there any red flags I should be concerned about?",
                "What would you recommend I negotiate or change?"
            ])
        
        return suggestions[:3]
    
    def _assess_completeness(self, response: EnhancedResponse, test_case: Any = None) -> float:
        """Assess response completeness"""
        # Simple heuristic based on response length and content
        base_score = min(len(response.content) / 200, 1.0)  # Normalize to 200 chars
        
        # Bonus for structured format
        if hasattr(response, 'structured_format') and response.structured_format:
            base_score += 0.2
        
        # Bonus for suggestions
        if response.suggestions:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _assess_clarity(self, response: EnhancedResponse) -> float:
        """Assess response clarity"""
        content = response.content.lower()
        
        # Positive indicators
        clarity_score = 0.5  # Base score
        
        if any(phrase in content for phrase in ['in simple terms', 'this means', 'in other words']):
            clarity_score += 0.2
        
        if any(phrase in content for phrase in ['for example', 'such as', 'like']):
            clarity_score += 0.1
        
        # Negative indicators
        if content.count('however') > 2:
            clarity_score -= 0.1
        
        if len(content.split('.')) > 20:  # Too many sentences
            clarity_score -= 0.1
        
        return max(0.0, min(clarity_score, 1.0))
    
    def _assess_relevance(self, response: EnhancedResponse, test_case: Any = None) -> float:
        """Assess response relevance to question"""
        if not test_case or not hasattr(test_case, 'question'):
            return 0.8  # Default relevance if no test case
        
        question_words = set(test_case.question.lower().split())
        response_words = set(response.content.lower().split())
        
        # Calculate word overlap
        overlap = len(question_words.intersection(response_words))
        relevance_score = overlap / len(question_words) if question_words else 0.0
        
        return min(relevance_score + 0.3, 1.0)  # Add base relevance
    
    def _assess_question_complexity(self, question: str) -> QuestionComplexity:
        """Assess the complexity level of a question"""
        question_lower = question.lower()
        
        # Expert-level indicators
        expert_terms = [
            'derivative work', 'ip assignment', 'indemnification', 'liability cap',
            'force majeure', 'governing law', 'jurisdiction', 'arbitration',
            'severability', 'waiver', 'counterpart execution'
        ]
        
        # Complex indicators
        complex_terms = [
            'liability', 'intellectual property', 'termination', 'breach',
            'confidentiality', 'warranty', 'indemnity', 'damages'
        ]
        
        # Simple indicators
        simple_patterns = [
            'what is', 'what does', 'can you explain', 'tell me about'
        ]
        
        expert_count = sum(1 for term in expert_terms if term in question_lower)
        complex_count = sum(1 for term in complex_terms if term in question_lower)
        simple_count = sum(1 for pattern in simple_patterns if pattern in question_lower)
        
        word_count = len(question.split())
        
        if expert_count > 0 or word_count > 20:
            return QuestionComplexity.EXPERT
        elif complex_count > 1 or word_count > 15:
            return QuestionComplexity.COMPLEX
        elif complex_count > 0 or word_count > 10:
            return QuestionComplexity.MODERATE
        else:
            return QuestionComplexity.SIMPLE
    
    def _initialize_risk_keywords(self) -> Dict[str, List[str]]:
        """Initialize risk assessment keywords"""
        return {
            'financial': [
                'unlimited liability', 'no liability cap', 'full damages',
                'consequential damages', 'punitive damages', 'lost profits'
            ],
            'intellectual_property': [
                'broad ip assignment', 'all improvements', 'derivative ownership',
                'work for hire', 'exclusive license', 'perpetual rights'
            ],
            'operational': [
                'exclusive', 'sole source', 'no alternatives', 'single supplier',
                'dependency', 'critical path', 'no substitutes'
            ],
            'compliance': [
                'regulatory', 'government approval', 'license required',
                'compliance audit', 'reporting obligations', 'certification'
            ]
        }
    
    def _initialize_compliance_frameworks(self) -> List[str]:
        """Initialize compliance frameworks and regulations"""
        return [
            'GDPR', 'HIPAA', 'SOX', 'ITAR', 'EAR', 'FCPA', 'OSHA',
            'FDA', 'EPA', 'FTC', 'SEC', 'COSO', 'ISO 27001'
        ]
    
    def _initialize_example_templates(self) -> Dict[str, List[str]]:
        """Initialize example templates for different contract concepts"""
        return {
            'liability': [
                "For example, if a software defect causes damages, a liability cap limits your maximum exposure.",
                "Think of liability like insurance - it determines who pays when something goes wrong."
            ],
            'termination': [
                "For instance, a 30-day notice requirement means you must give notice by March 1st to terminate by March 31st.",
                "Termination clauses are like the exit strategy for a business relationship."
            ],
            'intellectual_property': [
                "IP ownership is like property ownership - the contract determines who 'owns' innovations.",
                "Think of IP rights like copyright for books - they determine who can use and profit from ideas."
            ]
        }
    
    def _find_text_in_document(self, text: str, document: Document) -> Optional[Dict[str, Any]]:
        """Find specific text in document and return location info"""
        if not document or not document.content:
            return None
        
        content = document.content.lower()
        text_lower = text.lower()
        
        if text_lower in content:
            # Find surrounding context
            start_pos = content.find(text_lower)
            context_start = max(0, start_pos - 100)
            context_end = min(len(content), start_pos + len(text_lower) + 100)
            context = content[context_start:context_end]
            
            return {
                'section': 'Document Content',
                'context': context,
                'position': start_pos
            }
        
        return None
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content"""
        # Simple key phrase extraction
        phrases = []
        
        # Look for quoted text
        quoted_matches = re.findall(r'"([^"]+)"', content)
        phrases.extend(quoted_matches)
        
        # Look for important legal terms
        legal_terms = [
            'liability', 'indemnification', 'intellectual property',
            'confidentiality', 'termination', 'breach', 'warranty'
        ]
        
        content_lower = content.lower()
        for term in legal_terms:
            if term in content_lower:
                phrases.append(term)
        
        return phrases[:5]  # Limit to top 5
    
    def _phrase_in_document(self, phrase: str, document: Document) -> bool:
        """Check if phrase exists in document"""
        if not document or not document.content:
            return False
        
        return phrase.lower() in document.content.lower()
    
    def _identify_technical_terms(self, content: str) -> List[str]:
        """Identify technical and legal terms in content"""
        technical_terms = [
            'indemnification', 'liability', 'intellectual property', 'derivative work',
            'force majeure', 'governing law', 'jurisdiction', 'arbitration',
            'confidentiality', 'proprietary', 'warranty', 'breach'
        ]
        
        content_lower = content.lower()
        found_terms = [term for term in technical_terms if term in content_lower]
        
        return found_terms
    
    def _simplify_legal_language(self, content: str) -> str:
        """Simplify legal language for better understanding"""
        # Simple replacements for common legal terms
        replacements = {
            'indemnification': 'protection from legal claims',
            'liability': 'responsibility for damages',
            'intellectual property': 'ideas and innovations',
            'derivative work': 'modified or improved versions',
            'force majeure': 'unforeseeable circumstances',
            'governing law': 'which state\'s laws apply',
            'jurisdiction': 'which court handles disputes',
            'arbitration': 'private dispute resolution',
            'confidentiality': 'keeping information secret',
            'proprietary': 'privately owned',
            'warranty': 'guarantee or promise',
            'breach': 'breaking the contract'
        }
        
        simplified = content
        for term, replacement in replacements.items():
            simplified = re.sub(
                rf'\b{re.escape(term)}\b',
                replacement,
                simplified,
                flags=re.IGNORECASE
            )
        
        return simplified
    
    def _get_term_definition(self, term: str) -> str:
        """Get definition for legal/technical terms"""
        definitions = {
            'liability': 'Legal responsibility for damages or losses',
            'indemnification': 'Protection from legal claims and associated costs',
            'intellectual property': 'Legal rights to ideas, inventions, and creative works',
            'derivative work': 'New work based on or incorporating existing work',
            'force majeure': 'Unforeseeable circumstances that prevent contract performance',
            'governing law': 'The jurisdiction\'s laws that apply to the contract',
            'arbitration': 'Private dispute resolution outside of court',
            'confidentiality': 'Obligation to keep certain information secret',
            'warranty': 'Promise or guarantee about product/service quality',
            'breach': 'Failure to fulfill contract obligations'
        }
        
        return definitions.get(term.lower(), f'Legal term: {term}')
    
    def _enhance_technical_detail(self, content: str) -> str:
        """Enhance technical detail for advanced users"""
        # Add more technical context and legal implications
        enhanced = content
        
        # Add technical context where appropriate
        if 'liability' in content.lower():
            enhanced += "\n\nTechnical Note: Consider the interaction with insurance coverage and corporate structure for liability allocation."
        
        if 'intellectual property' in content.lower():
            enhanced += "\n\nTechnical Note: Evaluate patent prosecution strategies and freedom-to-operate considerations."
        
        return enhanced