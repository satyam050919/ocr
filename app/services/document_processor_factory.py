from typing import Dict, Type, Optional
import logging

from app.models.document import DocumentType
from app.services.document_processor import DocumentProcessor
from app.services.textract_service import TextractService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class DocumentProcessorFactory:
    """
    Factory for creating document processors based on document type.
    Implements the Strategy pattern for document processing.
    """
    
    def __init__(self, textract_service: TextractService, validation_service: ValidationService):
        """
        Initialize the factory with services needed by processors.
        
        Args:
            textract_service: Service for interacting with AWS Textract
            validation_service: Service for validating processed documents
        """
        self.textract_service = textract_service
        self.validation_service = validation_service
        self.processors = {}
        self._register_processors()
    
    def _register_processors(self):
        """Register document processors for each document type."""
        for doc_type in DocumentType:
            self.processors[doc_type] = DocumentProcessor(self.textract_service)
    
    def get_processor(self, document_type: Optional[DocumentType] = None) -> DocumentProcessor:
        """
        Get a processor for the specified document type.
        
        Args:
            document_type: The type of document to process
            
        Returns:
            DocumentProcessor: A processor for the specified document type
        """
        if not document_type:
            document_type = DocumentType.GENERIC
            
        processor = self.processors.get(document_type)
        if not processor:
            logger.warning(f"No processor registered for document type {document_type}. Using generic processor.")
            processor = self.processors.get(DocumentType.GENERIC)
            
        return processor
