from src.paths import RAW_DIR, PROCESSED_DIR, PROJECT_ROOT

def main():
    print(f"--- Validação de Migração ---")
    print(f"RAW_DIR atual configurado: {RAW_DIR}")
    print(f"PROCESSED_DIR atual configurado: {PROCESSED_DIR}")
    
    # Valida D:
    raw_files = list(RAW_DIR.glob("*.zip"))
    processed_files = list(PROCESSED_DIR.glob("* ")) # Pega tudo
    
    print(f"\n[D:] Arquivos em RAW: {len(raw_files)}")
    print(f"[D:] Arquivos em PROCESSED: {len(processed_files)}")
    
    # Valida _old
    raw_old = PROJECT_ROOT / "data" / "raw_old"
    processed_old = PROJECT_ROOT / "data" / "processed_old"
    
    print(f"\n[OLD] Verificando pasta antiga {raw_old}...")
    if raw_old.exists():
        old_raw_files = list(raw_old.glob("*.zip"))
        print(f" -> Arquivos restantes em raw_old: {len(old_raw_files)}")
    else:
        print(" -> Pasta raw_old não existe.")

    print(f"\n[OLD] Verificando pasta antiga {processed_old}...")
    if processed_old.exists():
        old_proc_files = list(processed_old.glob("* "))
        print(f" -> Arquivos restantes em processed_old: {len(old_proc_files)}")
    else:
        print(" -> Pasta processed_old não existe.")
        
    if len(raw_files) > 0:
        print("\n✅ Validação SUCESSO: Arquivos detectados no drive D.")
    else:
        print("\n❌ Validação FALHA: Nenhum arquivo encontrado no drive D.")

if __name__ == "__main__":
    main()
