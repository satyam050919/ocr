# Textract Document Processor - Technical Documentation

**Document Status:** Draft  
**Last Updated:** May 2, 2025  
**Author:** Devin AI  
**Stakeholders:** Engineering, Product, QA

## 1. Introduction

### 1.1 Purpose

This document provides comprehensive technical documentation for the Textract Document Processor, a scalable backend service built with FastAPI that processes OCR responses from AWS Textract. The service extracts and normalizes structured data from different document types such as passports, invoices, driver's licenses, and utility bills.

### 1.2 Scope

This documentation covers:
- System architecture and components
- API endpoints and usage
- Document processing workflows
- Validation and confidence scoring
- Human-in-the-loop validation
- Deployment and scaling

### 1.3 Audience

This documentation is intended for:
- Software engineers implementing or extending the system
- DevOps engineers deploying and maintaining the system
- QA engineers testing the system
- Product managers understanding system capabilities

## 2. System Architecture

### 2.1 High-Level Architecture

The Textract Document Processor follows a modular, pluggable architecture with the following key components:

| Layer | Description | Key Components |
|-------|-------------|----------------|
| Document Ingress | Handles document uploads and initial processing | FastAPI endpoints, File validation |
| Document Type Detection | Identifies document type based on content and metadata | Heuristic classifier, ML-based classifier |
| Document Processing | Extracts structured data based on document type | Type-specific processors, Extraction strategies |
| Validation | Validates extracted data and assigns confidence scores | Field validation, Format validation, Cross-field validation |
| Message Queue | Manages asynchronous processing and scaling | AWS SQS/Kafka, Job tracking, Retry mechanism |
| Storage | Persists documents and extracted data | Document storage, Extracted data store, Audit logs |
| API | Exposes functionality to clients | REST endpoints, GraphQL API, Webhooks |
| UI | Provides human-in-the-loop validation | Document viewer, Extraction results, Manual correction |

### 2.2 Component Details

#### 2.2.1 Document Type-Aware Processing

The system implements a modular architecture where each document type has its own parser:

| Document Type | Parser | Key Features |
|---------------|--------|--------------|
| Passport | PassportProcessor | MRZ extraction, Personal information extraction, Document validation |
| Invoice | InvoiceProcessor | Line item detection, Total calculation, Vendor recognition |
| Driver's License | DriversLicenseProcessor | ID extraction, Personal information, License details |
| Utility Bill | UtilityBillProcessor | Account information, Service details, Payment information |
| Generic | GenericDocumentProcessor | Key-value extraction for unrecognized document types |

The routing layer decides whether to:
- Use pure rule-based extraction logic
- Invoke a pre-trained ML model for context-aware field mapping
- Use metadata or document heuristics to help classify document types

#### 2.2.2 Validation and Confidence Scoring

The validation layer:
- Throws hard blocks (errors) when critical fields are missing
- Issues warnings when confidence scores are low
- Provides detailed logs for downstream observability

Validation rules are defined per document type and include:
- Required field validation
- Format validation using regex patterns
- Cross-field validation for logical consistency

#### 2.2.3 Scalability and Extensibility

The system is designed for scalability and extensibility:
- Pluggable strategy pattern for each document type processor
- Message-driven architecture using AWS SQS for scaling OCR processing jobs
- Clean interfaces for ML models and rule logic

#### 2.2.4 Microfrontend UI

The UI component provides:
- Visualization of original document with overlaid extracted fields
- Highlighting of low-confidence fields and validation errors
- Interface for manual correction and re-validation

## 3. API Reference

### 3.1 REST API Endpoints

#### 3.1.1 Document Processing

##### Synchronous Processing

```
POST /documents/process
```

Process a document synchronously and return the extracted data.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: The document file (PDF, PNG, JPEG)
  - `document_type` (optional): Specify the document type
  - `auto_detect_type` (optional): Whether to auto-detect the document type (default: true)

**Response:**
```json
{
  "document_type": "passport",
  "fields": [
    {
      "name": "passport_number",
      "value": "AB123456",
      "confidence": 95.5,
      "bounding_box": {
        "top": 0.1,
        "left": 0.2,
        "width": 0.3,
        "height": 0.1
      }
    },
    {
      "name": "surname",
      "value": "DOE",
      "confidence": 98.2,
      "bounding_box": {
        "top": 0.2,
        "left": 0.2,
        "width": 0.3,
        "height": 0.1
      }
    }
  ],
  "raw_text": "...",
  "confidence_score": 92.3,
  "metadata": {
    "source": "textract",
    "processing_time_ms": 1250
  }
}
```

##### Asynchronous Processing

```
POST /processing/async
```

Process a document asynchronously and return a job ID for tracking.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: The document file (PDF, PNG, JPEG)
  - `document_type` (optional): Specify the document type
  - `auto_detect_type` (optional): Whether to auto-detect the document type (default: true)
  - `callback_url` (optional): URL to call when processing is complete

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "550e8400-e29b-41d4-a716-446655440001",
  "document_type": "passport",
  "status": "pending",
  "created_at": "2025-05-02T06:30:00.000Z",
  "updated_at": "2025-05-02T06:30:00.000Z"
}
```

## 4. Implementation Guide

### 4.1 Setting Up the Environment

1. Clone the repository:
```bash
git clone https://github.com/satyam050919/ocr.git
cd ocr
```

2. Install dependencies:
```bash
poetry install
```

3. Configure AWS credentials:
```bash
# Edit .env file
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### 4.2 Running the Service

1. Start the API server:
```bash
poetry run fastapi dev app/main.py
```

2. Start the frontend UI:
```bash
./start_frontend.sh
```

### 4.3 Deployment

1. Deploy using Docker:
```bash
./deploy.sh
```

## 5. Testing

### 5.1 API Testing

Test the API endpoints using curl:

```bash
# Process a document synchronously
curl -X POST "http://localhost:8000/documents/process" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -F "auto_detect_type=true"

# Process a document asynchronously
curl -X POST "http://localhost:8000/processing/async" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf" \
  -F "auto_detect_type=true"
```

### 5.2 Unit Testing

Run the unit tests:

```bash
poetry run pytest
```

## 6. Extending the System

### 6.1 Adding a New Document Type

1. Define the document type in `app/models/document.py`
2. Create a new processor in `app/services/document_processor.py`
3. Add validation rules in `app/services/validation_service.py`
4. Register the processor in `app/services/document_processor_factory.py`

### 6.2 Customizing Validation Rules

Validation rules can be customized in `app/services/validation_service.py`:

```python
# Example: Adding a new validation rule for passports
passport_rules = DocumentValidationRules(
    document_type=DocumentType.PASSPORT,
    field_rules=[
        FieldValidationRule(
            field_name="passport_number",
            is_required=True,
            min_confidence=0.8,
            custom_error_message="Passport number is required"
        ),
        # Add more rules here
    ],
    format_rules=[
        FormatValidationRule(
            field_name="passport_number",
            is_required=True,
            min_confidence=0.8,
            regex_pattern=r"^[A-Z0-9]{6,9}$",
            format_description="Passport number must be 6-9 alphanumeric characters"
        ),
        # Add more format rules here
    ],
    cross_field_rules=[
        # Add cross-field validation rules here
    ],
    min_overall_confidence=0.7
)
```
