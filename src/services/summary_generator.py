"""
Summary Generator for creating structured document summaries.
Produces tailored summaries based on document type with comprehensive sections.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

from .document_type_classifier import DocumentType, DocumentTypeResult
from .enhanced_document_analyzer import DocumentAnalysis, KeyInformation
from .risk_analysis_engine import RiskAnalysis, Risk, RiskCategory

logger = logging.getLogger(__name__)

@dataclass
class DocumentSummary:
    """Complete document summary with all sections"""
    document_id: str
    title: str
    document_type: str
    overview: str
    key_terms: Dict[str, str]
    important_dates: List[Dict[str, Any]]
    parties_involved: List[Dict[str, str]]
    liabilities_and_risks: List[Dict[str, Any]]
    recommended_actions: List[str]
    document_type_specific_info: Dict[str, Any]
    confidence_indicators: Dict[str, float]
    summary_timestamp: datetime

class SummaryTemplate:
    """Template for generating document summaries"""
    
    def __init__(self, document_type: DocumentType):
        self.document_type = document_type
        self.sections = self._get_template_sections()
        self.priorities = self._get_section_priorities()
    
    def _get_template_sections(self) -> Dict[str, str]:
        """Get template sections for the document type"""
        base_sections = {
            "overview": "Document overview and purpose",
            "key_terms": "Important terms and definitions",
            "important_dates": "Critical dates and deadlines",
            "parties": "Parties involved and their roles",
            "risks": "Identified risks and liabilities",
            "actions": "Recommended actions and next steps"
        }
        
        # Document-type specific sections
        type_specific = {
            DocumentType.CONTRACT: {
                "performance_obligations": "Performance obligations and deliverables",
                "termination_clauses": "Termination conditions and procedures",
                "governing_law": "Governing law and dispute resolution"
            },
            DocumentType.MTA: {
                "material_description": "Description of transferred materials",
                "research_restrictions": "Research use restrictions and limitations",
                "publication_rights": "Publication and intellectual property rights",
                "compliance_requirements": "Regulatory and safety compliance"
            },
            DocumentType.PURCHASE_AGREEMENT: {
                "purchase_details": "Purchase specifications and quantities",
                "delivery_terms": "Delivery schedule and logistics",
                "payment_terms": "Payment schedule and methods",
                "warranties": "Product warranties and guarantees"
            },
            DocumentType.DISCLOSURE_SCHEDULE: {
                "disclosure_items": "Items disclosed by category",
                "exceptions": "Exceptions to representations and warranties",
                "material_contracts": "Material contracts and agreements",
                "financial_matters": "Financial disclosures and statements"
            },
            DocumentType.NDA: {
                "confidential_info": "Definition of confidential information",
                "permitted_uses": "Permitted uses and restrictions",
                "return_obligations": "Information return and destruction",
                "term_duration": "Agreement term and survival"
            }
        }
        
        base_sections.update(type_specific.get(self.document_type, {}))
        return base_sections
    
    def _get_section_priorities(self) -> Dict[str, int]:
        """Get priority levels for sections (1=highest, 5=lowest)"""
        return {
            "overview": 1,
            "key_terms": 2,
            "important_dates": 1,
            "parties": 2,
            "risks": 1,
            "actions": 1,
            "performance_obligations": 2,
            "termination_clauses": 3,
            "governing_law": 4,
            "material_description": 2,
            "research_restrictions": 1,
            "publication_rights": 2,
            "compliance_requirements": 3,
            "purchase_details": 2,
            "delivery_terms": 2,
            "payment_terms": 1,
            "warranties": 3,
            "disclosure_items": 2,
            "exceptions": 2,
            "material_contracts": 3,
            "financial_matters": 2,
            "confidential_info": 1,
            "permitted_uses": 2,
            "return_obligations": 3,
            "term_duration": 3
        }

class SummaryGenerator:
    """
    Generator for structured document summaries with document-type specific templates.
    Creates comprehensive summaries with Overview, Key Terms, Important Dates, 
    Liabilities & Risks, and Recommended Actions sections.
    """
    
    def __init__(self):
        self.templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize summary templates for different document types"""
        for doc_type in DocumentType:
            self.templates[doc_type] = SummaryTemplate(doc_type)
    
    def generate_summary(self, document_analysis: DocumentAnalysis, 
                        classification_result: DocumentTypeResult,
                        risk_analysis: RiskAnalysis) -> DocumentSummary:
        """
        Generate comprehensive document summary based on analysis results.
        """
        try:
            # Get appropriate template
            template = self.templates.get(
                classification_result.document_type, 
                self.templates[DocumentType.UNKNOWN]
            )
            
            # Generate each section
            overview = self._generate_overview(document_analysis, classification_result)
            key_terms = self._generate_key_terms(document_analysis)
            important_dates = self._generate_important_dates(document_analysis)
            parties = self._generate_parties_section(document_analysis)
            risks = self._generate_risks_section(risk_analysis)
            actions = self._generate_recommended_actions(document_analysis, risk_analysis)
            type_specific = self._generate_type_specific_info(
                document_analysis, classification_result, template
            )
            
            # Calculate confidence indicators
            confidence = self._calculate_confidence_indicators(
                document_analysis, classification_result, risk_analysis
            )
            
            return DocumentSummary(
                document_id=document_analysis.document_id,
                title=document_analysis.metadata.title,
                document_type=classification_result.document_type.value,
                overview=overview,
                key_terms=key_terms,
                important_dates=important_dates,
                parties_involved=parties,
                liabilities_and_risks=risks,
                recommended_actions=actions,
                document_type_specific_info=type_specific,
                confidence_indicators=confidence,
                summary_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return self._create_error_summary(document_analysis.document_id)
    
    def _generate_overview(self, analysis: DocumentAnalysis, 
                          classification: DocumentTypeResult) -> str:
        """Generate document overview section"""
        try:
            doc_type = classification.document_type.value.replace('_', ' ').title()
            confidence = f"{classification.confidence:.1%}"
            
            # Basic overview
            overview_parts = [
                f"This document has been classified as a {doc_type} with {confidence} confidence.",
                f"The document contains {analysis.metadata.word_count} words across {analysis.metadata.page_count} pages."
            ]
            
            # Add parties information if available
            if analysis.key_information.parties:
                party_names = [p.name for p in analysis.key_information.parties[:3]]
                if len(party_names) == 1:
                    overview_parts.append(f"The primary party involved is {party_names[0]}.")
                elif len(party_names) == 2:
                    overview_parts.append(f"The main parties are {party_names[0]} and {party_names[1]}.")
                else:
                    overview_parts.append(f"Key parties include {', '.join(party_names[:-1])}, and {party_names[-1]}.")
            
            # Add financial information if available
            if analysis.key_information.financial_terms:
                financial_count = len(analysis.key_information.financial_terms)
                overview_parts.append(f"The document contains {financial_count} financial terms or obligations.")
            
            # Add date information if available
            if analysis.key_information.key_dates:
                date_count = len(analysis.key_information.key_dates)
                overview_parts.append(f"There are {date_count} important dates identified in the document.")
            
            # Document-specific overview additions
            overview_parts.extend(self._get_type_specific_overview(analysis, classification))
            
            return " ".join(overview_parts)
            
        except Exception as e:
            logger.error(f"Error generating overview: {str(e)}")
            return "Document overview could not be generated due to analysis errors."
    
    def _get_type_specific_overview(self, analysis: DocumentAnalysis, 
                                   classification: DocumentTypeResult) -> List[str]:
        """Get document-type specific overview additions"""
        additions = []
        doc_type = classification.document_type
        content = analysis.extracted_text.lower()
        
        if doc_type == DocumentType.CONTRACT:
            if 'termination' in content:
                additions.append("The contract includes termination provisions.")
            if 'renewal' in content:
                additions.append("Renewal terms are specified in the agreement.")
                
        elif doc_type == DocumentType.MTA:
            if 'research' in content:
                additions.append("The agreement governs research material transfer.")
            if 'publication' in content:
                additions.append("Publication rights and restrictions are addressed.")
                
        elif doc_type == DocumentType.PURCHASE_AGREEMENT:
            if 'delivery' in content:
                additions.append("Delivery terms and schedules are specified.")
            if 'warranty' in content:
                additions.append("Product warranties and guarantees are included.")
                
        elif doc_type == DocumentType.NDA:
            if 'confidential' in content:
                additions.append("The agreement establishes confidentiality obligations.")
            if 'return' in content:
                additions.append("Information return requirements are specified.")
        
        return additions
    
    def _generate_key_terms(self, analysis: DocumentAnalysis) -> Dict[str, str]:
        """Generate key terms section"""
        key_terms = {}
        
        # Add extracted definitions
        key_terms.update(analysis.key_information.definitions)
        
        # Add important financial terms
        for financial_term in analysis.key_information.financial_terms[:5]:
            if financial_term.amount:
                key_terms[f"{financial_term.term_type.title()} Amount"] = (
                    f"{financial_term.currency} {financial_term.amount:,.2f} - {financial_term.description[:100]}..."
                )
        
        # Add key obligations as terms
        for obligation in analysis.key_information.obligations[:3]:
            term_key = f"{obligation.obligation_type.title()} Obligation"
            key_terms[term_key] = f"{obligation.party}: {obligation.description[:150]}..."
        
        # Add governing clauses
        for i, clause in enumerate(analysis.key_information.governing_clauses[:2]):
            key_terms[f"Governing Clause {i+1}"] = clause[:200] + "..." if len(clause) > 200 else clause
        
        return key_terms
    
    def _generate_important_dates(self, analysis: DocumentAnalysis) -> List[Dict[str, Any]]:
        """Generate important dates section"""
        dates = []
        
        for date_item in analysis.key_information.key_dates:
            dates.append({
                "date": date_item.date.strftime("%Y-%m-%d"),
                "description": date_item.description,
                "type": date_item.date_type,
                "criticality": date_item.criticality,
                "days_from_now": (date_item.date - datetime.now()).days
            })
        
        # Sort by date
        dates.sort(key=lambda x: x["date"])
        
        return dates
    
    def _generate_parties_section(self, analysis: DocumentAnalysis) -> List[Dict[str, str]]:
        """Generate parties involved section"""
        parties = []
        
        for party in analysis.key_information.parties:
            party_info = {
                "name": party.name,
                "role": party.role,
                "entity_type": party.legal_entity_type or "Not specified"
            }
            if party.contact_info:
                party_info["contact"] = party.contact_info
            parties.append(party_info)
        
        return parties
    
    def _generate_risks_section(self, risk_analysis: RiskAnalysis) -> List[Dict[str, Any]]:
        """Generate liabilities and risks section"""
        risks = []
        
        # Get high and medium severity risks
        for category, category_risks in risk_analysis.risk_categories.items():
            for risk in category_risks:
                if risk.severity.value in ['high', 'critical', 'medium']:
                    risks.append({
                        "id": risk.risk_id,
                        "description": risk.description,
                        "category": risk.category.value,
                        "severity": risk.severity.value,
                        "probability": f"{risk.probability:.1%}",
                        "impact": risk.impact_description,
                        "affected_parties": risk.affected_parties,
                        "timeframe": risk.materialization_timeframe,
                        "mitigation_available": len(risk.mitigation_strategies) > 0
                    })
        
        # Sort by severity and probability
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        risks.sort(key=lambda x: (severity_order.get(x['severity'], 0), float(x['probability'].rstrip('%'))/100), reverse=True)
        
        return risks[:10]  # Limit to top 10 risks
    
    def _generate_recommended_actions(self, analysis: DocumentAnalysis, 
                                    risk_analysis: RiskAnalysis) -> List[str]:
        """Generate recommended actions section"""
        actions = []
        
        # Risk-based recommendations
        high_risks = [
            risk for risks in risk_analysis.risk_categories.values() 
            for risk in risks if risk.severity.value in ['high', 'critical']
        ]
        
        if high_risks:
            actions.append(f"Address {len(high_risks)} high-severity risks identified in the analysis")
        
        # Date-based recommendations
        upcoming_dates = [
            date for date in analysis.key_information.key_dates
            if (date.date - datetime.now()).days <= 90 and (date.date - datetime.now()).days > 0
        ]
        
        if upcoming_dates:
            actions.append(f"Monitor {len(upcoming_dates)} upcoming important dates within 90 days")
        
        # Financial recommendations
        if analysis.key_information.financial_terms:
            high_value_terms = [
                term for term in analysis.key_information.financial_terms
                if term.amount and term.amount > 10000
            ]
            if high_value_terms:
                actions.append("Review high-value financial obligations and ensure adequate budgeting")
        
        # Obligation-based recommendations
        high_criticality_obligations = [
            obligation for obligation in analysis.key_information.obligations
            if obligation.criticality == 'high'
        ]
        
        if high_criticality_obligations:
            actions.append("Establish processes to fulfill high-criticality obligations")
        
        # Document-type specific recommendations
        actions.extend(self._get_type_specific_actions(analysis))
        
        # General recommendations
        if not actions:
            actions.extend([
                "Conduct regular review of document terms and obligations",
                "Establish monitoring system for key dates and deadlines",
                "Ensure all parties understand their roles and responsibilities"
            ])
        
        # Add risk mitigation recommendations
        if risk_analysis.recommendations:
            actions.extend(risk_analysis.recommendations[:3])
        
        return actions[:8]  # Limit to 8 recommendations
    
    def _get_type_specific_actions(self, analysis: DocumentAnalysis) -> List[str]:
        """Get document-type specific recommended actions"""
        actions = []
        content = analysis.extracted_text.lower()
        
        # Contract-specific actions
        if 'contract' in content or 'agreement' in content:
            if 'termination' in content:
                actions.append("Review termination clauses and ensure compliance procedures are in place")
            if 'indemnification' in content:
                actions.append("Assess indemnification exposure and consider insurance coverage")
        
        # MTA-specific actions
        if 'material transfer' in content or 'mta' in content:
            actions.append("Ensure proper material handling and storage procedures are established")
            if 'publication' in content:
                actions.append("Establish publication review process with material provider")
        
        # Purchase agreement actions
        if 'purchase' in content or 'buy' in content:
            actions.append("Verify delivery schedules and acceptance procedures")
            if 'warranty' in content:
                actions.append("Document warranty terms and establish claim procedures")
        
        # NDA-specific actions
        if 'confidential' in content or 'non-disclosure' in content:
            actions.append("Implement information security measures for confidential data")
            actions.append("Train staff on confidentiality obligations and restrictions")
        
        return actions
    
    def _generate_type_specific_info(self, analysis: DocumentAnalysis,
                                   classification: DocumentTypeResult,
                                   template: SummaryTemplate) -> Dict[str, Any]:
        """Generate document-type specific information"""
        type_info = {}
        doc_type = classification.document_type
        content = analysis.extracted_text.lower()
        
        if doc_type == DocumentType.CONTRACT:
            type_info.update(self._extract_contract_specific_info(analysis, content))
        elif doc_type == DocumentType.MTA:
            type_info.update(self._extract_mta_specific_info(analysis, content))
        elif doc_type == DocumentType.PURCHASE_AGREEMENT:
            type_info.update(self._extract_purchase_specific_info(analysis, content))
        elif doc_type == DocumentType.DISCLOSURE_SCHEDULE:
            type_info.update(self._extract_disclosure_specific_info(analysis, content))
        elif doc_type == DocumentType.NDA:
            type_info.update(self._extract_nda_specific_info(analysis, content))
        
        return type_info
    
    def _extract_contract_specific_info(self, analysis: DocumentAnalysis, content: str) -> Dict[str, Any]:
        """Extract contract-specific information"""
        info = {}
        
        # Performance obligations
        obligations = [
            obligation for obligation in analysis.key_information.obligations
            if obligation.obligation_type in ['delivery', 'performance']
        ]
        if obligations:
            info['performance_obligations'] = [
                {
                    'party': ob.party,
                    'description': ob.description,
                    'deadline': ob.deadline.isoformat() if ob.deadline else None
                }
                for ob in obligations[:5]
            ]
        
        # Termination information
        if 'termination' in content:
            info['has_termination_clauses'] = True
            info['termination_summary'] = "Termination provisions are included in the contract"
        
        # Governing law
        if analysis.key_information.governing_clauses:
            info['governing_law'] = analysis.key_information.governing_clauses[0]
        
        return info
    
    def _extract_mta_specific_info(self, analysis: DocumentAnalysis, content: str) -> Dict[str, Any]:
        """Extract MTA-specific information"""
        info = {}
        
        # Research restrictions
        if 'research' in content:
            info['research_purpose'] = True
            if 'commercial' in content:
                info['commercial_use_restricted'] = 'commercial' in content and 'not' in content
        
        # Publication rights
        if 'publication' in content:
            info['publication_rights_addressed'] = True
            info['publication_summary'] = "Publication rights and review processes are specified"
        
        # Material description
        material_terms = [
            term for term in analysis.key_information.definitions.keys()
            if any(keyword in term.lower() for keyword in ['material', 'sample', 'specimen'])
        ]
        if material_terms:
            info['material_types'] = material_terms[:3]
        
        return info
    
    def _extract_purchase_specific_info(self, analysis: DocumentAnalysis, content: str) -> Dict[str, Any]:
        """Extract purchase agreement specific information"""
        info = {}
        
        # Purchase details
        purchase_terms = [
            term for term in analysis.key_information.financial_terms
            if term.term_type in ['total_value', 'payment']
        ]
        if purchase_terms:
            info['purchase_value'] = {
                'amount': purchase_terms[0].amount,
                'currency': purchase_terms[0].currency
            }
        
        # Delivery terms
        delivery_obligations = [
            ob for ob in analysis.key_information.obligations
            if ob.obligation_type == 'delivery'
        ]
        if delivery_obligations:
            info['delivery_obligations'] = len(delivery_obligations)
        
        # Warranties
        if 'warranty' in content or 'guarantee' in content:
            info['warranties_included'] = True
        
        return info
    
    def _extract_disclosure_specific_info(self, analysis: DocumentAnalysis, content: str) -> Dict[str, Any]:
        """Extract disclosure schedule specific information"""
        info = {}
        
        # Disclosure categories
        if 'schedule' in content:
            info['is_schedule_format'] = True
        
        # Material contracts
        if 'material contract' in content:
            info['material_contracts_disclosed'] = True
        
        # Financial disclosures
        if analysis.key_information.financial_terms:
            info['financial_disclosures'] = len(analysis.key_information.financial_terms)
        
        return info
    
    def _extract_nda_specific_info(self, analysis: DocumentAnalysis, content: str) -> Dict[str, Any]:
        """Extract NDA-specific information"""
        info = {}
        
        # Confidential information definition
        conf_definitions = [
            term for term in analysis.key_information.definitions.keys()
            if 'confidential' in term.lower()
        ]
        if conf_definitions:
            info['confidential_info_defined'] = True
        
        # Term duration
        duration_dates = [
            date for date in analysis.key_information.key_dates
            if date.date_type in ['expiration', 'termination']
        ]
        if duration_dates:
            info['agreement_term'] = duration_dates[0].date.strftime("%Y-%m-%d")
        
        # Return obligations
        if 'return' in content or 'destroy' in content:
            info['return_obligations'] = True
        
        return info
    
    def _calculate_confidence_indicators(self, analysis: DocumentAnalysis,
                                       classification: DocumentTypeResult,
                                       risk_analysis: RiskAnalysis) -> Dict[str, float]:
        """Calculate confidence indicators for the summary"""
        return {
            'document_classification': classification.confidence,
            'content_extraction': analysis.confidence_scores.get('overall', 0.0),
            'risk_analysis': risk_analysis.confidence_level,
            'overall_summary': (
                classification.confidence + 
                analysis.confidence_scores.get('overall', 0.0) + 
                risk_analysis.confidence_level
            ) / 3
        }
    
    def _create_error_summary(self, document_id: str) -> DocumentSummary:
        """Create error summary when generation fails"""
        return DocumentSummary(
            document_id=document_id,
            title="Summary Generation Error",
            document_type="unknown",
            overview="Summary could not be generated due to analysis errors.",
            key_terms={},
            important_dates=[],
            parties_involved=[],
            liabilities_and_risks=[],
            recommended_actions=["Review document manually", "Re-upload document if corrupted"],
            document_type_specific_info={},
            confidence_indicators={'overall_summary': 0.0},
            summary_timestamp=datetime.now()
        )