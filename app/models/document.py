from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    PASSPORT = "passport"
    INVOICE = "invoice"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    GENERIC = "generic"


class TextractBlock(BaseModel):
    id: str
    block_type: str
    text: Optional[str] = None
    confidence: Optional[float] = None
    geometry: Optional[Dict[str, Any]] = None
    relationships: Optional[List[Dict[str, Any]]] = None


class ExtractedField(BaseModel):
    name: str
    value: str
    confidence: float


class ProcessedDocument(BaseModel):
    document_type: DocumentType
    fields: List[ExtractedField] = []
    raw_text: Optional[str] = None
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentRequest(BaseModel):
    document_type: Optional[DocumentType] = DocumentType.GENERIC
    auto_detect_type: bool = True
