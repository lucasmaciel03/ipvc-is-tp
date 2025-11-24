"""
Intelligent CSV Processor that automatically analyzes and imports any CSV structure.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from django.conf import settings
from django.db import transaction
import logging
import re
from datetime import datetime

from app.core.models import Dataset, DatasetColumn, DataRecord, ImportLog

logger = logging.getLogger(__name__)


class CSVAnalyzer:
    """
    Analyzes CSV files to determine structure, data types, and statistics.
    """
    
    # Common date formats to detect
    DATE_FORMATS = [
        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
        '%d-%m-%Y', '%m-%d-%Y', '%d.%m.%Y', '%Y.%m.%d',
        '%d/%m/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'
    ]
    
    @staticmethod
    def detect_delimiter(file_path: str, sample_size: int = 5) -> str:
        """
        Detect CSV delimiter by analyzing first few lines.
        Supports: comma, semicolon, tab, pipe
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [f.readline() for _ in range(sample_size)]
        
        delimiters = [',', ';', '\t', '|']
        delimiter_counts = {d: sum(line.count(d) for line in lines) for d in delimiters}
        
        # Return delimiter with highest count
        detected = max(delimiter_counts.items(), key=lambda x: x[1])[0]
        logger.info(f"Detected delimiter: {repr(detected)}")
        return detected
    
    @staticmethod
    def infer_data_type(series: pd.Series) -> str:
        """
        Intelligently infer the data type of a pandas Series.
        """
        # Remove null values for analysis
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return 'string'
        
        # Try boolean first
        if non_null_series.dtype == bool or set(non_null_series.unique()).issubset({True, False, 'True', 'False', 'true', 'false', 0, 1}):
            return 'boolean'
        
        # Try integer
        try:
            if all(float(x).is_integer() for x in non_null_series if pd.notna(x)):
                return 'integer'
        except (ValueError, TypeError):
            pass
        
        # Try float
        try:
            pd.to_numeric(non_null_series)
            return 'float'
        except (ValueError, TypeError):
            pass
        
        # Try datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        # Try parsing as date with common formats
        for date_format in CSVAnalyzer.DATE_FORMATS:
            try:
                pd.to_datetime(non_null_series, format=date_format)
                return 'date'
            except (ValueError, TypeError):
                continue
        
        # Check if it looks like a date (contains /, -, or digits in date pattern)
        sample = str(non_null_series.iloc[0]) if len(non_null_series) > 0 else ''
        if re.match(r'\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4}', sample):
            return 'date'
        
        # Default to string
        return 'string'
    
    @classmethod
    def analyze_csv(cls, file_path: str) -> Dict[str, Any]:
        """
        Perform complete analysis of a CSV file.
        Returns structure, statistics, and metadata.
        """
        logger.info(f"Analyzing CSV file: {file_path}")
        
        # Detect delimiter
        delimiter = cls.detect_delimiter(file_path)
        
        # Read CSV with pandas
        df = pd.read_csv(file_path, delimiter=delimiter, low_memory=False)
        
        # Basic statistics
        total_rows = len(df)
        total_columns = len(df.columns)
        
        # Analyze each column
        columns_info = []
        for idx, col in enumerate(df.columns):
            col_series = df[col]
            data_type = cls.infer_data_type(col_series)
            
            # Statistics
            null_count = col_series.isna().sum()
            unique_count = col_series.nunique()
            
            # Sample values (first 5 unique non-null values)
            sample_values = col_series.dropna().unique()[:5].tolist()
            
            # Convert numpy types to Python types for JSON serialization
            sample_values = [
                int(v) if isinstance(v, (np.integer, np.int64)) else
                float(v) if isinstance(v, (np.floating, np.float64)) else
                str(v)
                for v in sample_values
            ]
            
            columns_info.append({
                'name': col,
                'data_type': data_type,
                'position': idx,
                'nullable': bool(null_count > 0),
                'null_count': int(null_count),
                'unique_count': int(unique_count),
                'unique': bool(unique_count == total_rows),
                'sample_values': sample_values
            })
        
        logger.info(f"Analysis complete: {total_rows} rows, {total_columns} columns")
        
        return {
            'total_rows': total_rows,
            'total_columns': total_columns,
            'columns': columns_info,
            'delimiter': delimiter,
            'dataframe': df  # Return for further processing
        }


class CSVImporter:
    """
    Imports CSV data into the database using the flexible schema.
    """
    
    @staticmethod
    def import_csv(
        file_path: str,
        dataset_name: str = None,
        description: str = None,
        batch_size: int = 1000
    ) -> Dataset:
        """
        Import a CSV file into the database.
        Automatically analyzes structure and imports data.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Use filename as dataset name if not provided
        if not dataset_name:
            dataset_name = file_path.stem
        
        logger.info(f"Starting import of {file_path} as '{dataset_name}'")
        
        try:
            # Analyze CSV structure
            analysis = CSVAnalyzer.analyze_csv(str(file_path))
            df = analysis['dataframe']
            
            with transaction.atomic():
                # Create Dataset record
                dataset = Dataset.objects.create(
                    name=dataset_name,
                    description=description or f"Imported from {file_path.name}",
                    source_file=str(file_path),
                    total_rows=analysis['total_rows'],
                    total_columns=analysis['total_columns'],
                    structure={'columns': analysis['columns']},
                    status='processing'
                )
                
                ImportLog.objects.create(
                    dataset=dataset,
                    level='info',
                    message=f"Starting import of {analysis['total_rows']} rows"
                )
                
                # Create DatasetColumn records
                for col_info in analysis['columns']:
                    DatasetColumn.objects.create(
                        dataset=dataset,
                        name=col_info['name'],
                        data_type=col_info['data_type'],
                        position=col_info['position'],
                        nullable=col_info['nullable'],
                        unique=col_info['unique'],
                        null_count=col_info['null_count'],
                        unique_count=col_info['unique_count'],
                        sample_values=col_info['sample_values']
                    )
                
                # Import data records in batches
                records_to_create = []
                for idx, row in df.iterrows():
                    # Convert row to dict, handling NaN values
                    row_data = row.to_dict()
                    
                    # Clean up data for JSON storage
                    cleaned_data = {}
                    for key, value in row_data.items():
                        if pd.isna(value):
                            cleaned_data[key] = None
                        elif isinstance(value, (np.integer, np.int64)):
                            cleaned_data[key] = int(value)
                        elif isinstance(value, (np.floating, np.float64)):
                            cleaned_data[key] = float(value)
                        else:
                            cleaned_data[key] = str(value)
                    
                    records_to_create.append(
                        DataRecord(
                            dataset=dataset,
                            data=cleaned_data,
                            row_number=idx + 1
                        )
                    )
                    
                    # Batch insert for performance
                    if len(records_to_create) >= batch_size:
                        DataRecord.objects.bulk_create(records_to_create)
                        records_to_create = []
                        logger.info(f"Imported {idx + 1}/{analysis['total_rows']} rows")
                
                # Insert remaining records
                if records_to_create:
                    DataRecord.objects.bulk_create(records_to_create)
                
                # Mark as completed
                dataset.mark_as_completed()
                
                ImportLog.objects.create(
                    dataset=dataset,
                    level='success',
                    message=f"Successfully imported {analysis['total_rows']} rows"
                )
                
                logger.info(f"Import completed successfully for '{dataset_name}'")
                return dataset
                
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            
            if 'dataset' in locals():
                dataset.mark_as_failed()
                ImportLog.objects.create(
                    dataset=dataset,
                    level='error',
                    message=f"Import failed: {str(e)}"
                )
            
            raise
    
    @staticmethod
    def get_dataset_data(dataset: Dataset, limit: int = None) -> pd.DataFrame:
        """
        Retrieve dataset data as pandas DataFrame.
        """
        records = dataset.records.all()
        
        if limit:
            records = records[:limit]
        
        data = [record.data for record in records]
        return pd.DataFrame(data)
