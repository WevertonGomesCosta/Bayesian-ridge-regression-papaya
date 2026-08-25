from pathlib import Path


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {n}")
    return text.replace(old, new, 1)


pt_path = Path("analysis/01_preprocessing_pt.Rmd")
pt = pt_path.read_text(encoding="utf-8")

pt = replace_once(
    pt,
    "Na aba `Genealex`, os identificadores dos indivíduos começam na quarta linha da segunda coluna e os nomes dos locos aparecem na terceira linha, em colunas alternadas a partir da terceira coluna. As expressões `4:(3 + n_individuals)` e `seq(3, 2 + 2 * n_loci, by = 2)` traduzem exatamente essa estrutura do arquivo de origem. Os identificadores são mantidos como texto — importante para valores alfanuméricos — e espaços externos são removidos com `trimws()`. Por fim, chamadas SSR ausentes codificadas como `-9` são convertidas em `NA` para que as funções de R as reconheçam como dados ausentes.",
    """Na aba `Genealex`, a posição de cada informação é definida explicitamente:

1. **Linhas dos indivíduos.** Os identificadores começam na linha 4 da segunda coluna. Como existem `n_individuals` indivíduos, as linhas são definidas por `individual_rows <- 4:(3 + n_individuals)`. O intervalo começa em 4 e termina em `3 + n_individuals`, incluindo exatamente uma linha para cada indivíduo.
2. **Colunas dos locos.** Os nomes dos locos estão na linha 3 e aparecem em colunas alternadas a partir da coluna 3. Essas posições são obtidas com `locus_columns <- seq(3, 2 + 2 * n_loci, by = 2)`. A função `seq()` começa em 3 e avança de duas em duas colunas até reunir os `n_loci` nomes.
3. **Identificadores dos indivíduos.** A expressão `genealex[[2]][individual_rows]` seleciona a segunda coluna apenas nas linhas definidas acima. Em seguida, `as.character()` preserva identificadores alfanuméricos e `trimws()` remove espaços antes ou depois do código: `ids <- trimws(as.character(genealex[[2]][individual_rows]))`.
4. **Nomes dos locos.** A expressão `genealex[3, locus_columns]` seleciona a terceira linha somente nas colunas dos locos. `unlist(..., use.names = FALSE)` transforma essa seleção em um vetor, e `trimws(as.character(...))` garante nomes em formato de texto sem espaços externos.
5. **Chamadas ausentes.** Depois de formar a matriz numérica de SSR, o código `ssr_raw[ssr_raw == -9] <- NA_real_` substitui o valor `-9`, usado no arquivo de origem para indicar ausência, pelo valor ausente padrão do R (`NA`).""",
    "pt Genealex explanation",
)

pt = replace_once(
    pt,
    "Em seguida, a tabela fenotípica é reordenada com `match()` de acordo com os identificadores da matriz SSR, de modo que cada linha fenotípica corresponda à mesma planta da linha genotípica. `FAM` é convertida em fator para representar a variável categórica que será usada no Módulo 02, enquanto as dez características são reunidas em uma matriz numérica.",
    """Em seguida, o alinhamento é feito com `match(ids, pheno_raw$IND)`. Para cada identificador presente em `ids`, `match()` retorna a posição correspondente em `pheno_raw$IND`. Essas posições são usadas diretamente em `pheno_raw[match(ids, pheno_raw$IND), required_columns]`, que reordena as linhas fenotípicas na mesma sequência da matriz SSR. Assim, a linha *i* dos fenótipos e a linha *i* dos genótipos passam a representar o mesmo indivíduo. Depois do alinhamento, `FAM` é convertida em fator para representar a variável categórica usada no Módulo 02, e as dez características são reunidas em uma matriz numérica.""",
    "pt match explanation",
)

pt = replace_once(
    pt,
    "Para cada loco são calculados a taxa de chamada — proporção dos 150 indivíduos com genótipo observado — e o número de classes genotípicas distintas. Um loco é mantido quando apresenta taxa de chamada igual ou superior a 0,90 (pelo menos 135 chamadas observadas) e pelo menos duas classes genotípicas. O segundo critério remove locos sem variação observável no painel, mesmo que sua taxa de chamada seja alta.",
    """Para cada loco, a taxa de chamada é calculada por `colMeans(!is.na(ssr_raw))`. Primeiro, `is.na(ssr_raw)` identifica as células ausentes; o operador `!` inverte o resultado, deixando `TRUE` para genótipos observados e `FALSE` para ausências. Como R trata `TRUE` como 1 e `FALSE` como 0 no cálculo da média, `colMeans()` fornece diretamente a proporção de indivíduos com genótipo observado em cada loco.

O número de classes genotípicas é calculado, para cada coluna `j`, por `length(unique(na.omit(ssr_raw[, j])))`: `na.omit()` remove as ausências, `unique()` mantém apenas os códigos genotípicos distintos e `length()` conta quantas classes foram observadas. Um loco é mantido quando a taxa de chamada é igual ou superior a 0,90 — pelo menos 135 dos 150 indivíduos — e quando existem pelo menos duas classes genotípicas. Esse segundo critério remove locos sem variação observável mesmo quando a taxa de chamada é alta.""",
    "pt marker QC explanation",
)

pt = replace_once(
    pt,
    "A quantidade de chamadas SSR disponíveis é resumida para cada indivíduo usando os 35 locos originais (`ssr_raw`). Esse diagnóstico descreve a completude do painel recebido antes do filtro por loco. Nenhum limiar de exclusão por completude é aplicado aos indivíduos; todos os 150 indivíduos alinhados são preservados para as etapas seguintes.",
    """A completude genotípica também é calculada por indivíduo usando os 35 locos originais (`ssr_raw`). A expressão `rowSums(!is.na(ssr_raw))` conta quantos locos possuem genótipo observado em cada indivíduo, enquanto `rowMeans(!is.na(ssr_raw))` divide implicitamente essa contagem pelo número de locos e fornece a proporção de chamadas disponíveis. Nenhum limiar de exclusão por completude é aplicado aos indivíduos; todos os 150 indivíduos alinhados são preservados para as etapas seguintes.""",
    "pt individual call rate explanation",
)

pt_path.write_text(pt, encoding="utf-8")

en_path = Path("analysis/01_preprocessing_en.Rmd")
en = en_path.read_text(encoding="utf-8")

en = replace_once(
    en,
    "In `Genealex`, individual identifiers begin on row 4 of column 2, whereas locus names occur on row 3 in alternating columns beginning with column 3. The expressions `4:(3 + n_individuals)` and `seq(3, 2 + 2 * n_loci, by = 2)` translate this source-file layout directly. Identifiers are kept as text — which preserves alphanumeric codes — and surrounding spaces are removed with `trimws()`. Finally, missing SSR calls coded as `-9` are converted to `NA` so that R functions recognize them as missing data.",
    """In `Genealex`, each piece of information is located explicitly:

1. **Individual rows.** Identifiers begin on row 4 of column 2. Because there are `n_individuals` individuals, their rows are defined by `individual_rows <- 4:(3 + n_individuals)`. The interval starts at 4 and ends at `3 + n_individuals`, including exactly one row per individual.
2. **Locus columns.** Locus names are stored on row 3 in alternating columns beginning with column 3. These positions are obtained with `locus_columns <- seq(3, 2 + 2 * n_loci, by = 2)`. The `seq()` function starts at column 3 and advances by two columns until all `n_loci` names are included.
3. **Individual identifiers.** The expression `genealex[[2]][individual_rows]` selects column 2 only at the rows defined above. Then `as.character()` preserves alphanumeric identifiers and `trimws()` removes spaces before or after the code: `ids <- trimws(as.character(genealex[[2]][individual_rows]))`.
4. **Locus names.** The expression `genealex[3, locus_columns]` selects row 3 only at the locus columns. `unlist(..., use.names = FALSE)` converts this selection to a vector, and `trimws(as.character(...))` ensures text names without surrounding spaces.
5. **Missing calls.** After the numerical SSR matrix is formed, `ssr_raw[ssr_raw == -9] <- NA_real_` replaces `-9`, the missing-value code in the source file, with R's standard missing value (`NA`).""",
    "en Genealex explanation",
)

en = replace_once(
    en,
    "The phenotype table is then reordered with `match()` according to the SSR identifiers so that every phenotype row corresponds to the same plant in the genotype matrix. `FAM` is converted to a factor to represent the categorical variable used in Module 02, while the ten traits are collected in a numeric matrix.",
    """Phenotypes are then aligned with `match(ids, pheno_raw$IND)`. For every identifier in `ids`, `match()` returns its corresponding position in `pheno_raw$IND`. Those positions are used directly in `pheno_raw[match(ids, pheno_raw$IND), required_columns]`, which reorders phenotype rows to the same sequence as the SSR matrix. Thus, phenotype row *i* and genotype row *i* represent the same individual. After alignment, `FAM` is converted to a factor to represent the categorical variable used in Module 02, and the ten traits are collected in a numeric matrix.""",
    "en match explanation",
)

en = replace_once(
    en,
    "For each locus, the call rate — the proportion of the 150 individuals with an observed genotype — and the number of distinct genotype classes are calculated. A locus is retained when its call rate is at least 0.90 (at least 135 observed calls) and at least two genotype classes are present. The second criterion removes loci with no observable variation in the panel even when their call rate is high.",
    """For each locus, call rate is calculated with `colMeans(!is.na(ssr_raw))`. First, `is.na(ssr_raw)` identifies missing cells; the `!` operator reverses the result, leaving `TRUE` for observed genotypes and `FALSE` for missing calls. Because R treats `TRUE` as 1 and `FALSE` as 0 when computing a mean, `colMeans()` directly returns the proportion of individuals with an observed genotype at each locus.

The number of genotype classes is calculated for each column `j` with `length(unique(na.omit(ssr_raw[, j])))`: `na.omit()` removes missing values, `unique()` retains distinct genotype codes, and `length()` counts the observed classes. A locus is retained when call rate is at least 0.90 — at least 135 of 150 individuals — and at least two genotype classes are present. The second criterion removes loci with no observable variation even when their call rate is high.""",
    "en marker QC explanation",
)

en = replace_once(
    en,
    "The amount of available SSR information is summarized for every individual using the 35 original loci (`ssr_raw`). This diagnostic describes completeness of the received panel before locus filtering. No individual-exclusion threshold based on completeness is applied; all 150 aligned individuals are preserved for subsequent stages.",
    """Genotype completeness is also calculated for each individual using the 35 original loci (`ssr_raw`). The expression `rowSums(!is.na(ssr_raw))` counts how many loci have an observed genotype for each individual, whereas `rowMeans(!is.na(ssr_raw))` implicitly divides that count by the number of loci and returns the proportion of available calls. No individual-exclusion threshold based on completeness is applied; all 150 aligned individuals are preserved for subsequent stages.""",
    "en individual call rate explanation",
)

en_path.write_text(en, encoding="utf-8")

print("PASS: M01 stepwise explanations prepared in PT/EN")
