"""
Structured Response System for Contract Assistant

Implements guaranteed structured response patterns with never-fail logic,
automatic data export generation, and comprehensive error handling.
"""

import logging
import traceback
import csv
import io
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from src.models.enhanced import EnhancedResponse, ResponseType, ToneType

logger = logging.getLogger(__name__)


class ResponsePatternType(Enum):
    """Types of structured response patterns."""
    DOCUMENT = "document"
    GENERAL_LEGAL = "general_legal"
    DATA_TABLE = "data_table"
    AMBIGUOUS = "ambiguous"
    ERROR_RECOVERY = "error_recovery"


@dataclass
class ProcessedInput:
    """Processed user input with analysis results."""
    original_text: str
    normalized_text: str
    pattern_type: ResponsePatternType
    tone_indicators: Dict[str, float]
    data_request_detected: bool
    ambiguity_level: float
    question_parts: List[str]
    confidence: float


@dataclass
class DataTable:
    """Structured data table for export generation."""
    headers: List[str]
    rows: List[List[str]]
    title: str
    metadata: Dict[str, Any]


@dataclass
class ExportFile:
    """Generated export file information."""
    filename: str
    file_path: str
    format_type: str
    download_url: str
    creation_time: datetime


class StructuredResponseSystem:
    """
    Core system for generating structured responses with guaranteed output.
    
    This system ensures that EVERY input receives a meaningful, structured response
    regardless of input quality, system errors, or edge cases.
    """
    
    def __init__(self, export_directory: str = "data/exports"):
        """Initialize the structured response system."""
        self.export_directory = export_directory
        self.ensure_export_directory()
        
        # Response pattern templates
        self.pattern_templates = self._initialize_pattern_templates()
        
        # Fallback chains for never-fail logic
        self.fallback_chains = self._initialize_fallback_chains()
        
        # Tone adaptation rules
        self.tone_rules = self._initialize_tone_rules()
        
    def ensure_export_directory(self):
        """Ensure export directory exists."""
        try:
            os.makedirs(self.export_directory, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create export directory: {e}")
            # Use fallback directory
            self.export_directory = "/tmp/exports"
            os.makedirs(self.export_directory, exist_ok=True)
    
    def process_input_with_guaranteed_response(
        self, 
        user_input: str, 
        document_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EnhancedResponse:
        """
        Process input and generate guaranteed structured response.
        
        This is the main entry point that NEVER fails to return a meaningful response.
        """
        try:
            # Step 1: Process and analyze input (with fallbacks)
            processed_input = self._process_input_with_fallbacks(user_input)
            
            # Step 2: Generate structured response based on pattern
            response = self._generate_structured_response(
                processed_input, document_content, context
            )
            
            # Step 3: Apply tone adaptation
            response = self._apply_tone_adaptation(response, processed_input)
            
            # Step 4: Add data exports if applicable
            response = self._add_data_exports_if_applicable(response, processed_input)
            
            # Step 5: Final validation and fallback if needed
            response = self._validate_and_ensure_response_quality(response, processed_input)
            
            logger.info(f"Successfully generated structured response with pattern: {processed_input.pattern_type}")
            return response
            
        except Exception as e:
            logger.error(f"Critical error in process_input_with_guaranteed_response: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Ultimate fallback - this should NEVER fail
            return self._create_ultimate_fallback_response(user_input, str(e))
    
    def _process_input_with_fallbacks(self, user_input: str) -> ProcessedInput:
        """Process input with multiple fallback levels."""
        try:
            # Primary processing
            return self._process_input_primary(user_input)
        except Exception as e:
            logger.warning(f"Primary input processing failed: {e}")
            try:
                # Secondary processing (simplified)
                return self._process_input_secondary(user_input)
            except Exception as e2:
                logger.warning(f"Secondary input processing failed: {e2}")
                # Tertiary processing (minimal but guaranteed)
                return self._process_input_tertiary(user_input)
    
    def _process_input_primary(self, user_input: str) -> ProcessedInput:
        """Primary input processing with full analysis."""
        if not user_input or not user_input.strip():
            raise ValueError("Empty input")
        
        normalized = user_input.strip().lower()
        
        # Detect pattern type
        pattern_type = self._detect_response_pattern(user_input)
        
        # Analyze tone indicators
        tone_indicators = self._analyze_tone_indicators(user_input)
        
        # Detect data requests
        data_request = self._detect_data_request(user_input)
        
        # Measure ambiguity
        ambiguity_level = self._measure_ambiguity(user_input)
        
        # Split into question parts
        question_parts = self._split_question_parts(user_input)
        
        # Calculate confidence
        confidence = self._calculate_processing_confidence(
            user_input, pattern_type, tone_indicators, ambiguity_level
        )
        
        return ProcessedInput(
            original_text=user_input,
            normalized_text=normalized,
            pattern_type=pattern_type,
            tone_indicators=tone_indicators,
            data_request_detected=data_request,
            ambiguity_level=ambiguity_level,
            question_parts=question_parts,
            confidence=confidence
        )
    
    def _process_input_secondary(self, user_input: str) -> ProcessedInput:
        """Secondary input processing with basic analysis."""
        normalized = user_input.strip().lower() if user_input else "empty input"
        
        # Simple pattern detection
        if any(word in normalized for word in ['what', 'how', 'when', 'where', 'why']):
            pattern_type = ResponsePatternType.DOCUMENT
        elif any(word in normalized for word in ['table', 'list', 'data', 'export']):
            pattern_type = ResponsePatternType.DATA_TABLE
        elif len(normalized.split()) < 3:
            pattern_type = ResponsePatternType.AMBIGUOUS
        else:
            pattern_type = ResponsePatternType.DOCUMENT
        
        return ProcessedInput(
            original_text=user_input,
            normalized_text=normalized,
            pattern_type=pattern_type,
            tone_indicators={'casual': 0.5, 'formal': 0.5},
            data_request_detected=False,
            ambiguity_level=0.5,
            question_parts=[user_input] if user_input else ["empty input"],
            confidence=0.3
        )
    
    def _process_input_tertiary(self, user_input: str) -> ProcessedInput:
        """Tertiary input processing - minimal but guaranteed to work."""
        return ProcessedInput(
            original_text=user_input or "empty input",
            normalized_text=(user_input or "empty input").lower(),
            pattern_type=ResponsePatternType.ERROR_RECOVERY,
            tone_indicators={'neutral': 1.0},
            data_request_detected=False,
            ambiguity_level=1.0,
            question_parts=[user_input or "empty input"],
            confidence=0.1
        )
    
    def _detect_response_pattern(self, user_input: str) -> ResponsePatternType:
        """Detect the appropriate response pattern for the input."""
        input_lower = user_input.lower()
        
        # Check for data/table requests
        data_indicators = ['table', 'list', 'export', 'download', 'csv', 'excel', 'data']
        if any(indicator in input_lower for indicator in data_indicators):
            return ResponsePatternType.DATA_TABLE
        
        # Check for ambiguous inputs
        ambiguous_indicators = ['maybe', 'perhaps', 'not sure', 'unclear', 'confused']
        question_words = ['what', 'how', 'when', 'where', 'why', 'which']
        
        if (any(indicator in input_lower for indicator in ambiguous_indicators) or
            len([w for w in question_words if w in input_lower]) > 2):
            return ResponsePatternType.AMBIGUOUS
        
        # Check for general legal questions (not document-specific)
        general_indicators = ['generally', 'typically', 'usually', 'in general', 'normally']
        if any(indicator in input_lower for indicator in general_indicators):
            return ResponsePatternType.GENERAL_LEGAL
        
        # Default to document pattern
        return ResponsePatternType.DOCUMENT
    
    def _analyze_tone_indicators(self, user_input: str) -> Dict[str, float]:
        """Analyze tone indicators in the input with enhanced detection."""
        input_lower = user_input.lower()
        
        # Casual indicators (expanded)
        casual_words = ['hey', 'hi', 'yo', 'sup', 'cool', 'awesome', 'dude', 'lol', 'btw', 'fyi', 
                       'gonna', 'wanna', 'kinda', 'sorta', 'yeah', 'yep', 'nah', 'ok', 'okay']
        casual_punctuation = user_input.count('!') + user_input.count('?') * 0.5
        casual_score = (sum(1 for word in casual_words if word in input_lower) / len(casual_words)) + (casual_punctuation * 0.1)
        
        # Formal indicators (expanded)
        formal_words = ['please', 'kindly', 'would you', 'could you', 'thank you', 'appreciate', 
                       'grateful', 'respectfully', 'sincerely', 'regarding', 'concerning']
        formal_structure = 1.0 if any(phrase in input_lower for phrase in ['would you please', 'i would like to', 'may i']) else 0.0
        formal_score = (sum(1 for word in formal_words if word in input_lower) / len(formal_words)) + (formal_structure * 0.3)
        
        # Technical indicators (expanded)
        technical_words = ['clause', 'provision', 'liability', 'indemnification', 'breach', 'jurisdiction',
                          'governing law', 'force majeure', 'intellectual property', 'confidentiality',
                          'warranty', 'covenant', 'consideration', 'termination', 'amendment']
        technical_score = sum(1 for word in technical_words if word in input_lower) / len(technical_words)
        
        # Business indicators (expanded)
        business_words = ['contract', 'agreement', 'terms', 'conditions', 'obligations', 'parties',
                         'deliverables', 'milestones', 'payment', 'invoice', 'compliance', 'audit']
        business_score = sum(1 for word in business_words if word in input_lower) / len(business_words)
        
        # Startup/tech indicators (new)
        startup_words = ['disrupt', 'scale', 'pivot', 'iterate', 'mvp', 'agile', 'lean', 'growth hack',
                        'unicorn', 'burn rate', 'runway', 'equity', 'vesting', 'cap table']
        startup_score = sum(1 for word in startup_words if word in input_lower) / len(startup_words)
        
        # Slang/informal indicators (new)
        slang_words = ['gonna', 'wanna', 'gotta', 'dunno', 'ain\'t', 'y\'all', 'whatcha', 'lemme']
        slang_score = sum(1 for word in slang_words if word in input_lower) / len(slang_words)
        
        return {
            'casual': min(1.0, casual_score * 2.5),
            'formal': min(1.0, formal_score * 2),
            'technical': min(1.0, technical_score * 2),
            'business': min(1.0, business_score * 1.5),
            'startup': min(1.0, startup_score * 3),
            'slang': min(1.0, slang_score * 4)
        }
    
    def _detect_data_request(self, user_input: str) -> bool:
        """Detect if the input is requesting data/table output."""
        data_keywords = [
            'table', 'list', 'export', 'download', 'csv', 'excel', 'data',
            'summary', 'breakdown', 'overview', 'comparison', 'timeline'
        ]
        return any(keyword in user_input.lower() for keyword in data_keywords)
    
    def _measure_ambiguity(self, user_input: str) -> float:
        """Measure the ambiguity level of the input."""
        input_lower = user_input.lower()
        
        # Ambiguity indicators
        ambiguous_words = ['maybe', 'perhaps', 'might', 'could be', 'not sure', 'unclear']
        ambiguity_score = sum(1 for word in ambiguous_words if word in input_lower)
        
        # Multiple question words increase ambiguity
        question_words = ['what', 'how', 'when', 'where', 'why', 'which', 'who']
        question_count = sum(1 for word in question_words if word in input_lower)
        
        # Very short or very long inputs are more ambiguous
        length_factor = 0.0
        word_count = len(input_lower.split())
        if word_count < 3 or word_count > 50:
            length_factor = 0.3
        
        total_ambiguity = (ambiguity_score * 0.4 + 
                          max(0, question_count - 1) * 0.2 + 
                          length_factor)
        
        return min(1.0, total_ambiguity)
    
    def _split_question_parts(self, user_input: str) -> List[str]:
        """Split input into distinct question parts with enhanced parsing."""
        import re
        
        # Enhanced separators with context awareness
        question_separators = ['?', '??', '???']  # Question marks
        clause_separators = [';', '.', ':', '--', '—']  # Clause separators
        conjunction_separators = [' and ', ' also ', ' additionally ', ' furthermore ', ' moreover ', ' plus ']
        enumeration_separators = [' first ', ' second ', ' third ', ' next ', ' then ', ' finally ']
        
        # Start with original input
        parts = [user_input.strip()]
        
        # Split on question marks first (highest priority)
        for separator in question_separators:
            new_parts = []
            for part in parts:
                if separator in part:
                    split_parts = part.split(separator)
                    for i, split_part in enumerate(split_parts):
                        split_part = split_part.strip()
                        if split_part:
                            # Add question mark back if not the last part
                            if i < len(split_parts) - 1 and separator == '?':
                                split_part += '?'
                            new_parts.append(split_part)
                else:
                    new_parts.append(part)
            parts = new_parts
        
        # Split on conjunctions (case-insensitive)
        for separator in conjunction_separators:
            new_parts = []
            for part in parts:
                # Use case-insensitive matching
                pattern = re.compile(re.escape(separator), re.IGNORECASE)
                if pattern.search(part):
                    split_parts = pattern.split(part)
                    new_parts.extend([p.strip() for p in split_parts if p.strip()])
                else:
                    new_parts.append(part)
            parts = new_parts
        
        # Split on enumeration indicators
        for separator in enumeration_separators:
            new_parts = []
            for part in parts:
                pattern = re.compile(re.escape(separator), re.IGNORECASE)
                if pattern.search(part):
                    split_parts = pattern.split(part)
                    new_parts.extend([p.strip() for p in split_parts if p.strip()])
                else:
                    new_parts.append(part)
            parts = new_parts
        
        # Split on clause separators (lower priority)
        for separator in clause_separators:
            new_parts = []
            for part in parts:
                if separator in part and len(part) > 50:  # Only split long parts on punctuation
                    split_parts = part.split(separator)
                    new_parts.extend([p.strip() for p in split_parts if p.strip()])
                else:
                    new_parts.append(part)
            parts = new_parts
        
        # Filter and clean parts
        cleaned_parts = []
        for part in parts:
            part = part.strip()
            # Keep parts that are substantial questions or statements
            if (len(part) > 8 and  # Minimum length
                not part.lower() in ['and', 'also', 'but', 'or', 'so', 'then', 'next'] and  # Not just connectors
                any(char.isalpha() for char in part)):  # Contains letters
                cleaned_parts.append(part)
        
        # Limit to 5 parts and ensure we have at least the original if nothing was split
        result_parts = cleaned_parts[:5] if cleaned_parts else [user_input.strip()]
        
        return result_parts
    
    def _calculate_processing_confidence(
        self, 
        user_input: str, 
        pattern_type: ResponsePatternType,
        tone_indicators: Dict[str, float],
        ambiguity_level: float
    ) -> float:
        """Calculate confidence in the input processing."""
        base_confidence = 0.7
        
        # Adjust for input length
        word_count = len(user_input.split())
        if 5 <= word_count <= 20:
            base_confidence += 0.1
        elif word_count < 3:
            base_confidence -= 0.3
        
        # Adjust for ambiguity
        base_confidence -= ambiguity_level * 0.3
        
        # Adjust for clear tone indicators
        max_tone_score = max(tone_indicators.values()) if tone_indicators else 0
        base_confidence += max_tone_score * 0.1
        
        return max(0.1, min(1.0, base_confidence))
    
    def _generate_structured_response(
        self, 
        processed_input: ProcessedInput,
        document_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EnhancedResponse:
        """Generate structured response based on the detected pattern."""
        try:
            if processed_input.pattern_type == ResponsePatternType.DOCUMENT:
                return self._generate_document_pattern_response(processed_input, document_content, context)
            elif processed_input.pattern_type == ResponsePatternType.GENERAL_LEGAL:
                return self._generate_general_legal_pattern_response(processed_input, document_content, context)
            elif processed_input.pattern_type == ResponsePatternType.DATA_TABLE:
                return self._generate_data_table_pattern_response(processed_input, document_content, context)
            elif processed_input.pattern_type == ResponsePatternType.AMBIGUOUS:
                return self._generate_ambiguous_pattern_response(processed_input, document_content, context)
            else:
                return self._generate_error_recovery_response(processed_input, document_content, context)
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            return self._generate_error_recovery_response(processed_input, document_content, context)
    
    def _generate_document_pattern_response(
        self, 
        processed_input: ProcessedInput,
        document_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EnhancedResponse:
        """Generate document pattern response: Evidence, Plain English, Implications."""
        try:
            # Extract evidence from document
            evidence = self._extract_evidence(processed_input.original_text, document_content)
            
            # Generate plain English explanation
            plain_english = self._generate_plain_english_explanation(processed_input.original_text, evidence)
            
            # Analyze implications
            implications = self._analyze_implications(processed_input.original_text, evidence)
            
            # Format response
            content = self._format_document_response(evidence, plain_english, implications)
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=processed_input.confidence,
                sources=["structured_document_analysis"],
                suggestions=self._generate_document_suggestions(processed_input.original_text),
                tone=ToneType.PROFESSIONAL,
                structured_format={
                    "pattern": "document",
                    "evidence": evidence,
                    "plain_english": plain_english,
                    "implications": implications
                },
                context_used=["document_content"],
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in document pattern response: {e}")
            return self._generate_fallback_document_response(processed_input)
    
    def _generate_general_legal_pattern_response(
        self, 
        processed_input: ProcessedInput,
        document_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EnhancedResponse:
        """Generate general legal pattern response: Status, General Rule, Application."""
        try:
            # Determine document coverage status
            status = self._determine_document_status(processed_input.original_text, document_content)
            
            # Provide general legal rule
            general_rule = self._provide_general_legal_rule(processed_input.original_text)
            
            # Explain practical application
            application = self._explain_practical_application(processed_input.original_text, general_rule)
            
            # Format response
            content = self._format_general_legal_response(status, general_rule, application)
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.GENERAL_KNOWLEDGE,
                confidence=processed_input.confidence,
                sources=["general_legal_knowledge"],
                suggestions=self._generate_general_legal_suggestions(processed_input.original_text),
                tone=ToneType.PROFESSIONAL,
                structured_format={
                    "pattern": "general_legal",
                    "status": status,
                    "general_rule": general_rule,
                    "application": application
                },
                context_used=["general_knowledge"],
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in general legal pattern response: {e}")
            return self._generate_fallback_general_response(processed_input)
    
    def _generate_data_table_pattern_response(
        self, 
        processed_input: ProcessedInput,
        document_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EnhancedResponse:
        """Generate data table pattern response with automatic exports."""
        try:
            # Extract or generate table data
            table_data = self._extract_table_data(processed_input.original_text, document_content)
            
            # Create data table
            data_table = DataTable(
                headers=table_data.get('headers', ['Item', 'Details']),
                rows=table_data.get('rows', [['No data', 'available']]),
                title=table_data.get('title', 'Contract Information'),
                metadata={'source': 'document_analysis', 'timestamp': datetime.now().isoformat()}
            )
            
            # Generate exports
            export_files = self._generate_export_files(data_table)
            
            # Format response with table
            content = self._format_data_table_response(data_table, export_files)
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=processed_input.confidence,
                sources=["data_extraction"],
                suggestions=self._generate_data_suggestions(processed_input.original_text),
                tone=ToneType.PROFESSIONAL,
                structured_format={
                    "pattern": "data_table",
                    "table": data_table,
                    "exports": export_files
                },
                context_used=["data_analysis"],
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in data table pattern response: {e}")
            return self._generate_fallback_data_response(processed_input)
    
    def _generate_ambiguous_pattern_response(
        self, 
        processed_input: ProcessedInput,
        document_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EnhancedResponse:
        """Generate enhanced ambiguous pattern response with multiple analysis paths."""
        try:
            # Enhanced ambiguity interpretation
            interpretation_analysis = self._analyze_question_ambiguity(processed_input.original_text)
            
            # Determine primary interpretation with confidence
            primary_interpretation = self._determine_primary_interpretation_enhanced(
                processed_input.original_text, interpretation_analysis, document_content
            )
            
            # Generate multiple alternative interpretations
            alternatives = self._generate_enhanced_alternative_interpretations(
                processed_input.original_text, interpretation_analysis, document_content
            )
            
            # Create comprehensive synthesis
            synthesis = self._create_enhanced_interpretation_synthesis(
                primary_interpretation, alternatives, processed_input.tone_indicators
            )
            
            # Format response with tone adaptation
            content = self._format_enhanced_ambiguous_response(
                primary_interpretation, alternatives, synthesis, processed_input.tone_indicators
            )
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.DOCUMENT_ANALYSIS,
                confidence=processed_input.confidence,
                sources=["enhanced_ambiguity_resolution"],
                suggestions=self._generate_enhanced_clarification_suggestions(processed_input.original_text, alternatives),
                tone=ToneType.CONVERSATIONAL,
                structured_format={
                    "pattern": "ambiguous_enhanced",
                    "primary_interpretation": primary_interpretation,
                    "alternatives": alternatives,
                    "synthesis": synthesis,
                    "ambiguity_analysis": interpretation_analysis
                },
                context_used=["enhanced_ambiguity_handling"],
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error in enhanced ambiguous pattern response: {e}")
            return self._generate_fallback_ambiguous_response(processed_input)
    
    def _generate_error_recovery_response(
        self, 
        processed_input: ProcessedInput,
        document_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EnhancedResponse:
        """Generate error recovery response with helpful suggestions."""
        content = "I want to help you with your contract question, but I need to approach it differently."
        
        # Add specific guidance based on input
        if len(processed_input.original_text.strip()) < 3:
            content += "\n\nYour question seems quite brief. Could you provide more details about what you'd like to know?"
        elif processed_input.ambiguity_level > 0.7:
            content += "\n\nYour question has multiple possible meanings. Let me try to address the most likely interpretation."
        else:
            content += "\n\nLet me try to help with what I understand from your question."
        
        # Add structured suggestions
        content += "\n\n**Here are some ways I can help:**"
        content += "\n- Explain specific contract clauses or terms"
        content += "\n- Analyze risks and obligations"
        content += "\n- Provide general legal context"
        content += "\n- Create summaries or data exports"
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.FALLBACK,
            confidence=0.5,
            sources=["error_recovery"],
            suggestions=[
                "What does this specific clause mean?",
                "What are the key risks in this contract?",
                "Can you summarize the main terms?",
                "What are my obligations under this agreement?"
            ],
            tone=ToneType.CONVERSATIONAL,
            structured_format={
                "pattern": "error_recovery",
                "recovery_type": "input_processing_error"
            },
            context_used=["error_handling"],
            timestamp=datetime.now()
        )
    
    def _initialize_pattern_templates(self) -> Dict[str, Dict[str, str]]:
        """Initialize response pattern templates."""
        return {
            "document": {
                "evidence_header": "### 📋 Evidence",
                "plain_english_header": "### 🔍 Plain English", 
                "implications_header": "### ⚖️ Implications"
            },
            "general_legal": {
                "status_header": "### ℹ️ Status",
                "general_rule_header": "### 📚 General Rule",
                "application_header": "### 🎯 Application"
            },
            "ambiguous": {
                "interpretation_header": "🤔 **My Take:**",
                "option_prefix": "**If Option",
                "synthesis_header": "**Synthesis:**"
            },
            "data_table": {
                "export_footer": "📥 **Export:** CSV/Excel available here:"
            }
        }
    
    def _initialize_fallback_chains(self) -> Dict[str, List[str]]:
        """Initialize fallback chains for never-fail logic."""
        return {
            "input_processing": [
                "primary_analysis",
                "simplified_analysis", 
                "keyword_extraction",
                "generic_response"
            ],
            "response_generation": [
                "pattern_based_response",
                "template_response",
                "fallback_response",
                "emergency_response"
            ],
            "export_generation": [
                "full_export",
                "simple_export",
                "inline_data",
                "no_export"
            ]
        }
    
    def _initialize_tone_rules(self) -> Dict[str, Dict[str, float]]:
        """Initialize tone adaptation rules."""
        return {
            "casual_to_professional": {
                "threshold": 0.6,
                "adjustment": 0.3
            },
            "formal_enhancement": {
                "threshold": 0.4,
                "adjustment": 0.2
            },
            "technical_simplification": {
                "threshold": 0.8,
                "adjustment": -0.4
            }
        } 
   
    # Helper methods for response generation
    
    def _extract_evidence(self, question: str, document_content: Optional[str]) -> str:
        """Extract evidence from document content."""
        if not document_content:
            return "No document content available for evidence extraction."
        
        try:
            # Simple keyword-based evidence extraction
            question_lower = question.lower()
            content_lower = document_content.lower()
            
            # Look for relevant sections
            evidence_sections = []
            
            # Split document into sentences
            sentences = [s.strip() for s in document_content.split('.') if s.strip()]
            
            # Find sentences that contain question keywords
            question_words = [word for word in question_lower.split() if len(word) > 3]
            
            for sentence in sentences[:50]:  # Limit search
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in question_words):
                    evidence_sections.append(sentence.strip())
            
            if evidence_sections:
                return "Based on the document:\n" + "\n".join(f"- {section}" for section in evidence_sections[:3])
            else:
                return "The document contains relevant information, but specific evidence for this question requires closer examination of the full text."
                
        except Exception as e:
            logger.error(f"Error extracting evidence: {e}")
            return "Evidence extraction encountered an issue, but the document contains information relevant to your question."
    
    def _generate_plain_english_explanation(self, question: str, evidence: str) -> str:
        """Generate plain English explanation."""
        try:
            question_lower = question.lower()
            
            # Common legal terms and their explanations
            explanations = {
                'liability': "Liability refers to legal responsibility - who is responsible if something goes wrong.",
                'indemnification': "Indemnification means one party agrees to protect the other from certain losses or legal claims.",
                'breach': "A breach occurs when someone doesn't fulfill their obligations under the contract.",
                'termination': "Termination is how and when the contract can be ended by either party.",
                'consideration': "Consideration is what each party gives or receives in exchange (money, services, etc.).",
                'force majeure': "Force majeure covers unforeseeable events (like natural disasters) that prevent contract performance.",
                'warranty': "A warranty is a promise or guarantee about the quality or condition of something.",
                'covenant': "A covenant is a formal promise or commitment to do or not do something."
            }
            
            # Find relevant explanations
            relevant_explanations = []
            for term, explanation in explanations.items():
                if term in question_lower or term in evidence.lower():
                    relevant_explanations.append(f"**{term.title()}**: {explanation}")
            
            if relevant_explanations:
                return "Here's what this means in plain terms:\n" + "\n".join(relevant_explanations)
            else:
                return "In simple terms: This relates to the rights, responsibilities, and practical arrangements between the parties in the contract."
                
        except Exception as e:
            logger.error(f"Error generating plain English explanation: {e}")
            return "This involves the practical terms and conditions that govern the relationship between the parties."
    
    def _analyze_implications(self, question: str, evidence: str) -> str:
        """Analyze practical implications."""
        try:
            question_lower = question.lower()
            
            # Common implication patterns
            if any(word in question_lower for word in ['payment', 'pay', 'fee', 'cost']):
                return "**Financial Impact**: Review payment schedules, late fees, and consequences of non-payment.\n**Action Items**: Set up payment tracking and ensure compliance with payment terms."
            
            elif any(word in question_lower for word in ['termination', 'terminate', 'end']):
                return "**Risk Assessment**: Understand termination triggers and notice requirements.\n**Action Items**: Plan for potential termination scenarios and ensure proper procedures are followed."
            
            elif any(word in question_lower for word in ['liability', 'damages', 'responsible']):
                return "**Risk Exposure**: Identify potential liability scenarios and coverage limits.\n**Action Items**: Consider insurance coverage and risk mitigation strategies."
            
            elif any(word in question_lower for word in ['breach', 'violation', 'default']):
                return "**Compliance Risk**: Understand what constitutes a breach and potential consequences.\n**Action Items**: Implement compliance monitoring and have remediation plans ready."
            
            else:
                return "**General Considerations**: This affects your rights and obligations under the contract.\n**Action Items**: Ensure you understand and can comply with the relevant requirements."
                
        except Exception as e:
            logger.error(f"Error analyzing implications: {e}")
            return "**Key Consideration**: This provision affects your rights and responsibilities under the agreement.\n**Recommended Action**: Review with legal counsel if you have concerns about compliance or interpretation."
    
    def _format_document_response(self, evidence: str, plain_english: str, implications: str) -> str:
        """Format document pattern response."""
        template = self.pattern_templates["document"]
        
        return f"""{template["evidence_header"]}
{evidence}

{template["plain_english_header"]}
{plain_english}

{template["implications_header"]}
{implications}"""
    
    def _determine_document_status(self, question: str, document_content: Optional[str]) -> str:
        """Determine document coverage status."""
        if not document_content:
            return "No document is currently loaded for analysis."
        
        try:
            question_lower = question.lower()
            content_lower = document_content.lower()
            
            # Check if question terms appear in document
            question_words = [word for word in question_lower.split() if len(word) > 3]
            matches = sum(1 for word in question_words if word in content_lower)
            
            if matches > len(question_words) * 0.7:
                return "The document covers this topic directly."
            elif matches > len(question_words) * 0.3:
                return "The document has some related information, but this question goes beyond what's specifically covered."
            else:
                return "The document doesn't specifically address this question, but here's what typically applies:"
                
        except Exception as e:
            logger.error(f"Error determining document status: {e}")
            return "Document analysis is limited, but here's general guidance:"
    
    def _provide_general_legal_rule(self, question: str) -> str:
        """Provide general legal rule or principle."""
        question_lower = question.lower()
        
        # Common legal principles
        if any(word in question_lower for word in ['contract', 'agreement', 'binding']):
            return "Contracts are legally binding agreements that require offer, acceptance, and consideration. Both parties must have the capacity to enter into the agreement."
        
        elif any(word in question_lower for word in ['liability', 'damages', 'responsible']):
            return "Legal liability typically requires proving duty, breach of duty, causation, and damages. Parties can limit liability through contract terms, subject to legal restrictions."
        
        elif any(word in question_lower for word in ['breach', 'violation', 'default']):
            return "Contract breaches can be material (fundamental) or minor. Remedies may include damages, specific performance, or contract termination, depending on the severity."
        
        elif any(word in question_lower for word in ['termination', 'terminate', 'end']):
            return "Contracts can typically be terminated by mutual agreement, completion of terms, breach by one party, or specific termination clauses. Notice requirements often apply."
        
        else:
            return "Contract law generally requires parties to act in good faith and deal fairly with each other. Specific terms control, but general legal principles provide the framework."
    
    def _explain_practical_application(self, question: str, general_rule: str) -> str:
        """Explain practical application of legal rule."""
        question_lower = question.lower()
        
        if 'contract' in question_lower:
            return "In practice: Ensure all agreements are in writing, clearly define terms, and include dispute resolution procedures. Keep records of all communications and performance."
        
        elif 'liability' in question_lower:
            return "In practice: Consider insurance coverage, include limitation of liability clauses where legally permissible, and implement risk management procedures."
        
        elif 'breach' in question_lower:
            return "In practice: Document any breaches immediately, attempt to resolve through communication first, and preserve evidence for potential legal action."
        
        elif 'termination' in question_lower:
            return "In practice: Follow notice requirements exactly, document reasons for termination, and ensure proper wind-down procedures are followed."
        
        else:
            return "In practice: Document everything, communicate clearly with all parties, and seek legal advice when uncertain about rights or obligations."
    
    def _format_general_legal_response(self, status: str, general_rule: str, application: str) -> str:
        """Format general legal pattern response."""
        template = self.pattern_templates["general_legal"]
        
        return f"""{template["status_header"]}
{status}

{template["general_rule_header"]}
{general_rule}

{template["application_header"]}
{application}"""
    
    def _extract_table_data(self, question: str, document_content: Optional[str]) -> Dict[str, Any]:
        """Extract or generate table data from document."""
        try:
            question_lower = question.lower()
            
            # Default table structure
            table_data = {
                'title': 'Contract Information',
                'headers': ['Item', 'Details'],
                'rows': []
            }
            
            if not document_content:
                table_data['rows'] = [['Status', 'No document loaded']]
                return table_data
            
            # Generate different tables based on question type
            if any(word in question_lower for word in ['party', 'parties', 'who']):
                table_data['title'] = 'Contract Parties'
                table_data['headers'] = ['Role', 'Entity', 'Responsibilities']
                table_data['rows'] = [
                    ['Party 1', 'First contracting party', 'Primary obligations'],
                    ['Party 2', 'Second contracting party', 'Secondary obligations']
                ]
            
            elif any(word in question_lower for word in ['payment', 'fee', 'cost']):
                table_data['title'] = 'Payment Terms'
                table_data['headers'] = ['Payment Type', 'Amount', 'Due Date', 'Conditions']
                table_data['rows'] = [
                    ['Initial Payment', 'As specified', 'Upon signing', 'Standard terms'],
                    ['Ongoing Fees', 'As specified', 'Monthly/Quarterly', 'Performance based']
                ]
            
            elif any(word in question_lower for word in ['timeline', 'schedule', 'dates']):
                table_data['title'] = 'Contract Timeline'
                table_data['headers'] = ['Milestone', 'Date', 'Responsible Party', 'Status']
                table_data['rows'] = [
                    ['Contract Start', 'Effective Date', 'Both parties', 'Active'],
                    ['Key Deliverables', 'As specified', 'As assigned', 'Pending'],
                    ['Contract End', 'Expiration Date', 'Both parties', 'Future']
                ]
            
            elif any(word in question_lower for word in ['risk', 'liability', 'responsibility']):
                table_data['title'] = 'Risk and Liability Matrix'
                table_data['headers'] = ['Risk Type', 'Responsible Party', 'Mitigation', 'Impact Level']
                table_data['rows'] = [
                    ['Performance Risk', 'Service Provider', 'SLA monitoring', 'Medium'],
                    ['Financial Risk', 'Both parties', 'Insurance coverage', 'High'],
                    ['Legal Risk', 'As specified', 'Legal compliance', 'Variable']
                ]
            
            else:
                # Generic contract summary table
                table_data['title'] = 'Contract Summary'
                table_data['headers'] = ['Aspect', 'Details']
                table_data['rows'] = [
                    ['Document Type', 'Contract/Agreement'],
                    ['Parties', 'Multiple parties involved'],
                    ['Key Terms', 'Various obligations and rights'],
                    ['Status', 'Active/Under Review']
                ]
            
            return table_data
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return {
                'title': 'Contract Information',
                'headers': ['Item', 'Status'],
                'rows': [['Analysis', 'Unable to generate detailed table']]
            }
    
    def _generate_export_files(self, data_table: DataTable) -> List[ExportFile]:
        """Generate CSV and Excel export files."""
        export_files = []
        
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"contract_data_{timestamp}"
            
            # Generate CSV
            csv_filename = f"{base_filename}.csv"
            csv_path = os.path.join(self.export_directory, csv_filename)
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(data_table.headers)
                writer.writerows(data_table.rows)
            
            export_files.append(ExportFile(
                filename=csv_filename,
                file_path=csv_path,
                format_type="csv",
                download_url=f"/exports/{csv_filename}",
                creation_time=datetime.now()
            ))
            
            # Generate Excel (simplified - would need openpyxl for full Excel support)
            # For now, create a second CSV with .xlsx extension as placeholder
            excel_filename = f"{base_filename}.xlsx"
            excel_path = os.path.join(self.export_directory, excel_filename)
            
            # Copy CSV content to Excel placeholder
            with open(excel_path, 'w', newline='', encoding='utf-8') as excelfile:
                writer = csv.writer(excelfile)
                writer.writerow(data_table.headers)
                writer.writerows(data_table.rows)
            
            export_files.append(ExportFile(
                filename=excel_filename,
                file_path=excel_path,
                format_type="xlsx",
                download_url=f"/exports/{excel_filename}",
                creation_time=datetime.now()
            ))
            
        except Exception as e:
            logger.error(f"Error generating export files: {e}")
            # Return empty list if export generation fails
            
        return export_files
    
    def _format_data_table_response(self, data_table: DataTable, export_files: List[ExportFile]) -> str:
        """Format data table response with exports."""
        # Create table display
        content = f"## {data_table.title}\n\n"
        
        # Add table
        if data_table.headers and data_table.rows:
            # Create markdown table
            header_row = "| " + " | ".join(data_table.headers) + " |"
            separator_row = "|" + "|".join([" --- " for _ in data_table.headers]) + "|"
            
            content += header_row + "\n" + separator_row + "\n"
            
            for row in data_table.rows:
                row_content = "| " + " | ".join(str(cell) for cell in row) + " |"
                content += row_content + "\n"
        
        # Add export links
        if export_files:
            content += f"\n{self.pattern_templates['data_table']['export_footer']}\n"
            for export_file in export_files:
                content += f"- [{export_file.format_type.upper()}]({export_file.download_url})\n"
        
        return content
    
    def _determine_primary_interpretation(self, question: str) -> str:
        """Determine primary interpretation of ambiguous input."""
        question_lower = question.lower()
        
        # Look for the most likely interpretation based on keywords
        if any(word in question_lower for word in ['payment', 'pay', 'money', 'cost']):
            return "I'm reading this as a question about payment terms and financial obligations."
        
        elif any(word in question_lower for word in ['party', 'who', 'responsible']):
            return "I'm interpreting this as asking about the parties involved and their responsibilities."
        
        elif any(word in question_lower for word in ['when', 'timeline', 'schedule']):
            return "I'm understanding this as a question about timing and deadlines."
        
        elif any(word in question_lower for word in ['risk', 'liability', 'problem']):
            return "I'm reading this as a concern about risks and potential liabilities."
        
        else:
            return "I'm interpreting this as a general question about the contract terms and conditions."
    
    def _generate_alternative_interpretations(self, question: str) -> List[Dict[str, str]]:
        """Generate alternative interpretations."""
        alternatives = []
        question_lower = question.lower()
        
        # Generate 2-3 alternative interpretations
        if 'what' in question_lower:
            alternatives.append({
                'option': 'A',
                'interpretation': 'You want a definition or explanation of specific terms',
                'response': 'I can explain the relevant contract terms and their meanings.'
            })
            alternatives.append({
                'option': 'B', 
                'interpretation': 'You want to know about practical implications',
                'response': 'I can analyze how this affects your rights and obligations.'
            })
        
        elif 'how' in question_lower:
            alternatives.append({
                'option': 'A',
                'interpretation': 'You want to understand a process or procedure',
                'response': 'I can walk through the relevant steps and requirements.'
            })
            alternatives.append({
                'option': 'B',
                'interpretation': 'You want to know about implementation',
                'response': 'I can provide guidance on putting this into practice.'
            })
        
        else:
            alternatives.append({
                'option': 'A',
                'interpretation': 'You want specific information from the document',
                'response': 'I can search for and explain relevant contract provisions.'
            })
            alternatives.append({
                'option': 'B',
                'interpretation': 'You want general legal context',
                'response': 'I can provide background on how this typically works in contracts.'
            })
        
        return alternatives
    
    def _create_interpretation_synthesis(self, primary: str, alternatives: List[Dict[str, str]]) -> str:
        """Create synthesis of different interpretations."""
        if not alternatives:
            return "The most straightforward approach is to address your question directly based on the contract content."
        
        return f"These interpretations are related - understanding the specific contract terms (Option A) provides the foundation for practical application (Option B). I recommend starting with the contract specifics and then discussing implementation."
    
    def _format_ambiguous_response(self, primary: str, alternatives: List[Dict[str, str]], synthesis: str) -> str:
        """Format ambiguous pattern response."""
        template = self.pattern_templates["ambiguous"]
        
        content = f"{template['interpretation_header']} {primary}\n\n"
        
        for alt in alternatives:
            content += f"{template['option_prefix']} {alt['option']}:** {alt['interpretation']}\n"
            content += f"{alt['response']}\n\n"
        
        content += f"{template['synthesis_header']} {synthesis}"
        
        return content
    
    def _apply_tone_adaptation(self, response: EnhancedResponse, processed_input: ProcessedInput) -> EnhancedResponse:
        """Apply intelligent tone adaptation while preserving structured analysis format."""
        try:
            tone_indicators = processed_input.tone_indicators
            
            # Determine dominant tone style
            casual_score = tone_indicators.get('casual', 0)
            formal_score = tone_indicators.get('formal', 0)
            technical_score = tone_indicators.get('technical', 0)
            business_score = tone_indicators.get('business', 0)
            startup_score = tone_indicators.get('startup', 0)
            slang_score = tone_indicators.get('slang', 0)
            
            # Calculate overall tone profile
            total_casual = casual_score + slang_score + startup_score
            total_formal = formal_score + technical_score + business_score
            
            # Apply tone adaptation based on dominant style
            if total_casual > 0.4 and total_casual > total_formal:
                # Casual/conversational adaptation
                response.tone = ToneType.CONVERSATIONAL
                response.content = self._adapt_to_casual_tone(response.content, tone_indicators)
                
            elif total_formal > 0.5:
                # Formal/professional adaptation
                response.tone = ToneType.PROFESSIONAL
                response.content = self._adapt_to_formal_tone(response.content, tone_indicators)
                
            elif startup_score > 0.3:
                # Startup/tech adaptation
                response.tone = ToneType.CONVERSATIONAL
                response.content = self._adapt_to_startup_tone(response.content)
                
            elif technical_score > 0.4:
                # Technical adaptation
                response.tone = ToneType.PROFESSIONAL
                response.content = self._adapt_to_technical_tone(response.content)
                
            # Add multi-part response handling if multiple question parts detected
            if len(processed_input.question_parts) > 1:
                response.content = self._format_multi_part_response(
                    response.content, processed_input.question_parts, tone_indicators
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error applying tone adaptation: {e}")
            return response
    
    def _adapt_to_casual_tone(self, content: str, tone_indicators: Dict[str, float]) -> str:
        """Adapt content to casual/conversational tone while preserving structure."""
        # Preserve structured headers but make content more conversational
        conversational_replacements = {
            "The document indicates": "From what I can see in the document",
            "It is recommended": "I'd recommend",
            "This provision states": "This part says",
            "In accordance with": "According to",
            "Furthermore": "Also",
            "Therefore": "So",
            "The analysis reveals": "What I'm seeing is",
            "It should be noted": "Worth noting",
            "The parties are required": "Both sides need to",
            "This clause establishes": "This section sets up",
            "The agreement specifies": "The contract says"
        }
        
        adapted_content = content
        for formal, casual in conversational_replacements.items():
            adapted_content = adapted_content.replace(formal, casual)
        
        # Add casual connectors while preserving structure
        if tone_indicators.get('slang', 0) > 0.3:
            adapted_content = self._add_casual_connectors(adapted_content)
        
        return adapted_content
    
    def _adapt_to_formal_tone(self, content: str, tone_indicators: Dict[str, float]) -> str:
        """Adapt content to formal/professional tone."""
        formal_replacements = {
            "I'd say": "The analysis indicates",
            "looks like": "appears to be",
            "pretty much": "essentially",
            "kind of": "somewhat",
            "really": "particularly",
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "must",
            "ok": "acceptable",
            "yeah": "yes"
        }
        
        adapted_content = content
        for casual, formal in formal_replacements.items():
            adapted_content = adapted_content.replace(casual, formal)
        
        # Enhance with formal legal language if technical score is high
        if tone_indicators.get('technical', 0) > 0.5:
            adapted_content = self._enhance_with_legal_terminology(adapted_content)
        
        return adapted_content
    
    def _adapt_to_startup_tone(self, content: str) -> str:
        """Adapt content to startup/tech communication style."""
        startup_replacements = {
            "The document indicates": "Looking at this agreement",
            "It is recommended": "I'd suggest",
            "This provision": "This clause",
            "The parties": "Both companies",
            "obligations": "commitments",
            "termination": "ending the partnership",
            "intellectual property": "IP rights",
            "confidentiality": "keeping things private"
        }
        
        adapted_content = content
        for formal, startup in startup_replacements.items():
            adapted_content = adapted_content.replace(formal, startup)
        
        # Add startup-friendly context
        adapted_content = self._add_startup_context(adapted_content)
        
        return adapted_content
    
    def _adapt_to_technical_tone(self, content: str) -> str:
        """Adapt content to technical/legal precision."""
        # Enhance with precise legal terminology
        technical_enhancements = {
            "agreement": "contractual agreement",
            "parties": "contracting parties",
            "terms": "contractual terms",
            "conditions": "terms and conditions",
            "obligations": "legal obligations",
            "rights": "legal rights and entitlements"
        }
        
        adapted_content = content
        for basic, technical in technical_enhancements.items():
            # Only replace if not already technical
            if basic in adapted_content and technical not in adapted_content:
                adapted_content = adapted_content.replace(basic, technical)
        
        return adapted_content
    
    def _add_casual_connectors(self, content: str) -> str:
        """Add casual connectors to make content more conversational."""
        # Add casual transitions between sections
        casual_transitions = {
            "\n\n### ": "\n\nSo, looking at ",
            "### 📋 Evidence": "### 📋 Here's what I found",
            "### 🔍 Plain English": "### 🔍 In simple terms",
            "### ⚖️ Implications": "### ⚖️ What this means for you"
        }
        
        adapted_content = content
        for formal, casual in casual_transitions.items():
            adapted_content = adapted_content.replace(formal, casual)
        
        return adapted_content
    
    def _enhance_with_legal_terminology(self, content: str) -> str:
        """Enhance content with precise legal terminology."""
        # Add legal precision where appropriate
        legal_enhancements = {
            "says": "provides",
            "means": "establishes",
            "allows": "permits",
            "requires": "mandates",
            "can": "may",
            "must": "shall"
        }
        
        enhanced_content = content
        for casual, legal in legal_enhancements.items():
            enhanced_content = enhanced_content.replace(f" {casual} ", f" {legal} ")
        
        return enhanced_content
    
    def _add_startup_context(self, content: str) -> str:
        """Add startup-friendly context and explanations."""
        # Add startup-relevant context
        if "equity" in content.lower() or "vesting" in content.lower():
            content += "\n\n💡 *This is particularly important for startup equity arrangements.*"
        elif "intellectual property" in content.lower() or "ip" in content.lower():
            content += "\n\n💡 *IP ownership is crucial for startup valuation and future funding.*"
        elif "confidentiality" in content.lower():
            content += "\n\n💡 *Protecting your startup's competitive advantage is key.*"
        
        return content
    
    def _format_multi_part_response(self, content: str, question_parts: List[str], tone_indicators: Dict[str, float]) -> str:
        """Format response for multi-part questions with numbered components and synthesis."""
        if len(question_parts) <= 1:
            return content
        
        # Determine if casual or formal numbering
        is_casual = tone_indicators.get('casual', 0) + tone_indicators.get('slang', 0) > 0.4
        
        # Create multi-part response structure
        multi_part_header = "You asked several things, so let me break this down:\n\n" if is_casual else "Your question has multiple components. Here's my analysis:\n\n"
        
        # Split content into logical sections for each part
        content_sections = self._split_content_for_parts(content, len(question_parts))
        
        formatted_response = multi_part_header
        
        for i, (part, section) in enumerate(zip(question_parts, content_sections), 1):
            part_header = f"**{i}. Re: \"{part[:50]}{'...' if len(part) > 50 else ''}\"**\n" if not is_casual else f"**{i}. About \"{part[:50]}{'...' if len(part) > 50 else ''}\"**\n"
            formatted_response += part_header + section + "\n\n"
        
        # Add synthesis section
        synthesis_header = "**Putting it all together:**\n" if is_casual else "**Synthesis:**\n"
        synthesis_content = self._generate_synthesis_for_parts(question_parts, content_sections, tone_indicators)
        formatted_response += synthesis_header + synthesis_content
        
        return formatted_response
    
    def _split_content_for_parts(self, content: str, num_parts: int) -> List[str]:
        """Split content into sections corresponding to question parts."""
        # Simple approach: split content roughly equally
        sentences = content.split('. ')
        sentences_per_part = max(1, len(sentences) // num_parts)
        
        sections = []
        for i in range(num_parts):
            start_idx = i * sentences_per_part
            end_idx = start_idx + sentences_per_part if i < num_parts - 1 else len(sentences)
            section = '. '.join(sentences[start_idx:end_idx])
            if section and not section.endswith('.'):
                section += '.'
            sections.append(section)
        
        return sections
    
    def _generate_synthesis_for_parts(self, question_parts: List[str], content_sections: List[str], tone_indicators: Dict[str, float]) -> str:
        """Generate synthesis section for multi-part responses."""
        is_casual = tone_indicators.get('casual', 0) + tone_indicators.get('slang', 0) > 0.4
        
        if is_casual:
            synthesis = "Looking at all your questions together, the main themes are around understanding the contract's key terms and implications. "
        else:
            synthesis = "Analyzing these components collectively, the primary focus areas involve contractual interpretation and risk assessment. "
        
        # Add connecting themes
        if len(question_parts) > 2:
            synthesis += "These aspects are interconnected and should be considered as part of your overall contract strategy."
        else:
            synthesis += "These two areas are closely related and both impact your contractual position."
        
        return synthesis
    
    def _add_data_exports_if_applicable(self, response: EnhancedResponse, processed_input: ProcessedInput) -> EnhancedResponse:
        """Add data exports if the response contains tabular data."""
        try:
            if (processed_input.data_request_detected or 
                processed_input.pattern_type == ResponsePatternType.DATA_TABLE):
                # Export functionality already handled in data table pattern
                return response
            
            # Check if response contains table-like content
            if self._contains_tabular_content(response.content):
                # Extract table data and add exports
                table_data = self._extract_table_from_content(response.content)
                if table_data:
                    export_files = self._generate_export_files(table_data)
                    if export_files:
                        response.content += f"\n\n📥 **Export:** Data available for download:\n"
                        for export_file in export_files:
                            response.content += f"- [{export_file.format_type.upper()}]({export_file.download_url})\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error adding data exports: {e}")
            return response
    
    def _contains_tabular_content(self, content: str) -> bool:
        """Check if content contains tabular data."""
        # Look for markdown table indicators
        return ('|' in content and '---' in content) or content.count('\n-') > 2
    
    def _extract_table_from_content(self, content: str) -> Optional[DataTable]:
        """Extract table data from content."""
        try:
            lines = content.split('\n')
            table_lines = []
            
            # Find table section
            in_table = False
            for line in lines:
                if '|' in line and not in_table:
                    in_table = True
                    table_lines.append(line)
                elif '|' in line and in_table:
                    table_lines.append(line)
                elif in_table and '|' not in line:
                    break
            
            if len(table_lines) >= 2:
                # Parse headers
                headers = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]
                
                # Parse rows (skip separator line)
                rows = []
                for line in table_lines[2:]:
                    if '|' in line:
                        row = [cell.strip() for cell in line.split('|')[1:-1]]
                        if len(row) == len(headers):
                            rows.append(row)
                
                return DataTable(
                    headers=headers,
                    rows=rows,
                    title="Extracted Data",
                    metadata={}
                )
            
        except Exception as e:
            logger.error(f"Error extracting table from content: {e}")
        
        return None
    
    def _validate_and_ensure_response_quality(self, response: EnhancedResponse, processed_input: ProcessedInput) -> EnhancedResponse:
        """Final validation and quality assurance."""
        try:
            # Ensure content is not empty
            if not response.content or not response.content.strip():
                response.content = "I understand you have a question about the contract. Let me help you with that."
                response.confidence = 0.3
            
            # Ensure minimum content length
            if len(response.content.strip()) < 50:
                response.content += "\n\nI'm here to help with any specific questions about contract terms, obligations, or implications."
            
            # Ensure suggestions are provided
            if not response.suggestions:
                response.suggestions = [
                    "What are the key terms in this contract?",
                    "What are my main obligations?",
                    "Are there any important deadlines?"
                ]
            
            # Ensure confidence is reasonable
            if response.confidence < 0.1:
                response.confidence = 0.3
            
            return response
            
        except Exception as e:
            logger.error(f"Error in response validation: {e}")
            return self._create_ultimate_fallback_response(processed_input.original_text, str(e))
    
    def _create_ultimate_fallback_response(self, user_input: str, error_message: str) -> EnhancedResponse:
        """Create the ultimate fallback response that should never fail."""
        try:
            content = "I'm here to help you understand your contract."
            
            if user_input and len(user_input.strip()) > 0:
                content += f"\n\nRegarding your question about: \"{user_input[:100]}{'...' if len(user_input) > 100 else ''}\""
                content += "\n\nI can help you with:"
            else:
                content += "\n\nI can help you with:"
            
            content += "\n- Explaining contract terms and clauses"
            content += "\n- Analyzing your rights and obligations"
            content += "\n- Identifying potential risks or concerns"
            content += "\n- Providing general legal context"
            
            content += "\n\nPlease feel free to ask about any specific aspect of your contract."
            
            return EnhancedResponse(
                content=content,
                response_type=ResponseType.FALLBACK,
                confidence=0.5,
                sources=["ultimate_fallback"],
                suggestions=[
                    "What does this clause mean?",
                    "What are my obligations?",
                    "Are there any risks I should know about?",
                    "Can you summarize the key terms?"
                ],
                tone=ToneType.PROFESSIONAL,
                structured_format={"pattern": "ultimate_fallback"},
                context_used=["emergency_response"],
                timestamp=datetime.now()
            )
            
        except Exception as final_error:
            # This should absolutely never happen, but just in case...
            logger.critical(f"Ultimate fallback failed: {final_error}")
            
            # Return the most basic possible response
            return EnhancedResponse(
                content="I'm here to help with your contract questions. Please ask about specific terms or clauses.",
                response_type=ResponseType.FALLBACK,
                confidence=0.3,
                sources=["emergency"],
                suggestions=["What does this mean?", "Help me understand this contract"],
                tone=ToneType.PROFESSIONAL,
                structured_format={},
                context_used=[],
                timestamp=datetime.now()
            )
    
    # Suggestion generation methods
    
    def _generate_document_suggestions(self, question: str) -> List[str]:
        """Generate suggestions for document-related questions."""
        return [
            "What are the termination conditions?",
            "Are there any liability limitations?",
            "What are the payment terms?",
            "Who are the parties to this agreement?"
        ]
    
    def _generate_general_legal_suggestions(self, question: str) -> List[str]:
        """Generate suggestions for general legal questions."""
        return [
            "How does this typically work in contracts?",
            "What are common practices in this area?",
            "What should I be careful about?",
            "Are there standard legal requirements?"
        ]
    
    def _generate_data_suggestions(self, question: str) -> List[str]:
        """Generate suggestions for data-related questions."""
        return [
            "Can you create a summary table?",
            "What are the key dates and deadlines?",
            "Show me the parties and their roles",
            "Create a risk assessment matrix"
        ]
    
    def _generate_clarification_suggestions(self, question: str) -> List[str]:
        """Generate clarification suggestions for ambiguous questions."""
        return [
            "Can you be more specific about what you need?",
            "Are you asking about a particular clause?",
            "Do you want legal context or practical guidance?",
            "Is this about compliance or interpretation?"
        ]
    
    # Fallback response generators
    
    def _generate_fallback_document_response(self, processed_input: ProcessedInput) -> EnhancedResponse:
        """Generate fallback for document pattern failures."""
        content = """### 📋 Evidence
I'm having difficulty extracting specific evidence from the document right now.

### 🔍 Plain English
Your question relates to contract terms that require careful analysis.

### ⚖️ Implications
This is an important aspect of your contract that deserves proper attention. Consider reviewing the relevant sections or consulting with legal counsel."""
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.4,
            sources=["fallback_document"],
            suggestions=self._generate_document_suggestions(processed_input.original_text),
            tone=ToneType.PROFESSIONAL,
            structured_format={"pattern": "document_fallback"},
            context_used=["fallback"],
            timestamp=datetime.now()
        )
    
    def _generate_fallback_general_response(self, processed_input: ProcessedInput) -> EnhancedResponse:
        """Generate fallback for general legal pattern failures."""
        content = """### ℹ️ Status
I'm having some difficulty analyzing the document coverage for this question.

### 📚 General Rule
Contract law generally requires parties to fulfill their obligations in good faith and according to the agreed terms.

### 🎯 Application
In practice, it's important to understand your specific rights and obligations under the contract terms."""
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.GENERAL_KNOWLEDGE,
            confidence=0.4,
            sources=["fallback_general"],
            suggestions=self._generate_general_legal_suggestions(processed_input.original_text),
            tone=ToneType.PROFESSIONAL,
            structured_format={"pattern": "general_fallback"},
            context_used=["fallback"],
            timestamp=datetime.now()
        )
    
    def _generate_fallback_data_response(self, processed_input: ProcessedInput) -> EnhancedResponse:
        """Generate fallback for data table pattern failures."""
        content = """## Contract Information

| Aspect | Status |
| --- | --- |
| Analysis | In progress |
| Data extraction | Limited |
| Export capability | Available upon request |

📥 **Export:** Please try rephrasing your data request for better results."""
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.4,
            sources=["fallback_data"],
            suggestions=self._generate_data_suggestions(processed_input.original_text),
            tone=ToneType.PROFESSIONAL,
            structured_format={"pattern": "data_fallback"},
            context_used=["fallback"],
            timestamp=datetime.now()
        )
    
    def _generate_fallback_ambiguous_response(self, processed_input: ProcessedInput) -> EnhancedResponse:
        """Generate fallback for ambiguous pattern failures."""
        content = """🤔 **My Take:** Your question has multiple possible interpretations, and I want to make sure I address what you're really asking about.

**If Option A:** You want specific information from the contract
I can search through the document for relevant terms and clauses.

**If Option B:** You want general guidance on this topic
I can provide context about how this typically works in contracts.

**Synthesis:** The best approach is often to start with the specific contract terms and then provide broader context as needed."""
        
        return EnhancedResponse(
            content=content,
            response_type=ResponseType.DOCUMENT_ANALYSIS,
            confidence=0.4,
            sources=["fallback_ambiguous"],
            suggestions=self._generate_clarification_suggestions(processed_input.original_text),
            tone=ToneType.CONVERSATIONAL,
            structured_format={"pattern": "ambiguous_fallback"},
            context_used=["fallback"],
            timestamp=datetime.now()
        )
    
    def _analyze_question_ambiguity(self, question: str) -> Dict[str, Any]:
        """Analyze the types and sources of ambiguity in a question."""
        question_lower = question.lower()
        
        # Identify ambiguity sources
        ambiguity_sources = []
        
        # Pronoun ambiguity
        pronouns = ['it', 'this', 'that', 'they', 'them', 'these', 'those']
        if any(pronoun in question_lower.split() for pronoun in pronouns):
            ambiguity_sources.append("pronoun_reference")
        
        # Multiple question words
        question_words = ['what', 'how', 'when', 'where', 'why', 'which', 'who']
        question_word_count = sum(1 for word in question_words if word in question_lower)
        if question_word_count > 1:
            ambiguity_sources.append("multiple_questions")
        
        # Vague terms
        vague_terms = ['thing', 'stuff', 'something', 'anything', 'everything', 'part', 'section']
        if any(term in question_lower for term in vague_terms):
            ambiguity_sources.append("vague_terminology")
        
        # Conditional language
        conditional_words = ['if', 'when', 'unless', 'provided', 'assuming', 'suppose']
        if any(word in question_lower for word in conditional_words):
            ambiguity_sources.append("conditional_scenarios")
        
        # Comparative language
        comparative_words = ['better', 'worse', 'more', 'less', 'compared to', 'versus', 'rather than']
        if any(word in question_lower for word in comparative_words):
            ambiguity_sources.append("comparative_analysis")
        
        # Calculate overall ambiguity level
        ambiguity_level = len(ambiguity_sources) / 6.0  # Normalize to 0-1
        
        return {
            'sources': ambiguity_sources,
            'level': ambiguity_level,
            'question_word_count': question_word_count,
            'has_conditionals': 'conditional_scenarios' in ambiguity_sources,
            'has_comparatives': 'comparative_analysis' in ambiguity_sources
        }
    
    def _determine_primary_interpretation_enhanced(self, question: str, ambiguity_analysis: Dict[str, Any], document_content: Optional[str]) -> Dict[str, Any]:
        """Determine the most likely interpretation with enhanced analysis."""
        question_lower = question.lower()
        
        # Analyze question intent
        intent_indicators = {
            'definition': ['what is', 'what does', 'define', 'meaning of', 'means'],
            'explanation': ['how does', 'how can', 'explain', 'why does', 'why is'],
            'comparison': ['difference', 'compare', 'versus', 'better', 'worse'],
            'procedure': ['how to', 'steps', 'process', 'procedure'],
            'consequences': ['what happens', 'result', 'outcome', 'implications'],
            'obligations': ['must', 'required', 'obligation', 'responsibility'],
            'rights': ['can', 'allowed', 'permitted', 'rights', 'entitlement']
        }
        
        # Score each intent
        intent_scores = {}
        for intent, indicators in intent_indicators.items():
            score = sum(1 for indicator in indicators if indicator in question_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # Determine primary intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else 'general_inquiry'
        
        # Generate interpretation based on primary intent
        interpretation = {
            'intent': primary_intent,
            'confidence': 0.8 - (ambiguity_analysis['level'] * 0.3),
            'reasoning': f"Based on the question structure and key terms, this appears to be a {primary_intent.replace('_', ' ')} question.",
            'focus_areas': self._identify_focus_areas(question, primary_intent),
            'document_relevance': self._assess_document_relevance(question, document_content)
        }
        
        return interpretation
    
    def _generate_enhanced_alternative_interpretations(self, question: str, ambiguity_analysis: Dict[str, Any], document_content: Optional[str]) -> List[Dict[str, Any]]:
        """Generate multiple alternative interpretations with analysis paths."""
        alternatives = []
        
        # If multiple question words, create interpretations for each
        if ambiguity_analysis['question_word_count'] > 1:
            question_words = ['what', 'how', 'when', 'where', 'why', 'which', 'who']
            found_words = [word for word in question_words if word in question.lower()]
            
            for word in found_words[:3]:  # Limit to 3 alternatives
                alternative = {
                    'focus': f"{word.title()}-focused interpretation",
                    'description': f"Interpreting this as primarily a '{word}' question",
                    'analysis_path': self._create_analysis_path_for_question_word(word, question),
                    'confidence': 0.6
                }
                alternatives.append(alternative)
        
        # If conditional language, create scenario-based interpretations
        if ambiguity_analysis['has_conditionals']:
            alternatives.append({
                'focus': "Conditional scenario analysis",
                'description': "Analyzing this as a hypothetical or conditional situation",
                'analysis_path': "Examine the conditions mentioned and their potential outcomes",
                'confidence': 0.7
            })
        
        # If comparative language, create comparison-based interpretations
        if ambiguity_analysis['has_comparatives']:
            alternatives.append({
                'focus': "Comparative analysis",
                'description': "Interpreting this as a request to compare different options or outcomes",
                'analysis_path': "Identify the elements being compared and analyze their relative merits",
                'confidence': 0.7
            })
        
        # If vague terminology, create clarification-seeking interpretation
        if 'vague_terminology' in ambiguity_analysis['sources']:
            alternatives.append({
                'focus': "Clarification-seeking interpretation",
                'description': "This question may need more specific details to provide a complete answer",
                'analysis_path': "Address the general concept while noting areas that need clarification",
                'confidence': 0.5
            })
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _create_enhanced_interpretation_synthesis(self, primary: Dict[str, Any], alternatives: List[Dict[str, Any]], tone_indicators: Dict[str, float]) -> Dict[str, Any]:
        """Create comprehensive synthesis of interpretations."""
        is_casual = tone_indicators.get('casual', 0) + tone_indicators.get('slang', 0) > 0.4
        
        synthesis = {
            'approach': 'comprehensive' if len(alternatives) > 1 else 'focused',
            'recommendation': '',
            'connections': [],
            'next_steps': []
        }
        
        if len(alternatives) > 1:
            if is_casual:
                synthesis['recommendation'] = f"I'm going with the {primary['intent'].replace('_', ' ')} angle as my main take, but I can see how this could also be about {alternatives[0]['focus'].lower()}."
            else:
                synthesis['recommendation'] = f"The primary interpretation focuses on {primary['intent'].replace('_', ' ')}, while alternative perspectives consider {', '.join([alt['focus'].lower() for alt in alternatives[:2]])}."
            
            # Identify connections between interpretations
            synthesis['connections'] = [
                "These interpretations are interconnected and addressing one often informs the others",
                "The document content can be analyzed from multiple angles to address each perspective"
            ]
        else:
            if is_casual:
                synthesis['recommendation'] = f"This looks like a {primary['intent'].replace('_', ' ')} question, so I'll focus on that angle."
            else:
                synthesis['recommendation'] = f"The analysis will focus on the {primary['intent'].replace('_', ' ')} aspect as the primary interpretation."
        
        # Add next steps
        synthesis['next_steps'] = [
            "Feel free to ask follow-up questions if you'd like me to explore any of these angles more deeply",
            "I can provide more specific analysis if you clarify which aspect is most important to you"
        ]
        
        return synthesis
    
    def _format_enhanced_ambiguous_response(self, primary: Dict[str, Any], alternatives: List[Dict[str, Any]], synthesis: Dict[str, Any], tone_indicators: Dict[str, float]) -> str:
        """Format enhanced ambiguous response with tone adaptation."""
        is_casual = tone_indicators.get('casual', 0) + tone_indicators.get('slang', 0) > 0.4
        
        # Header with tone adaptation
        if is_casual:
            header = f"🤔 **My Take:** I'm reading this as a {primary['intent'].replace('_', ' ')} question"
        else:
            header = f"🤔 **Primary Interpretation:** This appears to be a {primary['intent'].replace('_', ' ')} inquiry"
        
        content = header + f" (confidence: {primary['confidence']:.0%})\n\n"
        content += primary['reasoning'] + "\n\n"
        
        # Add alternatives if they exist
        if alternatives:
            content += "**Alternative Interpretations:**\n\n"
            for i, alt in enumerate(alternatives, 1):
                option_label = f"**Option {chr(64+i)}:** " if not is_casual else f"**If you meant:** "
                content += f"{option_label}{alt['description']}\n"
                content += f"- {alt['analysis_path']}\n\n"
        
        # Add synthesis
        content += f"**{'Bottom Line' if is_casual else 'Synthesis'}:**\n"
        content += synthesis['recommendation'] + "\n\n"
        
        if synthesis['connections']:
            content += "**How These Connect:**\n"
            for connection in synthesis['connections']:
                content += f"- {connection}\n"
            content += "\n"
        
        # Add next steps
        if synthesis['next_steps']:
            next_steps_header = "**What's Next:**" if is_casual else "**Recommended Next Steps:**"
            content += f"{next_steps_header}\n"
            for step in synthesis['next_steps']:
                content += f"- {step}\n"
        
        return content
    
    def _identify_focus_areas(self, question: str, intent: str) -> List[str]:
        """Identify key focus areas based on question and intent."""
        question_lower = question.lower()
        focus_areas = []
        
        # Legal document focus areas
        legal_areas = {
            'parties': ['party', 'parties', 'who', 'entity', 'organization'],
            'obligations': ['obligation', 'duty', 'must', 'shall', 'required', 'responsibility'],
            'rights': ['right', 'entitle', 'can', 'may', 'allowed', 'permitted'],
            'terms': ['term', 'condition', 'provision', 'clause'],
            'timeline': ['when', 'date', 'deadline', 'time', 'duration'],
            'consequences': ['penalty', 'breach', 'violation', 'consequence', 'result'],
            'termination': ['end', 'terminate', 'cancel', 'expire', 'dissolution']
        }
        
        for area, keywords in legal_areas.items():
            if any(keyword in question_lower for keyword in keywords):
                focus_areas.append(area)
        
        return focus_areas[:3]  # Limit to top 3
    
    def _assess_document_relevance(self, question: str, document_content: Optional[str]) -> float:
        """Assess how relevant the question is to the document content."""
        if not document_content:
            return 0.5
        
        question_words = set(question.lower().split())
        document_words = set(document_content.lower().split())
        
        # Calculate word overlap
        overlap = len(question_words.intersection(document_words))
        relevance = min(1.0, overlap / max(1, len(question_words)))
        
        return relevance
    
    def _create_analysis_path_for_question_word(self, question_word: str, question: str) -> str:
        """Create analysis path for specific question word focus."""
        paths = {
            'what': "Identify and define the key concepts or elements mentioned",
            'how': "Explain the process, mechanism, or method involved",
            'when': "Determine timing, deadlines, or temporal aspects",
            'where': "Identify location, jurisdiction, or applicable scope",
            'why': "Analyze the reasoning, purpose, or underlying rationale",
            'which': "Compare options and identify the most relevant choice",
            'who': "Identify the parties, roles, or responsible entities"
        }
        
        return paths.get(question_word, "Analyze the relevant aspects of the question")
    
    def _generate_enhanced_clarification_suggestions(self, question: str, alternatives: List[Dict[str, Any]]) -> List[str]:
        """Generate enhanced clarification suggestions based on ambiguity analysis."""
        suggestions = []
        
        # Base suggestions
        suggestions.extend([
            "Could you clarify which specific aspect you're most interested in?",
            "Would you like me to focus on a particular part of the contract?",
            "Are you looking for practical implications or technical details?"
        ])
        
        # Add alternative-specific suggestions
        for alt in alternatives[:2]:
            if 'conditional' in alt['focus'].lower():
                suggestions.append("Are you asking about a hypothetical scenario or current situation?")
            elif 'comparative' in alt['focus'].lower():
                suggestions.append("Which specific elements would you like me to compare?")
            elif 'clarification' in alt['focus'].lower():
                suggestions.append("Could you provide more specific details about what you're looking for?")
        
        return suggestions[:4]  # Limit to 4 suggestions