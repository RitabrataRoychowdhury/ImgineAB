"""Workflow manager for coordinating document processing workflows."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import queue
import time

from src.models.document import Document, ProcessingJob
from src.storage.document_storage import DocumentStorage
from src.workflow.enhanced_workflow import EnhancedDocumentWorkflow
from src.config import config
from src.utils.logging_config import get_logger
from src.utils.error_handling import WorkflowError, handle_errors

logger = get_logger(__name__)


class WorkflowManager:
    """Manages document processing workflows and job queues."""
    
    def __init__(self, storage: Optional[DocumentStorage] = None):
        self.storage = storage or DocumentStorage()
        self.workflow = EnhancedDocumentWorkflow(self.storage)
        self.job_queue = queue.Queue()
        self.active_jobs = {}
        self.worker_thread = None
        self.running = False
        
    def start(self):
        """Start the workflow manager and worker thread."""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("Workflow manager started")
    
    def stop(self):
        """Stop the workflow manager."""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Workflow manager stopped")
    
    def shutdown(self):
        """Alias for stop() method for compatibility."""
        self.stop()
    
    def submit_document_for_processing(self, document: Document, api_key: str) -> str:
        """Submit a document for processing and return job ID."""
        try:
            # Create the document record
            self.storage.create_document(document)
            
            # Create processing job
            job_id = str(uuid.uuid4())
            processing_job = ProcessingJob(
                job_id=job_id,
                document_id=document.id,
                status="queued",
                current_step="queued"
            )
            
            self.storage.create_processing_job(processing_job)
            
            # Add to job queue
            job_data = {
                'job_id': job_id,
                'document_id': document.id,
                'document_text': document.original_text,
                'api_key': api_key,
                'submitted_at': datetime.now()
            }
            
            self.job_queue.put(job_data)
            logger.info(f"Submitted document {document.id} for processing with job {job_id}")
            
            return job_id
            
        except Exception as e:
            logger.error(f"Error submitting document for processing: {e}")
            raise
    
    def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get the current status of a processing job."""
        return self.storage.get_processing_job(job_id)
    
    def get_document_processing_status(self, document_id: str) -> Optional[ProcessingJob]:
        """Get the latest processing job for a document."""
        jobs = self.storage.list_processing_jobs(document_id)
        return jobs[0] if jobs else None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a processing job if it's still queued."""
        try:
            job = self.storage.get_processing_job(job_id)
            if job and job.status in ['queued', 'pending']:
                self.storage.update_processing_job(
                    job_id,
                    status="cancelled",
                    error_message="Job cancelled by user",
                    completed_at=datetime.now()
                )
                logger.info(f"Cancelled job {job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling job {job_id}: {e}")
            return False
    
    def _worker_loop(self):
        """Main worker loop for processing jobs."""
        logger.info("Workflow worker thread started")
        
        while self.running:
            try:
                # Get next job from queue (with timeout to allow checking running flag)
                try:
                    job_data = self.job_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                job_id = job_data['job_id']
                
                # Check if job was cancelled
                job = self.storage.get_processing_job(job_id)
                if not job or job.status == 'cancelled':
                    logger.info(f"Skipping cancelled job {job_id}")
                    continue
                
                # Process the job
                self._process_job(job_data)
                
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                time.sleep(1)  # Brief pause before continuing
        
        logger.info("Workflow worker thread stopped")
    
    def _process_job(self, job_data: Dict[str, Any]):
        """Process a single job."""
        job_id = job_data['job_id']
        document_id = job_data['document_id']
        
        try:
            logger.info(f"Starting processing for job {job_id}")
            self.active_jobs[job_id] = job_data
            
            # Update job status to processing
            self.storage.update_processing_job(
                job_id,
                status="processing",
                current_step="starting"
            )
            
            # Run the workflow
            result_job_id = self.workflow.process_document(
                document_id=document_id,
                document_text=job_data['document_text'],
                api_key=job_data['api_key']
            )
            
            logger.info(f"Completed processing for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            
            # Update job with error
            try:
                self.storage.update_processing_job(
                    job_id,
                    status="failed",
                    error_message=str(e),
                    completed_at=datetime.now()
                )
                
                # Update document status
                self.storage.update_document(document_id, {
                    'processing_status': 'failed',
                    'updated_at': datetime.now()
                })
                
            except Exception as update_error:
                logger.error(f"Error updating job status: {update_error}")
        
        finally:
            # Remove from active jobs
            self.active_jobs.pop(job_id, None)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue and processing status."""
        return {
            'queue_size': self.job_queue.qsize(),
            'active_jobs': len(self.active_jobs),
            'running': self.running,
            'active_job_ids': list(self.active_jobs.keys())
        }
    
    def get_recent_jobs(self, limit: int = 10) -> List[ProcessingJob]:
        """Get recent processing jobs."""
        return self.storage.list_processing_jobs()[:limit]


# Global workflow manager instance
_workflow_manager = None


def get_workflow_manager() -> WorkflowManager:
    """Get the global workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
        _workflow_manager.start()
    return _workflow_manager


def shutdown_workflow_manager():
    """Shutdown the global workflow manager."""
    global _workflow_manager
    if _workflow_manager:
        _workflow_manager.stop()
        _workflow_manager = None