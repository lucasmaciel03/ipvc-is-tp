"""
XML-RPC Server Implementation for IPVC Integration System
"""

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import logging
import json

# Django setup
import os
import sys
import django

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from app.core.models import Dataset, DatasetColumn, DataRecord
from app.xml_tools.xml_service import XMLService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestHandler(SimpleXMLRPCRequestHandler):
    """Custom request handler"""
    rpc_paths = ('/RPC2',)


class DatasetRPCService:
    """
    XML-RPC Service for Dataset operations
    """
    
    def list_datasets(self, page=1, page_size=50):
        """
        List all datasets with pagination
        
        Args:
            page: Page number (default: 1)
            page_size: Number of datasets per page (default: 50)
            
        Returns:
            dict: {
                'datasets': [...],
                'total_count': int,
                'page': int,
                'page_size': int
            }
        """
        try:
            offset = (page - 1) * page_size
            total_count = Dataset.objects.count()
            datasets = Dataset.objects.all().order_by('-created_at')[offset:offset+page_size]
            
            dataset_list = []
            for dataset in datasets:
                dataset_list.append({
                    'id': dataset.id,
                    'name': dataset.name,
                    'description': dataset.description or '',
                    'total_rows': dataset.total_rows,
                    'total_columns': dataset.total_columns,
                    'status': dataset.status,
                    'created_at': dataset.created_at.isoformat(),
                    'updated_at': dataset.updated_at.isoformat()
                })
            
            return {
                'datasets': dataset_list,
                'total_count': total_count,
                'page': page,
                'page_size': page_size
            }
            
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            return {'error': str(e)}
    
    def get_dataset(self, dataset_id):
        """
        Get detailed dataset information
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            dict: Dataset details with columns
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            columns = dataset.columns.all().order_by('position')
            
            column_list = []
            for col in columns:
                column_list.append({
                    'id': col.id,
                    'name': col.name,
                    'data_type': col.data_type,
                    'nullable': col.nullable,
                    'unique': col.unique,
                    'primary_key': col.primary_key,
                    'null_count': col.null_count,
                    'unique_count': col.unique_count,
                    'position': col.position,
                    'sample_values': col.sample_values or []
                })
            
            return {
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description or '',
                'source_file': dataset.source_file or '',
                'total_rows': dataset.total_rows,
                'total_columns': dataset.total_columns,
                'status': dataset.status,
                'created_at': dataset.created_at.isoformat(),
                'updated_at': dataset.updated_at.isoformat(),
                'imported_at': dataset.imported_at.isoformat() if dataset.imported_at else '',
                'xml_file_path': dataset.xml_file_path or '',
                'xml_schema_path': dataset.xml_schema_path or '',
                'columns': column_list
            }
            
        except Dataset.DoesNotExist:
            return {'error': f'Dataset with id {dataset_id} not found'}
        except Exception as e:
            logger.error(f"Error getting dataset: {e}")
            return {'error': str(e)}
    
    def get_dataset_records(self, dataset_id, limit=100, offset=0):
        """
        Get dataset records with pagination
        
        Args:
            dataset_id: Dataset ID
            limit: Maximum records to return (default: 100)
            offset: Number of records to skip (default: 0)
            
        Returns:
            dict: {
                'dataset': str,
                'total_rows': int,
                'offset': int,
                'limit': int,
                'count': int,
                'records': [...]
            }
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            records = dataset.records.all().order_by('row_number')[offset:offset+limit]
            
            record_list = []
            for record in records:
                record_list.append({
                    'id': record.id,
                    'row_number': record.row_number,
                    'data': record.data,
                    'created_at': record.created_at.isoformat()
                })
            
            return {
                'dataset': dataset.name,
                'total_rows': dataset.total_rows,
                'offset': offset,
                'limit': limit,
                'count': len(record_list),
                'records': record_list
            }
            
        except Dataset.DoesNotExist:
            return {'error': f'Dataset with id {dataset_id} not found'}
        except Exception as e:
            logger.error(f"Error getting records: {e}")
            return {'error': str(e)}
    
    def generate_xml(self, dataset_id, limit=0, generate_xsd=True, validate=True):
        """
        Generate XML and optionally XSD for dataset
        
        Args:
            dataset_id: Dataset ID
            limit: Limit number of records (0 = all)
            generate_xsd: Generate XSD schema (default: True)
            validate: Validate XML against XSD (default: True)
            
        Returns:
            dict: Generation result with paths and validation status
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            xml_service = XMLService(dataset)
            
            result = {
                'dataset_name': dataset.name,
                'xsd_generated': False,
                'xml_generated': False,
                'validation_passed': None
            }
            
            # Generate XSD
            if generate_xsd:
                xsd_path = xml_service.generate_xsd()
                result['xsd_generated'] = True
                result['xsd_path'] = xsd_path
            
            # Generate XML
            xml_limit = limit if limit > 0 else None
            xml_path = xml_service.generate_xml(limit=xml_limit)
            result['xml_generated'] = True
            result['xml_path'] = xml_path
            
            # Validate
            if validate:
                is_valid, errors = xml_service.validate_xml()
                result['validation_passed'] = is_valid
                result['validation_errors'] = errors
            
            return result
            
        except Dataset.DoesNotExist:
            return {'error': f'Dataset with id {dataset_id} not found'}
        except Exception as e:
            logger.error(f"Error generating XML: {e}")
            return {'error': str(e)}
    
    def validate_xml(self, dataset_id):
        """
        Validate existing XML against XSD
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            dict: Validation result
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            xml_service = XMLService(dataset)
            
            is_valid, errors = xml_service.validate_xml()
            
            return {
                'dataset_name': dataset.name,
                'is_valid': is_valid,
                'errors': errors
            }
            
        except Dataset.DoesNotExist:
            return {'error': f'Dataset with id {dataset_id} not found'}
        except Exception as e:
            logger.error(f"Error validating XML: {e}")
            return {'error': str(e)}
    
    def get_dataset_columns(self, dataset_id):
        """
        Get all columns for a dataset
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            list: List of column dictionaries
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            columns = dataset.columns.all().order_by('position')
            
            column_list = []
            for col in columns:
                column_list.append({
                    'id': col.id,
                    'name': col.name,
                    'data_type': col.data_type,
                    'nullable': col.nullable,
                    'unique': col.unique,
                    'primary_key': col.primary_key,
                    'null_count': col.null_count,
                    'unique_count': col.unique_count,
                    'position': col.position
                })
            
            return column_list
            
        except Dataset.DoesNotExist:
            return {'error': f'Dataset with id {dataset_id} not found'}
        except Exception as e:
            logger.error(f"Error getting columns: {e}")
            return {'error': str(e)}
    
    def get_dataset_stats(self, dataset_id):
        """
        Get statistics for a dataset
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            dict: Dataset statistics
        """
        try:
            dataset = Dataset.objects.get(id=dataset_id)
            
            return {
                'dataset_name': dataset.name,
                'total_rows': dataset.total_rows,
                'total_columns': dataset.total_columns,
                'status': dataset.status,
                'has_xml': bool(dataset.xml_file_path),
                'has_xsd': bool(dataset.xml_schema_path),
                'created_at': dataset.created_at.isoformat(),
                'updated_at': dataset.updated_at.isoformat()
            }
            
        except Dataset.DoesNotExist:
            return {'error': f'Dataset with id {dataset_id} not found'}
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}


def serve(host='127.0.0.1', port=8001):
    """Start XML-RPC server"""
    
    # Create server
    server = SimpleXMLRPCServer(
        (host, port),
        requestHandler=RequestHandler,
        allow_none=True
    )
    
    server.register_introspection_functions()
    
    # Register service
    service = DatasetRPCService()
    server.register_instance(service)
    
    logger.info(f"🚀 XML-RPC Server started on {host}:{port}")
    logger.info(f"   Methods:")
    logger.info(f"   - list_datasets(page, page_size)")
    logger.info(f"   - get_dataset(dataset_id)")
    logger.info(f"   - get_dataset_records(dataset_id, limit, offset)")
    logger.info(f"   - get_dataset_columns(dataset_id)")
    logger.info(f"   - get_dataset_stats(dataset_id)")
    logger.info(f"   - generate_xml(dataset_id, limit, generate_xsd, validate)")
    logger.info(f"   - validate_xml(dataset_id)")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down XML-RPC server...")


if __name__ == '__main__':
    serve()
