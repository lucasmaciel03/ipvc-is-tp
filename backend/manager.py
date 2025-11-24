"""
Main manager script for IPVC Integration System.
Provides CLI commands for dataset management and system operations.
"""

import os
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
import django
django.setup()

from app.csv_processor.processor import CSVImporter, CSVAnalyzer
from app.core.models import Dataset, DataRecord
from app.database.manager import DatabaseManager
from django.conf import settings
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IPVCManager:
    """Main management class for IPVC Integration System"""
    
    @staticmethod
    def import_csv(file_path: str, name: str = None, description: str = None):
        """Import a CSV file into the database"""
        print(f"\n{'='*60}")
        print(f"Importing CSV: {file_path}")
        print(f"{'='*60}\n")
        
        try:
            dataset = CSVImporter.import_csv(
                file_path=file_path,
                dataset_name=name,
                description=description
            )
            
            print(f"\n✓ Import successful!")
            print(f"  Dataset: {dataset.name}")
            print(f"  Rows: {dataset.total_rows}")
            print(f"  Columns: {dataset.total_columns}")
            print(f"  Status: {dataset.status}")
            
        except Exception as e:
            print(f"\n✗ Import failed: {str(e)}")
            sys.exit(1)
    
    @staticmethod
    def list_datasets():
        """List all imported datasets"""
        datasets = Dataset.objects.all()
        
        print(f"\n{'='*80}")
        print(f"{'DATASET NAME':<30} {'ROWS':<10} {'COLS':<10} {'STATUS':<15} {'DATE':<15}")
        print(f"{'='*80}")
        
        for ds in datasets:
            print(f"{ds.name:<30} {ds.total_rows:<10} {ds.total_columns:<10} "
                  f"{ds.status:<15} {ds.created_at.strftime('%Y-%m-%d'):<15}")
        
        print(f"{'='*80}")
        print(f"Total datasets: {datasets.count()}\n")
    
    @staticmethod
    def show_dataset(name: str, limit: int = 10):
        """Show dataset details and sample data"""
        try:
            dataset = Dataset.objects.get(name=name)
            
            print(f"\n{'='*60}")
            print(f"Dataset: {dataset.name}")
            print(f"{'='*60}")
            print(f"Description: {dataset.description}")
            print(f"Source: {dataset.source_file}")
            print(f"Rows: {dataset.total_rows}")
            print(f"Columns: {dataset.total_columns}")
            print(f"Status: {dataset.status}")
            print(f"Created: {dataset.created_at}")
            print(f"\nColumns:")
            
            for col in dataset.columns.all()[:10]:
                print(f"  - {col.name} ({col.data_type})")
            
            print(f"\nSample data (first {limit} rows):")
            records = dataset.records.all()[:limit]
            
            for record in records:
                print(f"  Row {record.row_number}: {record.data}")
            
        except Dataset.DoesNotExist:
            print(f"✗ Dataset '{name}' not found")
            sys.exit(1)
    
    @staticmethod
    def db_info():
        """Show database information"""
        info = DatabaseManager.get_database_info()
        
        print(f"\n{'='*60}")
        print(f"Database Information")
        print(f"{'='*60}")
        print(f"Engine: {info['engine']}")
        print(f"Name: {info['name']}")
        print(f"Host: {info['host']}")
        print(f"Port: {info['port']}")
        
        # Test connection
        if DatabaseManager.test_connection():
            print(f"Status: ✓ Connected")
        else:
            print(f"Status: ✗ Connection failed")
        
        print(f"{'='*60}\n")
    
    @staticmethod
    def analyze_csv(file_path: str):
        """Analyze a CSV file without importing"""
        print(f"\n{'='*60}")
        print(f"Analyzing: {file_path}")
        print(f"{'='*60}\n")
        
        analysis = CSVAnalyzer.analyze_csv(file_path)
        
        print(f"Total Rows: {analysis['total_rows']}")
        print(f"Total Columns: {analysis['total_columns']}")
        print(f"Delimiter: {repr(analysis['delimiter'])}")
        print(f"\nColumn Details:")
        
        for col in analysis['columns']:
            print(f"\n  {col['name']}:")
            print(f"    Type: {col['data_type']}")
            print(f"    Nullable: {col['nullable']}")
            print(f"    Unique values: {col['unique_count']}")
            print(f"    Null count: {col['null_count']}")
            print(f"    Samples: {col['sample_values'][:3]}")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description='IPVC Integration System Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import a CSV file')
    import_parser.add_argument('file', help='Path to CSV file')
    import_parser.add_argument('-n', '--name', help='Dataset name')
    import_parser.add_argument('-d', '--description', help='Dataset description')
    
    # List command
    subparsers.add_parser('list', help='List all datasets')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show dataset details')
    show_parser.add_argument('name', help='Dataset name')
    show_parser.add_argument('-l', '--limit', type=int, default=10, help='Number of rows to show')
    
    # DB info command
    subparsers.add_parser('dbinfo', help='Show database information')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze CSV without importing')
    analyze_parser.add_argument('file', help='Path to CSV file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = IPVCManager()
    
    if args.command == 'import':
        manager.import_csv(args.file, args.name, args.description)
    elif args.command == 'list':
        manager.list_datasets()
    elif args.command == 'show':
        manager.show_dataset(args.name, args.limit)
    elif args.command == 'dbinfo':
        manager.db_info()
    elif args.command == 'analyze':
        manager.analyze_csv(args.file)


if __name__ == '__main__':
    main()
