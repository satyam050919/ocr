"""
Attribute Extraction Service for OCR Processing

This service is responsible for extracting structured attributes from documents
based on their type, OCR results, and classification.
"""

import os
import json
import logging
import re
from datetime import datetime
import numpy as np
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Attribute Extraction Service",
    description="Service for extracting structured attributes from documents",
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

class AttributeType(str, Enum):
    TEXT = "text"
    DATE = "date"
    NUMBER = "number"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    BOOLEAN = "boolean"
    ID = "id"
    NAME = "name"
    ADDRESS = "address"
    PHONE = "phone"
    EMAIL = "email"
    CUSTOM = "custom"

class ExtractionMethod(str, Enum):
    REGEX = "regex"
    KEYWORD = "keyword"
    POSITION = "position"
    TABLE = "table"
    FORM = "form"
    ML = "ml"
    CUSTOM = "custom"

class Attribute(BaseModel):
    name: str
    value: Any
    type: AttributeType
    confidence: float
    extraction_method: ExtractionMethod
    metadata: Optional[Dict[str, Any]] = None

class ExtractionRequest(BaseModel):
    document_id: str
    document_type: DocumentType
    ocr_result: Dict[str, Any]
    tags: Optional[List[Dict[str, Any]]] = None
    custom_extraction_rules: Optional[Dict[str, Any]] = None

class ExtractionResponse(BaseModel):
    document_id: str
    document_type: DocumentType
    attributes: List[Attribute]
    processing_details: Dict[str, Any]

EXTRACTION_RULES = {
    DocumentType.PASSPORT: [
        {
            "name": "passport_number",
            "type": AttributeType.ID,
            "method": ExtractionMethod.REGEX,
            "pattern": r"passport\s*no[.:]\s*([A-Z0-9]{6,12})",
            "confidence_base": 0.8
        },
        {
            "name": "full_name",
            "type": AttributeType.NAME,
            "method": ExtractionMethod.REGEX,
            "pattern": r"name[.:]\s*([A-Za-z\s]+)",
            "confidence_base": 0.7
        },
        {
            "name": "date_of_birth",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(birth|dob|born)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "nationality",
            "type": AttributeType.TEXT,
            "method": ExtractionMethod.REGEX,
            "pattern": r"nationality[.:]\s*([A-Za-z\s]+)",
            "confidence_base": 0.7
        },
        {
            "name": "expiry_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(expiry|expiration)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "mrz_line1",
            "type": AttributeType.TEXT,
            "method": ExtractionMethod.REGEX,
            "pattern": r"([A-Z0-9<]{44})",
            "confidence_base": 0.9
        },
        {
            "name": "mrz_line2",
            "type": AttributeType.TEXT,
            "method": ExtractionMethod.REGEX,
            "pattern": r"([A-Z0-9<]{44})",
            "confidence_base": 0.9
        }
    ],
    DocumentType.INVOICE: [
        {
            "name": "invoice_number",
            "type": AttributeType.ID,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(invoice|inv)[\s#:]*([A-Z0-9\-]{3,20})",
            "confidence_base": 0.8
        },
        {
            "name": "invoice_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(date|invoice date)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "due_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(due date|payment due)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "total_amount",
            "type": AttributeType.CURRENCY,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(total|amount due|balance due)[.:]*\s*[$€£¥]?[\s]*([0-9,]+\.[0-9]{2})",
            "confidence_base": 0.8
        },
        {
            "name": "tax_amount",
            "type": AttributeType.CURRENCY,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(tax|vat|gst)[.:]*\s*[$€£¥]?[\s]*([0-9,]+\.[0-9]{2})",
            "confidence_base": 0.7
        },
        {
            "name": "vendor_name",
            "type": AttributeType.NAME,
            "method": ExtractionMethod.KEYWORD,
            "keywords": ["from", "vendor", "seller", "billed from"],
            "confidence_base": 0.6
        },
        {
            "name": "customer_name",
            "type": AttributeType.NAME,
            "method": ExtractionMethod.KEYWORD,
            "keywords": ["to", "bill to", "customer", "buyer"],
            "confidence_base": 0.6
        }
    ],
    DocumentType.DRIVERS_LICENSE: [
        {
            "name": "license_number",
            "type": AttributeType.ID,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(license|lic|dl)[\s#:]*([A-Z0-9\-]{5,20})",
            "confidence_base": 0.8
        },
        {
            "name": "full_name",
            "type": AttributeType.NAME,
            "method": ExtractionMethod.REGEX,
            "pattern": r"name[.:]\s*([A-Za-z\s]+)",
            "confidence_base": 0.7
        },
        {
            "name": "date_of_birth",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(birth|dob|born)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "address",
            "type": AttributeType.ADDRESS,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(address|adr)[.:]\s*([A-Za-z0-9\s,\.\-]+)",
            "confidence_base": 0.6
        },
        {
            "name": "issue_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(issue|issued)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "expiry_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(expiry|expiration|exp)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "class",
            "type": AttributeType.TEXT,
            "method": ExtractionMethod.REGEX,
            "pattern": r"class[.:]\s*([A-Z0-9]{1,3})",
            "confidence_base": 0.8
        }
    ],
    DocumentType.UTILITY_BILL: [
        {
            "name": "account_number",
            "type": AttributeType.ID,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(account|acct)[\s#:]*([A-Z0-9\-]{5,20})",
            "confidence_base": 0.8
        },
        {
            "name": "bill_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(date|bill date)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "due_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(due date|payment due)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "total_amount",
            "type": AttributeType.CURRENCY,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(total|amount due|balance due)[.:]*\s*[$€£¥]?[\s]*([0-9,]+\.[0-9]{2})",
            "confidence_base": 0.8
        },
        {
            "name": "customer_name",
            "type": AttributeType.NAME,
            "method": ExtractionMethod.KEYWORD,
            "keywords": ["customer", "name", "bill to"],
            "confidence_base": 0.6
        },
        {
            "name": "service_address",
            "type": AttributeType.ADDRESS,
            "method": ExtractionMethod.KEYWORD,
            "keywords": ["service address", "property address"],
            "confidence_base": 0.6
        },
        {
            "name": "utility_type",
            "type": AttributeType.TEXT,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(electricity|water|gas|internet|phone)",
            "confidence_base": 0.7
        }
    ],
    DocumentType.BANK_STATEMENT: [
        {
            "name": "account_number",
            "type": AttributeType.ID,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(account|acct)[\s#:]*([A-Z0-9\-]{5,20})",
            "confidence_base": 0.8
        },
        {
            "name": "statement_date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(statement date|period ending)[.:]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.7
        },
        {
            "name": "opening_balance",
            "type": AttributeType.CURRENCY,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(opening balance|beginning balance)[.:]*\s*[$€£¥]?[\s]*([0-9,]+\.[0-9]{2})",
            "confidence_base": 0.7
        },
        {
            "name": "closing_balance",
            "type": AttributeType.CURRENCY,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(closing balance|ending balance)[.:]*\s*[$€£¥]?[\s]*([0-9,]+\.[0-9]{2})",
            "confidence_base": 0.7
        },
        {
            "name": "customer_name",
            "type": AttributeType.NAME,
            "method": ExtractionMethod.KEYWORD,
            "keywords": ["customer", "name", "prepared for"],
            "confidence_base": 0.6
        },
        {
            "name": "bank_name",
            "type": AttributeType.NAME,
            "method": ExtractionMethod.POSITION,
            "position": "top",
            "confidence_base": 0.5
        }
    ],
    DocumentType.UNKNOWN: [
        {
            "name": "date",
            "type": AttributeType.DATE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            "confidence_base": 0.5
        },
        {
            "name": "amount",
            "type": AttributeType.CURRENCY,
            "method": ExtractionMethod.REGEX,
            "pattern": r"[$€£¥]?[\s]*([0-9,]+\.[0-9]{2})",
            "confidence_base": 0.5
        },
        {
            "name": "email",
            "type": AttributeType.EMAIL,
            "method": ExtractionMethod.REGEX,
            "pattern": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            "confidence_base": 0.8
        },
        {
            "name": "phone",
            "type": AttributeType.PHONE,
            "method": ExtractionMethod.REGEX,
            "pattern": r"(\+?[0-9]{1,3}[\s\-\.]?)?(\([0-9]{1,4}\)[\s\-\.]?)?[0-9]{3,4}[\s\-\.]?[0-9]{3,4}",
            "confidence_base": 0.7
        }
    ]
}

def extract_with_regex(text: str, pattern: str, confidence_base: float) -> List[Dict[str, Any]]:
    """Extract attributes using regex pattern."""
    results = []
    
    matches = re.finditer(pattern, text, re.IGNORECASE)
    for match in matches:
        value = match.group(2) if len(match.groups()) > 1 else match.group(1)
        
        confidence = confidence_base
        
        if len(value) < 3:
            confidence *= 0.8
        
        results.append({
            "value": value.strip(),
            "confidence": min(0.99, confidence),
            "metadata": {
                "match_position": match.start(),
                "match_length": len(match.group(0)),
                "full_match": match.group(0)
            }
        })
    
    return results

def extract_with_keyword(text: str, keywords: List[str], confidence_base: float) -> List[Dict[str, Any]]:
    """Extract attributes using keyword context."""
    results = []
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        for keyword in keywords:
            if keyword.lower() in line_lower:
                value_line = ""
                if ":" in line:
                    value_line = line.split(":", 1)[1].strip()
                elif i + 1 < len(lines):
                    value_line = lines[i + 1].strip()
                
                if value_line:
                    confidence = confidence_base
                    
                    keyword_pos = line_lower.find(keyword.lower())
                    if keyword_pos == 0:
                        confidence *= 1.1  # Boost if keyword is at start of line
                    
                    results.append({
                        "value": value_line,
                        "confidence": min(0.99, confidence),
                        "metadata": {
                            "keyword": keyword,
                            "line_number": i,
                            "context_line": line
                        }
                    })
    
    return results

def extract_with_position(text: str, position: str, confidence_base: float) -> List[Dict[str, Any]]:
    """Extract attributes based on position in document."""
    results = []
    
    lines = text.split('\n')
    
    if position == "top" and len(lines) > 0:
        for i, line in enumerate(lines[:3]):  # Check first 3 lines
            if line.strip():
                results.append({
                    "value": line.strip(),
                    "confidence": confidence_base,
                    "metadata": {
                        "position": position,
                        "line_number": i
                    }
                })
                break
    
    elif position == "bottom" and len(lines) > 0:
        for i, line in enumerate(reversed(lines[-3:])):  # Check last 3 lines
            if line.strip():
                results.append({
                    "value": line.strip(),
                    "confidence": confidence_base,
                    "metadata": {
                        "position": position,
                        "line_number": len(lines) - i - 1
                    }
                })
                break
    
    return results

def extract_from_tables(ocr_result: Dict[str, Any], attribute_name: str, confidence_base: float) -> List[Dict[str, Any]]:
    """Extract attributes from tables in OCR result."""
    results = []
    
    tables = ocr_result.get("tables", [])
    
    for table_idx, table in enumerate(tables):
        for row_idx, row in enumerate(table.get("cells", [])):
            for col_idx, cell in enumerate(row):
                cell_text = cell.get("text", "").lower()
                
                if attribute_name.lower() in cell_text:
                    value_cell = None
                    
                    if col_idx + 1 < len(row):
                        value_cell = row[col_idx + 1]
                    elif row_idx + 1 < len(table.get("cells", [])):
                        next_row = table.get("cells", [])[row_idx + 1]
                        if col_idx < len(next_row):
                            value_cell = next_row[col_idx]
                    
                    if value_cell:
                        value = value_cell.get("text", "")
                        if value:
                            results.append({
                                "value": value,
                                "confidence": confidence_base * value_cell.get("confidence", 0.8),
                                "metadata": {
                                    "table_index": table_idx,
                                    "row": row_idx,
                                    "column": col_idx,
                                    "header_text": cell_text
                                }
                            })
    
    return results

def extract_from_forms(ocr_result: Dict[str, Any], attribute_name: str, confidence_base: float) -> List[Dict[str, Any]]:
    """Extract attributes from forms in OCR result."""
    results = []
    
    forms = ocr_result.get("forms", [])
    
    for form_idx, form in enumerate(forms):
        for field_idx, field in enumerate(form.get("fields", [])):
            field_key = field.get("key", {}).get("text", "").lower()
            
            if attribute_name.lower() in field_key:
                value = field.get("value", {}).get("text", "")
                if value:
                    results.append({
                        "value": value,
                        "confidence": confidence_base * field.get("confidence", 0.8),
                        "metadata": {
                            "form_index": form_idx,
                            "field_index": field_idx,
                            "field_key": field_key
                        }
                    })
    
    return results

def extract_attributes(document_type: DocumentType, ocr_result: Dict[str, Any], 
                       custom_rules: Optional[Dict[str, Any]] = None) -> List[Attribute]:
    """Extract attributes from document based on type and OCR result."""
    attributes = []
    
    text_content = ocr_result.get("text_content", "")
    
    type_rules = EXTRACTION_RULES.get(document_type, [])
    
    generic_rules = EXTRACTION_RULES.get(DocumentType.UNKNOWN, [])
    all_rules = type_rules + generic_rules
    
    if custom_rules and "rules" in custom_rules:
        all_rules.extend(custom_rules["rules"])
    
    for rule in all_rules:
        name = rule["name"]
        attr_type = rule["type"]
        method = rule["method"]
        confidence_base = rule.get("confidence_base", 0.5)
        
        extracted_values = []
        
        if method == ExtractionMethod.REGEX and "pattern" in rule:
            extracted_values = extract_with_regex(text_content, rule["pattern"], confidence_base)
        
        elif method == ExtractionMethod.KEYWORD and "keywords" in rule:
            extracted_values = extract_with_keyword(text_content, rule["keywords"], confidence_base)
        
        elif method == ExtractionMethod.POSITION and "position" in rule:
            extracted_values = extract_with_position(text_content, rule["position"], confidence_base)
        
        elif method == ExtractionMethod.TABLE:
            extracted_values = extract_from_tables(ocr_result, name, confidence_base)
        
        elif method == ExtractionMethod.FORM:
            extracted_values = extract_from_forms(ocr_result, name, confidence_base)
        
        for extracted in extracted_values:
            attribute = Attribute(
                name=name,
                value=extracted["value"],
                type=attr_type,
                confidence=extracted["confidence"],
                extraction_method=method,
                metadata=extracted.get("metadata", {})
            )
            
            attributes.append(attribute)
    
    attributes.sort(key=lambda x: x.confidence, reverse=True)
    
    unique_attributes = {}
    for attr in attributes:
        key = attr.name
        if key not in unique_attributes or attr.confidence > unique_attributes[key].confidence:
            unique_attributes[key] = attr
    
    return list(unique_attributes.values())

@app.post("/extract", response_model=ExtractionResponse)
async def extract_document_attributes(request: ExtractionRequest = Body(...)):
    """
    Extract attributes from a document based on its type and OCR result.
    
    This endpoint accepts a document type and OCR result,
    and returns a list of extracted attributes with confidence scores.
    """
    try:
        attributes = extract_attributes(
            request.document_type,
            request.ocr_result,
            request.custom_extraction_rules
        )
        
        return ExtractionResponse(
            document_id=request.document_id,
            document_type=request.document_type,
            attributes=attributes,
            processing_details={
                "attributes_count": len(attributes),
                "document_type": request.document_type,
                "processing_timestamp": datetime.now().isoformat()
            }
        )
            
    except Exception as e:
        logger.error(f"Error extracting attributes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
