import logging
import pandas as pd
from sqlalchemy import create_engine, text
from src.config import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("SanityCheck")

def main():
    engine = create_engine(settings.sqlalchemy_url)
    
    queries = {
        "Contagens por Tabela": """
            SELECT 
                (SELECT COUNT(*) FROM empresas) AS empresas,
                (SELECT COUNT(*) FROM estabelecimentos) AS estabelecimentos,
                (SELECT COUNT(*) FROM socios) AS socios;
        """,
        "Nulos em cnpj_basico": """
            SELECT 
                (SELECT COUNT(*) FROM empresas WHERE cnpj_basico IS NULL) AS empresas_null,
                (SELECT COUNT(*) FROM estabelecimentos WHERE cnpj_basico IS NULL) AS estab_null,
                (SELECT COUNT(*) FROM socios WHERE cnpj_basico IS NULL) AS socios_null;
        """,
                "Duplicidades em Empresas (cnpj_basico)": """
                    SELECT cnpj_basico, COUNT(*) as n
                    FROM empresas
                    GROUP BY cnpj_basico
                    HAVING COUNT(*) > 1
                    LIMIT 10;
                """,
                "Estabelecimentos Órfãos (sem Empresa)": """
                    SELECT COUNT(*) AS estab_sem_empresa
                    FROM estabelecimentos e
                    LEFT JOIN empresas emp ON emp.cnpj_basico = e.cnpj_basico
                    WHERE emp.cnpj_basico IS NULL;
                """,
                "Sócios Órfãos (sem Empresa)": """
                    SELECT COUNT(*) AS socios_sem_empresa
                    FROM socios s
                    LEFT JOIN empresas emp ON emp.cnpj_basico = s.cnpj_basico
                    WHERE emp.cnpj_basico IS NULL;
                """,
                        "Percentual de Match (Estab -> Empresa)": """
                            SELECT
                              COUNT(*) FILTER (WHERE emp.cnpj_basico IS NOT NULL) * 100.0 / COUNT(*) AS pct_match
                            FROM estabelecimentos e
                            LEFT JOIN empresas emp ON emp.cnpj_basico = e.cnpj_basico;
                        """,
                        "Top Naturezas Jurídicas (Empresas)": """
                            SELECT natureza_juridica, COUNT(*)
                            FROM empresas
                            GROUP BY natureza_juridica
                            ORDER BY COUNT(*) DESC
                            LIMIT 5;
                        """,
                        "Top Municípios (Estabelecimentos)": """
                            SELECT municipio, COUNT(*)
                            FROM estabelecimentos
                            GROUP BY municipio
                            ORDER BY COUNT(*) DESC
                            LIMIT 5;
                        """,
                        "Top Qualificação Sócio": """
                            SELECT qualificacao_socio, COUNT(*)
                            FROM socios
                            GROUP BY qualificacao_socio
                            ORDER BY COUNT(*) DESC
                            LIMIT 5;
                        """
                    }
    with engine.connect() as conn:
        print("\n" + "="*50)
        print("🔍 EXECUTANDO SANITY CHECKS")
        print("="*50)

        for title, sql in queries.items():
            print(f"\n--- {title} ---")
            df = pd.read_sql(text(sql), conn)
            if df.empty:
                print("Nenhum registro encontrado.")
            else:
                print(df.to_string(index=False))

        print("\n" + "="*50)

if __name__ == "__main__":
    main()
