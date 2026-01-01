import great_expectations as gx
import logging
import sys
import webbrowser
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("QualityGate")

def main():
    logger.info("🛡️  Iniciando Quality Gate (Great Expectations)...")
    
    context = gx.get_context(project_root_dir=".")
    checkpoint_name = "checkpoint_full_validation"
    
    try:
        # Executa o checkpoint configurado (Sintaxe v1.0+)
        checkpoint = context.checkpoints.get(checkpoint_name)
        results = checkpoint.run()
    except Exception as e:
        logger.error(f"❌ Erro ao executar checkpoint: {e}")
        sys.exit(1)

    # Analisa resultados
    success = results.success
    logger.info("="*50)
    
    if success:
        logger.info("✅ QUALITY GATE APROVADO! Todas as expectativas foram atendidas.")
    else:
        logger.error("❌ QUALITY GATE FALHOU! Violações detectadas.")
        
    # Build Data Docs para visualização
    logger.info("📄 Gerando Data Docs...")
    context.build_data_docs()
    
    # Opcional: Abrir docs automaticamente (comentado para ambiente headless)
    # context.open_data_docs()
    
    docs_path = Path("gx/uncommitted/data_docs/local_site/index.html").resolve()
    logger.info(f"👉 Relatório completo disponível em: {docs_path}")
    logger.info("="*50)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
