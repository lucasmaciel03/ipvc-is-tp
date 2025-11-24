"""
REST API Serializers for IPVC Integration System
"""

from rest_framework import serializers
from app.core.models import Dataset, DatasetColumn, DataRecord, ImportLog


class DatasetColumnSerializer(serializers.ModelSerializer):
    """Serializer for DatasetColumn model"""
    
    class Meta:
        model = DatasetColumn
        fields = [
            'id', 'name', 'data_type', 'nullable', 'unique', 
            'primary_key', 'null_count', 'unique_count', 
            'position', 'sample_values'
        ]


class DatasetListSerializer(serializers.ModelSerializer):
    """Serializer for Dataset list view"""
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'total_rows', 
            'total_columns', 'status', 'created_at', 'updated_at'
        ]


class DatasetDetailSerializer(serializers.ModelSerializer):
    """Serializer for Dataset detail view with columns"""
    columns = DatasetColumnSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dataset
        fields = [
            'id', 'name', 'description', 'source_file',
            'structure', 'total_rows', 'total_columns', 
            'status', 'created_at', 'updated_at', 'imported_at',
            'xml_file_path', 'xml_schema_path', 'columns'
        ]


class DataRecordSerializer(serializers.ModelSerializer):
    """Serializer for DataRecord model"""
    
    class Meta:
        model = DataRecord
        fields = ['id', 'dataset', 'data', 'row_number', 'created_at']


class ImportLogSerializer(serializers.ModelSerializer):
    """Serializer for ImportLog model"""
    
    class Meta:
        model = ImportLog
        fields = ['id', 'dataset', 'level', 'message', 'details', 'timestamp']


class DatasetImportSerializer(serializers.Serializer):
    """Serializer for dataset import requests"""
    file = serializers.FileField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class XMLGenerationSerializer(serializers.Serializer):
    """Serializer for XML generation requests"""
    limit = serializers.IntegerField(required=False, min_value=1)
    generate_xsd = serializers.BooleanField(default=True)
    validate = serializers.BooleanField(default=True)
