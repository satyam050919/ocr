"""
Document Tagging Service for OCR Processing

This service is responsible for tagging documents based on their content,
metadata, and extracted attributes.
"""

import os
import json
import logging
import numpy as np
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from datetime import datetime
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Tagging Service",
    description="Service for tagging documents based on content and metadata",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentType(str, Enum):
    PASSPORT = "passport"
    INVOICE = "invoice"
    DRIVERS_LICENSE = "drivers_license"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    MEDICAL_RECORD = "medical_record"
    LEGAL_DOCUMENT = "legal_document"
    UNKNOWN = "unknown"

class TagCategory(str, Enum):
    DOCUMENT_TYPE = "document_type"
    CONTENT = "content"
    METADATA = "metadata"
    SECURITY = "security"
    QUALITY = "quality"
    CUSTOM = "custom"

class Tag(BaseModel):
    name: str
    category: TagCategory
    confidence: float
    source: str  # rule, ml, manual
    metadata: Optional[Dict[str, Any]] = None

class TaggingRequest(BaseModel):
    document_id: str
    document_type: Optional[DocumentType] = None
    ocr_result: Dict[str, Any]
    extraction_result: Optional[Dict[str, Any]] = None
    custom_tags: Optional[List[Tag]] = None

class TaggingResponse(BaseModel):
    document_id: str
    tags: List[Tag]
    processing_details: Dict[str, Any]

TAG_RULES = {
    DocumentType.PASSPORT: [
        {"pattern": r"passport", "tag": "passport", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"nationality", "tag": "nationality", "category": TagCategory.CONTENT},
        {"pattern": r"visa", "tag": "visa", "category": TagCategory.CONTENT},
        {"pattern": r"expir", "tag": "expiration", "category": TagCategory.CONTENT},
    ],
    DocumentType.INVOICE: [
        {"pattern": r"invoice", "tag": "invoice", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"total", "tag": "financial", "category": TagCategory.CONTENT},
        {"pattern": r"amount", "tag": "financial", "category": TagCategory.CONTENT},
        {"pattern": r"tax", "tag": "tax", "category": TagCategory.CONTENT},
        {"pattern": r"payment", "tag": "payment", "category": TagCategory.CONTENT},
    ],
    DocumentType.DRIVERS_LICENSE: [
        {"pattern": r"driver", "tag": "drivers_license", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"license", "tag": "license", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"class", "tag": "license_class", "category": TagCategory.CONTENT},
        {"pattern": r"restriction", "tag": "restrictions", "category": TagCategory.CONTENT},
    ],
    DocumentType.UTILITY_BILL: [
        {"pattern": r"utility", "tag": "utility", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"bill", "tag": "bill", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"electricity", "tag": "electricity", "category": TagCategory.CONTENT},
        {"pattern": r"water", "tag": "water", "category": TagCategory.CONTENT},
        {"pattern": r"gas", "tag": "gas", "category": TagCategory.CONTENT},
    ],
    DocumentType.BANK_STATEMENT: [
        {"pattern": r"statement", "tag": "statement", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"bank", "tag": "bank", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"balance", "tag": "balance", "category": TagCategory.CONTENT},
        {"pattern": r"deposit", "tag": "deposit", "category": TagCategory.CONTENT},
        {"pattern": r"withdraw", "tag": "withdrawal", "category": TagCategory.CONTENT},
    ],
    DocumentType.MEDICAL_RECORD: [
        {"pattern": r"medical", "tag": "medical", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"patient", "tag": "patient", "category": TagCategory.CONTENT},
        {"pattern": r"diagnosis", "tag": "diagnosis", "category": TagCategory.CONTENT},
        {"pattern": r"prescription", "tag": "prescription", "category": TagCategory.CONTENT},
    ],
    DocumentType.LEGAL_DOCUMENT: [
        {"pattern": r"legal", "tag": "legal", "category": TagCategory.DOCUMENT_TYPE},
        {"pattern": r"contract", "tag": "contract", "category": TagCategory.CONTENT},
        {"pattern": r"agreement", "tag": "agreement", "category": TagCategory.CONTENT},
        {"pattern": r"party", "tag": "party", "category": TagCategory.CONTENT},
        {"pattern": r"clause", "tag": "clause", "category": TagCategory.CONTENT},
    ],
    DocumentType.UNKNOWN: [
        {"pattern": r"confidential", "tag": "confidential", "category": TagCategory.SECURITY},
        {"pattern": r"private", "tag": "private", "category": TagCategory.SECURITY},
        {"pattern": r"draft", "tag": "draft", "category": TagCategory.QUALITY},
        {"pattern": r"final", "tag": "final", "category": TagCategory.QUALITY},
    ]
}

def apply_rule_based_tagging(text: str, document_type: DocumentType) -> List[Tag]:
    """Apply rule-based tagging to document text."""
    tags = []
    
    type_rules = TAG_RULES.get(document_type, [])
    
    generic_rules = TAG_RULES.get(DocumentType.UNKNOWN, [])
    all_rules = type_rules + generic_rules
    
    for rule in all_rules:
        pattern = rule["pattern"]
        tag_name = rule["tag"]
        category = rule["category"]
        
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            confidence = min(0.9, 0.5 + (len(matches) * 0.1))
            
            tag = Tag(
                name=tag_name,
                category=category,
                confidence=confidence,
                source="rule",
                metadata={"matches": len(matches), "rule_pattern": pattern}
            )
            
            tags.append(tag)
    
    return tags

def apply_ml_based_tagging(text: str) -> List[Tag]:
    """Apply ML-based tagging to document text."""
    tags = []
    
    try:
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform([text])
        
        feature_names = vectorizer.get_feature_names_out()
        
        try:
            try:
                scores = np.zeros(len(feature_names))
                if hasattr(tfidf_matrix, 'data') and hasattr(tfidf_matrix, 'indices'):
                    for i, j, v in zip(np.zeros(len(tfidf_matrix.data), dtype=int), 
                                      tfidf_matrix.indices, 
                                      tfidf_matrix.data):
                        scores[j] = v
                else:
                    scores = np.array(tfidf_matrix)[0]
            except Exception as inner_e:
                logger.warning(f"Inner error converting sparse matrix: {str(inner_e)}")
                scores = np.zeros(len(feature_names))
        except Exception as e:
            logger.warning(f"Error converting sparse matrix: {str(e)}")
            scores = np.zeros(len(feature_names))
        
        sorted_indices = np.argsort(scores)[::-1]
        
        top_keywords = [(feature_names[i], scores[i]) for i in sorted_indices[:10] if scores[i] > 0]
        
        for keyword, score in top_keywords:
            tag = Tag(
                name=keyword,
                category=TagCategory.CONTENT,
                confidence=float(score),
                source="ml",
                metadata={"tfidf_score": float(score)}
            )
            
            tags.append(tag)
        
        if len(tags) > 1:
            tag_names = [tag.name for tag in tags]
            
            cluster_vectorizer = TfidfVectorizer()
            cluster_matrix = cluster_vectorizer.fit_transform(tag_names)
            
            try:
                cluster_dense = np.zeros((len(tag_names), cluster_vectorizer.get_feature_names_out().shape[0]))
                cx = cluster_matrix.tocoo()
                for i, j, v in zip(cx.row, cx.col, cx.data):
                    cluster_dense[i, j] = v
                
                clustering = DBSCAN(eps=0.5, min_samples=1).fit(cluster_dense)
                
                for i, tag in enumerate(tags):
                    tag.metadata = tag.metadata or {}
                    tag.metadata["cluster"] = int(clustering.labels_[i])
            except Exception as e:
                logger.warning(f"Error in clustering: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in ML-based tagging: {str(e)}")
    
    return tags

def merge_tags(tags: List[Tag]) -> List[Tag]:
    """Merge duplicate tags and combine confidence scores."""
    tag_dict = {}
    
    for tag in tags:
        key = f"{tag.name}:{tag.category}"
        
        if key in tag_dict:
            existing_tag = tag_dict[key]
            
            combined_confidence = (existing_tag.confidence + tag.confidence) / 2
            
            combined_metadata = existing_tag.metadata or {}
            if tag.metadata:
                for k, v in tag.metadata.items():
                    if k in combined_metadata:
                        if isinstance(v, (int, float)) and isinstance(combined_metadata[k], (int, float)):
                            combined_metadata[k] = max(combined_metadata[k], v)
                        else:
                            combined_metadata[k] = v
                    else:
                        combined_metadata[k] = v
            
            sources = set([existing_tag.source, tag.source])
            combined_source = ",".join(sources)
            
            updated_tag = Tag(
                name=tag.name,
                category=tag.category,
                confidence=combined_confidence,
                source=combined_source,
                metadata=combined_metadata
            )
            
            tag_dict[key] = updated_tag
        else:
            tag_dict[key] = tag
    
    return list(tag_dict.values())

@app.post("/tag", response_model=TaggingResponse)
async def tag_document(request: TaggingRequest = Body(...)):
    """
    Tag a document based on its content and metadata.
    
    This endpoint accepts OCR results and extracted attributes,
    and returns a list of tags for the document.
    """
    try:
        text_content = request.ocr_result.get("text_content", "")
        
        rule_tags = apply_rule_based_tagging(
            text_content, 
            request.document_type or DocumentType.UNKNOWN
        )
        
        ml_tags = apply_ml_based_tagging(text_content)
        
        all_tags = rule_tags + ml_tags
        
        if request.custom_tags:
            all_tags.extend(request.custom_tags)
        
        merged_tags = merge_tags(all_tags)
        
        sorted_tags = sorted(merged_tags, key=lambda x: x.confidence, reverse=True)
        
        return TaggingResponse(
            document_id=request.document_id,
            tags=sorted_tags,
            processing_details={
                "rule_tags_count": len(rule_tags),
                "ml_tags_count": len(ml_tags),
                "custom_tags_count": len(request.custom_tags) if request.custom_tags else 0,
                "total_tags_count": len(sorted_tags),
                "processing_timestamp": datetime.now().isoformat()
            }
        )
            
    except Exception as e:
        logger.error(f"Error tagging document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Tagging error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
