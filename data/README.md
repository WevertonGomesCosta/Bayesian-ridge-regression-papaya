# Data contract

The project uses two source workbooks. Their filenames were normalized to make
paths portable across operating systems; the workbook contents were not
altered.

| Project file | Uploaded source | SHA-256 |
|---|---|---|
| `papaya_ssr_genotypes.xlsx` | `Matriz numérica_SSR_populações.xlsx` | `ffd891bc4b7599eaa38760f5e828e05a945198d8a68783f1493a8df575fe68a1` |
| `papaya_phenotypes_2024_2025.xlsx` | `Produção_mamão_24 e 25.xlsx` | `5fbbc48ecd934f9fffda65d28db5bf1c9a7921d5a6bed9f04df043073f5b77ef` |

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
The consolidated columns reproduce the corresponding source columns exactly;
`PRODEF` is the sum of bananoid, carpelloid, and pentandric defective-fruit
production.

## Alignment invariants

- Genotype and phenotype tables each contain 150 unique identifiers.
- Their identifier sets and row order are identical.
- No phenotype is missing for the ten canonical traits.
- Block (`BL`) and family (`FAM`) are retained as categorical fixed effects.
