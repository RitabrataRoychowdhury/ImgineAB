"""
Advanced Document Analysis System for Enhanced Contract Assistant

This module provides comprehensive document analysis with cross-referencing,
exhibit integration, timeline analysis, party obligation mapping, risk matrix
generation, and compliance requirement identification.
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import re
import json

from src.models.document import Document
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class RiskLevel(Enum):
    """Risk levels for risk matrix"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ObligationType(Enum):
    """Types of contractual obligations"""
    PAYMENT = "payment"
    DELIVERY = "delivery"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    REPORTING = "reporting"
    CONFIDENTIALITY = "confidentiality"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    TERMINATION = "termination"


@dataclass
class CrossReference:
    """Cross-reference between document sections"""
    source_section: str
    target_section: str
    reference_type: str  # direct, indirect, related
    relationship: str
    confidence: float


@dataclass
class ExhibitReference:
    """Reference to exhibits or appendices"""
    exhibit_id: str
    exhibit_title: str
    referenced_in_sections: List[str]
    content_summary: str
    importance_level: str


@dataclass
class TimelineEvent:
    """Timeline event extracted from contract"""
    event_type: str
    description: str
    date: Optional[datetime]
    relative_timing: Optional[str]  # "30 days after", "upon completion"
    responsible_party: Optional[str]
    dependencies: List[str]
    criticality: str


@dataclass
class PartyObligation:
    """Obligation assigned to a specific party"""
    party_name: str
    obligation_type: ObligationType
    description: str
    deadline: Optional[str]
    conditions: List[str]
    consequences: List[str]
    section_reference: str
    priority: str


@dataclass
class RiskMatrixEntry:
    """Entry in the risk assessment matrix"""
    risk_id: str
    risk_category: str
    description: str
    probability: str  # low, medium, high
    impact: str  # low, medium, high
    overall_risk: RiskLevel
    mitigation_strategies: List[str]
    responsible_party: Optional[str]
    section_references: List[str]


@dataclass
class ComplianceRequirement:
    """Compliance requirement identified in document"""
    requirement_id: str
    regulatory_framework: str
    description: str
    applicable_sections: List[str]
    compliance_deadline: Optional[str]
    responsible_party: Optional[str]
    verification_method: str
    penalties: List[str]


@dataclass
class AdvancedAnalysisResult:
    """Comprehensive advanced analysis result"""
    cross_references: List[CrossReference]
    exhibit_references: List[ExhibitReference]
    timeline_events: List[TimelineEvent]
    party_obligations: Dict[str, List[PartyObligation]]
    risk_matrix: List[RiskMatrixEntry]
    compliance_requirements: List[ComplianceRequirement]
    document_structure: Dict[str, Any]
    key_relationships: List[Dict[str, Any]]


class AdvancedDocumentAnalyzer:
    """
    Advanced document analyzer that provides:
    - Cross-referencing between sections and exhibits
    - Timeline analysis with critical path identification
    - Party obligation mapping with responsibility matrix
    - Risk matrix generation with probability/impact assessment
    - Compliance requirement identification and tracking
    """
    
    def __init__(self):
        """Initialize the advanced document analyzer"""
        self.section_patterns = self._initialize_section_patterns()
        self.date_patterns = self._initialize_date_patterns()
        self.obligation_keywords = self._initialize_obligation_keywords()
        self.risk_indicators = self._initialize_risk_indicators()
        self.compliance_frameworks = self._initialize_compliance_frameworks()
        
    def perform_advanced_analysis(self, document: Document) -> AdvancedAnalysisResult:
        """
        Perform comprehensive advanced analysis of the document
        
        Args:
            document: Document to analyze
            
        Returns:
            AdvancedAnalysisResult with comprehensive analysis
        """
        try:
            logger.info(f"Starting advanced analysis for document {document.id}")
            
            # Parse document structure
            document_structure = self._parse_document_structure(document)
            
            # Find cross-references
            cross_references = self._find_cross_references(document, document_structure)
            
            # Identify exhibit references
            exhibit_references = self._identify_exhibit_references(document)
            
            # Extract timeline events
            timeline_events = self._extract_timeline_events(document)
            
            # Map party obligations
            party_obligations = self._map_party_obligations(document)
            
            # Generate risk matrix
            risk_matrix = self._generate_risk_matrix(document)
            
            # Identify compliance requirements
            compliance_requirements = self._identify_compliance_requirements(document)
            
            # Analyze key relationships
            key_relationships = self._analyze_key_relationships(
                cross_references, timeline_events, party_obligations
            )
            
            result = AdvancedAnalysisResult(
                cross_references=cross_references,
                exhibit_references=exhibit_references,
                timeline_events=timeline_events,
                party_obligations=party_obligations,
                risk_matrix=risk_matrix,
                compliance_requirements=compliance_requirements,
                document_structure=document_structure,
                key_relationships=key_relationships
            )
            
            logger.info(f"Advanced analysis completed with {len(cross_references)} cross-references, "
                       f"{len(timeline_events)} timeline events, {len(risk_matrix)} risks")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced document analysis: {e}")
            # Return empty result structure
            return AdvancedAnalysisResult(
                cross_references=[],
                exhibit_references=[],
                timeline_events=[],
                party_obligations={},
                risk_matrix=[],
                compliance_requirements=[],
                document_structure={},
                key_relationships=[]
            )
    
    def _parse_document_structure(self, document: Document) -> Dict[str, Any]:
        """Parse document structure and identify sections"""
        structure = {
            'sections': [],
            'exhibits': [],
            'parties': [],
            'definitions': {},
            'total_sections': 0
        }
        
        content = document.content
        
        # Find sections
        for pattern_name, pattern in self.section_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                section_info = {
                    'type': pattern_name,
                    'number': match.group(1) if match.groups() else None,
                    'title': match.group(2) if len(match.groups()) > 1 else None,
                    'start_pos': match.start(),
                    'text': match.group(0)
                }
                structure['sections'].append(section_info)
        
        structure['total_sections'] = len(structure['sections'])
        
        # Find parties
        party_patterns = [
            r'(?:Provider|Recipient|Licensor|Licensee|Company|Institution|University)\s*[:\(]?\s*([^,\n\)]+)',
            r'Party\s+(?:A|B|1|2)\s*[:\(]?\s*([^,\n\)]+)',
            r'between\s+([^,\n]+)\s+and\s+([^,\n]+)'
        ]
        
        for pattern in party_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                for group in match.groups():
                    if group and len(group.strip()) > 2:
                        party_name = group.strip().strip('()"')
                        if party_name not in structure['parties']:
                            structure['parties'].append(party_name)
        
        # Find definitions
        definition_patterns = [
            r'"([^"]+)"\s+means\s+([^.]+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+shall\s+mean\s+([^.]+)'
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                structure['definitions'][term] = definition
        
        return structure
    
    def _find_cross_references(
        self, 
        document: Document, 
        structure: Dict[str, Any]
    ) -> List[CrossReference]:
        """Find cross-references between document sections"""
        cross_refs = []
        content = document.content
        
        # Direct section references
        reference_patterns = [
            r'(?:Section|Article|Paragraph|Clause)\s+(\d+(?:\.\d+)*)',
            r'(?:see|refer to|pursuant to|in accordance with)\s+(?:Section|Article)\s+(\d+(?:\.\d+)*)',
            r'as\s+(?:set forth|described|defined)\s+in\s+(?:Section|Article)\s+(\d+(?:\.\d+)*)'
        ]
        
        for pattern in reference_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                referenced_section = match.group(1)
                
                # Find the section containing this reference
                source_section = self._find_containing_section(match.start(), structure['sections'])
                
                if source_section and referenced_section:
                    cross_ref = CrossReference(
                        source_section=source_section,
                        target_section=f"Section {referenced_section}",
                        reference_type="direct",
                        relationship="references",
                        confidence=0.9
                    )
                    cross_refs.append(cross_ref)
        
        # Exhibit references
        exhibit_patterns = [
            r'(?:Exhibit|Appendix|Schedule)\s+([A-Z]|\d+)',
            r'attached\s+(?:hereto\s+as\s+)?(?:Exhibit|Appendix)\s+([A-Z]|\d+)'
        ]
        
        for pattern in exhibit_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                exhibit_id = match.group(1)
                source_section = self._find_containing_section(match.start(), structure['sections'])
                
                if source_section:
                    cross_ref = CrossReference(
                        source_section=source_section,
                        target_section=f"Exhibit {exhibit_id}",
                        reference_type="exhibit",
                        relationship="incorporates",
                        confidence=0.8
                    )
                    cross_refs.append(cross_ref)
        
        # Thematic cross-references (related concepts)
        concept_groups = {
            'liability': ['liability', 'indemnification', 'damages', 'losses'],
            'intellectual_property': ['intellectual property', 'patent', 'copyright', 'trademark'],
            'confidentiality': ['confidential', 'proprietary', 'non-disclosure'],
            'termination': ['termination', 'expiration', 'breach', 'default']
        }
        
        for concept, keywords in concept_groups.items():
            sections_with_concept = []
            
            for section in structure['sections']:
                section_text = self._get_section_text(section, content)
                if any(keyword in section_text.lower() for keyword in keywords):
                    sections_with_concept.append(section)
            
            # Create cross-references between related sections
            for i, section1 in enumerate(sections_with_concept):
                for section2 in sections_with_concept[i+1:]:
                    cross_ref = CrossReference(
                        source_section=self._get_section_identifier(section1),
                        target_section=self._get_section_identifier(section2),
                        reference_type="thematic",
                        relationship=f"related_{concept}",
                        confidence=0.6
                    )
                    cross_refs.append(cross_ref)
        
        return cross_refs
    
    def _identify_exhibit_references(self, document: Document) -> List[ExhibitReference]:
        """Identify and analyze exhibit references"""
        exhibits = []
        content = document.content
        
        # Find exhibit definitions
        exhibit_patterns = [
            r'(?:Exhibit|Appendix|Schedule)\s+([A-Z]|\d+)\s*[-:]?\s*([^\n]+)',
            r'attached\s+(?:hereto\s+as\s+)?(?:Exhibit|Appendix)\s+([A-Z]|\d+)\s*[-:]?\s*([^\n]*)'
        ]
        
        exhibit_map = {}
        
        for pattern in exhibit_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                exhibit_id = match.group(1)
                exhibit_title = match.group(2).strip() if len(match.groups()) > 1 else f"Exhibit {exhibit_id}"
                
                if exhibit_id not in exhibit_map:
                    exhibit_map[exhibit_id] = {
                        'title': exhibit_title,
                        'references': [],
                        'content_hints': []
                    }
        
        # Find all references to each exhibit
        for exhibit_id in exhibit_map.keys():
            reference_pattern = rf'(?:Exhibit|Appendix|Schedule)\s+{re.escape(exhibit_id)}\b'
            matches = re.finditer(reference_pattern, content, re.IGNORECASE)
            
            for match in matches:
                # Find the section containing this reference
                section = self._find_containing_section(match.start(), [])
                if section:
                    exhibit_map[exhibit_id]['references'].append(section)
        
        # Create ExhibitReference objects
        for exhibit_id, info in exhibit_map.items():
            # Determine importance based on number of references
            ref_count = len(info['references'])
            if ref_count >= 3:
                importance = "high"
            elif ref_count >= 2:
                importance = "medium"
            else:
                importance = "low"
            
            exhibit = ExhibitReference(
                exhibit_id=exhibit_id,
                exhibit_title=info['title'],
                referenced_in_sections=info['references'],
                content_summary=f"Referenced {ref_count} times in the document",
                importance_level=importance
            )
            exhibits.append(exhibit)
        
        return exhibits
    
    def _extract_timeline_events(self, document: Document) -> List[TimelineEvent]:
        """Extract timeline events and deadlines from document"""
        events = []
        content = document.content
        
        # Date patterns
        absolute_date_patterns = [
            r'(?:by|on|before|after)\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',  # January 1, 2024
            r'(?:by|on|before|after)\s+(\d{1,2}/\d{1,2}/\d{4})',  # 1/1/2024
            r'(?:by|on|before|after)\s+(\d{1,2}-\d{1,2}-\d{4})'   # 1-1-2024
        ]
        
        # Relative timing patterns
        relative_patterns = [
            r'within\s+(\d+)\s+(days?|weeks?|months?|years?)',
            r'(\d+)\s+(days?|weeks?|months?|years?)\s+(?:after|before|from)',
            r'no\s+(?:later|earlier)\s+than\s+(\d+)\s+(days?|weeks?|months?|years?)',
            r'upon\s+([^,\n]+)',
            r'immediately\s+(?:after|upon)\s+([^,\n]+)'
        ]
        
        # Extract absolute date events
        for pattern in absolute_date_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1)
                context = self._get_surrounding_context(match.start(), content, 100)
                
                event = TimelineEvent(
                    event_type="deadline",
                    description=context.strip(),
                    date=self._parse_date(date_str),
                    relative_timing=None,
                    responsible_party=self._extract_responsible_party(context),
                    dependencies=[],
                    criticality=self._assess_event_criticality(context)
                )
                events.append(event)
        
        # Extract relative timing events
        for pattern in relative_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    duration = match.group(1)
                    unit = match.group(2)
                    relative_timing = f"{duration} {unit}"
                else:
                    relative_timing = match.group(1)
                
                context = self._get_surrounding_context(match.start(), content, 150)
                
                event = TimelineEvent(
                    event_type="relative_deadline",
                    description=context.strip(),
                    date=None,
                    relative_timing=relative_timing,
                    responsible_party=self._extract_responsible_party(context),
                    dependencies=self._extract_dependencies(context),
                    criticality=self._assess_event_criticality(context)
                )
                events.append(event)
        
        # Extract milestone events
        milestone_patterns = [
            r'(?:completion|delivery|execution|signing|effective date)\s+of\s+([^,\n]+)',
            r'when\s+([^,\n]+)\s+(?:occurs|happens|is completed)',
            r'following\s+([^,\n]+)'
        ]
        
        for pattern in milestone_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                milestone = match.group(1)
                context = self._get_surrounding_context(match.start(), content, 100)
                
                event = TimelineEvent(
                    event_type="milestone",
                    description=f"Milestone: {milestone}",
                    date=None,
                    relative_timing=None,
                    responsible_party=self._extract_responsible_party(context),
                    dependencies=[milestone],
                    criticality=self._assess_event_criticality(context)
                )
                events.append(event)
        
        return events
    
    def _map_party_obligations(self, document: Document) -> Dict[str, List[PartyObligation]]:
        """Map obligations to specific parties"""
        obligations_by_party = {}
        content = document.content
        
        # Extract party names
        parties = self._extract_party_names(content)
        
        # Obligation patterns
        obligation_patterns = {
            ObligationType.PAYMENT: [
                r'(?:shall|will|must)\s+pay\s+([^.]+)',
                r'payment\s+of\s+([^.]+)',
                r'(?:fees?|costs?|expenses?)\s+(?:shall|will)\s+be\s+([^.]+)'
            ],
            ObligationType.DELIVERY: [
                r'(?:shall|will|must)\s+(?:deliver|provide|supply)\s+([^.]+)',
                r'delivery\s+of\s+([^.]+)',
                r'(?:shall|will)\s+furnish\s+([^.]+)'
            ],
            ObligationType.PERFORMANCE: [
                r'(?:shall|will|must)\s+perform\s+([^.]+)',
                r'performance\s+of\s+([^.]+)',
                r'(?:shall|will)\s+carry\s+out\s+([^.]+)'
            ],
            ObligationType.COMPLIANCE: [
                r'(?:shall|will|must)\s+comply\s+with\s+([^.]+)',
                r'compliance\s+with\s+([^.]+)',
                r'(?:shall|will)\s+adhere\s+to\s+([^.]+)'
            ],
            ObligationType.REPORTING: [
                r'(?:shall|will|must)\s+(?:report|notify|inform)\s+([^.]+)',
                r'reporting\s+(?:of|on)\s+([^.]+)',
                r'(?:shall|will)\s+provide\s+notice\s+([^.]+)'
            ],
            ObligationType.CONFIDENTIALITY: [
                r'(?:shall|will|must)\s+(?:maintain|keep)\s+(?:confidential|secret)\s+([^.]+)',
                r'confidentiality\s+of\s+([^.]+)',
                r'(?:shall|will)\s+not\s+disclose\s+([^.]+)'
            ]
        }
        
        # Extract obligations for each type
        for obligation_type, patterns in obligation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    obligation_text = match.group(1).strip()
                    context = self._get_surrounding_context(match.start(), content, 200)
                    
                    # Determine responsible party
                    responsible_party = self._determine_responsible_party(context, parties)
                    
                    # Extract conditions and consequences
                    conditions = self._extract_conditions(context)
                    consequences = self._extract_consequences(context)
                    
                    # Determine deadline
                    deadline = self._extract_deadline_from_context(context)
                    
                    # Assess priority
                    priority = self._assess_obligation_priority(context, obligation_type)
                    
                    obligation = PartyObligation(
                        party_name=responsible_party or "Unspecified",
                        obligation_type=obligation_type,
                        description=obligation_text,
                        deadline=deadline,
                        conditions=conditions,
                        consequences=consequences,
                        section_reference=self._find_containing_section(match.start(), []) or "Unknown",
                        priority=priority
                    )
                    
                    # Add to party's obligations
                    party_key = responsible_party or "Unspecified"
                    if party_key not in obligations_by_party:
                        obligations_by_party[party_key] = []
                    
                    obligations_by_party[party_key].append(obligation)
        
        return obligations_by_party
    
    def _generate_risk_matrix(self, document: Document) -> List[RiskMatrixEntry]:
        """Generate comprehensive risk assessment matrix"""
        risks = []
        content = document.content.lower()
        
        # Risk categories and their indicators
        risk_categories = {
            'financial': {
                'indicators': [
                    'unlimited liability', 'no liability cap', 'consequential damages',
                    'punitive damages', 'lost profits', 'indirect damages'
                ],
                'base_probability': 'medium',
                'base_impact': 'high'
            },
            'intellectual_property': {
                'indicators': [
                    'broad ip assignment', 'all improvements', 'derivative ownership',
                    'work for hire', 'exclusive license', 'perpetual rights'
                ],
                'base_probability': 'high',
                'base_impact': 'medium'
            },
            'operational': {
                'indicators': [
                    'exclusive', 'sole source', 'single supplier', 'dependency',
                    'critical path', 'no alternatives', 'key person'
                ],
                'base_probability': 'low',
                'base_impact': 'high'
            },
            'compliance': {
                'indicators': [
                    'regulatory', 'government approval', 'license required',
                    'audit', 'reporting obligations', 'certification'
                ],
                'base_probability': 'medium',
                'base_impact': 'medium'
            },
            'reputational': {
                'indicators': [
                    'public disclosure', 'media attention', 'brand damage',
                    'reputation', 'publicity', 'public relations'
                ],
                'base_probability': 'low',
                'base_impact': 'medium'
            },
            'data_security': {
                'indicators': [
                    'personal data', 'confidential information', 'data breach',
                    'security', 'privacy', 'gdpr', 'hipaa'
                ],
                'base_probability': 'medium',
                'base_impact': 'high'
            }
        }
        
        risk_id_counter = 1
        
        for category, config in risk_categories.items():
            indicators_found = []
            section_refs = []
            
            for indicator in config['indicators']:
                if indicator in content:
                    indicators_found.append(indicator)
                    # Find sections containing this indicator
                    pattern = re.escape(indicator)
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        section = self._find_containing_section(match.start(), [])
                        if section and section not in section_refs:
                            section_refs.append(section)
            
            if indicators_found:
                # Adjust probability and impact based on number of indicators
                probability = self._adjust_risk_level(
                    config['base_probability'], 
                    len(indicators_found), 
                    len(config['indicators'])
                )
                impact = config['base_impact']
                
                # Calculate overall risk
                overall_risk = self._calculate_overall_risk(probability, impact)
                
                # Generate mitigation strategies
                mitigation_strategies = self._generate_mitigation_strategies(category, indicators_found)
                
                # Determine responsible party
                responsible_party = self._determine_risk_owner(category)
                
                risk = RiskMatrixEntry(
                    risk_id=f"RISK-{risk_id_counter:03d}",
                    risk_category=category,
                    description=f"{category.title()} risk due to: {', '.join(indicators_found[:3])}",
                    probability=probability,
                    impact=impact,
                    overall_risk=overall_risk,
                    mitigation_strategies=mitigation_strategies,
                    responsible_party=responsible_party,
                    section_references=section_refs
                )
                
                risks.append(risk)
                risk_id_counter += 1
        
        # Sort risks by overall risk level
        risk_priority = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1
        }
        
        risks.sort(key=lambda r: risk_priority[r.overall_risk], reverse=True)
        
        return risks
    
    def _identify_compliance_requirements(self, document: Document) -> List[ComplianceRequirement]:
        """Identify compliance requirements and regulatory obligations"""
        requirements = []
        content = document.content.lower()
        
        # Compliance frameworks and their indicators
        frameworks = {
            'GDPR': {
                'indicators': ['gdpr', 'general data protection regulation', 'personal data', 'data subject'],
                'description': 'General Data Protection Regulation compliance for personal data processing'
            },
            'HIPAA': {
                'indicators': ['hipaa', 'health insurance portability', 'protected health information', 'phi'],
                'description': 'HIPAA compliance for protected health information'
            },
            'SOX': {
                'indicators': ['sarbanes-oxley', 'sox', 'financial reporting', 'internal controls'],
                'description': 'Sarbanes-Oxley compliance for financial reporting and controls'
            },
            'FDA': {
                'indicators': ['fda', 'food and drug administration', 'clinical trial', 'medical device'],
                'description': 'FDA regulatory compliance for medical products and research'
            },
            'Export Control': {
                'indicators': ['itar', 'ear', 'export control', 'dual use', 'controlled technology'],
                'description': 'Export control compliance for controlled technologies and information'
            },
            'Environmental': {
                'indicators': ['epa', 'environmental protection', 'hazardous materials', 'waste disposal'],
                'description': 'Environmental compliance for hazardous materials and waste'
            },
            'Research Ethics': {
                'indicators': ['irb', 'institutional review board', 'human subjects', 'animal care', 'iacuc'],
                'description': 'Research ethics compliance for human and animal subjects'
            }
        }
        
        req_id_counter = 1
        
        for framework, config in frameworks.items():
            applicable_sections = []
            found_indicators = []
            
            for indicator in config['indicators']:
                if indicator in content:
                    found_indicators.append(indicator)
                    # Find sections containing this indicator
                    pattern = re.escape(indicator)
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        section = self._find_containing_section(match.start(), [])
                        if section and section not in applicable_sections:
                            applicable_sections.append(section)
            
            if found_indicators:
                # Extract compliance deadline
                deadline = self._extract_compliance_deadline(content, found_indicators)
                
                # Determine responsible party
                responsible_party = self._determine_compliance_owner(framework)
                
                # Determine verification method
                verification_method = self._determine_verification_method(framework)
                
                # Extract potential penalties
                penalties = self._extract_penalties(content, found_indicators)
                
                requirement = ComplianceRequirement(
                    requirement_id=f"COMP-{req_id_counter:03d}",
                    regulatory_framework=framework,
                    description=config['description'],
                    applicable_sections=applicable_sections,
                    compliance_deadline=deadline,
                    responsible_party=responsible_party,
                    verification_method=verification_method,
                    penalties=penalties
                )
                
                requirements.append(requirement)
                req_id_counter += 1
        
        return requirements
    
    def _analyze_key_relationships(
        self,
        cross_references: List[CrossReference],
        timeline_events: List[TimelineEvent],
        party_obligations: Dict[str, List[PartyObligation]]
    ) -> List[Dict[str, Any]]:
        """Analyze key relationships between different analysis components"""
        relationships = []
        
        # Relationship between timeline events and obligations
        for party, obligations in party_obligations.items():
            for obligation in obligations:
                # Find related timeline events
                related_events = []
                for event in timeline_events:
                    if (obligation.description.lower() in event.description.lower() or
                        any(keyword in event.description.lower() 
                            for keyword in obligation.description.lower().split()[:3])):
                        related_events.append(event)
                
                if related_events:
                    relationships.append({
                        'type': 'obligation_timeline',
                        'party': party,
                        'obligation': obligation.description,
                        'related_events': [e.description for e in related_events],
                        'criticality': obligation.priority
                    })
        
        # Cross-reference clusters (highly interconnected sections)
        section_connections = {}
        for cross_ref in cross_references:
            source = cross_ref.source_section
            target = cross_ref.target_section
            
            if source not in section_connections:
                section_connections[source] = set()
            if target not in section_connections:
                section_connections[target] = set()
            
            section_connections[source].add(target)
            section_connections[target].add(source)
        
        # Find highly connected sections (hubs)
        for section, connections in section_connections.items():
            if len(connections) >= 3:  # Threshold for "highly connected"
                relationships.append({
                    'type': 'section_hub',
                    'section': section,
                    'connections': list(connections),
                    'connection_count': len(connections),
                    'importance': 'high' if len(connections) >= 5 else 'medium'
                })
        
        # Critical path analysis for timeline events
        critical_events = [e for e in timeline_events if e.criticality == 'high']
        if len(critical_events) >= 2:
            relationships.append({
                'type': 'critical_path',
                'events': [e.description for e in critical_events],
                'total_events': len(critical_events),
                'risk_level': 'high' if len(critical_events) >= 5 else 'medium'
            })
        
        return relationships
    
    # Helper methods
    
    def _initialize_section_patterns(self) -> Dict[str, str]:
        """Initialize patterns for identifying document sections"""
        return {
            'section': r'(?:Section|Article)\s+(\d+(?:\.\d+)*)\s*[-.]?\s*([^\n]*)',
            'paragraph': r'(?:Paragraph|Para)\s+(\d+(?:\.\d+)*)\s*[-.]?\s*([^\n]*)',
            'clause': r'(?:Clause)\s+(\d+(?:\.\d+)*)\s*[-.]?\s*([^\n]*)',
            'exhibit': r'(?:Exhibit|Appendix|Schedule)\s+([A-Z]|\d+)\s*[-:]?\s*([^\n]*)'
        }
    
    def _initialize_date_patterns(self) -> List[str]:
        """Initialize patterns for date recognition"""
        return [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',
            r'\b\d{4}-\d{1,2}-\d{1,2}\b'
        ]
    
    def _initialize_obligation_keywords(self) -> Dict[str, List[str]]:
        """Initialize keywords for different obligation types"""
        return {
            'payment': ['pay', 'payment', 'fee', 'cost', 'expense', 'remuneration'],
            'delivery': ['deliver', 'provide', 'supply', 'furnish', 'give'],
            'performance': ['perform', 'execute', 'carry out', 'complete', 'fulfill'],
            'compliance': ['comply', 'adhere', 'conform', 'follow', 'observe'],
            'reporting': ['report', 'notify', 'inform', 'disclose', 'communicate'],
            'confidentiality': ['confidential', 'secret', 'proprietary', 'non-disclosure']
        }
    
    def _initialize_risk_indicators(self) -> Dict[str, List[str]]:
        """Initialize risk indicators for different categories"""
        return {
            'high_risk': ['unlimited', 'no limit', 'all', 'entire', 'complete', 'total'],
            'medium_risk': ['significant', 'substantial', 'material', 'important'],
            'low_risk': ['limited', 'restricted', 'capped', 'maximum', 'not to exceed']
        }
    
    def _initialize_compliance_frameworks(self) -> List[str]:
        """Initialize compliance frameworks and regulations"""
        return [
            'GDPR', 'HIPAA', 'SOX', 'ITAR', 'EAR', 'FCPA', 'OSHA',
            'FDA', 'EPA', 'FTC', 'SEC', 'COSO', 'ISO 27001', 'PCI DSS'
        ]
    
    def _find_containing_section(self, position: int, sections: List[Dict]) -> Optional[str]:
        """Find the section containing a given position in the document"""
        # Simple implementation - would need document structure for full implementation
        return f"Section {position // 1000 + 1}"  # Rough approximation
    
    def _get_section_text(self, section: Dict, content: str) -> str:
        """Get the text content of a section"""
        start_pos = section.get('start_pos', 0)
        # Simple implementation - extract next 500 characters
        return content[start_pos:start_pos + 500]
    
    def _get_section_identifier(self, section: Dict) -> str:
        """Get a string identifier for a section"""
        section_type = section.get('type', 'Section')
        section_number = section.get('number', 'Unknown')
        return f"{section_type} {section_number}"
    
    def _get_surrounding_context(self, position: int, content: str, context_length: int) -> str:
        """Get surrounding context for a position in the document"""
        start = max(0, position - context_length // 2)
        end = min(len(content), position + context_length // 2)
        return content[start:end]
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into a datetime object"""
        # Simple date parsing - would use more robust parsing in production
        try:
            # Handle common formats
            if '/' in date_str:
                return datetime.strptime(date_str, '%m/%d/%Y')
            elif '-' in date_str:
                return datetime.strptime(date_str, '%m-%d-%Y')
            else:
                # Handle month name format
                return datetime.strptime(date_str, '%B %d, %Y')
        except:
            return None
    
    def _extract_responsible_party(self, context: str) -> Optional[str]:
        """Extract responsible party from context"""
        party_indicators = ['provider', 'recipient', 'company', 'institution', 'party']
        context_lower = context.lower()
        
        for indicator in party_indicators:
            if indicator in context_lower:
                return indicator.title()
        
        return None
    
    def _assess_event_criticality(self, context: str) -> str:
        """Assess the criticality of a timeline event"""
        high_criticality_words = ['critical', 'essential', 'required', 'mandatory', 'must']
        medium_criticality_words = ['important', 'should', 'recommended', 'advisable']
        
        context_lower = context.lower()
        
        if any(word in context_lower for word in high_criticality_words):
            return 'high'
        elif any(word in context_lower for word in medium_criticality_words):
            return 'medium'
        else:
            return 'low'
    
    def _extract_dependencies(self, context: str) -> List[str]:
        """Extract dependencies from context"""
        dependency_patterns = [
            r'after\s+([^,\n]+)',
            r'upon\s+([^,\n]+)',
            r'following\s+([^,\n]+)',
            r'once\s+([^,\n]+)'
        ]
        
        dependencies = []
        for pattern in dependency_patterns:
            matches = re.finditer(pattern, context, re.IGNORECASE)
            for match in matches:
                dependencies.append(match.group(1).strip())
        
        return dependencies
    
    def _extract_party_names(self, content: str) -> List[str]:
        """Extract party names from document content"""
        parties = []
        
        # Common party patterns
        party_patterns = [
            r'(?:Provider|Recipient|Licensor|Licensee|Company|Institution|University)\s*[:\(]?\s*([^,\n\)]+)',
            r'Party\s+(?:A|B|1|2)\s*[:\(]?\s*([^,\n\)]+)'
        ]
        
        for pattern in party_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                party_name = match.group(1).strip().strip('()"')
                if len(party_name) > 2 and party_name not in parties:
                    parties.append(party_name)
        
        return parties
    
    def _determine_responsible_party(self, context: str, parties: List[str]) -> Optional[str]:
        """Determine which party is responsible based on context"""
        context_lower = context.lower()
        
        # Look for party names in context
        for party in parties:
            if party.lower() in context_lower:
                return party
        
        # Look for generic party indicators
        if 'provider' in context_lower:
            return 'Provider'
        elif 'recipient' in context_lower:
            return 'Recipient'
        elif 'company' in context_lower:
            return 'Company'
        
        return None
    
    def _extract_conditions(self, context: str) -> List[str]:
        """Extract conditions from context"""
        condition_patterns = [
            r'if\s+([^,\n]+)',
            r'provided\s+that\s+([^,\n]+)',
            r'subject\s+to\s+([^,\n]+)',
            r'unless\s+([^,\n]+)'
        ]
        
        conditions = []
        for pattern in condition_patterns:
            matches = re.finditer(pattern, context, re.IGNORECASE)
            for match in matches:
                conditions.append(match.group(1).strip())
        
        return conditions
    
    def _extract_consequences(self, context: str) -> List[str]:
        """Extract consequences from context"""
        consequence_patterns = [
            r'(?:failure|breach|violation)\s+(?:to|of)\s+([^,\n]+)\s+(?:shall|will|may)\s+result\s+in\s+([^,\n]+)',
            r'in\s+the\s+event\s+of\s+([^,\n]+),\s+([^,\n]+)',
            r'penalty\s+(?:of|for)\s+([^,\n]+)'
        ]
        
        consequences = []
        for pattern in consequence_patterns:
            matches = re.finditer(pattern, context, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    consequences.append(f"{match.group(1)} -> {match.group(2)}")
                else:
                    consequences.append(match.group(1))
        
        return consequences
    
    def _extract_deadline_from_context(self, context: str) -> Optional[str]:
        """Extract deadline information from context"""
        deadline_patterns = [
            r'within\s+(\d+\s+(?:days?|weeks?|months?|years?))',
            r'by\s+([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})',
            r'no\s+later\s+than\s+([^,\n]+)'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _assess_obligation_priority(self, context: str, obligation_type: ObligationType) -> str:
        """Assess the priority of an obligation"""
        high_priority_words = ['critical', 'essential', 'mandatory', 'required', 'must']
        medium_priority_words = ['important', 'should', 'recommended']
        
        context_lower = context.lower()
        
        # Payment and compliance obligations are generally high priority
        if obligation_type in [ObligationType.PAYMENT, ObligationType.COMPLIANCE]:
            return 'high'
        
        if any(word in context_lower for word in high_priority_words):
            return 'high'
        elif any(word in context_lower for word in medium_priority_words):
            return 'medium'
        else:
            return 'low'
    
    def _adjust_risk_level(self, base_level: str, indicators_found: int, total_indicators: int) -> str:
        """Adjust risk level based on number of indicators found"""
        ratio = indicators_found / total_indicators
        
        if ratio >= 0.7:  # 70% or more indicators found
            if base_level == 'low':
                return 'medium'
            elif base_level == 'medium':
                return 'high'
            else:
                return base_level
        elif ratio >= 0.4:  # 40-70% indicators found
            return base_level
        else:  # Less than 40% indicators found
            if base_level == 'high':
                return 'medium'
            elif base_level == 'medium':
                return 'low'
            else:
                return base_level
    
    def _calculate_overall_risk(self, probability: str, impact: str) -> RiskLevel:
        """Calculate overall risk level from probability and impact"""
        risk_matrix = {
            ('low', 'low'): RiskLevel.LOW,
            ('low', 'medium'): RiskLevel.LOW,
            ('low', 'high'): RiskLevel.MEDIUM,
            ('medium', 'low'): RiskLevel.LOW,
            ('medium', 'medium'): RiskLevel.MEDIUM,
            ('medium', 'high'): RiskLevel.HIGH,
            ('high', 'low'): RiskLevel.MEDIUM,
            ('high', 'medium'): RiskLevel.HIGH,
            ('high', 'high'): RiskLevel.CRITICAL
        }
        
        return risk_matrix.get((probability, impact), RiskLevel.MEDIUM)
    
    def _generate_mitigation_strategies(self, category: str, indicators: List[str]) -> List[str]:
        """Generate mitigation strategies for a risk category"""
        strategies = {
            'financial': [
                'Negotiate liability caps and limitations',
                'Obtain appropriate insurance coverage',
                'Include indemnification provisions',
                'Establish escrow or security deposits'
            ],
            'intellectual_property': [
                'Negotiate carve-outs for background IP',
                'Limit assignment to specific improvements',
                'Retain rights to independently developed IP',
                'Include patent prosecution cost-sharing'
            ],
            'operational': [
                'Develop backup supplier relationships',
                'Negotiate performance guarantees',
                'Include termination rights for non-performance',
                'Establish service level agreements'
            ],
            'compliance': [
                'Establish compliance monitoring procedures',
                'Regular legal review of regulatory changes',
                'Maintain documentation and audit trails',
                'Provide compliance training to staff'
            ],
            'reputational': [
                'Develop crisis communication plan',
                'Monitor media and social media mentions',
                'Establish stakeholder communication protocols',
                'Maintain professional liability insurance'
            ],
            'data_security': [
                'Implement data encryption and access controls',
                'Conduct regular security audits',
                'Establish incident response procedures',
                'Provide data security training'
            ]
        }
        
        return strategies.get(category, ['Conduct regular risk assessment', 'Monitor compliance'])
    
    def _determine_risk_owner(self, category: str) -> Optional[str]:
        """Determine who should own/manage a particular risk category"""
        owners = {
            'financial': 'Finance Team',
            'intellectual_property': 'Legal/IP Team',
            'operational': 'Operations Team',
            'compliance': 'Compliance Officer',
            'reputational': 'Communications Team',
            'data_security': 'IT Security Team'
        }
        
        return owners.get(category)
    
    def _extract_compliance_deadline(self, content: str, indicators: List[str]) -> Optional[str]:
        """Extract compliance deadline from content"""
        # Look for deadlines near compliance indicators
        for indicator in indicators:
            pattern = rf'{re.escape(indicator)}.{{0,200}}?(?:by|within|before)\s+([^,\n]+)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _determine_compliance_owner(self, framework: str) -> Optional[str]:
        """Determine who should own compliance for a framework"""
        owners = {
            'GDPR': 'Data Protection Officer',
            'HIPAA': 'Privacy Officer',
            'SOX': 'Finance Team',
            'FDA': 'Regulatory Affairs',
            'Export Control': 'Export Control Officer',
            'Environmental': 'Environmental Health & Safety',
            'Research Ethics': 'IRB/IACUC Administrator'
        }
        
        return owners.get(framework, 'Compliance Officer')
    
    def _determine_verification_method(self, framework: str) -> str:
        """Determine verification method for compliance framework"""
        methods = {
            'GDPR': 'Data protection impact assessment and audit',
            'HIPAA': 'Privacy and security risk assessment',
            'SOX': 'Internal controls testing and certification',
            'FDA': 'Regulatory submission and inspection',
            'Export Control': 'Export license review and audit',
            'Environmental': 'Environmental compliance audit',
            'Research Ethics': 'IRB/IACUC review and approval'
        }
        
        return methods.get(framework, 'Compliance audit and documentation review')
    
    def _extract_penalties(self, content: str, indicators: List[str]) -> List[str]:
        """Extract potential penalties from content"""
        penalty_patterns = [
            r'penalty\s+(?:of|for)\s+([^,\n]+)',
            r'fine\s+(?:of|up to)\s+([^,\n]+)',
            r'damages\s+(?:of|up to)\s+([^,\n]+)',
            r'violation\s+(?:may|shall|will)\s+result\s+in\s+([^,\n]+)'
        ]
        
        penalties = []
        for pattern in penalty_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                penalties.append(match.group(1).strip())
        
        return penalties[:3]  # Limit to top 3 penalties