"""
Request Analyzer for automatic tabular data detection and export triggering.
Analyzes user requests to determine when exports should be generated.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class RequestType(Enum):
    """Types of user requests."""
    EXPORT_REQUEST = "export"
    TABULAR_DATA_REQUEST = "tabular"
    REPORT_REQUEST = "report"
    ANALYSIS_REQUEST = "analysis"
    STANDARD_QA = "qa"
    COMPARISON_REQUEST = "comparison"


@dataclass
class RequestAnalysis:
    """Analysis result of a user request."""
    request_type: RequestType
    should_generate_export: bool
    export_format_preferences: List[str]
    template_type: str
    confidence: float
    detected_keywords: List[str]
    data_structure_hints: Dict[str, Any]


class RequestAnalyzer:
    """
    Analyzes user requests to automatically detect when tabular data exports should be generated.
    Triggers export generation for any user request involving tables, reports, or structured data.
    """
    
    def __init__(self):
        # Keywords that indicate export requests
        self.export_keywords = {
            'direct_export': [
                'export', 'download', 'excel', 'csv', 'spreadsheet', 'table',
                'report', 'generate report', 'create report', 'save as',
                'give me a file', 'provide a file', 'can i download'
            ],
            'tabular_data': [
                'list', 'table', 'breakdown', 'summary table', 'data table',
                'organize', 'structure', 'format', 'tabulate', 'matrix',
                'grid', 'rows and columns', 'spreadsheet format'
            ],
            'analysis_reports': [
                'analysis', 'compare', 'comparison', 'versus', 'vs',
                'analyze', 'assessment', 'evaluation', 'review',
                'risk analysis', 'portfolio analysis', 'summary report'
            ],
            'data_aggregation': [
                'all', 'total', 'count', 'sum', 'average', 'statistics',
                'metrics', 'overview', 'dashboard', 'summary',
                'aggregate', 'compile', 'collect'
            ]
        }
        
        # Format preferences based on keywords
        self.format_indicators = {
            'excel': ['excel', 'xlsx', 'spreadsheet', 'workbook'],
            'csv': ['csv', 'comma separated', 'comma-separated'],
            'json': ['json', 'api format', 'structured data'],
            'pdf': ['pdf', 'document', 'printable']
        }
        
        # Template type indicators
        self.template_indicators = {
            'risk_analysis': [
                'risk', 'risks', 'risk analysis', 'risk assessment',
                'threats', 'vulnerabilities', 'mitigation', 'liability'
            ],
            'document_summary': [
                'summary', 'summarize', 'key points', 'overview',
                'main points', 'highlights', 'abstract'
            ],
            'portfolio_analysis': [
                'portfolio', 'all documents', 'multiple documents',
                'collection', 'entire set', 'all files'
            ],
            'qa_history': [
                'conversation', 'chat history', 'questions asked',
                'previous questions', 'discussion', 'dialogue'
            ],
            'comparative_analysis': [
                'compare', 'comparison', 'versus', 'vs', 'against',
                'differences', 'similarities', 'contrast'
            ]
        }
        
        # Phrases that strongly indicate export needs
        self.strong_export_phrases = [
            r"can you (give me|provide|create|generate) (a|an)? (excel|csv|table|report|file)",
            r"i need (a|an)? (excel|csv|table|report|file)",
            r"export (this|the data|everything) (to|as|in) (excel|csv|table)",
            r"download (this|the data|everything)",
            r"save (this|the data|everything) as",
            r"put (this|the data|everything) in (a|an)? (excel|csv|table|spreadsheet)",
            r"organize (this|the data|everything) in (a|an)? (table|spreadsheet)",
            r"show me (this|the data|everything) in (a|an)? (table|spreadsheet|excel) format"
        ]
        
        # Phrases that indicate tabular data requests
        self.tabular_phrases = [
            r"list (all|the)? (.*)",
            r"show me (all|the)? (.*) in (a|an)? (table|list|format)",
            r"break down (the|all)? (.*)",
            r"organize (the|all)? (.*)",
            r"what are (all|the)? (.*)",
            r"give me (all|the)? (.*) for",
            r"i want to see (all|the)? (.*)"
        ]
    
    def analyze_request(self, user_request: str, context: Dict[str, Any] = None) -> RequestAnalysis:
        """
        Analyze a user request to determine if exports should be generated.
        
        Args:
            user_request: The user's question or request
            context: Additional context about the current session/document
            
        Returns:
            RequestAnalysis with recommendations for export generation
        """
        logger.info(f"Analyzing request: {user_request[:100]}...")
        
        request_lower = user_request.lower()
        
        # Check for strong export indicators
        export_confidence = self._calculate_export_confidence(request_lower)
        
        # Determine request type
        request_type = self._determine_request_type(request_lower)
        
        # Should we generate an export?
        should_export = self._should_generate_export(request_lower, export_confidence, context)
        
        # Determine format preferences
        format_preferences = self._determine_format_preferences(request_lower)
        
        # Determine template type
        template_type = self._determine_template_type(request_lower, context)
        
        # Extract detected keywords
        detected_keywords = self._extract_keywords(request_lower)
        
        # Analyze data structure hints
        data_hints = self._analyze_data_structure_hints(request_lower, context)
        
        analysis = RequestAnalysis(
            request_type=request_type,
            should_generate_export=should_export,
            export_format_preferences=format_preferences,
            template_type=template_type,
            confidence=export_confidence,
            detected_keywords=detected_keywords,
            data_structure_hints=data_hints
        )
        
        logger.info(f"Request analysis complete: {analysis.request_type.value}, export: {should_export}, confidence: {export_confidence:.2f}")
        
        return analysis
    
    def _calculate_export_confidence(self, request_lower: str) -> float:
        """Calculate confidence that this request needs an export."""
        confidence = 0.0
        
        # Check strong export phrases (high confidence)
        for phrase_pattern in self.strong_export_phrases:
            if re.search(phrase_pattern, request_lower):
                confidence = max(confidence, 0.9)
        
        # Check direct export keywords
        for keyword in self.export_keywords['direct_export']:
            if keyword in request_lower:
                confidence = max(confidence, 0.8)
        
        # Check tabular data phrases
        for phrase_pattern in self.tabular_phrases:
            if re.search(phrase_pattern, request_lower):
                confidence = max(confidence, 0.7)
        
        # Check tabular data keywords
        for keyword in self.export_keywords['tabular_data']:
            if keyword in request_lower:
                confidence = max(confidence, 0.6)
        
        # Check analysis keywords
        for keyword in self.export_keywords['analysis_reports']:
            if keyword in request_lower:
                confidence = max(confidence, 0.5)
        
        # Check data aggregation keywords
        for keyword in self.export_keywords['data_aggregation']:
            if keyword in request_lower:
                confidence = max(confidence, 0.4)
        
        return confidence
    
    def _determine_request_type(self, request_lower: str) -> RequestType:
        """Determine the type of request."""
        # Check for direct export requests
        for keyword in self.export_keywords['direct_export']:
            if keyword in request_lower:
                return RequestType.EXPORT_REQUEST
        
        # Check for strong export phrases
        for phrase_pattern in self.strong_export_phrases:
            if re.search(phrase_pattern, request_lower):
                return RequestType.EXPORT_REQUEST
        
        # Check for tabular data requests
        for phrase_pattern in self.tabular_phrases:
            if re.search(phrase_pattern, request_lower):
                return RequestType.TABULAR_DATA_REQUEST
        
        # Check for report requests
        if any(keyword in request_lower for keyword in ['report', 'analysis', 'assessment']):
            return RequestType.REPORT_REQUEST
        
        # Check for comparison requests
        if any(keyword in request_lower for keyword in ['compare', 'comparison', 'versus', 'vs']):
            return RequestType.COMPARISON_REQUEST
        
        # Check for analysis requests
        if any(keyword in request_lower for keyword in self.export_keywords['analysis_reports']):
            return RequestType.ANALYSIS_REQUEST
        
        return RequestType.STANDARD_QA
    
    def _should_generate_export(self, request_lower: str, confidence: float, context: Dict[str, Any] = None) -> bool:
        """Determine if an export should be generated."""
        # High confidence requests always get exports
        if confidence >= 0.7:
            return True
        
        # Medium confidence with supporting context
        if confidence >= 0.5:
            if context and context.get('has_structured_data', False):
                return True
            if any(keyword in request_lower for keyword in ['all', 'list', 'show me']):
                return True
        
        # Low confidence but clear tabular indicators
        if confidence >= 0.3:
            if any(keyword in request_lower for keyword in ['table', 'spreadsheet', 'organize']):
                return True
        
        return False
    
    def _determine_format_preferences(self, request_lower: str) -> List[str]:
        """Determine preferred export formats based on request."""
        preferences = []
        
        # Check for explicit format mentions
        for format_type, keywords in self.format_indicators.items():
            if any(keyword in request_lower for keyword in keywords):
                preferences.append(format_type)
        
        # Default preferences if none specified
        if not preferences:
            if any(keyword in request_lower for keyword in ['analysis', 'report', 'complex']):
                preferences = ['excel', 'csv']
            elif any(keyword in request_lower for keyword in ['simple', 'basic', 'quick']):
                preferences = ['csv', 'excel']
            else:
                preferences = ['excel', 'csv', 'json']
        
        return preferences
    
    def _determine_template_type(self, request_lower: str, context: Dict[str, Any] = None) -> str:
        """Determine the appropriate template type."""
        # Check template indicators
        for template_type, keywords in self.template_indicators.items():
            if any(keyword in request_lower for keyword in keywords):
                return template_type
        
        # Use context to determine template
        if context:
            if context.get('analysis_mode') == 'contract':
                return 'document_summary'
            if context.get('multiple_documents', False):
                return 'portfolio_analysis'
            if context.get('has_qa_history', False):
                return 'qa_history'
        
        # Default template
        return 'generic'
    
    def _extract_keywords(self, request_lower: str) -> List[str]:
        """Extract relevant keywords from the request."""
        keywords = []
        
        for category, keyword_list in self.export_keywords.items():
            for keyword in keyword_list:
                if keyword in request_lower:
                    keywords.append(keyword)
        
        return keywords
    
    def _analyze_data_structure_hints(self, request_lower: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze hints about the expected data structure."""
        hints = {}
        
        # Check for specific data types mentioned
        if 'risk' in request_lower:
            hints['expected_data_types'] = ['risks', 'mitigation_strategies']
        
        if any(word in request_lower for word in ['date', 'deadline', 'timeline']):
            hints['include_dates'] = True
        
        if any(word in request_lower for word in ['party', 'parties', 'stakeholder']):
            hints['include_parties'] = True
        
        if any(word in request_lower for word in ['term', 'definition', 'glossary']):
            hints['include_definitions'] = True
        
        # Check for aggregation hints
        if any(word in request_lower for word in ['total', 'count', 'sum', 'average']):
            hints['needs_aggregation'] = True
        
        # Check for comparison hints
        if any(word in request_lower for word in ['compare', 'versus', 'difference']):
            hints['needs_comparison'] = True
        
        # Add context hints
        if context:
            hints.update(context.get('data_hints', {}))
        
        return hints
    
    def is_export_request(self, user_request: str) -> bool:
        """Quick check if a request is likely an export request."""
        analysis = self.analyze_request(user_request)
        return analysis.should_generate_export
    
    def get_export_recommendations(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get detailed export recommendations for a request."""
        analysis = self.analyze_request(user_request, context)
        
        return {
            'should_export': analysis.should_generate_export,
            'confidence': analysis.confidence,
            'recommended_formats': analysis.export_format_preferences,
            'template_type': analysis.template_type,
            'request_type': analysis.request_type.value,
            'detected_keywords': analysis.detected_keywords,
            'data_hints': analysis.data_structure_hints,
            'explanation': self._generate_explanation(analysis)
        }
    
    def _generate_explanation(self, analysis: RequestAnalysis) -> str:
        """Generate explanation for the analysis decision."""
        if analysis.should_generate_export:
            if analysis.confidence >= 0.8:
                return f"Strong export request detected (confidence: {analysis.confidence:.1%}). User explicitly requested downloadable data."
            elif analysis.confidence >= 0.6:
                return f"Tabular data request detected (confidence: {analysis.confidence:.1%}). User appears to want structured information."
            else:
                return f"Potential export need detected (confidence: {analysis.confidence:.1%}). Request suggests structured data would be helpful."
        else:
            return f"Standard Q&A request (confidence: {analysis.confidence:.1%}). No export generation needed."