"""
OCR Processing Service for Document Processing

This service handles the extraction of text and structure from documents
using AWS Textract and other OCR engines.
"""

import os
import json
import logging
import boto3
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
import io
from datetime import datetime
import pytesseract
from PIL import Image
import numpy as np
import cv2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OCR Processing Service",
    description="Service for extracting text and structure from documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
textract_client = boto3.client('textract', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)

class DocumentType(str, Enum):
    PASSPORT = "passport"
    INVOICE = "invoice"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    MEDICAL_RECORD = "medical_record"
    LEGAL_DOCUMENT = "legal_document"
    UNKNOWN = "unknown"

class OCRRequest(BaseModel):
    document_id: str
    file_path: str
    document_type: Optional[DocumentType] = None
    ocr_engine: Optional[str] = "textract"  # textract, tesseract, or auto
    enhanced_features: Optional[bool] = True

class OCRResponse(BaseModel):
    document_id: str
    document_type: DocumentType
    text_content: str
    blocks: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    forms: List[Dict[str, Any]]
    pages: int
    processing_details: Dict[str, Any]

def download_from_s3(s3_path):
    """Download a file from S3."""
    if not s3_path.startswith("s3://"):
        return s3_path  # Not an S3 path
    
    path_parts = s3_path.replace("s3://", "").split("/")
    bucket = path_parts[0]
    key = "/".join(path_parts[1:])
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return io.BytesIO(response['Body'].read())
    
    except Exception as e:
        logger.error(f"Error downloading from S3: {str(e)}")
        raise HTTPException(status_code=500, detail=f"S3 download error: {str(e)}")

def process_with_textract(document_data, document_type, enhanced_features=True):
    """Process document with AWS Textract."""
    try:
        features = []
        
        if enhanced_features:
            features = ["TABLES", "FORMS"]
            
            if document_type in [DocumentType.INVOICE, DocumentType.BANK_STATEMENT]:
                features.append("QUERIES")
        
        if features:
            response = textract_client.analyze_document(
                Document={'Bytes': document_data.getvalue() if hasattr(document_data, 'getvalue') else document_data},
                FeatureTypes=features
            )
        else:
            response = textract_client.detect_document_text(
                Document={'Bytes': document_data.getvalue() if hasattr(document_data, 'getvalue') else document_data}
            )
        
        text_content = ""
        blocks = []
        tables = []
        forms = []
        
        if 'Blocks' in response:
            blocks = response['Blocks']
            
            for block in blocks:
                if block['BlockType'] == 'LINE' and 'Text' in block:
                    text_content += block['Text'] + "\n"
        
        if 'Tables' in response:
            tables = response['Tables']
        
        if 'Forms' in response:
            forms = response['Forms']
        
        pages = 1
        if 'DocumentMetadata' in response and 'Pages' in response['DocumentMetadata']:
            pages = response['DocumentMetadata']['Pages']
        
        return {
            "text_content": text_content,
            "blocks": blocks,
            "tables": tables,
            "forms": forms,
            "pages": pages,
            "engine": "textract",
            "enhanced_features": enhanced_features
        }
    
    except Exception as e:
        logger.error(f"Error processing with Textract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Textract processing error: {str(e)}")

def process_with_tesseract(document_data, document_type):
    """Process document with Tesseract OCR."""
    try:
        if isinstance(document_data, str):
            image = Image.open(document_data)
        else:
            image = Image.open(document_data)
        
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        img_array = np.array(image)
        
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        text_content = pytesseract.image_to_string(gray)
        
        boxes = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        blocks = []
        for i in range(len(boxes['text'])):
            if boxes['text'][i].strip():
                block = {
                    'BlockType': 'LINE',
                    'Text': boxes['text'][i],
                    'Confidence': float(boxes['conf'][i]) if boxes['conf'][i] > 0 else 50.0,
                    'Geometry': {
                        'BoundingBox': {
                            'Width': boxes['width'][i] / image.width,
                            'Height': boxes['height'][i] / image.height,
                            'Left': boxes['left'][i] / image.width,
                            'Top': boxes['top'][i] / image.height
                        }
                    }
                }
                blocks.append(block)
        
        return {
            "text_content": text_content,
            "blocks": blocks,
            "tables": [],  # Tesseract doesn't provide table detection
            "forms": [],   # Tesseract doesn't provide form detection
            "pages": 1,    # Assume single page for image
            "engine": "tesseract",
            "enhanced_features": False
        }
    
    except Exception as e:
        logger.error(f"Error processing with Tesseract: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tesseract processing error: {str(e)}")

def select_ocr_engine(document_data, document_type, requested_engine):
    """Select the appropriate OCR engine based on document type and requested engine."""
    if requested_engine == "textract":
        return "textract"
    elif requested_engine == "tesseract":
        return "tesseract"
    else:  # Auto selection
        if document_type in [DocumentType.INVOICE, DocumentType.BANK_STATEMENT, DocumentType.LEGAL_DOCUMENT]:
            return "textract"
        else:
            return "tesseract"

@app.post("/process", response_model=OCRResponse)
async def process_document(request: OCRRequest = Body(...)):
    """
    Process a document with OCR to extract text and structure.
    
    This endpoint accepts a document file path and metadata,
    and returns the extracted text and document structure.
    """
    try:
        document_data = download_from_s3(request.file_path)
        
        engine = select_ocr_engine(document_data, request.document_type, request.ocr_engine)
        
        if engine == "textract":
            enhanced_features = True if request.enhanced_features is None else request.enhanced_features
            result = process_with_textract(document_data, request.document_type, enhanced_features)
        else:
            result = process_with_tesseract(document_data, request.document_type)
        
        return OCRResponse(
            document_id=request.document_id,
            document_type=request.document_type or DocumentType.UNKNOWN,
            text_content=result["text_content"],
            blocks=result["blocks"],
            tables=result["tables"],
            forms=result["forms"],
            pages=result["pages"],
            processing_details={
                "engine": result["engine"],
                "enhanced_features": result["enhanced_features"],
                "processing_timestamp": datetime.now().isoformat()
            }
        )
            
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
