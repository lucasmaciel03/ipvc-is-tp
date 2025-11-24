"""
gRPC Client Example for IPVC Integration System
"""

import grpc
import json
from protos import dataset_service_pb2
from protos import dataset_service_pb2_grpc


def run_tests():
    """Run gRPC client tests"""
    
    # Connect to gRPC server
    channel = grpc.insecure_channel('localhost:50052')
    stub = dataset_service_pb2_grpc.DatasetServiceStub(channel)
    
    print("="*80)
    print("🚀 IPVC Integration System - gRPC Client Tests")
    print("="*80)
    
    # Test 1: List Datasets
    print("\n\n🔍 TEST 1: List Datasets")
    print("-"*80)
    try:
        request = dataset_service_pb2.ListDatasetsRequest(page=1, page_size=10)
        response = stub.ListDatasets(request)
        
        print(f"Total datasets: {response.total_count}")
        print(f"Page: {response.page}, Page size: {response.page_size}")
        print(f"\nDatasets:")
        for dataset in response.datasets:
            print(f"  • ID: {dataset.id}")
            print(f"    Name: {dataset.name}")
            print(f"    Rows: {dataset.total_rows}, Columns: {dataset.total_columns}")
            print(f"    Status: {dataset.status}")
            print()
        
        # Save first dataset ID for other tests
        dataset_id = response.datasets[0].id if response.datasets else None
        
    except grpc.RpcError as e:
        print(f"❌ Error: {e.code()}: {e.details()}")
        return
    
    if not dataset_id:
        print("❌ No datasets found. Please import CSV files first.")
        return
    
    # Test 2: Get Dataset Detail
    print(f"\n\n🔍 TEST 2: Get Dataset Detail (ID={dataset_id})")
    print("-"*80)
    try:
        request = dataset_service_pb2.GetDatasetRequest(id=dataset_id)
        response = stub.GetDataset(request)
        
        print(f"Dataset: {response.name}")
        print(f"Description: {response.description}")
        print(f"Total rows: {response.total_rows}")
        print(f"Total columns: {response.total_columns}")
        print(f"Status: {response.status}")
        print(f"Created: {response.created_at}")
        print(f"XML path: {response.xml_file_path}")
        print(f"XSD path: {response.xml_schema_path}")
        print(f"\nColumns ({len(response.columns)}):")
        for col in response.columns[:5]:  # Show first 5
            print(f"  • {col.name} ({col.data_type})")
            print(f"    Nullable: {col.nullable}, Unique: {col.unique}")
        
    except grpc.RpcError as e:
        print(f"❌ Error: {e.code()}: {e.details()}")
    
    # Test 3: Get Dataset Records
    print(f"\n\n🔍 TEST 3: Get Dataset Records (ID={dataset_id}, limit=5)")
    print("-"*80)
    try:
        request = dataset_service_pb2.GetDatasetRecordsRequest(
            dataset_id=dataset_id,
            limit=5,
            offset=0
        )
        response = stub.GetDatasetRecords(request)
        
        print(f"Total rows: {response.total_rows}")
        print(f"Offset: {response.offset}, Limit: {response.limit}")
        print(f"Retrieved: {len(response.records)} records")
        print(f"\nRecords:")
        for record in response.records[:3]:  # Show first 3
            data = json.loads(record.data_json)
            print(f"  • Row {record.row_number}:")
            # Show first 3 fields
            for i, (key, value) in enumerate(list(data.items())[:3]):
                print(f"    {key}: {value}")
            print()
        
    except grpc.RpcError as e:
        print(f"❌ Error: {e.code()}: {e.details()}")
    
    # Test 4: Generate XML
    print(f"\n\n🔍 TEST 4: Generate XML (ID={dataset_id}, limit=10)")
    print("-"*80)
    try:
        request = dataset_service_pb2.GenerateXMLRequest(
            dataset_id=dataset_id,
            limit=10,
            generate_xsd=True,
            validate=True
        )
        response = stub.GenerateXML(request)
        
        print(f"Dataset: {response.dataset_name}")
        print(f"XSD Generated: {response.xsd_generated}")
        if response.xsd_generated:
            print(f"  Path: {response.xsd_path}")
        print(f"XML Generated: {response.xml_generated}")
        if response.xml_generated:
            print(f"  Path: {response.xml_path}")
        print(f"Validation Passed: {response.validation_passed}")
        if response.validation_errors:
            print(f"Validation Errors:")
            for error in response.validation_errors:
                print(f"  • {error}")
        
    except grpc.RpcError as e:
        print(f"❌ Error: {e.code()}: {e.details()}")
    
    # Test 5: Validate XML
    print(f"\n\n🔍 TEST 5: Validate XML (ID={dataset_id})")
    print("-"*80)
    try:
        request = dataset_service_pb2.ValidateXMLRequest(dataset_id=dataset_id)
        response = stub.ValidateXML(request)
        
        print(f"Dataset: {response.dataset_name}")
        print(f"Is Valid: {response.is_valid}")
        if response.errors:
            print(f"Errors:")
            for error in response.errors:
                print(f"  • {error}")
        
    except grpc.RpcError as e:
        print(f"❌ Error: {e.code()}: {e.details()}")
    
    # Test 6: Stream Records
    print(f"\n\n🔍 TEST 6: Stream Dataset Records (ID={dataset_id}, batch_size=10)")
    print("-"*80)
    try:
        request = dataset_service_pb2.StreamRecordsRequest(
            dataset_id=dataset_id,
            batch_size=10
        )
        
        record_count = 0
        for record in stub.StreamDatasetRecords(request):
            record_count += 1
            if record_count <= 3:  # Show first 3
                data = json.loads(record.data_json)
                print(f"  • Row {record.row_number}: {list(data.keys())[:3]}...")
            elif record_count == 10:
                break
        
        print(f"\nStreamed {record_count} records")
        
    except grpc.RpcError as e:
        print(f"❌ Error: {e.code()}: {e.details()}")
    
    print("\n\n" + "="*80)
    print("✅ All gRPC tests completed!")
    print("="*80)
    print("\n📝 gRPC Service Methods:")
    print("   • ListDatasets       - List all datasets with pagination")
    print("   • GetDataset         - Get detailed dataset information")
    print("   • GetDatasetRecords  - Get dataset records with pagination")
    print("   • GenerateXML        - Generate XML and XSD for dataset")
    print("   • ValidateXML        - Validate XML against XSD")
    print("   • StreamDatasetRecords - Stream records in batches")
    print("\n🌐 gRPC Server: localhost:50051")


if __name__ == '__main__':
    try:
        run_tests()
    except grpc.RpcError as e:
        print(f"\n❌ ERROR: Could not connect to gRPC server.")
        print(f"   Error: {e.code()}: {e.details()}")
        print("   Make sure gRPC server is running:")
        print("   python app/interfaces/grpc/server.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
