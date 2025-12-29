from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class DBConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "cnpjdb")
    user: str = os.getenv("DB_USER", "cnpj")
    password: str = os.getenv("DB_PASSWORD", "cnpj123")

    @property
    def sqlalchemy_url(self) -> str:
        # Retorna a string de conexao pronta para uso
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

# Cria uma instancia padrao para facilitar a importacao nos outros arquivos
settings = DBConfig()
