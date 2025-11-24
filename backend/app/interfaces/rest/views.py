"""
REST API Views for IPVC Integration System
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile
import os

from app.core.models import Dataset, DatasetColumn, DataRecord, ImportLog
from app.csv_processor.processor import CSVImporter
from app.xml_tools.xml_service import XMLService
from .serializers import (
    DatasetListSerializer, DatasetDetailSerializer,
    DatasetColumnSerializer, DataRecordSerializer,
    ImportLogSerializer, DatasetImportSerializer,
    XMLGenerationSerializer
)


class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Dataset operations.
    
    list: Get all datasets
    retrieve: Get a specific dataset with columns
    columns: Get columns for a dataset
    records: Get data records for a dataset
    logs: Get import logs for a dataset
    import_csv: Import a new CSV file
    generate_xml: Generate XML and XSD for a dataset
    validate_xml: Validate XML against XSD
    """
    
    queryset = Dataset.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DatasetListSerializer
        return DatasetDetailSerializer
    
    @action(detail=True, methods=['get'])
    def columns(self, request, pk=None):
        """Get all columns for a dataset"""
        dataset = self.get_object()
        columns = dataset.columns.all().order_by('position')
        serializer = DatasetColumnSerializer(columns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        """Get data records for a dataset with pagination"""
        dataset = self.get_object()
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        
        # Get records
        records = dataset.records.all().order_by('row_number')[offset:offset+limit]
        
        return Response({
            'dataset': dataset.name,
            'total_rows': dataset.total_rows,
            'offset': offset,
            'limit': limit,
            'count': records.count(),
            'records': [record.data for record in records]
        })
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get import logs for a dataset"""
        dataset = self.get_object()
        logs = dataset.logs.all().order_by('-timestamp')
        serializer = ImportLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def import_csv(self, request):
        """
        Import a CSV file and create a new dataset.
        
        Expected form data:
        - file: CSV file
        - name: Dataset name (optional, will use filename)
        - description: Dataset description (optional)
        """
        serializer = DatasetImportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid request', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        csv_file = serializer.validated_data['file']
        dataset_name = serializer.validated_data.get('name') or csv_file.name.rsplit('.', 1)[0]
        description = serializer.validated_data.get('description', '')
        
        # Save uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, csv_file.name)
        
        try:
            # Write file to temp location
            with open(temp_path, 'wb+') as destination:
                for chunk in csv_file.chunks():
                    destination.write(chunk)
            
            # Import CSV
            dataset = CSVImporter.import_csv(
                file_path=temp_path,
                dataset_name=dataset_name,
                description=description
            )
            
            serializer = DatasetDetailSerializer(dataset)
            
            return Response({
                'message': 'CSV imported successfully',
                'dataset': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Import failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
    
    @action(detail=True, methods=['post'])
    def generate_xml(self, request, pk=None):
        """
        Generate XML and optionally XSD for a dataset.
        
        Optional parameters:
        - limit: Limit number of records to export
        - generate_xsd: Generate XSD schema (default: true)
        - validate: Validate XML against XSD (default: true)
        """
        dataset = self.get_object()
        serializer = XMLGenerationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid request', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        limit = serializer.validated_data.get('limit')
        generate_xsd = serializer.validated_data.get('generate_xsd', True)
        validate = serializer.validated_data.get('validate', True)
        
        try:
            xml_service = XMLService(dataset)
            result = {
                'dataset': dataset.name,
                'xsd_generated': False,
                'xml_generated': False,
                'validation_passed': None
            }
            
            # Generate XSD
            if generate_xsd:
                xsd_path = xml_service.generate_xsd()
                result['xsd_path'] = xsd_path
                result['xsd_generated'] = True
            
            # Generate XML
            xml_path = xml_service.generate_xml(limit=limit)
            result['xml_path'] = xml_path
            result['xml_generated'] = True
            
            # Validate
            if validate:
                is_valid, errors = xml_service.validate_xml()
                result['validation_passed'] = is_valid
                result['validation_errors'] = errors
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'XML generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def validate_xml(self, request, pk=None):
        """Validate existing XML against XSD"""
        dataset = self.get_object()
        
        try:
            xml_service = XMLService(dataset)
            is_valid, errors = xml_service.validate_xml()
            
            return Response({
                'dataset': dataset.name,
                'is_valid': is_valid,
                'errors': errors
            })
            
        except Exception as e:
            return Response(
                {'error': f'Validation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DataRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for DataRecord operations.
    
    Allows querying individual records across all datasets.
    """
    queryset = DataRecord.objects.all()
    serializer_class = DataRecordSerializer
    
    def get_queryset(self):
        queryset = DataRecord.objects.all()
        
        # Filter by dataset if provided
        dataset_id = self.request.query_params.get('dataset')
        if dataset_id:
            queryset = queryset.filter(dataset_id=dataset_id)
        
        return queryset.order_by('dataset', 'row_number')
