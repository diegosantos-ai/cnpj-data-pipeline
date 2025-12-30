import zipfile
import logging
import csv
from pathlib import Path
from tqdm import tqdm

from src.paths import RAW_DIR, PROCESSED_DIR, SAMPLE_DIR
from src.bootstrap import bootstrap
from src.config import pipeline_settings

# Configuração de logging padronizada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def write_head_sample(in_csv, out_csv, n_rows):
    """Lê as primeiras N linhas de um CSV e escreve em outro arquivo (streaming)."""
    # RFB usa latin1 e delimitador ;
    with open(in_csv, "r", encoding="latin1", errors="replace", newline="") as fin, \
         open(out_csv, "w", encoding="utf-8", newline="") as fout:
        
        # Como os arquivos da RFB NÃO têm header, não usamos next(reader)
        # O script de carga via COPY vai assumir a ordem correta das colunas
        reader = csv.reader(fin, delimiter=";")
        writer = csv.writer(fout, delimiter=";")

        count = 0
        for row in reader:
            writer.writerow(row)
            count += 1
            if count >= n_rows:
                break
    return count

def main():
    bootstrap()
    
    zip_files = list(RAW_DIR.glob("*.zip"))
    
    if not zip_files:
        logger.warning("⚠️ Nenhum arquivo .zip encontrado em data/raw")
        return

    logger.info(f"📦 Encontrados {len(zip_files)} arquivos para extração.")
    
    # Define diretório de destino
    target_base = SAMPLE_DIR if pipeline_settings.mode == "sample" else PROCESSED_DIR
    target_base.mkdir(parents=True, exist_ok=True)

    for zip_path in zip_files:
        logger.info(f"🔧 Processando: {zip_path.name}")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for member in zf.infolist():
                    # No modo SAMPLE, extraímos para TMP e depois fazemos o head
                    if pipeline_settings.mode == "sample":
                        tmp_path = PROCESSED_DIR / member.filename # Usa processed como staging
                        final_path = SAMPLE_DIR / member.filename
                        
                        if final_path.exists() and not pipeline_settings.sample_force:
                            logger.info(f"⏩ Amostra de {member.filename} já existe. Pulando.")
                            continue

                        logger.info(f"📂 Extraindo e gerando amostra de {member.filename}...")
                        # Extrai arquivo completo temporariamente
                        zf.extract(member, path=PROCESSED_DIR)
                        
                        # Gera o head (amostra)
                        rows = write_head_sample(tmp_path, final_path, pipeline_settings.sample_rows)
                        logger.info(f"🧪 Amostra gerada: {rows} linhas em {final_path.name}")
                        
                        # Remove o arquivo gigante original para economizar espaço
                        tmp_path.unlink()
                    else:
                        # Modo FULL
                        target_path = PROCESSED_DIR / member.filename
                        if target_path.exists():
                            if target_path.stat().st_size == member.file_size:
                                logger.info(f"⏩ {member.filename} já extraído. Pulando.")
                                continue

                        logger.info(f"📂 Extraindo {member.filename}...")
                        zf.extract(member, path=PROCESSED_DIR)
                    
        except zipfile.BadZipFile:
            logger.error(f"❌ Arquivo corrompido: {zip_path.name}")
        except Exception as e:
            logger.error(f"❌ Erro ao extrair {zip_path.name}: {e}")

    logger.info(f"✅ Processo de extração ({pipeline_settings.mode}) finalizado.")

if __name__ == "__main__":
    main()