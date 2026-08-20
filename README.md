# Genomic Selection in Papaya with Bayesian Regression, GBLUP, and RR-BLUP

[English](#english) | [Português](#português)

---

## English

### Overview

This repository contains a bilingual and reproducible `workflowr` tutorial for genomic prediction and selection in papaya using multi-allelic SSR markers.

The validated analytical dataset contains 150 individuals, 34 retained SSR loci expanded into 72 allele-dosage columns, and 10 production and fruit-quality traits. Family is included as the only categorical fixed effect; block is removed during preprocessing and is not used in the models.

Seven genomic prediction methods are compared: RR-BLUP/BRR, BayesA, BayesB, BayesB2, BayesC, Bayesian Lasso, and GBLUP.

### Tutorial workflow

The website is organized into five bilingual modules:

1. **Data preprocessing and diagnostics** — reading, alignment, missing data, SSR quality control, phenotype summaries, and descriptive diagnostics.
2. **Matrix construction and diagnostics** — allele-dosage coding, construction of `X`, `M`, and `G`, and definition of the five family-stratified folds.
3. **Model fitting and MCMC diagnostics** — fitting the seven genomic prediction methods with BGLR and summarizing posterior diagnostics.
4. **Derivation and model selection** — OOF predictive performance, DIC-based comparison, model selection by trait, OOF genomic values, and trait-specific rankings.
5. **Results presentation** — presentation of the final tables and figures used as the analytical basis for the manuscript.

### Repository structure

- `analysis/`: bilingual workflowr source pages for the site and Modules 01--05;
- `data/`: canonical source workbooks and the data contract;
- `docs/`: generated website;
- `output/`: local analytical objects, checkpoints, diagnostics, tables, and figures;
- `renv.lock` and `renv/`: reproducible R environment metadata.

The detailed analytical contract, including fixed effects, matrix construction,
cross-validation, fitting, selection, and presentation rules, is documented in
the corresponding module pages.

### Reproduction

Restore the project environment:

```r
renv::restore()
renv::status()
```

Build the complete bilingual workflow:

```r
workflowr::wflow_build(
  c(
    "analysis/index.Rmd",
    "analysis/01_preprocessing_en.Rmd",
    "analysis/01_preprocessing_pt.Rmd",
    "analysis/02_matrices_en.Rmd",
    "analysis/02_matrices_pt.Rmd",
    "analysis/03_models_en.Rmd",
    "analysis/03_models_pt.Rmd",
    "analysis/04_results_en.Rmd",
    "analysis/04_results_pt.Rmd",
    "analysis/05_results_en.Rmd",
    "analysis/05_results_pt.Rmd",
    "analysis/about.Rmd",
    "analysis/license.Rmd"
  )
)
```

A complete reproduction from raw data can require the 350 model fits from Module 03. When validated checkpoints already exist locally, setting `PAPAYA_MAX_NEW_RUNS=0` prevents new model fits during a site rebuild.

### Data and references

The source workbooks are versioned in `data/` with portable filenames. Their original names, SHA-256 checksums, and the data contract are documented in [`data/README.md`](data/README.md).

The main reference for the analytical presentation is:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

---

## Português

### Visão geral

Este repositório contém um tutorial bilíngue e reprodutível em `workflowr` para predição e seleção genômica em mamoeiro utilizando marcadores SSR multialélicos.

O conjunto analítico validado contém 150 indivíduos, 34 locos SSR mantidos e expandidos em 72 colunas de dosagem alélica e 10 características de produção e qualidade dos frutos. Família é incluída como o único efeito fixo categórico; bloco é removido durante o pré-processamento e não é utilizado nos modelos.

Sete métodos de predição genômica são comparados: RR-BLUP/BRR, BayesA, BayesB, BayesB2, BayesC, Lasso Bayesiano e GBLUP.

### Fluxo do tutorial

O site está organizado em cinco módulos bilíngues:

1. **Pré-processamento e diagnóstico dos dados** — leitura, alinhamento, dados ausentes, controle de qualidade dos SSR, resumos fenotípicos e diagnósticos descritivos.
2. **Construção e diagnóstico das matrizes** — codificação das dosagens alélicas, construção de `X`, `M` e `G` e definição dos cinco folds estratificados por família.
3. **Ajuste dos modelos e diagnósticos MCMC** — ajuste dos sete métodos de predição genômica com BGLR e resumo dos diagnósticos posteriores.
4. **Derivação e seleção dos modelos** — desempenho preditivo OOF, comparação por DIC, seleção do método por característica, valores genômicos OOF e rankings específicos por característica.
5. **Apresentação dos resultados** — apresentação das tabelas e figuras finais utilizadas como base analítica para o manuscrito.

### Estrutura do repositório

- `analysis/`: páginas-fonte bilíngues do workflowr para o site e os Módulos 01--05;
- `data/`: planilhas-fonte canônicas e contrato dos dados;
- `docs/`: site gerado;
- `output/`: objetos analíticos locais, checkpoints, diagnósticos, tabelas e figuras;
- `renv.lock` e `renv/`: metadados do ambiente R reprodutível.

O contrato analítico detalhado, incluindo efeitos fixos, construção das matrizes,
validação cruzada, ajuste, seleção e apresentação, está documentado nas páginas
dos módulos correspondentes.

### Reprodução

Restaure o ambiente do projeto:

```r
renv::restore()
renv::status()
```

Construa o fluxo bilíngue completo:

```r
workflowr::wflow_build(
  c(
    "analysis/index.Rmd",
    "analysis/01_preprocessing_en.Rmd",
    "analysis/01_preprocessing_pt.Rmd",
    "analysis/02_matrices_en.Rmd",
    "analysis/02_matrices_pt.Rmd",
    "analysis/03_models_en.Rmd",
    "analysis/03_models_pt.Rmd",
    "analysis/04_results_en.Rmd",
    "analysis/04_results_pt.Rmd",
    "analysis/05_results_en.Rmd",
    "analysis/05_results_pt.Rmd",
    "analysis/about.Rmd",
    "analysis/license.Rmd"
  )
)
```

Uma reprodução completa a partir dos dados brutos pode exigir os 350 ajustes do Módulo 03. Quando os checkpoints validados já existem localmente, definir `PAPAYA_MAX_NEW_RUNS=0` impede novos ajustes durante uma reconstrução do site.

### Dados e referências

As planilhas-fonte são versionadas em `data/` com nomes portáveis. Seus nomes originais, hashes SHA-256 e o contrato dos dados estão documentados em [`data/README.md`](data/README.md).

A principal referência para a estrutura de apresentação das análises é:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

### Contact / Contato

**Weverton Gomes da Costa**<br>
Postdoctoral Researcher / Pesquisador Pós-Doutoral<br>
Department of Statistics / Departamento de Estatística<br>
Federal University of Viçosa / Universidade Federal de Viçosa<br>
[weverton.costa@ufv.br](mailto:weverton.costa@ufv.br)
