import boto3
import logging
from typing import Dict, List, Optional, Any, BinaryIO
from botocore.exceptions import ClientError

from app.models.document import TextractBlock

logger = logging.getLogger(__name__)


class TextractService:
    def __init__(self, aws_region: str = "us-east-1"):
        self.client = boto3.client('textract', region_name=aws_region)
    
    def analyze_document(self, document: BinaryIO) -> Dict[str, Any]:
        """
        Analyze a document using AWS Textract and return the raw response.
        """
        try:
            response = self.client.analyze_document(
                Document={'Bytes': document.read()},
                FeatureTypes=['FORMS', 'TABLES']
            )
            return response
        except ClientError as e:
            logger.error(f"Error analyzing document with Textract: {e}")
            raise
    
    def extract_blocks(self, textract_response: Dict[str, Any]) -> List[TextractBlock]:
        """
        Extract and convert Textract blocks from the raw response.
        """
        blocks = []
        for block in textract_response.get('Blocks', []):
            blocks.append(
                TextractBlock(
                    id=block.get('Id'),
                    block_type=block.get('BlockType'),
                    text=block.get('Text'),
                    confidence=block.get('Confidence'),
                    geometry=block.get('Geometry'),
                    relationships=block.get('Relationships')
                )
            )
        return blocks
    
    def get_form_key_value_pairs(self, blocks: List[TextractBlock]) -> Dict[str, Dict[str, Any]]:
        """
        Extract key-value pairs from form fields in the document.
        """
        key_map = {}
        value_map = {}
        block_map = {}
        
        for block in blocks:
            block_map[block.id] = block
            
            if block.block_type == "KEY_VALUE_SET":
                if 'KEY' in block.entity_types:
                    key_map[block.id] = block
                elif 'VALUE' in block.entity_types:
                    value_map[block.id] = block
        
        result = {}
        for key_id, key_block in key_map.items():
            value_id = None
            for relationship in key_block.relationships or []:
                if relationship.get('Type') == 'VALUE':
                    for value_id in relationship.get('Ids', []):
                        value_block = value_map.get(value_id)
                        if value_block:
                            key_text = self._get_text(key_block, block_map)
                            value_text = self._get_text(value_block, block_map)
                            result[key_text] = {
                                'value': value_text,
                                'confidence': min(key_block.confidence or 0, value_block.confidence or 0)
                            }
        
        return result
    
    def _get_text(self, block: TextractBlock, block_map: Dict[str, TextractBlock]) -> str:
        """
        Get the text value of a block, including handling child blocks.
        """
        if block.text:
            return block.text
        
        text = ""
        if block.relationships:
            for relationship in block.relationships:
                if relationship.get('Type') == 'CHILD':
                    for child_id in relationship.get('Ids', []):
                        child = block_map.get(child_id)
                        if child and child.text:
                            text += child.text + " "
        
        return text.strip()
