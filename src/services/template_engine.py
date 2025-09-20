"""Template Engine for customizable document analysis."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.models.document import Document, AnalysisTemplate
from src.storage.document_storage import DocumentStorage
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class TemplateEngine:
    """Engine for managing and applying analysis templates."""
    
    def __init__(self, storage: DocumentStorage):
        self.storage = storage
        self._predefined_templates = self._initialize_predefined_templates()
    
    def get_predefined_templates(self) -> List[AnalysisTemplate]:
        """Get all predefined analysis templates."""
        return list(self._predefined_templates.values())
    
    def create_custom_template(self, template_spec: Dict[str, Any]) -> AnalysisTemplate:
        """
        Create a custom analysis template.
        
        Args:
            template_spec: Dictionary containing template specifications
            
        Returns:
            Created AnalysisTemplate
        """
        template_id = str(uuid.uuid4())
        
        template = AnalysisTemplate(
            template_id=template_id,
            name=template_spec['name'],
            description=template_spec['description'],
            document_types=template_spec.get('document_types', []),
            analysis_sections=template_spec.get('analysis_sections', []),
            custom_prompts=template_spec.get('custom_prompts', {}),
            parameters=template_spec.get('parameters', {}),
            created_by=template_spec.get('created_by', 'system'),
            version=template_spec.get('version', '1.0'),
            is_active=template_spec.get('is_active', True)
        )
        
        # Store the template (would need to implement storage methods)
        logger.info(f"Created custom template: {template.name} ({template_id})")
        
        return template
    
    def recommend_template(self, document: Document) -> Optional[AnalysisTemplate]:
        """
        Recommend the most appropriate template for a document.
        
        Args:
            document: Document to analyze
            
        Returns:
            Recommended AnalysisTemplate or None
        """
        # Check document type and content to recommend template
        document_type = document.document_type or ""
        legal_type = document.legal_document_type or ""
        
        # Priority order for template matching
        if document.is_legal_document:
            if "contract" in legal_type.lower() or "agreement" in legal_type.lower():
                return self._predefined_templates.get("contract_analysis")
            elif "nda" in legal_type.lower() or "confidentiality" in legal_type.lower():
                return self._predefined_templates.get("nda_analysis")
            elif "mta" in legal_type.lower() or "transfer" in legal_type.lower():
                return self._predefined_templates.get("mta_analysis")
            else:
                return self._predefined_templates.get("legal_general")
        
        # Check document content for clues
        content = (document.original_text or "").lower()
        if any(term in content for term in ["policy", "procedure", "guideline"]):
            return self._predefined_templates.get("policy_analysis")
        elif any(term in content for term in ["report", "findings", "analysis"]):
            return self._predefined_templates.get("report_analysis")
        
        # Default to general analysis
        return self._predefined_templates.get("general_analysis")
    
    def apply_template(self, document: Document, template: AnalysisTemplate) -> Dict[str, Any]:
        """
        Apply a template to generate analysis prompts.
        
        Args:
            document: Document to analyze
            template: Template to apply
            
        Returns:
            Dictionary of analysis prompts and parameters
        """
        analysis_prompts = {}
        
        # Generate prompts for each analysis section
        for section in template.analysis_sections:
            if section in template.custom_prompts:
                # Use custom prompt
                prompt = template.custom_prompts[section]
            else:
                # Generate default prompt for section
                prompt = self._generate_default_prompt(section, document, template)
            
            # Apply template parameters
            prompt = self._apply_template_parameters(prompt, template.parameters, document)
            analysis_prompts[section] = prompt
        
        return {
            'prompts': analysis_prompts,
            'template_id': template.template_id,
            'template_name': template.name,
            'parameters': template.parameters
        }
    
    def save_template(self, template: AnalysisTemplate) -> str:
        """
        Save a template to storage.
        
        Args:
            template: Template to save
            
        Returns:
            Template ID
        """
        # Would implement actual storage here
        logger.info(f"Saved template: {template.name} ({template.template_id})")
        return template.template_id
    
    def load_template(self, template_id: str) -> Optional[AnalysisTemplate]:
        """
        Load a template by ID.
        
        Args:
            template_id: ID of template to load
            
        Returns:
            AnalysisTemplate or None if not found
        """
        # Check predefined templates first
        for template in self._predefined_templates.values():
            if template.template_id == template_id:
                return template
        
        # Would check stored custom templates here
        logger.warning(f"Template not found: {template_id}")
        return None
    
    def _initialize_predefined_templates(self) -> Dict[str, AnalysisTemplate]:
        """Initialize predefined analysis templates."""
        templates = {}
        
        # Contract Analysis Template
        templates["contract_analysis"] = AnalysisTemplate(
            template_id="contract_analysis_v1",
            name="Contract Analysis",
            description="Comprehensive analysis for contracts and agreements",
            document_types=["contract", "agreement", "service_agreement"],
            analysis_sections=[
                "document_overview",
                "key_findings", 
                "critical_information",
                "risk_assessment",
                "commitment_extraction",
                "deliverable_dates",
                "recommended_actions",
                "executive_recommendation"
            ],
            custom_prompts={
                "risk_assessment": """
                Analyze this contract for potential risks. Focus on:
                1. Financial risks (payment terms, penalties, liability)
                2. Legal risks (compliance, jurisdiction, termination)
                3. Operational risks (performance obligations, dependencies)
                4. Timeline risks (deadlines, milestones, delays)
                
                For each risk identified, provide:
                - Risk description
                - Severity level (High/Medium/Low)
                - Affected parties
                - Mitigation suggestions
                """,
                "commitment_extraction": """
                Extract all commitments and obligations from this contract. For each commitment, identify:
                - What needs to be done
                - Who is responsible (obligated party)
                - Who benefits (beneficiary party)
                - When it needs to be done (deadline)
                - Type of commitment (deliverable, payment, action, etc.)
                """
            },
            parameters={
                "focus_areas": ["risks", "commitments", "dates"],
                "detail_level": "comprehensive",
                "include_recommendations": True
            },
            created_by="system",
            version="1.0",
            is_active=True
        )
        
        # NDA Analysis Template
        templates["nda_analysis"] = AnalysisTemplate(
            template_id="nda_analysis_v1",
            name="NDA Analysis",
            description="Specialized analysis for Non-Disclosure Agreements",
            document_types=["nda", "confidentiality_agreement"],
            analysis_sections=[
                "document_overview",
                "confidentiality_scope",
                "permitted_uses",
                "restrictions",
                "term_duration",
                "risk_assessment"
            ],
            custom_prompts={
                "confidentiality_scope": """
                Analyze the scope of confidential information covered by this NDA:
                - What types of information are considered confidential?
                - Are there any exclusions or exceptions?
                - How is confidential information defined?
                """,
                "permitted_uses": """
                Identify what the receiving party is allowed to do with confidential information:
                - Permitted purposes for use
                - Who can access the information
                - Any restrictions on disclosure within the organization
                """
            },
            parameters={
                "focus_areas": ["confidentiality", "restrictions", "duration"],
                "detail_level": "detailed"
            },
            created_by="system",
            version="1.0",
            is_active=True
        )
        
        # General Legal Analysis Template
        templates["legal_general"] = AnalysisTemplate(
            template_id="legal_general_v1",
            name="General Legal Analysis",
            description="General analysis for legal documents",
            document_types=["legal_document"],
            analysis_sections=[
                "document_overview",
                "key_findings",
                "critical_information",
                "legal_terms",
                "recommended_actions"
            ],
            custom_prompts={},
            parameters={
                "focus_areas": ["legal_terms", "obligations", "rights"],
                "detail_level": "standard"
            },
            created_by="system",
            version="1.0",
            is_active=True
        )
        
        # Policy Analysis Template
        templates["policy_analysis"] = AnalysisTemplate(
            template_id="policy_analysis_v1",
            name="Policy Analysis",
            description="Analysis for policies and procedures",
            document_types=["policy", "procedure", "guideline"],
            analysis_sections=[
                "document_overview",
                "key_requirements",
                "compliance_obligations",
                "implementation_steps",
                "recommended_actions"
            ],
            custom_prompts={
                "compliance_obligations": """
                Identify compliance requirements and obligations in this policy:
                - What must be done to comply?
                - Who is responsible for compliance?
                - What are the consequences of non-compliance?
                """
            },
            parameters={
                "focus_areas": ["requirements", "compliance", "implementation"],
                "detail_level": "standard"
            },
            created_by="system",
            version="1.0",
            is_active=True
        )
        
        # General Analysis Template (fallback)
        templates["general_analysis"] = AnalysisTemplate(
            template_id="general_analysis_v1",
            name="General Analysis",
            description="Standard analysis for any document type",
            document_types=["any"],
            analysis_sections=[
                "document_overview",
                "key_findings",
                "critical_information",
                "recommended_actions"
            ],
            custom_prompts={},
            parameters={
                "focus_areas": ["key_points", "important_information"],
                "detail_level": "standard"
            },
            created_by="system",
            version="1.0",
            is_active=True
        )
        
        return templates
    
    def _generate_default_prompt(self, section: str, document: Document, template: AnalysisTemplate) -> str:
        """Generate a default prompt for an analysis section."""
        prompts = {
            "document_overview": f"""
            Provide a comprehensive overview of this {document.document_type or 'document'}:
            - Document type and purpose
            - Main parties involved (if applicable)
            - Key subject matter
            - Document structure and organization
            """,
            
            "key_findings": """
            Identify and summarize the most important findings in this document:
            - Critical facts and information
            - Important decisions or conclusions
            - Significant data points or metrics
            - Notable patterns or trends
            """,
            
            "critical_information": """
            Extract critical information that requires attention:
            - Urgent matters or deadlines
            - Important warnings or notices
            - Key decisions that need to be made
            - Information that could impact operations or compliance
            """,
            
            "recommended_actions": """
            Based on the document content, recommend specific actions:
            - Immediate actions required
            - Follow-up tasks needed
            - Decisions that should be made
            - Areas requiring further investigation
            """,
            
            "executive_recommendation": """
            Provide an executive-level recommendation based on this document:
            - Overall assessment and recommendation
            - Key risks and opportunities
            - Strategic implications
            - Next steps for leadership consideration
            """
        }
        
        return prompts.get(section, f"Analyze the {section} aspects of this document.")
    
    def _apply_template_parameters(self, prompt: str, parameters: Dict[str, Any], document: Document) -> str:
        """Apply template parameters to customize the prompt."""
        # Replace parameter placeholders in the prompt
        customized_prompt = prompt
        
        # Add document-specific context
        if document.title:
            customized_prompt += f"\n\nDocument Title: {document.title}"
        
        if document.document_type:
            customized_prompt += f"\nDocument Type: {document.document_type}"
        
        # Apply focus areas if specified
        focus_areas = parameters.get("focus_areas", [])
        if focus_areas:
            customized_prompt += f"\n\nFocus particularly on: {', '.join(focus_areas)}"
        
        # Apply detail level
        detail_level = parameters.get("detail_level", "standard")
        if detail_level == "comprehensive":
            customized_prompt += "\n\nProvide comprehensive, detailed analysis with specific examples and citations."
        elif detail_level == "summary":
            customized_prompt += "\n\nProvide a concise summary focusing on the most important points."
        
        return customized_prompt