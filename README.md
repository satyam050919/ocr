# Textract Document Processor API

A scalable backend service built with FastAPI that processes OCR responses from AWS Textract. The service extracts and normalizes structured data from different document types such as passports, invoices, driver's licenses, and utility bills.

## Architecture Overview

The system follows a modular, pluggable architecture with the following key components:

1. **Document Type-Aware Processing**:
   - Modular architecture with dedicated parsers for each document type
   - Routing layer that decides between rule-based extraction and ML-based extraction
   - Document type classification using metadata and heuristics

2. **Validation and Confidence Scoring**:
   - Hard blocks (errors) for critical missing fields
   - Warnings for low confidence scores
   - Detailed logging for observability

3. **Scalability and Extensibility**:
   - Pluggable strategy pattern for document processors
   - Message-driven architecture for scaling OCR processing jobs
   - Clean interfaces for ML models and rule logic

4. **Microfrontend UI**:
   - Human-in-the-loop validation
   - Document visualization with overlaid extracted fields
   - Highlighting of low-confidence fields and validation errors
   - Manual correction capabilities

## Features

- Process documents using AWS Textract OCR
- Auto-detect document types
- Extract structured data based on document type
- Normalize data into consistent formats
- Asynchronous processing with job tracking
- Validation with confidence scoring
- Human-in-the-loop validation for low-confidence extractions
- RESTful API with Swagger documentation

## Supported Document Types

- **Passports**:
  - MRZ (Machine Readable Zone)
  - Personal information (name, date of birth, etc.)
  - Document number and expiry date

- **Invoices**:
  - Invoice number and date
  - Vendor information
  - Line items and total amount
  - Payment details

- **Driver's Licenses**:
  - License number
  - Personal information
  - Issue and expiry dates
  - License class and restrictions

- **Utility Bills**:
  - Account number
  - Service address
  - Billing period
  - Amount due and due date

- **Generic documents** (fallback)

## API Endpoints

### Document Processing

#### Process Document (Synchronous)

```
POST /documents/process
```

Process a single document and extract structured data.

**Parameters:**
- `file`: The document file to process (PDF, PNG, JPEG)
- `document_type`: (Optional) Document type to process as
- `auto_detect_type`: Whether to auto-detect document type (default: true)

**Response:**
```json
{
  "document_type": "passport",
  "fields": [
    {
      "name": "passport_number",
      "value": "AB123456",
      "confidence": 95.5
    },
    {
      "name": "surname",
      "value": "DOE",
      "confidence": 98.2
    },
    ...
  ],
  "raw_text": "...",
  "confidence_score": 92.3,
  "metadata": {
    "source": "textract"
  }
}
```

#### Process Document (Asynchronous)

```
POST /processing/async
```

Process a document asynchronously and receive a job ID for tracking.

**Parameters:**
- `file`: The document file to process (PDF, PNG, JPEG)
- `document_type`: (Optional) Document type to process as
- `auto_detect_type`: Whether to auto-detect document type (default: true)

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

### Job Management

#### List Jobs

```
GET /processing/jobs
```

List all processing jobs.

#### Get Job Status

```
GET /processing/jobs/{job_id}
```

Get the status of a specific job.

#### Get Job Result

```
GET /processing/jobs/{job_id}/result
```

Get the result of a completed job.

### Human Validation

```
POST /processing/jobs/{job_id}/validate
```

Submit human validation for a job requiring manual review.

## Setup and Deployment

### Prerequisites

- Python 3.12+
- AWS account with Textract access
- AWS credentials configured
- Docker (optional, for containerized deployment)

### Local Development

1. Install dependencies:
```
poetry install
```

2. Set up AWS credentials:
```
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

3. Run the development server:
```
poetry run fastapi dev app/main.py
```

4. Access the API documentation at http://localhost:8000/docs

### Docker Deployment

1. Build and run the Docker container:
```
./deploy.sh
```

Or manually:
```
docker build -t textract-processor:latest .
docker run -d -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your_access_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret_key \
  --name textract-processor \
  textract-processor:latest
```

## Usage Examples

### Process a Passport (Synchronous)

```bash
curl -X POST "http://localhost:8000/documents/process" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@passport.jpg" \
  -F "document_type=passport" \
  -F "auto_detect_type=true"
```

### Process an Invoice with Auto-detection (Asynchronous)

```bash
curl -X POST "http://localhost:8000/processing/async" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf" \
  -F "auto_detect_type=true"
```

### Check Job Status

```bash
curl -X GET "http://localhost:8000/processing/jobs/550e8400-e29b-41d4-a716-446655440000" \
  -H "accept: application/json"
```
