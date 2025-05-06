"""
Document Ingestion Service for OCR Processing

This service handles the ingestion of documents into the processing pipeline.
It validates document formats, extracts basic metadata, and prepares documents
for further processing.
"""

import os
import json
import logging
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
import boto3
from datetime import datetime
import aiofiles
import asyncio
from kafka import KafkaProducer
import magic
import io

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Ingestion Service",
    description="Service for ingesting documents into the OCR processing pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

S3_BUCKET = os.getenv("S3_BUCKET", "document-processing")
s3_client = boto3.client('s3')

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
DOCUMENT_TOPIC = os.getenv("DOCUMENT_TOPIC", "document-ingestion")

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
except Exception as e:
    logger.error(f"Failed to connect to Kafka: {str(e)}")
    producer = None

TEMP_STORAGE_PATH = os.getenv("TEMP_STORAGE_PATH", "/tmp/document-ingestion")
os.makedirs(TEMP_STORAGE_PATH, exist_ok=True)

class DocumentType(str, Enum):
    PASSPORT = "passport"
    INVOICE = "invoice"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    MEDICAL_RECORD = "medical_record"
    LEGAL_DOCUMENT = "legal_document"
    UNKNOWN = "unknown"

class DocumentFormat(str, Enum):
    PDF = "pdf"
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    BMP = "bmp"
    HEIC = "heic"
    UNKNOWN = "unknown"

class DocumentMetadata(BaseModel):
    document_id: str
    original_filename: str
    file_size: int
    file_format: DocumentFormat
    mime_type: str
    page_count: Optional[int] = None
    document_type: Optional[DocumentType] = None
    upload_timestamp: str
    s3_path: Optional[str] = None
    local_path: Optional[str] = None

class IngestionResponse(BaseModel):
    document_id: str
    status: str
    message: str
    metadata: DocumentMetadata

def detect_file_format(file_content: bytes) -> tuple:
    """Detect file format and MIME type from file content."""
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_content)
    
    format_mapping = {
        "application/pdf": DocumentFormat.PDF,
        "image/jpeg": DocumentFormat.JPEG,
        "image/png": DocumentFormat.PNG,
        "image/tiff": DocumentFormat.TIFF,
        "image/bmp": DocumentFormat.BMP,
        "image/heic": DocumentFormat.HEIC
    }
    
    file_format = format_mapping.get(mime_type, DocumentFormat.UNKNOWN)
    
    return file_format, mime_type

def get_page_count(file_path: str, file_format: DocumentFormat) -> int:
    """Get the page count of a document."""
    if file_format == DocumentFormat.PDF:
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                return len(pdf.pages)
        except Exception as e:
            logger.error(f"Error getting PDF page count: {str(e)}")
            return 1
    else:
        return 1

def send_to_kafka(topic: str, message: Dict[str, Any]):
    """Send a message to Kafka."""
    if producer is None:
        logger.warning("Kafka producer not available, skipping message")
        return
    
    try:
        future = producer.send(topic, message)
        producer.flush()
        record_metadata = future.get(timeout=10)
        logger.info(f"Message sent to Kafka: {record_metadata.topic} [{record_metadata.partition}] @ {record_metadata.offset}")
    except Exception as e:
        logger.error(f"Error sending message to Kafka: {str(e)}")

@app.post("/ingest", response_model=IngestionResponse)
async def ingest_document(
    file: UploadFile = File(...),
    document_type: Optional[DocumentType] = None
):
    """
    Ingest a document into the processing pipeline.
    
    This endpoint accepts a document file, validates it, extracts basic metadata,
    and prepares it for further processing.
    """
    try:
        document_id = str(uuid.uuid4())
        
        file_content = await file.read()
        file_size = len(file_content)
        
        file_format, mime_type = detect_file_format(file_content)
        
        if file_format == DocumentFormat.UNKNOWN:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {mime_type}"
            )
        
        local_path = os.path.join(TEMP_STORAGE_PATH, f"{document_id}_{file.filename}")
        async with aiofiles.open(local_path, 'wb') as f:
            await f.write(file_content)
        
        page_count = get_page_count(local_path, file_format)
        
        s3_key = f"{document_id}/{file.filename}"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=io.BytesIO(file_content)
        )
        s3_path = f"s3://{S3_BUCKET}/{s3_key}"
        
        metadata = DocumentMetadata(
            document_id=document_id,
            original_filename=file.filename,
            file_size=file_size,
            file_format=file_format,
            mime_type=mime_type,
            page_count=page_count,
            document_type=document_type,
            upload_timestamp=datetime.now().isoformat(),
            s3_path=s3_path,
            local_path=local_path
        )
        
        message = {
            "document_id": document_id,
            "metadata": metadata.dict(),
            "timestamp": datetime.now().isoformat()
        }
        send_to_kafka(DOCUMENT_TOPIC, message)
        
        return IngestionResponse(
            document_id=document_id,
            status="ingested",
            message="Document successfully ingested",
            metadata=metadata
        )
            
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion error: {str(e)}")

@app.get("/documents/{document_id}")
async def get_document_metadata(document_id: str):
    """Get metadata for a specific document."""
    try:
        return {
            "document_id": document_id,
            "status": "not_found",
            "message": "Document metadata retrieval not implemented"
        }
    except Exception as e:
        logger.error(f"Error retrieving document metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
