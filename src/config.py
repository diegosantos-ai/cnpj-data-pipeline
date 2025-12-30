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
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass(frozen=True)
class PipelineConfig:
    mode: str = os.getenv("PIPELINE_MODE", "full")  # full | sample
    sample_rows: int = int(os.getenv("SAMPLE_ROWS", "10000"))
    sample_files_per_type: int = int(os.getenv("SAMPLE_FILES_PER_TYPE", "1"))
    sample_seed: int = int(os.getenv("SAMPLE_SEED", "42"))
    sample_force: bool = os.getenv("SAMPLE_FORCE", "0") == "1"

settings = DBConfig()
pipeline_settings = PipelineConfig()