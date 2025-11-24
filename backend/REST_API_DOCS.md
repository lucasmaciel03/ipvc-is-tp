# REST API Documentation

## IPVC Integration System - REST API

Base URL: `http://127.0.0.1:8000/api/`

### Authentication

Currently set to `AllowAny` for development. Should be configured with proper authentication in production.

---

## Endpoints

### 1. List All Datasets

**GET** `/api/datasets/`

Returns a paginated list of all datasets in the system.

**Response:**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "name": "retail",
      "description": "Retail Supply Chain Sales Dataset",
      "total_rows": 9994,
      "total_columns": 23,
      "status": "completed",
      "created_at": "2025-11-24T18:53:41.248994Z",
      "updated_at": "2025-11-24T19:07:26.828289Z"
    }
  ]
}
```

---

### 2. Get Dataset Detail

**GET** `/api/datasets/{id}/`

Returns detailed information about a specific dataset including all columns.

**Response:**

```json
{
  "id": 1,
  "name": "agriculture",
  "description": "Agriculture dataset from Kaggle",
  "source_file": "/data/AgricultureData.csv",
  "structure": { ... },
  "total_rows": 8893,
  "total_columns": 10,
  "status": "completed",
  "created_at": "2025-11-24T18:53:26.237653Z",
  "updated_at": "2025-11-24T19:05:56.955789Z",
  "imported_at": "2025-11-24T18:53:26.237653Z",
  "xml_file_path": "/xml_output/agriculture.xml",
  "xml_schema_path": "/schemas/agriculture.xsd",
  "columns": [
    {
      "id": 1,
      "name": "State_Name",
      "data_type": "string",
      "nullable": false,
      "unique": false,
      "primary_key": false,
      "null_count": 0,
      "unique_count": 36,
      "position": 0,
      "sample_values": ["Andaman and Nicobar Islands", "Andhra Pradesh", ...]
    }
  ]
}
```

---

### 3. Get Dataset Columns

**GET** `/api/datasets/{id}/columns/`

Returns all columns for a specific dataset.

**Response:**

```json
[
  {
    "id": 1,
    "name": "State_Name",
    "data_type": "string",
    "nullable": false,
    "unique": false,
    "primary_key": false,
    "null_count": 0,
    "unique_count": 36,
    "position": 0,
    "sample_values": ["Andaman and Nicobar Islands", ...]
  }
]
```

---

### 4. Get Dataset Records

**GET** `/api/datasets/{id}/records/`

Returns data records for a dataset with pagination.

**Query Parameters:**

- `limit` (optional): Maximum number of records to return (default: 100)
- `offset` (optional): Number of records to skip (default: 0)

**Response:**

```json
{
  "dataset": "agriculture",
  "total_rows": 8893,
  "offset": 0,
  "limit": 5,
  "count": 5,
  "records": [
    {
      "State_Name": "Andaman and Nicobar Islands",
      "District_Name": "NICOBARS",
      "Crop_Year": "2000",
      "Season": "Kharif",
      "Crop": "Arecanut",
      "Area": "1254.0",
      "Production": "2000.0"
    }
  ]
}
```

---

### 5. Get Import Logs

**GET** `/api/datasets/{id}/logs/`

Returns import and processing logs for a dataset.

**Response:**

```json
[
  {
    "id": 123,
    "dataset": 1,
    "level": "INFO",
    "message": "CSV import completed successfully",
    "details": { "rows_imported": 8893 },
    "timestamp": "2025-11-24T18:53:26.237653Z"
  }
]
```

---

### 6. Import CSV File

**POST** `/api/datasets/import_csv/`

Import a new CSV file and create a dataset.

**Content-Type:** `multipart/form-data`

**Form Parameters:**

- `file` (required): CSV file to import
- `name` (optional): Dataset name (defaults to filename)
- `description` (optional): Dataset description

**Example using curl:**

```bash
curl -X POST http://127.0.0.1:8000/api/datasets/import_csv/ \
  -F "file=@/path/to/data.csv" \
  -F "name=my_dataset" \
  -F "description=My awesome dataset"
```

**Response:**

```json
{
  "message": "CSV imported successfully",
  "dataset": {
    "id": 3,
    "name": "my_dataset",
    "description": "My awesome dataset",
    "total_rows": 1000,
    "total_columns": 15,
    "status": "completed",
    ...
  }
}
```

---

### 7. Generate XML and XSD

**POST** `/api/datasets/{id}/generate_xml/`

Generate XML and optionally XSD schema for a dataset.

**Request Body:**

```json
{
  "limit": 100,
  "generate_xsd": true,
  "validate": true
}
```

**Parameters:**

- `limit` (optional): Limit number of records to export
- `generate_xsd` (optional): Generate XSD schema (default: true)
- `validate` (optional): Validate XML against XSD (default: true)

**Response:**

```json
{
  "dataset": "agriculture",
  "xsd_generated": true,
  "xsd_path": "/schemas/agriculture.xsd",
  "xml_generated": true,
  "xml_path": "/xml_output/agriculture.xml",
  "validation_passed": true,
  "validation_errors": []
}
```

---

### 8. Validate XML

**POST** `/api/datasets/{id}/validate_xml/`

Validate existing XML against its XSD schema.

**Response:**

```json
{
  "dataset": "agriculture",
  "is_valid": true,
  "errors": []
}
```

---

### 9. List All Records

**GET** `/api/records/`

List all data records across all datasets with pagination.

**Query Parameters:**

- `dataset` (optional): Filter by dataset ID
- `page` (optional): Page number for pagination

**Response:**

```json
{
  "count": 18887,
  "next": "http://127.0.0.1:8000/api/records/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "dataset": 1,
      "data": { ... },
      "row_number": 1,
      "created_at": "2025-11-24T18:53:26.237653Z"
    }
  ]
}
```

---

## Testing the API

### Using curl

```bash
# List all datasets
curl http://127.0.0.1:8000/api/datasets/

# Get dataset detail
curl http://127.0.0.1:8000/api/datasets/1/

# Get dataset records
curl http://127.0.0.1:8000/api/datasets/1/records/?limit=10

# Generate XML
curl -X POST http://127.0.0.1:8000/api/datasets/1/generate_xml/ \
  -H "Content-Type: application/json" \
  -d '{"limit": 50, "generate_xsd": true, "validate": true}'

# Import CSV
curl -X POST http://127.0.0.1:8000/api/datasets/import_csv/ \
  -F "file=@/path/to/data.csv" \
  -F "name=test_dataset"
```

### Using Python requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# List datasets
response = requests.get(f"{BASE_URL}/datasets/")
print(response.json())

# Get dataset detail
response = requests.get(f"{BASE_URL}/datasets/1/")
print(response.json())

# Generate XML
response = requests.post(
    f"{BASE_URL}/datasets/1/generate_xml/",
    json={"limit": 100, "validate": True}
)
print(response.json())

# Import CSV
with open("/path/to/data.csv", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/datasets/import_csv/",
        files={"file": f},
        data={"name": "my_dataset"}
    )
print(response.json())
```

### Browsable API

Django REST Framework provides a browsable web interface for the API:

- Main API: http://127.0.0.1:8000/api/
- Datasets: http://127.0.0.1:8000/api/datasets/
- Records: http://127.0.0.1:8000/api/records/

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "details": { ... }
}
```

**Common HTTP Status Codes:**

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request creating a resource
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Pagination uses `page` parameter (e.g., `?page=2`)
- Default page size is 50 records
- Authentication is currently disabled for development
- File uploads must use `multipart/form-data` content type
