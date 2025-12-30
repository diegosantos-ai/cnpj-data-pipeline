import logging
import os
import re
import requests
from pathlib import Path
from tqdm import tqdm
from src.paths import RAW_DIR
from src.bootstrap import bootstrap
from src.config import pipeline_settings

# Configuração de logging padronizada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"

def get_available_folders(base_url: str) -> list:
    """Retorna lista de pastas de data (YYYY-MM) ordenadas."""
    logger.info(f"🔍 Mapeando versões disponíveis em: {base_url}")
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão: {e}")
        return []

    # Regex para capturar pastas no formato YYYY-MM
    folders = re.findall(r'href="(\d{4}-\d{2})/"', response.text)
    return sorted(list(set(folders)))

def get_files_from_folder(folder_url: str) -> list:
    """Retorna lista de arquivos .zip dentro de uma pasta."""
    logger.info(f"📡 Inspecionando: {folder_url}")
    try:
        response = requests.get(folder_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    # Regex mais robusto para encontrar .zip (aceita aspas simples ou duplas)
    # Ignora maiúsculas/minúsculas
    files = re.findall(r'href=["\'](.*?\.zip)["\']', response.text, re.IGNORECASE)
    
    # Filtra apenas os arquivos de interesse
    targets = [
        f for f in files
        if f.startswith(("Empresas", "Estabelecimentos", "Socios"))
    ]
    return list(set(targets)) # Remove duplicatas se houver

def download_file(url: str, output_path: Path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with open(output_path, "wb") as file, tqdm(
        desc=output_path.name,
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                bar.update(len(chunk))    

def main():
    bootstrap()
    folders = get_available_folders(BASE_URL)
    if not folders:
        logger.error("❌ Nenhuma pasta de dados encontrada.")
        return

    # Tenta do mais recente para o mais antigo (fallback)
    # Pega os 3 últimos meses para garantir
    candidate_folders = folders[-3:] 
    candidate_folders.reverse() # Começa do mais atual

    selected_files = []
    target_url = ""

    for month_folder in candidate_folders:
        target_url = BASE_URL + month_folder + "/"
        logger.info(f"Tentando mês: {month_folder}...")
        
        found_files = get_files_from_folder(target_url)
        
        if len(found_files) > 0:
            logger.info(f"✅ Sucesso! Encontrados {len(found_files)} arquivos em {month_folder}")
            selected_files = found_files
            break
        else:
            logger.warning(f"⚠️  Pasta {month_folder} parece vazia ou incompleta. Tentando anterior...")

    if not selected_files:
        logger.error("❌ Não foi possível encontrar arquivos em nenhum dos meses recentes.")
        return

    # APLICANDO FILTRO DE AMOSTRA SE NECESSÁRIO
    if pipeline_settings.mode == "sample":
        logger.info(f"🧪 MODO SAMPLE ATIVADO: Baixando apenas {pipeline_settings.sample_files_per_type} arquivos por tipo.")
        
        empresas = [f for f in selected_files if "Empresas" in f]
        estabelecimentos = [f for f in selected_files if "Estabelecimentos" in f]
        socios = [f for f in selected_files if "Socios" in f]
        
        # Pega os primeiros K de cada (determinístico pois a lista vem ordenada/estável do site)
        k = pipeline_settings.sample_files_per_type
        
        # Ordena para garantir determinismo absoluto
        empresas.sort()
        estabelecimentos.sort()
        socios.sort()
        
        sample_selection = []
        sample_selection.extend(empresas[:k])
        sample_selection.extend(estabelecimentos[:k])
        sample_selection.extend(socios[:k])
        
        logger.info(f"📋 Arquivos selecionados para amostra: {sample_selection}")
        selected_files = sample_selection

    # Inicia Download
    logger.info(f"🚀 Iniciando download de {len(selected_files)} arquivos...")
    for filename in selected_files:
        file_path = RAW_DIR / filename
        
        if file_path.exists():
            logger.info(f"⏭️  {filename} já existe. Pulando.")
            continue

        file_url = target_url + filename
        logger.info(f"⬇️  Baixando {filename}...")
        try:
            download_file(file_url, file_path)
        except Exception as e:
            logger.error(f"❌ Erro em {filename}: {e}")
            if file_path.exists(): os.remove(file_path)

    logger.info("🎉 Processo finalizado.")

if __name__ == "__main__":
    main()
