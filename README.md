# cnpj-data-pipeline

Pipeline de engenharia de dados para os **Dados Abertos de CNPJ da Receita Federal**, com foco em **governança, qualidade, reprodutibilidade e evolução controlada**.

O projeto demonstra a construção de um **sistema de dados batch governado**, partindo da ingestão até a camada analítica, com contratos explícitos, quality gate bloqueante e baseline operacional definida.

---

## 🧠 Método de Construção do Projeto

Este projeto foi desenvolvido seguindo um modelo estruturado de execução inspirado em um **Laboratório de Agentes**, utilizado para garantir clareza de responsabilidade, qualidade e controle evolutivo.

Papéis envolvidos no processo:

- **Orquestrador** — define escopo, fluxo e progressão de fases  
- **Execução Técnica** — implementa soluções técnicas  
- **QA** — valida, bloqueia e classifica prontidão  
- **Documentação** — fixa conhecimento validado  
- **Automação** — escala apenas o que está maduro  

Esse modelo orienta a execução, mas **o foco deste repositório é o sistema de dados CNPJ**.

---

## 📁 Estrutura Geral do Projeto

```text
cnpj-data-pipeline/
├── src/
│   ├── ingest/              # Scripts de ingestão e carga
│   ├── paths.py             # Resolução centralizada de paths (DATA_ROOT)
│   ├── runners/             # Runner operacional do pipeline
│   └── utils/               # Utilitários compartilhados
├── expectations/            # Suites do Great Expectations
├── analytics/               # SQL de promoção para schema analytics
├── docs/                    # Documentação adicional do laboratório
├── README.md
└── pyproject.toml
```

Os dados **não** fazem parte do repositório e residem fora do Git (ex.: HD externo), conforme contrato de armazenamento.

---

## 🚦 Fases do Projeto

### ✅ Fase 1 — Ingestão de Dados (ENCERRADA)

Escopo:

* Download dos dados públicos de CNPJ
* Extração controlada
* Carga inicial no banco
* Separação clara entre código e dados
* Runner operacional
* Execução reprodutível em modo SAMPLE

Status:

* Pipeline executável ponta a ponta
* Baseline de ingestão estabilizada

---

### ✅ Fase 2 — Arquitetura Analytics & Qualidade (ENCERRADA)

Escopo:

* Arquitetura em camadas (`raw`, `processed`, `analytics`)
* Schema dedicado `analytics`
* Promoção controlada `processed → analytics`
* Qualidade de dados formal com **Great Expectations**
* **Quality Gate bloqueante**
* Contratos explícitos (SAMPLE, QA)
* Evidências de execução e auditoria

Status:

* Sistema de dados governado e auditável
* Baseline evolutiva **v2.x** adotada
* Nenhum risco estrutural aberto

---

## 🏗️ Arquitetura de Dados

* **raw**: dados conforme origem, imutáveis
* **processed**: dados tratados tecnicamente
* **analytics**: dados promovidos para consumo, somente após aprovação do gate

A promoção para `analytics` ocorre **exclusivamente** após validação de qualidade.

---

## 🧪 Data Quality (Great Expectations)

A qualidade é tratada como **sistema**, não como checklist manual.

Implementação:

* Suites de expectativas *sample-first*
* Critérios binários (contagem, não nulos, unicidade)
* **Quality Gate bloqueante**
* Data Docs para auditoria local

Falha no gate **bloqueia** a promoção para `analytics`.

---

## 📜 Contratos

### Contrato de SAMPLE

* Subconjunto determinístico e reprodutível
* Utilizado para:

  * desenvolvimento
  * QA
  * regressão
* Não representa volume ou distribuição completa do dataset FULL

### Contrato de QA

* Gates bloqueantes
* Critérios objetivos
* Regressão obrigatória para qualquer incremento
* Nenhuma promoção sem aprovação explícita

---

## ▶️ Como Executar

### Pré-requisitos

* Python 3.10+
* PostgreSQL (local ou via Docker)
* Variável de ambiente `DATA_ROOT` apontando para o diretório de dados

### Execução (baseline operacional)

```bash
python -m src.runners.run_pipeline
```

Modos suportados:

* `SAMPLE` (baseline atual)
* `FULL` (preservado, não executado por padrão)

O runner atual é considerado o **baseline operacional** do sistema.

---

## 📌 Estado Atual do Sistema

* Pipeline rodando ponta a ponta
* Qualidade de dados formal e bloqueante
* Promoção segura para analytics
* Sistema auditável e reexecutável
* Execução viável no hardware disponível (modo SAMPLE)

Este estado representa o **mínimo aceitável** para qualquer evolução futura.

---

## 🏛️ Governança

* Fases só são encerradas após:

  * execução comprovada
  * validação do QA
  * fixação pela Documentação
* Incrementos futuros:

  * devem respeitar contratos
  * passam por regressão obrigatória
  * não reabrem fases encerradas
* Automação e escala só ocorrem sobre baselines validadas

---

## 📎 Observações Finais

Este projeto serve como:

* referência técnica do laboratório
* base de auditoria e reexecução
* ativo de portfólio em engenharia de dados

O foco não é volume, mas **maturidade arquitetural, governança e qualidade**.
