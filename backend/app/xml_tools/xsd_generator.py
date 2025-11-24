"""
XSD Schema Generator - Generates XML Schema Definition files dynamically
based on dataset structure.
"""

from lxml import etree
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class XSDGenerator:
    """
    Generates XSD (XML Schema Definition) files based on dataset column metadata.
    """
    
    # Mapping of internal data types to XSD types
    TYPE_MAPPING = {
        'string': 'xs:string',
        'integer': 'xs:integer',
        'float': 'xs:decimal',
        'decimal': 'xs:decimal',
        'boolean': 'xs:boolean',
        'date': 'xs:date',
        'datetime': 'xs:dateTime',
    }
    
    def __init__(self, dataset_name: str, columns: List[Dict]):
        """
        Initialize XSD Generator.
        
        Args:
            dataset_name: Name of the dataset
            columns: List of column metadata dicts with 'name', 'data_type', 'nullable', etc.
        """
        self.dataset_name = dataset_name
        self.columns = columns
        
    def generate_xsd(self) -> etree.Element:
        """
        Generate XSD schema as lxml Element.
        
        Returns:
            lxml.etree.Element: The complete XSD schema
        """
        # Create XSD root element
        xs_namespace = "http://www.w3.org/2001/XMLSchema"
        XS = "{%s}" % xs_namespace
        
        nsmap = {'xs': xs_namespace}
        schema = etree.Element(
            XS + "schema",
            nsmap=nsmap,
            attrib={
                'elementFormDefault': 'qualified',
                'attributeFormDefault': 'unqualified'
            }
        )
        
        # Create root element definition
        root_element = etree.SubElement(schema, XS + "element", name=self.dataset_name)
        root_complex_type = etree.SubElement(root_element, XS + "complexType")
        root_sequence = etree.SubElement(root_complex_type, XS + "sequence")
        
        # Add 'record' element that can repeat
        record_element = etree.SubElement(
            root_sequence,
            XS + "element",
            name="record",
            minOccurs="0",
            maxOccurs="unbounded"
        )
        
        # Define record structure
        record_complex_type = etree.SubElement(record_element, XS + "complexType")
        record_sequence = etree.SubElement(record_complex_type, XS + "sequence")
        
        # Add each column as an element
        for column in self.columns:
            self._add_column_element(record_sequence, column, XS)
        
        return schema
    
    @staticmethod
    def normalize_xml_name(name: str) -> str:
        """
        Normalize column name to be valid XML element name.
        
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
    
    def _add_column_element(self, parent: etree.Element, column: Dict, xs_prefix: str):
        """
        Add a column element to the XSD schema.
        
        Args:
            parent: Parent XML element
            column: Column metadata dict
            xs_prefix: XSD namespace prefix
        """
        column_name = self.normalize_xml_name(column['name'])
        data_type = column.get('data_type', 'string')
        nullable = column.get('nullable', True)
        
        # Get XSD type
        xsd_type = self.TYPE_MAPPING.get(data_type, 'xs:string')
        
        # Create element
        attribs = {
            'name': column_name,
            'type': xsd_type
        }
        
        # Set minOccurs based on nullable
        if nullable:
            attribs['minOccurs'] = '0'
        
        etree.SubElement(parent, xs_prefix + "element", **attribs)
    
    def save_xsd(self, output_path: str) -> str:
        """
        Generate and save XSD to file.
        
        Args:
            output_path: Path where XSD file will be saved
            
        Returns:
            str: Path to saved XSD file
        """
        schema = self.generate_xsd()
        
        # Create directory if it doesn't exist
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write XSD to file with pretty formatting
        tree = etree.ElementTree(schema)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8'
        )
        
        logger.info(f"XSD schema saved to {output_path}")
        return str(output_path)
    
    @staticmethod
    def from_dataset(dataset) -> 'XSDGenerator':
        """
        Create XSD generator from a Dataset model instance.
        
        Args:
            dataset: Dataset model instance
            
        Returns:
            XSDGenerator instance
        """
        columns = []
        for col in dataset.columns.all().order_by('position'):
            columns.append({
                'name': col.name,
                'data_type': col.data_type,
                'nullable': col.nullable,
                'unique': col.unique
            })
        
        return XSDGenerator(dataset.name, columns)
