"""Database migration scripts for enhanced Q&A capabilities."""

import sqlite3
import logging
from typing import List, Dict, Any
from src.storage.database import db_manager
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseMigrator:
    """Handles database schema migrations for enhanced features."""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def run_migrations(self) -> bool:
        """Run all pending migrations."""
        try:
            with self.db_manager.get_connection() as conn:
                # Create migrations tracking table if it doesn't exist
                self._create_migrations_table(conn)
                
                # Get applied migrations
                applied_migrations = self._get_applied_migrations(conn)
                
                # Define all migrations
                migrations = [
                    {
                        'id': '001_add_legal_document_fields',
                        'description': 'Add legal document fields to documents table',
                        'sql': self._migration_001_legal_fields()
                    },
                    {
                        'id': '002_enhance_qa_sessions',
                        'description': 'Add analysis mode to Q&A sessions',
                        'sql': self._migration_002_enhance_qa_sessions()
                    },
                    {
                        'id': '003_enhance_qa_interactions',
                        'description': 'Add structured response fields to Q&A interactions',
                        'sql': self._migration_003_enhance_qa_interactions()
                    },
                    {
                        'id': '004_create_enhanced_tables',
                        'description': 'Create new tables for enhanced analysis',
                        'sql': self._migration_004_create_enhanced_tables()
                    }
                ]
                
                # Apply pending migrations
                for migration in migrations:
                    if migration['id'] not in applied_migrations:
                        logger.info(f"Applying migration: {migration['id']} - {migration['description']}")
                        self._apply_migration(conn, migration)
                
                logger.info("All migrations completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def _create_migrations_table(self, conn: sqlite3.Connection):
        """Create migrations tracking table."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                migration_id TEXT PRIMARY KEY,
                description TEXT,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    
    def _get_applied_migrations(self, conn: sqlite3.Connection) -> List[str]:
        """Get list of applied migration IDs."""
        cursor = conn.cursor()
        cursor.execute("SELECT migration_id FROM schema_migrations")
        return [row[0] for row in cursor.fetchall()]
    
    def _apply_migration(self, conn: sqlite3.Connection, migration: Dict[str, Any]):
        """Apply a single migration."""
        try:
            # Execute migration SQL
            for sql_statement in migration['sql']:
                conn.execute(sql_statement)
            
            # Record migration as applied
            conn.execute("""
                INSERT INTO schema_migrations (migration_id, description)
                VALUES (?, ?)
            """, (migration['id'], migration['description']))
            
            conn.commit()
            logger.info(f"Migration {migration['id']} applied successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to apply migration {migration['id']}: {e}")
            raise
    
    def _migration_001_legal_fields(self) -> List[str]:
        """Add legal document fields to documents table."""
        return [
            """
            ALTER TABLE documents ADD COLUMN is_legal_document BOOLEAN DEFAULT FALSE
            """,
            """
            ALTER TABLE documents ADD COLUMN legal_document_type TEXT
            """,
            """
            ALTER TABLE documents ADD COLUMN contract_parties TEXT
            """,
            """
            ALTER TABLE documents ADD COLUMN key_legal_terms TEXT
            """,
            """
            ALTER TABLE documents ADD COLUMN legal_analysis_confidence REAL DEFAULT 0.0
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_documents_legal ON documents (is_legal_document)
            """
        ]
    
    def _migration_002_enhance_qa_sessions(self) -> List[str]:
        """Add analysis mode to Q&A sessions."""
        return [
            """
            ALTER TABLE qa_sessions ADD COLUMN analysis_mode TEXT DEFAULT 'standard'
            """,
            """
            ALTER TABLE qa_sessions ADD COLUMN legal_document_type TEXT
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_qa_sessions_mode ON qa_sessions (analysis_mode)
            """
        ]
    
    def _migration_003_enhance_qa_interactions(self) -> List[str]:
        """Add structured response fields to Q&A interactions."""
        return [
            """
            ALTER TABLE qa_interactions ADD COLUMN analysis_mode TEXT DEFAULT 'standard'
            """,
            """
            ALTER TABLE qa_interactions ADD COLUMN structured_response TEXT
            """,
            """
            ALTER TABLE qa_interactions ADD COLUMN legal_terms_found TEXT
            """,
            """
            ALTER TABLE qa_interactions ADD COLUMN confidence REAL DEFAULT 0.0
            """
        ]
    
    def _migration_004_create_enhanced_tables(self) -> List[str]:
        """Create new tables for enhanced analysis features."""
        return [
            """
            CREATE TABLE IF NOT EXISTS comprehensive_analysis (
                analysis_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                document_overview TEXT,
                key_findings TEXT,
                critical_information TEXT,
                recommended_actions TEXT,
                executive_recommendation TEXT,
                key_legal_terms TEXT,
                template_used TEXT,
                confidence_score REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS risk_assessments (
                risk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                analysis_id TEXT,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                category TEXT NOT NULL,
                affected_parties TEXT,
                mitigation_suggestions TEXT,
                source_text TEXT,
                confidence REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
                FOREIGN KEY (analysis_id) REFERENCES comprehensive_analysis (analysis_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS commitments (
                commitment_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                analysis_id TEXT,
                description TEXT NOT NULL,
                obligated_party TEXT,
                beneficiary_party TEXT,
                deadline DATETIME,
                status TEXT DEFAULT 'Active',
                commitment_type TEXT,
                source_text TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
                FOREIGN KEY (analysis_id) REFERENCES comprehensive_analysis (analysis_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS deliverable_dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                analysis_id TEXT,
                date DATETIME NOT NULL,
                description TEXT NOT NULL,
                responsible_party TEXT,
                deliverable_type TEXT,
                status TEXT DEFAULT 'Pending',
                source_text TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
                FOREIGN KEY (analysis_id) REFERENCES comprehensive_analysis (analysis_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS analysis_templates (
                template_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                document_types TEXT,
                analysis_sections TEXT,
                custom_prompts TEXT,
                parameters TEXT,
                created_by TEXT,
                version TEXT DEFAULT '1.0',
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS conversation_contexts (
                session_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                current_topic TEXT,
                analysis_mode TEXT DEFAULT 'casual',
                user_preferences TEXT,
                context_summary TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS excel_reports (
                report_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                download_url TEXT,
                report_type TEXT,
                document_ids TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_comprehensive_analysis_document ON comprehensive_analysis (document_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_risk_assessments_document ON risk_assessments (document_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_risk_assessments_severity ON risk_assessments (severity)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_commitments_document ON commitments (document_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_commitments_deadline ON commitments (deadline)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_deliverable_dates_document ON deliverable_dates (document_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_deliverable_dates_date ON deliverable_dates (date)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_analysis_templates_active ON analysis_templates (is_active)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_conversation_contexts_document ON conversation_contexts (document_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_excel_reports_expires ON excel_reports (expires_at)
            """
        ]


# Global migrator instance
migrator = DatabaseMigrator()