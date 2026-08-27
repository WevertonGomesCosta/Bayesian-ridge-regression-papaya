# Genomic Selection in Papaya with Bayesian Regression, GBLUP, and RR-BLUP

[English](#english) | [Português](#português)

**Tutorial website:** <https://wevertongomescosta.github.io/Bayesian-ridge-regression-papaya/>

---

## English

### Purpose

This repository contains a bilingual and reproducible `workflowr` tutorial for genomic prediction and selection in papaya using multi-allelic SSR markers. The tutorial is organized to guide the reader from source-data inspection and quality control to genomic matrices, cross-validation, model fitting, diagnostics, model comparison, and exploratory candidate prioritization.

The analytical dataset contains 150 individuals, 34 retained SSR loci expanded into 72 allele-dosage columns, and 10 production and fruit-quality traits. Family is included as the only categorical fixed effect; block is removed during preprocessing and is not used in the prediction models.

Seven genomic prediction methods are compared: RR-BLUP/BRR, BayesA, BayesB, BayesB2, BayesC, Bayesian Lasso, and GBLUP.

### How to follow the tutorial

The modules are intended to be read in sequence because each stage creates the objects used by the next one. Each page explains the purpose of the step before the corresponding code, documents methodological parameters and diagnostic thresholds, and uses short comments inside longer code blocks to make the analytical logic easier to follow.

1. **Data preprocessing and diagnostics** — reads and aligns genotype and phenotype data, handles SSR missing values, applies locus quality control, and summarizes phenotype diagnostics.
2. **Matrix construction and diagnostics** — converts multi-allelic SSR genotypes to allele dosages, constructs `X`, `M`, and `G`, and defines five family-stratified cross-validation folds.
3. **Model fitting and MCMC diagnostics** — specifies the seven genomic prediction methods in BGLR, defines the cross-validation fitting procedure, and documents posterior diagnostics. The complete fitting code is visible, while computationally intensive fitting chunks are not executed automatically during routine website rendering.
4. **Result derivation and model selection** — derives pooled OOF predictive metrics, DIC-based support measures, trait-specific method selection, cross-fitted genomic values, and exploratory candidate rankings.
5. **Results presentation** — consolidates the main comparative tables, diagnostics, rankings, recurrence summaries, and figures produced by the preceding modules.

### Validation scope and interpretation

The five-fold cross-validation is stratified by family. With 150 individuals, each fold contains 30 validation individuals and 120 training individuals, and every individual is used once for OOF validation. This design evaluates prediction within the represented breeding population; it is not a leave-family-out assessment of entirely new families.

Genotype-derived matrices are constructed from the aligned genotyped candidate panel, whereas validation phenotypes are masked during each fit. Consequently, the OOF genomic values are cross-fitted predictions rather than final breeding values from a full-data refit. Candidate rankings are therefore presented as exploratory proportional prioritizations and are constructed only for traits with positive pooled OOF correlation, selecting the top 20% of candidates within each eligible trait. A positive OOF correlation alone is not treated as demonstrated predictive utility when its corresponding significance assessment remains weak.

### Repository structure

- `analysis/`: bilingual `workflowr` source pages for the site and Modules 01--05;
- `data/`: canonical source workbooks and the data contract;
- `docs/`: rendered tutorial website;
- `output/`: analytical objects, diagnostics, tables, and figures created by the workflow; this directory is ignored by Git;
- `renv.lock` and `renv/`: metadata for the reproducible R environment.

### Reproducing the workflow

Restore the recorded R environment before executing the tutorial:

```r
renv::restore()
renv::status()
```

Then inspect [`data/README.md`](data/README.md) for the source-data contract and follow Modules 01--05 in order. Routine website rendering reproduces the documented pages but does not automatically launch the computationally intensive model-fitting chunks in Module 03; a full refit requires those fitting steps to be executed intentionally as documented in that module.

### Data and references

The source workbooks are versioned in `data/` with portable filenames. Their original names, SHA-256 checksums, and alignment invariants are documented in [`data/README.md`](data/README.md).

The main methodological reference for the comparative analytical structure is:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

---

## Português

### Objetivo

Este repositório contém um tutorial bilíngue e reprodutível em `workflowr` para predição e seleção genômica em mamoeiro utilizando marcadores SSR multialélicos. O tutorial foi organizado para conduzir o leitor desde a inspeção e o controle de qualidade dos dados-fonte até a construção das matrizes genômicas, validação cruzada, ajuste dos modelos, diagnósticos, comparação dos métodos e priorização exploratória de candidatos.

O conjunto analítico contém 150 indivíduos, 34 locos SSR mantidos e expandidos em 72 colunas de dosagem alélica e 10 características de produção e qualidade dos frutos. Família é incluída como o único efeito fixo categórico; bloco é removido durante o pré-processamento e não é utilizado nos modelos de predição.

Sete métodos de predição genômica são comparados: RR-BLUP/BRR, BayesA, BayesB, BayesB2, BayesC, Lasso Bayesiano e GBLUP.

### Como acompanhar o tutorial

Os módulos devem ser lidos em sequência, pois cada etapa cria os objetos utilizados pela seguinte. Cada página explica o objetivo da etapa antes do código correspondente, documenta parâmetros metodológicos e limiares diagnósticos e utiliza comentários curtos dentro de blocos maiores para tornar a lógica analítica mais fácil de acompanhar.

1. **Pré-processamento e diagnóstico dos dados** — lê e alinha os dados genotípicos e fenotípicos, trata valores ausentes dos SSR, aplica o controle de qualidade dos locos e resume os diagnósticos fenotípicos.
2. **Construção e diagnóstico das matrizes** — converte genótipos SSR multialélicos em dosagens alélicas, constrói `X`, `M` e `G` e define cinco folds de validação cruzada estratificados por família.
3. **Ajuste dos modelos e diagnósticos MCMC** — especifica os sete métodos de predição genômica no BGLR, define o procedimento de ajuste em validação cruzada e documenta os diagnósticos posteriores. O código completo de ajuste permanece visível, enquanto os chunks computacionalmente intensivos não são executados automaticamente durante a renderização rotineira do site.
4. **Derivação dos resultados e seleção dos modelos** — deriva métricas preditivas OOF agregadas, medidas de suporte baseadas em DIC, seleção do método por característica, valores genômicos cross-fitted e rankings exploratórios de candidatos.
5. **Apresentação dos resultados** — consolida as principais tabelas comparativas, diagnósticos, rankings, resumos de recorrência e figuras produzidos pelos módulos anteriores.

### Escopo da validação e interpretação

A validação cruzada em cinco folds é estratificada por família. Com 150 indivíduos, cada fold contém 30 indivíduos de validação e 120 de treinamento, e cada indivíduo participa uma única vez da avaliação OOF. Esse desenho avalia a predição dentro da população de melhoramento representada; não constitui uma avaliação leave-family-out de famílias inteiramente novas.

As matrizes derivadas dos genótipos são construídas a partir do painel alinhado de candidatos genotipados, enquanto os fenótipos de validação são mascarados em cada ajuste. Consequentemente, os valores genômicos OOF são predições cross-fitted, e não valores genéticos finais provenientes de um reajuste com todos os dados. Os rankings de candidatos são, portanto, apresentados como priorizações proporcionais exploratórias e são construídos somente para características com correlação OOF agregada positiva, selecionando os 20% superiores dos candidatos em cada característica elegível. Uma correlação OOF positiva, isoladamente, não é tratada como utilidade preditiva demonstrada quando sua avaliação de significância correspondente permanece fraca.

### Estrutura do repositório

- `analysis/`: páginas-fonte bilíngues do `workflowr` para o site e os Módulos 01--05;
- `data/`: planilhas-fonte canônicas e contrato dos dados;
- `docs/`: site tutorial renderizado;
- `output/`: objetos analíticos, diagnósticos, tabelas e figuras produzidos pelo fluxo; esse diretório é ignorado pelo Git;
- `renv.lock` e `renv/`: metadados do ambiente R reprodutível.

### Reprodução do fluxo

Restaure o ambiente R registrado antes de executar o tutorial:

```r
renv::restore()
renv::status()
```

Em seguida, consulte [`data/README.md`](data/README.md) para o contrato dos dados-fonte e siga os Módulos 01--05 na ordem. A renderização rotineira do site reproduz as páginas documentadas, mas não inicia automaticamente os chunks computacionalmente intensivos de ajuste do Módulo 03; uma reprodução completa dos ajustes exige a execução intencional dessas etapas conforme documentado no próprio módulo.

### Dados e referências

As planilhas-fonte são versionadas em `data/` com nomes portáveis. Seus nomes originais, hashes SHA-256 e invariantes de alinhamento estão documentados em [`data/README.md`](data/README.md).

A principal referência metodológica para a estrutura comparativa das análises é:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

### Contact / Contato

**Weverton Gomes da Costa**<br>
Postdoctoral Researcher / Pesquisador Pós-Doutoral<br>
Department of Statistics / Departamento de Estatística<br>
Federal University of Viçosa / Universidade Federal de Viçosa<br>
[weverton.costa@ufv.br](mailto:weverton.costa@ufv.br)