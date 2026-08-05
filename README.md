# Genomic Selection in Papaya with Bayesian Regression, RR-BLUP, and GBLUP

[English](#english) | [Português](#português)

---

## English

### Overview

This repository contains a bilingual and reproducible `workflowr` project for
genomic prediction and selection in papaya using multi-allelic SSR markers.

The project analyzes:

- 150 papaya individuals;
- 35 original SSR loci;
- 34 SSR loci retained after global quality control;
- 72 retained allele-dosage columns;
- 10 production and fruit-quality traits;
- block and family as categorical fixed effects.

The alphanumeric individual identifier `144B` is preserved throughout the
alignment of genotype and phenotype records.

### Prediction methods

Eight genomic prediction methods are compared:

1. Bayesian ridge regression (`BRR`);
2. BayesA;
3. BayesB;
4. BayesB with the reference article's zero-effect probability convention
   (`pi = 1e-5`);
5. BayesC;
6. Bayesian Lasso (`BL`);
7. ridge-regression BLUP (`RR-BLUP`);
8. genomic BLUP (`GBLUP`).

In BGLR, `probIn` denotes the probability that a marker effect is non-zero.
Therefore, the special BayesB configuration uses
`probIn = 1 - 1e-5`.

### Data and matrix contract

The analytical matrices are constructed once using the complete aligned
dataset:

- `X`: fixed-effect matrix with intercept, block, and family;
- `M`: centered allele-dosage matrix;
- `G`: additive genomic relationship matrix derived from `M`.

The current validated dimensions are:

| Matrix | Dimensions | Rank |
|---|---:|---:|
| `X` | 150 × 19 | 19 |
| `M` | 150 × 72 | 38 |
| `G` | 150 × 150 | 38 |

The same `X`, `M`, and `G` are used in every cross-validation fold. Marker
filtering, allele coding, imputation, centering, allele-frequency calculation,
and genomic-matrix construction are not repeated within folds.

### Cross-validation contract

The project uses five deterministic folds stratified by family.

Each fold contains:

- 30 validation individuals;
- 120 training individuals;
- exactly 3 validation individuals from each of the 10 families.

Cross-validation changes only the phenotype vector. For each trait and fold,
the observed phenotype vector is copied and the 30 validation phenotypes are
replaced by `NA`. The original validation phenotypes are retained separately
for predictive assessment.

### Phenotypic audit

Phenotypic values at least four standard deviations from the corresponding
trait mean are highlighted as descriptive diagnostics. They remain exactly as
recorded in the source workbook and are not automatically corrected,
winsorized, transformed, or removed.

### Analytical workflow

The website is organized into four bilingual modules:

1. data preprocessing and audit;
2. construction and validation of `X`, `M`, `G`, and the five folds;
3. fitting of the eight genomic prediction methods;
4. predictive comparison, genomic values, and trait-specific rankings.

English and Portuguese pages contain equivalent analytical code and differ
only in explanatory language.

### Reproduction

Restore the project environment:

```r
renv::restore()
renv::status()
```

Build the completed modules directly with `workflowr`:

```r
workflowr::wflow_build(
  c(
    "analysis/01_preprocessing_en.Rmd",
    "analysis/01_preprocessing_pt.Rmd",
    "analysis/02_matrices_en.Rmd",
    "analysis/02_matrices_pt.Rmd"
  )
)
```

The model-fitting and results pages will be added to the same sequence after
modules 03 and 04 are completed and validated.

### Source data

The source workbooks are versioned in `data/` with portable filenames. Their
original names and SHA-256 checksums are documented in
[`data/README.md`](data/README.md).

### Reference article

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for
SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*,
11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

---

## Português

### Visão geral

Este repositório contém um projeto bilíngue e reprodutível em `workflowr` para
predição e seleção genômica em mamoeiro utilizando marcadores SSR
multialélicos.

O projeto analisa:

- 150 indivíduos de mamoeiro;
- 35 locos SSR originais;
- 34 locos SSR mantidos após o controle de qualidade global;
- 72 colunas de dosagem alélica mantidas;
- 10 características de produção e qualidade dos frutos;
- bloco e família como efeitos fixos categóricos.

O identificador alfanumérico `144B` é preservado durante todo o alinhamento dos
registros genotípicos e fenotípicos.

### Métodos de predição

Oito métodos de predição genômica são comparados:

1. regressão ridge Bayesiana (`BRR`);
2. BayesA;
3. BayesB;
4. BayesB com a convenção de probabilidade de efeito nulo do artigo de
   referência (`pi = 1e-5`);
5. BayesC;
6. Lasso Bayesiano (`BL`);
7. ridge-regression BLUP (`RR-BLUP`);
8. genomic BLUP (`GBLUP`).

No BGLR, `probIn` representa a probabilidade de o efeito do marcador ser
diferente de zero. Portanto, a configuração especial do BayesB utiliza
`probIn = 1 - 1e-5`.

### Contrato dos dados e das matrizes

As matrizes analíticas são construídas uma única vez com o conjunto completo
de dados alinhados:

- `X`: matriz de efeitos fixos com intercepto, bloco e família;
- `M`: matriz centralizada de dosagens alélicas;
- `G`: matriz de relacionamento genômico aditivo derivada de `M`.

As dimensões atualmente validadas são:

| Matriz | Dimensões | Posto |
|---|---:|---:|
| `X` | 150 × 19 | 19 |
| `M` | 150 × 72 | 38 |
| `G` | 150 × 150 | 38 |

As mesmas `X`, `M` e `G` são utilizadas em todos os folds. O filtro dos
marcadores, a codificação dos alelos, a imputação, a centralização, o cálculo
das frequências alélicas e a construção da matriz genômica não são repetidos
dentro dos folds.

### Contrato da validação cruzada

O projeto utiliza cinco folds determinísticos e estratificados por família.

Cada fold contém:

- 30 indivíduos de validação;
- 120 indivíduos de treinamento;
- exatamente 3 indivíduos de validação de cada uma das 10 famílias.

A validação cruzada altera somente o vetor fenotípico. Para cada característica
e fold, o vetor observado é copiado e os 30 fenótipos de validação são
substituídos por `NA`. Os fenótipos originais de validação são mantidos
separadamente para a avaliação preditiva.

### Auditoria fenotípica

Valores fenotípicos localizados a pelo menos quatro desvios-padrão da média da
respectiva característica são destacados como diagnósticos descritivos. Eles
permanecem exatamente como registrados na planilha original e não são
automaticamente corrigidos, winsorizados, transformados ou removidos.

### Fluxo analítico

O site está organizado em quatro módulos bilíngues:

1. pré-processamento e auditoria dos dados;
2. construção e validação de `X`, `M`, `G` e dos cinco folds;
3. ajuste dos oito métodos de predição genômica;
4. comparação preditiva, valores genômicos e rankings por característica.

As páginas em inglês e português apresentam códigos analíticos equivalentes e
diferem apenas no idioma das explicações.

### Reprodução

Restaure o ambiente do projeto:

```r
renv::restore()
renv::status()
```

Construa diretamente os módulos concluídos com o `workflowr`:

```r
workflowr::wflow_build(
  c(
    "analysis/01_preprocessing_en.Rmd",
    "analysis/01_preprocessing_pt.Rmd",
    "analysis/02_matrices_en.Rmd",
    "analysis/02_matrices_pt.Rmd"
  )
)
```

As páginas de ajuste dos modelos e resultados serão adicionadas à mesma
sequência depois que os módulos 03 e 04 forem concluídos e validados.

### Dados-fonte

As planilhas-fonte são versionadas em `data/` com nomes portáveis. Os nomes
originais e os hashes SHA-256 estão documentados em
[`data/README.md`](data/README.md).

### Artigo de referência

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for
SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*,
11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

### Contact / Contato

**Weverton Gomes da Costa**<br>
Postdoctoral Researcher / Pesquisador Pós-Doutoral<br>
Department of Statistics / Departamento de Estatística<br>
Federal University of Viçosa / Universidade Federal de Viçosa<br>
[weverton.costa@ufv.br](mailto:weverton.costa@ufv.br)
