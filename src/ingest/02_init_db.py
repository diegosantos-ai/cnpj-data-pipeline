import logging
import time
from pathlib import Path
from sqlalchemy import create_engine, text
from src.config import settings
from src.paths import PROJECT_ROOT
from src.runners.bootstrap import bootstrap

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SQL_FILE = PROJECT_ROOT / "sql" / "create_tables.sql"

def main():
    bootstrap()
    logger.info("🔌 Conectando ao banco de dados...")
    engine = create_engine(settings.sqlalchemy_url)
    
    if not SQL_FILE.exists():
        logger.error(f"❌ Arquivo SQL não encontrado: {SQL_FILE}")
        return

    logger.info(f"📂 Lendo arquivo de esquema: {SQL_FILE}")
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    logger.info("🚀 Executando criação de tabelas...")
    try:
        with engine.connect() as conn:
            # SQLAlchemy text() para execucao
            # Como sao multiplos statements, precisamos garantir o commit
            # O execute do sqlalchemy com string bruta pode falhar se forem multiplos comandos
            # sem transação explícita
            with conn.begin():
                conn.execute(text(sql_content))
            
            logger.info("✅ Tabelas criadas com sucesso!")
    
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    main()
