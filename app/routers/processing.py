import logging
import uuid
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.document import DocumentType, DocumentRequest, ProcessedDocument
from app.models.validation import ProcessingJob, ProcessingStatus, ValidationResult
from app.services.textract_service import TextractService
from app.services.document_processor_factory import DocumentProcessorFactory
from app.services.validation_service import ValidationService
from app.services.message_queue_service import MessageQueueService
from app.utils.aws_helpers import upload_to_s3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/processing", tags=["processing"])


def get_services():
    """Get the services needed for document processing."""
    textract_service = TextractService()
    validation_service = ValidationService()
    processor_factory = DocumentProcessorFactory(textract_service, validation_service)
    message_queue_service = MessageQueueService()
    
    return {
        "textract_service": textract_service,
        "validation_service": validation_service,
        "processor_factory": processor_factory,
        "message_queue_service": message_queue_service
    }


async def process_document_task(
    file_content: bytes,
    file_name: str,
    document_type: Optional[DocumentType],
    auto_detect_type: bool,
    job_id: str,
    services: dict
):
    """
    Background task for processing a document.
    
    Args:
        file_content: Content of the document file
        file_name: Name of the document file
        document_type: Type of the document
        auto_detect_type: Whether to auto-detect the document type
        job_id: ID of the processing job
        services: Services needed for processing
    """
    try:
        message_queue = services["message_queue_service"]
        message_queue.update_job_status(job_id, ProcessingStatus.PROCESSING)
        
        processor_factory = services["processor_factory"]
        processor = processor_factory.get_processor(document_type)
        
        from io import BytesIO
        document_file = BytesIO(file_content)
        processed_document = processor.process_document(
            document_file,
            document_type=document_type,
            auto_detect_type=auto_detect_type
        )
        
        validation_service = services["validation_service"]
        validation_result = validation_service.validate_document(processed_document)
        
        result_data = {
            "processed_document": processed_document.dict(),
            "validation_result": validation_result.dict()
        }
        
        result_url = f"mock://results/{job_id}"
        
        if not validation_result.is_valid:
            message_queue.update_job_status(
                job_id, 
                ProcessingStatus.VALIDATION_REQUIRED,
                result_url=result_url
            )
        else:
            message_queue.update_job_status(
                job_id, 
                ProcessingStatus.COMPLETED,
                result_url=result_url
            )
            
    except Exception as e:
        logger.error(f"Error processing document for job {job_id}: {str(e)}")
        message_queue = services["message_queue_service"]
        message_queue.update_job_status(
            job_id, 
            ProcessingStatus.FAILED,
            error_message=str(e)
        )


@router.post("/async", response_model=ProcessingJob)
async def process_document_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: Optional[DocumentType] = Form(None),
    auto_detect_type: bool = Form(True),
    services: dict = Depends(get_services)
):
    """
    Process a document asynchronously using AWS Textract.
    
    - **file**: The document file to process (PDF, PNG, JPEG)
    - **document_type**: Optional document type to process as
    - **auto_detect_type**: Whether to auto-detect document type
    """
    allowed_types = ["application/pdf", "image/png", "image/jpeg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Supported types: PDF, PNG, JPEG"
        )
    
    try:
        document_id = str(uuid.uuid4())
        
        message_queue = services["message_queue_service"]
        job = message_queue.create_job(document_id, document_type)
        
        file_content = await file.read()
        
        background_tasks.add_task(
            process_document_task,
            file_content,
            file.filename,
            document_type,
            auto_detect_type,
            job.job_id,
            services
        )
        
        return job
        
    except Exception as e:
        logger.error(f"Error starting document processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting document processing: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=ProcessingJob)
async def get_job_status(
    job_id: str,
    services: dict = Depends(get_services)
):
    """
    Get the status of a processing job.
    
    - **job_id**: ID of the job to get status for
    """
    message_queue = services["message_queue_service"]
    job = message_queue.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return job


@router.get("/jobs", response_model=List[ProcessingJob])
async def list_jobs(
    status: Optional[ProcessingStatus] = None,
    services: dict = Depends(get_services)
):
    """
    List processing jobs, optionally filtered by status.
    
    - **status**: Status to filter by
    """
    message_queue = services["message_queue_service"]
    jobs = message_queue.list_jobs(status)
    
    return jobs
