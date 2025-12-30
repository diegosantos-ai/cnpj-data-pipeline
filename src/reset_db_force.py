from sqlalchemy import create_engine, text
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("🔥 Iniciando RESET FORÇADO do banco de dados...")
    engine = create_engine(settings.sqlalchemy_url, isolation_level="AUTOCOMMIT")
    
    with engine.connect() as conn:
        # Drop tables
        logger.info("💥 Dropando tabelas existentes...")
        conn.execute(text("DROP TABLE IF EXISTS empresas CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS estabelecimentos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS socios CASCADE;"))
        
        # Read SQL
        with open("sql/create_tables.sql", "r", encoding="utf-8") as f:
            sql = f.read()
            
        # Recreate
        logger.info("🏗️ Recriando tabelas...")
        conn.execute(text(sql))
        
    logger.info("✅ Reset concluído com sucesso!")

if __name__ == "__main__":
    main()
