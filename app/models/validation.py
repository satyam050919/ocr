from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

from app.models.document import DocumentType, ExtractedField


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    ERROR = "error"  # Hard block - critical issue
    WARNING = "warning"  # Soft warning - potential issue
    INFO = "info"  # Informational - not an issue but worth noting


class ValidationIssue(BaseModel):
    """Model for validation issues found during document processing."""
    field_name: Optional[str] = None
    message: str
    severity: ValidationSeverity
    confidence: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    """Model for validation results of a processed document."""
    is_valid: bool
    issues: List[ValidationIssue] = []
    document_type: DocumentType
    confidence_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FieldValidationRule(BaseModel):
    """Base model for field validation rules."""
    field_name: str
    is_required: bool = False
    min_confidence: float = 0.0
    custom_error_message: Optional[str] = None


class FormatValidationRule(FieldValidationRule):
    """Validation rule for field format."""
    regex_pattern: str
    format_description: str


class CrossFieldValidationRule(BaseModel):
    """Validation rule for cross-field validation."""
    field_names: List[str]
    validation_function: str  # Name of the function to call for validation
    error_message: str


class DocumentValidationRules(BaseModel):
    """Collection of validation rules for a document type."""
    document_type: DocumentType
    field_rules: List[FieldValidationRule] = []
    format_rules: List[FormatValidationRule] = []
    cross_field_rules: List[CrossFieldValidationRule] = []
    min_overall_confidence: float = 0.0


class ProcessingStatus(str, Enum):
    """Status of a document processing job."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATION_REQUIRED = "validation_required"  # Requires human validation


class ProcessingJob(BaseModel):
    """Model for a document processing job."""
    job_id: str
    document_id: str
    document_type: Optional[DocumentType] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: str
    updated_at: str
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HumanValidationRequest(BaseModel):
    """Model for a human validation request."""
    job_id: str
    document_id: str
    fields_to_validate: List[ExtractedField]
    validation_issues: List[ValidationIssue]
    original_document_url: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HumanValidationResponse(BaseModel):
    """Model for a human validation response."""
    job_id: str
    document_id: str
    validated_fields: List[ExtractedField]
    validation_notes: Optional[str] = None
    validated_by: str
    validated_at: str
