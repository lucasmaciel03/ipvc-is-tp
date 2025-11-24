# Sistema de Integração e Interoperabilidade de Dados

## IPVC - Instituto Politécnico de Viana do Castelo

![Status](https://img.shields.io/badge/status-completed-success)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Django](https://img.shields.io/badge/django-4.2-green)
![APIs](https://img.shields.io/badge/APIs-REST%20%7C%20gRPC%20%7C%20XML--RPC-orange)

### 🎯 Visão Geral

Plataforma completa de integração de dados que permite:

- ✅ Importação inteligente de arquivos CSV (qualquer estrutura)
- ✅ Armazenamento flexível em banco de dados (PostgreSQL/MySQL/SQLite)
- ✅ Geração automática de XML e XSD
- ✅ Validação de conformidade XSD
- ✅ Exposição de dados via **3 protocolos de API** (REST, gRPC, XML-RPC)
- ✅ Interface web para visualização e gerenciamento

---

## 🚀 Quick Start

### 1. Setup (2 minutos)

```bash
# Clone e instale
cd ipvc-is-tp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Inicie PostgreSQL
cd docker && docker-compose up -d && cd ..

# Configure o banco
cd backend
python manage.py migrate
python manage.py createsuperuser  # admin/admin
```

### 2. Importe Dados (1 minuto)

```bash
python manager.py import ../data/AgricultureData.csv agriculture "Agriculture dataset"
python manager.py import ../data/Retail-Supply-Chain-Sales-Dataset.csv retail "Retail dataset"
```

### 3. Gere XML (30 segundos)

```bash
python manager.py xml agriculture -l 100
python manager.py xml retail -l 50
```

### 4. Inicie Servidores (3 terminais)

```bash
# Terminal 1: Django (REST + Web)
python manage.py runserver

# Terminal 2: gRPC
python app/interfaces/grpc/server.py

# Terminal 3: XML-RPC
python app/interfaces/xmlrpc/server.py
```

### 5. Acesse 🌐

- **Web Dashboard**: http://127.0.0.1:8000/
- **REST API**: http://127.0.0.1:8000/api/
- **Admin Panel**: http://127.0.0.1:8000/admin (admin/admin)
- **gRPC**: localhost:50052
- **XML-RPC**: http://127.0.0.1:8001/RPC2

---

## 📋 Funcionalidades

### ✅ Importação CSV

- Detecção automática de delimitadores
- Inferência de tipos de dados
- Análise de estrutura
- Import em lote (1000 registros/segundo)

### ✅ XML/XSD

- Geração dinâmica de schemas XSD
- Export de dados para XML
- Validação automática contra XSD

### ✅ REST API (9 endpoints)

```bash
GET    /api/datasets/                     # Lista datasets
GET    /api/datasets/{id}/                # Detalhes
GET    /api/datasets/{id}/records/        # Dados paginados
POST   /api/datasets/import_csv/          # Importar CSV
POST   /api/datasets/{id}/generate_xml/   # Gerar XML
```

### ✅ gRPC API (6 métodos)

```protobuf
ListDatasets(page, page_size)
GetDataset(id)
GetDatasetRecords(id, limit, offset)
GenerateXML(id, limit, generate_xsd, validate)
ValidateXML(id)
StreamDatasetRecords(id, batch_size)  // Streaming
```

### ✅ XML-RPC API (7 métodos)

```python
list_datasets(page, page_size)
get_dataset(dataset_id)
get_dataset_records(id, limit, offset)
generate_xml(id, limit, generate_xsd, validate)
validate_xml(dataset_id)
```

### ✅ XPath/XQuery (6 endpoints)

```bash
GET    /api/xpath/                    # Lista exemplos
POST   /api/xpath/execute/            # Executa query XPath
POST   /api/xpath/statistics/         # Estatísticas do XML
POST   /api/xpath/aggregate/          # Agregações (sum, avg, etc)
POST   /api/xpath/group_by/           # Group by com agregação
POST   /api/xpath/query/              # Queries FLWOR-like
```

**CLI:**

```bash
python manager.py xpath agriculture "//record[1]" -f dict
python manager.py xpath retail "count(//record)" -f count
```

---

## 🧪 Testes

```bash
cd backend

# REST API
python test_rest_api.py

# gRPC
python app/interfaces/grpc/client_test.py

# XML-RPC
python app/interfaces/xmlrpc/client_test.py
```

---

## 📊 Datasets Incluídos

| Dataset     | Registros | Colunas |
| ----------- | --------- | ------- |
| Agriculture | 8,893     | 10      |
| Retail      | 9,994     | 23      |

---

## 🛠️ Tecnologias

- Django 4.2.26
- Django REST Framework
- PostgreSQL 15 (Docker)
- pandas 2.3.3
- lxml 6.0.2, xmlschema 4.2.0
- grpcio 1.59+, protobuf 4.25+

---

## 📚 Documentação

| Arquivo                                              | Descrição              |
| ---------------------------------------------------- | ---------------------- |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)             | Resumo executivo       |
| [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) | Documentação completa  |
| [QUICK_START.md](QUICK_START.md)                     | Guia rápido            |
| [REST_API_DOCS.md](backend/REST_API_DOCS.md)         | REST API reference     |
| [XPATH_GUIDE.md](docs/XPATH_GUIDE.md)                | XPath/XQuery reference |

---

## ✅ Status

**Projeto 100% Funcional!**

- ✅ CSV Import: 2 datasets importados (18,887 registros)
- ✅ XML/XSD: Arquivos gerados e validados
- ✅ REST API: 9 endpoints testados
- ✅ gRPC API: 6 métodos testados
- ✅ XML-RPC API: 7 métodos testados
- ✅ XPath/XQuery: 6 endpoints + CLI funcional
- ✅ Web Interface: Dashboard funcional
- ✅ CLI Tool: 8 comandos disponíveis

---

## 👥 Créditos

**IPVC - Instituto Politécnico de Viana do Castelo**  
Integração e Interoperabilidade de Sistemas - 2025

---

**Pronto para usar!** 🚀

```bash
cd backend && python manage.py runserver
# Acesse: http://127.0.0.1:8000/
```
