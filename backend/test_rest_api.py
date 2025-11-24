"""
REST API Testing Script
Tests all REST API endpoints for the IPVC Integration System
"""

import requests
import json
from pprint import pprint

# Base URL
BASE_URL = "http://127.0.0.1:8000/api"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status: {response.status_code}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2)[:2000])  # Limit output
    except:
        print(response.text[:500])


def test_list_datasets():
    """Test GET /api/datasets/"""
    print("\n\n🔍 TEST 1: List All Datasets")
    response = requests.get(f"{BASE_URL}/datasets/")
    print_response("GET /api/datasets/", response)
    return response.json() if response.status_code == 200 else None


def test_dataset_detail(dataset_id):
    """Test GET /api/datasets/{id}/"""
    print(f"\n\n🔍 TEST 2: Dataset Detail (ID={dataset_id})")
    response = requests.get(f"{BASE_URL}/datasets/{dataset_id}/")
    print_response(f"GET /api/datasets/{dataset_id}/", response)


def test_dataset_columns(dataset_id):
    """Test GET /api/datasets/{id}/columns/"""
    print(f"\n\n🔍 TEST 3: Dataset Columns (ID={dataset_id})")
    response = requests.get(f"{BASE_URL}/datasets/{dataset_id}/columns/")
    print_response(f"GET /api/datasets/{dataset_id}/columns/", response)


def test_dataset_records(dataset_id, limit=10):
    """Test GET /api/datasets/{id}/records/"""
    print(f"\n\n🔍 TEST 4: Dataset Records (ID={dataset_id}, limit={limit})")
    response = requests.get(f"{BASE_URL}/datasets/{dataset_id}/records/?limit={limit}")
    print_response(f"GET /api/datasets/{dataset_id}/records/?limit={limit}", response)


def test_dataset_logs(dataset_id):
    """Test GET /api/datasets/{id}/logs/"""
    print(f"\n\n🔍 TEST 5: Dataset Import Logs (ID={dataset_id})")
    response = requests.get(f"{BASE_URL}/datasets/{dataset_id}/logs/")
    print_response(f"GET /api/datasets/{dataset_id}/logs/", response)


def test_generate_xml(dataset_id, limit=5):
    """Test POST /api/datasets/{id}/generate_xml/"""
    print(f"\n\n🔍 TEST 6: Generate XML (ID={dataset_id}, limit={limit})")
    
    data = {
        "limit": limit,
        "generate_xsd": True,
        "validate": True
    }
    
    response = requests.post(
        f"{BASE_URL}/datasets/{dataset_id}/generate_xml/",
        json=data
    )
    print_response(f"POST /api/datasets/{dataset_id}/generate_xml/", response)


def test_validate_xml(dataset_id):
    """Test POST /api/datasets/{id}/validate_xml/"""
    print(f"\n\n🔍 TEST 7: Validate XML (ID={dataset_id})")
    response = requests.post(f"{BASE_URL}/datasets/{dataset_id}/validate_xml/")
    print_response(f"POST /api/datasets/{dataset_id}/validate_xml/", response)


def test_list_records(dataset_id=None):
    """Test GET /api/records/"""
    print(f"\n\n🔍 TEST 8: List All Records")
    
    url = f"{BASE_URL}/records/"
    if dataset_id:
        url += f"?dataset={dataset_id}"
    
    response = requests.get(url)
    print_response(f"GET {url}", response)


def run_all_tests():
    """Run all API tests"""
    print("="*80)
    print("🚀 IPVC Integration System - REST API Tests")
    print("="*80)
    
    # Test 1: List datasets
    datasets_response = test_list_datasets()
    
    if not datasets_response or 'results' not in datasets_response:
        print("\n❌ No datasets found. Please import CSV files first.")
        return
    
    datasets = datasets_response['results']
    
    if not datasets:
        print("\n❌ No datasets found. Please import CSV files first.")
        return
    
    # Use first dataset for remaining tests
    dataset_id = datasets[0]['id']
    dataset_name = datasets[0]['name']
    
    print(f"\n✅ Using dataset: {dataset_name} (ID={dataset_id}) for tests")
    
    # Test 2-8
    test_dataset_detail(dataset_id)
    test_dataset_columns(dataset_id)
    test_dataset_records(dataset_id, limit=5)
    test_dataset_logs(dataset_id)
    test_generate_xml(dataset_id, limit=5)
    test_validate_xml(dataset_id)
    test_list_records(dataset_id)
    
    print("\n\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)
    print("\n📝 REST API Endpoints Summary:")
    print("   • GET    /api/datasets/                     - List all datasets")
    print("   • GET    /api/datasets/{id}/                - Get dataset detail")
    print("   • GET    /api/datasets/{id}/columns/        - Get dataset columns")
    print("   • GET    /api/datasets/{id}/records/        - Get dataset records")
    print("   • GET    /api/datasets/{id}/logs/           - Get import logs")
    print("   • POST   /api/datasets/import_csv/          - Import new CSV")
    print("   • POST   /api/datasets/{id}/generate_xml/   - Generate XML & XSD")
    print("   • POST   /api/datasets/{id}/validate_xml/   - Validate XML")
    print("   • GET    /api/records/                      - List all records")
    print("\n🌐 Browse API: http://127.0.0.1:8000/api/datasets/")


if __name__ == "__main__":
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
