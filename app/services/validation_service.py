import re
import logging
from typing import Dict, List, Optional, Any, Callable, Type
import importlib

from app.models.document import DocumentType, ProcessedDocument, ExtractedField
from app.models.validation import (
    ValidationSeverity, 
    ValidationIssue, 
    ValidationResult,
    FieldValidationRule,
    FormatValidationRule,
    CrossFieldValidationRule,
    DocumentValidationRules
)

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating processed documents."""
    
    def __init__(self):
        """Initialize the validation service with document type specific rules."""
        self.validation_rules = self._load_validation_rules()
        self.cross_field_validators = self._load_cross_field_validators()
    
    def _load_validation_rules(self) -> Dict[DocumentType, DocumentValidationRules]:
        """Load validation rules for each document type."""
        rules = {}
        
        passport_rules = DocumentValidationRules(
            document_type=DocumentType.PASSPORT,
            field_rules=[
                FieldValidationRule(
                    field_name="passport_number",
                    is_required=True,
                    min_confidence=80.0,
                    custom_error_message="Passport number is required"
                ),
                FieldValidationRule(
                    field_name="surname",
                    is_required=True,
                    min_confidence=80.0
                ),
                FieldValidationRule(
                    field_name="given_names",
                    is_required=True,
                    min_confidence=80.0
                ),
                FieldValidationRule(
                    field_name="date_of_birth",
                    is_required=True,
                    min_confidence=80.0
                ),
                FieldValidationRule(
                    field_name="date_of_expiry",
                    is_required=True,
                    min_confidence=80.0
                ),
            ],
            format_rules=[
                FormatValidationRule(
                    field_name="passport_number",
                    is_required=True,
                    regex_pattern=r"^[A-Z0-9]{6,9}$",
                    format_description="Passport number should be 6-9 alphanumeric characters"
                ),
                FormatValidationRule(
                    field_name="date_of_birth",
                    is_required=True,
                    regex_pattern=r"^\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}$",
                    format_description="Date should be in DD/MM/YYYY format"
                ),
                FormatValidationRule(
                    field_name="date_of_expiry",
                    is_required=True,
                    regex_pattern=r"^\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}$",
                    format_description="Date should be in DD/MM/YYYY format"
                ),
            ],
            cross_field_rules=[
                CrossFieldValidationRule(
                    field_names=["date_of_birth", "date_of_expiry"],
                    validation_function="validate_expiry_after_birth",
                    error_message="Expiry date must be after date of birth"
                )
            ],
            min_overall_confidence=75.0
        )
        rules[DocumentType.PASSPORT] = passport_rules
        
        invoice_rules = DocumentValidationRules(
            document_type=DocumentType.INVOICE,
            field_rules=[
                FieldValidationRule(
                    field_name="invoice_number",
                    is_required=True,
                    min_confidence=75.0
                ),
                FieldValidationRule(
                    field_name="invoice_date",
                    is_required=True,
                    min_confidence=75.0
                ),
                FieldValidationRule(
                    field_name="total_amount",
                    is_required=True,
                    min_confidence=85.0,
                    custom_error_message="Total amount is required with high confidence"
                ),
            ],
            format_rules=[
                FormatValidationRule(
                    field_name="invoice_date",
                    is_required=True,
                    regex_pattern=r"^\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}$",
                    format_description="Date should be in DD/MM/YYYY format"
                ),
                FormatValidationRule(
                    field_name="total_amount",
                    is_required=True,
                    regex_pattern=r"^[$€£]?\s*\d+(?:[.,]\d+)?$",
                    format_description="Amount should be a valid currency value"
                ),
            ],
            min_overall_confidence=70.0
        )
        rules[DocumentType.INVOICE] = invoice_rules
        
        drivers_license_rules = DocumentValidationRules(
            document_type=DocumentType.DRIVERS_LICENSE,
            field_rules=[
                FieldValidationRule(
                    field_name="license_number",
                    is_required=True,
                    min_confidence=80.0
                ),
                FieldValidationRule(
                    field_name="full_name",
                    is_required=True,
                    min_confidence=80.0
                ),
                FieldValidationRule(
                    field_name="date_of_birth",
                    is_required=True,
                    min_confidence=80.0
                ),
                FieldValidationRule(
                    field_name="expiration_date",
                    is_required=True,
                    min_confidence=80.0
                ),
            ],
            format_rules=[
                FormatValidationRule(
                    field_name="date_of_birth",
                    is_required=True,
                    regex_pattern=r"^\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}$",
                    format_description="Date should be in DD/MM/YYYY format"
                ),
                FormatValidationRule(
                    field_name="expiration_date",
                    is_required=True,
                    regex_pattern=r"^\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}$",
                    format_description="Date should be in DD/MM/YYYY format"
                ),
            ],
            cross_field_rules=[
                CrossFieldValidationRule(
                    field_names=["date_of_birth", "expiration_date"],
                    validation_function="validate_expiry_after_birth",
                    error_message="Expiration date must be after date of birth"
                )
            ],
            min_overall_confidence=75.0
        )
        rules[DocumentType.DRIVERS_LICENSE] = drivers_license_rules
        
        utility_bill_rules = DocumentValidationRules(
            document_type=DocumentType.UTILITY_BILL,
            field_rules=[
                FieldValidationRule(
                    field_name="account_number",
                    is_required=True,
                    min_confidence=75.0
                ),
                FieldValidationRule(
                    field_name="bill_date",
                    is_required=True,
                    min_confidence=75.0
                ),
                FieldValidationRule(
                    field_name="total_amount",
                    is_required=True,
                    min_confidence=80.0
                ),
                FieldValidationRule(
                    field_name="service_address",
                    is_required=True,
                    min_confidence=75.0
                ),
            ],
            format_rules=[
                FormatValidationRule(
                    field_name="bill_date",
                    is_required=True,
                    regex_pattern=r"^\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4}$",
                    format_description="Date should be in DD/MM/YYYY format"
                ),
                FormatValidationRule(
                    field_name="total_amount",
                    is_required=True,
                    regex_pattern=r"^[$€£]?\s*\d+(?:[.,]\d+)?$",
                    format_description="Amount should be a valid currency value"
                ),
            ],
            min_overall_confidence=70.0
        )
        rules[DocumentType.UTILITY_BILL] = utility_bill_rules
        
        generic_rules = DocumentValidationRules(
            document_type=DocumentType.GENERIC,
            min_overall_confidence=60.0
        )
        rules[DocumentType.GENERIC] = generic_rules
        
        return rules
    
    def _load_cross_field_validators(self) -> Dict[str, Callable]:
        """Load cross-field validation functions."""
        validators = {
            "validate_expiry_after_birth": self._validate_expiry_after_birth,
        }
        return validators
    
    def _validate_expiry_after_birth(self, fields: Dict[str, ExtractedField]) -> Optional[ValidationIssue]:
        """Validate that expiry date is after birth date."""
        birth_date = fields.get("date_of_birth", None) or fields.get("dob", None)
        expiry_date = fields.get("date_of_expiry", None) or fields.get("expiration_date", None)
        
        if not birth_date or not expiry_date:
            return ValidationIssue(
                message="Missing date fields for cross-validation",
                severity=ValidationSeverity.WARNING
            )
        
        birth_parts = re.split(r'[\/\.\-]', birth_date.value)
        expiry_parts = re.split(r'[\/\.\-]', expiry_date.value)
        
        if len(birth_parts) >= 3 and len(expiry_parts) >= 3:
            birth_year = int(birth_parts[2])
            expiry_year = int(expiry_parts[2])
            
            if birth_year > expiry_year:
                return ValidationIssue(
                    field_name="date_of_expiry",
                    message="Expiry date must be after date of birth",
                    severity=ValidationSeverity.ERROR
                )
        
        return None
    
    def validate_document(self, document: ProcessedDocument) -> ValidationResult:
        """
        Validate a processed document against the rules for its document type.
        
        Args:
            document: The processed document to validate
            
        Returns:
            ValidationResult: The result of the validation
        """
        issues = []
        
        rules = self.validation_rules.get(document.document_type, None)
        if not rules:
            return ValidationResult(
                is_valid=True,
                document_type=document.document_type,
                confidence_score=document.confidence_score or 0.0
            )
        
        if (document.confidence_score or 0.0) < rules.min_overall_confidence:
            issues.append(ValidationIssue(
                message=f"Overall confidence score {document.confidence_score} is below threshold {rules.min_overall_confidence}",
                severity=ValidationSeverity.WARNING,
                confidence=document.confidence_score
            ))
        
        field_map = {field.name: field for field in document.fields}
        
        for rule in rules.field_rules:
            field = field_map.get(rule.field_name)
            
            if rule.is_required and not field:
                issues.append(ValidationIssue(
                    field_name=rule.field_name,
                    message=rule.custom_error_message or f"Required field '{rule.field_name}' is missing",
                    severity=ValidationSeverity.ERROR
                ))
            elif field and field.confidence < rule.min_confidence:
                issues.append(ValidationIssue(
                    field_name=rule.field_name,
                    message=f"Confidence for field '{rule.field_name}' is below threshold",
                    severity=ValidationSeverity.WARNING,
                    confidence=field.confidence
                ))
        
        for rule in rules.format_rules:
            field = field_map.get(rule.field_name)
            
            if field:
                if not re.match(rule.regex_pattern, field.value):
                    issues.append(ValidationIssue(
                        field_name=rule.field_name,
                        message=f"Field '{rule.field_name}' format is invalid. {rule.format_description}",
                        severity=ValidationSeverity.ERROR if rule.is_required else ValidationSeverity.WARNING
                    ))
        
        for rule in rules.cross_field_rules:
            validator = self.cross_field_validators.get(rule.validation_function)
            if validator:
                validation_fields = {name: field_map.get(name) for name in rule.field_names if name in field_map}
                
                if len(validation_fields) == len(rule.field_names):
                    issue = validator(validation_fields)
                    if issue:
                        issues.append(issue)
        
        is_valid = not any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            document_type=document.document_type,
            confidence_score=document.confidence_score or 0.0,
            metadata=document.metadata
        )
