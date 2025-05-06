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

## 7. Document Processing Use Cases

This section outlines key document processing use cases supported by the Textract Document Processor, along with feasibility analysis for field extraction and implementation considerations.

### 7.1 Document Validation Use Cases

| Use Case | Description | Feasibility | Fields to Extract | Implementation Approach | Confidence Threshold |
|----------|-------------|-------------|-------------------|-------------------------|----------------------|
| MRZ Validation | Validate Machine Readable Zone on passports and travel documents | High | MRZ lines, document number, issuing country, expiry date | Rule-based pattern matching with checksum validation | 90% |
| Invoice Total Verification | Verify that line items sum to the invoice total | High | Line item amounts, subtotal, tax, total amount | Mathematical validation with OCR error tolerance | 85% |
| ID Document Authenticity | Verify security features on ID documents | Medium | Hologram markers, microprint indicators, document patterns | ML-based feature detection with reference database | 95% |
| Address Verification | Validate address format and existence | Medium | Street, city, state/province, postal code, country | Geocoding API integration with format validation | 80% |
| Signature Verification | Verify signature presence and characteristics | Medium | Signature box, signature strokes | ML-based signature detection and analysis | 75% |
| Document Completeness | Verify all required fields are present | High | Document-specific required fields | Rule-based completeness checking with field detection | 90% |
| Expiration Validation | Verify document is not expired | High | Issue date, expiry date | Date extraction and comparison with current date | 95% |

### 7.2 Document Tagging Use Cases

| Use Case | Description | Feasibility | Tags to Apply | Implementation Approach | Confidence Threshold |
|----------|-------------|-------------|---------------|-------------------------|----------------------|
| Document Type Classification | Automatically classify document into predefined categories | High | Document type (passport, invoice, license, etc.) | ML-based document classification with visual and textual features | 85% |
| Content-based Tagging | Apply tags based on document content | High | Content tags (financial, medical, legal, etc.) | NLP-based content analysis with keyword extraction | 80% |
| Metadata Tagging | Apply tags based on document metadata | High | Metadata tags (date range, issuer, recipient, etc.) | Rule-based metadata extraction and categorization | 90% |
| Compliance Tagging | Tag documents based on regulatory requirements | Medium | Compliance tags (PII, HIPAA, GDPR, etc.) | Rule-based sensitive information detection | 95% |
| Quality Tagging | Tag documents based on image quality | High | Quality tags (high-res, low-res, needs review) | Image analysis for resolution, contrast, and clarity | 85% |
| Language Tagging | Identify and tag document language | High | Language tags (English, Spanish, French, etc.) | Language detection algorithms with character set analysis | 90% |
| Custom Entity Tagging | Tag documents based on presence of custom entities | Medium | Entity tags (contains SSN, contains credit card, etc.) | Pattern matching with entity recognition | 90% |

### 7.3 Attribute Extraction Use Cases

| Use Case | Description | Feasibility | Fields to Extract | Implementation Approach | Storage Mechanism for Confidence Scores |
|----------|-------------|-------------|-------------------|-------------------------|----------------------------------------|
| Personal Information Extraction | Extract personal details from ID documents | High | Name, DOB, gender, nationality, ID number | ML-based field detection with contextual validation | JSON field with confidence score per attribute |
| Invoice Data Extraction | Extract key data points from invoices | High | Invoice number, date, vendor, line items, total | Template-based extraction with positional awareness | Database columns for each field with confidence score |
| Receipt Information Extraction | Extract transaction details from receipts | Medium | Merchant, date, items, prices, total, payment method | ML-based field detection with positional relationships | NoSQL document with nested confidence scores |
| Medical Document Extraction | Extract medical information from healthcare documents | Medium | Patient info, diagnosis codes, treatment details | Healthcare-specific NLP with medical terminology awareness | FHIR-compliant JSON with confidence metadata |
| Contract Clause Extraction | Extract key clauses and terms from contracts | Medium | Parties, effective dates, termination clauses, obligations | Legal NLP with clause detection | Structured JSON with clause-level confidence scores |
| Financial Statement Extraction | Extract financial data from statements | Medium | Account numbers, transaction details, balances | Template matching with financial data validation | Relational database with confidence score columns |
| Address Extraction | Extract and normalize address components | High | Street, city, state/province, postal code, country | Address parsing with geocoding validation | Normalized address object with component confidence |

### 7.4 Document Splitting Use Cases

| Use Case | Description | Feasibility | Split Criteria | Implementation Approach | Confidence Considerations |
|----------|-------------|-------------|----------------|-------------------------|---------------------------|
| Multi-Document PDF Splitting | Split PDF containing multiple document types | High | Document type boundaries, page markers | ML-based document boundary detection with visual cues | Confidence threshold for boundary detection |
| Form Package Separation | Separate multi-form packages into individual forms | High | Form type, form boundaries, page breaks | Template matching with form recognition | Minimum confidence for form identification |
| Statement Separation | Split financial statements by account or statement period | Medium | Statement headers, account identifiers, date ranges | Header/footer detection with date recognition | Confidence scoring for statement boundaries |
| Medical Record Separation | Split medical records by document type or encounter | Medium | Document type indicators, encounter dates, patient identifiers | Healthcare document classification with boundary detection | Hierarchical confidence scoring for document types |
| Invoice Attachment Separation | Separate invoices from supporting documentation | High | Invoice markers, attachment indicators, content type | Content-based classification with visual separation | Dual confidence scoring for invoice and attachment |
| ID Document Batch Splitting | Split batches of ID documents into individual records | High | Document boundaries, document type, white space | Edge detection with document classification | Boundary confidence threshold |
| Legal Document Unbundling | Split legal document bundles by document type | Medium | Document headers, legal formatting, section markers | Legal document classification with structural analysis | Confidence matrix for document type and boundaries |

### 7.5 Implementation Considerations

#### 7.5.1 Confidence Score Storage

The system stores confidence scores using the following mechanisms:

1. **Field-Level Confidence:**
   ```json
   {
     "field_name": "passport_number",
     "value": "AB123456",
     "confidence": 95.5,
     "bounding_box": {
       "top": 0.1,
       "left": 0.2,
       "width": 0.3,
       "height": 0.1
     }
   }
   ```

2. **Document-Level Confidence:**
   ```json
   {
     "document_type": "passport",
     "confidence_score": 92.3,
     "fields": [...],
     "metadata": {
       "confidence_calculation": "weighted_average",
       "critical_fields_confidence": 94.8,
       "non_critical_fields_confidence": 89.2
     }
   }
   ```

3. **Confidence Thresholds:**
   - Critical fields: 90% minimum confidence
   - Non-critical fields: 75% minimum confidence
   - Overall document: 85% minimum confidence

4. **Database Schema:**
   ```sql
   CREATE TABLE extracted_fields (
     id SERIAL PRIMARY KEY,
     document_id UUID REFERENCES documents(id),
     field_name VARCHAR(100) NOT NULL,
     field_value TEXT,
     confidence DECIMAL(5,2) NOT NULL,
     requires_review BOOLEAN GENERATED ALWAYS AS (confidence < 90.0) STORED
   );
   ```

#### 7.5.2 Human-in-the-Loop Validation

For fields with confidence scores below thresholds:
1. Fields are flagged for human review
2. UI highlights low-confidence fields
3. Human reviewers can correct values
4. System records original and corrected values
5. Corrections are used to improve future extraction accuracy

#### 7.5.3 Extensibility for New Use Cases

The system is designed to be extensible for new use cases:
1. Define new document types in the document model
2. Implement custom processors for new document types
3. Define validation rules specific to the new document type
4. Configure confidence thresholds appropriate for the use case
5. Implement UI components for human review if needed

## 8. Technology Stack Analysis: Python vs Java for OCR Extraction

This section provides a comparative analysis of Python and Java libraries for OCR extraction work, evaluating their suitability for document processing tasks.

### 8.1 Library Comparison

| Feature | Python Libraries | Java Libraries | Comparison |
|---------|------------------|---------------|------------|
| **OCR Engines** | Tesseract (via pytesseract), AWS Textract, Google Vision API, Azure Computer Vision | Tesseract (via Tess4J), Apache PDFBox, Aspose.OCR, ABBYY FineReader | Python offers easier integration with cloud OCR services, while Java has more robust on-premises solutions |
| **Image Processing** | OpenCV, Pillow, scikit-image | OpenCV, ImageJ, Marvin | Both ecosystems have strong image processing capabilities; Python's libraries are more accessible for rapid development |
| **NLP Capabilities** | NLTK, spaCy, Transformers (BERT, GPT), Flair | Stanford NLP, OpenNLP, DL4J, CoreNLP | Python has a significant advantage with more modern NLP libraries and pre-trained models |
| **ML Integration** | scikit-learn, TensorFlow, PyTorch, Keras | Deeplearning4j, Weka, MOA, H2O | Python dominates in ML/DL ecosystem with more libraries, models, and community support |
| **Cloud Integration** | AWS SDK (boto3), Google Cloud, Azure SDK | AWS SDK, Google Cloud, Azure SDK | Both have good cloud integration, but Python SDKs often have more examples and community support |
| **Development Speed** | Rapid prototyping, less boilerplate | More verbose, stronger typing | Python enables significantly faster development cycles for OCR solutions |
| **Performance** | Interpreted, GIL limitations | JVM optimization, multithreading | Java offers better performance for high-throughput, multi-threaded OCR processing |
| **Scalability** | Good with async frameworks (FastAPI, asyncio) | Excellent with Spring, Quarkus, Micronaut | Java has an edge for enterprise-scale deployments with mature frameworks |
| **Deployment** | Docker, serverless, lightweight | Docker, enterprise containers, microservices | Python deployments are simpler; Java offers more enterprise deployment options |
| **Maintenance** | Dynamic typing can lead to runtime errors | Static typing catches errors at compile time | Java's type system provides better long-term maintainability for complex systems |

### 8.2 Python OCR Libraries in Detail

| Library | Strengths | Limitations | Best Use Cases |
|---------|-----------|-------------|---------------|
| **AWS Textract** | Excellent accuracy, managed service, document understanding features | AWS-specific, cost based on usage | Production-ready document processing with minimal infrastructure |
| **pytesseract** | Open-source, free, extensive language support | Lower accuracy than cloud services, requires tuning | Basic OCR needs, offline processing, multilingual documents |
| **EasyOCR** | 80+ languages, easy to use, good accuracy | Slower than commercial options | Multilingual document processing, simple integration needs |
| **Google Vision API** | High accuracy, document text detection, language detection | Cost based on usage, requires internet | High-quality OCR with minimal development effort |
| **Keras-OCR** | End-to-end OCR pipeline, customizable models | Requires ML expertise to optimize | Custom OCR solutions, specialized document types |
| **PaddleOCR** | High performance, multilingual, open-source | Complex setup, requires GPU for best results | High-volume OCR processing, specialized document layouts |

### 8.3 Java OCR Libraries in Detail

| Library | Strengths | Limitations | Best Use Cases |
|---------|-----------|-------------|---------------|
| **Tess4J** | Java wrapper for Tesseract, mature | Same limitations as Tesseract, JNI overhead | Enterprise Java applications requiring basic OCR |
| **Apache PDFBox** | PDF parsing, text extraction, manipulation | Limited to PDFs, not for general images | PDF-specific document processing workflows |
| **Aspose.OCR** | High accuracy, extensive format support | Commercial, licensing costs | Enterprise document processing with SLAs |
| **ABBYY FineReader Engine** | Industry-leading accuracy, document analysis | Expensive, complex integration | High-volume, mission-critical document processing |
| **Java OCR** | Simple API, lightweight | Limited features, lower accuracy | Basic OCR needs in Java applications |
| **AsprisePDF** | PDF and image processing, OCR capabilities | Commercial licensing | PDF-centric document workflows |

### 8.4 Recommendation: Python for OCR Extraction

Based on the comprehensive analysis above, **Python is recommended** as the more suitable language for OCR extraction work for the following reasons:

1. **Ecosystem Advantages:**
   - Richer ecosystem of modern OCR and NLP libraries
   - Better integration with cloud-based OCR services like AWS Textract
   - More extensive community support and examples
   - Faster development cycles for OCR solutions

2. **Technical Considerations:**
   - Simpler integration with machine learning models for document classification
   - More accessible image processing capabilities
   - Better support for modern NLP techniques for context extraction
   - Easier prototyping and iteration for complex document processing

3. **Implementation Efficiency:**
   - Less boilerplate code required for OCR pipelines
   - More straightforward integration with AWS services
   - Faster time-to-market for document processing solutions
   - Simplified deployment options for serverless architectures

4. **Specific Advantages for Document Processing:**
   - Python's AWS Textract client provides more intuitive access to document analysis features
   - Better support for document understanding through libraries like spaCy and Transformers
   - More flexible handling of document structure and metadata
   - Easier implementation of confidence scoring mechanisms

While Java offers advantages in performance, type safety, and enterprise deployment, these benefits are outweighed by Python's significant advantages in development speed, library ecosystem, and integration capabilities for OCR extraction work.

For high-volume production systems where performance is critical, a hybrid approach could be considered: using Python for the OCR extraction and document understanding components, while implementing high-throughput processing pipelines in Java.

### 8.5 Implementation Strategy with Python

The recommended implementation strategy using Python includes:

1. **Core OCR Processing:**
   - AWS Textract for primary OCR and document analysis
   - Fallback to pytesseract for offline processing or specific use cases

2. **Image Pre-processing:**
   - OpenCV for image enhancement and normalization
   - Pillow for basic image manipulation and format conversion

3. **Document Understanding:**
   - spaCy for entity recognition and text analysis
   - Transformers (BERT) for context-aware field extraction
   - Custom rule-based extractors for structured documents

4. **API and Service Layer:**
   - FastAPI for high-performance API endpoints
   - Pydantic for data validation and schema enforcement
   - asyncio for concurrent processing of multiple documents

5. **Deployment:**
   - Docker containers for consistent environments
   - AWS Lambda for serverless processing of individual documents
   - ECS/EKS for scalable document processing pipelines
