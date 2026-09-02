# Data contract / Contrato dos dados

[English](#english) | [Português](#português)

## English

### Purpose and availability

The project uses two canonical source workbooks. Their filenames were normalized to make paths portable across operating systems. The workbooks are required locally for a full reconstruction of the analysis but are intentionally excluded from Git; this versioned file preserves their provenance, expected placement, and validation fingerprints.

The repository does **not** currently provide a public download URL for these workbooks. To reproduce the analysis from raw inputs, obtain the original files from the project data provider/author, verify that they correspond to the fingerprints below, and place them in the repository `data/` directory using the canonical project filenames.

### Canonical files

| Project file | Provenance | Current SHA-256 |
|---|---|---|
| `papaya_ssr_genotypes.xlsx` | `Matriz numérica_SSR_populações.xlsx`; portable filename | `ffd891bc4b7599eaa38760f5e828e05a945198d8a68783f1493a8df575fe68a1` |
| `papaya_phenotypes_2024_2025.xlsx` | `Produção_mamão_24 e 25.xlsx`; corrected canonical phenotype workbook | `41c65e0a1f6992bebe633dce829e87575190cec8c12274d319001f73174e4bec` |

The SHA-256 values identify the exact canonical workbook bytes used by the validated workflow. Files with different fingerprints should not be silently substituted.

Expected local layout:

```text
Bayesian-ridge-regression-papaya/
└── data/
    ├── README.md
    ├── papaya_ssr_genotypes.xlsx
    └── papaya_phenotypes_2024_2025.xlsx
```

On Git Bash, local copies can be checked with:

```bash
sha256sum data/papaya_ssr_genotypes.xlsx
sha256sum data/papaya_phenotypes_2024_2025.xlsx
```

The expected hashes are the values in the table above.

### Genotypes

- 150 genotyped individuals;
- 35 original SSR loci;
- diploid genotype codes such as `11`, `12`, `22`, and `23`;
- missing calls coded as `-9`;
- 126 missing calls among 5,250 genotype-locus combinations (2.4%);
- individual identifiers read from column `Ind` of the `Genealex` sheet;
- `144B` is a valid identifier and must remain character data.

The first column of the `Genes` sheet is a sequential population-group index. It is not used as the phenotypic family identifier. Rows are linked to phenotypes through `Genealex!Ind`.

Four loci are triallelic (`P3K3256CC`, `P3K149C0`, `P3K4426C0`, and `P3K6568CC`). Consequently, SSR genotypes are expanded into allele-dosage columns rather than being forced into a biallelic SNP encoding. Locus `P6K1129CC` contains a single observed genotype class and is removed as non-informative, leaving 34 retained loci and 72 allele-dosage columns.

### Phenotypes

The canonical phenotype table is the `Médias_IND_artigo` sheet. It contains 150 individuals and ten complete traits:

| Code | Description | Unit |
|---|---|---|
| `MMCOM` | Mean mass of commercial fruit | kg |
| `PRODCOM` | Production of commercial fruit | kg |
| `PRODEF` | Total production of defective fruit | kg |
| `CF` | Fruit length | cm |
| `DF` | Fruit diameter | cm |
| `DCI` | Internal-cavity diameter | cm |
| `EP` | Mean pulp thickness | cm |
| `FFC` | External fruit firmness | N |
| `FFP` | Internal pulp firmness | N |
| `SS` | Soluble solids | °Brix |

The source metadata reports evaluation from June 2024 through December 2025. Fruit-quality variables were obtained from five fruits per selected plant. The consolidated columns reproduce the canonical phenotype table used by the current workflow; `PRODEF` is the sum of bananoid, carpelloid, and pentandric defective-fruit production.

### Alignment invariants

- Genotype and phenotype tables each contain 150 unique identifiers.
- Their identifier sets and row order are identical after the M01 alignment.
- No phenotype is missing for the ten canonical traits.
- Block (`BL`) is present in the canonical source phenotype worksheet and is retained in `pheno_raw` during source inspection, then excluded when M01 defines the analytical columns; it is not propagated to metadata, `X`, cross-validation folds, or prediction models.
- Family (`FAM`) is retained and is the only categorical fixed effect used in the prediction models.

### What Git does and does not preserve

Git preserves this contract, the analytical source code, the rendered site, and a selected public subset of M04 result tables. The raw workbooks themselves are ignored by `.gitignore`. Generated `.rds`, most generated CSV files, and native BGLR chain files are also excluded. Therefore, a fresh clone can inspect the validated analysis but cannot reconstruct all downstream objects without first restoring the canonical workbooks and deliberately rerunning the required stages.

---

## Português

### Objetivo e disponibilidade

O projeto utiliza duas planilhas-fonte canônicas. Seus nomes foram normalizados para tornar os caminhos portáveis entre sistemas operacionais. As planilhas são necessárias localmente para uma reconstrução completa da análise, mas são intencionalmente excluídas do Git; este arquivo versionado preserva sua proveniência, localização esperada e fingerprints de validação.

O repositório **não disponibiliza atualmente uma URL pública de download** dessas planilhas. Para reproduzir a análise a partir dos dados brutos, obtenha os arquivos originais com o responsável/provedor dos dados do projeto, confirme que correspondem aos fingerprints abaixo e coloque-os no diretório `data/` usando os nomes canônicos do projeto.

### Arquivos canônicos

| Arquivo no projeto | Proveniência | SHA-256 atual |
|---|---|---|
| `papaya_ssr_genotypes.xlsx` | `Matriz numérica_SSR_populações.xlsx`; nome portável | `ffd891bc4b7599eaa38760f5e828e05a945198d8a68783f1493a8df575fe68a1` |
| `papaya_phenotypes_2024_2025.xlsx` | `Produção_mamão_24 e 25.xlsx`; planilha fenotípica canônica corrigida | `41c65e0a1f6992bebe633dce829e87575190cec8c12274d319001f73174e4bec` |

Os valores SHA-256 identificam exatamente os bytes das planilhas canônicas utilizadas pelo fluxo validado. Arquivos com fingerprints diferentes não devem ser substituídos silenciosamente.

Estrutura local esperada:

```text
Bayesian-ridge-regression-papaya/
└── data/
    ├── README.md
    ├── papaya_ssr_genotypes.xlsx
    └── papaya_phenotypes_2024_2025.xlsx
```

No Git Bash, as cópias locais podem ser verificadas com:

```bash
sha256sum data/papaya_ssr_genotypes.xlsx
sha256sum data/papaya_phenotypes_2024_2025.xlsx
```

Os hashes esperados são os valores apresentados na tabela acima.

### Genótipos

- 150 indivíduos genotipados;
- 35 locos SSR originais;
- códigos genotípicos diploides como `11`, `12`, `22` e `23`;
- chamadas ausentes codificadas como `-9`;
- 126 chamadas ausentes em 5.250 combinações indivíduo-loco (2,4%);
- identificadores dos indivíduos lidos da coluna `Ind` da planilha `Genealex`;
- `144B` é um identificador válido e deve permanecer como dado de caractere.

A primeira coluna da planilha `Genes` é um índice sequencial de grupo populacional. Ela não é utilizada como identificador fenotípico de família. As linhas são vinculadas aos fenótipos por `Genealex!Ind`.

Quatro locos são trialélicos (`P3K3256CC`, `P3K149C0`, `P3K4426C0` e `P3K6568CC`). Por isso, os genótipos SSR são expandidos em colunas de dosagem alélica em vez de serem forçados a uma codificação bialélica de SNP. O loco `P6K1129CC` contém uma única classe genotípica observada e é removido como não informativo, resultando em 34 locos mantidos e 72 colunas de dosagem alélica.

### Fenótipos

A tabela fenotípica canônica é a planilha `Médias_IND_artigo`. Ela contém 150 indivíduos e dez características completas:

| Código | Descrição | Unidade |
|---|---|---|
| `MMCOM` | Massa média de fruto comercial | kg |
| `PRODCOM` | Produção de fruto comercial | kg |
| `PRODEF` | Produção total de fruto defeituoso | kg |
| `CF` | Comprimento do fruto | cm |
| `DF` | Diâmetro do fruto | cm |
| `DCI` | Diâmetro da cavidade interna | cm |
| `EP` | Espessura média de polpa | cm |
| `FFC` | Firmeza externa do fruto | N |
| `FFP` | Firmeza interna da polpa | N |
| `SS` | Sólidos solúveis | °Brix |

Os metadados da fonte informam avaliação entre junho de 2024 e dezembro de 2025. As variáveis de qualidade dos frutos foram obtidas a partir de cinco frutos por planta selecionada. As colunas consolidadas reproduzem a tabela fenotípica canônica utilizada pelo fluxo atual; `PRODEF` é a soma da produção de frutos defeituosos bananoides, carpelóides e pentândricos.

### Invariantes de alinhamento

- As tabelas genotípica e fenotípica contêm 150 identificadores únicos cada.
- Seus conjuntos de identificadores e a ordem das linhas são idênticos após o alinhamento do M01.
- Não há fenótipos ausentes para as dez características canônicas.
- Bloco (`BL`) está presente na planilha fenotípica canônica e é mantido em `pheno_raw` durante a inspeção da fonte, mas é excluído quando o M01 define as colunas analíticas; ele não é propagado para metadados, `X`, folds de validação cruzada ou modelos de predição.
- Família (`FAM`) é mantida e constitui o único efeito fixo categórico utilizado nos modelos de predição.

### O que o Git preserva e o que não preserva

O Git preserva este contrato, o código-fonte analítico, o site renderizado e um subconjunto público selecionado das tabelas de resultados do M04. As planilhas brutas são ignoradas pelo `.gitignore`. Objetos `.rds` gerados, a maior parte dos CSV gerados e as cadeias nativas do BGLR também são excluídos. Portanto, um clone novo permite inspecionar a análise validada, mas não reconstruir todos os objetos posteriores sem primeiro restaurar as planilhas canônicas e executar deliberadamente as etapas necessárias.
