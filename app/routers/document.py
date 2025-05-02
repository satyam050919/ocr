import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional

from app.models.document import DocumentType, DocumentRequest, ProcessedDocument
from app.services.textract_service import TextractService
from app.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


def get_document_processor():
    textract_service = TextractService()
    return DocumentProcessor(textract_service)


@router.post("/process", response_model=ProcessedDocument)
async def process_document(
    file: UploadFile = File(...),
    document_type: Optional[DocumentType] = Form(None),
    auto_detect_type: bool = Form(True),
    processor: DocumentProcessor = Depends(get_document_processor)
):
    """
    Process a document using AWS Textract and extract structured data.
    
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
        contents = await file.read()
        file.file.seek(0)
        
        result = processor.process_document(
            file.file,
            document_type=document_type,
            auto_detect_type=auto_detect_type
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.post("/batch-process")
async def batch_process_documents():
    """
    Batch process multiple documents (placeholder for future implementation).
    """
    return {"message": "Batch processing not implemented yet"}
