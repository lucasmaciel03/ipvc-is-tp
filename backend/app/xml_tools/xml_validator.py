"""
XML Validator - Validates XML files against XSD schemas
"""

from lxml import etree
import xmlschema
from pathlib import Path
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class XMLValidator:
    """
    Validates XML documents against XSD schemas.
    """
    
    def __init__(self, xsd_path: str):
        """
        Initialize validator with XSD schema.
        
        Args:
            xsd_path: Path to XSD schema file
        """
        self.xsd_path = Path(xsd_path)
        self.schema = None
        self._load_schema()
    
    def _load_schema(self):
        """Load XSD schema from file."""
        if not self.xsd_path.exists():
            raise FileNotFoundError(f"XSD schema not found: {self.xsd_path}")
        
        try:
            # Load schema using xmlschema (more robust)
            self.schema = xmlschema.XMLSchema(str(self.xsd_path))
            logger.info(f"XSD schema loaded: {self.xsd_path}")
        except Exception as e:
            logger.error(f"Failed to load XSD schema: {e}")
            raise
    
    def validate(self, xml_path: str) -> Tuple[bool, List[str]]:
        """
        Validate XML file against the loaded schema.
        
        Args:
            xml_path: Path to XML file to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        xml_path = Path(xml_path)
        
        if not xml_path.exists():
            return False, [f"XML file not found: {xml_path}"]
        
        errors = []
        
        try:
            # Validate using xmlschema
            self.schema.validate(str(xml_path))
            logger.info(f"✓ XML validation successful: {xml_path}")
            return True, []
            
        except xmlschema.XMLSchemaException as e:
            errors.append(f"Schema validation error: {str(e)}")
            logger.error(f"✗ XML validation failed: {e}")
            return False, errors
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            logger.error(f"✗ Unexpected validation error: {e}")
            return False, errors
    
    def validate_string(self, xml_string: str) -> Tuple[bool, List[str]]:
        """
        Validate XML from string.
        
        Args:
            xml_string: XML content as string
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Parse XML string
            root = etree.fromstring(xml_string.encode('utf-8'))
            
            # Validate against schema
            self.schema.validate(root)
            return True, []
            
        except xmlschema.XMLSchemaException as e:
            errors.append(f"Schema validation error: {str(e)}")
            return False, errors
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors
    
    def get_validation_report(self, xml_path: str) -> Dict:
        """
        Get detailed validation report.
        
        Args:
            xml_path: Path to XML file
            
        Returns:
            Dict with validation details
        """
        is_valid, errors = self.validate(xml_path)
        
        report = {
            'xml_file': str(xml_path),
            'xsd_file': str(self.xsd_path),
            'is_valid': is_valid,
            'errors': errors,
            'error_count': len(errors)
        }
        
        if is_valid:
            report['message'] = "✓ XML is valid according to the XSD schema"
        else:
            report['message'] = f"✗ XML validation failed with {len(errors)} error(s)"
        
        return report
