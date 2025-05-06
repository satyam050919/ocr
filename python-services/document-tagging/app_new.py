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
from collections import Counter

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

STOP_WORDS = set([
    "a", "an", "the", "and", "or", "but", "if", "because", "as", "what",
    "when", "where", "how", "all", "any", "both", "each", "few", "more",
    "most", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should",
    "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren", "couldn",
    "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma", "mightn", "mustn",
    "needn", "shan", "shouldn", "wasn", "weren", "won", "wouldn", "i", "me",
    "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her",
    "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "this", "that", "these", "those", "am", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "to", "from", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "why", "how", "with",
    "about", "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "up", "down", "for", "by", "at", "of"
])

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
    """Apply ML-based tagging to document text using simple keyword extraction."""
    tags = []
    
    try:
        words = re.findall(r'\b\w+\b', text.lower())
        
        filtered_words = [word for word in words if word not in STOP_WORDS and len(word) > 2]
        
        word_counts = Counter(filtered_words)
        
        most_common = word_counts.most_common(15)
        
        total_count = sum(count for _, count in most_common) if most_common else 1
        
        for word, count in most_common:
            score = min(0.9, count / (total_count * 0.5))
            
            tag = Tag(
                name=word,
                category=TagCategory.CONTENT,
                confidence=float(score),
                source="ml",
                metadata={"frequency": count, "score": float(score)}
            )
            
            tags.append(tag)
        
        if len(filtered_words) > 1:
            bigrams = [f"{filtered_words[i]} {filtered_words[i+1]}" for i in range(len(filtered_words)-1)]
            bigram_counts = Counter(bigrams)
            most_common_bigrams = bigram_counts.most_common(5)
            
            for bigram, count in most_common_bigrams:
                if count > 1:  # Only add if it appears more than once
                    score = min(0.8, count / (total_count * 0.3))
                    
                    tag = Tag(
                        name=bigram,
                        category=TagCategory.CONTENT,
                        confidence=float(score),
                        source="ml",
                        metadata={"frequency": count, "score": float(score), "type": "bigram"}
                    )
                    
                    tags.append(tag)
        
        if len(tags) > 1:
            clusters = {}
            for tag in tags:
                prefix = tag.name[:4] if len(tag.name) > 4 else tag.name
                if prefix not in clusters:
                    clusters[prefix] = []
                clusters[prefix].append(tag)
            
            for cluster_id, cluster_tags in enumerate(clusters.values()):
                for tag in cluster_tags:
                    tag.metadata = tag.metadata or {}
                    tag.metadata["cluster"] = cluster_id
        
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
