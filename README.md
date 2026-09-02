# Genomic Selection in Papaya with Bayesian Regression, GBLUP, and RR-BLUP

[English](#english) | [Português](#português)

**Tutorial website:** <https://wevertongomescosta.github.io/Bayesian-ridge-regression-papaya/>

---

## English

### Purpose

This repository contains a bilingual `workflowr` tutorial for genomic prediction and selection in papaya using multi-allelic SSR markers. The tutorial guides the reader from source-data inspection and quality control to genomic matrices, cross-validation, model fitting, diagnostics, model comparison, and exploratory candidate prioritization.

The analytical dataset contains 150 individuals, 34 retained SSR loci expanded into 72 allele-dosage columns, and 10 production and fruit-quality traits. Family is included as the only categorical fixed effect in the prediction models.

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

Genotype-derived matrices are constructed from the aligned genotyped candidate panel, whereas validation phenotypes are masked during each fit. Consequently, the OOF genomic values are cross-fitted predictions rather than final breeding values from a full-data refit. Candidate rankings are exploratory proportional prioritizations constructed only for traits with positive pooled OOF correlation, selecting the top 20% of candidates within each eligible trait. A positive OOF correlation alone is not treated as demonstrated predictive utility when its corresponding significance assessment remains weak.

### Repository structure

- `analysis/`: bilingual `workflowr` source pages for the site and Modules 01--05;
- `data/`: local canonical source workbooks, excluded from Git, plus the versioned data contract in `data/README.md`;
- `docs/`: rendered tutorial website tracked by Git;
- `output/`: locally generated analytical objects, diagnostics, tables, and figures; generated artifacts are ignored by default, while a defined public subset of M04 result tables is versioned;
- `renv.lock` and `renv/`: metadata for the reproducible R environment;
- `.github/workflows/`: lightweight repository-integrity CI that validates the tracked project structure without requiring private/local workbooks or rerunning the 350 model fits.

### Reproducibility modes

This repository supports two distinct forms of reproducibility and they should not be conflated.

#### 1. Read or inspect the validated analysis

The rendered `docs/` website is versioned in Git and published through GitHub Pages. A fresh clone is sufficient to inspect the validated tutorial, code, tables, and rendered figures that are committed to the repository.

The public M04 tables intentionally versioned under `output/results/m04/` provide a machine-readable subset of the final scientific results.

#### 2. Reconstruct the analytical workflow

A fresh clone **cannot by itself rerun the complete analysis from raw inputs**. The following inputs or generated intermediates are intentionally not distributed in Git:

- the two canonical Excel workbooks in `data/`;
- generated M01/M02/M03/M04 `.rds` objects and most generated CSV files;
- native BGLR chain files (`*.dat`/`*.bin`), including the fold-1 `mu` chains used by the illustrative M05 trace.

To reconstruct the analysis, first obtain the two canonical workbooks from the project data provider/author, place them in `data/` using the portable filenames documented in [`data/README.md`](data/README.md), and verify their SHA-256 fingerprints. The repository does not currently provide a public download URL for those workbooks.

Then restore the recorded R environment:

```r
renv::restore()
renv::status()
```

Execute Modules 01 and 02 in sequence to recreate preprocessing and matrix objects. Module 03 contains the complete code for the 350 trait × fold × method fits, but its computationally intensive fitting chunks are intentionally `eval=FALSE`; a full reconstruction therefore requires those fitting blocks to be run deliberately before the downstream persisted outputs are assembled. Modules 04 and 05 then consume those regenerated outputs.

Routine `workflowr` rendering should not be interpreted as a substitute for this full computational reconstruction: downstream pages require persisted objects or chain files that are deliberately excluded from Git.

### Data and references

The canonical source workbooks are kept locally in `data/` with portable filenames and are excluded from Git. Their original names, SHA-256 checksums, placement instructions, and alignment invariants are documented in [`data/README.md`](data/README.md).

The main methodological reference for the comparative analytical structure is:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

---

## Português

### Objetivo

Este repositório contém um tutorial bilíngue em `workflowr` para predição e seleção genômica em mamoeiro utilizando marcadores SSR multialélicos. O tutorial conduz o leitor desde a inspeção e o controle de qualidade dos dados-fonte até a construção das matrizes genômicas, validação cruzada, ajuste dos modelos, diagnósticos, comparação dos métodos e priorização exploratória de candidatos.

O conjunto analítico contém 150 indivíduos, 34 locos SSR mantidos e expandidos em 72 colunas de dosagem alélica e 10 características de produção e qualidade dos frutos. Família é incluída como o único efeito fixo categórico nos modelos de predição.

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

As matrizes derivadas dos genótipos são construídas a partir do painel alinhado de candidatos genotipados, enquanto os fenótipos de validação são mascarados em cada ajuste. Consequentemente, os valores genômicos OOF são predições cross-fitted, e não valores genéticos finais provenientes de um reajuste com todos os dados. Os rankings de candidatos são priorizações proporcionais exploratórias construídas somente para características com correlação OOF agregada positiva, selecionando os 20% superiores dos candidatos em cada característica elegível. Uma correlação OOF positiva, isoladamente, não é tratada como utilidade preditiva demonstrada quando sua avaliação de significância correspondente permanece fraca.

### Estrutura do repositório

- `analysis/`: páginas-fonte bilíngues do `workflowr` para o site e os Módulos 01--05;
- `data/`: planilhas-fonte canônicas mantidas localmente e excluídas do Git, além do contrato versionado em `data/README.md`;
- `docs/`: site tutorial renderizado e versionado no Git;
- `output/`: objetos analíticos, diagnósticos, tabelas e figuras produzidos localmente; os artefatos gerados são ignorados por padrão, enquanto um subconjunto público definido das tabelas finais do M04 é versionado;
- `renv.lock` e `renv/`: metadados do ambiente R reprodutível;
- `.github/workflows/`: CI leve de integridade do repositório, executado sem exigir os workbooks locais nem refazer os 350 ajustes.

### Modos de reprodutibilidade

Este repositório oferece duas formas distintas de reprodutibilidade, que não devem ser tratadas como equivalentes.

#### 1. Ler ou inspecionar a análise validada

O site renderizado em `docs/` é versionado no Git e publicado pelo GitHub Pages. Um clone novo é suficiente para inspecionar o tutorial validado, o código, as tabelas e as figuras renderizadas que foram commitadas.

As tabelas públicas do M04 intencionalmente versionadas em `output/results/m04/` fornecem um subconjunto legível por máquina dos resultados científicos finais.

#### 2. Reconstruir o fluxo analítico

Um clone novo **não consegue, sozinho, refazer toda a análise a partir dos dados brutos**. Os seguintes arquivos de entrada ou intermediários gerados são deliberadamente excluídos do Git:

- as duas planilhas Excel canônicas em `data/`;
- objetos `.rds` e a maior parte dos CSV gerados em M01/M02/M03/M04;
- cadeias nativas do BGLR (`*.dat`/`*.bin`), incluindo as cadeias `mu` do fold 1 utilizadas no trace ilustrativo do M05.

Para reconstruir a análise, obtenha primeiro as duas planilhas canônicas com o responsável/provedor dos dados do projeto, coloque-as em `data/` com os nomes portáveis documentados em [`data/README.md`](data/README.md) e valide seus hashes SHA-256. O repositório não disponibiliza atualmente uma URL pública para download dessas planilhas.

Depois, restaure o ambiente R registrado:

```r
renv::restore()
renv::status()
```

Execute os Módulos 01 e 02 em sequência para recriar os objetos de pré-processamento e matrizes. O Módulo 03 contém o código completo dos 350 ajustes característica × fold × método, mas seus chunks computacionalmente intensivos permanecem intencionalmente com `eval=FALSE`; uma reconstrução completa exige, portanto, executar deliberadamente esses blocos antes de consolidar as saídas persistidas. Os Módulos 04 e 05 consomem então os resultados regenerados.

A renderização rotineira com `workflowr` não deve ser interpretada como substituta dessa reconstrução computacional completa: as páginas posteriores dependem de objetos persistidos ou cadeias que são deliberadamente excluídos do Git.

### Dados e referências

As planilhas-fonte canônicas são mantidas localmente em `data/` com nomes portáveis e são excluídas do Git. Seus nomes originais, hashes SHA-256, instruções de posicionamento e invariantes de alinhamento estão documentados em [`data/README.md`](data/README.md).

A principal referência metodológica para a estrutura comparativa das análises é:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

### Contact / Contato

**Weverton Gomes da Costa**<br>
Postdoctoral Researcher / Pesquisador Pós-Doutoral<br>
Department of Statistics / Departamento de Estatística<br>
Federal University of Viçosa / Universidade Federal de Viçosa<br>
[weverton.costa@ufv.br](mailto:weverton.costa@ufv.br)
