"""
XML Service - Orchestrates XML/XSD generation and validation
"""

from pathlib import Path
from django.conf import settings
from app.xml_tools.xsd_generator import XSDGenerator
from app.xml_tools.xml_generator import XMLGenerator
from app.xml_tools.xml_validator import XMLValidator
from app.core.models import Dataset, ImportLog
import logging

logger = logging.getLogger(__name__)


class XMLService:
    """
    Service for managing XML generation, XSD creation, and validation.
    """
    
    def __init__(self, dataset: Dataset):
        """
        Initialize XML Service for a dataset.
        
        Args:
            dataset: Dataset model instance
        """
        self.dataset = dataset
        self.xml_output_dir = settings.XML_OUTPUT_DIR
        self.xsd_output_dir = settings.XML_SCHEMA_DIR
    
    def get_xsd_path(self) -> Path:
        """Get path for XSD file."""
        return self.xsd_output_dir / f"{self.dataset.name}.xsd"
    
    def get_xml_path(self) -> Path:
        """Get path for XML file."""
        return self.xml_output_dir / f"{self.dataset.name}.xml"
    
    def generate_xsd(self) -> str:
        """
        Generate XSD schema for the dataset.
        
        Returns:
            str: Path to generated XSD file
        """
        logger.info(f"Generating XSD for dataset '{self.dataset.name}'")
        
        try:
            # Create XSD generator
            xsd_gen = XSDGenerator.from_dataset(self.dataset)
            
            # Generate and save XSD
            xsd_path = xsd_gen.save_xsd(str(self.get_xsd_path()))
            
            # Update dataset with XSD path
            self.dataset.xml_schema_path = xsd_path
            self.dataset.save()
            
            # Log success
            ImportLog.objects.create(
                dataset=self.dataset,
                level='success',
                message=f"XSD schema generated successfully",
                details={'xsd_path': xsd_path}
            )
            
            logger.info(f"✓ XSD generated: {xsd_path}")
            return xsd_path
            
        except Exception as e:
            logger.error(f"✗ XSD generation failed: {e}")
            ImportLog.objects.create(
                dataset=self.dataset,
                level='error',
                message=f"XSD generation failed: {str(e)}"
            )
            raise
    
    def generate_xml(self, limit: int = None) -> str:
        """
        Generate XML file from dataset records.
        
        Args:
            limit: Optional limit on number of records to export
            
        Returns:
            str: Path to generated XML file
        """
        logger.info(f"Generating XML for dataset '{self.dataset.name}'")
        
        try:
            # Create XML generator
            xml_gen = XMLGenerator.from_dataset(self.dataset, limit=limit)
            
            # Generate and save XML
            xml_path = xml_gen.save_xml(str(self.get_xml_path()))
            
            # Update dataset with XML path
            self.dataset.xml_file_path = xml_path
            self.dataset.save()
            
            # Log success
            record_count = limit if limit else self.dataset.total_rows
            ImportLog.objects.create(
                dataset=self.dataset,
                level='success',
                message=f"XML generated successfully with {record_count} records",
                details={'xml_path': xml_path}
            )
            
            logger.info(f"✓ XML generated: {xml_path}")
            return xml_path
            
        except Exception as e:
            logger.error(f"✗ XML generation failed: {e}")
            ImportLog.objects.create(
                dataset=self.dataset,
                level='error',
                message=f"XML generation failed: {str(e)}"
            )
            raise
    
    def validate_xml(self) -> tuple:
        """
        Validate XML against XSD schema.
        
        Returns:
            tuple: (is_valid, errors)
        """
        logger.info(f"Validating XML for dataset '{self.dataset.name}'")
        
        xsd_path = self.get_xsd_path()
        xml_path = self.get_xml_path()
        
        # Check if files exist
        if not xsd_path.exists():
            error_msg = "XSD schema not found. Generate XSD first."
            logger.error(error_msg)
            return False, [error_msg]
        
        if not xml_path.exists():
            error_msg = "XML file not found. Generate XML first."
            logger.error(error_msg)
            return False, [error_msg]
        
        try:
            # Create validator
            validator = XMLValidator(str(xsd_path))
            
            # Validate
            is_valid, errors = validator.validate(str(xml_path))
            
            # Log result
            if is_valid:
                ImportLog.objects.create(
                    dataset=self.dataset,
                    level='success',
                    message="XML validation successful"
                )
                logger.info("✓ XML is valid")
            else:
                ImportLog.objects.create(
                    dataset=self.dataset,
                    level='error',
                    message=f"XML validation failed",
                    details={'errors': errors}
                )
                logger.error(f"✗ XML validation failed: {errors}")
            
            return is_valid, errors
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg)
            ImportLog.objects.create(
                dataset=self.dataset,
                level='error',
                message=error_msg
            )
            return False, [error_msg]
    
    def generate_and_validate(self, limit: int = None) -> dict:
        """
        Complete workflow: Generate XSD, generate XML, and validate.
        
        Args:
            limit: Optional limit on number of records to export
            
        Returns:
            dict: Summary of the process
        """
        logger.info(f"Starting complete XML workflow for '{self.dataset.name}'")
        
        result = {
            'dataset': self.dataset.name,
            'xsd_generated': False,
            'xml_generated': False,
            'validation_passed': False,
            'errors': []
        }
        
        try:
            # Step 1: Generate XSD
            xsd_path = self.generate_xsd()
            result['xsd_path'] = xsd_path
            result['xsd_generated'] = True
            
            # Step 2: Generate XML
            xml_path = self.generate_xml(limit=limit)
            result['xml_path'] = xml_path
            result['xml_generated'] = True
            
            # Step 3: Validate
            is_valid, errors = self.validate_xml()
            result['validation_passed'] = is_valid
            result['validation_errors'] = errors
            
            logger.info("✓ Complete XML workflow finished successfully")
            
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(f"✗ {error_msg}")
        
        return result
