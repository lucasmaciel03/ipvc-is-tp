# IPVC Integration System - Complete Project Documentation

## 📋 Visão Geral

Sistema completo de integração e interoperabilidade de dados desenvolvido em Django, capaz de:

- Importar qualquer arquivo CSV com detecção automática de estrutura
- Armazenar dados em PostgreSQL/MySQL/SQLite com estrutura flexível
- Gerar XML e XSD dinamicamente a partir dos dados
- Validar XML contra XSD
- Expor dados através de 3 protocolos de API: REST, gRPC, XML-RPC
- Interface web para visualização e gerenciamento

---

## 🏗️ Arquitetura

```
ipvc-is-tp/
├── backend/
│   ├── app/
│   │   ├── core/              # Models, views, templates
│   │   ├── csv_processor/     # CSV analysis and import
│   │   ├── xml_tools/         # XML/XSD generation and validation
│   │   ├── database/          # Database utilities
│   │   └── interfaces/        # API implementations
│   │       ├── rest/          # Django REST Framework
│   │       ├── grpc/          # gRPC Server + proto definitions
│   │       └── xmlrpc/        # XML-RPC Server
│   ├── manager.py             # CLI tool
│   └── test_*.py              # API test scripts
├── data/                       # CSV datasets
├── xml_output/                # Generated XML files
├── schemas/                   # Generated XSD schemas
└── docker/                    # Docker configurations
```

---

## 🚀 Funcionalidades Implementadas

### ✅ 1. Importação de CSV

- **Detecção automática** de delimitadores (`,`, `;`, `\t`, `|`)
- **Inferência de tipos** (string, integer, float, boolean, date, datetime)
- **Análise de estrutura** (nullable, unique, primary key)
- **Importação em lote** (batch_size=1000 registros)
- **Validação** de integridade de dados

### ✅ 2. Armazenamento Flexível

- **Modelo dinâmico** usando `JSONField` para qualquer CSV
- **4 modelos principais**:
  - `Dataset`: Metadados do conjunto de dados
  - `DatasetColumn`: Definição de colunas
  - `DataRecord`: Dados JSON dos registros
  - `ImportLog`: Logs de importação
- **Suporte a 3 bancos**: PostgreSQL, MySQL, SQLite

### ✅ 3. Geração XML/XSD

- **XSD Generator**: Cria esquemas XSD com:
  - Mapeamento de tipos (string→xs:string, date→xs:date, etc.)
  - Normalização de nomes de elementos XML
  - Suporte a campos nullable (minOccurs="0")
- **XML Generator**: Exporta dados para XML com:
  - Valores null usando `xsi:nil="true"`
  - Limite configurável de registros
  - Encoding UTF-8
- **XML Validator**: Valida XML contra XSD usando `xmlschema`

### ✅ 4. REST API (Django REST Framework)

**Base URL**: `http://127.0.0.1:8000/api/`

**Endpoints**:

- `GET /datasets/` - Lista todos os datasets
- `GET /datasets/{id}/` - Detalhes de um dataset
- `GET /datasets/{id}/columns/` - Colunas de um dataset
- `GET /datasets/{id}/records/?limit=100&offset=0` - Registros paginados
- `GET /datasets/{id}/logs/` - Logs de importação
- `POST /datasets/import_csv/` - Importar novo CSV
- `POST /datasets/{id}/generate_xml/` - Gerar XML e XSD
- `POST /datasets/{id}/validate_xml/` - Validar XML
- `GET /records/?dataset={id}` - Todos os registros

**Recursos**:

- Paginação automática (50 itens/página)
- Serializers para JSON
- Browsable API para teste manual
- Upload de arquivos multipart

### ✅ 5. gRPC API

**Servidor**: `localhost:50052`

**Arquivo Proto**: `dataset_service.proto`

**Métodos**:

- `ListDatasets(page, page_size)` - Lista datasets
- `GetDataset(id)` - Obtém dataset completo
- `GetDatasetRecords(id, limit, offset)` - Obtém registros
- `GenerateXML(id, limit, generate_xsd, validate)` - Gera XML
- `ValidateXML(id)` - Valida XML
- `StreamDatasetRecords(id, batch_size)` - Stream de registros

**Recursos**:

- Protocol Buffers para serialização eficiente
- Streaming bidirecional
- Type safety
- Suporte a múltiplas linguagens

### ✅ 6. XML-RPC API

**Servidor**: `http://127.0.0.1:8001/RPC2`

**Métodos**:

- `list_datasets(page, page_size)` - Lista datasets
- `get_dataset(dataset_id)` - Obtém dataset
- `get_dataset_records(id, limit, offset)` - Obtém registros
- `get_dataset_columns(dataset_id)` - Obtém colunas
- `get_dataset_stats(dataset_id)` - Estatísticas do dataset
- `generate_xml(id, limit, generate_xsd, validate)` - Gera XML
- `validate_xml(dataset_id)` - Valida XML

**Recursos**:

- Compatibilidade com sistemas legados
- Introspection (system.listMethods)
- Simplicidade de implementação
- Suporte XML nativo

### ✅ 7. Interface Web

**URL**: `http://127.0.0.1:8000/`

**Páginas**:

- **Dashboard**: Lista de todos os datasets com estatísticas
- **Detalhe**: Visualização completa de um dataset
  - Informações gerais
  - Lista de colunas com tipos
  - Amostra de dados
  - Status de XML/XSD
- **Admin**: Interface Django Admin em `/admin`

**Recursos**:

- Design responsivo
- Cards informativos
- Tabelas interativas
- Status visual (badges)

### ✅ 8. CLI Manager

**Comando**: `python manager.py <command>`

**Comandos disponíveis**:

```bash
# Importar CSV
python manager.py import <file> <name> [description]

# Listar datasets
python manager.py list

# Mostrar dataset específico
python manager.py show <dataset_id>

# Analisar CSV sem importar
python manager.py analyze <file>

# Informações do banco de dados
python manager.py dbinfo

# Gerar XML e XSD
python manager.py xml <dataset_id> [-l LIMIT]

# Validar XML
python manager.py validate <dataset_id>
```

---

## 🔧 Tecnologias Utilizadas

### Backend

- **Django 4.2.26**: Framework web
- **Django REST Framework 3.14+**: REST API
- **PostgreSQL 15**: Banco de dados principal
- **pandas 2.3.3**: Análise e processamento de CSV
- **lxml 6.0.2**: Processamento XML
- **xmlschema 4.2.0**: Validação XSD
- **grpcio 1.59+**: gRPC server/client
- **protobuf 4.25+**: Protocol Buffers

### DevOps

- **Docker**: Containerização do PostgreSQL
- **Docker Compose**: Orquestração
- **python-dotenv**: Gestão de variáveis de ambiente

---

## 📦 Instalação e Configuração

### 1. Clonar repositório

```bash
git clone <repo_url>
cd ipvc-is-tp
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar banco de dados

#### Opção A: PostgreSQL (Docker)

```bash
cd docker
docker-compose up -d
```

Criar arquivo `.env` na raiz:

```env
DB_ENGINE=postgresql
DB_NAME=ipvc_db
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=localhost
DB_PORT=5433
```

#### Opção B: SQLite (sem Docker)

```env
DB_ENGINE=sqlite
```

### 5. Aplicar migrações

```bash
cd backend
python manage.py migrate
```

### 6. Criar superusuário

```bash
python manage.py createsuperuser
# Username: admin
# Password: admin
```

### 7. Importar dados de exemplo

```bash
python manager.py import ../data/AgricultureData.csv agriculture "Agriculture dataset from Kaggle"
python manager.py import ../data/Retail-Supply-Chain-Sales-Dataset.csv retail "Retail Supply Chain Sales Dataset"
```

---

## 🚦 Como Executar

### 1. Servidor Django (REST API + Web)

```bash
cd backend
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

### 2. Servidor gRPC

```bash
cd backend
python app/interfaces/grpc/server.py
```

Porta: 50052

### 3. Servidor XML-RPC

```bash
cd backend
python app/interfaces/xmlrpc/server.py
```

URL: http://127.0.0.1:8001/RPC2

### 4. Executar todos os servidores

```bash
# Terminal 1: Django
cd backend && python manage.py runserver

# Terminal 2: gRPC
cd backend && python app/interfaces/grpc/server.py

# Terminal 3: XML-RPC
cd backend && python app/interfaces/xmlrpc/server.py
```

---

## 🧪 Testes

### REST API

```bash
cd backend
python test_rest_api.py
```

### gRPC

```bash
cd backend
python app/interfaces/grpc/client_test.py
```

### XML-RPC

```bash
cd backend
python app/interfaces/xmlrpc/client_test.py
```

### Exemplos de uso

#### REST API (curl)

```bash
# Listar datasets
curl http://127.0.0.1:8000/api/datasets/

# Obter registros
curl "http://127.0.0.1:8000/api/datasets/1/records/?limit=10"

# Gerar XML
curl -X POST http://127.0.0.1:8000/api/datasets/1/generate_xml/ \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "validate": true}'
```

#### gRPC (Python)

```python
import grpc
from protos import dataset_service_pb2, dataset_service_pb2_grpc

channel = grpc.insecure_channel('localhost:50052')
stub = dataset_service_pb2_grpc.DatasetServiceStub(channel)

request = dataset_service_pb2.ListDatasetsRequest(page=1, page_size=10)
response = stub.ListDatasets(request)
print(response.datasets)
```

#### XML-RPC (Python)

```python
import xmlrpc.client

proxy = xmlrpc.client.ServerProxy('http://127.0.0.1:8001/RPC2')
datasets = proxy.list_datasets(1, 10)
print(datasets)
```

---

## 📊 Datasets de Exemplo

### 1. Agriculture Dataset

- **Origem**: Kaggle
- **Registros**: 8,893
- **Colunas**: 10
- **Tipos**: string, integer, float, date
- **Campos**: State_Name, District_Name, Crop_Year, Season, Crop, Area, Production

### 2. Retail Supply Chain

- **Origem**: Kaggle
- **Registros**: 9,994
- **Colunas**: 23
- **Tipos**: string, integer, float, date
- **Campos**: Order ID, Product Name, Sales, Profit, Region, Category, etc.

---

## 🔍 Detalhes Técnicos

### Modelo de Dados

```python
# Dataset: Metadados do conjunto de dados
{
    "id": 1,
    "name": "agriculture",
    "structure": {
        "delimiter": ",",
        "encoding": "utf-8",
        "columns": [...]
    },
    "total_rows": 8893,
    "total_columns": 10,
    "status": "completed"
}

# DatasetColumn: Definição de coluna
{
    "name": "State_Name",
    "data_type": "string",
    "nullable": false,
    "unique": false,
    "null_count": 0,
    "unique_count": 36,
    "sample_values": ["Kerala", "Tamil Nadu", ...]
}

# DataRecord: Registro de dados
{
    "row_number": 1,
    "data": {
        "State_Name": "Kerala",
        "Crop": "Rice",
        "Area": "1000.0"
    }
}
```

### Workflow de Processamento

1. **Upload CSV** → `CSVAnalyzer` detecta estrutura
2. **Análise** → `CSVAnalyzer` infere tipos e metadados
3. **Importação** → `CSVImporter` salva em lote no banco
4. **Geração XSD** → `XSDGenerator` cria esquema baseado nos tipos
5. **Geração XML** → `XMLGenerator` exporta dados
6. **Validação** → `XMLValidator` verifica conformidade

---

## 📝 Configurações Avançadas

### Personalizar Porta do Django

```bash
python manage.py runserver 0.0.0.0:8080
```

### Usar MySQL em vez de PostgreSQL

```env
DB_ENGINE=mysql
DB_NAME=ipvc_db
DB_USER=root
DB_PASSWORD=rootpass
DB_HOST=localhost
DB_PORT=3306
```

### Aumentar Limite de Registros XML

```python
xml_service.generate_xml(limit=10000)  # Gera XML com 10k registros
```

### Personalizar Batch Size de Importação

```python
# csv_processor/processor.py
CSVImporter.import_csv(file_path, batch_size=5000)
```

---

## 🐛 Troubleshooting

### Erro: Port already in use

```bash
# Encontrar processo usando a porta
lsof -i :8000
# Matar processo
kill -9 <PID>
```

### Erro: No module named 'app'

```bash
# Certifique-se de estar no diretório correto
cd backend
python manage.py ...
```

### Erro: Connection refused (gRPC/XML-RPC)

```bash
# Verificar se servidor está rodando
ps aux | grep "server.py"
# Iniciar servidor novamente
python app/interfaces/grpc/server.py
```

### Erro: XML validation failed

- **Causa**: Formato de data não ISO (ex: 11/08/2016)
- **Solução**: Sistema detecta automaticamente, mas não converte
- **Recomendação**: Limpar dados CSV antes da importação

---

## 📚 Referências e Links

### Documentação Completa

- [REST API Documentation](REST_API_DOCS.md)
- [gRPC Proto Definition](app/interfaces/grpc/protos/dataset_service.proto)

### Endpoints

- Web Dashboard: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin
- REST API: http://127.0.0.1:8000/api/
- gRPC Server: localhost:50052
- XML-RPC Server: http://127.0.0.1:8001/RPC2

### Tecnologias

- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- gRPC: https://grpc.io/docs/languages/python/
- XML-RPC: https://docs.python.org/3/library/xmlrpc.html

---

## 👥 Créditos

**Desenvolvido para**: IPVC - Instituto Politécnico de Viana do Castelo  
**Disciplina**: Integração e Interoperabilidade de Sistemas  
**Ano**: 2025

---

## 📄 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.
