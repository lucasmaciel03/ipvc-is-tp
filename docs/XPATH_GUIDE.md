# XPath/XQuery Query Guide

Complete guide for querying XML data using XPath expressions.

## Table of Contents

1. [Overview](#overview)
2. [REST API Endpoints](#rest-api-endpoints)
3. [CLI Usage](#cli-usage)
4. [XPath Examples](#xpath-examples)
5. [Query Builder](#query-builder)
6. [Advanced Queries](#advanced-queries)

---

## Overview

The IPVC Integration System provides powerful XPath/XQuery capabilities for querying XML data generated from imported datasets. The implementation uses **lxml** library for high-performance XML processing.

### Key Features

- ✅ Standard XPath 1.0 expressions
- ✅ XQuery-like FLWOR queries (For-Let-Where-Order-Return)
- ✅ Aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- ✅ Group by operations
- ✅ Pre-defined query examples
- ✅ Programmatic query builder
- ✅ Multiple output formats (dict, text, count)
- ✅ REST API and CLI interfaces

---

## REST API Endpoints

### 1. List Available Examples

Get pre-defined query examples and builder methods.

**Request:**

```bash
curl -X GET http://127.0.0.1:8000/api/xpath/
```

**Response:**

```json
{
  "examples": {
    "all_records": "//record",
    "first_record": "//record[1]",
    "last_record": "//record[last()]",
    "count_records": "count(//record)",
    "distinct_values": "//*/name()[not(.=preceding::*/name())]",
    "nested_query": "//record[position() mod 2 = 0]",
    "field_values": "//field_name",
    "conditional": "//record[field > value]",
    "range": "//record[position() >= start and position() <= end]",
    "text_search": "//record[contains(field, 'text')]"
  },
  "builders": [
    "select_all_records()",
    "select_record_by_index(index)",
    "select_field_values(field_name)",
    "count_records()",
    "select_distinct_values(field_name)",
    "select_records_where(field, value)"
  ]
}
```

### 2. Execute XPath Query

Execute custom XPath expressions on dataset XML.

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/api/xpath/execute/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "xpath": "//record[position() <= 5]",
    "format": "dict"
  }'
```

**Parameters:**

- `dataset_id` (integer, required): Dataset ID with generated XML
- `xpath` (string, required): XPath expression
- `format` (string, optional): Output format
  - `dict` - Structured dictionaries (default)
  - `text` - Text values only
  - `count` - Count of matching elements

**Response (dict format):**

```json
{
  "dataset": "agriculture",
  "query": "//record[position() <= 5]",
  "count": 5,
  "results": [
    {
      "_tag": "record",
      "State_Name": "Andaman and Nicobar Islands",
      "District_Name": "NICOBARS",
      "Crop_Year": "2000",
      "Season": "Kharif",
      "Crop": "Arecanut",
      "Area": "1254.0",
      "Production": "2000.0"
    }
    // ... more records
  ]
}
```

### 3. Get XML Statistics

Get comprehensive statistics about the XML structure.

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/api/xpath/statistics/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1
  }'
```

**Response:**

```json
{
  "dataset": "agriculture",
  "statistics": {
    "root_element": "agriculture",
    "total_records": 100,
    "total_elements": 841,
    "depth": 2
  }
}
```

### 4. Aggregate Functions

Perform aggregate operations on numeric fields.

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/api/xpath/aggregate/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "field": "Area",
    "operation": "sum"
  }'
```

**Parameters:**

- `dataset_id` (integer, required): Dataset ID
- `field` (string, required): Field name to aggregate
- `operation` (string, required): Aggregation operation
  - `sum` - Sum of all values
  - `avg` - Average value
  - `min` - Minimum value
  - `max` - Maximum value
  - `count` - Count of non-null values

**Response:**

```json
{
  "dataset": "agriculture",
  "field": "Area",
  "operation": "sum",
  "result": 1234567.5
}
```

### 5. Group By Operations

Group records by a field with optional aggregation.

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/api/xpath/group_by/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "group_field": "Season",
    "aggregate_field": "Production",
    "operation": "sum"
  }'
```

**Parameters:**

- `dataset_id` (integer, required): Dataset ID
- `group_field` (string, required): Field to group by
- `aggregate_field` (string, optional): Field to aggregate
- `operation` (string, optional): Aggregation operation (sum, avg, min, max, count)

**Response:**

```json
{
  "dataset": "agriculture",
  "grouped_by": "Season",
  "results": {
    "Kharif": {
      "count": 45,
      "Production_sum": 567890.0
    },
    "Rabi": {
      "count": 35,
      "Production_sum": 432100.0
    },
    "Whole Year": {
      "count": 20,
      "Production_sum": 234560.0
    }
  }
}
```

### 6. FLWOR-like Queries

Execute XQuery-style queries with For-Where-Return clauses.

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/api/xpath/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "for_xpath": "//record",
    "where_condition": "Area > 1000",
    "return_field": "Crop"
  }'
```

**Parameters:**

- `dataset_id` (integer, required): Dataset ID
- `for_xpath` (string, required): XPath expression for records
- `where_condition` (string, optional): Filtering condition
- `return_field` (string, optional): Specific field to return

**Response:**

```json
{
  "dataset": "agriculture",
  "query": {
    "for": "//record",
    "where": "Area > 1000",
    "return": "Crop"
  },
  "count": 67,
  "results": [
    {
      "_tag": "record",
      "State_Name": "Andaman and Nicobar Islands",
      "Crop": "Arecanut",
      "Area": "1254.0"
    }
    // ... more records
  ]
}
```

---

## CLI Usage

### Basic Syntax

```bash
python manager.py xpath <dataset_name> "<xpath_query>" [-f format]
```

### Examples

#### 1. Count Total Records

```bash
python manager.py xpath agriculture "count(//record)" -f count
```

Output:

```
============================================================
XPath Query: agriculture
============================================================
Query: count(//record)
Format: count
============================================================

Count: 100

============================================================
✓ Query executed successfully
============================================================
```

#### 2. Get First 3 Records (Dict Format)

```bash
python manager.py xpath agriculture "//record[position() <= 3]" -f dict
```

Output:

```
============================================================
XPath Query: agriculture
============================================================
Query: //record[position() <= 3]
Format: dict
============================================================

Results (3 items):

1. {
  "_tag": "record",
  "State_Name": "Andaman and Nicobar Islands",
  "District_Name": "NICOBARS",
  "Crop_Year": "2000",
  "Season": "Kharif",
  "Crop": "Arecanut",
  "Area": "1254.0",
  "Production": "2000.0"
}

2. {
  ...
}

3. {
  ...
}

============================================================
✓ Query executed successfully
============================================================
```

#### 3. Get All State Names (Text Format)

```bash
python manager.py xpath agriculture "//State_Name" -f text
```

Output:

```
Results (100 items):
  1. Andaman and Nicobar Islands
  2. Andaman and Nicobar Islands
  3. Andhra Pradesh
  4. Andhra Pradesh
  ...
```

#### 4. Filter Records by Condition

```bash
python manager.py xpath agriculture "//record[Season='Kharif']" -f count
```

#### 5. Get Last Record

```bash
python manager.py xpath agriculture "//record[last()]" -f dict
```

#### 6. Get Distinct Crop Names

```bash
python manager.py xpath agriculture "//Crop[not(.=preceding::Crop)]" -f text
```

---

## XPath Examples

### Basic Selection

#### Select All Records

```xpath
//record
```

#### Select First Record

```xpath
//record[1]
```

#### Select Last Record

```xpath
//record[last()]
```

#### Select Records 10-20

```xpath
//record[position() >= 10 and position() <= 20]
```

### Field Selection

#### Get All Values of a Field

```xpath
//State_Name
```

#### Get Unique Field Values

```xpath
//Crop[not(.=preceding::Crop)]
```

### Conditional Queries

#### Records with Specific Value

```xpath
//record[Season='Kharif']
```

#### Records with Numeric Condition

```xpath
//record[Area > 1000]
```

#### Records with Multiple Conditions

```xpath
//record[Season='Kharif' and Area > 1000]
```

#### Text Search

```xpath
//record[contains(Crop, 'Rice')]
```

### Counting and Aggregation

#### Count All Records

```xpath
count(//record)
```

#### Count Filtered Records

```xpath
count(//record[Season='Kharif'])
```

#### Count Unique Values

```xpath
count(//State_Name[not(.=preceding::State_Name)])
```

### Advanced Queries

#### Even Numbered Records

```xpath
//record[position() mod 2 = 0]
```

#### Odd Numbered Records

```xpath
//record[position() mod 2 = 1]
```

#### Records NOT Matching Condition

```xpath
//record[not(Season='Kharif')]
```

#### Records with Empty Field

```xpath
//record[not(Production) or Production='']
```

#### Multiple Field Conditions with OR

```xpath
//record[Season='Kharif' or Season='Rabi']
```

---

## Query Builder

The `XPathQueryBuilder` class provides static methods for programmatic query construction.

### Available Methods

```python
from app.xml_tools.xpath_query import XPathQueryBuilder

# Select all records
query = XPathQueryBuilder.select_all_records()
# Result: "//record"

# Select specific record by index
query = XPathQueryBuilder.select_record_by_index(5)
# Result: "//record[5]"

# Select all values of a field
query = XPathQueryBuilder.select_field_values('State_Name')
# Result: "//State_Name"

# Count records
query = XPathQueryBuilder.count_records()
# Result: "count(//record)"

# Select distinct values
query = XPathQueryBuilder.select_distinct_values('Crop')
# Result: "//Crop[not(.=preceding::Crop)]"

# Select records with condition
query = XPathQueryBuilder.select_records_where('Season', 'Kharif')
# Result: "//record[Season='Kharif']"
```

### Usage in Python

```python
from app.xml_tools.xpath_query import XPathQueryEngine, XPathQueryBuilder
from app.core.models import Dataset

# Get dataset
dataset = Dataset.objects.get(name='agriculture')

# Create engine
engine = XPathQueryEngine(dataset)

# Build and execute query
query = XPathQueryBuilder.select_records_where('Season', 'Kharif')
results = engine.query_to_dict(query)

print(f"Found {len(results)} Kharif season records")
```

---

## Advanced Queries

### XQuery Support

The `XQuerySupport` class provides FLWOR-like query capabilities.

#### Simple FLWOR Query

```python
from app.xml_tools.xpath_query import XPathQueryEngine, XQuerySupport
from app.core.models import Dataset

dataset = Dataset.objects.get(name='agriculture')
xquery = XQuerySupport(dataset)

# For each record, return specific field
results = xquery.execute_flwor_like(
    for_xpath='//record',
    return_field='Crop'
)
```

#### FLWOR with WHERE Clause

```python
# For each record WHERE condition, return field
results = xquery.execute_flwor_like(
    for_xpath='//record',
    where_condition='Area > 1000',
    return_field='State_Name'
)
```

### Aggregate Functions

```python
from app.xml_tools.xpath_query import XQuerySupport
from app.core.models import Dataset

dataset = Dataset.objects.get(name='agriculture')
xquery = XQuerySupport(dataset)

# Sum
total_area = xquery.aggregate('//Area', operation='sum')

# Average
avg_production = xquery.aggregate('//Production', operation='avg')

# Min/Max
min_area = xquery.aggregate('//Area', operation='min')
max_area = xquery.aggregate('//Area', operation='max')

# Count
record_count = xquery.aggregate('//record', operation='count')
```

### Group By Operations

```python
# Group by Season, sum Production
groups = xquery.group_by(
    group_field='Season',
    aggregate_field='Production',
    operation='sum'
)

# Result:
# {
#   'Kharif': {'count': 45, 'Production_sum': 567890.0},
#   'Rabi': {'count': 35, 'Production_sum': 432100.0},
#   ...
# }
```

---

## Performance Tips

### 1. Use Specific Paths

❌ Slow: `//*/Crop`  
✅ Fast: `//Crop`

### 2. Limit Results Early

❌ Slow: Get all, then filter in Python  
✅ Fast: `//record[position() <= 100]`

### 3. Use count() for Counting

❌ Slow: Get all results, count in Python  
✅ Fast: `count(//record)`

### 4. Cache XML Files

The system automatically caches parsed XML trees for performance.

### 5. Index on Demand

For large datasets, consider generating smaller XML files:

```bash
python manager.py xml agriculture -l 1000
```

---

## Error Handling

### Common Errors

#### 1. Dataset Has No XML

```
✗ No XML file for dataset 'agriculture'
Generate XML first: python manager.py xml agriculture -l 100
```

**Solution:** Generate XML file first.

#### 2. Invalid XPath Expression

```
✗ Query failed: Invalid expression
```

**Solution:** Check XPath syntax. Use validators or examples.

#### 3. Field Not Found

Returns empty results if field doesn't exist in the dataset.

**Solution:** Check field names with statistics endpoint or dataset schema.

---

## Examples by Use Case

### Data Exploration

```bash
# How many records?
python manager.py xpath agriculture "count(//record)" -f count

# What are the unique states?
python manager.py xpath agriculture "//State_Name[not(.=preceding::State_Name)]" -f text

# Show first 5 records
python manager.py xpath agriculture "//record[position() <= 5]" -f dict
```

### Data Analysis

```bash
# All Kharif season records
curl -X POST http://127.0.0.1:8000/api/xpath/execute/ \
  -H "Content-Type: application/json" \
  -d '{"dataset_id": 1, "xpath": "//record[Season='\'Kharif\'']", "format": "count"}'

# Total production by season
curl -X POST http://127.0.0.1:8000/api/xpath/group_by/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "group_field": "Season",
    "aggregate_field": "Production",
    "operation": "sum"
  }'

# Average area by state
curl -X POST http://127.0.0.1:8000/api/xpath/group_by/ \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "group_field": "State_Name",
    "aggregate_field": "Area",
    "operation": "avg"
  }'
```

### Data Filtering

```bash
# Large area farms
python manager.py xpath agriculture "//record[Area > 5000]" -f count

# Specific crop in specific state
python manager.py xpath agriculture "//record[State_Name='Punjab' and Crop='Wheat']" -f dict

# Production in range
python manager.py xpath agriculture "//record[Production >= 1000 and Production <= 5000]" -f count
```

---

## Integration Examples

### Python Script

```python
#!/usr/bin/env python
import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api/xpath/'

def query_dataset(dataset_id, xpath, format='dict'):
    response = requests.post(
        f'{BASE_URL}execute/',
        json={
            'dataset_id': dataset_id,
            'xpath': xpath,
            'format': format
        }
    )
    return response.json()

# Get first 10 records
results = query_dataset(1, '//record[position() <= 10]')
print(f"Found {results['count']} records")

# Count by condition
results = query_dataset(
    1,
    "//record[Season='Kharif']",
    format='count'
)
print(f"Kharif records: {results['results']}")
```

### JavaScript/Node.js

```javascript
const axios = require("axios");

const BASE_URL = "http://127.0.0.1:8000/api/xpath/";

async function queryDataset(datasetId, xpath, format = "dict") {
  const response = await axios.post(`${BASE_URL}execute/`, {
    dataset_id: datasetId,
    xpath: xpath,
    format: format,
  });
  return response.data;
}

// Usage
(async () => {
  const results = await queryDataset(1, "//record[position() <= 10]");
  console.log(`Found ${results.count} records`);
})();
```

---

## References

- [XPath 1.0 Specification](https://www.w3.org/TR/xpath-10/)
- [lxml XPath Documentation](https://lxml.de/xpathxslt.html)
- [XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)
- [XQuery Primer](https://www.w3.org/TR/xquery-30/)

---

**Last Updated:** January 2025  
**Version:** 1.0.0
