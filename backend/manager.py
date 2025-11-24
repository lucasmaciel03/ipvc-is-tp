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
from app.xml_tools.xml_service import XMLService
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
    
    @staticmethod
    def generate_xml(name: str, limit: int = None):
        """Generate XML and XSD for a dataset"""
        try:
            dataset = Dataset.objects.get(name=name)
            
            print(f"\n{'='*60}")
            print(f"Generating XML for: {dataset.name}")
            print(f"{'='*60}\n")
            
            # Create XML service
            xml_service = XMLService(dataset)
            
            # Generate XSD
            print("Step 1: Generating XSD schema...")
            xsd_path = xml_service.generate_xsd()
            print(f"✓ XSD generated: {xsd_path}\n")
            
            # Generate XML
            print(f"Step 2: Generating XML (limit: {limit or 'all records'})...")
            xml_path = xml_service.generate_xml(limit=limit)
            print(f"✓ XML generated: {xml_path}\n")
            
            # Validate
            print("Step 3: Validating XML against XSD...")
            is_valid, errors = xml_service.validate_xml()
            
            if is_valid:
                print("✓ XML validation PASSED\n")
            else:
                print("✗ XML validation FAILED")
                print("Errors:")
                for error in errors:
                    print(f"  - {error}")
                print()
            
            print(f"{'='*60}")
            print("Summary:")
            print(f"  XSD: {xsd_path}")
            print(f"  XML: {xml_path}")
            print(f"  Valid: {'Yes' if is_valid else 'No'}")
            print(f"{'='*60}\n")
            
        except Dataset.DoesNotExist:
            print(f"✗ Dataset '{name}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            sys.exit(1)
    
    @staticmethod
    def validate_xml(name: str):
        """Validate XML against XSD for a dataset"""
        try:
            dataset = Dataset.objects.get(name=name)
            
            print(f"\n{'='*60}")
            print(f"Validating XML for: {dataset.name}")
            print(f"{'='*60}\n")
            
            xml_service = XMLService(dataset)
            is_valid, errors = xml_service.validate_xml()
            
            if is_valid:
                print("✓ XML validation PASSED")
            else:
                print("✗ XML validation FAILED")
                print("\nErrors:")
                for error in errors:
                    print(f"  - {error}")
            
            print()
            
        except Dataset.DoesNotExist:
            print(f"✗ Dataset '{name}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            sys.exit(1)
    
    @staticmethod
    def xpath_query(name: str, query: str, output_format: str = 'text'):
        """Execute XPath query on dataset XML"""
        from app.xml_tools.xpath_query import XPathQueryEngine
        import json
        
        try:
            dataset = Dataset.objects.get(name=name)
        except Dataset.DoesNotExist:
            print(f"✗ Dataset '{name}' not found")
            sys.exit(1)
        
        if not dataset.xml_file_path:
            print(f"✗ No XML file for dataset '{name}'")
            print(f"Generate XML first: python manager.py xml {name} -l 100")
            sys.exit(1)
        
        print(f"\n{'='*60}")
        print(f"XPath Query: {dataset.name}")
        print(f"{'='*60}")
        print(f"Query: {query}")
        print(f"Format: {output_format}")
        print(f"{'='*60}\n")
        
        try:
            xpath_engine = XPathQueryEngine(dataset)
            
            if output_format == 'text':
                results = xpath_engine.get_element_text(query)
                print(f"Results ({len(results)} items):")
                for i, result in enumerate(results[:50], 1):  # Show first 50
                    print(f"  {i}. {result}")
                if len(results) > 50:
                    print(f"  ... and {len(results) - 50} more")
            
            elif output_format == 'count':
                count = xpath_engine.count_elements(query)
                print(f"Count: {count}")
            
            else:  # dict
                results = xpath_engine.query_to_dict(query)
                print(f"Results ({len(results)} items):")
                for i, result in enumerate(results[:10], 1):  # Show first 10
                    print(f"\n{i}. {json.dumps(result, indent=2)}")
                if len(results) > 10:
                    print(f"\n... and {len(results) - 10} more")
            
            print(f"\n{'='*60}")
            print("✓ Query executed successfully")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n✗ Query failed: {e}")
            sys.exit(1)


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
    
    # Generate XML command
    xml_parser = subparsers.add_parser('xml', help='Generate XML and XSD for dataset')
    xml_parser.add_argument('name', help='Dataset name')
    xml_parser.add_argument('-l', '--limit', type=int, help='Limit number of records')
    
    # Validate XML command
    validate_parser = subparsers.add_parser('validate', help='Validate XML against XSD')
    validate_parser.add_argument('name', help='Dataset name')
    
    # XPath query command
    xpath_parser = subparsers.add_parser('xpath', help='Execute XPath query on XML')
    xpath_parser.add_argument('name', help='Dataset name')
    xpath_parser.add_argument('query', help='XPath expression')
    xpath_parser.add_argument('-f', '--format', choices=['dict', 'text', 'count'], 
                             default='text', help='Output format')
    
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
    elif args.command == 'xml':
        manager.generate_xml(args.name, args.limit)
    elif args.command == 'validate':
        manager.validate_xml(args.name)
    elif args.command == 'xpath':
        manager.xpath_query(args.name, args.query, args.format)


if __name__ == '__main__':
    main()
