import zipfile
import logging
import csv
import os
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

# Conjunto global para armazenar chaves de empresas (CNPJ Básico)
# Usado apenas no modo sample para garantir integridade referencial
EMPRESA_KEYS = set()

def extract_and_sample(zip_path: Path, output_dir: Path, is_empresa: bool = False):
    """
    Extrai arquivo do zip e gera amostra.
    Se is_empresa=True, popula o set EMPRESA_KEYS.
    Se is_empresa=False, filtra usando EMPRESA_KEYS.
    """
    global EMPRESA_KEYS
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.infolist():
                final_path = output_dir / member.filename
                
                # Check de idempotência (se não forçado)
                if final_path.exists() and not pipeline_settings.sample_force:
                    logger.info(f"⏩ Amostra de {member.filename} já existe. Pulando.")
                    
                    # Se for empresa e o arquivo já existe, precisamos carregar as chaves dele
                    # para poder filtrar os próximos (estabelecimentos/socios)
                    if is_empresa and pipeline_settings.mode == "sample":
                        logger.info(f"♻️  Carregando chaves de empresa existentes de {final_path.name}...")
                        with open(final_path, "r", encoding="utf-8") as f:
                            reader = csv.reader(f, delimiter=";")
                            for row in reader:
                                if row: EMPRESA_KEYS.add(row[0])
                        logger.info(f"📊 Chaves carregadas: {len(EMPRESA_KEYS)}")
                    continue

                logger.info(f"📂 Extraindo e gerando amostra inteligente de {member.filename}...")
                
                # Extrai para stream (usando open do zipfile)
                # Não extrai para disco para economizar I/O e espaço
                with zf.open(member) as zfile:
                    # Wrapper para ler como texto (latin1 é o padrão da RFB)
                    import io
                    text_stream = io.TextIOWrapper(zfile, encoding="latin1", errors="replace")
                    
                    with open(final_path, "w", encoding="utf-8", newline="") as fout:
                        reader = csv.reader(text_stream, delimiter=";")
                        writer = csv.writer(fout, delimiter=";")
                        
                        count = 0
                        skipped = 0
                        
                        for row in reader:
                            if not row: continue
                            
                            cnpj_basico = row[0]
                            
                            if is_empresa:
                                # Modo Empresa: Adiciona ao set e escreve
                                EMPRESA_KEYS.add(cnpj_basico)
                                writer.writerow(row)
                                count += 1
                            else:
                                # Modo Satélite (Estab/Socio): Filtra pelo set
                                if cnpj_basico in EMPRESA_KEYS:
                                    writer.writerow(row)
                                    count += 1
                                else:
                                    skipped += 1
                            
                            # Limite de linhas (apenas se escreveu)
                            if count >= pipeline_settings.sample_rows:
                                break
                        
                        logger.info(f"✅ {final_path.name}: {count} linhas escritas. (Skipped: {skipped})")

    except zipfile.BadZipFile:
        logger.error(f"❌ Arquivo corrompido: {zip_path.name}")
    except Exception as e:
        logger.error(f"❌ Erro ao processar {zip_path.name}: {e}")

def main():
    bootstrap()
    
    if pipeline_settings.mode == "sample":
        logger.info(f"🧪 MODO SAMPLE (Inteligente) ATIVADO")
        logger.info(f"🎯 Alvo: {pipeline_settings.sample_rows} linhas filtradas por integridade.")
        target_dir = SAMPLE_DIR
    else:
        logger.info("🚀 MODO FULL ATIVADO")
        target_dir = PROCESSED_DIR
    
    target_dir.mkdir(parents=True, exist_ok=True)
    
    all_zips = list(RAW_DIR.glob("*.zip"))
    if not all_zips:
        logger.warning("⚠️ Nenhum arquivo .zip encontrado.")
        return

    # Separa por tipos para garantir ordem de processamento
    # 1. Empresas (Gera as chaves)
    # 2. Estabelecimentos (Consome chaves)
    # 3. Socios (Consome chaves)
    
    zips_emp = sorted([f for f in all_zips if "Empresas" in f.name])
    zips_estab = sorted([f for f in all_zips if "Estabelecimentos" in f.name])
    zips_socio = sorted([f for f in all_zips if "Socios" in f.name])
    
    # Se estiver em modo sample, filtra a quantidade de arquivos aqui também
    # (Embora o download já tenha filtrado, é bom garantir)
    if pipeline_settings.mode == "sample":
        k = pipeline_settings.sample_files_per_type
        zips_emp = zips_emp[:k]
        zips_estab = zips_estab[:k]
        zips_socio = zips_socio[:k]

    # 1. Processar Empresas
    logger.info("--- ETAPA 1: EMPRESAS (Gerando Chaves) ---")
    for z in zips_emp:
        extract_and_sample(z, target_dir, is_empresa=True)
    
    logger.info(f"🔑 Total de Chaves de Empresas Carregadas: {len(EMPRESA_KEYS)}")

    # 2. Processar Estabelecimentos
    logger.info("--- ETAPA 2: ESTABELECIMENTOS (Filtrando) ---")
    for z in zips_estab:
        extract_and_sample(z, target_dir, is_empresa=False)

    # 3. Processar Socios
    logger.info("--- ETAPA 3: SOCIOS (Filtrando) ---")
    for z in zips_socio:
        extract_and_sample(z, target_dir, is_empresa=False)

    logger.info("✅ Processo finalizado com sucesso.")

if __name__ == "__main__":
    main()
