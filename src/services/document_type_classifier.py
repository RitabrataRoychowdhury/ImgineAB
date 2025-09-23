"""
Document Type Classifier for automatic classification of legal documents.
Supports contracts, MTAs, purchase agreements, and disclosure schedules.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Supported document types"""
    CONTRACT = "contract"
    MTA = "material_transfer_agreement"
    PURCHASE_AGREEMENT = "purchase_agreement"
    DISCLOSURE_SCHEDULE = "disclosure_schedule"
    NDA = "non_disclosure_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    EMPLOYMENT_AGREEMENT = "employment_agreement"
    LEASE_AGREEMENT = "lease_agreement"
    UNKNOWN = "unknown"

@dataclass
class DocumentTypeResult:
    """Result of document type classification"""
    document_type: DocumentType
    confidence: float
    secondary_types: List[Tuple[DocumentType, float]]
    classification_reasons: List[str]
    suggested_template: str

@dataclass
class TemplateCustomization:
    """Customization suggestion for document templates"""
    section_name: str
    priority: str  # "high", "medium", "low"
    reason: str
    suggested_content: Optional[str] = None

class DocumentTypeClassifier:
    """
    Classifier for identifying document types based on content analysis.
    Uses pattern matching and keyword analysis to determine document type.
    """
    
    def __init__(self):
        self.classification_patterns = self._initialize_classification_patterns()
        self.template_mappings = self._initialize_template_mappings()
        
    def _initialize_classification_patterns(self) -> Dict[DocumentType, Dict[str, List[str]]]:
        """Initialize patterns for document type classification"""
        return {
            DocumentType.CONTRACT: {
                'keywords': [
                    'contract', 'agreement', 'party', 'parties', 'terms and conditions',
                    'obligations', 'performance', 'breach', 'termination', 'governing law',
                    'developer', 'client', 'services', 'fee', 'payment', 'completion'
                ],
                'phrases': [
                    'this agreement', 'the parties agree', 'terms of this contract',
                    'subject to the terms', 'in consideration of', 'mutual covenants',
                    'development agreement', 'service agreement', 'entered into',
                    'shall provide', 'total fee', 'governed by'
                ],
                'structure': [
                    'whereas', 'now therefore', 'witnesseth', 'recitals',
                    'definitions', 'representations and warranties', 'agreement is entered'
                ]
            },
            DocumentType.MTA: {
                'keywords': [
                    'material transfer', 'mta', 'research material', 'biological material',
                    'transfer', 'recipient', 'provider', 'research', 'publication',
                    'intellectual property', 'derivatives', 'modifications'
                ],
                'phrases': [
                    'material transfer agreement', 'research purposes only',
                    'original material', 'recipient scientist', 'provider scientist',
                    'publication rights', 'research results', 'biological materials'
                ],
                'structure': [
                    'material description', 'permitted uses', 'restrictions',
                    'publication policy', 'intellectual property rights'
                ]
            },
            DocumentType.PURCHASE_AGREEMENT: {
                'keywords': [
                    'purchase', 'buy', 'sell', 'buyer', 'seller', 'vendor',
                    'goods', 'products', 'delivery', 'payment', 'invoice',
                    'purchase order', 'specifications', 'warranty'
                ],
                'phrases': [
                    'purchase agreement', 'sale of goods', 'delivery terms',
                    'payment terms', 'purchase price', 'goods and services',
                    'delivery schedule', 'acceptance criteria'
                ],
                'structure': [
                    'purchase price', 'delivery terms', 'payment schedule',
                    'specifications', 'warranties', 'acceptance procedures'
                ]
            },
            DocumentType.DISCLOSURE_SCHEDULE: {
                'keywords': [
                    'disclosure', 'schedule', 'exhibit', 'attachment',
                    'representations', 'warranties', 'exceptions', 'qualifications',
                    'material adverse', 'knowledge', 'disclosure letter'
                ],
                'phrases': [
                    'disclosure schedule', 'disclosure letter', 'attached hereto',
                    'set forth in', 'except as disclosed', 'material contracts',
                    'financial statements', 'litigation matters'
                ],
                'structure': [
                    'schedule', 'exhibit', 'attachment', 'section references',
                    'cross-references', 'item numbers'
                ]
            },
            DocumentType.NDA: {
                'keywords': [
                    'confidential', 'confidentiality', 'non-disclosure', 'nda',
                    'proprietary', 'trade secret', 'confidential information',
                    'disclosing party', 'receiving party', 'non-use'
                ],
                'phrases': [
                    'non-disclosure agreement', 'confidentiality agreement',
                    'confidential information', 'proprietary information',
                    'trade secrets', 'disclosing party', 'receiving party'
                ],
                'structure': [
                    'definition of confidential information', 'permitted uses',
                    'restrictions', 'return of information', 'term'
                ]
            },
            DocumentType.SERVICE_AGREEMENT: {
                'keywords': [
                    'services', 'service provider', 'client', 'professional services',
                    'consulting', 'work', 'deliverables', 'statement of work',
                    'service level', 'performance standards', 'development', 'software',
                    'custom', 'developer', 'completion', 'defects', 'warranty'
                ],
                'phrases': [
                    'service agreement', 'professional services', 'consulting services',
                    'statement of work', 'service levels', 'deliverables',
                    'performance standards', 'service provider', 'development services',
                    'software development', 'custom software', 'free from defects'
                ],
                'structure': [
                    'scope of services', 'deliverables', 'service levels',
                    'performance metrics', 'acceptance criteria', 'development agreement'
                ]
            }
        }
    
    def _initialize_template_mappings(self) -> Dict[DocumentType, str]:
        """Initialize template mappings for different document types"""
        return {
            DocumentType.CONTRACT: "general_contract_template",
            DocumentType.MTA: "mta_template",
            DocumentType.PURCHASE_AGREEMENT: "purchase_agreement_template",
            DocumentType.DISCLOSURE_SCHEDULE: "disclosure_schedule_template",
            DocumentType.NDA: "nda_template",
            DocumentType.SERVICE_AGREEMENT: "service_agreement_template",
            DocumentType.EMPLOYMENT_AGREEMENT: "employment_agreement_template",
            DocumentType.LEASE_AGREEMENT: "lease_agreement_template",
            DocumentType.UNKNOWN: "general_template"
        }
    
    def classify_document_type(self, content: str, title: str = "") -> DocumentTypeResult:
        """
        Classify document type based on content analysis.
        Returns the most likely document type with confidence score.
        """
        try:
            # Calculate scores for each document type
            type_scores = {}
            classification_details = {}
            
            for doc_type in DocumentType:
                if doc_type == DocumentType.UNKNOWN:
                    continue
                    
                score, reasons = self._calculate_type_score(content, title, doc_type)
                type_scores[doc_type] = score
                classification_details[doc_type] = reasons
            
            # Find the best match
            if not type_scores:
                return self._create_unknown_result()
            
            best_type = max(type_scores.keys(), key=lambda k: type_scores[k])
            best_score = type_scores[best_type]
            
            # If confidence is too low, classify as unknown
            if best_score < 0.3:
                return self._create_unknown_result()
            
            # Get secondary types (sorted by score)
            secondary_types = [
                (doc_type, score) for doc_type, score in type_scores.items()
                if doc_type != best_type and score > 0.2
            ]
            secondary_types.sort(key=lambda x: x[1], reverse=True)
            
            return DocumentTypeResult(
                document_type=best_type,
                confidence=best_score,
                secondary_types=secondary_types[:3],  # Top 3 alternatives
                classification_reasons=classification_details[best_type],
                suggested_template=self.template_mappings[best_type]
            )
            
        except Exception as e:
            logger.error(f"Error classifying document type: {str(e)}")
            return self._create_unknown_result()
    
    def _calculate_type_score(self, content: str, title: str, doc_type: DocumentType) -> Tuple[float, List[str]]:
        """Calculate classification score for a specific document type"""
        if doc_type not in self.classification_patterns:
            return 0.0, []
        
        patterns = self.classification_patterns[doc_type]
        content_lower = content.lower()
        title_lower = title.lower()
        combined_text = f"{title_lower} {content_lower}"
        
        scores = []
        reasons = []
        
        # Score based on keywords
        keyword_score, keyword_reasons = self._score_keywords(
            combined_text, patterns.get('keywords', [])
        )
        scores.append(keyword_score * 0.4)  # 40% weight
        reasons.extend(keyword_reasons)
        
        # Score based on phrases
        phrase_score, phrase_reasons = self._score_phrases(
            combined_text, patterns.get('phrases', [])
        )
        scores.append(phrase_score * 0.4)  # 40% weight
        reasons.extend(phrase_reasons)
        
        # Score based on document structure
        structure_score, structure_reasons = self._score_structure(
            combined_text, patterns.get('structure', [])
        )
        scores.append(structure_score * 0.2)  # 20% weight
        reasons.extend(structure_reasons)
        
        # Calculate final score
        final_score = sum(scores)
        
        # Apply title boost if document type appears in title
        if any(keyword in title_lower for keyword in patterns.get('keywords', [])[:3]):
            final_score *= 1.2
            reasons.append(f"Document type keywords found in title")
        
        return min(1.0, final_score), reasons
    
    def _score_keywords(self, text: str, keywords: List[str]) -> Tuple[float, List[str]]:
        """Score based on keyword presence"""
        if not keywords:
            return 0.0, []
        
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in text:
                found_keywords.append(keyword)
        
        score = len(found_keywords) / len(keywords)
        reasons = []
        
        if found_keywords:
            reasons.append(f"Found keywords: {', '.join(found_keywords[:5])}")
        
        return score, reasons
    
    def _score_phrases(self, text: str, phrases: List[str]) -> Tuple[float, List[str]]:
        """Score based on phrase presence"""
        if not phrases:
            return 0.0, []
        
        found_phrases = []
        for phrase in phrases:
            if phrase.lower() in text:
                found_phrases.append(phrase)
        
        score = len(found_phrases) / len(phrases)
        reasons = []
        
        if found_phrases:
            reasons.append(f"Found phrases: {', '.join(found_phrases[:3])}")
        
        return score, reasons
    
    def _score_structure(self, text: str, structure_elements: List[str]) -> Tuple[float, List[str]]:
        """Score based on document structure elements"""
        if not structure_elements:
            return 0.0, []
        
        found_elements = []
        for element in structure_elements:
            # Look for structure elements as section headers or prominent text
            pattern = rf'\b{re.escape(element.lower())}\b'
            if re.search(pattern, text):
                found_elements.append(element)
        
        score = len(found_elements) / len(structure_elements)
        reasons = []
        
        if found_elements:
            reasons.append(f"Found structure elements: {', '.join(found_elements[:3])}")
        
        return score, reasons
    
    def _create_unknown_result(self) -> DocumentTypeResult:
        """Create result for unknown document type"""
        return DocumentTypeResult(
            document_type=DocumentType.UNKNOWN,
            confidence=0.0,
            secondary_types=[],
            classification_reasons=["Could not determine document type with sufficient confidence"],
            suggested_template=self.template_mappings[DocumentType.UNKNOWN]
        )
    
    def get_confidence_score(self, classification: str, content: str) -> float:
        """Get confidence score for a specific classification"""
        try:
            doc_type = DocumentType(classification)
            score, _ = self._calculate_type_score(content, "", doc_type)
            return score
        except (ValueError, KeyError):
            return 0.0
    
    def identify_document_subtypes(self, doc_type: str, content: str) -> List[str]:
        """Identify document subtypes based on content"""
        subtypes = []
        content_lower = content.lower()
        
        try:
            document_type = DocumentType(doc_type)
            
            if document_type == DocumentType.CONTRACT:
                if any(term in content_lower for term in ['employment', 'employee', 'job']):
                    subtypes.append('employment_contract')
                if any(term in content_lower for term in ['lease', 'rent', 'tenant']):
                    subtypes.append('lease_contract')
                if any(term in content_lower for term in ['service', 'consulting', 'professional']):
                    subtypes.append('service_contract')
                    
            elif document_type == DocumentType.MTA:
                if any(term in content_lower for term in ['biological', 'cell', 'tissue']):
                    subtypes.append('biological_mta')
                if any(term in content_lower for term in ['software', 'code', 'algorithm']):
                    subtypes.append('software_mta')
                    
            elif document_type == DocumentType.PURCHASE_AGREEMENT:
                if any(term in content_lower for term in ['software', 'license', 'saas']):
                    subtypes.append('software_purchase')
                if any(term in content_lower for term in ['equipment', 'machinery', 'hardware']):
                    subtypes.append('equipment_purchase')
                    
        except ValueError:
            pass
        
        return subtypes
    
    def suggest_template_customizations(self, doc_type: str, content: str) -> List[TemplateCustomization]:
        """Suggest template customizations based on document content"""
        customizations = []
        content_lower = content.lower()
        
        try:
            document_type = DocumentType(doc_type)
            
            # Common customizations based on content analysis
            if 'intellectual property' in content_lower or 'ip' in content_lower:
                customizations.append(TemplateCustomization(
                    section_name="Intellectual Property",
                    priority="high",
                    reason="Document contains intellectual property terms",
                    suggested_content="Detailed IP ownership and licensing terms"
                ))
            
            if any(term in content_lower for term in ['confidential', 'proprietary', 'trade secret']):
                customizations.append(TemplateCustomization(
                    section_name="Confidentiality",
                    priority="high",
                    reason="Document contains confidentiality requirements"
                ))
            
            if any(term in content_lower for term in ['indemnif', 'liability', 'damages']):
                customizations.append(TemplateCustomization(
                    section_name="Liability and Indemnification",
                    priority="high",
                    reason="Document contains liability and indemnification terms"
                ))
            
            if any(term in content_lower for term in ['governing law', 'jurisdiction', 'dispute']):
                customizations.append(TemplateCustomization(
                    section_name="Governing Law and Disputes",
                    priority="medium",
                    reason="Document contains governing law provisions"
                ))
            
            # Document-type specific customizations
            if document_type == DocumentType.MTA:
                if 'publication' in content_lower:
                    customizations.append(TemplateCustomization(
                        section_name="Publication Rights",
                        priority="high",
                        reason="MTA contains publication-related terms"
                    ))
                    
            elif document_type == DocumentType.PURCHASE_AGREEMENT:
                if any(term in content_lower for term in ['warranty', 'guarantee', 'defect']):
                    customizations.append(TemplateCustomization(
                        section_name="Warranties and Guarantees",
                        priority="high",
                        reason="Purchase agreement contains warranty terms"
                    ))
                    
        except ValueError:
            pass
        
        return customizations
    
    def register_custom_document_type(self, type_definition: Dict[str, Any]) -> bool:
        """Register a custom document type (placeholder for future enhancement)"""
        # This would allow organizations to define custom document types
        # For now, return False as not implemented
        logger.info(f"Custom document type registration requested: {type_definition}")
        return False