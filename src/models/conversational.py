"""
Conversational AI data models for enhanced Q&A capabilities.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class QuestionType:
    """Classification of question types for conversational AI."""
    primary_type: str  # casual, legal, technical, compound
    confidence: float
    sub_types: List[str]
    requires_legal_analysis: bool
    requires_context_switching: bool


@dataclass
class CompoundResponse:
    """Response structure for compound questions."""
    question_parts: List[str]
    individual_responses: List[Dict[str, Any]]
    synthesized_response: str
    sources: List[str]
    analysis_modes_used: List[str]


@dataclass
class ConversationalResponse:
    """Standard response structure for conversational interactions."""
    answer: str
    conversation_tone: str  # professional, casual, technical
    context_used: List[str]
    follow_up_suggestions: List[str]
    analysis_mode: str
    confidence: float


@dataclass
class ConversationContext:
    """Context management for conversation sessions."""
    session_id: str
    document_id: str
    conversation_history: List['ConversationTurn']
    current_topic: str
    analysis_mode: str
    user_preferences: Dict[str, Any]
    context_summary: str


@dataclass
class ConversationTurn:
    """Individual turn in a conversation."""
    turn_id: str
    question: str
    response: str
    question_type: QuestionType
    analysis_mode: str
    sources_used: List[str]
    timestamp: datetime
    user_satisfaction: Optional[int] = None


@dataclass
class ExcelReport:
    """Excel report metadata and structure."""
    report_id: str
    filename: str
    file_path: str
    download_url: str
    sheets: List['ExcelSheet']
    created_at: datetime
    expires_at: datetime


@dataclass
class ExcelSheet:
    """Individual sheet within an Excel report."""
    name: str
    data: List[Dict[str, Any]]
    formatting: Dict[str, Any]
    charts: List[Dict[str, Any]]


@dataclass
class ReportTemplate:
    """Template for Excel report generation."""
    template_id: str
    name: str
    description: str
    sheet_definitions: List[Dict[str, Any]]
    formatting_rules: Dict[str, Any]
    chart_specifications: List[Dict[str, Any]]