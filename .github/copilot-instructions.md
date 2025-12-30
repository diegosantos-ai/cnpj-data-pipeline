# CNPJ Data Pipeline - AI Coding Assistant Guide

## Project Overview

This is a **data engineering pipeline** for processing Brazilian Federal Revenue's public CNPJ (company registration) data. It downloads large volumes of public data, extracts it, and loads it into PostgreSQL for analysis. The project is structured as a **learning portfolio** with phased implementation.

**Stack:** Python 3.13, PostgreSQL 16, Docker, SQLAlchemy, Pandas

## Architecture & Data Flow

The pipeline follows a sequential ETL pattern with numbered scripts:

1. **01_download.py** → Downloads ZIP files from Receita Federal's public FTP (uses regex to parse HTML listings)
2. **03_extract_files.py** → Extracts CSV files from ZIPs (skips already extracted files by size check)
3. **04_load_data.py** → Bulk loads CSVs into PostgreSQL using `COPY` (raw psycopg2 `copy_expert`)

Supporting scripts:
- **02_init_db.py** → Creates database schema from `sql/create_tables.sql`
- **00_test_connection.py** → Validates database connectivity (uses psycopg2 directly, not SQLAlchemy)
- **bootstrap.py** → Required initialization (validates paths, creates directories)

**Module Execution Pattern**: All scripts are executed as modules (`python -m src.script_name`), not direct file execution. This ensures proper package imports.

### Critical Path Pattern

**Every executable script MUST call `bootstrap()` at the start of `main()`**. This validates the `DATA_ROOT` environment variable and ensures directory structure exists. See [src/01_download.py](src/01_download.py#L68) for the pattern.

## Configuration System

### Database Configuration
- Central config in [src/config.py](src/config.py) using frozen dataclass
- Loads from `.env` file with sensible defaults
- **Never hardcode credentials** - always use `settings.sqlalchemy_url`

### Path Management
[src/paths.py](src/paths.py) manages all file system paths:
- `DATA_ROOT` can point to external drive (set in `.env`) to avoid filling C: drive
- **Validation is strict**: if `DATA_ROOT` is set but drive doesn't exist, scripts fail fast
- Use `RAW_DIR`, `PROCESSED_DIR`, `TMP_DIR` constants - never construct paths manually

## Data Processing Conventions

### File Naming Patterns
CSV files from Receita Federal follow specific suffixes mapped to tables in [src/04_load_data.py](src/04_load_data.py#L12-L16):
- `*EMPRECSV` → `empresas` table
- `*ESTABELE` → `estabelecimentos` table  
- `*SOCIOCSV` → `socios` table

### Encoding and Delimiters
All CSV files are **LATIN1 encoded** with `;` delimiter. The PostgreSQL `COPY` command in [04_load_data.py](src/04_load_data.py#L25-L32) demonstrates the required parameters.

### Fallback Strategy
[01_download.py](src/01_download.py#L73-L88) implements a **3-month fallback** - tries the most recent data folder first, falls back to previous months if empty. This handles incomplete uploads on the source server.

### Web Scraping Pattern
The download script uses **regex-based HTML parsing** instead of BeautifulSoup:
- Folder discovery: `r'href="(\d{4}-\d{2})/"'` to find YYYY-MM directories
- File discovery: `r'href=["\'](.*?\.zip)["\']'` with case-insensitive matching
- Filters files by prefix: `("Empresas", "Estabelecimentos", "Socios")`

## Development Workflows

### Environment Setup
```powershell
# Start infrastructure
docker-compose up -d

# Access Adminer (database UI) at http://localhost:8080
# System: PostgreSQL | Server: postgres | User: cnpj | Password: cnpj123 | Database: cnpjdb

# Python environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pandas sqlalchemy psycopg2-binary requests tqdm python-dotenv
```

### Running the Pipeline
Execute in order:
```powershell
python -m src.00_test_connection  # Verify DB connectivity first
python -m src.02_init_db          # Create tables
python -m src.01_download         # Download data (slow, GBs)
python -m src.03_extract_files    # Extract ZIPs
python -m src.04_load_data        # Load to PostgreSQL
```

### External Drive Configuration
If using external storage (recommended for large datasets):
```ini
# In .env
DATA_ROOT=D:\cnpj-data  # Adjust drive letter
```
The code will **fail explicitly** if the drive is unavailable rather than silently falling back to project directory.

## Code Quality Patterns

- **Logging**: All scripts use `logging` module with standard format: `"%(asctime)s - %(levelname)s - %(message)s"`
- **Error Handling**: Network operations use try/except with user-friendly emoji messages (❌, ✅, ⚠️, 🚀)
- **Progress Indication**: Downloads use `tqdm` for progress bars with byte-level tracking
- **Idempotency**: Scripts check if work is already done (file exists, correct size) before reprocessing
- **Bilingual Context**: README is in Portuguese; code comments and variable names are English-first

## Database Schema Notes

Tables in [sql/create_tables.sql](sql/create_tables.sql) are designed for **bulk loading performance**:
- No primary keys or indexes initially (add after load)
- Many columns are VARCHAR instead of typed fields (matches CSV format)
- Capital social stored as VARCHAR (comes with comma separators in CSV)

The schema deliberately trades normalization for load speed, expecting downstream transformation.

### PostgreSQL COPY Usage
The load script uses **raw psycopg2 cursor** for COPY operations, not SQLAlchemy abstractions:
```python
cursor = connection.connection.cursor()  # Access underlying psycopg2 cursor
cursor.copy_expert(sql, file_handle)     # Direct COPY FROM STDIN
connection.connection.commit()           # Manual transaction control
```
This is required because SQLAlchemy doesn't expose `COPY` functionality directly
The schema deliberately trades normalization for load speed, expecting downstream transformation.

## Common Pitfalls

1. **Forgetting `bootstrap()`**: Scripts will fail on path operations without it
2. **Wrong encoding**: CSVs are LATIN1, not UTF-8
3. **Drive letter changes**: External drives may get different letters - update `.env`
4. **Transaction handling**: SQLAlchemy COPY requires explicit transaction management (see [04_load_data.py](src/04_load_data.py#L40))

## Project Goals

This is a **portfolio/learning project** emphasizing:
- Working with real, large-scale public data
- Reproducible environment setup
- Professional Python project structure  
- Documented, phased implementation

When suggesting improvements, prioritize **clarity and documentation** over optimization.
