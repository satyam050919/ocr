import requests
import json
import os
import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

def process_document(api_url, document_path, document_type=None, auto_detect=True):
    """
    Process a document using the Textract Document Processor API.
    
    Args:
        api_url (str): The base URL of the API
        document_path (str): Path to the document file
        document_type (str, optional): Document type (passport, invoice, drivers_license, utility_bill, generic)
        auto_detect (bool): Whether to auto-detect document type
    
    Returns:
        dict: The processed document data
    """
    endpoint = f"{api_url}/documents/process"
    
    files = {
        'file': (os.path.basename(document_path), open(document_path, 'rb'), 
                 'application/pdf' if document_path.endswith('.pdf') else 'image/jpeg')
    }
    
    data = {'auto_detect_type': str(auto_detect).lower()}
    if document_type:
        data['document_type'] = document_type
    
    response = requests.post(endpoint, files=files, data=data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()


def main():
    parser = argparse.ArgumentParser(description='Test the Textract Document Processor API')
    parser.add_argument('--api-url', default='http://localhost:8000', help='API base URL')
    parser.add_argument('--document', required=True, help='Path to document file')
    parser.add_argument('--type', choices=['passport', 'invoice', 'drivers_license', 'utility_bill', 'generic'], 
                        help='Document type')
    parser.add_argument('--no-auto-detect', action='store_true', help='Disable auto-detection')
    
    args = parser.parse_args()
    
    result = process_document(
        args.api_url, 
        args.document, 
        args.type, 
        not args.no_auto_detect
    )
    
    if result:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
