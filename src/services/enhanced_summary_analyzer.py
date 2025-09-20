"""Enhanced Summary Analyzer with risk assessment and comprehensive analysis capabilities."""

import uuid
import re
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import requests

from src.models.document import (
    Document, RiskAssessment, Commitment, DeliverableDate, 
    AnalysisTemplate, ComprehensiveAnalysis
)
from src.services.template_engine import TemplateEngine
from src.storage.document_storage import DocumentStorage
from src.utils.logging_config import get_logger
from src.utils.error_handling import (
    EnhancedAnalysisError, TemplateError, APIError, handle_errors, 
    graceful_degradation, ErrorType
)

logger = get_logger(__name__)


class EnhancedSummaryAnalyzer:
    """Enhanced analyzer for comprehensive document analysis with risk assessment."""
    
    def __init__(self, storage: DocumentStorage, api_key: str):
        self.storage = storage
        self.api_key = api_key
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        self.template_engine = TemplateEngine(storage)
    
    @handle_errors(ErrorType.ENHANCED_ANALYSIS_ERROR)
    def analyze_document_comprehensive(self, document: Document, template: Optional[AnalysisTemplate] = None) -> ComprehensiveAnalysis:
        """
        Perform comprehensive analysis of a document.
        
        Args:
            document: Document to analyze
            template: Optional analysis template to use
            
        Returns:
            ComprehensiveAnalysis containing all analysis results
        """
        analysis_id = str(uuid.uuid4())
        
        # Use provided template or recommend one
        if not template:
            template = self.template_engine.recommend_template(document)
        
        logger.info(f"Starting comprehensive analysis for document {document.id} using template {template.name if template else 'None'}")
        
        try:
            # Generate enhanced summary sections with fallback handling
            document_overview = self._safe_generate_section(
                lambda: self._generate_document_overview(document, template),
                "Failed to generate document overview"
            )
            
            key_findings = self._safe_generate_section(
                lambda: self._extract_key_findings(document, template),
                []
            )
            
            critical_information = self._safe_generate_section(
                lambda: self._extract_critical_information(document, template),
                []
            )
            
            recommended_actions = self._safe_generate_section(
                lambda: self._generate_recommended_actions(document, template),
                []
            )
            
            executive_recommendation = self._safe_generate_section(
                lambda: self._generate_executive_recommendation(document, template),
                "Analysis completed with limited information due to processing constraints."
            )
            
            key_legal_terms = self._safe_generate_section(
                lambda: self._extract_key_legal_terms(document),
                []
            )
            
            # Perform specialized analysis with error handling
            risks = self._safe_generate_section(
                lambda: self.identify_risks(document),
                []
            )
            
            commitments = self._safe_generate_section(
                lambda: self.extract_commitments(document),
                []
            )
            
            deliverable_dates = self._safe_generate_section(
                lambda: self.find_deliverable_dates(document),
                []
            )
            
        except Exception as e:
            logger.error(f"Critical error in comprehensive analysis: {str(e)}")
            raise EnhancedAnalysisError(
                f"Failed to complete comprehensive analysis for document {document.id}",
                {"document_id": document.id, "template": template.name if template else None},
                e
            )
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(
            document, risks, commitments, deliverable_dates
        )
        
        analysis = ComprehensiveAnalysis(
            document_id=document.id,
            analysis_id=analysis_id,
            document_overview=document_overview,
            key_findings=key_findings,
            critical_information=critical_information,
            recommended_actions=recommended_actions,
            executive_recommendation=executive_recommendation,
            key_legal_terms=key_legal_terms,
            risks=risks,
            commitments=commitments,
            deliverable_dates=deliverable_dates,
            template_used=template.template_id if template else None,
            confidence_score=confidence_score
        )
        
        logger.info(f"Completed comprehensive analysis {analysis_id} with confidence {confidence_score:.2f}")
        return analysis
    
    def _safe_generate_section(self, operation: Callable, fallback_result: Any) -> Any:
        """Safely execute a section generation operation with fallback."""
        try:
            return operation()
        except Exception as e:
            logger.warning(f"Section generation failed, using fallback: {str(e)}")
            return fallback_result
    
    @handle_errors(ErrorType.ENHANCED_ANALYSIS_ERROR)
    def identify_risks(self, document: Document) -> List[RiskAssessment]:
        """
        Identify and assess risks in the document.
        
        Args:
            document: Document to analyze
            
        Returns:
            List of identified risks
        """
        prompt = f"""
        Analyze the following document for potential risks. Identify risks in these categories:
        1. Legal risks (compliance, liability, jurisdiction issues)
        2. Financial risks (payment terms, penalties, cost overruns)
        3. Operational risks (performance obligations, dependencies, resource constraints)
        4. Timeline risks (deadlines, milestones, scheduling conflicts)
        5. Reputational risks (public relations, brand impact)
        
        For each risk, provide:
        - A clear description of the risk
        - Severity level (High, Medium, Low)
        - Category (Legal, Financial, Operational, Timeline, Reputational)
        - Affected parties
        - Specific mitigation suggestions
        - The source text that indicates this risk
        
        Document Title: {document.title}
        Document Type: {document.document_type or 'Unknown'}
        
        Document Content:
        {document.original_text[:4000] if document.original_text else 'No content available'}
        
        Return the analysis in JSON format with this structure:
        {{
            "risks": [
                {{
                    "description": "Risk description",
                    "severity": "High|Medium|Low",
                    "category": "Legal|Financial|Operational|Timeline|Reputational",
                    "affected_parties": ["Party 1", "Party 2"],
                    "mitigation_suggestions": ["Suggestion 1", "Suggestion 2"],
                    "source_text": "Relevant text from document",
                    "confidence": 0.85
                }}
            ]
        }}
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=2000)
            risks_data = self._parse_json_response(response)
            
            risks = []
            for i, risk_data in enumerate(risks_data.get('risks', [])):
                risk = RiskAssessment(
                    risk_id=f"{document.id}_risk_{i+1}",
                    description=risk_data.get('description', ''),
                    severity=risk_data.get('severity', 'Medium'),
                    category=risk_data.get('category', 'Operational'),
                    affected_parties=risk_data.get('affected_parties', []),
                    mitigation_suggestions=risk_data.get('mitigation_suggestions', []),
                    source_text=risk_data.get('source_text', ''),
                    confidence=risk_data.get('confidence', 0.7)
                )
                risks.append(risk)
            
            logger.info(f"Identified {len(risks)} risks in document {document.id}")
            return risks
            
        except Exception as e:
            logger.error(f"Error identifying risks: {e}")
            raise EnhancedAnalysisError(
                f"Failed to identify risks in document {document.id}",
                {"document_id": document.id, "operation": "risk_identification"},
                e
            )
    
    @handle_errors(ErrorType.ENHANCED_ANALYSIS_ERROR)
    def extract_commitments(self, document: Document) -> List[Commitment]:
        """
        Extract commitments and obligations from the document.
        
        Args:
            document: Document to analyze
            
        Returns:
            List of identified commitments
        """
        prompt = f"""
        Extract all commitments, obligations, and promises from this document. Look for:
        1. Deliverables that must be provided
        2. Actions that must be taken
        3. Payments that must be made
        4. Services that must be performed
        5. Compliance requirements that must be met
        
        For each commitment, identify:
        - What needs to be done (description)
        - Who is responsible (obligated party)
        - Who benefits (beneficiary party)
        - When it needs to be done (deadline, if specified)
        - Type of commitment (Deliverable, Payment, Action, Service, Compliance)
        - Current status (Active, if determinable)
        - The source text
        
        Document Title: {document.title}
        Document Content:
        {document.original_text[:4000] if document.original_text else 'No content available'}
        
        Return in JSON format:
        {{
            "commitments": [
                {{
                    "description": "What needs to be done",
                    "obligated_party": "Who must do it",
                    "beneficiary_party": "Who benefits",
                    "deadline": "YYYY-MM-DD or null",
                    "commitment_type": "Deliverable|Payment|Action|Service|Compliance",
                    "status": "Active",
                    "source_text": "Relevant text from document"
                }}
            ]
        }}
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=2000)
            commitments_data = self._parse_json_response(response)
            
            commitments = []
            for i, commitment_data in enumerate(commitments_data.get('commitments', [])):
                # Parse deadline if provided
                deadline = None
                deadline_str = commitment_data.get('deadline')
                if deadline_str and deadline_str != 'null':
                    try:
                        deadline = datetime.fromisoformat(deadline_str)
                    except ValueError:
                        logger.warning(f"Could not parse deadline: {deadline_str}")
                
                commitment = Commitment(
                    commitment_id=f"{document.id}_commitment_{i+1}",
                    description=commitment_data.get('description', ''),
                    obligated_party=commitment_data.get('obligated_party', ''),
                    beneficiary_party=commitment_data.get('beneficiary_party', ''),
                    deadline=deadline,
                    status=commitment_data.get('status', 'Active'),
                    source_text=commitment_data.get('source_text', ''),
                    commitment_type=commitment_data.get('commitment_type', 'Action')
                )
                commitments.append(commitment)
            
            logger.info(f"Extracted {len(commitments)} commitments from document {document.id}")
            return commitments
            
        except Exception as e:
            logger.error(f"Error extracting commitments: {e}")
            raise EnhancedAnalysisError(
                f"Failed to extract commitments from document {document.id}",
                {"document_id": document.id, "operation": "commitment_extraction"},
                e
            )
    
    @handle_errors(ErrorType.ENHANCED_ANALYSIS_ERROR)
    def find_deliverable_dates(self, document: Document) -> List[DeliverableDate]:
        """
        Find and extract deliverable dates from the document.
        
        Args:
            document: Document to analyze
            
        Returns:
            List of deliverable dates
        """
        prompt = f"""
        Find all important dates, deadlines, and milestones in this document. Look for:
        1. Delivery deadlines
        2. Payment due dates
        3. Milestone dates
        4. Compliance deadlines
        5. Review dates
        6. Expiration dates
        7. Renewal dates
        
        For each date, identify:
        - The specific date
        - What is due or happens on that date
        - Who is responsible
        - Type of deliverable/event
        - Current status (if determinable)
        - The source text
        
        Document Content:
        {document.original_text[:4000] if document.original_text else 'No content available'}
        
        Return in JSON format:
        {{
            "deliverable_dates": [
                {{
                    "date": "YYYY-MM-DD",
                    "description": "What happens on this date",
                    "responsible_party": "Who is responsible",
                    "deliverable_type": "Delivery|Payment|Milestone|Compliance|Review|Expiration|Renewal",
                    "status": "Pending|Active|Completed",
                    "source_text": "Relevant text from document"
                }}
            ]
        }}
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=1500)
            dates_data = self._parse_json_response(response)
            
            deliverable_dates = []
            for date_data in dates_data.get('deliverable_dates', []):
                try:
                    date = datetime.fromisoformat(date_data.get('date', ''))
                    
                    deliverable_date = DeliverableDate(
                        date=date,
                        description=date_data.get('description', ''),
                        responsible_party=date_data.get('responsible_party', ''),
                        deliverable_type=date_data.get('deliverable_type', 'Milestone'),
                        status=date_data.get('status', 'Pending'),
                        source_text=date_data.get('source_text', '')
                    )
                    deliverable_dates.append(deliverable_date)
                    
                except ValueError as e:
                    logger.warning(f"Could not parse date: {date_data.get('date', '')}")
            
            # Sort by date
            deliverable_dates.sort(key=lambda x: x.date)
            
            logger.info(f"Found {len(deliverable_dates)} deliverable dates in document {document.id}")
            return deliverable_dates
            
        except Exception as e:
            logger.error(f"Error finding deliverable dates: {e}")
            raise EnhancedAnalysisError(
                f"Failed to find deliverable dates in document {document.id}",
                {"document_id": document.id, "operation": "date_extraction"},
                e
            )
    
    def apply_custom_template(self, document: Document, template: AnalysisTemplate) -> Dict[str, Any]:
        """
        Apply a custom template to analyze the document.
        
        Args:
            document: Document to analyze
            template: Custom template to apply
            
        Returns:
            Dictionary containing template analysis results
        """
        template_application = self.template_engine.apply_template(document, template)
        results = {}
        
        for section, prompt in template_application['prompts'].items():
            try:
                full_prompt = f"""
                {prompt}
                
                Document Title: {document.title}
                Document Content:
                {document.original_text[:3000] if document.original_text else 'No content available'}
                """
                
                response = self._call_gemini_api(full_prompt, max_tokens=1000)
                results[section] = response.strip()
                
            except Exception as e:
                logger.error(f"Error analyzing section {section}: {e}")
                results[section] = f"Error analyzing {section}: {str(e)}"
        
        return {
            'template_id': template.template_id,
            'template_name': template.name,
            'results': results,
            'parameters': template_application['parameters']
        }
    
    def generate_enhanced_summary(self, document: Document) -> Dict[str, Any]:
        """
        Generate an enhanced summary with all analysis components.
        
        Args:
            document: Document to analyze
            
        Returns:
            Dictionary containing enhanced summary sections
        """
        analysis = self.analyze_document_comprehensive(document)
        
        return {
            'document_overview': analysis.document_overview,
            'key_findings': analysis.key_findings,
            'critical_information': analysis.critical_information,
            'recommended_actions': analysis.recommended_actions,
            'executive_recommendation': analysis.executive_recommendation,
            'key_legal_terms': analysis.key_legal_terms,
            'risks_summary': self._summarize_risks(analysis.risks),
            'commitments_summary': self._summarize_commitments(analysis.commitments),
            'dates_summary': self._summarize_dates(analysis.deliverable_dates),
            'confidence_score': analysis.confidence_score
        }
    
    def _generate_document_overview(self, document: Document, template: Optional[AnalysisTemplate]) -> str:
        """Generate document overview section."""
        prompt = f"""
        Provide a comprehensive overview of this document:
        - Document type and purpose
        - Main parties involved (if applicable)
        - Key subject matter
        - Document structure and scope
        - Overall context and significance
        
        Document Title: {document.title}
        Document Type: {document.document_type or 'Unknown'}
        
        Document Content:
        {document.original_text[:2000] if document.original_text else 'No content available'}
        """
        
        try:
            return self._call_gemini_api(prompt, max_tokens=500).strip()
        except Exception as e:
            logger.error(f"Error generating document overview: {e}")
            return "Error generating document overview."
    
    def _extract_key_findings(self, document: Document, template: Optional[AnalysisTemplate]) -> List[str]:
        """Extract key findings from the document."""
        prompt = f"""
        Identify the most important findings in this document. Return as a JSON array of strings.
        Focus on:
        - Critical facts and information
        - Important decisions or conclusions
        - Significant data points or metrics
        - Notable patterns or trends
        
        Document Content:
        {document.original_text[:3000] if document.original_text else 'No content available'}
        
        Return format: {{"findings": ["Finding 1", "Finding 2", ...]}}
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=800)
            data = self._parse_json_response(response)
            return data.get('findings', [])
        except Exception as e:
            logger.error(f"Error extracting key findings: {e}")
            return []
    
    def _extract_critical_information(self, document: Document, template: Optional[AnalysisTemplate]) -> List[str]:
        """Extract critical information that requires attention."""
        prompt = f"""
        Extract critical information that requires immediate attention. Return as JSON array.
        Look for:
        - Urgent matters or deadlines
        - Important warnings or notices
        - Key decisions that need to be made
        - Information that could impact operations or compliance
        
        Document Content:
        {document.original_text[:3000] if document.original_text else 'No content available'}
        
        Return format: {{"critical_info": ["Item 1", "Item 2", ...]}}
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=800)
            data = self._parse_json_response(response)
            return data.get('critical_info', [])
        except Exception as e:
            logger.error(f"Error extracting critical information: {e}")
            return []
    
    def _generate_recommended_actions(self, document: Document, template: Optional[AnalysisTemplate]) -> List[str]:
        """Generate recommended actions based on document analysis."""
        prompt = f"""
        Based on this document, recommend specific actions. Return as JSON array.
        Include:
        - Immediate actions required
        - Follow-up tasks needed
        - Decisions that should be made
        - Areas requiring further investigation
        
        Document Content:
        {document.original_text[:3000] if document.original_text else 'No content available'}
        
        Return format: {{"actions": ["Action 1", "Action 2", ...]}}
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=800)
            data = self._parse_json_response(response)
            return data.get('actions', [])
        except Exception as e:
            logger.error(f"Error generating recommended actions: {e}")
            return []
    
    def _generate_executive_recommendation(self, document: Document, template: Optional[AnalysisTemplate]) -> str:
        """Generate executive-level recommendation."""
        prompt = f"""
        Provide an executive-level recommendation based on this document:
        - Overall assessment and recommendation
        - Key risks and opportunities
        - Strategic implications
        - Next steps for leadership consideration
        
        Document Title: {document.title}
        Document Content:
        {document.original_text[:2000] if document.original_text else 'No content available'}
        """
        
        try:
            return self._call_gemini_api(prompt, max_tokens=500).strip()
        except Exception as e:
            logger.error(f"Error generating executive recommendation: {e}")
            return "Error generating executive recommendation."
    
    def _extract_key_legal_terms(self, document: Document) -> List[str]:
        """Extract key legal terms from the document."""
        if not document.is_legal_document:
            return []
        
        prompt = f"""
        Extract key legal terms and concepts from this legal document. Return as JSON array.
        Look for:
        - Legal terminology and definitions
        - Important clauses and provisions
        - Rights and obligations
        - Legal concepts and principles
        
        Document Content:
        {document.original_text[:3000] if document.original_text else 'No content available'}
        
        Return format: {{"legal_terms": ["Term 1", "Term 2", ...]}}
        """
        
        try:
            response = self._call_gemini_api(prompt, max_tokens=600)
            data = self._parse_json_response(response)
            return data.get('legal_terms', [])
        except Exception as e:
            logger.error(f"Error extracting legal terms: {e}")
            return []
    
    def _calculate_confidence_score(self, document: Document, risks: List[RiskAssessment], 
                                  commitments: List[Commitment], dates: List[DeliverableDate]) -> float:
        """Calculate overall confidence score for the analysis."""
        base_score = 0.7
        
        # Adjust based on document completeness
        if document.original_text and len(document.original_text) > 100:
            base_score += 0.1
        
        # Adjust based on analysis completeness
        if risks:
            base_score += 0.05
        if commitments:
            base_score += 0.05
        if dates:
            base_score += 0.05
        
        # Adjust based on document type
        if document.is_legal_document:
            base_score += 0.05
        
        return min(base_score, 0.95)  # Cap at 95%
    
    def _summarize_risks(self, risks: List[RiskAssessment]) -> Dict[str, Any]:
        """Summarize risks for display."""
        if not risks:
            return {'total': 0, 'by_severity': {}, 'top_risks': []}
        
        by_severity = {'High': 0, 'Medium': 0, 'Low': 0}
        for risk in risks:
            by_severity[risk.severity] = by_severity.get(risk.severity, 0) + 1
        
        top_risks = sorted(risks, key=lambda r: {'High': 3, 'Medium': 2, 'Low': 1}[r.severity], reverse=True)[:3]
        
        return {
            'total': len(risks),
            'by_severity': by_severity,
            'top_risks': [{'description': r.description, 'severity': r.severity} for r in top_risks]
        }
    
    def _summarize_commitments(self, commitments: List[Commitment]) -> Dict[str, Any]:
        """Summarize commitments for display."""
        if not commitments:
            return {'total': 0, 'by_type': {}, 'upcoming': []}
        
        by_type = {}
        upcoming = []
        
        for commitment in commitments:
            by_type[commitment.commitment_type] = by_type.get(commitment.commitment_type, 0) + 1
            if commitment.deadline and commitment.deadline > datetime.now():
                upcoming.append(commitment)
        
        upcoming.sort(key=lambda c: c.deadline or datetime.max)
        
        return {
            'total': len(commitments),
            'by_type': by_type,
            'upcoming': [{'description': c.description, 'deadline': c.deadline.isoformat() if c.deadline else None} 
                        for c in upcoming[:5]]
        }
    
    def _summarize_dates(self, dates: List[DeliverableDate]) -> Dict[str, Any]:
        """Summarize deliverable dates for display."""
        if not dates:
            return {'total': 0, 'upcoming': [], 'by_type': {}}
        
        upcoming = [d for d in dates if d.date > datetime.now()]
        upcoming.sort(key=lambda d: d.date)
        
        by_type = {}
        for date in dates:
            by_type[date.deliverable_type] = by_type.get(date.deliverable_type, 0) + 1
        
        return {
            'total': len(dates),
            'upcoming': [{'description': d.description, 'date': d.date.isoformat(), 'type': d.deliverable_type} 
                        for d in upcoming[:5]],
            'by_type': by_type
        }
    
    def _call_gemini_api(self, prompt: str, max_tokens: int = 1000) -> str:
        """Make API call to Gemini."""
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.3
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"Gemini API error: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response format: {e}")
            raise Exception(f"Unexpected API response format: {str(e)}")
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from API, handling potential formatting issues."""
        try:
            # Try to parse as-is first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try to find JSON-like content
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            logger.warning(f"Could not parse JSON response: {response[:200]}...")
            return {}