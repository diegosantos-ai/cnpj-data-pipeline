
# CNPJ Data Pipeline

## 📋 Visão geral do projeto

Este projeto tem como objetivo construir um **pipeline de engenharia de dados** utilizando os **Dados Abertos de CNPJ da Receita Federal**, cobrindo desde a preparação do ambiente até a ingestão, modelagem e disponibilização dos dados para análise.

O projeto foi estruturado por **fases**, cada uma documentada e versionada, para servir tanto como **material de aprendizado prático** quanto como **evidência de experiência aplicada em engenharia de dados**.

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
- **Bibliotecas:** SQLAlchemy, Pandas, python-dotenv
- **Ferramentas:** Adminer (interface de banco), Git e GitHub

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
│   ├── __init__.py          # Define src como pacote Python
│   ├── config.py            # Configuração central do banco de dados
│   └── 00_test_connection.py # Teste de conexão com o banco
│
├── data/
│   ├── raw/                 # Dados brutos (não versionados)
│   └── processed/           # Dados processados
│
├── sql/                     # Scripts SQL
├── docs/                    # Documentação e evidências
└── logs/                    # Logs de execução
Fase 0 — Setup do ambiente
Objetivo da fase
Preparar um ambiente local totalmente reprodutível, garantindo que:

O banco de dados esteja isolado via container.

O acesso ao banco seja simples e visual.

O ambiente Python esteja controlado.

A estrutura base do projeto esteja organizada.

Nota: Nenhum dado é processado nesta fase. Ela estabelece a fundação sólida para todo o pipeline.

🐳 Infraestrutura com Docker
docker-compose.yml
YAML

services:
  postgres:
    image: postgres:16
    container_name: cnpj_postgres
    environment:
      POSTGRES_USER: cnpj
      POSTGRES_PASSWORD: cnpj123
      POSTGRES_DB: cnpjdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata_cnpj:/var/lib/postgresql/data

  adminer:
    image: adminer:4
    container_name: cnpj_adminer
    ports:
      - "8080:8080"
    depends_on:
      - postgres

volumes:
  pgdata_cnpj:
O que este arquivo faz:

Sobe um banco PostgreSQL em container.

Cria um volume persistente para os dados (pgdata_cnpj).

Disponibiliza o Adminer via navegador (porta 8080).

Evita instalação manual de banco no sistema operacional.

⚙️ Configurações e Ambiente
Variáveis de ambiente
Arquivo .env (na raiz do projeto, não versionado):

Ini, TOML

DB_HOST=localhost
DB_PORT=5432
DB_NAME=cnpjdb
DB_USER=cnpj
DB_PASSWORD=cnpj123
Essas variáveis são carregadas pelos scripts Python para configurar a conexão com o banco.

Ambiente Python
Criação do ambiente virtual:

Bash

python -m venv .venv
.\.venv\Scripts\Activate.ps1
Instalação das dependências:

Bash

pip install pandas sqlalchemy psycopg2-binary requests tqdm python-dotenv
🐍 Implementação em Python
Configuração central do banco (src/config.py)
Python

from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

@dataclass(frozen=True)
class DBConfig:
    # Parâmetros de conexão com o banco
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "cnpjdb")
    user: str = os.getenv("DB_USER", "cnpj")
    password: str = os.getenv("DB_PASSWORD", "cnpj123")

    @property
    def sqlalchemy_url(self) -> str:
        # String de conexão usada pelo SQLAlchemy
        return (
            f"postgresql+psycopg2://"
            f"{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )
Por que isso é importante:

Centraliza a configuração de acesso.

Evita credenciais hardcoded no código.

Facilita reutilização em outros scripts.

Teste de conexão (src/00_test_connection.py)
Python

from sqlalchemy import create_engine, text
from src.config import DBConfig

def main():
    # Cria objeto de configuração
    cfg = DBConfig()

    # Cria engine de conexão com o banco
    engine = create_engine(cfg.sqlalchemy_url)

    # Abre conexão e executa query simples
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 AS ok")
        ).mappings().one()

        # Confirma que o banco respondeu corretamente
        print(f"DB connection OK: {result['ok']}")

if __name__ == "__main__":
    main()
Execução do teste:

Bash

python -m src.00_test_connection
Resultado esperado:

Plaintext

DB connection OK: 1
✅ Checklist da Fase 0
[x] Docker Compose configurado

[x] PostgreSQL rodando em container

[x] Adminer acessível via navegador

[x] Ambiente Python isolado com venv

[x] Estrutura base do projeto criada

[x] Conexão com banco validada via código

🚀 O que esta fase demonstra
Capacidade de preparar ambiente reprodutível.

Uso prático de Docker e PostgreSQL.

Organização profissional de projeto Python.

Boas práticas iniciais de engenharia de dados.

🔜 Próxima fase: Fase 1 — Ingestão de dados
Análise da estrutura dos dados da Receita Federal.

Download automatizado dos arquivos.

Extração dos dados brutos para processamento.


