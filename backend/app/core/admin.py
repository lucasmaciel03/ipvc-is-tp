from django.contrib import admin
from .models import Dataset, DatasetColumn, DataRecord, ImportLog


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_rows', 'total_columns', 'status', 'created_at', 'imported_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'imported_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'source_file', 'status')
        }),
        ('Structure', {
            'fields': ('structure', 'total_rows', 'total_columns')
        }),
        ('XML Files', {
            'fields': ('xml_file_path', 'xml_schema_path')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'imported_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DatasetColumn)
class DatasetColumnAdmin(admin.ModelAdmin):
    list_display = ['name', 'dataset', 'data_type', 'nullable', 'unique', 'position']
    list_filter = ['dataset', 'data_type', 'nullable']
    search_fields = ['name', 'dataset__name']
    ordering = ['dataset', 'position']


@admin.register(DataRecord)
class DataRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'dataset', 'row_number', 'created_at']
    list_filter = ['dataset', 'created_at']
    search_fields = ['dataset__name']
    readonly_fields = ['created_at', 'updated_at']
    
    # Limit records shown in admin for performance
    list_per_page = 50


@admin.register(ImportLog)
class ImportLogAdmin(admin.ModelAdmin):
    list_display = ['level', 'message_preview', 'dataset', 'timestamp']
    list_filter = ['level', 'timestamp', 'dataset']
    search_fields = ['message']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
