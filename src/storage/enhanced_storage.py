"""Enhanced storage service for new Q&A capabilities."""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import sqlite3

from src.models.document import (
    ComprehensiveAnalysis, RiskAssessment, Commitment, DeliverableDate, AnalysisTemplate
)
from src.models.conversational import (
    ConversationContext, ConversationTurn, ExcelReport, ExcelSheet
)
from src.storage.database import db_manager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedDocumentStorage:
    """Enhanced storage service for new Q&A capabilities."""
    
    def __init__(self):
        self.db_manager = db_manager
    
    # Comprehensive Analysis Operations
    
    def save_comprehensive_analysis(self, analysis: ComprehensiveAnalysis) -> str:
        """Save comprehensive analysis to database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Save main analysis record
                cursor.execute("""
                    INSERT OR REPLACE INTO comprehensive_analysis (
                        analysis_id, document_id, document_overview, key_findings,
                        critical_information, recommended_actions, executive_recommendation,
                        key_legal_terms, template_used, confidence_score, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis.analysis_id, analysis.document_id, analysis.document_overview,
                    json.dumps(analysis.key_findings), json.dumps(analysis.critical_information),
                    json.dumps(analysis.recommended_actions), analysis.executive_recommendation,
                    json.dumps(analysis.key_legal_terms), analysis.template_used,
                    analysis.confidence_score, analysis.created_at.isoformat()
                ))
                
                # Save risks
                for risk in analysis.risks:
                    self._save_risk_assessment(cursor, risk, analysis.analysis_id)
                
                # Save commitments
                for commitment in analysis.commitments:
                    self._save_commitment(cursor, commitment, analysis.analysis_id)
                
                # Save deliverable dates
                for date in analysis.deliverable_dates:
                    self._save_deliverable_date(cursor, date, analysis.analysis_id)
                
                conn.commit()
                logger.info(f"Saved comprehensive analysis: {analysis.analysis_id}")
                return analysis.analysis_id
                
        except Exception as e:
            logger.error(f"Error saving comprehensive analysis: {e}")
            raise
    
    def get_comprehensive_analysis(self, analysis_id: str) -> Optional[ComprehensiveAnalysis]:
        """Retrieve comprehensive analysis by ID."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get main analysis record
                cursor.execute("""
                    SELECT * FROM comprehensive_analysis WHERE analysis_id = ?
                """, (analysis_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                analysis_dict = dict(row)
                
                # Get related data
                risks = self._get_risks_for_analysis(cursor, analysis_id)
                commitments = self._get_commitments_for_analysis(cursor, analysis_id)
                dates = self._get_dates_for_analysis(cursor, analysis_id)
                
                # Reconstruct analysis object
                return ComprehensiveAnalysis(
                    document_id=analysis_dict['document_id'],
                    analysis_id=analysis_dict['analysis_id'],
                    document_overview=analysis_dict['document_overview'],
                    key_findings=json.loads(analysis_dict['key_findings'] or '[]'),
                    critical_information=json.loads(analysis_dict['critical_information'] or '[]'),
                    recommended_actions=json.loads(analysis_dict['recommended_actions'] or '[]'),
                    executive_recommendation=analysis_dict['executive_recommendation'],
                    key_legal_terms=json.loads(analysis_dict['key_legal_terms'] or '[]'),
                    risks=risks,
                    commitments=commitments,
                    deliverable_dates=dates,
                    template_used=analysis_dict['template_used'],
                    confidence_score=analysis_dict['confidence_score'],
                    created_at=datetime.fromisoformat(analysis_dict['created_at'])
                )
                
        except Exception as e:
            logger.error(f"Error retrieving comprehensive analysis: {e}")
            return None
    
    def get_document_analysis(self, document_id: str) -> Optional[ComprehensiveAnalysis]:
        """Get the latest comprehensive analysis for a document."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT analysis_id FROM comprehensive_analysis 
                    WHERE document_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (document_id,))
                
                row = cursor.fetchone()
                if row:
                    return self.get_comprehensive_analysis(row[0])
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting document analysis: {e}")
            return None
    
    # Risk Assessment Operations
    
    def _save_risk_assessment(self, cursor: sqlite3.Cursor, risk: RiskAssessment, analysis_id: str):
        """Save risk assessment to database."""
        cursor.execute("""
            INSERT OR REPLACE INTO risk_assessments (
                risk_id, document_id, analysis_id, description, severity, category,
                affected_parties, mitigation_suggestions, source_text, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            risk.risk_id, risk.risk_id.split('_')[0], analysis_id, risk.description,
            risk.severity, risk.category, json.dumps(risk.affected_parties),
            json.dumps(risk.mitigation_suggestions), risk.source_text, risk.confidence
        ))
    
    def _get_risks_for_analysis(self, cursor: sqlite3.Cursor, analysis_id: str) -> List[RiskAssessment]:
        """Get all risks for an analysis."""
        cursor.execute("""
            SELECT * FROM risk_assessments WHERE analysis_id = ?
        """, (analysis_id,))
        
        risks = []
        for row in cursor.fetchall():
            risk_dict = dict(row)
            risks.append(RiskAssessment(
                risk_id=risk_dict['risk_id'],
                description=risk_dict['description'],
                severity=risk_dict['severity'],
                category=risk_dict['category'],
                affected_parties=json.loads(risk_dict['affected_parties'] or '[]'),
                mitigation_suggestions=json.loads(risk_dict['mitigation_suggestions'] or '[]'),
                source_text=risk_dict['source_text'],
                confidence=risk_dict['confidence']
            ))
        
        return risks
    
    def get_document_risks(self, document_id: str, severity_filter: Optional[str] = None) -> List[RiskAssessment]:
        """Get all risks for a document, optionally filtered by severity."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if severity_filter:
                    cursor.execute("""
                        SELECT * FROM risk_assessments 
                        WHERE document_id = ? AND severity = ?
                        ORDER BY created_at DESC
                    """, (document_id, severity_filter))
                else:
                    cursor.execute("""
                        SELECT * FROM risk_assessments 
                        WHERE document_id = ?
                        ORDER BY created_at DESC
                    """, (document_id,))
                
                risks = []
                for row in cursor.fetchall():
                    risk_dict = dict(row)
                    risks.append(RiskAssessment(
                        risk_id=risk_dict['risk_id'],
                        description=risk_dict['description'],
                        severity=risk_dict['severity'],
                        category=risk_dict['category'],
                        affected_parties=json.loads(risk_dict['affected_parties'] or '[]'),
                        mitigation_suggestions=json.loads(risk_dict['mitigation_suggestions'] or '[]'),
                        source_text=risk_dict['source_text'],
                        confidence=risk_dict['confidence']
                    ))
                
                return risks
                
        except Exception as e:
            logger.error(f"Error getting document risks: {e}")
            return []
    
    # Commitment Operations
    
    def _save_commitment(self, cursor: sqlite3.Cursor, commitment: Commitment, analysis_id: str):
        """Save commitment to database."""
        cursor.execute("""
            INSERT OR REPLACE INTO commitments (
                commitment_id, document_id, analysis_id, description, obligated_party,
                beneficiary_party, deadline, status, commitment_type, source_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            commitment.commitment_id, commitment.commitment_id.split('_')[0], analysis_id,
            commitment.description, commitment.obligated_party, commitment.beneficiary_party,
            commitment.deadline.isoformat() if commitment.deadline else None,
            commitment.status, commitment.commitment_type, commitment.source_text
        ))
    
    def _get_commitments_for_analysis(self, cursor: sqlite3.Cursor, analysis_id: str) -> List[Commitment]:
        """Get all commitments for an analysis."""
        cursor.execute("""
            SELECT * FROM commitments WHERE analysis_id = ?
        """, (analysis_id,))
        
        commitments = []
        for row in cursor.fetchall():
            commitment_dict = dict(row)
            commitments.append(Commitment(
                commitment_id=commitment_dict['commitment_id'],
                description=commitment_dict['description'],
                obligated_party=commitment_dict['obligated_party'],
                beneficiary_party=commitment_dict['beneficiary_party'],
                deadline=datetime.fromisoformat(commitment_dict['deadline']) if commitment_dict['deadline'] else None,
                status=commitment_dict['status'],
                source_text=commitment_dict['source_text'],
                commitment_type=commitment_dict['commitment_type']
            ))
        
        return commitments
    
    def get_document_commitments(self, document_id: str, status_filter: Optional[str] = None) -> List[Commitment]:
        """Get all commitments for a document, optionally filtered by status."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if status_filter:
                    cursor.execute("""
                        SELECT * FROM commitments 
                        WHERE document_id = ? AND status = ?
                        ORDER BY deadline ASC
                    """, (document_id, status_filter))
                else:
                    cursor.execute("""
                        SELECT * FROM commitments 
                        WHERE document_id = ?
                        ORDER BY deadline ASC
                    """, (document_id,))
                
                commitments = []
                for row in cursor.fetchall():
                    commitment_dict = dict(row)
                    commitments.append(Commitment(
                        commitment_id=commitment_dict['commitment_id'],
                        description=commitment_dict['description'],
                        obligated_party=commitment_dict['obligated_party'],
                        beneficiary_party=commitment_dict['beneficiary_party'],
                        deadline=datetime.fromisoformat(commitment_dict['deadline']) if commitment_dict['deadline'] else None,
                        status=commitment_dict['status'],
                        source_text=commitment_dict['source_text'],
                        commitment_type=commitment_dict['commitment_type']
                    ))
                
                return commitments
                
        except Exception as e:
            logger.error(f"Error getting document commitments: {e}")
            return []
    
    # Deliverable Date Operations
    
    def _save_deliverable_date(self, cursor: sqlite3.Cursor, date: DeliverableDate, analysis_id: str):
        """Save deliverable date to database."""
        cursor.execute("""
            INSERT INTO deliverable_dates (
                document_id, analysis_id, date, description, responsible_party,
                deliverable_type, status, source_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id.split('_')[0], analysis_id, date.date.isoformat(),
            date.description, date.responsible_party, date.deliverable_type,
            date.status, date.source_text
        ))
    
    def _get_dates_for_analysis(self, cursor: sqlite3.Cursor, analysis_id: str) -> List[DeliverableDate]:
        """Get all deliverable dates for an analysis."""
        cursor.execute("""
            SELECT * FROM deliverable_dates WHERE analysis_id = ? ORDER BY date ASC
        """, (analysis_id,))
        
        dates = []
        for row in cursor.fetchall():
            date_dict = dict(row)
            dates.append(DeliverableDate(
                date=datetime.fromisoformat(date_dict['date']),
                description=date_dict['description'],
                responsible_party=date_dict['responsible_party'],
                deliverable_type=date_dict['deliverable_type'],
                status=date_dict['status'],
                source_text=date_dict['source_text']
            ))
        
        return dates
    
    def get_document_dates(self, document_id: str, upcoming_only: bool = False) -> List[DeliverableDate]:
        """Get all deliverable dates for a document."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if upcoming_only:
                    cursor.execute("""
                        SELECT * FROM deliverable_dates 
                        WHERE document_id = ? AND date > ?
                        ORDER BY date ASC
                    """, (document_id, datetime.now().isoformat()))
                else:
                    cursor.execute("""
                        SELECT * FROM deliverable_dates 
                        WHERE document_id = ?
                        ORDER BY date ASC
                    """, (document_id,))
                
                dates = []
                for row in cursor.fetchall():
                    date_dict = dict(row)
                    dates.append(DeliverableDate(
                        date=datetime.fromisoformat(date_dict['date']),
                        description=date_dict['description'],
                        responsible_party=date_dict['responsible_party'],
                        deliverable_type=date_dict['deliverable_type'],
                        status=date_dict['status'],
                        source_text=date_dict['source_text']
                    ))
                
                return dates
                
        except Exception as e:
            logger.error(f"Error getting document dates: {e}")
            return []
    
    # Analysis Template Operations
    
    def save_analysis_template(self, template: AnalysisTemplate) -> str:
        """Save analysis template to database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO analysis_templates (
                        template_id, name, description, document_types, analysis_sections,
                        custom_prompts, parameters, created_by, version, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    template.template_id, template.name, template.description,
                    json.dumps(template.document_types), json.dumps(template.analysis_sections),
                    json.dumps(template.custom_prompts), json.dumps(template.parameters),
                    template.created_by, template.version, template.is_active
                ))
                
                conn.commit()
                logger.info(f"Saved analysis template: {template.template_id}")
                return template.template_id
                
        except Exception as e:
            logger.error(f"Error saving analysis template: {e}")
            raise
    
    def get_analysis_template(self, template_id: str) -> Optional[AnalysisTemplate]:
        """Retrieve analysis template by ID."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM analysis_templates WHERE template_id = ?
                """, (template_id,))
                
                row = cursor.fetchone()
                if row:
                    template_dict = dict(row)
                    return AnalysisTemplate(
                        template_id=template_dict['template_id'],
                        name=template_dict['name'],
                        description=template_dict['description'],
                        document_types=json.loads(template_dict['document_types'] or '[]'),
                        analysis_sections=json.loads(template_dict['analysis_sections'] or '[]'),
                        custom_prompts=json.loads(template_dict['custom_prompts'] or '{}'),
                        parameters=json.loads(template_dict['parameters'] or '{}'),
                        created_by=template_dict['created_by'],
                        version=template_dict['version'],
                        is_active=template_dict['is_active'],
                        created_at=datetime.fromisoformat(template_dict['created_at'])
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving analysis template: {e}")
            return None
    
    def list_analysis_templates(self, active_only: bool = True) -> List[AnalysisTemplate]:
        """List all analysis templates."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if active_only:
                    cursor.execute("""
                        SELECT * FROM analysis_templates 
                        WHERE is_active = TRUE
                        ORDER BY name ASC
                    """)
                else:
                    cursor.execute("""
                        SELECT * FROM analysis_templates 
                        ORDER BY name ASC
                    """)
                
                templates = []
                for row in cursor.fetchall():
                    template_dict = dict(row)
                    templates.append(AnalysisTemplate(
                        template_id=template_dict['template_id'],
                        name=template_dict['name'],
                        description=template_dict['description'],
                        document_types=json.loads(template_dict['document_types'] or '[]'),
                        analysis_sections=json.loads(template_dict['analysis_sections'] or '[]'),
                        custom_prompts=json.loads(template_dict['custom_prompts'] or '{}'),
                        parameters=json.loads(template_dict['parameters'] or '{}'),
                        created_by=template_dict['created_by'],
                        version=template_dict['version'],
                        is_active=template_dict['is_active'],
                        created_at=datetime.fromisoformat(template_dict['created_at'])
                    ))
                
                return templates
                
        except Exception as e:
            logger.error(f"Error listing analysis templates: {e}")
            return []
    
    # Conversation Context Operations
    
    def save_conversation_context(self, context: ConversationContext) -> str:
        """Save conversation context to database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO conversation_contexts (
                        session_id, document_id, current_topic, analysis_mode,
                        user_preferences, context_summary, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    context.session_id, context.document_id, context.current_topic,
                    context.analysis_mode, json.dumps(context.user_preferences),
                    context.context_summary, datetime.now().isoformat()
                ))
                
                conn.commit()
                return context.session_id
                
        except Exception as e:
            logger.error(f"Error saving conversation context: {e}")
            raise
    
    def get_conversation_context(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation context by session ID."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM conversation_contexts WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    context_dict = dict(row)
                    return ConversationContext(
                        session_id=context_dict['session_id'],
                        document_id=context_dict['document_id'],
                        conversation_history=[],  # Would need separate table for full history
                        current_topic=context_dict['current_topic'],
                        analysis_mode=context_dict['analysis_mode'],
                        user_preferences=json.loads(context_dict['user_preferences'] or '{}'),
                        context_summary=context_dict['context_summary']
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving conversation context: {e}")
            return None
    
    # Excel Report Operations
    
    def save_excel_report(self, report: ExcelReport) -> str:
        """Save Excel report metadata to database."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Extract document IDs from sheets or other metadata
                document_ids = []  # This would be populated based on report content
                
                cursor.execute("""
                    INSERT INTO excel_reports (
                        report_id, filename, file_path, download_url, report_type,
                        document_ids, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report.report_id, report.filename, report.file_path,
                    report.download_url, "comprehensive", json.dumps(document_ids),
                    report.created_at.isoformat(), report.expires_at.isoformat()
                ))
                
                conn.commit()
                return report.report_id
                
        except Exception as e:
            logger.error(f"Error saving Excel report: {e}")
            raise
    
    def get_excel_report(self, report_id: str) -> Optional[ExcelReport]:
        """Retrieve Excel report by ID."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM excel_reports WHERE report_id = ?
                """, (report_id,))
                
                row = cursor.fetchone()
                if row:
                    report_dict = dict(row)
                    return ExcelReport(
                        report_id=report_dict['report_id'],
                        filename=report_dict['filename'],
                        file_path=report_dict['file_path'],
                        download_url=report_dict['download_url'],
                        sheets=[],  # Would need to reconstruct from file
                        created_at=datetime.fromisoformat(report_dict['created_at']),
                        expires_at=datetime.fromisoformat(report_dict['expires_at'])
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving Excel report: {e}")
            return None
    
    def cleanup_expired_reports(self) -> int:
        """Clean up expired Excel reports."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get expired reports
                cursor.execute("""
                    SELECT report_id, file_path FROM excel_reports 
                    WHERE expires_at < ?
                """, (datetime.now().isoformat(),))
                
                expired_reports = cursor.fetchall()
                
                # Delete files and database records
                import os
                deleted_count = 0
                
                for report_id, file_path in expired_reports:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        
                        cursor.execute("""
                            DELETE FROM excel_reports WHERE report_id = ?
                        """, (report_id,))
                        
                        deleted_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to delete report {report_id}: {e}")
                
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} expired reports")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error cleaning up expired reports: {e}")
            return 0


# Global enhanced storage instance
enhanced_storage = EnhancedDocumentStorage()