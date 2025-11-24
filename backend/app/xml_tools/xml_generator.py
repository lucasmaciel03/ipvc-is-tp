"""
XML Generator - Converts dataset records to XML format
"""

from lxml import etree
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class XMLGenerator:
    """
    Generates XML files from dataset records.
    """
    
    def __init__(self, dataset_name: str, columns: List[str], records: List[Dict[str, Any]]):
        """
        Initialize XML Generator.
        
        Args:
            dataset_name: Name of the dataset (root element name)
            columns: List of column names
            records: List of record dictionaries
        """
        self.dataset_name = dataset_name
        self.columns = columns
        self.records = records
    
    @staticmethod
    def normalize_xml_name(name: str) -> str:
        """
        Normalize column name to be valid XML element name.
        - Replace spaces with underscores
        - Remove special characters
        - Ensure it starts with letter or underscore
        
        Args:
            name: Original column name
            
        Returns:
            str: Valid XML element name
        """
        import re
        
        # Replace spaces and special chars with underscore
        normalized = re.sub(r'[^\w]', '_', name)
        
        # Ensure it starts with letter or underscore
        if normalized and not normalized[0].isalpha() and normalized[0] != '_':
            normalized = '_' + normalized
        
        return normalized
    
    def generate_xml(self) -> etree.Element:
        """
        Generate XML document as lxml Element.
        
        Returns:
            lxml.etree.Element: The complete XML document
        """
        # Create root element
        root = etree.Element(self.dataset_name)
        
        # Add each record
        for record in self.records:
            record_element = etree.SubElement(root, "record")
            
            # Add each column value
            for column in self.columns:
                value = record.get(column)
                
                # Normalize column name for XML
                xml_column_name = self.normalize_xml_name(column)
                
                # Create column element
                col_element = etree.SubElement(record_element, xml_column_name)
                
                # Set text value (handle None/null values)
                if value is not None:
                    col_element.text = str(value)
                else:
                    # For null values, use xsi:nil attribute
                    col_element.set(
                        "{http://www.w3.org/2001/XMLSchema-instance}nil",
                        "true"
                    )
        
        return root
    
    def save_xml(self, output_path: str) -> str:
        """
        Generate and save XML to file.
        
        Args:
            output_path: Path where XML file will be saved
            
        Returns:
            str: Path to saved XML file
        """
        root = self.generate_xml()
        
        # Create directory if it doesn't exist
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write XML to file with pretty formatting
        tree = etree.ElementTree(root)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8'
        )
        
        logger.info(f"XML saved to {output_path}")
        return str(output_path)
    
    @staticmethod
    def from_dataset(dataset, limit: int = None) -> 'XMLGenerator':
        """
        Create XML generator from a Dataset model instance.
        
        Args:
            dataset: Dataset model instance
            limit: Optional limit on number of records to export
            
        Returns:
            XMLGenerator instance
        """
        # Get columns in order
        columns = [col.name for col in dataset.columns.all().order_by('position')]
        
        # Get records
        records_qs = dataset.records.all().order_by('row_number')
        if limit:
            records_qs = records_qs[:limit]
        
        # Extract data from records
        records = [record.data for record in records_qs]
        
        return XMLGenerator(dataset.name, columns, records)
