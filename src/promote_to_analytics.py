import logging
from sqlalchemy import create_engine, text
from src.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("PromoteAnalytics")

def main():
    logger.info("🚀 Iniciando promoção para ANALYTICS...")
    
    engine = create_engine(settings.sqlalchemy_url)
    
    # 1. Validação (Exemplo simples: verificar se existem dados em empresas)
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM empresas")).scalar()
        if count == 0:
            logger.error("❌ Validação falhou: Tabela 'empresas' está vazia. Promoção abortada.")
            return
        logger.info(f"✅ Validação de dados OK (Empresas: {count} linhas).")

        # 2. Promoção (Criar View/Tabela em Analytics)
        # View de empresas ativas (Situação Cadastral = 02 na Matriz)
        ddl_view = """
        CREATE OR REPLACE VIEW analytics.v_empresas_ativas AS
        SELECT 
            e.cnpj_basico,
            e.razao_social,
            e.natureza_juridica,
            e.capital_social,
            est.situacao_cadastral,
            est.uf
        FROM public.empresas e
        JOIN public.estabelecimentos est ON e.cnpj_basico = est.cnpj_basico
        WHERE est.identificador_matriz_filial = '1' -- Apenas Matrizes
          AND est.situacao_cadastral = '02'; -- 02 = Ativa
        """
        
        logger.info("🛠️ Criando view 'analytics.v_empresas_ativas'...")
        conn.execute(text(ddl_view))
        conn.commit()
        
        logger.info("🎉 Promoção concluída com sucesso!")

if __name__ == "__main__":
    main()
