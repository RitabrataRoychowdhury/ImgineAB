"""
Risk Analysis Engine for comprehensive risk assessment of legal documents.
Provides multi-dimensional risk categorization, severity scoring, and mitigation strategies.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RiskCategory(Enum):
    """Risk categories for classification"""
    FINANCIAL = "financial"
    LEGAL = "legal"
    OPERATIONAL = "operational"
    REPUTATIONAL = "reputational"
    COMPLIANCE = "compliance"
    STRATEGIC = "strategic"

class RiskSeverity(Enum):
    """Risk severity levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"

@dataclass
class Risk:
    """Individual risk item"""
    risk_id: str
    description: str
    category: RiskCategory
    severity: RiskSeverity
    probability: float  # 0.0 to 1.0
    impact_description: str
    affected_parties: List[str]
    materialization_timeframe: Optional[str]
    source_sections: List[str]
    mitigation_strategies: List[str] = field(default_factory=list)
    interconnected_risks: List[str] = field(default_factory=list)
    confidence_score: float = 0.0

@dataclass
class MitigationStrategy:
    """Risk mitigation strategy"""
    strategy_id: str
    description: str
    implementation_steps: List[str]
    timeline: str
    responsible_party: str
    cost_estimate: Optional[str]
    effectiveness_rating: float  # 0.0 to 1.0

@dataclass
class RiskRelationship:
    """Relationship between risks"""
    primary_risk_id: str
    related_risk_id: str
    relationship_type: str  # "causes", "amplifies", "mitigates", "depends_on"
    strength: float  # 0.0 to 1.0

@dataclass
class RiskTimeline:
    """Timeline analysis of risk materialization"""
    immediate_risks: List[str]  # 0-30 days
    short_term_risks: List[str]  # 30-90 days
    medium_term_risks: List[str]  # 90-365 days
    long_term_risks: List[str]  # >365 days
    ongoing_risks: List[str]  # Continuous risks

@dataclass
class RiskMatrix:
    """Risk matrix for visualization and prioritization"""
    high_probability_high_impact: List[Risk]
    high_probability_low_impact: List[Risk]
    low_probability_high_impact: List[Risk]
    low_probability_low_impact: List[Risk]
    risk_distribution_summary: Dict[str, int]

@dataclass
class RiskAnalysis:
    """Complete risk analysis result"""
    overall_risk_score: float
    risk_categories: Dict[RiskCategory, List[Risk]]
    risk_matrix: RiskMatrix
    mitigation_strategies: List[MitigationStrategy]
    risk_timeline: RiskTimeline
    interconnected_risks: List[RiskRelationship]
    confidence_level: float
    analysis_timestamp: datetime
    recommendations: List[str]

class RiskAnalysisEngine:
    """
    Comprehensive risk analysis engine for legal documents.
    Identifies, categorizes, and assesses risks with mitigation strategies.
    """
    
    def __init__(self):
        self.risk_patterns = self._initialize_risk_patterns()
        self.mitigation_templates = self._initialize_mitigation_templates()
        self.severity_criteria = self._initialize_severity_criteria()
        
    def _initialize_risk_patterns(self) -> Dict[RiskCategory, Dict[str, List[str]]]:
        """Initialize patterns for risk identification"""
        return {
            RiskCategory.FINANCIAL: {
                'keywords': [
                    'payment', 'penalty', 'fine', 'cost', 'expense', 'liability',
                    'damages', 'loss', 'default', 'bankruptcy', 'insolvency',
                    'credit risk', 'currency', 'inflation', 'budget'
                ],
                'phrases': [
                    'late payment penalty', 'liquidated damages', 'cost overrun',
                    'financial exposure', 'payment default', 'credit risk',
                    'currency fluctuation', 'budget impact', 'financial loss'
                ],
                'indicators': [
                    'shall pay', 'liable for', 'responsible for costs',
                    'penalty of', 'damages in the amount', 'financial obligation'
                ]
            },
            RiskCategory.LEGAL: {
                'keywords': [
                    'breach', 'violation', 'non-compliance', 'lawsuit', 'litigation',
                    'indemnification', 'liability', 'negligence', 'warranty',
                    'representation', 'covenant', 'intellectual property', 'patent'
                ],
                'phrases': [
                    'breach of contract', 'material breach', 'legal action',
                    'indemnification clause', 'warranty breach', 'ip infringement',
                    'regulatory violation', 'compliance failure', 'legal liability'
                ],
                'indicators': [
                    'shall indemnify', 'breach of this agreement', 'legal proceedings',
                    'violation of law', 'infringement claim', 'regulatory action'
                ]
            },
            RiskCategory.OPERATIONAL: {
                'keywords': [
                    'delivery', 'performance', 'delay', 'failure', 'disruption',
                    'capacity', 'resource', 'availability', 'quality', 'defect',
                    'service level', 'downtime', 'interruption'
                ],
                'phrases': [
                    'delivery delay', 'performance failure', 'service disruption',
                    'quality defect', 'resource unavailability', 'system downtime',
                    'operational risk', 'capacity constraint', 'service interruption'
                ],
                'indicators': [
                    'failure to deliver', 'performance standards', 'service levels',
                    'quality requirements', 'operational capacity', 'resource allocation'
                ]
            },
            RiskCategory.REPUTATIONAL: {
                'keywords': [
                    'reputation', 'brand', 'public', 'media', 'publicity',
                    'confidentiality', 'disclosure', 'scandal', 'negative',
                    'image', 'stakeholder', 'customer', 'trust'
                ],
                'phrases': [
                    'reputational damage', 'negative publicity', 'brand impact',
                    'public disclosure', 'confidentiality breach', 'media attention',
                    'stakeholder confidence', 'customer trust', 'public image'
                ],
                'indicators': [
                    'public disclosure', 'media coverage', 'confidential information',
                    'reputation risk', 'brand damage', 'stakeholder impact'
                ]
            },
            RiskCategory.COMPLIANCE: {
                'keywords': [
                    'regulation', 'regulatory', 'compliance', 'law', 'statute',
                    'rule', 'requirement', 'standard', 'certification', 'audit',
                    'inspection', 'violation', 'non-compliance'
                ],
                'phrases': [
                    'regulatory compliance', 'legal requirement', 'compliance violation',
                    'regulatory audit', 'certification requirement', 'statutory obligation',
                    'compliance risk', 'regulatory change', 'legal standard'
                ],
                'indicators': [
                    'comply with', 'regulatory requirements', 'legal obligations',
                    'compliance standards', 'regulatory approval', 'certification needed'
                ]
            }
        }
    
    def _initialize_mitigation_templates(self) -> Dict[RiskCategory, List[str]]:
        """Initialize mitigation strategy templates"""
        return {
            RiskCategory.FINANCIAL: [
                "Establish payment guarantees or letters of credit",
                "Implement regular financial health monitoring",
                "Set up escrow accounts for large payments",
                "Negotiate payment terms with built-in protections",
                "Obtain appropriate insurance coverage",
                "Create contingency funds for unexpected costs"
            ],
            RiskCategory.LEGAL: [
                "Conduct thorough legal review of all terms",
                "Obtain appropriate legal insurance coverage",
                "Establish clear dispute resolution procedures",
                "Implement compliance monitoring systems",
                "Maintain detailed documentation and records",
                "Engage qualified legal counsel for ongoing support"
            ],
            RiskCategory.OPERATIONAL: [
                "Develop comprehensive backup plans",
                "Establish alternative suppliers or service providers",
                "Implement quality control and monitoring systems",
                "Create detailed performance metrics and SLAs",
                "Establish regular review and improvement processes",
                "Invest in redundant systems and capabilities"
            ],
            RiskCategory.REPUTATIONAL: [
                "Develop crisis communication plans",
                "Establish media relations protocols",
                "Implement stakeholder engagement strategies",
                "Create transparency and disclosure policies",
                "Monitor public perception and feedback",
                "Maintain high ethical and quality standards"
            ],
            RiskCategory.COMPLIANCE: [
                "Establish compliance monitoring systems",
                "Conduct regular compliance audits",
                "Maintain up-to-date regulatory knowledge",
                "Implement staff training programs",
                "Create compliance documentation and procedures",
                "Engage regulatory compliance experts"
            ]
        }
    
    def _initialize_severity_criteria(self) -> Dict[RiskSeverity, Dict[str, Any]]:
        """Initialize criteria for risk severity assessment"""
        return {
            RiskSeverity.CRITICAL: {
                'financial_threshold': 1000000,  # $1M+
                'probability_threshold': 0.7,
                'impact_keywords': ['bankruptcy', 'insolvency', 'business failure', 'critical'],
                'description': 'Risks that could threaten business continuity'
            },
            RiskSeverity.HIGH: {
                'financial_threshold': 100000,  # $100K+
                'probability_threshold': 0.5,
                'impact_keywords': ['significant', 'major', 'substantial', 'material'],
                'description': 'Risks with significant impact on operations or finances'
            },
            RiskSeverity.MEDIUM: {
                'financial_threshold': 10000,  # $10K+
                'probability_threshold': 0.3,
                'impact_keywords': ['moderate', 'noticeable', 'measurable'],
                'description': 'Risks with moderate impact that require attention'
            },
            RiskSeverity.LOW: {
                'financial_threshold': 1000,  # $1K+
                'probability_threshold': 0.1,
                'impact_keywords': ['minor', 'small', 'limited', 'minimal'],
                'description': 'Risks with limited impact that should be monitored'
            }
        }
    
    def analyze_document_risks(self, content: str, document_type: str, 
                             key_information: Any) -> RiskAnalysis:
        """
        Perform comprehensive risk analysis on document content.
        """
        try:
            # Identify risks by category
            identified_risks = self._identify_risks_by_category(content, document_type)
            
            # Assess risk severity and probability
            assessed_risks = self._assess_risk_severity(identified_risks, content, key_information)
            
            # Generate mitigation strategies
            mitigation_strategies = self._generate_mitigation_strategies(assessed_risks)
            
            # Analyze risk interconnections
            risk_relationships = self._analyze_risk_interconnections(assessed_risks)
            
            # Create risk timeline
            risk_timeline = self._create_risk_timeline(assessed_risks, key_information)
            
            # Create risk matrix
            risk_matrix = self._create_risk_matrix(assessed_risks)
            
            # Calculate overall risk score
            overall_score = self._calculate_overall_risk_score(assessed_risks)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(assessed_risks, risk_relationships)
            
            # Categorize risks
            risk_categories = self._categorize_risks(assessed_risks)
            
            return RiskAnalysis(
                overall_risk_score=overall_score,
                risk_categories=risk_categories,
                risk_matrix=risk_matrix,
                mitigation_strategies=mitigation_strategies,
                risk_timeline=risk_timeline,
                interconnected_risks=risk_relationships,
                confidence_level=self._calculate_confidence_level(assessed_risks),
                analysis_timestamp=datetime.now(),
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            return self._create_empty_risk_analysis()
    
    def _identify_risks_by_category(self, content: str, document_type: str) -> List[Risk]:
        """Identify risks by category using pattern matching"""
        risks = []
        content_lower = content.lower()
        risk_id_counter = 1
        
        for category, patterns in self.risk_patterns.items():
            category_risks = self._find_category_risks(
                content, content_lower, category, patterns, risk_id_counter
            )
            risks.extend(category_risks)
            risk_id_counter += len(category_risks)
        
        return risks
    
    def _find_category_risks(self, content: str, content_lower: str, 
                           category: RiskCategory, patterns: Dict[str, List[str]], 
                           start_id: int) -> List[Risk]:
        """Find risks for a specific category"""
        risks = []
        risk_contexts = set()
        
        # Search for risk indicators
        all_patterns = (
            patterns.get('keywords', []) + 
            patterns.get('phrases', []) + 
            patterns.get('indicators', [])
        )
        
        for pattern in all_patterns:
            matches = list(re.finditer(re.escape(pattern.lower()), content_lower))
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].strip()
                
                # Avoid duplicate contexts
                if context not in risk_contexts:
                    risk_contexts.add(context)
                    
                    risk = Risk(
                        risk_id=f"RISK_{start_id + len(risks):03d}",
                        description=self._generate_risk_description(context, category, pattern),
                        category=category,
                        severity=RiskSeverity.MEDIUM,  # Will be assessed later
                        probability=0.5,  # Will be assessed later
                        impact_description=self._generate_impact_description(context, category),
                        affected_parties=self._identify_affected_parties(context),
                        materialization_timeframe=self._estimate_timeframe(context),
                        source_sections=[context[:50] + "..."],
                        confidence_score=self._calculate_pattern_confidence(pattern, context)
                    )
                    risks.append(risk)
        
        return risks[:10]  # Limit per category to avoid overwhelming results
    
    def _generate_risk_description(self, context: str, category: RiskCategory, pattern: str) -> str:
        """Generate a descriptive risk description"""
        category_descriptions = {
            RiskCategory.FINANCIAL: f"Financial risk related to {pattern}",
            RiskCategory.LEGAL: f"Legal risk involving {pattern}",
            RiskCategory.OPERATIONAL: f"Operational risk concerning {pattern}",
            RiskCategory.REPUTATIONAL: f"Reputational risk associated with {pattern}",
            RiskCategory.COMPLIANCE: f"Compliance risk related to {pattern}"
        }
        
        base_description = category_descriptions.get(category, f"Risk related to {pattern}")
        
        # Try to make it more specific based on context
        if 'payment' in context.lower() and category == RiskCategory.FINANCIAL:
            return "Risk of payment delays or defaults"
        elif 'breach' in context.lower() and category == RiskCategory.LEGAL:
            return "Risk of contract breach and associated legal consequences"
        elif 'delivery' in context.lower() and category == RiskCategory.OPERATIONAL:
            return "Risk of delivery delays or performance failures"
        
        return base_description
    
    def _generate_impact_description(self, context: str, category: RiskCategory) -> str:
        """Generate impact description for a risk"""
        impact_templates = {
            RiskCategory.FINANCIAL: "Potential financial losses, increased costs, or payment obligations",
            RiskCategory.LEGAL: "Legal liability, litigation costs, or regulatory penalties",
            RiskCategory.OPERATIONAL: "Service disruptions, performance degradation, or operational inefficiencies",
            RiskCategory.REPUTATIONAL: "Damage to reputation, loss of stakeholder confidence, or negative publicity",
            RiskCategory.COMPLIANCE: "Regulatory violations, fines, or loss of certifications"
        }
        
        return impact_templates.get(category, "Potential negative impact on business operations")
    
    def _identify_affected_parties(self, context: str) -> List[str]:
        """Identify parties affected by the risk"""
        parties = []
        context_lower = context.lower()
        
        # Common party indicators
        party_patterns = [
            r'(?i)\b(provider|recipient|buyer|seller|vendor|client|contractor|company)\b',
            r'(?i)\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:shall|will|must|agrees)'
        ]
        
        for pattern in party_patterns:
            matches = re.findall(pattern, context)
            for match in matches:
                if isinstance(match, tuple):
                    parties.extend([m.strip() for m in match if m.strip()])
                else:
                    parties.append(match.strip())
        
        # Default parties if none found
        if not parties:
            parties = ["All parties", "Organization"]
        
        return list(set(parties))[:5]  # Limit and remove duplicates
    
    def _estimate_timeframe(self, context: str) -> Optional[str]:
        """Estimate when the risk might materialize"""
        context_lower = context.lower()
        
        if any(term in context_lower for term in ['immediate', 'now', 'currently', 'today']):
            return "Immediate (0-30 days)"
        elif any(term in context_lower for term in ['soon', 'shortly', 'within days', 'next month']):
            return "Short-term (30-90 days)"
        elif any(term in context_lower for term in ['months', 'quarterly', 'this year']):
            return "Medium-term (90-365 days)"
        elif any(term in context_lower for term in ['annual', 'yearly', 'long-term', 'future']):
            return "Long-term (>365 days)"
        else:
            return "Ongoing"
    
    def _calculate_pattern_confidence(self, pattern: str, context: str) -> float:
        """Calculate confidence score for pattern match"""
        # Base confidence
        confidence = 0.5
        
        # Boost for exact phrase matches
        if pattern.lower() in context.lower():
            confidence += 0.2
        
        # Boost for context richness
        if len(context.split()) > 20:
            confidence += 0.1
        
        # Boost for specific legal/financial terms
        if any(term in context.lower() for term in ['shall', 'must', 'liable', 'responsible']):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _assess_risk_severity(self, risks: List[Risk], content: str, key_information: Any) -> List[Risk]:
        """Assess severity and probability for identified risks"""
        for risk in risks:
            # Assess severity based on multiple factors
            severity_score = self._calculate_severity_score(risk, content, key_information)
            risk.severity = self._map_severity_score(severity_score)
            
            # Assess probability
            risk.probability = self._calculate_probability(risk, content)
        
        return risks
    
    def _calculate_severity_score(self, risk: Risk, content: str, key_information: Any) -> float:
        """Calculate severity score for a risk"""
        score = 0.5  # Base score
        
        # Category-based scoring
        category_weights = {
            RiskCategory.FINANCIAL: 0.9,
            RiskCategory.LEGAL: 0.8,
            RiskCategory.OPERATIONAL: 0.7,
            RiskCategory.REPUTATIONAL: 0.6,
            RiskCategory.COMPLIANCE: 0.8
        }
        score *= category_weights.get(risk.category, 0.5)
        
        # Context-based adjustments
        context = ' '.join(risk.source_sections).lower()
        
        # High-impact keywords
        high_impact_terms = ['critical', 'material', 'significant', 'substantial', 'major']
        if any(term in context for term in high_impact_terms):
            score += 0.3
        
        # Financial amount indicators
        financial_patterns = [r'\$[\d,]+', r'\d+(?:,\d{3})*\s*(?:dollars|usd)']
        for pattern in financial_patterns:
            matches = re.findall(pattern, context)
            if matches:
                # Try to extract amount and adjust score
                try:
                    amount_str = matches[0].replace('$', '').replace(',', '').replace('dollars', '').replace('usd', '').strip()
                    amount = float(re.search(r'\d+', amount_str).group())
                    if amount > 100000:
                        score += 0.4
                    elif amount > 10000:
                        score += 0.2
                except:
                    pass
        
        return min(1.0, score)
    
    def _map_severity_score(self, score: float) -> RiskSeverity:
        """Map severity score to severity level"""
        if score >= 0.8:
            return RiskSeverity.CRITICAL
        elif score >= 0.6:
            return RiskSeverity.HIGH
        elif score >= 0.4:
            return RiskSeverity.MEDIUM
        else:
            return RiskSeverity.LOW
    
    def _calculate_probability(self, risk: Risk, content: str) -> float:
        """Calculate probability of risk materialization"""
        base_probability = 0.3
        
        # Adjust based on risk category
        category_probabilities = {
            RiskCategory.FINANCIAL: 0.4,
            RiskCategory.LEGAL: 0.3,
            RiskCategory.OPERATIONAL: 0.5,
            RiskCategory.REPUTATIONAL: 0.2,
            RiskCategory.COMPLIANCE: 0.4
        }
        
        probability = category_probabilities.get(risk.category, base_probability)
        
        # Adjust based on context indicators
        context = ' '.join(risk.source_sections).lower()
        
        if any(term in context for term in ['likely', 'probable', 'expected']):
            probability += 0.2
        elif any(term in context for term in ['possible', 'may', 'could']):
            probability += 0.1
        elif any(term in context for term in ['unlikely', 'rare', 'minimal']):
            probability -= 0.2
        
        return max(0.1, min(0.9, probability))
    
    def _generate_mitigation_strategies(self, risks: List[Risk]) -> List[MitigationStrategy]:
        """Generate mitigation strategies for identified risks"""
        strategies = []
        strategy_id_counter = 1
        
        # Group risks by category for efficient strategy generation
        risks_by_category = {}
        for risk in risks:
            if risk.category not in risks_by_category:
                risks_by_category[risk.category] = []
            risks_by_category[risk.category].append(risk)
        
        for category, category_risks in risks_by_category.items():
            category_strategies = self._generate_category_strategies(
                category, category_risks, strategy_id_counter
            )
            strategies.extend(category_strategies)
            strategy_id_counter += len(category_strategies)
        
        return strategies
    
    def _generate_category_strategies(self, category: RiskCategory, 
                                    risks: List[Risk], start_id: int) -> List[MitigationStrategy]:
        """Generate mitigation strategies for a risk category"""
        strategies = []
        templates = self.mitigation_templates.get(category, [])
        
        for i, template in enumerate(templates[:5]):  # Limit to 5 strategies per category
            strategy = MitigationStrategy(
                strategy_id=f"MIT_{start_id + i:03d}",
                description=template,
                implementation_steps=self._generate_implementation_steps(template, category),
                timeline=self._estimate_implementation_timeline(template),
                responsible_party=self._suggest_responsible_party(category),
                cost_estimate=self._estimate_implementation_cost(template),
                effectiveness_rating=self._estimate_effectiveness(template, category)
            )
            strategies.append(strategy)
        
        return strategies
    
    def _generate_implementation_steps(self, strategy: str, category: RiskCategory) -> List[str]:
        """Generate implementation steps for a mitigation strategy"""
        # Generic implementation steps based on strategy type
        if 'monitoring' in strategy.lower():
            return [
                "Define monitoring criteria and metrics",
                "Implement monitoring systems and tools",
                "Establish reporting procedures",
                "Train staff on monitoring processes",
                "Regular review and adjustment"
            ]
        elif 'insurance' in strategy.lower():
            return [
                "Assess insurance requirements",
                "Research and compare insurance providers",
                "Negotiate coverage terms and premiums",
                "Implement insurance policies",
                "Regular policy review and updates"
            ]
        elif 'legal' in strategy.lower():
            return [
                "Engage qualified legal counsel",
                "Review and update legal documentation",
                "Implement compliance procedures",
                "Staff training on legal requirements",
                "Regular legal review and updates"
            ]
        else:
            return [
                "Assess current situation and requirements",
                "Develop implementation plan",
                "Allocate necessary resources",
                "Execute implementation plan",
                "Monitor and evaluate effectiveness"
            ]
    
    def _estimate_implementation_timeline(self, strategy: str) -> str:
        """Estimate implementation timeline for a strategy"""
        if any(term in strategy.lower() for term in ['immediate', 'urgent', 'critical']):
            return "1-2 weeks"
        elif any(term in strategy.lower() for term in ['system', 'process', 'comprehensive']):
            return "2-3 months"
        elif any(term in strategy.lower() for term in ['training', 'education', 'development']):
            return "1-2 months"
        else:
            return "3-4 weeks"
    
    def _suggest_responsible_party(self, category: RiskCategory) -> str:
        """Suggest responsible party for risk mitigation"""
        party_mapping = {
            RiskCategory.FINANCIAL: "Finance Team / CFO",
            RiskCategory.LEGAL: "Legal Team / General Counsel",
            RiskCategory.OPERATIONAL: "Operations Team / COO",
            RiskCategory.REPUTATIONAL: "Communications Team / CMO",
            RiskCategory.COMPLIANCE: "Compliance Team / Chief Compliance Officer"
        }
        return party_mapping.get(category, "Risk Management Team")
    
    def _estimate_implementation_cost(self, strategy: str) -> Optional[str]:
        """Estimate implementation cost for a strategy"""
        if 'insurance' in strategy.lower():
            return "Medium ($10K-$50K annually)"
        elif 'system' in strategy.lower() or 'technology' in strategy.lower():
            return "High ($50K-$200K)"
        elif 'training' in strategy.lower():
            return "Low ($5K-$15K)"
        elif 'legal' in strategy.lower():
            return "Medium ($15K-$75K)"
        else:
            return "Low-Medium ($5K-$25K)"
    
    def _estimate_effectiveness(self, strategy: str, category: RiskCategory) -> float:
        """Estimate effectiveness rating for a strategy"""
        # Base effectiveness by category
        base_effectiveness = {
            RiskCategory.FINANCIAL: 0.7,
            RiskCategory.LEGAL: 0.8,
            RiskCategory.OPERATIONAL: 0.6,
            RiskCategory.REPUTATIONAL: 0.5,
            RiskCategory.COMPLIANCE: 0.8
        }
        
        effectiveness = base_effectiveness.get(category, 0.6)
        
        # Adjust based on strategy type
        if 'comprehensive' in strategy.lower():
            effectiveness += 0.1
        elif 'monitoring' in strategy.lower():
            effectiveness += 0.15
        elif 'insurance' in strategy.lower():
            effectiveness += 0.2
        
        return min(1.0, effectiveness)
    
    def _analyze_risk_interconnections(self, risks: List[Risk]) -> List[RiskRelationship]:
        """Analyze interconnections between risks"""
        relationships = []
        
        for i, risk1 in enumerate(risks):
            for j, risk2 in enumerate(risks[i+1:], i+1):
                relationship = self._assess_risk_relationship(risk1, risk2)
                if relationship:
                    relationships.append(relationship)
        
        return relationships
    
    def _assess_risk_relationship(self, risk1: Risk, risk2: Risk) -> Optional[RiskRelationship]:
        """Assess relationship between two risks"""
        # Simple heuristic-based relationship assessment
        
        # Same category risks often amplify each other
        if risk1.category == risk2.category:
            return RiskRelationship(
                primary_risk_id=risk1.risk_id,
                related_risk_id=risk2.risk_id,
                relationship_type="amplifies",
                strength=0.6
            )
        
        # Financial risks often cause operational risks
        if (risk1.category == RiskCategory.FINANCIAL and 
            risk2.category == RiskCategory.OPERATIONAL):
            return RiskRelationship(
                primary_risk_id=risk1.risk_id,
                related_risk_id=risk2.risk_id,
                relationship_type="causes",
                strength=0.7
            )
        
        # Legal risks often cause reputational risks
        if (risk1.category == RiskCategory.LEGAL and 
            risk2.category == RiskCategory.REPUTATIONAL):
            return RiskRelationship(
                primary_risk_id=risk1.risk_id,
                related_risk_id=risk2.risk_id,
                relationship_type="causes",
                strength=0.8
            )
        
        return None
    
    def _create_risk_timeline(self, risks: List[Risk], key_information: Any) -> RiskTimeline:
        """Create timeline analysis of risk materialization"""
        timeline = RiskTimeline(
            immediate_risks=[],
            short_term_risks=[],
            medium_term_risks=[],
            long_term_risks=[],
            ongoing_risks=[]
        )
        
        for risk in risks:
            timeframe = risk.materialization_timeframe
            if not timeframe:
                timeline.ongoing_risks.append(risk.risk_id)
            elif "immediate" in timeframe.lower() or "0-30" in timeframe:
                timeline.immediate_risks.append(risk.risk_id)
            elif "short" in timeframe.lower() or "30-90" in timeframe:
                timeline.short_term_risks.append(risk.risk_id)
            elif "medium" in timeframe.lower() or "90-365" in timeframe:
                timeline.medium_term_risks.append(risk.risk_id)
            elif "long" in timeframe.lower() or ">365" in timeframe:
                timeline.long_term_risks.append(risk.risk_id)
            else:
                timeline.ongoing_risks.append(risk.risk_id)
        
        return timeline
    
    def _create_risk_matrix(self, risks: List[Risk]) -> RiskMatrix:
        """Create risk matrix for visualization"""
        matrix = RiskMatrix(
            high_probability_high_impact=[],
            high_probability_low_impact=[],
            low_probability_high_impact=[],
            low_probability_low_impact=[],
            risk_distribution_summary={}
        )
        
        for risk in risks:
            high_prob = risk.probability >= 0.5
            high_impact = risk.severity in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]
            
            if high_prob and high_impact:
                matrix.high_probability_high_impact.append(risk)
            elif high_prob and not high_impact:
                matrix.high_probability_low_impact.append(risk)
            elif not high_prob and high_impact:
                matrix.low_probability_high_impact.append(risk)
            else:
                matrix.low_probability_low_impact.append(risk)
        
        # Create distribution summary
        matrix.risk_distribution_summary = {
            "high_prob_high_impact": len(matrix.high_probability_high_impact),
            "high_prob_low_impact": len(matrix.high_probability_low_impact),
            "low_prob_high_impact": len(matrix.low_probability_high_impact),
            "low_prob_low_impact": len(matrix.low_probability_low_impact)
        }
        
        return matrix
    
    def _calculate_overall_risk_score(self, risks: List[Risk]) -> float:
        """Calculate overall risk score for the document"""
        if not risks:
            return 0.0
        
        # Weight risks by severity and probability
        total_weighted_score = 0.0
        total_weight = 0.0
        
        severity_weights = {
            RiskSeverity.CRITICAL: 1.0,
            RiskSeverity.HIGH: 0.8,
            RiskSeverity.MEDIUM: 0.5,
            RiskSeverity.LOW: 0.2
        }
        
        for risk in risks:
            severity_weight = severity_weights.get(risk.severity, 0.5)
            risk_score = risk.probability * severity_weight
            weight = severity_weight
            
            total_weighted_score += risk_score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, risks: List[Risk], 
                                relationships: List[RiskRelationship]) -> List[str]:
        """Generate high-level recommendations based on risk analysis"""
        recommendations = []
        
        # Priority recommendations based on high-severity risks
        high_severity_risks = [r for r in risks if r.severity in [RiskSeverity.HIGH, RiskSeverity.CRITICAL]]
        if high_severity_risks:
            recommendations.append(
                f"Immediate attention required for {len(high_severity_risks)} high-severity risks"
            )
        
        # Category-specific recommendations
        risk_categories = {}
        for risk in risks:
            if risk.category not in risk_categories:
                risk_categories[risk.category] = 0
            risk_categories[risk.category] += 1
        
        if risk_categories.get(RiskCategory.FINANCIAL, 0) > 3:
            recommendations.append("Consider comprehensive financial risk management review")
        
        if risk_categories.get(RiskCategory.LEGAL, 0) > 2:
            recommendations.append("Engage legal counsel for detailed contract review")
        
        # Interconnection-based recommendations
        if len(relationships) > 5:
            recommendations.append("Multiple interconnected risks identified - consider holistic mitigation approach")
        
        # Default recommendations
        if not recommendations:
            recommendations.append("Regular monitoring and review of identified risks recommended")
        
        return recommendations
    
    def _categorize_risks(self, risks: List[Risk]) -> Dict[RiskCategory, List[Risk]]:
        """Categorize risks by category"""
        categories = {}
        for risk in risks:
            if risk.category not in categories:
                categories[risk.category] = []
            categories[risk.category].append(risk)
        return categories
    
    def _calculate_confidence_level(self, risks: List[Risk]) -> float:
        """Calculate overall confidence level for the analysis"""
        if not risks:
            return 0.0
        
        total_confidence = sum(risk.confidence_score for risk in risks)
        return total_confidence / len(risks)
    
    def _create_empty_risk_analysis(self) -> RiskAnalysis:
        """Create empty risk analysis for error cases"""
        return RiskAnalysis(
            overall_risk_score=0.0,
            risk_categories={},
            risk_matrix=RiskMatrix([], [], [], [], {}),
            mitigation_strategies=[],
            risk_timeline=RiskTimeline([], [], [], [], []),
            interconnected_risks=[],
            confidence_level=0.0,
            analysis_timestamp=datetime.now(),
            recommendations=["Risk analysis could not be completed"]
        )