"""Data models for the Document Q&A System."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


@dataclass
class Document:
    """Document model representing a processed document."""
    
    id: str
    title: str
    file_type: str
    file_size: int
    upload_timestamp: datetime
    processing_status: str = "pending"
    original_text: Optional[str] = None
    document_type: Optional[str] = None
    extracted_info: Optional[Dict[str, Any]] = None
    analysis: Optional[str] = None
    summary: Optional[str] = None
    embeddings: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    # Enhanced fields for legal documents
    is_legal_document: bool = False
    legal_document_type: Optional[str] = None  # "MTA", "NDA", "Service Agreement", etc.
    contract_parties: Optional[List[str]] = None
    key_legal_terms: Optional[List[str]] = None
    legal_analysis_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for storage."""
        return {
            'id': self.id,
            'title': self.title,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'upload_timestamp': self.upload_timestamp.isoformat(),
            'processing_status': self.processing_status,
            'original_text': self.original_text,
            'document_type': self.document_type,
            'extracted_info': json.dumps(self.extracted_info) if self.extracted_info else None,
            'analysis': self.analysis,
            'summary': self.summary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_legal_document': self.is_legal_document,
            'legal_document_type': self.legal_document_type,
            'contract_parties': json.dumps(self.contract_parties) if self.contract_parties else None,
            'key_legal_terms': json.dumps(self.key_legal_terms) if self.key_legal_terms else None,
            'legal_analysis_confidence': self.legal_analysis_confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary."""
        return cls(
            id=data['id'],
            title=data['title'],
            file_type=data['file_type'],
            file_size=data['file_size'],
            upload_timestamp=datetime.fromisoformat(data['upload_timestamp']),
            processing_status=data.get('processing_status', 'pending'),
            original_text=data.get('original_text'),
            document_type=data.get('document_type'),
            extracted_info=json.loads(data['extracted_info']) if data.get('extracted_info') else None,
            analysis=data.get('analysis'),
            summary=data.get('summary'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
            is_legal_document=data.get('is_legal_document', False),
            legal_document_type=data.get('legal_document_type'),
            contract_parties=json.loads(data['contract_parties']) if data.get('contract_parties') else None,
            key_legal_terms=json.loads(data['key_legal_terms']) if data.get('key_legal_terms') else None,
            legal_analysis_confidence=data.get('legal_analysis_confidence', 0.0)
        )


@dataclass
class ProcessingJob:
    """Processing job model for tracking document processing."""
    
    job_id: str
    document_id: str
    status: str = "pending"  # pending, processing, completed, failed
    current_step: Optional[str] = None
    progress_percentage: int = 0
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert processing job to dictionary for storage."""
        return {
            'job_id': self.job_id,
            'document_id': self.document_id,
            'status': self.status,
            'current_step': self.current_step,
            'progress_percentage': self.progress_percentage,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingJob':
        """Create processing job from dictionary."""
        return cls(
            job_id=data['job_id'],
            document_id=data['document_id'],
            status=data.get('status', 'pending'),
            current_step=data.get('current_step'),
            progress_percentage=data.get('progress_percentage', 0),
            error_message=data.get('error_message'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None
        )


@dataclass
class QASession:
    """Q&A session model for managing document queries."""
    
    session_id: str
    document_id: str
    questions: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_interaction(self, question: str, answer: str, sources: Optional[List[str]] = None):
        """Add a question-answer interaction to the session."""
        interaction = {
            'question': question,
            'answer': answer,
            'sources': sources or [],
            'timestamp': datetime.now().isoformat()
        }
        self.questions.append(interaction)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Q&A session to dictionary for storage."""
        return {
            'session_id': self.session_id,
            'document_id': self.document_id,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QASession':
        """Create Q&A session from dictionary."""
        return cls(
            session_id=data['session_id'],
            document_id=data['document_id'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        )


@dataclass
class ContractAnalysisSession(QASession):
    """Enhanced QA session for legal document analysis."""
    analysis_mode: str = "contract"  # "contract" or "standard"
    legal_document_type: Optional[str] = None
    structured_responses: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_contract_interaction(self, question: str, structured_response: Dict[str, str], sources: Optional[List[str]] = None):
        """Add a contract analysis interaction to the session."""
        interaction = {
            'question': question,
            'structured_response': structured_response,
            'sources': sources or [],
            'timestamp': datetime.now().isoformat(),
            'analysis_mode': self.analysis_mode
        }
        self.questions.append(interaction)
        self.structured_responses.append(structured_response)


@dataclass
class QAInteraction:
    """Individual Q&A interaction model."""
    
    id: Optional[int]
    session_id: str
    question: str
    answer: str
    sources: Optional[List[str]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Q&A interaction to dictionary for storage."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question': self.question,
            'answer': self.answer,
            'sources': json.dumps(self.sources) if self.sources else None,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QAInteraction':
        """Create Q&A interaction from dictionary."""
        return cls(
            id=data.get('id'),
            session_id=data['session_id'],
            question=data['question'],
            answer=data['answer'],
            sources=json.loads(data['sources']) if data.get('sources') else None,
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else datetime.now()
        )


# Enhanced Analysis Data Models

@dataclass
class RiskAssessment:
    """Risk assessment model for document analysis."""
    
    risk_id: str
    description: str
    severity: str  # High, Medium, Low
    category: str  # Legal, Financial, Operational, etc.
    affected_parties: List[str]
    mitigation_suggestions: List[str]
    source_text: str
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'risk_id': self.risk_id,
            'description': self.description,
            'severity': self.severity,
            'category': self.category,
            'affected_parties': json.dumps(self.affected_parties),
            'mitigation_suggestions': json.dumps(self.mitigation_suggestions),
            'source_text': self.source_text,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskAssessment':
        """Create from dictionary."""
        return cls(
            risk_id=data['risk_id'],
            description=data['description'],
            severity=data['severity'],
            category=data['category'],
            affected_parties=json.loads(data['affected_parties']) if data.get('affected_parties') else [],
            mitigation_suggestions=json.loads(data['mitigation_suggestions']) if data.get('mitigation_suggestions') else [],
            source_text=data['source_text'],
            confidence=data['confidence']
        )


@dataclass
class Commitment:
    """Commitment model for tracking obligations in documents."""
    
    commitment_id: str
    description: str
    obligated_party: str
    beneficiary_party: str
    deadline: Optional[datetime]
    status: str  # Active, Completed, Overdue
    source_text: str
    commitment_type: str  # Deliverable, Payment, Action, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'commitment_id': self.commitment_id,
            'description': self.description,
            'obligated_party': self.obligated_party,
            'beneficiary_party': self.beneficiary_party,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'source_text': self.source_text,
            'commitment_type': self.commitment_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Commitment':
        """Create from dictionary."""
        return cls(
            commitment_id=data['commitment_id'],
            description=data['description'],
            obligated_party=data['obligated_party'],
            beneficiary_party=data['beneficiary_party'],
            deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
            status=data['status'],
            source_text=data['source_text'],
            commitment_type=data['commitment_type']
        )


@dataclass
class DeliverableDate:
    """Deliverable date model for tracking important dates."""
    
    date: datetime
    description: str
    responsible_party: str
    deliverable_type: str
    status: str
    source_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'date': self.date.isoformat(),
            'description': self.description,
            'responsible_party': self.responsible_party,
            'deliverable_type': self.deliverable_type,
            'status': self.status,
            'source_text': self.source_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeliverableDate':
        """Create from dictionary."""
        return cls(
            date=datetime.fromisoformat(data['date']),
            description=data['description'],
            responsible_party=data['responsible_party'],
            deliverable_type=data['deliverable_type'],
            status=data['status'],
            source_text=data['source_text']
        )


@dataclass
class AnalysisTemplate:
    """Template model for customizable document analysis."""
    
    template_id: str
    name: str
    description: str
    document_types: List[str]
    analysis_sections: List[str]
    custom_prompts: Dict[str, str]
    parameters: Dict[str, Any]
    created_by: str
    version: str
    is_active: bool
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'document_types': json.dumps(self.document_types),
            'analysis_sections': json.dumps(self.analysis_sections),
            'custom_prompts': json.dumps(self.custom_prompts),
            'parameters': json.dumps(self.parameters),
            'created_by': self.created_by,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisTemplate':
        """Create from dictionary."""
        return cls(
            template_id=data['template_id'],
            name=data['name'],
            description=data['description'],
            document_types=json.loads(data['document_types']) if data.get('document_types') else [],
            analysis_sections=json.loads(data['analysis_sections']) if data.get('analysis_sections') else [],
            custom_prompts=json.loads(data['custom_prompts']) if data.get('custom_prompts') else {},
            parameters=json.loads(data['parameters']) if data.get('parameters') else {},
            created_by=data['created_by'],
            version=data['version'],
            is_active=data['is_active'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        )


@dataclass
class ComprehensiveAnalysis:
    """Comprehensive analysis model containing all enhanced analysis results."""
    
    document_id: str
    analysis_id: str
    document_overview: str
    key_findings: List[str]
    critical_information: List[str]
    recommended_actions: List[str]
    executive_recommendation: str
    key_legal_terms: List[str]
    risks: List[RiskAssessment]
    commitments: List[Commitment]
    deliverable_dates: List[DeliverableDate]
    template_used: Optional[str]
    confidence_score: float
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'document_id': self.document_id,
            'analysis_id': self.analysis_id,
            'document_overview': self.document_overview,
            'key_findings': json.dumps(self.key_findings),
            'critical_information': json.dumps(self.critical_information),
            'recommended_actions': json.dumps(self.recommended_actions),
            'executive_recommendation': self.executive_recommendation,
            'key_legal_terms': json.dumps(self.key_legal_terms),
            'risks': json.dumps([risk.to_dict() for risk in self.risks]),
            'commitments': json.dumps([commitment.to_dict() for commitment in self.commitments]),
            'deliverable_dates': json.dumps([date.to_dict() for date in self.deliverable_dates]),
            'template_used': self.template_used,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComprehensiveAnalysis':
        """Create from dictionary."""
        risks_data = json.loads(data.get('risks', '[]'))
        commitments_data = json.loads(data.get('commitments', '[]'))
        dates_data = json.loads(data.get('deliverable_dates', '[]'))
        
        return cls(
            document_id=data['document_id'],
            analysis_id=data['analysis_id'],
            document_overview=data['document_overview'],
            key_findings=json.loads(data.get('key_findings', '[]')),
            critical_information=json.loads(data.get('critical_information', '[]')),
            recommended_actions=json.loads(data.get('recommended_actions', '[]')),
            executive_recommendation=data['executive_recommendation'],
            key_legal_terms=json.loads(data.get('key_legal_terms', '[]')),
            risks=[RiskAssessment.from_dict(risk) for risk in risks_data],
            commitments=[Commitment.from_dict(commitment) for commitment in commitments_data],
            deliverable_dates=[DeliverableDate.from_dict(date) for date in dates_data],
            template_used=data.get('template_used'),
            confidence_score=data['confidence_score'],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        )