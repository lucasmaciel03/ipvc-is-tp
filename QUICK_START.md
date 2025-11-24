# IPVC Integration System - Quick Start Guide

## 🚀 Início Rápido (5 minutos)

### 1. Setup do Ambiente

```bash
# Clone e configure
cd ipvc-is-tp
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Inicie o PostgreSQL (Docker)
cd docker && docker-compose up -d && cd ..

# Configure o banco
cd backend
python manage.py migrate
python manage.py createsuperuser  # admin/admin
```

### 2. Importe Dados

```bash
# Importe os datasets de exemplo
python manager.py import ../data/AgricultureData.csv agriculture "Agriculture dataset"
python manager.py import ../data/Retail-Supply-Chain-Sales-Dataset.csv retail "Retail dataset"

# Gere XML e XSD
python manager.py xml agriculture -l 100
python manager.py xml retail -l 50
```

### 3. Inicie os Servidores

**Terminal 1 - Django (REST + Web)**:

```bash
cd backend
python manage.py runserver
```

**Terminal 2 - gRPC**:

```bash
cd backend
python app/interfaces/grpc/server.py
```

**Terminal 3 - XML-RPC**:

```bash
cd backend
python app/interfaces/xmlrpc/server.py
```

### 4. Teste as APIs

**REST API**:

```bash
cd backend
python test_rest_api.py
```

**gRPC**:

```bash
cd backend
python app/interfaces/grpc/client_test.py
```

**XML-RPC**:

```bash
cd backend
python app/interfaces/xmlrpc/client_test.py
```

---

## 🌐 URLs de Acesso

| Serviço        | URL                         | Descrição        |
| -------------- | --------------------------- | ---------------- |
| Web Dashboard  | http://127.0.0.1:8000/      | Interface visual |
| Django Admin   | http://127.0.0.1:8000/admin | Admin panel      |
| REST API       | http://127.0.0.1:8000/api/  | REST endpoints   |
| gRPC Server    | localhost:50052             | gRPC service     |
| XML-RPC Server | http://127.0.0.1:8001/RPC2  | XML-RPC service  |

**Credenciais Admin**: admin / admin

---

## 📋 Comandos Úteis

### CLI Manager

```bash
# Listar datasets
python manager.py list

# Ver detalhes
python manager.py show 1

# Analisar CSV (sem importar)
python manager.py analyze ../data/sample.csv

# Status do banco
python manager.py dbinfo

# Validar XML
python manager.py validate agriculture
```

### Django

```bash
# Criar novas migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Shell Django
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic
```

### Docker

```bash
# Iniciar PostgreSQL
cd docker && docker-compose up -d

# Parar PostgreSQL
docker-compose down

# Ver logs
docker-compose logs -f

# Resetar volume (apaga dados!)
docker-compose down -v
```

---

## 🔥 Exemplos de Uso

### REST API (curl)

```bash
# Listar datasets
curl http://127.0.0.1:8000/api/datasets/ | jq

# Obter dataset
curl http://127.0.0.1:8000/api/datasets/1/ | jq

# Registros paginados
curl "http://127.0.0.1:8000/api/datasets/1/records/?limit=5" | jq

# Gerar XML
curl -X POST http://127.0.0.1:8000/api/datasets/1/generate_xml/ \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "validate": true}' | jq

# Importar CSV
curl -X POST http://127.0.0.1:8000/api/datasets/import_csv/ \
  -F "file=@../data/sample.csv" \
  -F "name=sample_data"
```

### REST API (Python)

```python
import requests

BASE = "http://127.0.0.1:8000/api"

# Listar datasets
r = requests.get(f"{BASE}/datasets/")
print(r.json())

# Obter registros
r = requests.get(f"{BASE}/datasets/1/records/?limit=10")
print(r.json()['records'])

# Gerar XML
r = requests.post(f"{BASE}/datasets/1/generate_xml/",
    json={"limit": 50, "validate": True})
print(r.json())
```

### gRPC (Python)

```python
import grpc
from protos import dataset_service_pb2 as pb2
from protos import dataset_service_pb2_grpc as pb2_grpc

channel = grpc.insecure_channel('localhost:50052')
stub = pb2_grpc.DatasetServiceStub(channel)

# Listar datasets
req = pb2.ListDatasetsRequest(page=1, page_size=10)
resp = stub.ListDatasets(req)
for ds in resp.datasets:
    print(f"{ds.name}: {ds.total_rows} rows")

# Obter dataset
req = pb2.GetDatasetRequest(id=1)
resp = stub.GetDataset(req)
print(f"Dataset: {resp.name}")
print(f"Columns: {len(resp.columns)}")

# Stream records
req = pb2.StreamRecordsRequest(dataset_id=1, batch_size=100)
for record in stub.StreamDatasetRecords(req):
    print(f"Row {record.row_number}")
```

### XML-RPC (Python)

```python
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8001/RPC2')

# Listar datasets
result = proxy.list_datasets(1, 10)
print(f"Total: {result['total_count']}")

# Obter dataset
dataset = proxy.get_dataset(1)
print(f"Dataset: {dataset['name']}")

# Obter registros
records = proxy.get_dataset_records(1, 10, 0)
print(f"Records: {records['count']}")

# Estatísticas
stats = proxy.get_dataset_stats(1)
print(stats)
```

---

## 📦 Estrutura de Arquivos Gerados

```
ipvc-is-tp/
├── schemas/                    # XSD schemas gerados
│   ├── agriculture.xsd
│   └── retail.xsd
├── xml_output/                 # XML files gerados
│   ├── agriculture.xml
│   └── retail.xml
└── backend/
    ├── db.sqlite3              # SQLite database (se usado)
    └── xmlrpc.log              # XML-RPC server log
```

---

## 🧪 Validação Rápida

Verifique se tudo está funcionando:

```bash
# 1. Banco de dados
python manager.py dbinfo

# 2. Datasets importados
python manager.py list

# 3. REST API
curl http://127.0.0.1:8000/api/datasets/ | head -20

# 4. Web interface
open http://127.0.0.1:8000/  # Mac
# ou navegue para http://127.0.0.1:8000/

# 5. gRPC
python app/interfaces/grpc/client_test.py | head -30

# 6. XML-RPC
python app/interfaces/xmlrpc/client_test.py | head -30
```

---

## 🐛 Resolução Rápida de Problemas

### Porta em uso

```bash
# Listar processos nas portas
lsof -i :8000  # Django
lsof -i :50052 # gRPC
lsof -i :8001  # XML-RPC

# Matar processo
kill -9 <PID>
```

### Reset do banco de dados

```bash
# Apagar banco SQLite
rm backend/db.sqlite3

# Reset PostgreSQL
cd docker && docker-compose down -v && docker-compose up -d

# Recriar migrações
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### Reinstalar dependências

```bash
pip install --force-reinstall -r requirements.txt
```

---

## 📊 Métricas do Sistema

### Datasets Importados

- **Agriculture**: 8,893 registros, 10 colunas
- **Retail**: 9,994 registros, 23 colunas

### Performance

- Import: ~1000 registros/segundo
- XML Generation: ~500 registros/segundo
- REST API: <50ms por request
- gRPC: <20ms por request

### Armazenamento

- PostgreSQL: ~5MB por 10k registros
- XML files: ~2-5MB por dataset
- XSD schemas: ~5-10KB

---

## 🎯 Próximos Passos

1. **Importe seus próprios CSVs**:

   ```bash
   python manager.py import <seu_arquivo.csv> <nome> "Descrição"
   ```

2. **Customize as APIs** em `backend/app/interfaces/`

3. **Adicione validações** personalizadas em `csv_processor/`

4. **Implemente XPath queries** em `xml_tools/`

5. **Adicione autenticação** nas APIs (JWT, OAuth)

---

## 📚 Documentação Completa

Para mais detalhes, consulte:

- [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) - Documentação completa
- [REST_API_DOCS.md](backend/REST_API_DOCS.md) - REST API reference
- [dataset_service.proto](backend/app/interfaces/grpc/protos/dataset_service.proto) - gRPC schema

---

## 💡 Dicas

- Use `jq` para formatar JSON: `curl ... | jq`
- Use `httpie` para testes REST mais fáceis: `http GET localhost:8000/api/datasets/`
- Ative logs de debug em Django: `DEBUG=True` no `.env`
- Monitore PostgreSQL: `docker-compose logs -f postgres`
- Use Django shell: `python manage.py shell` para testar código

---

**Pronto para começar!** 🚀
