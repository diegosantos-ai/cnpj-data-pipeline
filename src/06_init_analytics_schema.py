import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from src.config import settings
from src.paths import PROJECT_ROOT
from src.bootstrap import bootstrap

# Configuração de logging padronizada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("InitAnalytics")

SQL_FILE = PROJECT_ROOT / "sql" / "analytics" / "00_create_schema.sql"

def main():
    # Garante que o ambiente e caminhos estão prontos
    bootstrap()
    
    logger.info("🔌 Conectando ao banco de dados...")
    engine = create_engine(settings.sqlalchemy_url)
    
    if not SQL_FILE.exists():
        logger.error(f"❌ Arquivo SQL não encontrado: {SQL_FILE}")
        return

    logger.info(f"📂 Lendo script de schema: {SQL_FILE.name}")
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    logger.info("🚀 Executando criação do schema 'analytics'...")
    try:
        with engine.connect() as conn:
            # SQLAlchemy text() para execucao e commit explicito
            with conn.begin():
                conn.execute(text(sql_content))
            
            logger.info("✅ Schema 'analytics' validado/criado com sucesso!")
    
    except Exception as e:
        logger.error(f"❌ Erro ao criar schema: {e}")
        exit(1)

if __name__ == "__main__":
    main()
