-- Criação das tabelas para os Dados Abertos de CNPJ (Receita Federal)
-- Ordem das colunas segue estritamente o layout do arquivo CSV oficial

-- Drop tables para reset total
DROP TABLE IF EXISTS empresas;
DROP TABLE IF EXISTS estabelecimentos;
DROP TABLE IF EXISTS socios;

-- 1. TABELA EMPRESAS
CREATE TABLE empresas (
    cnpj_basico CHAR(8) NOT NULL,
    razao_social VARCHAR(255),
    natureza_juridica VARCHAR(4),
    qualificacao_responsavel VARCHAR(2),
    capital_social VARCHAR(255), -- Varchar para aceitar virgula do CSV
    porte_empresa VARCHAR(2),
    ente_federativo_responsavel VARCHAR(255)
);

-- 2. TABELA ESTABELECIMENTOS
CREATE TABLE estabelecimentos (
    cnpj_basico CHAR(8) NOT NULL,
    cnpj_ordem CHAR(4) NOT NULL,
    cnpj_dv CHAR(2) NOT NULL,
    identificador_matriz_filial CHAR(1),
    nome_fantasia VARCHAR(255),
    situacao_cadastral CHAR(2),
    data_situacao_cadastral VARCHAR(8), -- YYYYMMDD
    motivo_situacao_cadastral VARCHAR(4),
    nome_cidade_exterior VARCHAR(255),
    pais VARCHAR(3),
    data_inicio_atividade VARCHAR(8), -- YYYYMMDD
    cnae_fiscal_principal VARCHAR(7),
    cnae_fiscal_secundaria TEXT,
    tipo_logradouro VARCHAR(255),
    logradouro VARCHAR(255),
    numero VARCHAR(255), -- Aumentado para suportar "SEM NUMERO" etc
    complemento VARCHAR(255),
    bairro VARCHAR(255),
    cep VARCHAR(8),
    uf VARCHAR(2),
    municipio VARCHAR(4),
    ddd_1 VARCHAR(4),
    telefone_1 VARCHAR(20),
    ddd_2 VARCHAR(4),
    telefone_2 VARCHAR(20),
    ddd_fax VARCHAR(4),
    fax VARCHAR(20),
    correio_eletronico VARCHAR(255),
    situacao_especial VARCHAR(255),
    data_situacao_especial VARCHAR(8) -- YYYYMMDD
);

-- 3. TABELA SOCIOS
CREATE TABLE socios (
    cnpj_basico CHAR(8) NOT NULL,
    identificador_socio CHAR(1),
    nome_socio_razao_social VARCHAR(255),
    cpf_cnpj_socio VARCHAR(14),
    qualificacao_socio VARCHAR(2),
    data_entrada_sociedade VARCHAR(8), -- YYYYMMDD
    pais VARCHAR(3),
    representante_legal VARCHAR(11),
    nome_representante VARCHAR(255),
    qualificacao_representante_legal VARCHAR(2),
    faixa_etaria VARCHAR(1)
);