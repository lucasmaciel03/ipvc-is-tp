"""
XPath/XQuery Testing Script
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://127.0.0.1:8000/api"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status: {response.status_code}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2)[:2000])
    except:
        print(response.text[:500])


def test_xpath_examples():
    """Test 1: Get XPath examples"""
    print("\n\n🔍 TEST 1: Get XPath Query Examples")
    response = requests.get(f"{BASE_URL}/xpath/")
    print_response("GET /api/xpath/", response)


def test_xpath_execute(dataset_id=1):
    """Test 2: Execute XPath queries"""
    print(f"\n\n🔍 TEST 2: Execute XPath Queries (Dataset ID={dataset_id})")
    
    queries = [
        {
            'name': 'First 3 records',
            'xpath': '//record[position() <= 3]',
            'format': 'dict'
        },
        {
            'name': 'All State_Name values',
            'xpath': '//record/State_Name/text()',
            'format': 'text'
        },
        {
            'name': 'Count total records',
            'xpath': '//record',
            'format': 'count'
        },
    ]
    
    for query in queries:
        print(f"\n--- {query['name']} ---")
        response = requests.post(
            f"{BASE_URL}/xpath/execute/",
            json={
                'dataset_id': dataset_id,
                'xpath': query['xpath'],
                'format': query['format']
            }
        )
        print_response(f"XPath: {query['xpath']}", response)


def test_xpath_statistics(dataset_id=1):
    """Test 3: Get XML statistics"""
    print(f"\n\n🔍 TEST 3: Get XML Statistics (Dataset ID={dataset_id})")
    
    response = requests.post(
        f"{BASE_URL}/xpath/statistics/",
        json={'dataset_id': dataset_id}
    )
    print_response("POST /api/xpath/statistics/", response)


def test_aggregate(dataset_id=1):
    """Test 4: Aggregate operations"""
    print(f"\n\n🔍 TEST 4: Aggregate Operations (Dataset ID={dataset_id})")
    
    operations = ['count', 'sum', 'avg', 'min', 'max']
    
    for operation in operations:
        print(f"\n--- {operation.upper()} of Area field ---")
        response = requests.post(
            f"{BASE_URL}/xpath/aggregate/",
            json={
                'dataset_id': dataset_id,
                'field': 'Area',
                'operation': operation
            }
        )
        print_response(f"Aggregate: {operation}", response)


def test_group_by(dataset_id=1):
    """Test 5: Group by operations"""
    print(f"\n\n🔍 TEST 5: Group By Operations (Dataset ID={dataset_id})")
    
    print("\n--- Group by Season (with Area aggregation) ---")
    response = requests.post(
        f"{BASE_URL}/xpath/group_by/",
        json={
            'dataset_id': dataset_id,
            'group_field': 'Season',
            'aggregate_field': 'Area'
        }
    )
    print_response("Group by Season", response)


def test_flwor_query(dataset_id=1):
    """Test 6: FLWOR-like queries"""
    print(f"\n\n🔍 TEST 6: FLWOR-like Queries (Dataset ID={dataset_id})")
    
    queries = [
        {
            'name': 'Simple query - all records',
            'for': '//record',
            'where': None,
            'return': None
        },
        {
            'name': 'Query with WHERE - filter by Crop',
            'for': '//record',
            'where': 'Crop="Rice"',
            'return': None
        },
        {
            'name': 'Query with WHERE and RETURN',
            'for': '//record',
            'where': 'Crop="Rice"',
            'return': 'State_Name'
        },
    ]
    
    for query in queries:
        print(f"\n--- {query['name']} ---")
        data = {'dataset_id': dataset_id, 'for': query['for']}
        if query['where']:
            data['where'] = query['where']
        if query['return']:
            data['return'] = query['return']
        
        response = requests.post(
            f"{BASE_URL}/xpath/query/",
            json=data
        )
        print_response(f"FLWOR Query", response)


def test_advanced_xpath(dataset_id=1):
    """Test 7: Advanced XPath queries"""
    print(f"\n\n🔍 TEST 7: Advanced XPath Queries (Dataset ID={dataset_id})")
    
    queries = [
        {
            'name': 'Get distinct Crop values',
            'xpath': '//record/Crop[not(. = preceding::Crop)]/text()',
            'format': 'text'
        },
        {
            'name': 'Last 5 records',
            'xpath': '//record[position() > last()-5]',
            'format': 'dict'
        },
        {
            'name': 'Records with specific Season',
            'xpath': '//record[Season="Kharif"]',
            'format': 'count'
        },
    ]
    
    for query in queries:
        print(f"\n--- {query['name']} ---")
        response = requests.post(
            f"{BASE_URL}/xpath/execute/",
            json={
                'dataset_id': dataset_id,
                'xpath': query['xpath'],
                'format': query['format']
            }
        )
        print_response(f"XPath: {query['xpath']}", response)


def run_all_tests():
    """Run all XPath/XQuery tests"""
    print("="*80)
    print("🚀 IPVC Integration System - XPath/XQuery Tests")
    print("="*80)
    
    # Get datasets first
    print("\n📋 Getting available datasets...")
    response = requests.get(f"{BASE_URL}/datasets/")
    
    if response.status_code != 200:
        print("❌ Could not connect to API. Make sure Django server is running.")
        return
    
    datasets = response.json().get('results', [])
    
    if not datasets:
        print("❌ No datasets found. Please import CSV and generate XML first:")
        print("   python manager.py import ../data/AgricultureData.csv agriculture")
        print("   python manager.py xml agriculture -l 100")
        return
    
    # Find a dataset with XML
    dataset = None
    for ds in datasets:
        response_detail = requests.get(f"{BASE_URL}/datasets/{ds['id']}/")
        dataset_detail = response_detail.json()
        if dataset_detail.get('xml_file_path'):
            dataset = dataset_detail
            break
    
    if not dataset:
        print("❌ No datasets with XML found. Generate XML first:")
        print("   python manager.py xml agriculture -l 100")
        return
    
    dataset_id = dataset['id']
    dataset_name = dataset['name']
    
    print(f"✅ Using dataset: {dataset_name} (ID={dataset_id})")
    print(f"   XML: {dataset['xml_file_path']}")
    print(f"   XSD: {dataset['xml_schema_path']}")
    
    # Run tests
    test_xpath_examples()
    test_xpath_execute(dataset_id)
    test_xpath_statistics(dataset_id)
    test_aggregate(dataset_id)
    test_group_by(dataset_id)
    test_flwor_query(dataset_id)
    test_advanced_xpath(dataset_id)
    
    print("\n\n" + "="*80)
    print("✅ All XPath/XQuery tests completed!")
    print("="*80)
    print("\n📝 XPath/XQuery API Endpoints:")
    print("   • GET    /api/xpath/                - List examples")
    print("   • POST   /api/xpath/execute/        - Execute XPath query")
    print("   • POST   /api/xpath/statistics/     - Get XML statistics")
    print("   • POST   /api/xpath/aggregate/      - Aggregate operations")
    print("   • POST   /api/xpath/group_by/       - Group by field")
    print("   • POST   /api/xpath/query/          - FLWOR-like query")
    print("\n🌐 REST API: http://127.0.0.1:8000/api/xpath/")
    print("\n💡 Examples:")
    print("   curl -X POST http://127.0.0.1:8000/api/xpath/execute/ \\")
    print("     -H 'Content-Type: application/json' \\")
    print('     -d \'{"dataset_id": 1, "xpath": "//record[1]", "format": "dict"}\'')


if __name__ == '__main__':
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server.")
        print("   Make sure Django server is running:")
        print("   python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
