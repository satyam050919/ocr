import logging
from typing import Dict, List, Optional, Any, BinaryIO
import re

from app.models.document import (
    DocumentType, 
    ProcessedDocument, 
    ExtractedField, 
    TextractBlock
)
from app.services.textract_service import TextractService

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self, textract_service: TextractService):
        self.textract_service = textract_service
        self.document_type_detectors = {
            DocumentType.PASSPORT: self._detect_passport,
            DocumentType.INVOICE: self._detect_invoice,
            DocumentType.DRIVERS_LICENSE: self._detect_drivers_license,
            DocumentType.UTILITY_BILL: self._detect_utility_bill,
        }
        self.document_processors = {
            DocumentType.PASSPORT: self._process_passport,
            DocumentType.INVOICE: self._process_invoice,
            DocumentType.DRIVERS_LICENSE: self._process_drivers_license,
            DocumentType.UTILITY_BILL: self._process_utility_bill,
            DocumentType.GENERIC: self._process_generic,
        }
    
    def process_document(
        self, 
        document: BinaryIO, 
        document_type: Optional[DocumentType] = None,
        auto_detect_type: bool = True
    ) -> ProcessedDocument:
        """
        Process a document using AWS Textract and extract structured data.
        """
        textract_response = self.textract_service.analyze_document(document)
        blocks = self.textract_service.extract_blocks(textract_response)
        
        detected_type = document_type
        if auto_detect_type or not document_type:
            detected_type = self._detect_document_type(blocks)
        
        processor = self.document_processors.get(
            detected_type or DocumentType.GENERIC, 
            self._process_generic
        )
        
        return processor(blocks)
    
    def _detect_document_type(self, blocks: List[TextractBlock]) -> DocumentType:
        """
        Detect the document type based on content analysis.
        """
        full_text = " ".join([block.text for block in blocks if block.text])
        full_text = full_text.lower()
        
        for doc_type, detector in self.document_type_detectors.items():
            if detector(full_text, blocks):
                return doc_type
        
        return DocumentType.GENERIC
    
    def _detect_passport(self, text: str, blocks: List[TextractBlock]) -> bool:
        """Detect if document is a passport."""
        passport_keywords = [
            "passport", "nationality", "surname", "given names", 
            "date of birth", "place of birth", "date of issue", 
            "date of expiry", "authority", "holder's signature"
        ]
        return any(keyword in text for keyword in passport_keywords)
    
    def _detect_invoice(self, text: str, blocks: List[TextractBlock]) -> bool:
        """Detect if document is an invoice."""
        invoice_keywords = [
            "invoice", "bill to", "ship to", "invoice number", 
            "invoice date", "due date", "total due", "subtotal", 
            "tax", "amount due", "payment terms"
        ]
        return any(keyword in text for keyword in invoice_keywords)
    
    def _detect_drivers_license(self, text: str, blocks: List[TextractBlock]) -> bool:
        """Detect if document is a driver's license."""
        license_keywords = [
            "driver license", "driver's license", "driving licence", 
            "dl no", "class", "restrictions", "endorsements", 
            "date of birth", "sex", "height", "eyes", "issue date", 
            "expiration date", "dd"
        ]
        return any(keyword in text for keyword in license_keywords)
    
    def _detect_utility_bill(self, text: str, blocks: List[TextractBlock]) -> bool:
        """Detect if document is a utility bill."""
        utility_keywords = [
            "utility", "electric", "gas", "water", "sewage", 
            "bill date", "due date", "account number", "service address", 
            "meter reading", "usage", "current charges", "previous balance"
        ]
        return any(keyword in text for keyword in utility_keywords)
    
    def _process_passport(self, blocks: List[TextractBlock]) -> ProcessedDocument:
        """Process passport document."""
        full_text = " ".join([block.text for block in blocks if block.text])
        
        patterns = {
            "passport_number": r"passport no[.:]\s*([A-Z0-9]+)",
            "surname": r"surname[.:]\s*([A-Za-z\s-]+)",
            "given_names": r"given names[.:]\s*([A-Za-z\s-]+)",
            "nationality": r"nationality[.:]\s*([A-Za-z\s-]+)",
            "date_of_birth": r"date of birth[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "place_of_birth": r"place of birth[.:]\s*([A-Za-z\s-]+)",
            "date_of_issue": r"date of issue[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "date_of_expiry": r"date of expiry[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
        }
        
        fields = []
        for field_name, pattern in patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                fields.append(
                    ExtractedField(
                        name=field_name,
                        value=match.group(1).strip(),
                        confidence=90.0  # Placeholder confidence
                    )
                )
        
        return ProcessedDocument(
            document_type=DocumentType.PASSPORT,
            fields=fields,
            raw_text=full_text,
            confidence_score=85.0,  # Placeholder overall confidence
            metadata={"source": "textract"}
        )
    
    def _process_invoice(self, blocks: List[TextractBlock]) -> ProcessedDocument:
        """Process invoice document."""
        full_text = " ".join([block.text for block in blocks if block.text])
        
        patterns = {
            "invoice_number": r"invoice\s*(?:no|number|#)[.:]\s*([A-Z0-9-]+)",
            "invoice_date": r"(?:invoice|bill)\s*date[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "due_date": r"due\s*date[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "total_amount": r"(?:total|amount\s*due|balance\s*due)[.:]\s*[$€£]?\s*(\d+(?:[.,]\d+)?)",
            "subtotal": r"subtotal[.:]\s*[$€£]?\s*(\d+(?:[.,]\d+)?)",
            "tax": r"(?:tax|vat|gst)[.:]\s*[$€£]?\s*(\d+(?:[.,]\d+)?)",
            "vendor_name": r"(?:from|vendor|seller|company)[.:]\s*([A-Za-z0-9\s.,&-]+)",
            "customer_name": r"(?:to|bill\s*to|customer|client)[.:]\s*([A-Za-z0-9\s.,&-]+)",
        }
        
        fields = []
        for field_name, pattern in patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                fields.append(
                    ExtractedField(
                        name=field_name,
                        value=match.group(1).strip(),
                        confidence=85.0  # Placeholder confidence
                    )
                )
        
        return ProcessedDocument(
            document_type=DocumentType.INVOICE,
            fields=fields,
            raw_text=full_text,
            confidence_score=80.0,  # Placeholder overall confidence
            metadata={"source": "textract"}
        )
    
    def _process_drivers_license(self, blocks: List[TextractBlock]) -> ProcessedDocument:
        """Process driver's license document."""
        full_text = " ".join([block.text for block in blocks if block.text])
        
        patterns = {
            "license_number": r"(?:dl|license|licence)\s*(?:no|number|#)[.:]\s*([A-Z0-9-]+)",
            "full_name": r"(?:name|full\s*name)[.:]\s*([A-Za-z\s-]+)",
            "address": r"(?:address|addr)[.:]\s*([A-Za-z0-9\s.,#-]+)",
            "date_of_birth": r"(?:dob|date\s*of\s*birth|birth\s*date)[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "issue_date": r"(?:issue|issued)\s*(?:date|on)[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "expiration_date": r"(?:exp|expiration|expires)\s*(?:date|on)[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "class": r"class[.:]\s*([A-Z0-9]+)",
            "restrictions": r"(?:rest|restrictions)[.:]\s*([A-Z0-9\s-]+)",
        }
        
        fields = []
        for field_name, pattern in patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                fields.append(
                    ExtractedField(
                        name=field_name,
                        value=match.group(1).strip(),
                        confidence=85.0  # Placeholder confidence
                    )
                )
        
        return ProcessedDocument(
            document_type=DocumentType.DRIVERS_LICENSE,
            fields=fields,
            raw_text=full_text,
            confidence_score=82.0,  # Placeholder overall confidence
            metadata={"source": "textract"}
        )
    
    def _process_utility_bill(self, blocks: List[TextractBlock]) -> ProcessedDocument:
        """Process utility bill document."""
        full_text = " ".join([block.text for block in blocks if block.text])
        
        patterns = {
            "account_number": r"(?:account|acct)(?:\s*number|\s*no|\s*#)[.:]\s*([A-Z0-9-]+)",
            "bill_date": r"(?:bill|statement)\s*date[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "due_date": r"(?:due|payment)\s*date[.:]\s*(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})",
            "total_amount": r"(?:total|amount\s*due|please\s*pay)[.:]\s*[$€£]?\s*(\d+(?:[.,]\d+)?)",
            "service_address": r"(?:service|property)\s*address[.:]\s*([A-Za-z0-9\s.,#-]+)",
            "billing_period": r"(?:billing|service)\s*period[.:]\s*([A-Za-z0-9\s.,\/-]+)",
            "utility_provider": r"(?:from|provider|company)[.:]\s*([A-Za-z0-9\s.,&-]+)",
            "customer_name": r"(?:customer|client|name)[.:]\s*([A-Za-z\s-]+)",
        }
        
        fields = []
        for field_name, pattern in patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                fields.append(
                    ExtractedField(
                        name=field_name,
                        value=match.group(1).strip(),
                        confidence=85.0  # Placeholder confidence
                    )
                )
        
        return ProcessedDocument(
            document_type=DocumentType.UTILITY_BILL,
            fields=fields,
            raw_text=full_text,
            confidence_score=80.0,  # Placeholder overall confidence
            metadata={"source": "textract"}
        )
    
    def _process_generic(self, blocks: List[TextractBlock]) -> ProcessedDocument:
        """Process generic document when type is unknown."""
        full_text = " ".join([block.text for block in blocks if block.text])
        
        form_data = self.textract_service.get_form_key_value_pairs(blocks)
        
        fields = []
        for key, data in form_data.items():
            fields.append(
                ExtractedField(
                    name=key,
                    value=data['value'],
                    confidence=data['confidence']
                )
            )
        
        return ProcessedDocument(
            document_type=DocumentType.GENERIC,
            fields=fields,
            raw_text=full_text,
            confidence_score=75.0,  # Placeholder overall confidence
            metadata={"source": "textract"}
        )
