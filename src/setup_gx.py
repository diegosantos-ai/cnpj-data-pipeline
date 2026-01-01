import great_expectations as gx
import great_expectations.expectations as gxe
import logging
from src.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("GX_Setup")

def main():
    logger.info("🔧 Inicializando configuração do Great Expectations (v1.0+)...")
    
    context = gx.get_context(project_root_dir=".")
    
    # 1. Configurar Data Source (Postgres)
    datasource_name = "cnpj_postgres"
    try:
        datasource = context.data_sources.get(datasource_name)
        logger.info(f"✅ Data Source '{datasource_name}' já existe.")
    except KeyError:
        logger.info(f"🛠️ Criando Data Source '{datasource_name}'...")
        datasource = context.data_sources.add_postgres(
            name=datasource_name,
            connection_string=settings.sqlalchemy_url
        )
    
    # 2. Configurações por tabela
    config_map = {
        "empresas": {
            "table": "empresas",
            "expectations": [
                gxe.ExpectTableRowCountToBeBetween(min_value=1),
                gxe.ExpectColumnValuesToBeUnique(column="cnpj_basico"),
                gxe.ExpectColumnValuesToNotBeNull(column="cnpj_basico")
            ]
        },
        "estabelecimentos": {
            "table": "estabelecimentos",
            "expectations": [
                gxe.ExpectTableRowCountToBeBetween(min_value=1),
                gxe.ExpectColumnValuesToNotBeNull(column="cnpj_basico"),
                gxe.ExpectColumnValuesToNotBeNull(column="cnpj_ordem")
            ]
        },
        "socios": {
            "table": "socios",
            "expectations": [
                gxe.ExpectTableRowCountToBeBetween(min_value=1),
                gxe.ExpectColumnValuesToNotBeNull(column="cnpj_basico")
            ]
        }
    }

    validation_definitions = []

    for table_id, config in config_map.items():
        suite_name = f"suite_{table_id}"
        asset_name = f"table_{table_id}"
        val_def_name = f"validation_{table_id}"
        batch_def_name = f"batch_{table_id}"
        
        # A. Asset
        try:
            asset = datasource.get_asset(asset_name)
        except LookupError:
            logger.info(f"➕ Adicionando asset '{asset_name}'...")
            asset = datasource.add_table_asset(name=asset_name, table_name=config["table"])

        # B. Batch Definition
        try:
            batch_def = asset.get_batch_definition(batch_def_name)
        except KeyError:
            logger.info(f"📦 Criando Batch Definition '{batch_def_name}'...")
            # Corrigido para add_batch_definition_whole_table
            batch_def = asset.add_batch_definition_whole_table(batch_def_name)

        # C. Suite
        logger.info(f"📋 Configurando suite '{suite_name}'...")
        suite = gx.ExpectationSuite(name=suite_name)
        for exp in config["expectations"]:
            suite.add_expectation(exp)
        context.suites.add_or_update(suite)

        # D. Validation Definition
        logger.info(f"📑 Criando definição de validação '{val_def_name}'...")
        validation_def = gx.ValidationDefinition(
            name=val_def_name,
            data=batch_def,
            suite=suite
        )
        context.validation_definitions.add_or_update(validation_def)
        validation_definitions.append(validation_def)

    # 3. Criar Checkpoint
    checkpoint_name = "checkpoint_full_validation"
    logger.info(f"🏁 Criando Checkpoint '{checkpoint_name}'...")
    
    checkpoint = gx.Checkpoint(
        name=checkpoint_name,
        validation_definitions=validation_definitions,
        result_format="SUMMARY"
    )
    context.checkpoints.add_or_update(checkpoint)

    logger.info("🎉 Configuração do GX 1.0 concluída com sucesso!")

if __name__ == "__main__":
    main()