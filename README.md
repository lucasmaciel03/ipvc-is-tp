# IPVC Integration System 🚀

Sistema de Integração e Interoperabilidade com Informação Alfanumérica via XML, gRPC, REST API e XML-RPC.

## 📋 Características

- ✅ **Importação Dinâmica de CSV**: Suporta qualquer estrutura de CSV automaticamente
- ✅ **Conversão CSV → XML** com schema de validação
- ✅ **Base de Dados Flexível**: PostgreSQL ou MySQL
- ✅ **APIs Múltiplas**: REST, gRPC, XML-RPC
- ✅ **Processamento XQuery/XPath**
- ✅ **Django Admin Interface** completa
- ✅ **Docker & Docker Compose** ready
- ✅ **Arquitetura Escalável e Modular**

## 🏗️ Arquitetura

```
backend/
├── app/
│   ├── core/              # Modelos principais (Dataset, DataRecord)
│   ├── csv_processor/     # Processamento inteligente de CSV
│   ├── database/          # Gerenciamento de BD
│   ├── xml_tools/         # Conversão XML e XSD
│   └── interfaces/
│       ├── rest/          # API REST (FastAPI/Django)
│       ├── grpc/          # gRPC Server
│       └── xmlrpc/        # XML-RPC Server
├── manage.py              # Django management
└── manager.py             # CLI personalizado
```

## 🚀 Setup Rápido

### 1. Instalar Dependências

```bash
# Criar ambiente virtual (se ainda não tens)
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Instalar pacotes
pip install -r requirements.txt
```

### 2. Configurar Base de Dados

#### Opção A: PostgreSQL com Docker (Recomendado)

```bash
# Iniciar PostgreSQL
docker-compose up -d postgres
```

#### Opção B: SQLite (Desenvolvimento)

```bash
# Nenhuma configuração necessária - Django usará SQLite automaticamente
```

### 3. Executar Migrações

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Importar Datasets

```bash
# Usando o manager CLI
python manager.py import ../data/AgricultureData.csv -n agriculture -d "Agriculture dataset"
python manager.py import ../data/Retail-Supply-Chain-Sales-Dataset.csv -n retail -d "Retail supply chain"

# Listar datasets importados
python manager.py list

# Ver detalhes de um dataset
python manager.py show agriculture
```

## 🐳 Docker Setup

### Iniciar todos os serviços

```bash
# PostgreSQL + Django
docker-compose up -d

# Todos os serviços (inclui gRPC)
docker-compose --profile full up -d

# Com pgAdmin
docker-compose --profile tools up -d
```

### Executar migrações no Docker

```bash
docker-compose exec django python backend/manage.py migrate
docker-compose exec django python backend/manage.py createsuperuser
```

## 📊 Uso do Sistema

### CLI Manager

```bash
# Analisar CSV sem importar
python manager.py analyze ../data/AgricultureData.csv

# Importar CSV
python manager.py import <file> -n <name> -d <description>

# Listar datasets
python manager.py list

# Ver dataset específico
python manager.py show <name> -l 20

# Info da base de dados
python manager.py dbinfo
```

### Django Admin

```bash
# Iniciar servidor
python manage.py runserver

# Aceder: http://localhost:8000/admin
```

## 🗄️ Estrutura de Dados

### Modelo Flexível

O sistema usa um modelo JSON-based que se adapta a qualquer estrutura de CSV:

```python
Dataset
├── name: "agriculture"
├── structure: {"columns": [...]}
├── total_rows: 8895
└── records: [
    {
        "data": {
            "product_id": "b12c721e...",
            "product_name": "Lamb",
            "price_per_kg": 14.10,
            ...
        }
    }
]
```

### Modelos Django

- **Dataset**: Metadados do dataset
- **DatasetColumn**: Informação de cada coluna (tipo, nullable, unique, etc.)
- **DataRecord**: Registros armazenados como JSON (ultra flexível)
- **ImportLog**: Logs de importação

## 🔧 Próximos Passos

- [ ] Implementar conversão CSV → XML com XSD
- [ ] Implementar REST API completa
- [ ] Implementar gRPC server
- [ ] Implementar XML-RPC server
- [ ] Adicionar suporte a XQuery/XPath
- [ ] Testes unitários

## 📝 Exemplo de Uso Completo

```bash
# 1. Setup inicial
cd backend
python manage.py migrate
python manage.py createsuperuser

# 2. Importar dados
python manager.py import ../data/AgricultureData.csv -n agriculture

# 3. Verificar importação
python manager.py list
python manager.py show agriculture -l 5

# 4. Iniciar servidor
python manage.py runserver

# 5. Aceder ao admin: http://localhost:8000/admin
```

## 🌐 URLs Importantes

- **Django Admin**: http://localhost:8000/admin
- **REST API**: http://localhost:8000/api/
- **pgAdmin**: http://localhost:5050 (profile tools)
- **gRPC**: localhost:50051

## 📚 Tecnologias

- **Backend**: Django 4.2, Python 3.11
- **Databases**: PostgreSQL 15, MySQL 8.0, SQLite
- **Data Processing**: Pandas, NumPy
- **XML**: lxml, xmlschema
- **APIs**: FastAPI, gRPC, XML-RPC
- **Container**: Docker, Docker Compose
