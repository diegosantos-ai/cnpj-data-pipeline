import logging
from sqlalchemy import create_engine, text
from src.config import settings
from src.paths import PROJECT_ROOT
from src.bootstrap import bootstrap

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PromoteAnalytics")

SQL_FILE = PROJECT_ROOT / "sql" / "analytics" / "10_views_mvp.sql"

def main():
    bootstrap()
    
    logger.info("🚀 Iniciando promoção para ANALYTICS (MVP Views)...")
    engine = create_engine(settings.sqlalchemy_url)
    
    # 1. Gate: Validação de Dados (Exemplo simplificado)
    # Em produção, aqui verificaríamos os resultados do Great Expectations
    with engine.connect() as conn:
        logger.info("🛡️  Executando Gate de Qualidade (Sanity Check)...")
        count = conn.execute(text("SELECT COUNT(*) FROM public.empresas")).scalar()
        
        if count == 0:
            logger.error("❌ Gate FALHOU: Tabela 'empresas' está vazia.")
            return
        logger.info(f"✅ Gate APROVADO: {count} empresas encontradas.")

        # 2. Executar Views
        if not SQL_FILE.exists():
            logger.error(f"❌ Arquivo SQL não encontrado: {SQL_FILE}")
            return

        logger.info(f"📂 Aplicando views de: {SQL_FILE.name}")
        with open(SQL_FILE, "r", encoding="utf-8") as f:
            sql_content = f.read()
            
        try:
            # Executa comandos separados por ;
            commands = sql_content.split(';')
            for cmd in commands:
                if cmd.strip():
                    conn.execute(text(cmd))
            
            conn.commit() # Commit explícito para DDL
            
            logger.info("✅ Views criadas/atualizadas com sucesso!")
            
            # 3. Validação pós-promoção (Smoke Test)
            logger.info("🔎 Validando view 'v_distribuicao_natureza'...")
            res = conn.execute(text("SELECT COUNT(*) FROM analytics.v_distribuicao_natureza")).scalar()
            logger.info(f"✅ View acessível. Linhas retornadas: {res}")

        except Exception as e:
            logger.error(f"❌ Erro ao criar views: {e}")

if __name__ == "__main__":
    main()
