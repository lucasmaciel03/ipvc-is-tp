"""
gRPC Server Implementation for IPVC Integration System
"""

import grpc
from concurrent import futures
import json
import logging
from datetime import datetime

# Django setup
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from app.core.models import Dataset, DatasetColumn, DataRecord
from app.xml_tools.xml_service import XMLService

# Import generated gRPC code
from protos import dataset_service_pb2
from protos import dataset_service_pb2_grpc

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetServicer(dataset_service_pb2_grpc.DatasetServiceServicer):
    """
    Implementation of DatasetService gRPC interface
    """
    
    def ListDatasets(self, request, context):
        """List all datasets with pagination"""
        try:
            page = request.page or 1
            page_size = request.page_size or 50
            
            # Calculate offset
            offset = (page - 1) * page_size
            
            # Query datasets
            total_count = Dataset.objects.count()
            datasets = Dataset.objects.all().order_by('-created_at')[offset:offset+page_size]
            
            # Convert to protobuf messages
            dataset_summaries = []
            for dataset in datasets:
                summary = dataset_service_pb2.DatasetSummary(
                    id=dataset.id,
                    name=dataset.name,
                    description=dataset.description or "",
                    total_rows=dataset.total_rows,
                    total_columns=dataset.total_columns,
                    status=dataset.status,
                    created_at=dataset.created_at.isoformat(),
                    updated_at=dataset.updated_at.isoformat()
                )
                dataset_summaries.append(summary)
            
            return dataset_service_pb2.ListDatasetsResponse(
                datasets=dataset_summaries,
                total_count=total_count,
                page=page,
                page_size=page_size
            )
            
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dataset_service_pb2.ListDatasetsResponse()
    
    def GetDataset(self, request, context):
        """Get detailed dataset information"""
        try:
            dataset = Dataset.objects.get(id=request.id)
            columns = dataset.columns.all().order_by('position')
            
            # Convert columns to protobuf
            column_messages = []
            for col in columns:
                col_msg = dataset_service_pb2.DatasetColumn(
                    id=col.id,
                    name=col.name,
                    data_type=col.data_type,
                    nullable=col.nullable,
                    unique=col.unique,
                    primary_key=col.primary_key,
                    null_count=col.null_count,
                    unique_count=col.unique_count,
                    position=col.position,
                    sample_values=col.sample_values or []
                )
                column_messages.append(col_msg)
            
            # Create dataset message
            return dataset_service_pb2.Dataset(
                id=dataset.id,
                name=dataset.name,
                description=dataset.description or "",
                source_file=dataset.source_file or "",
                total_rows=dataset.total_rows,
                total_columns=dataset.total_columns,
                status=dataset.status,
                created_at=dataset.created_at.isoformat(),
                updated_at=dataset.updated_at.isoformat(),
                imported_at=dataset.imported_at.isoformat() if dataset.imported_at else "",
                xml_file_path=dataset.xml_file_path or "",
                xml_schema_path=dataset.xml_schema_path or "",
                columns=column_messages
            )
            
        except Dataset.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Dataset with id {request.id} not found")
            return dataset_service_pb2.Dataset()
        except Exception as e:
            logger.error(f"Error getting dataset: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dataset_service_pb2.Dataset()
    
    def GetDatasetRecords(self, request, context):
        """Get dataset records with pagination"""
        try:
            dataset = Dataset.objects.get(id=request.dataset_id)
            
            limit = request.limit or 100
            offset = request.offset or 0
            
            # Get records
            records = dataset.records.all().order_by('row_number')[offset:offset+limit]
            
            # Convert to protobuf
            record_messages = []
            for record in records:
                rec_msg = dataset_service_pb2.DataRecord(
                    id=record.id,
                    dataset_id=dataset.id,
                    row_number=record.row_number,
                    data_json=json.dumps(record.data),
                    created_at=record.created_at.isoformat()
                )
                record_messages.append(rec_msg)
            
            return dataset_service_pb2.GetDatasetRecordsResponse(
                records=record_messages,
                total_rows=dataset.total_rows,
                offset=offset,
                limit=limit
            )
            
        except Dataset.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Dataset with id {request.dataset_id} not found")
            return dataset_service_pb2.GetDatasetRecordsResponse()
        except Exception as e:
            logger.error(f"Error getting records: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dataset_service_pb2.GetDatasetRecordsResponse()
    
    def GenerateXML(self, request, context):
        """Generate XML and optionally XSD for dataset"""
        try:
            dataset = Dataset.objects.get(id=request.dataset_id)
            xml_service = XMLService(dataset)
            
            result = dataset_service_pb2.GenerateXMLResponse(
                dataset_name=dataset.name,
                xsd_generated=False,
                xml_generated=False
            )
            
            # Generate XSD
            if request.generate_xsd:
                xsd_path = xml_service.generate_xsd()
                result.xsd_generated = True
                result.xsd_path = xsd_path
            
            # Generate XML
            limit = request.limit if request.limit > 0 else None
            xml_path = xml_service.generate_xml(limit=limit)
            result.xml_generated = True
            result.xml_path = xml_path
            
            # Validate
            if request.validate:
                is_valid, errors = xml_service.validate_xml()
                result.validation_passed = is_valid
                result.validation_errors.extend(errors)
            
            return result
            
        except Dataset.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Dataset with id {request.dataset_id} not found")
            return dataset_service_pb2.GenerateXMLResponse()
        except Exception as e:
            logger.error(f"Error generating XML: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dataset_service_pb2.GenerateXMLResponse()
    
    def ValidateXML(self, request, context):
        """Validate existing XML against XSD"""
        try:
            dataset = Dataset.objects.get(id=request.dataset_id)
            xml_service = XMLService(dataset)
            
            is_valid, errors = xml_service.validate_xml()
            
            return dataset_service_pb2.ValidateXMLResponse(
                dataset_name=dataset.name,
                is_valid=is_valid,
                errors=errors
            )
            
        except Dataset.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Dataset with id {request.dataset_id} not found")
            return dataset_service_pb2.ValidateXMLResponse()
        except Exception as e:
            logger.error(f"Error validating XML: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return dataset_service_pb2.ValidateXMLResponse()
    
    def StreamDatasetRecords(self, request, context):
        """Stream dataset records in batches"""
        try:
            dataset = Dataset.objects.get(id=request.dataset_id)
            batch_size = request.batch_size or 100
            
            # Stream records in batches
            offset = 0
            total_records = dataset.total_rows
            
            while offset < total_records:
                records = dataset.records.all().order_by('row_number')[offset:offset+batch_size]
                
                for record in records:
                    yield dataset_service_pb2.DataRecord(
                        id=record.id,
                        dataset_id=dataset.id,
                        row_number=record.row_number,
                        data_json=json.dumps(record.data),
                        created_at=record.created_at.isoformat()
                    )
                
                offset += batch_size
                
        except Dataset.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Dataset with id {request.dataset_id} not found")
        except Exception as e:
            logger.error(f"Error streaming records: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))


def serve(port=50052):
    """Start gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dataset_service_pb2_grpc.add_DatasetServiceServicer_to_server(
        DatasetServicer(), server
    )
    
    # Bind to localhost only
    server.add_insecure_port(f'127.0.0.1:{port}')
    server.start()
    
    logger.info(f"🚀 gRPC Server started on port {port}")
    logger.info(f"   Services:")
    logger.info(f"   - DatasetService (ListDatasets, GetDataset, GetDatasetRecords, GenerateXML, ValidateXML, StreamDatasetRecords)")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
