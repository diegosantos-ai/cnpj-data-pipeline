import logging
import os
from pathlib import Path
from src.config import settings, pipeline_settings
from sqlalchemy import create_engine
from src.paths import PROCESSED_DIR, SAMPLE_DIR, ensure_dirs, validate_data_root
from src.runners.bootstrap import bootstrap

# Configuração de logging padronizada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define diretório de dados baseado no modo
DATA_DIR = SAMPLE_DIR if pipeline_settings.mode == "sample" else PROCESSED_DIR

# Mapeamento de sufixos de arquivo para tabelas
TABLE_MAPPING = {
    "EMPRECSV": "empresas",
    "ESTABELE": "estabelecimentos",
    "SOCIOCSV": "socios"
}

def get_table_name(filename: str) -> str:
    for suffix, table in TABLE_MAPPING.items():
        if filename.endswith(suffix) or f"{suffix}.loaded" in filename:
            return table
    return None

def load_file(file_path: Path, table_name: str, connection):
    logger.info(f"⏳ MODO {pipeline_settings.mode.upper()}: Carregando {file_path.name} na tabela {table_name}...")
    
    # Montando comando COPY
    # Se for sample, o arquivo foi salvo em UTF-8 no passo 03
    encoding = "UTF8" if pipeline_settings.mode == "sample" else "LATIN1"
    
    sql = f"""
        COPY {table_name} 
        FROM STDIN 
        WITH (
            FORMAT CSV, 
            DELIMITER ';', 
            QUOTE '"', 
            ENCODING '{encoding}', 
            NULL ''
        )
    """
    
    try:
        with open(file_path, "r", encoding=encoding.lower()) as f:
            cursor = connection.connection.cursor()
            cursor.copy_expert(sql, f)
            connection.connection.commit()
        logger.info(f"✅ {file_path.name} carregado com sucesso!")
        
        # Renomeia o arquivo para evitar recarga
        if not file_path.name.endswith(".loaded"):
            file_path.rename(file_path.with_suffix(file_path.suffix + ".loaded"))
        
    except Exception as e:
        connection.connection.rollback()
        logger.error(f"❌ Erro ao carregar {file_path.name}: {e}")

def main():
    bootstrap()
    logger.info(f"🚀 Iniciando carga em modo {pipeline_settings.mode.upper()} a partir de {DATA_DIR}")
    
    if not DATA_DIR.exists():
        logger.warning(f"⚠️ Diretório {DATA_DIR} não encontrado.")
        return

    files = list(DATA_DIR.iterdir())
    files = [f for f in files if f.is_file() and not f.name.endswith(".loaded")]
# ... (restante do main permanece igual)    
    if not files:
        logger.warning("⚠️ Nenhum arquivo pendente encontrado em data/processed.")
        return
        
    logger.info(f"🚀 Iniciando carga de {len(files)} arquivos...")
    
    engine = create_engine(settings.sqlalchemy_url)
    
    with engine.connect() as conn:
        for file_path in files:
            table_name = get_table_name(file_path.name)
            
            if not table_name:
                logger.warning(f"⚠️ Arquivo {file_path.name} ignorado (sem mapeamento de tabela).")
                continue
                
            load_file(file_path, table_name, conn)
            
    logger.info("🎉 Processo de carga finalizado.")

if __name__ == "__main__":
    main()