"""
Document Index Manager for portfolio-level tracking and management.
Provides document indexing, relationship mapping, and searchable metadata storage.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class IndexEntry:
    """Document index entry with metadata"""
    document_id: str
    title: str
    document_type: str
    upload_date: datetime
    file_path: str
    parties: List[str]
    key_dates: List[Dict[str, Any]]
    risk_summary: Dict[str, Any]
    status: str  # "active", "expired", "terminated", "pending"
    tags: List[str]
    relationships: List[str]  # Related document IDs
    metadata: Dict[str, Any]
    last_updated: datetime

@dataclass
class DocumentRelationship:
    """Relationship between documents"""
    primary_document_id: str
    related_document_id: str
    relationship_type: str  # "amendment", "related", "supersedes", "references"
    description: str
    created_date: datetime

@dataclass
class Deadline:
    """Important deadline from documents"""
    document_id: str
    document_title: str
    deadline_date: datetime
    description: str
    deadline_type: str  # "expiration", "renewal", "payment", "delivery", "compliance"
    criticality: str  # "high", "medium", "low"
    status: str  # "upcoming", "overdue", "completed"
    days_remaining: int

@dataclass
class PortfolioSummary:
    """Summary of document portfolio"""
    total_documents: int
    document_type_breakdown: Dict[str, int]
    upcoming_deadlines: List[Deadline]
    high_risk_documents: List[str]
    portfolio_risk_score: float
    key_metrics: Dict[str, float]
    recommendations: List[str]
    last_updated: datetime

@dataclass
class SearchQuery:
    """Search query parameters"""
    text_query: Optional[str] = None
    document_type: Optional[str] = None
    parties: Optional[List[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 50

@dataclass
class FilterCriteria:
    """Filter criteria for portfolio analysis"""
    document_types: Optional[List[str]] = None
    risk_levels: Optional[List[str]] = None
    date_range: Optional[Tuple[datetime, datetime]] = None
    parties: Optional[List[str]] = None
    statuses: Optional[List[str]] = None

class DocumentIndexManager:
    """
    Manager for document indexing and portfolio-level tracking.
    Provides searchable metadata storage, relationship mapping, and deadline tracking.
    """
    
    def __init__(self, database_path: str = "data/database/document_index.db"):
        self.database_path = database_path
        self._ensure_database_exists()
        self._initialize_database()
    
    def _ensure_database_exists(self):
        """Ensure database directory exists"""
        db_path = Path(self.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Documents table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS documents (
                        document_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        document_type TEXT NOT NULL,
                        upload_date TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        parties TEXT,  -- JSON array
                        key_dates TEXT,  -- JSON array
                        risk_summary TEXT,  -- JSON object
                        status TEXT DEFAULT 'active',
                        tags TEXT,  -- JSON array
                        metadata TEXT,  -- JSON object
                        last_updated TEXT NOT NULL
                    )
                ''')
                
                # Relationships table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS document_relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        primary_document_id TEXT NOT NULL,
                        related_document_id TEXT NOT NULL,
                        relationship_type TEXT NOT NULL,
                        description TEXT,
                        created_date TEXT NOT NULL,
                        FOREIGN KEY (primary_document_id) REFERENCES documents (document_id),
                        FOREIGN KEY (related_document_id) REFERENCES documents (document_id)
                    )
                ''')
                
                # Deadlines table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS deadlines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        document_id TEXT NOT NULL,
                        deadline_date TEXT NOT NULL,
                        description TEXT NOT NULL,
                        deadline_type TEXT NOT NULL,
                        criticality TEXT DEFAULT 'medium',
                        status TEXT DEFAULT 'upcoming',
                        created_date TEXT NOT NULL,
                        FOREIGN KEY (document_id) REFERENCES documents (document_id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_type ON documents (document_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_status ON documents (status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents (upload_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_deadlines_date ON deadlines (deadline_date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_deadlines_status ON deadlines (status)')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_document_to_index(self, document_analysis: Any, 
                            classification_result: Any,
                            risk_analysis: Any,
                            file_path: str) -> IndexEntry:
        """Add a document to the index with full analysis results"""
        try:
            # Create index entry
            entry = IndexEntry(
                document_id=document_analysis.document_id,
                title=document_analysis.metadata.title,
                document_type=classification_result.document_type.value,
                upload_date=datetime.now(),
                file_path=file_path,
                parties=[party.name for party in document_analysis.key_information.parties],
                key_dates=self._format_key_dates(document_analysis.key_information.key_dates),
                risk_summary=self._create_risk_summary(risk_analysis),
                status=self._determine_document_status(document_analysis, risk_analysis),
                tags=self._generate_tags(document_analysis, classification_result),
                relationships=[],  # Will be populated separately
                metadata=self._create_metadata(document_analysis, classification_result),
                last_updated=datetime.now()
            )
            
            # Store in database
            self._store_document_entry(entry)
            
            # Add deadlines
            self._add_document_deadlines(entry)
            
            logger.info(f"Added document {entry.document_id} to index")
            return entry
            
        except Exception as e:
            logger.error(f"Error adding document to index: {str(e)}")
            raise
    
    def _format_key_dates(self, key_dates: List[Any]) -> List[Dict[str, Any]]:
        """Format key dates for storage"""
        formatted_dates = []
        for date_item in key_dates:
            formatted_dates.append({
                'date': date_item.date.isoformat(),
                'description': date_item.description,
                'type': date_item.date_type,
                'criticality': date_item.criticality
            })
        return formatted_dates
    
    def _create_risk_summary(self, risk_analysis: Any) -> Dict[str, Any]:
        """Create risk summary for indexing"""
        return {
            'overall_score': risk_analysis.overall_risk_score,
            'high_risks': len([
                risk for risks in risk_analysis.risk_categories.values()
                for risk in risks if risk.severity.value in ['high', 'critical']
            ]),
            'total_risks': sum(len(risks) for risks in risk_analysis.risk_categories.values()),
            'categories': {
                category.value: len(risks) 
                for category, risks in risk_analysis.risk_categories.items()
            },
            'confidence': risk_analysis.confidence_level
        }
    
    def _determine_document_status(self, analysis: Any, risk_analysis: Any) -> str:
        """Determine document status based on analysis"""
        # Check for expiration dates
        current_date = datetime.now()
        for date_item in analysis.key_information.key_dates:
            if date_item.date_type == 'expiration' and date_item.date < current_date:
                return 'expired'
            elif date_item.date_type == 'termination' and date_item.date < current_date:
                return 'terminated'
        
        # Check for high-risk status
        high_risks = [
            risk for risks in risk_analysis.risk_categories.values()
            for risk in risks if risk.severity.value == 'critical'
        ]
        if high_risks:
            return 'high_risk'
        
        return 'active'
    
    def _generate_tags(self, analysis: Any, classification: Any) -> List[str]:
        """Generate tags for the document"""
        tags = []
        
        # Add document type as tag
        tags.append(classification.document_type.value)
        
        # Add tags based on content
        content_lower = analysis.extracted_text.lower()
        
        tag_keywords = {
            'confidential': ['confidential', 'proprietary', 'trade secret'],
            'financial': ['payment', 'money', 'cost', 'price', 'financial'],
            'international': ['international', 'foreign', 'global', 'overseas'],
            'regulatory': ['regulatory', 'compliance', 'law', 'regulation'],
            'intellectual_property': ['patent', 'copyright', 'trademark', 'ip', 'intellectual property'],
            'termination': ['termination', 'terminate', 'end', 'expire'],
            'renewal': ['renewal', 'renew', 'extend', 'extension'],
            'high_value': [],  # Will be determined by financial analysis
            'multi_party': []  # Will be determined by party count
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                tags.append(tag)
        
        # High value tag based on financial terms
        if analysis.key_information.financial_terms:
            high_value_terms = [
                term for term in analysis.key_information.financial_terms
                if term.amount and term.amount > 100000
            ]
            if high_value_terms:
                tags.append('high_value')
        
        # Multi-party tag
        if len(analysis.key_information.parties) > 2:
            tags.append('multi_party')
        
        return list(set(tags))  # Remove duplicates
    
    def _create_metadata(self, analysis: Any, classification: Any) -> Dict[str, Any]:
        """Create metadata for the document"""
        return {
            'word_count': analysis.metadata.word_count,
            'page_count': analysis.metadata.page_count,
            'file_format': analysis.metadata.file_format,
            'classification_confidence': classification.confidence,
            'analysis_confidence': analysis.confidence_scores.get('overall', 0.0),
            'language': analysis.metadata.language,
            'party_count': len(analysis.key_information.parties),
            'financial_terms_count': len(analysis.key_information.financial_terms),
            'obligations_count': len(analysis.key_information.obligations),
            'key_dates_count': len(analysis.key_information.key_dates)
        }
    
    def _store_document_entry(self, entry: IndexEntry):
        """Store document entry in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO documents 
                    (document_id, title, document_type, upload_date, file_path, 
                     parties, key_dates, risk_summary, status, tags, metadata, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.document_id,
                    entry.title,
                    entry.document_type,
                    entry.upload_date.isoformat(),
                    entry.file_path,
                    json.dumps(entry.parties),
                    json.dumps(entry.key_dates),
                    json.dumps(entry.risk_summary),
                    entry.status,
                    json.dumps(entry.tags),
                    json.dumps(entry.metadata),
                    entry.last_updated.isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error storing document entry: {str(e)}")
            raise
    
    def _add_document_deadlines(self, entry: IndexEntry):
        """Add document deadlines to the deadlines table"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                for date_info in entry.key_dates:
                    cursor.execute('''
                        INSERT INTO deadlines 
                        (document_id, deadline_date, description, deadline_type, criticality, created_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        entry.document_id,
                        date_info['date'],
                        date_info['description'],
                        date_info['type'],
                        date_info['criticality'],
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error adding deadlines: {str(e)}")
    
    def update_document_relationships(self, document_id: str, 
                                    related_docs: List[Tuple[str, str, str]]) -> bool:
        """Update document relationships"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Remove existing relationships for this document
                cursor.execute('''
                    DELETE FROM document_relationships 
                    WHERE primary_document_id = ?
                ''', (document_id,))
                
                # Add new relationships
                for related_id, relationship_type, description in related_docs:
                    cursor.execute('''
                        INSERT INTO document_relationships 
                        (primary_document_id, related_document_id, relationship_type, description, created_date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        document_id,
                        related_id,
                        relationship_type,
                        description,
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating relationships: {str(e)}")
            return False
    
    def search_documents(self, query: SearchQuery) -> List[IndexEntry]:
        """Search documents based on query parameters"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Build SQL query
                sql_parts = ["SELECT * FROM documents WHERE 1=1"]
                params = []
                
                if query.text_query:
                    sql_parts.append("AND (title LIKE ? OR metadata LIKE ?)")
                    params.extend([f"%{query.text_query}%", f"%{query.text_query}%"])
                
                if query.document_type:
                    sql_parts.append("AND document_type = ?")
                    params.append(query.document_type)
                
                if query.status:
                    sql_parts.append("AND status = ?")
                    params.append(query.status)
                
                if query.date_range:
                    sql_parts.append("AND upload_date BETWEEN ? AND ?")
                    params.extend([query.date_range[0].isoformat(), query.date_range[1].isoformat()])
                
                if query.parties:
                    for party in query.parties:
                        sql_parts.append("AND parties LIKE ?")
                        params.append(f"%{party}%")
                
                if query.tags:
                    for tag in query.tags:
                        sql_parts.append("AND tags LIKE ?")
                        params.append(f"%{tag}%")
                
                sql_parts.append(f"ORDER BY last_updated DESC LIMIT {query.limit}")
                
                sql_query = " ".join(sql_parts)
                cursor.execute(sql_query, params)
                
                results = []
                for row in cursor.fetchall():
                    entry = self._row_to_index_entry(row)
                    results.append(entry)
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def _row_to_index_entry(self, row: Tuple) -> IndexEntry:
        """Convert database row to IndexEntry"""
        return IndexEntry(
            document_id=row[0],
            title=row[1],
            document_type=row[2],
            upload_date=datetime.fromisoformat(row[3]),
            file_path=row[4],
            parties=json.loads(row[5]) if row[5] else [],
            key_dates=json.loads(row[6]) if row[6] else [],
            risk_summary=json.loads(row[7]) if row[7] else {},
            status=row[8],
            tags=json.loads(row[9]) if row[9] else [],
            relationships=[],  # Would need separate query to populate
            metadata=json.loads(row[10]) if row[10] else {},
            last_updated=datetime.fromisoformat(row[11])
        )
    
    def get_upcoming_deadlines(self, timeframe: timedelta = timedelta(days=90)) -> List[Deadline]:
        """Get upcoming deadlines within specified timeframe"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                current_date = datetime.now()
                end_date = current_date + timeframe
                
                cursor.execute('''
                    SELECT d.*, doc.title 
                    FROM deadlines d
                    JOIN documents doc ON d.document_id = doc.document_id
                    WHERE d.deadline_date BETWEEN ? AND ?
                    AND d.status = 'upcoming'
                    ORDER BY d.deadline_date ASC
                ''', (current_date.isoformat(), end_date.isoformat()))
                
                deadlines = []
                for row in cursor.fetchall():
                    deadline_date = datetime.fromisoformat(row[2])
                    days_remaining = (deadline_date - current_date).days
                    
                    deadline = Deadline(
                        document_id=row[1],
                        document_title=row[7],  # From joined documents table
                        deadline_date=deadline_date,
                        description=row[3],
                        deadline_type=row[4],
                        criticality=row[5],
                        status='overdue' if days_remaining < 0 else 'upcoming',
                        days_remaining=days_remaining
                    )
                    deadlines.append(deadline)
                
                return deadlines
                
        except Exception as e:
            logger.error(f"Error getting upcoming deadlines: {str(e)}")
            return []
    
    def generate_portfolio_summary(self, filter_criteria: Optional[FilterCriteria] = None) -> PortfolioSummary:
        """Generate portfolio-level summary"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Build base query with filters
                where_clauses = []
                params = []
                
                if filter_criteria:
                    if filter_criteria.document_types:
                        placeholders = ','.join(['?' for _ in filter_criteria.document_types])
                        where_clauses.append(f"document_type IN ({placeholders})")
                        params.extend(filter_criteria.document_types)
                    
                    if filter_criteria.statuses:
                        placeholders = ','.join(['?' for _ in filter_criteria.statuses])
                        where_clauses.append(f"status IN ({placeholders})")
                        params.extend(filter_criteria.statuses)
                    
                    if filter_criteria.date_range:
                        where_clauses.append("upload_date BETWEEN ? AND ?")
                        params.extend([filter_criteria.date_range[0].isoformat(), 
                                     filter_criteria.date_range[1].isoformat()])
                
                where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                # Get total document count
                cursor.execute(f"SELECT COUNT(*) FROM documents {where_clause}", params)
                total_documents = cursor.fetchone()[0]
                
                # Get document type breakdown
                cursor.execute(f'''
                    SELECT document_type, COUNT(*) 
                    FROM documents {where_clause}
                    GROUP BY document_type
                ''', params)
                type_breakdown = dict(cursor.fetchall())
                
                # Get high-risk documents
                cursor.execute(f'''
                    SELECT document_id, title, risk_summary 
                    FROM documents {where_clause}
                ''', params)
                
                high_risk_docs = []
                total_risk_score = 0.0
                risk_count = 0
                
                for row in cursor.fetchall():
                    risk_summary = json.loads(row[2]) if row[2] else {}
                    risk_score = risk_summary.get('overall_score', 0.0)
                    
                    if risk_score > 0:
                        total_risk_score += risk_score
                        risk_count += 1
                    
                    if risk_summary.get('high_risks', 0) > 0:
                        high_risk_docs.append(row[0])  # document_id
                
                # Calculate portfolio risk score
                portfolio_risk_score = total_risk_score / risk_count if risk_count > 0 else 0.0
                
                # Get upcoming deadlines
                upcoming_deadlines = self.get_upcoming_deadlines(timedelta(days=30))
                
                # Calculate key metrics
                key_metrics = {
                    'average_risk_score': portfolio_risk_score,
                    'high_risk_percentage': len(high_risk_docs) / total_documents * 100 if total_documents > 0 else 0,
                    'upcoming_deadlines_30_days': len(upcoming_deadlines),
                    'documents_per_type': len(type_breakdown)
                }
                
                # Generate recommendations
                recommendations = self._generate_portfolio_recommendations(
                    total_documents, high_risk_docs, upcoming_deadlines, type_breakdown
                )
                
                return PortfolioSummary(
                    total_documents=total_documents,
                    document_type_breakdown=type_breakdown,
                    upcoming_deadlines=upcoming_deadlines[:10],  # Top 10 most urgent
                    high_risk_documents=high_risk_docs,
                    portfolio_risk_score=portfolio_risk_score,
                    key_metrics=key_metrics,
                    recommendations=recommendations,
                    last_updated=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Error generating portfolio summary: {str(e)}")
            return PortfolioSummary(
                total_documents=0,
                document_type_breakdown={},
                upcoming_deadlines=[],
                high_risk_documents=[],
                portfolio_risk_score=0.0,
                key_metrics={},
                recommendations=["Error generating portfolio summary"],
                last_updated=datetime.now()
            )
    
    def _generate_portfolio_recommendations(self, total_docs: int, high_risk_docs: List[str],
                                          upcoming_deadlines: List[Deadline],
                                          type_breakdown: Dict[str, int]) -> List[str]:
        """Generate portfolio-level recommendations"""
        recommendations = []
        
        if len(high_risk_docs) > total_docs * 0.2:  # More than 20% high risk
            recommendations.append("High proportion of risky documents - consider comprehensive risk review")
        
        if len(upcoming_deadlines) > 10:
            recommendations.append("Multiple upcoming deadlines - establish deadline monitoring system")
        
        overdue_deadlines = [d for d in upcoming_deadlines if d.days_remaining < 0]
        if overdue_deadlines:
            recommendations.append(f"{len(overdue_deadlines)} overdue deadlines require immediate attention")
        
        if len(type_breakdown) > 5:
            recommendations.append("Diverse document portfolio - consider specialized management approaches")
        
        if total_docs > 50:
            recommendations.append("Large document portfolio - consider automated monitoring and reporting")
        
        if not recommendations:
            recommendations.append("Portfolio appears well-managed - continue regular monitoring")
        
        return recommendations
    
    def get_document_relationships(self, document_id: str) -> List[DocumentRelationship]:
        """Get relationships for a specific document"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM document_relationships 
                    WHERE primary_document_id = ? OR related_document_id = ?
                ''', (document_id, document_id))
                
                relationships = []
                for row in cursor.fetchall():
                    relationship = DocumentRelationship(
                        primary_document_id=row[1],
                        related_document_id=row[2],
                        relationship_type=row[3],
                        description=row[4] or "",
                        created_date=datetime.fromisoformat(row[5])
                    )
                    relationships.append(relationship)
                
                return relationships
                
        except Exception as e:
            logger.error(f"Error getting document relationships: {str(e)}")
            return []
    
    def update_document_status(self, document_id: str, new_status: str) -> bool:
        """Update document status"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE documents 
                    SET status = ?, last_updated = ?
                    WHERE document_id = ?
                ''', (new_status, datetime.now().isoformat(), document_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error updating document status: {str(e)}")
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document from index"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Delete from all related tables
                cursor.execute('DELETE FROM deadlines WHERE document_id = ?', (document_id,))
                cursor.execute('DELETE FROM document_relationships WHERE primary_document_id = ? OR related_document_id = ?', 
                             (document_id, document_id))
                cursor.execute('DELETE FROM documents WHERE document_id = ?', (document_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False