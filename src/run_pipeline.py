import subprocess
import sys
import logging
import time
import argparse
import os

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PipelineOrchestrator")

# Lista de passos do pipeline (Módulos Python)
PIPELINE_STEPS = [
    "src.01_download",      # Baixa arquivos
    "src.02_init_db",       # Cria/Reseta tabelas
    "src.03_extract_files", # Extrai zips
    "src.04_load_data"      # Carrega no Banco
]

def run_step(module_name: str, dry_run: bool = False) -> None:
    """Executa um módulo python como script e aborta em caso de erro."""
    prefix = "[DRY-RUN] " if dry_run else ""
    logger.info(f"▶️  {prefix}Iniciando etapa: {module_name}")
    
    start_time = time.time()
    
    if dry_run:
        time.sleep(0.2)
        logger.info(f"✅ {prefix}Etapa {module_name} simulada com sucesso.\n")
        return

    try:
        subprocess.run(
            [sys.executable, "-m", module_name],
            check=True,
            text=True
        )
        elapsed = time.time() - start_time
        logger.info(f"✅ Etapa {module_name} concluída em {elapsed:.2f}s.\n")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FALHA CRÍTICA na etapa {module_name}. Código de saída: {e.returncode}")
        logger.error("🛑 Abortando pipeline.")
        sys.exit(e.returncode)
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao executar {module_name}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Orquestrador do Pipeline de Dados CNPJ")
    
    parser.add_argument("--mode", choices=["full", "sample"], default="sample", help="Modo de execução (padrão: sample)")
    parser.add_argument("--sample-rows", type=int, default=10000, help="Núm. de linhas por arquivo no modo sample")
    parser.add_argument("--sample-files-per-type", type=int, default=1, dest="sample_files", help="Núm. de arquivos por tipo no modo sample")
    parser.add_argument("--sample-seed", type=int, default=42, help="Seed para seleção aleatória (se implementado)")
    parser.add_argument("--force", action="store_true", help="Força a re-extração/re-amostragem de arquivos já existentes")
    parser.add_argument("--dry-run", action="store_true", help="Simula a execução")
    parser.add_argument("--only", type=str, help="Executa apenas uma etapa específica")

    args = parser.parse_args()

    # Repassa argumentos via variáveis de ambiente para os sub-processos
    os.environ["PIPELINE_MODE"] = args.mode
    os.environ["SAMPLE_ROWS"] = str(args.sample_rows)
    os.environ["SAMPLE_FILES_PER_TYPE"] = str(args.sample_files)
    os.environ["SAMPLE_SEED"] = str(args.sample_seed)
    os.environ["SAMPLE_FORCE"] = "1" if args.force else "0"

    print("="*60)
    mode_str = f"MODO {args.mode.upper()}"
    if args.dry_run: mode_str += " (SIMULAÇÃO)"
    logger.info(f"🚀 ORQUESTRADOR DE PIPELINE INICIADO - {mode_str}")
    logger.info(f"📍 DATA_ROOT: {os.getenv('DATA_ROOT', 'data/ (local)')}")
    print("="*60 + "\n")

    steps_to_run = PIPELINE_STEPS
    if args.only:
        steps_to_run = [s for s in PIPELINE_STEPS if args.only in s]
        if not steps_to_run:
            logger.error(f"❌ Nenhuma etapa encontrada para: {args.only}")
            sys.exit(1)

    total_start = time.time()
    for step in steps_to_run:
        run_step(step, dry_run=args.dry_run)

    total_elapsed = time.time() - total_start
    print("\n" + "="*60)
    logger.info(f"🎉 PIPELINE FINALIZADO! Tempo total: {total_elapsed:.2f}s")
    print("="*60)

if __name__ == "__main__":
    main()
