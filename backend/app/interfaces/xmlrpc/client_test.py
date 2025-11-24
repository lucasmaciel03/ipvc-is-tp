"""
XML-RPC Client Test for IPVC Integration System
"""

import xmlrpc.client
import json
from pprint import pprint


def run_tests():
    """Run XML-RPC client tests"""
    
    # Connect to XML-RPC server
    proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8001/RPC2')
    
    print("="*80)
    print("🚀 IPVC Integration System - XML-RPC Client Tests")
    print("="*80)
    
    # Test 1: List Datasets
    print("\n\n🔍 TEST 1: List Datasets")
    print("-"*80)
    try:
        result = proxy.list_datasets(1, 10)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print(f"Total datasets: {result['total_count']}")
        print(f"Page: {result['page']}, Page size: {result['page_size']}")
        print(f"\nDatasets:")
        for dataset in result['datasets']:
            print(f"  • ID: {dataset['id']}")
            print(f"    Name: {dataset['name']}")
            print(f"    Rows: {dataset['total_rows']}, Columns: {dataset['total_columns']}")
            print(f"    Status: {dataset['status']}")
            print()
        
        dataset_id = result['datasets'][0]['id'] if result['datasets'] else None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    if not dataset_id:
        print("❌ No datasets found. Please import CSV files first.")
        return
    
    # Test 2: Get Dataset Detail
    print(f"\n\n🔍 TEST 2: Get Dataset Detail (ID={dataset_id})")
    print("-"*80)
    try:
        result = proxy.get_dataset(dataset_id)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Dataset: {result['name']}")
            print(f"Description: {result['description']}")
            print(f"Total rows: {result['total_rows']}")
            print(f"Total columns: {result['total_columns']}")
            print(f"Status: {result['status']}")
            print(f"Created: {result['created_at']}")
            print(f"XML path: {result['xml_file_path']}")
            print(f"XSD path: {result['xml_schema_path']}")
            print(f"\nColumns ({len(result['columns'])}):")
            for col in result['columns'][:5]:
                print(f"  • {col['name']} ({col['data_type']})")
                print(f"    Nullable: {col['nullable']}, Unique: {col['unique']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get Dataset Statistics
    print(f"\n\n🔍 TEST 3: Get Dataset Statistics (ID={dataset_id})")
    print("-"*80)
    try:
        result = proxy.get_dataset_stats(dataset_id)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Dataset: {result['dataset_name']}")
            print(f"Total rows: {result['total_rows']}")
            print(f"Total columns: {result['total_columns']}")
            print(f"Status: {result['status']}")
            print(f"Has XML: {result['has_xml']}")
            print(f"Has XSD: {result['has_xsd']}")
            print(f"Created: {result['created_at']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get Dataset Columns
    print(f"\n\n🔍 TEST 4: Get Dataset Columns (ID={dataset_id})")
    print("-"*80)
    try:
        result = proxy.get_dataset_columns(dataset_id)
        
        if isinstance(result, dict) and 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Columns ({len(result)}):")
            for col in result[:5]:
                print(f"  • {col['name']} ({col['data_type']})")
                print(f"    Position: {col['position']}, Nullable: {col['nullable']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Get Dataset Records
    print(f"\n\n🔍 TEST 5: Get Dataset Records (ID={dataset_id}, limit=5)")
    print("-"*80)
    try:
        result = proxy.get_dataset_records(dataset_id, 5, 0)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Dataset: {result['dataset']}")
            print(f"Total rows: {result['total_rows']}")
            print(f"Offset: {result['offset']}, Limit: {result['limit']}")
            print(f"Retrieved: {result['count']} records")
            print(f"\nRecords:")
            for record in result['records'][:3]:
                print(f"  • Row {record['row_number']}:")
                # Show first 3 fields
                for i, (key, value) in enumerate(list(record['data'].items())[:3]):
                    print(f"    {key}: {value}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: Generate XML
    print(f"\n\n🔍 TEST 6: Generate XML (ID={dataset_id}, limit=10)")
    print("-"*80)
    try:
        result = proxy.generate_xml(dataset_id, 10, True, True)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Dataset: {result['dataset_name']}")
            print(f"XSD Generated: {result['xsd_generated']}")
            if result['xsd_generated']:
                print(f"  Path: {result.get('xsd_path', 'N/A')}")
            print(f"XML Generated: {result['xml_generated']}")
            if result['xml_generated']:
                print(f"  Path: {result.get('xml_path', 'N/A')}")
            print(f"Validation Passed: {result.get('validation_passed', 'N/A')}")
            if result.get('validation_errors'):
                print(f"Validation Errors:")
                for error in result['validation_errors'][:2]:
                    print(f"  • {error[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 7: Validate XML
    print(f"\n\n🔍 TEST 7: Validate XML (ID={dataset_id})")
    print("-"*80)
    try:
        result = proxy.validate_xml(dataset_id)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"Dataset: {result['dataset_name']}")
            print(f"Is Valid: {result['is_valid']}")
            if result['errors']:
                print(f"Errors ({len(result['errors'])}):")
                for error in result['errors'][:2]:
                    print(f"  • {error[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: List System Methods
    print(f"\n\n🔍 TEST 8: List Available Methods")
    print("-"*80)
    try:
        methods = proxy.system.listMethods()
        print(f"Available methods ({len(methods)}):")
        for method in methods:
            if not method.startswith('system.'):
                print(f"  • {method}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n\n" + "="*80)
    print("✅ All XML-RPC tests completed!")
    print("="*80)
    print("\n📝 XML-RPC Methods:")
    print("   • list_datasets          - List all datasets with pagination")
    print("   • get_dataset            - Get detailed dataset information")
    print("   • get_dataset_records    - Get dataset records with pagination")
    print("   • get_dataset_columns    - Get dataset column definitions")
    print("   • get_dataset_stats      - Get dataset statistics")
    print("   • generate_xml           - Generate XML and XSD for dataset")
    print("   • validate_xml           - Validate XML against XSD")
    print("\n🌐 XML-RPC Server: http://127.0.0.1:8001/")


if __name__ == '__main__':
    try:
        run_tests()
    except ConnectionRefusedError:
        print("\n❌ ERROR: Could not connect to XML-RPC server.")
        print("   Make sure XML-RPC server is running:")
        print("   python app/interfaces/xmlrpc/server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
