from src.paths import validate_data_root, ensure_dirs

def bootstrap() -> None:
    """
    Executa validações iniciais e garante que a estrutura de diretórios existe.
    Deve ser chamado no início do main() de cada script executável.
    """
    validate_data_root()
    ensure_dirs()
