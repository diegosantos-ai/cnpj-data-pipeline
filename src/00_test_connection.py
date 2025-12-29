import psycopg2
# CORRECAO AQUI: Adicionamos 'src.' antes de config
from src.config import settings

def test_db():
    print(f'--- Testando conexao com {settings.host}:{settings.port} ---')
    try:
        conn = psycopg2.connect(
            host=settings.host,
            port=settings.port,
            dbname=settings.name,
            user=settings.user,
            password=settings.password
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        res = cur.fetchone()
        
        print(f"✅ Conexão BEM-SUCEDIDA! O banco respondeu: {res[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ FALHA na conexão: {e}")

if __name__ == "__main__":
    test_db()
