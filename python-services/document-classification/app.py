"""
Document Classification Service for OCR Processing

This service is responsible for classifying documents into predefined categories
using machine learning models and heuristic rules.
"""

import os
import json
import logging
import numpy as np
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
import boto3
from datetime import datetime
import io
import pickle
from PIL import Image
import cv2
import tensorflow as tf
from transformers import LayoutLMModel, LayoutLMTokenizer
import torch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Classification Service",
    description="Service for classifying documents into predefined categories",
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

MODEL_DIR = os.getenv("MODEL_DIR", "/app/models")
os.makedirs(MODEL_DIR, exist_ok=True)

class DocumentType(str, Enum):
    PASSPORT = "passport"
    INVOICE = "invoice"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    MEDICAL_RECORD = "medical_record"
    LEGAL_DOCUMENT = "legal_document"
    UNKNOWN = "unknown"

class ClassificationRequest(BaseModel):
    document_id: str
    file_path: str
    metadata: Optional[Dict[str, Any]] = None

class ClassificationResponse(BaseModel):
    document_id: str
    document_type: DocumentType
    confidence: float
    classification_details: Dict[str, Any]

def load_models():
    """Load classification models."""
    models = {}
    
    try:
        models["image_classifier"] = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(len(DocumentType), activation='softmax')
        ])
        
        if torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")
        
        models["layout_model"] = {
            "tokenizer": LayoutLMTokenizer.from_pretrained("microsoft/layoutlm-base-uncased"),
            "model": LayoutLMModel.from_pretrained("microsoft/layoutlm-base-uncased").to(device),
            "device": device
        }
        
        logger.info("Models loaded successfully")
        return models
    
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        return {}

models = load_models()

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

def preprocess_image(image_data):
    """Preprocess image for classification."""
    try:
        if isinstance(image_data, str):
            image = Image.open(image_data)
        else:
            image = Image.open(image_data)
        
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        image = image.resize((224, 224))
        
        img_array = np.array(image) / 255.0
        
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image preprocessing error: {str(e)}")

def classify_with_cnn(image_data):
    """Classify document using CNN model."""
    if "image_classifier" not in models:
        return None, 0.0
    
    try:
        img_array = preprocess_image(image_data)
        
        predictions = models["image_classifier"].predict(img_array)
        
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        
        document_types = list(DocumentType)
        document_type = document_types[class_idx]
        
        return document_type, confidence
    
    except Exception as e:
        logger.error(f"Error classifying with CNN: {str(e)}")
        return None, 0.0

def classify_with_layout(image_data):
    """Classify document using LayoutLM model."""
    if "layout_model" not in models:
        return None, 0.0
    
    try:
        
        return DocumentType.UNKNOWN, 0.0
    
    except Exception as e:
        logger.error(f"Error classifying with LayoutLM: {str(e)}")
        return None, 0.0

def classify_with_rules(image_data):
    """Classify document using rule-based heuristics."""
    try:
        if isinstance(image_data, str):
            img = cv2.imread(image_data)
        else:
            image_data.seek(0)
            file_bytes = np.asarray(bytearray(image_data.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        height, width, _ = img.shape
        aspect_ratio = width / height
        
        
        if 1.4 <= aspect_ratio <= 1.5:
            return DocumentType.PASSPORT, 0.7
        
        elif 1.55 <= aspect_ratio <= 1.65:
            return DocumentType.DRIVERS_LICENSE, 0.6
        
        elif aspect_ratio < 0.8:
            edges = cv2.Canny(img, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
            
            if lines is not None and len(lines) > 10:
                return DocumentType.INVOICE, 0.5
            else:
                return DocumentType.BANK_STATEMENT, 0.4
        
        return DocumentType.UNKNOWN, 0.3
    
    except Exception as e:
        logger.error(f"Error in rule-based classification: {str(e)}")
        return DocumentType.UNKNOWN, 0.1

def ensemble_classification(image_data):
    """Combine multiple classification methods."""
    results = []
    
    cnn_type, cnn_conf = classify_with_cnn(image_data)
    if cnn_type:
        results.append((cnn_type, cnn_conf, "cnn"))
    
    layout_type, layout_conf = classify_with_layout(image_data)
    if layout_type:
        results.append((layout_type, layout_conf, "layout"))
    
    rule_type, rule_conf = classify_with_rules(image_data)
    if rule_type:
        results.append((rule_type, rule_conf, "rules"))
    
    if not results:
        return DocumentType.UNKNOWN, 0.0, "fallback"
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results[0]

@app.post("/classify", response_model=ClassificationResponse)
async def classify_document(request: ClassificationRequest = Body(...)):
    """
    Classify a document into predefined categories.
    
    This endpoint accepts a document file path and metadata,
    and returns the document type classification with confidence score.
    """
    try:
        image_data = download_from_s3(request.file_path)
        
        doc_type, confidence, method = ensemble_classification(image_data)
        
        classification_details = {
            "classification_method": method,
            "confidence_score": confidence,
            "possible_types": [
                {"type": doc_type, "confidence": confidence}
            ]
        }
        
        return ClassificationResponse(
            document_id=request.document_id,
            document_type=doc_type,
            confidence=confidence,
            classification_details=classification_details
        )
            
    except Exception as e:
        logger.error(f"Error classifying document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
