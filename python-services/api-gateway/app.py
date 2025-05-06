"""
API Gateway Service for Document Processing Microservices

This service acts as the entry point for the document processing system,
routing requests to the appropriate microservices.
"""

import os
import json
import logging
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
import aiohttp
import asyncio
from datetime import datetime
import boto3
from kafka import KafkaProducer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Processing API Gateway",
    description="API Gateway for OCR Document Processing Microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_ENDPOINTS = {
    "document_ingestion": os.getenv("DOCUMENT_INGESTION_SERVICE", "http://document-ingestion-service:8001"),
    "document_classification": os.getenv("DOCUMENT_CLASSIFICATION_SERVICE", "http://document-classification-service:8002"),
    "ocr_processing": os.getenv("OCR_PROCESSING_SERVICE", "http://ocr-processing-service:8003"),
    "document_validation": os.getenv("DOCUMENT_VALIDATION_SERVICE", "http://document-validation-service:8004"),
    "document_tagging": os.getenv("DOCUMENT_TAGGING_SERVICE", "http://document-tagging-service:8005"),
    "attribute_extraction": os.getenv("ATTRIBUTE_EXTRACTION_SERVICE", "http://attribute-extraction-service:8006"),
    "document_splitting": os.getenv("DOCUMENT_SPLITTING_SERVICE", "http://document-splitting-service:8007"),
    "confidence_scoring": os.getenv("CONFIDENCE_SCORING_SERVICE", "http://confidence-scoring-service:8008"),
    "document_storage": os.getenv("DOCUMENT_STORAGE_SERVICE", "http://document-storage-service:8009"),
}

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
DOCUMENT_TOPIC = os.getenv("DOCUMENT_TOPIC", "document-processing")

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    logger.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
except Exception as e:
    logger.error(f"Failed to connect to Kafka: {str(e)}")
    producer = None

S3_BUCKET = os.getenv("S3_BUCKET", "document-processing")
s3_client = boto3.client('s3')

class DocumentType(str, Enum):
    PASSPORT = "passport"
    INVOICE = "invoice"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    MEDICAL_RECORD = "medical_record"
    LEGAL_DOCUMENT = "legal_document"
    UNKNOWN = "unknown"

class ProcessingMode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"

class ProcessingRequest(BaseModel):
    document_id: Optional[str] = None
    document_type: Optional[DocumentType] = None
    processing_mode: ProcessingMode = ProcessingMode.ASYNC
    confidence_threshold: float = 0.7
    services: List[str] = ["all"]

class ProcessingResponse(BaseModel):
    document_id: str
    status: str
    message: str
    processing_details: Optional[Dict[str, Any]] = None

async def call_service(service_name: str, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Call a microservice endpoint."""
    if service_name not in SERVICE_ENDPOINTS:
        raise ValueError(f"Unknown service: {service_name}")
    
    url = f"{SERVICE_ENDPOINTS[service_name]}/{endpoint}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    logger.error(f"Error calling {service_name}: {error_text}")
                    raise HTTPException(status_code=response.status, detail=f"Service error: {error_text}")
                
                return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Error connecting to {service_name}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {service_name}")

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

async def process_document_async(document_id: str, file_path: str, request: ProcessingRequest):
    """Process a document asynchronously through the microservices pipeline."""
    try:
        message = {
            "document_id": document_id,
            "file_path": file_path,
            "document_type": request.document_type,
            "confidence_threshold": request.confidence_threshold,
            "services": request.services,
            "timestamp": datetime.now().isoformat()
        }
        
        send_to_kafka(DOCUMENT_TOPIC, message)
        logger.info(f"Document {document_id} sent for async processing")
        
    except Exception as e:
        logger.error(f"Error in async processing for document {document_id}: {str(e)}")

async def process_document_sync(document_id: str, file_path: str, request: ProcessingRequest) -> Dict[str, Any]:
    """Process a document synchronously through the microservices pipeline."""
    try:
        classification_result = await call_service(
            "document_classification", 
            "classify", 
            {"document_id": document_id, "file_path": file_path}
        )
        
        document_type = classification_result.get("document_type", request.document_type or DocumentType.UNKNOWN)
        
        ocr_result = await call_service(
            "ocr_processing",
            "process",
            {"document_id": document_id, "file_path": file_path, "document_type": document_type}
        )
        
        validation_result = await call_service(
            "document_validation",
            "validate",
            {
                "document_id": document_id, 
                "ocr_result": ocr_result,
                "document_type": document_type,
                "confidence_threshold": request.confidence_threshold
            }
        )
        
        extraction_result = await call_service(
            "attribute_extraction",
            "extract",
            {
                "document_id": document_id,
                "ocr_result": ocr_result,
                "document_type": document_type,
                "validation_result": validation_result
            }
        )
        
        tagging_result = await call_service(
            "document_tagging",
            "tag",
            {
                "document_id": document_id,
                "ocr_result": ocr_result,
                "extraction_result": extraction_result,
                "document_type": document_type
            }
        )
        
        confidence_result = await call_service(
            "confidence_scoring",
            "score",
            {
                "document_id": document_id,
                "extraction_result": extraction_result,
                "validation_result": validation_result,
                "confidence_threshold": request.confidence_threshold
            }
        )
        
        storage_result = await call_service(
            "document_storage",
            "store",
            {
                "document_id": document_id,
                "file_path": file_path,
                "ocr_result": ocr_result,
                "extraction_result": extraction_result,
                "validation_result": validation_result,
                "tagging_result": tagging_result,
                "confidence_result": confidence_result
            }
        )
        
        return {
            "document_id": document_id,
            "document_type": document_type,
            "validation": validation_result,
            "extraction": extraction_result,
            "tagging": tagging_result,
            "confidence": confidence_result,
            "storage": storage_result
        }
        
    except Exception as e:
        logger.error(f"Error in sync processing for document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/documents/process", response_model=ProcessingResponse)
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request_data: str = Form(...),
):
    """
    Process a document through the microservices pipeline.
    
    This endpoint accepts a document file and processing parameters,
    and routes the document through the appropriate microservices.
    """
    try:
        request = ProcessingRequest.parse_raw(request_data)
        
        document_id = request.document_id or str(uuid.uuid4())
        
        file_content = await file.read()
        file_name = f"{document_id}/{file.filename}"
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=file_name,
            Body=file_content
        )
        file_path = f"s3://{S3_BUCKET}/{file_name}"
        
        if request.processing_mode == ProcessingMode.ASYNC:
            background_tasks.add_task(
                process_document_async,
                document_id,
                file_path,
                request
            )
            
            return ProcessingResponse(
                document_id=document_id,
                status="processing",
                message="Document submitted for processing",
                processing_details={"file_path": file_path}
            )
        else:
            result = await process_document_sync(document_id, file_path, request)
            
            return ProcessingResponse(
                document_id=document_id,
                status="completed",
                message="Document processing completed",
                processing_details=result
            )
            
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/documents/{document_id}/status")
async def get_document_status(document_id: str):
    """Get the processing status of a document."""
    try:
        result = await call_service(
            "document_storage",
            f"documents/{document_id}",
            {}
        )
        
        return result
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
