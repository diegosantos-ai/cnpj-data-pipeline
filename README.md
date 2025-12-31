# CNPJ Data Pipeline

## 📋 Visão geral do projeto

Este projeto nasceu como uma resposta prática a um desafio real de engenharia de dados envolvendo os Dados Abertos de CNPJ da Receita Federal, que é uma base pública, massiva e pouco amigável para uso analítico.

Mais do que construir um pipeline funcional, o objetivo foi lidar com decisões reais de escopo, volume, integridade e trade-offs, comuns em ambientes de produção, mas raramente exploradas em projetos acadêmicos.

O projeto é estruturado por fases, cada uma documentada e versionada, servindo como material de aprendizado prático e, principalmente, como evidência concreta da minha capacidade de atuar em engenharia de dados orientada a contexto e uso real.

---

## 🎯 Objetivos do projeto

- Trabalhar com **dados públicos reais e volumosos**.
- Construir um pipeline **reprodutível e organizado**.
- Aplicar boas práticas de engenharia de dados desde o setup.
- Gerar material utilizável como **portfólio profissional**.

---

## 🛠 Stack utilizada

- **Linguagem:** Python 3.13
- **Banco de Dados:** PostgreSQL 16
- **Infraestrutura:** Docker + Docker Compose
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
│   ├── __init__.py
│   ├── config.py            # Configuração central (DB e Pipeline)
│   ├── paths.py             # Centralização de caminhos (DATA_ROOT)
│   ├── bootstrap.py         # Validação de ambiente e diretórios
│   ├── run_pipeline.py      # Orquestrador do pipeline
│   ├── 00_test_connection.py # Teste de conexão
│   ├── 01_download.py        # Ingestão (Download)
│   ├── 02_init_db.py         # Inicialização do schema
│   ├── 03_extract_files.py   # Extração e Amostragem
│   └── 04_load_data.py       # Carga no banco de dados
│
├── sql/
│   └── create_tables.sql    # DDL das tabelas
├── logs/                    # Logs de execução
└── docs/                    # Documentação e evidências
```

---

## 🏗️ Fase 0 — Setup do ambiente (✅ Concluída)

**Objetivo:** Preparar um ambiente local totalmente reprodutível, isolado via container e com ambiente Python controlado.

**Destaques:**
- PostgreSQL via Docker Compose.
- Variáveis de ambiente centralizadas no `.env`.
- Scripts de teste de conexão validados.

---

## 📥 Fase 1 — Ingestão de Dados (✅ Concluída)

### 1. Status da Fase
- **Status:** Concluída
- **Validação:** QA aprovado (Sanity Checks 100% match em modo sample)
- **HD Externo:** Configurado e validado para grandes volumes.

### 2. Critério de Encerramento
A Fase 1 foi encerrada após o atendimento dos seguintes critérios:
- Pipeline de ingestão executável ponta a ponta.
- Paths externos (`DATA_ROOT`) configurados e isolados.
- Estrutura de `bootstrap` validada (Fail-fast para HD desconectado).
- Runner funcional (`run_pipeline.py`) com suporte a flags.
- **Suporte a modo `sample` inteligente** (preservando integridade referencial entre Empresas, Estabelecimentos e Sócios).

### 3. Decisões Técnicas Documentadas

#### 3.1 Padrão DATA_ROOT
Adotado para centralizar a localização de dados brutos e processados fora do repositório Git, facilitando a portabilidade e mantendo o repositório leve.

#### 3.2 Uso de HD Externo
Decisão consciente de arquitetura para lidar com o volume massivo da base completa (Big Data), garantindo escalabilidade sem comprometer o armazenamento interno (SSD).

#### 3.3 Modo Sample Inteligente
Implementação de amostragem ancorada em **Empresas**. O pipeline extrai uma amostra de empresas e filtra automaticamente os estabelecimentos e sócios correspondentes, garantindo que o banco de dados de teste seja consistente (Join Rate de 100%).

#### 3.4 Orquestrador (Runner)
Criação do `src.run_pipeline` para centralizar a execução, suportando as flags:
- `--mode [full|sample]`: Alterna entre carga completa e amostra.
- `--sample-rows N`: Define o tamanho da amostra.
- `--force`: Força a regeração de amostras.
- `--dry-run`: Simula as etapas sem execução real.

### 4. Evidências de Execução

**Execução em modo Sample:**
```powershell
python -m src.run_pipeline --mode sample --sample-rows 50000 --force
```
- **Resultado:** ~500k registros carregados (50k por arquivo) com integridade referencial total.
- **Sanity Check:** Match rate Estabelecimentos -> Empresas: **100.0%**.

---

## 🔜 Próxima fase: Fase 2 — Transformação e Normalização
- Limpeza de dados.
- Tipagem correta de colunas (Datas, Números).
- Criação de Primary Keys e Índices para performance.
- Normalização de tabelas auxiliares (CNAEs, Municípios, etc.).
