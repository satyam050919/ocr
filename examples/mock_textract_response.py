"""
This script provides a mock AWS Textract response for testing without actual AWS credentials.
It can be used to simulate Textract responses for different document types.
"""

import json
import boto3
from unittest.mock import patch
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.models.document import DocumentType
from app.services.textract_service import TextractService
from app.services.document_processor import DocumentProcessor


def create_mock_passport_response():
    """Create a mock Textract response for a passport."""
    return {
        "Blocks": [
            {
                "Id": "1",
                "BlockType": "LINE",
                "Text": "PASSPORT",
                "Confidence": 99.5,
                "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.05, "Left": 0.1, "Top": 0.1}}
            },
            {
                "Id": "2",
                "BlockType": "LINE",
                "Text": "Surname: SMITH",
                "Confidence": 98.2,
                "Geometry": {"BoundingBox": {"Width": 0.2, "Height": 0.05, "Left": 0.1, "Top": 0.2}}
            },
            {
                "Id": "3",
                "BlockType": "LINE",
                "Text": "Given Names: JOHN MICHAEL",
                "Confidence": 97.8,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.3}}
            },
            {
                "Id": "4",
                "BlockType": "LINE",
                "Text": "Nationality: UNITED STATES OF AMERICA",
                "Confidence": 96.5,
                "Geometry": {"BoundingBox": {"Width": 0.4, "Height": 0.05, "Left": 0.1, "Top": 0.4}}
            },
            {
                "Id": "5",
                "BlockType": "LINE",
                "Text": "Date of Birth: 15/04/1985",
                "Confidence": 95.9,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.5}}
            },
            {
                "Id": "6",
                "BlockType": "LINE",
                "Text": "Place of Birth: NEW YORK",
                "Confidence": 94.7,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.6}}
            },
            {
                "Id": "7",
                "BlockType": "LINE",
                "Text": "Passport No: AB123456",
                "Confidence": 99.1,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.7}}
            },
            {
                "Id": "8",
                "BlockType": "LINE",
                "Text": "Date of Issue: 01/01/2020",
                "Confidence": 98.3,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.8}}
            },
            {
                "Id": "9",
                "BlockType": "LINE",
                "Text": "Date of Expiry: 01/01/2030",
                "Confidence": 97.6,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.9}}
            }
        ]
    }


def create_mock_invoice_response():
    """Create a mock Textract response for an invoice."""
    return {
        "Blocks": [
            {
                "Id": "1",
                "BlockType": "LINE",
                "Text": "INVOICE",
                "Confidence": 99.8,
                "Geometry": {"BoundingBox": {"Width": 0.1, "Height": 0.05, "Left": 0.1, "Top": 0.1}}
            },
            {
                "Id": "2",
                "BlockType": "LINE",
                "Text": "Invoice No: INV-2023-001",
                "Confidence": 98.5,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.2}}
            },
            {
                "Id": "3",
                "BlockType": "LINE",
                "Text": "Invoice Date: 15/03/2023",
                "Confidence": 97.9,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.3}}
            },
            {
                "Id": "4",
                "BlockType": "LINE",
                "Text": "Due Date: 15/04/2023",
                "Confidence": 97.2,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.4}}
            },
            {
                "Id": "5",
                "BlockType": "LINE",
                "Text": "From: ABC Company Inc.",
                "Confidence": 96.8,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.5}}
            },
            {
                "Id": "6",
                "BlockType": "LINE",
                "Text": "To: XYZ Corporation",
                "Confidence": 96.1,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.6}}
            },
            {
                "Id": "7",
                "BlockType": "LINE",
                "Text": "Subtotal: $1,000.00",
                "Confidence": 95.7,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.7}}
            },
            {
                "Id": "8",
                "BlockType": "LINE",
                "Text": "Tax: $100.00",
                "Confidence": 95.2,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.8}}
            },
            {
                "Id": "9",
                "BlockType": "LINE",
                "Text": "Total Amount: $1,100.00",
                "Confidence": 99.1,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.9}}
            }
        ]
    }


def create_mock_drivers_license_response():
    """Create a mock Textract response for a driver's license."""
    return {
        "Blocks": [
            {
                "Id": "1",
                "BlockType": "LINE",
                "Text": "DRIVER LICENSE",
                "Confidence": 99.7,
                "Geometry": {"BoundingBox": {"Width": 0.2, "Height": 0.05, "Left": 0.1, "Top": 0.1}}
            },
            {
                "Id": "2",
                "BlockType": "LINE",
                "Text": "DL No: D12345678",
                "Confidence": 98.9,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.2}}
            },
            {
                "Id": "3",
                "BlockType": "LINE",
                "Text": "Name: JANE DOE",
                "Confidence": 98.3,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.3}}
            },
            {
                "Id": "4",
                "BlockType": "LINE",
                "Text": "Address: 123 MAIN ST, ANYTOWN, CA 12345",
                "Confidence": 97.5,
                "Geometry": {"BoundingBox": {"Width": 0.5, "Height": 0.05, "Left": 0.1, "Top": 0.4}}
            },
            {
                "Id": "5",
                "BlockType": "LINE",
                "Text": "DOB: 01/15/1990",
                "Confidence": 96.8,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.5}}
            },
            {
                "Id": "6",
                "BlockType": "LINE",
                "Text": "Issue Date: 05/10/2020",
                "Confidence": 96.2,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.6}}
            },
            {
                "Id": "7",
                "BlockType": "LINE",
                "Text": "Expiration Date: 05/10/2028",
                "Confidence": 95.9,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.7}}
            },
            {
                "Id": "8",
                "BlockType": "LINE",
                "Text": "Class: C",
                "Confidence": 99.5,
                "Geometry": {"BoundingBox": {"Width": 0.2, "Height": 0.05, "Left": 0.1, "Top": 0.8}}
            },
            {
                "Id": "9",
                "BlockType": "LINE",
                "Text": "Restrictions: NONE",
                "Confidence": 98.7,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.9}}
            }
        ]
    }


def create_mock_utility_bill_response():
    """Create a mock Textract response for a utility bill."""
    return {
        "Blocks": [
            {
                "Id": "1",
                "BlockType": "LINE",
                "Text": "UTILITY BILL",
                "Confidence": 99.6,
                "Geometry": {"BoundingBox": {"Width": 0.2, "Height": 0.05, "Left": 0.1, "Top": 0.1}}
            },
            {
                "Id": "2",
                "BlockType": "LINE",
                "Text": "Account Number: 987654321",
                "Confidence": 98.7,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.2}}
            },
            {
                "Id": "3",
                "BlockType": "LINE",
                "Text": "Bill Date: 01/04/2023",
                "Confidence": 98.1,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.3}}
            },
            {
                "Id": "4",
                "BlockType": "LINE",
                "Text": "Due Date: 15/04/2023",
                "Confidence": 97.8,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.4}}
            },
            {
                "Id": "5",
                "BlockType": "LINE",
                "Text": "Customer: ROBERT JOHNSON",
                "Confidence": 97.2,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.5}}
            },
            {
                "Id": "6",
                "BlockType": "LINE",
                "Text": "Service Address: 456 ELM ST, SOMEWHERE, NY 54321",
                "Confidence": 96.5,
                "Geometry": {"BoundingBox": {"Width": 0.5, "Height": 0.05, "Left": 0.1, "Top": 0.6}}
            },
            {
                "Id": "7",
                "BlockType": "LINE",
                "Text": "Billing Period: 01/03/2023 - 31/03/2023",
                "Confidence": 96.1,
                "Geometry": {"BoundingBox": {"Width": 0.4, "Height": 0.05, "Left": 0.1, "Top": 0.7}}
            },
            {
                "Id": "8",
                "BlockType": "LINE",
                "Text": "Provider: City Power & Water",
                "Confidence": 95.8,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.8}}
            },
            {
                "Id": "9",
                "BlockType": "LINE",
                "Text": "Total Amount Due: $125.75",
                "Confidence": 99.3,
                "Geometry": {"BoundingBox": {"Width": 0.3, "Height": 0.05, "Left": 0.1, "Top": 0.9}}
            }
        ]
    }


def test_document_processor_with_mock(document_type):
    """
    Test the document processor with a mock Textract response.
    
    Args:
        document_type (str): The type of document to test
    """
    mock_responses = {
        "passport": create_mock_passport_response,
        "invoice": create_mock_invoice_response,
        "drivers_license": create_mock_drivers_license_response,
        "utility_bill": create_mock_utility_bill_response
    }
    
    mock_response = mock_responses.get(document_type, create_mock_passport_response)()
    
    with patch.object(boto3, 'client', autospec=True):
        textract_service = TextractService()
        
        with patch.object(textract_service, 'analyze_document', return_value=mock_response):
            processor = DocumentProcessor(textract_service)
            
            from io import BytesIO
            dummy_document = BytesIO(b"dummy content")
            
            doc_type = getattr(DocumentType, document_type.upper()) if document_type else None
            result = processor.process_document(
                dummy_document,
                document_type=doc_type,
                auto_detect_type=True
            )
            
            print(f"\nProcessed {document_type.upper()} document:")
            print(f"Document Type: {result.document_type}")
            print(f"Confidence Score: {result.confidence_score}")
            print("\nExtracted Fields:")
            for field in result.fields:
                print(f"  {field.name}: {field.value} (confidence: {field.confidence})")
            
            return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test document processing with mock Textract responses')
    parser.add_argument('--type', choices=['passport', 'invoice', 'drivers_license', 'utility_bill'], 
                        default='passport', help='Document type to test')
    
    args = parser.parse_args()
    
    test_document_processor_with_mock(args.type)


if __name__ == "__main__":
    main()
