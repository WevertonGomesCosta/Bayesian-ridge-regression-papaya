# Data contract

The project uses two canonical source workbooks. Their filenames were normalized
to make paths portable across operating systems. The workbooks are required
locally for a full reproduction of the analysis but are intentionally excluded
from Git; this versioned file preserves their provenance and validation
fingerprints.

The genotype workbook is the normalized version of the originally supplied SSR
workbook. The phenotype workbook is the **corrected canonical phenotype file**
currently used by the analytical workflow. The fingerprints below identify the
exact current canonical workbooks and are the authoritative provenance record
for verifying local copies.

| Project file | Provenance | Current SHA-256 |
|---|---|---|
| `papaya_ssr_genotypes.xlsx` | `Matriz numérica_SSR_populações.xlsx`; portable filename | `ffd891bc4b7599eaa38760f5e828e05a945198d8a68783f1493a8df575fe68a1` |
| `papaya_phenotypes_2024_2025.xlsx` | `Produção_mamão_24 e 25.xlsx`; corrected canonical phenotype workbook | `41c65e0a1f6992bebe633dce829e87575190cec8c12274d319001f73174e4bec` |

The SHA-256 values identify the exact canonical workbook bytes and allow local
copies to be checked against the files used by the validated workflow. The
workbooks themselves are not tracked in the current Git tree.

## Genotypes

- 150 genotyped individuals;
- 35 SSR loci;
- diploid genotype codes such as `11`, `12`, `22`, and `23`;
- missing calls coded as `-9`;
- 126 missing calls among 5,250 genotype-locus combinations (2.4%);
- individual identifiers read from column `Ind` of the `Genealex` sheet;
- `144B` is a valid identifier and must remain character data.

The first column of the `Genes` sheet is a sequential population-group index.
It is not used as the phenotypic family identifier. Rows are linked to
phenotypes through `Genealex!Ind`.

Four loci are triallelic (`P3K3256CC`, `P3K149C0`, `P3K4426C0`, and
`P3K6568CC`). Consequently, SSR genotypes are expanded into allele-dosage
columns rather than being forced into a biallelic SNP encoding. Locus
`P6K1129CC` contains a single observed genotype class and is removed as
non-informative.

## Phenotypes

The canonical phenotype table is the `Médias_IND_artigo` sheet. It contains
150 individuals and ten complete traits:

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

The source metadata reports evaluation from June 2024 through December 2025.
Fruit-quality variables were obtained from five fruits per selected plant.
The consolidated columns reproduce the canonical phenotype table used by the
current workflow; `PRODEF` is the sum of bananoid, carpelloid, and pentandric
defective-fruit production.

## Alignment invariants

- Genotype and phenotype tables each contain 150 unique identifiers.
- Their identifier sets and row order are identical after the M01 alignment.
- No phenotype is missing for the ten canonical traits.
- Block (`BL`) is present in the canonical source phenotype worksheet and is
  removed immediately when M01 reads the phenotype data; it is not propagated
  to metadata, `X`, cross-validation folds, or prediction models.
- Family (`FAM`) is retained and is the only categorical fixed effect used in
  the prediction models.
