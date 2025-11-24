"""
Core models for dynamic dataset management.
This module provides a flexible architecture to handle any CSV structure.
"""

from django.db import models
from django.contrib.postgres.fields import JSONField as PostgresJSONField
from django.core.exceptions import ValidationError
from django.utils import timezone
import json


class Dataset(models.Model):
    """
    Represents a dataset imported from CSV or other sources.
    Stores metadata about the dataset structure.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    source_file = models.CharField(max_length=500, help_text="Original CSV file path")
    
    # Dataset structure stored as JSON
    # Example: {"columns": [{"name": "product_id", "type": "string", "nullable": false}, ...]}
    structure = models.JSONField(default=dict, help_text="Dataset schema definition")
    
    # Statistics
    total_rows = models.IntegerField(default=0)
    total_columns = models.IntegerField(default=0)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    imported_at = models.DateTimeField(null=True, blank=True)
    
    # XML related
    xml_file_path = models.CharField(max_length=500, blank=True, null=True)
    xml_schema_path = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        db_table = 'datasets'
        ordering = ['-created_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
    
    def __str__(self):
        return f"{self.name} ({self.total_rows} rows)"
    
    def mark_as_completed(self):
        """Mark dataset import as completed"""
        self.status = 'completed'
        self.imported_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark dataset import as failed"""
        self.status = 'failed'
        self.save()


class DatasetColumn(models.Model):
    """
    Represents individual columns in a dataset.
    Provides detailed metadata about each column.
    """
    
    DATA_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('decimal', 'Decimal'),
    ]
    
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name='columns'
    )
    
    name = models.CharField(max_length=255, db_index=True)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    
    # Column properties
    nullable = models.BooleanField(default=True)
    unique = models.BooleanField(default=False)
    primary_key = models.BooleanField(default=False)
    
    # Statistics
    null_count = models.IntegerField(default=0)
    unique_count = models.IntegerField(default=0)
    
    # Order in the dataset
    position = models.IntegerField(default=0)
    
    # Additional metadata
    sample_values = models.JSONField(
        default=list, 
        help_text="Sample values from this column"
    )
    
    class Meta:
        db_table = 'dataset_columns'
        ordering = ['dataset', 'position']
        unique_together = [['dataset', 'name']]
        verbose_name = 'Dataset Column'
        verbose_name_plural = 'Dataset Columns'
    
    def __str__(self):
        return f"{self.dataset.name}.{self.name} ({self.data_type})"


class DataRecord(models.Model):
    """
    Generic model to store actual data records from any dataset.
    Uses JSON field for flexibility to accommodate any structure.
    """
    
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name='records',
        db_index=True
    )
    
    # Stores the actual row data as JSON
    # Example: {"product_id": "b12c721e", "product_name": "Lamb", "price_per_kg": 14.10, ...}
    data = models.JSONField(help_text="Row data as JSON object")
    
    # Optional: Store original row number from CSV
    row_number = models.IntegerField(null=True, blank=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'data_records'
        ordering = ['dataset', 'row_number']
        indexes = [
            models.Index(fields=['dataset', 'row_number']),
            models.Index(fields=['dataset', 'created_at']),
        ]
        verbose_name = 'Data Record'
        verbose_name_plural = 'Data Records'
    
    def __str__(self):
        return f"Record #{self.row_number} from {self.dataset.name}"
    
    def get_field(self, field_name):
        """Get a specific field value from the JSON data"""
        return self.data.get(field_name)
    
    def set_field(self, field_name, value):
        """Set a specific field value in the JSON data"""
        self.data[field_name] = value
        self.save()


class ImportLog(models.Model):
    """
    Tracks import operations and their results.
    """
    
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ]
    
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name='logs',
        null=True,
        blank=True
    )
    
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'import_logs'
        ordering = ['-timestamp']
        verbose_name = 'Import Log'
        verbose_name_plural = 'Import Logs'
    
    def __str__(self):
        return f"[{self.level.upper()}] {self.message[:50]}"
