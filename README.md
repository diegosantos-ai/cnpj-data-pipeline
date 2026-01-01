# CNPJ Data Pipeline

## 📋 Visão geral do projeto

Este projeto tem como objetivo construir um **pipeline de engenharia de dados** utilizando os **Dados Abertos de CNPJ da Receita Federal**, cobrindo desde a preparação do ambiente até a ingestão, modelagem e disponibilização dos dados para análise.

O projeto é estruturado por **fases**, cada uma documentada e versionada, para servir tanto como **material de aprendizado prático** quanto como **evidência de experienciada aplicada em engenharia de dados**.

---

## 🎯 Objetivos do projeto

- Trabalhar com **dados públicos reais e volumosos**.
- Construir um pipeline **reprodutível e organizado**.
- Aplicar boas práticas de engenharia de dados (Quality Gates, Analytics Schema).
- Gerar material utilizável como **portfólio profissional**.

---

## 🛠 Stack utilizada

- **Linguagem:** Python 3.13
- **Banco de Dados:** PostgreSQL 16
- **Infraestrutura:** Docker + Docker Compose
- **Qualidade:** Great Expectations (GX)
- **Bibliotecas:** SQLAlchemy, Pandas, python-dotenv, tqdm, requests
- **Ferramentas:** Adminer, Git e GitHub

---

## 📂 Estrutura do projeto

```text
cnpj-data-pipeline/
│
├── docker-compose.yml       # Infraestrutura (Postgres + Adminer)
├── .env                     # Variáveis de ambiente (não versionado)
├── .gitignore
│
├── src/
│   ├── run_pipeline.py      # Orquestrador do pipeline (Runner)
│   ├── bootstrap.py         # Validação de ambiente e diretórios
│   ├── paths.py             # Centralização de caminhos (DATA_ROOT)
│   ├── setup_gx.py          # Configuração do Great Expectations
│   ├── 01_download.py        # Ingestão (Download)
│   ├── 02_init_db.py         # Inicialização do schema public
│   ├── 03_extract_files.py   # Extração e Amostragem Inteligente
│   ├── 04_load_data.py       # Carga no banco de dados
│   ├── 06_init_analytics_schema.py # Criação do schema analytics
│   ├── 07_promote_to_analytics.py  # Promoção Processed -> Analytics
│   └── 08_quality_gate.py    # Gate de Qualidade bloqueante (GX)
│
├── sql/
│   ├── create_tables.sql    # DDL das tabelas raw (public)
│   └── analytics/           # Scripts de promoção e views
└── docs/                    # Documentação e evidências
```

---

## 🏗️ Fase 0 — Setup do ambiente (✅ Concluída)

**Objetivo:** Preparar um ambiente local totalmente reprodutível, isolado via container e com ambiente Python controlado.

---

## 📥 Fase 1 — Ingestão de Dados (✅ Concluída)

**Destaques:**
- **Padrão DATA_ROOT:** Armazenamento em drive externo para Big Data.
- **Modo Sample Inteligente:** Amostragem ancorada em Empresas com filtragem em cascata para Estabelecimentos e Sócios, garantindo **100% de integridade referencial** mesmo em amostras pequenas.

---

## 📊 Fase 2 — Arquitetura Analytics & Qualidade (✅ Concluída)

### 1. Promoção Processed → Analytics
Implementada a separação física entre dados de processamento (`public`) e dados para consumo analítico (`analytics`).
- **Gate de Qualidade:** O script de promoção só é executado se os dados passarem nas validações de integridade.
- **Views de Consumo:** Criação de views analíticas otimizadas para dashboards.

### 2. Quality Gate com Great Expectations
Integração do **Great Expectations (GX 1.0+)** para garantir que apenas dados íntegros cheguem ao usuário final.
- **Validações:** Contagem de linhas, unicidade de CNPJ, obrigatoriedade de campos chave.
- **Data Docs:** Documentação automatizada da qualidade dos dados gerada a cada execução.

---

## 🚀 Como Executar

### 1. Iniciar Infraestrutura
```powershell
docker-compose up -d
```

### 2. Rodar Pipeline (Modo Sample)
```powershell
python -m src.run_pipeline --mode sample --sample-rows 50000 --force
```

### 3. Validar e Promover
```powershell
python -m src.06_init_analytics_schema
python -m src.08_quality_gate
python -m src.07_promote_to_analytics
```

---

## 🔜 Próxima fase: Fase 3 — Transformação Pesada (Dask/DuckDB)
- Processamento paralelo para carga Full.
- Conversão para Parquet no HD externo.
- Otimização de performance para milhões de registros.
