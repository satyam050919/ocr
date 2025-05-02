import json
import logging
import uuid
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from app.models.document import DocumentType
from app.models.validation import ProcessingJob, ProcessingStatus

logger = logging.getLogger(__name__)


class MessageQueueService:
    """
    Service for handling message queue operations.
    In a production environment, this would integrate with AWS SQS, Kafka, or similar.
    This is a simplified in-memory implementation for demonstration.
    """
    
    def __init__(self):
        """Initialize the message queue service."""
        self.jobs = {}  # In-memory job storage
        self.callbacks = {}  # Registered callbacks for job events
    
    def create_job(self, document_id: str, document_type: Optional[DocumentType] = None) -> ProcessingJob:
        """
        Create a new processing job.
        
        Args:
            document_id: ID of the document to process
            document_type: Type of the document
            
        Returns:
            ProcessingJob: The created job
        """
        job_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        job = ProcessingJob(
            job_id=job_id,
            document_id=document_id,
            document_type=document_type,
            status=ProcessingStatus.PENDING,
            created_at=now,
            updated_at=now
        )
        
        self.jobs[job_id] = job
        logger.info(f"Created processing job {job_id} for document {document_id}")
        
        return job
    
    def update_job_status(self, job_id: str, status: ProcessingStatus, 
                          result_url: Optional[str] = None, 
                          error_message: Optional[str] = None) -> ProcessingJob:
        """
        Update the status of a processing job.
        
        Args:
            job_id: ID of the job to update
            status: New status of the job
            result_url: URL to the processing result (if completed)
            error_message: Error message (if failed)
            
        Returns:
            ProcessingJob: The updated job
        """
        if job_id not in self.jobs:
            logger.error(f"Job {job_id} not found")
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        job.status = status
        job.updated_at = datetime.utcnow().isoformat()
        
        if result_url:
            job.result_url = result_url
            
        if error_message:
            job.error_message = error_message
        
        logger.info(f"Updated job {job_id} status to {status}")
        
        self._trigger_callbacks(job)
        
        return job
    
    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """
        Get a processing job by ID.
        
        Args:
            job_id: ID of the job to get
            
        Returns:
            ProcessingJob: The job, or None if not found
        """
        return self.jobs.get(job_id)
    
    def list_jobs(self, status: Optional[ProcessingStatus] = None) -> List[ProcessingJob]:
        """
        List processing jobs, optionally filtered by status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List[ProcessingJob]: List of matching jobs
        """
        if status:
            return [job for job in self.jobs.values() if job.status == status]
        return list(self.jobs.values())
    
    def register_callback(self, status: ProcessingStatus, callback: Callable[[ProcessingJob], None]):
        """
        Register a callback for a specific job status.
        
        Args:
            status: The status to trigger the callback for
            callback: The callback function to call
        """
        if status not in self.callbacks:
            self.callbacks[status] = []
        self.callbacks[status].append(callback)
    
    def _trigger_callbacks(self, job: ProcessingJob):
        """
        Trigger callbacks for a job.
        
        Args:
            job: The job that was updated
        """
        callbacks = self.callbacks.get(job.status, [])
        for callback in callbacks:
            try:
                callback(job)
            except Exception as e:
                logger.error(f"Error in callback for job {job.job_id}: {str(e)}")
