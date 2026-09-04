# Genomic Selection in Papaya with Bayesian Regression, GBLUP, and RR-BLUP

[English](#english) | [Português](#português)

**Tutorial website:** <https://wevertongomescosta.github.io/Bayesian-ridge-regression-papaya/>

---

## English

### Purpose

This repository contains a bilingual `workflowr` tutorial for genomic prediction and selection in papaya using multi-allelic SSR markers. It documents the complete analytical sequence from source-data inspection and quality control to genomic matrices, cross-validation, model fitting, diagnostics, model comparison, and exploratory candidate prioritization.

The analytical dataset contains 150 individuals, 34 retained SSR loci expanded into 72 allele-dosage columns, and 10 production and fruit-quality traits. Family is the only categorical fixed effect used in the prediction models.

Seven genomic prediction methods are compared: RR-BLUP/BRR, BayesA, BayesB, BayesB2, BayesC, Bayesian Lasso, and GBLUP.

### Tutorial modules

The modules are intended to be read in sequence because each stage creates the objects used by the next one.

1. **Data preprocessing and diagnostics** — reads and aligns genotype and phenotype data, handles SSR missing values, applies locus quality control, and summarizes phenotype diagnostics.
2. **Matrix construction and diagnostics** — converts multi-allelic SSR genotypes to allele dosages, constructs `X`, `M`, and `G`, and defines five family-stratified cross-validation folds.
3. **Model fitting and MCMC diagnostics** — specifies the seven genomic prediction methods in BGLR and documents the cross-validation fitting procedure and MCMC diagnostics. The complete fitting code is visible, but computationally intensive fitting chunks are not executed automatically during routine website rendering.
4. **Result derivation and model selection** — derives pooled OOF predictive metrics, DIC-based support measures, trait-specific method selection, cross-fitted genomic values, and exploratory candidate rankings.
5. **Results presentation** — consolidates the main comparative tables, diagnostics, rankings, recurrence summaries, and figures produced by the preceding modules.

### Validation scope

The five-fold cross-validation is stratified by family. With 150 individuals, each fold contains 30 validation individuals and 120 training individuals, and every individual is evaluated once out of fold.

This design evaluates prediction within the represented breeding population. Genotype-derived matrices are constructed from the aligned panel of 150 genotyped candidates, while validation phenotypes are masked during each fit. The OOF genomic values are therefore cross-fitted predictions rather than final breeding values from a full-data refit.

Candidate rankings are exploratory proportional prioritizations constructed only for traits with positive pooled OOF correlation, selecting the top 20% of candidates within each eligible trait. A positive OOF correlation alone is not treated as demonstrated predictive utility when its corresponding significance assessment remains weak.

The full scientific scope and interpretation boundaries are documented on the tutorial [About](https://wevertongomescosta.github.io/Bayesian-ridge-regression-papaya/about.html) page.

### Repository structure

- `analysis/`: bilingual `workflowr` source pages for the site and Modules 01--05;
- `data/`: local canonical source workbooks, excluded from Git, plus the versioned data contract in `data/README.md`;
- `docs/`: rendered tutorial website tracked by Git;
- `output/`: locally generated analytical objects, diagnostics, tables, and figures; generated artifacts are ignored by default, while a defined subset of M04 result tables is versioned;
- `renv.lock` and `renv/`: metadata for the reproducible R environment;
- `.github/workflows/`: lightweight repository-integrity CI that validates the tracked project structure without requiring local workbooks or rerunning the 350 model fits.

### Reproducibility

The repository supports two distinct reproducibility tasks.

#### Inspect the validated analysis

The rendered `docs/` site is versioned in Git and published through GitHub Pages. A fresh clone is sufficient to inspect the validated tutorial, code, tables, and rendered figures committed to the repository. The M04 result tables versioned under `output/results/m04/` provide a machine-readable subset of the final results.

#### Reconstruct the analytical workflow

A fresh clone **cannot by itself rerun the complete analysis from raw inputs**. The canonical Excel workbooks are intentionally excluded from Git, as are generated `.rds` objects, most generated CSV files, and native BGLR chain files (`*.dat`/`*.bin`).

To reconstruct the analysis:

1. obtain the two canonical workbooks from the project data provider/author;
2. place them in `data/` using the canonical filenames documented in [`data/README.md`](data/README.md);
3. verify their SHA-256 hashes;
4. restore the recorded R environment with `renv::restore()` and inspect it with `renv::status()`;
5. execute Modules 01 and 02;
6. deliberately execute the computationally intensive fitting blocks documented in Module 03;
7. regenerate the downstream outputs consumed by Modules 04 and 05.

Routine `workflowr` rendering is not a substitute for full computational reconstruction because downstream pages depend on persisted objects and chain files that are deliberately excluded from Git.

### Data and methodological reference

The canonical source workbooks are kept locally in `data/`. Their provenance, original filenames, canonical project filenames, SHA-256 hashes, expected layout, and alignment invariants are documented in [`data/README.md`](data/README.md). The repository does not currently provide a public download URL for those workbooks.

The comparative analytical structure was informed by:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

### Citation and license

Project citation metadata are provided in [`CITATION.cff`](CITATION.cff). Except where otherwise indicated, original project materials are distributed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license; see [`LICENSE.md`](LICENSE.md) and the tutorial [License](https://wevertongomescosta.github.io/Bayesian-ridge-regression-papaya/license.html) page. Source datasets and third-party materials are not relicensed by this project.

---

## Português

### Objetivo

Este repositório contém um tutorial bilíngue em `workflowr` para predição e seleção genômica em mamoeiro utilizando marcadores SSR multialélicos. Ele documenta toda a sequência analítica, desde a inspeção e o controle de qualidade dos dados-fonte até a construção das matrizes genômicas, validação cruzada, ajuste dos modelos, diagnósticos, comparação dos métodos e priorização exploratória de candidatos.

O conjunto analítico contém 150 indivíduos, 34 locos SSR mantidos e expandidos em 72 colunas de dosagem alélica e 10 características de produção e qualidade dos frutos. Família é o único efeito fixo categórico utilizado nos modelos de predição.

Sete métodos de predição genômica são comparados: RR-BLUP/BRR, BayesA, BayesB, BayesB2, BayesC, Lasso Bayesiano e GBLUP.

### Módulos do tutorial

Os módulos devem ser lidos em sequência, pois cada etapa cria os objetos utilizados pela seguinte.

1. **Pré-processamento e diagnóstico dos dados** — lê e alinha os dados genotípicos e fenotípicos, trata valores ausentes dos SSR, aplica o controle de qualidade dos locos e resume os diagnósticos fenotípicos.
2. **Construção e diagnóstico das matrizes** — converte genótipos SSR multialélicos em dosagens alélicas, constrói `X`, `M` e `G` e define cinco folds de validação cruzada estratificados por família.
3. **Ajuste dos modelos e diagnósticos MCMC** — especifica os sete métodos de predição genômica no BGLR e documenta o procedimento de ajuste em validação cruzada e os diagnósticos MCMC. O código completo de ajuste permanece visível, mas os chunks computacionalmente intensivos não são executados automaticamente durante a renderização rotineira do site.
4. **Derivação dos resultados e seleção dos modelos** — deriva métricas preditivas OOF agregadas, medidas de suporte baseadas em DIC, seleção do método por característica, valores genômicos cross-fitted e rankings exploratórios de candidatos.
5. **Apresentação dos resultados** — consolida as principais tabelas comparativas, diagnósticos, rankings, resumos de recorrência e figuras produzidos pelos módulos anteriores.

### Escopo da validação

A validação cruzada em cinco folds é estratificada por família. Com 150 indivíduos, cada fold contém 30 indivíduos de validação e 120 de treinamento, e cada indivíduo é avaliado uma única vez fora do fold.

Esse desenho avalia a predição dentro da população de melhoramento representada. As matrizes derivadas dos genótipos são construídas a partir do painel alinhado de 150 candidatos genotipados, enquanto os fenótipos dos indivíduos de validação são mascarados em cada ajuste. Os valores genômicos OOF são, portanto, predições cross-fitted, e não valores genéticos finais provenientes de um reajuste com todos os dados.

Os rankings de candidatos são priorizações proporcionais exploratórias construídas somente para características com correlação OOF agregada positiva, selecionando os 20% superiores dos candidatos em cada característica elegível. Uma correlação OOF positiva, isoladamente, não é tratada como utilidade preditiva demonstrada quando sua avaliação de significância correspondente permanece fraca.

O escopo científico completo e os limites de interpretação são documentados na página [Sobre](https://wevertongomescosta.github.io/Bayesian-ridge-regression-papaya/about.html) do tutorial.

### Estrutura do repositório

- `analysis/`: páginas-fonte bilíngues do `workflowr` para o site e os Módulos 01--05;
- `data/`: planilhas-fonte canônicas mantidas localmente e excluídas do Git, além do contrato versionado em `data/README.md`;
- `docs/`: site tutorial renderizado e versionado no Git;
- `output/`: objetos analíticos, diagnósticos, tabelas e figuras produzidos localmente; os artefatos gerados são ignorados por padrão, enquanto um subconjunto definido das tabelas de resultados do M04 é versionado;
- `renv.lock` e `renv/`: metadados do ambiente R reprodutível;
- `.github/workflows/`: CI leve de integridade do repositório, executado sem exigir as planilhas locais nem refazer os 350 ajustes.

### Reprodutibilidade

O repositório contempla duas tarefas distintas de reprodutibilidade.

#### Inspecionar a análise validada

O site renderizado em `docs/` é versionado no Git e publicado pelo GitHub Pages. Um clone novo é suficiente para inspecionar o tutorial validado, o código, as tabelas e as figuras renderizadas que foram commitadas. As tabelas de resultados do M04 versionadas em `output/results/m04/` fornecem um subconjunto legível por máquina dos resultados finais.

#### Reconstruir o fluxo analítico

Um clone novo **não consegue, sozinho, refazer toda a análise a partir dos dados brutos**. As planilhas Excel canônicas são intencionalmente excluídas do Git, assim como os objetos `.rds` gerados, a maior parte dos CSV gerados e as cadeias nativas do BGLR (`*.dat`/`*.bin`).

Para reconstruir a análise:

1. obtenha as duas planilhas canônicas com o responsável/provedor dos dados do projeto;
2. coloque-as em `data/` com os nomes canônicos documentados em [`data/README.md`](data/README.md);
3. valide seus hashes SHA-256;
4. restaure o ambiente R registrado com `renv::restore()` e inspecione-o com `renv::status()`;
5. execute os Módulos 01 e 02;
6. execute deliberadamente os blocos computacionalmente intensivos documentados no Módulo 03;
7. regenere as saídas posteriores consumidas pelos Módulos 04 e 05.

A renderização rotineira com `workflowr` não substitui a reconstrução computacional completa, pois as páginas posteriores dependem de objetos persistidos e cadeias que são deliberadamente excluídos do Git.

### Dados e referência metodológica

As planilhas-fonte canônicas são mantidas localmente em `data/`. Sua proveniência, nomes originais, nomes canônicos no projeto, hashes SHA-256, estrutura esperada e invariantes de alinhamento estão documentados em [`data/README.md`](data/README.md). O repositório não disponibiliza atualmente uma URL pública para download dessas planilhas.

A estrutura comparativa das análises foi orientada por:

Silva, F. A. et al. (2021). Bayesian ridge regression shows the best fit for SSR markers in *Psidium guajava* among Bayesian models. *Scientific Reports*, 11, 13639. <https://doi.org/10.1038/s41598-021-93120-z>.

### Citação e licença

Os metadados para citação do projeto estão em [`CITATION.cff`](CITATION.cff). Salvo indicação diferente, os materiais originais do projeto são distribuídos sob a licença Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0 Internacional; consulte [`LICENSE.md`](LICENSE.md) e a página [Licença](https://wevertongomescosta.github.io/Bayesian-ridge-regression-papaya/license.html) do tutorial. Os dados-fonte e materiais de terceiros não são relicenciados por este projeto.

---

## Contact / Contato

**Weverton Gomes da Costa**<br>
Postdoctoral Researcher / Pesquisador Pós-Doutoral<br>
Department of Statistics / Departamento de Estatística<br>
Federal University of Viçosa / Universidade Federal de Viçosa<br>
[weverton.costa@ufv.br](mailto:weverton.costa@ufv.br)
