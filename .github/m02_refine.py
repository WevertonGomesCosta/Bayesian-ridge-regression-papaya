from pathlib import Path
import re


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 occurrence, found {n}")
    return text.replace(old, new, 1)


def refine_pt(text):
    text = replace_once(
        text,
        "O chunk oculto a seguir define apenas opções de renderização compartilhadas por esta página. Ele não carrega os objetos analíticos, não constrói matrizes e não interfere na validação cruzada.\n\n",
        "",
        "pt hidden setup prose",
    )
    text = replace_once(
        text,
        "Ao final do módulo, o leitor terá quatro componentes que serão reutilizados diretamente no Módulo 03: a matriz de efeitos fixos `X`, a matriz centralizada de marcadores `M`, a matriz de relacionamento genômico `G` e a tabela `cv_folds` que identifica o fold de validação de cada indivíduo. Os diagnósticos apresentados ao longo da página verificam se a codificação alélica, a centralização, o relacionamento genômico e a estratificação por família são coerentes com esse desenho.",
        "O módulo produz quatro componentes reutilizados diretamente no Módulo 03: a matriz de efeitos fixos `X`, a matriz centralizada de marcadores `M`, a matriz de relacionamento genômico `G` e a tabela `cv_folds`, que identifica o fold de validação de cada indivíduo. Os diagnósticos apresentados ao longo do módulo verificam a codificação alélica, a centralização, o relacionamento genômico e a estratificação por família.",
        "pt reader prose",
    )
    old_packages = '''O primeiro chunk carrega somente os pacotes necessários para manipulação dos objetos, reorganização tabular, gráficos, tabelas e caminhos portáveis. Nenhuma matriz é criada nesta etapa.\n\n```{r pacotes}\nsuppressPackageStartupMessages({\n  library(dplyr)\n  library(tidyr)\n  library(ggplot2)\n  library(knitr)\n  library(here)\n})\n```'''
    new_packages = '''Os pacotes utilizados neste módulo têm funções distintas:\n\n- `dplyr`: seleção, transformação e resumo das tabelas;\n- `tidyr`: reorganização dos dados para diagnósticos e gráficos;\n- `ggplot2`: construção dos gráficos de frequências, folds e relacionamento genômico;\n- `knitr`: formatação das tabelas apresentadas no tutorial;\n- `here`: construção de caminhos de arquivos independentes do diretório local do computador.\n\n```{r pacotes, warning=FALSE, message=FALSE}\nlibrary(dplyr)   # Manipulação, transformação e resumo de tabelas.\nlibrary(tidyr)   # Reorganização dos dados entre formatos.\nlibrary(ggplot2) # Construção de gráficos e mapas de calor.\nlibrary(knitr)   # Formatação de tabelas e saídas do R Markdown.\nlibrary(here)    # Construção de caminhos portáveis dentro do projeto.\n```\n\nPara manter a apresentação consistente, todas as tabelas são formatadas pela função `tabela_html()`. As tabelas ocupam a largura disponível da página e recebem rolagem horizontal quando o conteúdo ultrapassa essa largura.\n\n```{r formatacao-tabelas, include=FALSE}\ntabela_html <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  tabela <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      tabela,\n      '</div>'\n    )\n  )\n}\n```'''
    text = replace_once(text, old_packages, new_packages, "pt packages")

    old_params = '''A etapa seguinte carrega o objeto de pré-processamento e fixa os parâmetros usados na construção das matrizes e da validação cruzada.\n\nSão definidos cinco folds porque, com 150 indivíduos, a partição 5-fold produz 30 indivíduos de validação e 120 de treinamento em cada fold, mantendo a estratificação por família. Cada indivíduo aparece exatamente uma vez em validação; trata-se de uma única partição estratificada em cinco folds, e não de validação cruzada repetida. `SEED_CV = 20260723` serve apenas para reproduzir a mesma alocação dos indivíduos e não possui interpretação inferencial.\n\nO limite `ALLELE_FREQUENCY_MIN = 0.05` mantém colunas alélicas com frequência entre 0,05 e 0,95, desde que também apresentem variação de dosagem positiva. Assim, alelos muito raros ou praticamente fixados não entram em `M`. O limite de taxa de chamada é herdado do Módulo 01 para registrar a mesma regra de controle de qualidade; os locos já chegam a este módulo com essa decisão aplicada.'''
    new_params = '''O objeto `preprocessing_object.rds`, produzido no Módulo 01, fornece os indivíduos, fenótipos, famílias e locos SSR que entram na construção das matrizes.\n\nTrês parâmetros são definidos neste módulo:\n\n- `N_FOLDS = 5`: divide os 150 indivíduos em cinco grupos de validação com 30 indivíduos cada e 120 indivíduos de treinamento. Cada indivíduo participa uma única vez da validação; não se trata de validação cruzada repetida.\n- `SEED_CV = 20260723`: reproduz exatamente a mesma alocação estratificada dos indivíduos entre os folds. A semente controla apenas a reprodutibilidade da partição e não possui interpretação inferencial.\n- `ALLELE_FREQUENCY_MIN = 0.05`: mantém colunas alélicas com frequência entre 0,05 e 0,95, desde que também apresentem variação de dosagem positiva. Alelos muito raros ou praticamente fixados não entram em `M`.\n\nO limite de taxa de chamada é recuperado do Módulo 01 porque o filtro de locos já foi aplicado antes da construção das dosagens alélicas.'''
    text = replace_once(text, old_params, new_params, "pt parameters")

    text = text.replace("nenhum novo filtro é aplicado neste chunk.", "nenhum novo filtro é aplicado nessa conferência.")
    text = text.replace("calculada no chunk anterior", "calculada anteriormente")
    text = text.replace("No conjunto canônico,", "No conjunto de dados analisado,")
    text = text.replace("de acordo com o desenho transdutivo definido no início do módulo", "de acordo com o cenário transdutivo descrito no início do módulo")
    text = re.sub(r'(?<!::)\bkable\(', 'tabela_html(', text)

    anchors = [
        (
            '  tabela_html(caption = "Dados de entrada para a construção das matrizes")\n```\n\n## 3. Codificação das dosagens alélicas',
            '  tabela_html(caption = "Dados de entrada para a construção das matrizes")\n```\n\nA conferência mostra `r length(ids)` indivíduos, `r ncol(phenotypes)` características fenotípicas, `r ncol(ssr_raw)` locos SSR originais e `r sum(locus_audit_full$Keep_locus)` locos mantidos após o controle de qualidade do Módulo 01. As famílias permanecem representadas por `r nlevels(metadata$FAM)` níveis de `FAM`.\n\n## 3. Codificação das dosagens alélicas',
            "pt input interpretation",
        ),
        (
            'dosage_full_raw[1:6, 1:8]\n```\n\n## 4. Frequências alélicas e retenção das colunas de dosagem',
            'dosage_full_raw[1:6, 1:8]\n```\n\nA codificação gera `r ncol(dosage_full_raw)` colunas de dosagem a partir dos `r ncol(ssr_full)` locos mantidos. Em cada coluna, os valores 0, 1 e 2 indicam o número de cópias do alelo identificado após `__A`; `NA` indica uma chamada SSR ausente. Um mesmo loco pode originar mais de duas colunas quando apresenta mais de dois alelos no painel.\n\n## 4. Frequências alélicas e retenção das colunas de dosagem',
            "pt dosage interpretation",
        ),
        (
            '  caption = "Colunas de dosagem alélica por loco SSR"\n)\n```\n\nO histograma mostra',
            '  caption = "Colunas de dosagem alélica por loco SSR"\n)\n```\n\nDas `r nrow(allele_audit_full)` colunas alélicas inicialmente codificadas, `r sum(allele_audit_full$Keep_allele)` atendem simultaneamente ao intervalo de frequência e à exigência de variação positiva. A tabela mostra, para cada loco, quantos alelos foram observados e quantos permanecem na matriz de marcadores.\n\nO histograma mostra',
            "pt allele table interpretation",
        ),
        (
            '  theme_bw()\n```\n\n## 5. Matriz de marcadores',
            '  theme_bw()\n```\n\nAs frequências observadas variam de `r sprintf("%.3f", min(allele_audit_full$Allele_frequency, na.rm = TRUE))` a `r sprintf("%.3f", max(allele_audit_full$Allele_frequency, na.rm = TRUE))`. As barras classificadas como não mantidas correspondem a colunas que falham em pelo menos um dos critérios definidos; as linhas tracejadas mostram apenas os limites de frequência.\n\n## 5. Matriz de marcadores',
            "pt allele plot interpretation",
        ),
        (
            '    caption = "Dimensões e centralização da matriz de marcadores"\n  )\n```\n\n## 6. Matriz de relacionamento genômico',
            '    caption = "Dimensões e centralização da matriz de marcadores"\n  )\n```\n\nA matriz `M` possui `r nrow(M_full)` linhas e `r ncol(M_full)` colunas de dosagem retidas. Seu posto é `r qr(M_full)$rank`, inferior ao número de colunas porque dosagens pertencentes ao mesmo loco podem apresentar dependência linear. A maior média absoluta das colunas é `r format(max(abs(colMeans(M_full))), scientific = TRUE, digits = 3)`, confirmando a centralização numérica.\n\n## 6. Matriz de relacionamento genômico',
            "pt M interpretation",
        ),
        (
            '    caption = "Resumo numérico da matriz de relacionamento genômico"\n  )\n```\n\n## 7. Matriz de efeitos fixos',
            '    caption = "Resumo numérico da matriz de relacionamento genômico"\n  )\n```\n\nA matriz `G` é numericamente simétrica, com diferença máxima de `r format(max(abs(G_full - t(G_full))), scientific = TRUE, digits = 3)`. A média da diagonal é `r sprintf("%.3f", mean(diag(G_full)))` e o menor autovalor é `r format(min(eigenvalues_G_full), scientific = TRUE, digits = 3)`. Valores negativos de magnitude muito pequena são compatíveis com erro numérico de arredondamento.\n\n## 7. Matriz de efeitos fixos',
            "pt G interpretation",
        ),
        (
            '  tabela_html(caption = "Dimensões e postos das matrizes analíticas")\n```\n\n## 8. Cinco folds estratificados por família',
            '  tabela_html(caption = "Dimensões e postos das matrizes analíticas")\n```\n\n`X`, `M` e `G` têm `r length(ids)` linhas, garantindo a mesma ordem dos indivíduos. `X` contém o intercepto e as colunas necessárias para representar `FAM`; `M` contém as dosagens centralizadas; e `G` é uma matriz quadrada de relacionamento entre todos os indivíduos.\n\n## 8. Cinco folds estratificados por família',
            "pt matrix dimensions interpretation",
        ),
        (
            '  caption = "Tamanhos amostrais da validação cruzada"\n)\n```\n\nA tabela família × fold',
            '  caption = "Tamanhos amostrais da validação cruzada"\n)\n```\n\nTodos os cinco folds contêm `r unique(fold_summary$Validation_n)` indivíduos de validação e `r unique(fold_summary$Training_n)` indivíduos de treinamento. Assim, o tamanho amostral é constante entre as cinco rodadas.\n\nA tabela família × fold',
            "pt folds interpretation",
        ),
        (
            '  caption = "Número de indivíduos de cada família em cada fold"\n)\n```\n\nO mapa de calor apresenta',
            '  caption = "Número de indivíduos de cada família em cada fold"\n)\n```\n\nA maior diferença entre a contagem máxima e mínima de uma mesma família nos cinco folds é `r max(family_balance)` indivíduo. Esse resultado confirma que a estratificação distribui cada família de forma tão equilibrada quanto permite seu tamanho.\n\nO mapa de calor apresenta',
            "pt family balance interpretation",
        ),
        (
            '  theme_bw()\n```\n\n## 9. Uso dos folds no ajuste dos modelos',
            '  theme_bw()\n```\n\nO mapa de calor confirma visualmente o equilíbrio mostrado na tabela: as contagens de uma mesma família diferem, no máximo, pela unidade indicada acima. A figura descreve a composição dos folds e não altera a partição já definida.\n\n## 9. Uso dos folds no ajuste dos modelos',
            "pt fold heatmap interpretation",
        ),
        (
            '  tabela_html(caption = "Exemplo da atribuição dos indivíduos aos folds")\n```\n\n## 10. Mapa de calor do relacionamento genômico',
            '  tabela_html(caption = "Exemplo da atribuição dos indivíduos aos folds")\n```\n\nA prévia mostra apenas 15 linhas ordenadas para facilitar a inspeção. A tabela completa `cv_folds` mantém os 150 indivíduos e será usada diretamente no Módulo 03.\n\n## 10. Mapa de calor do relacionamento genômico',
            "pt fold example interpretation",
        ),
        (
            '  theme_bw()\n```\n\n## 11. Diagnósticos das matrizes construídas',
            '  theme_bw()\n```\n\nO mapa de calor sintetiza os relacionamentos pareados presentes em `G`. Como a ordem dos indivíduos é mantida e nenhum agrupamento é aplicado, regiões de maior ou menor intensidade devem ser interpretadas como padrões descritivos de relacionamento, e não como grupos inferidos pelo gráfico.\n\n## 11. Diagnósticos das matrizes construídas',
            "pt G heatmap interpretation",
        ),
        (
            '  caption = "Resumo das matrizes e da validação cruzada"\n)\n```\n\n## 12. Gravação das matrizes e dos folds',
            '  caption = "Resumo das matrizes e da validação cruzada"\n)\n```\n\nO inventário final reúne em uma única tabela as verificações anteriores. Para os dados analisados, `M` possui `r ncol(M_full)` colunas e posto `r qr(M_full)$rank`, igual ao posto teórico `r theoretical_rank_M`; a soma das dosagens por loco e a reconstrução de `G` apresentam erros máximos próximos de zero, e os cinco folds mantêm os mesmos tamanhos de treinamento e validação.\n\n## 12. Gravação das matrizes e dos folds',
            "pt inventory interpretation",
        ),
    ]
    for old, new, label in anchors:
        text = replace_once(text, old, new, label)

    if 'href="03_models_pt.html"' not in text:
        text = text.rstrip() + '''\n\n<div style="display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;">\n<a href="01_preprocessing_pt.html">← Módulo 01 — Pré-processamento</a>\n<a href="03_models_pt.html">Módulo 03 — Ajuste dos modelos →</a>\n</div>\n'''
    return text


def refine_en(text):
    text = replace_once(
        text,
        "The hidden chunk below defines only the rendering options shared by this page. It does not load analytical objects, construct matrices, or affect cross-validation.\n\n",
        "",
        "en hidden setup prose",
    )
    text = replace_once(
        text,
        "At the end of the module, the reader will have four components used directly in Module 03: the fixed-effect matrix `X`, the centered marker matrix `M`, the genomic relationship matrix `G`, and the `cv_folds` table identifying each individual's validation fold. Diagnostics throughout the page check whether allele coding, centering, genomic relationships, and family stratification are coherent with this design.",
        "The module produces four components used directly in Module 03: the fixed-effect matrix `X`, the centered marker matrix `M`, the genomic relationship matrix `G`, and the `cv_folds` table identifying each individual's validation fold. Diagnostics throughout the module check allele coding, centering, genomic relationships, and family stratification.",
        "en reader prose",
    )
    old_packages = '''The first chunk loads only the packages required for object manipulation, tabular reshaping, figures, tables, and portable paths. No matrix is created at this stage.\n\n```{r packages}\nsuppressPackageStartupMessages({\n  library(dplyr)\n  library(tidyr)\n  library(ggplot2)\n  library(knitr)\n  library(here)\n})\n```'''
    new_packages = '''The packages used in this module have distinct roles:\n\n- `dplyr`: selects, transforms, and summarizes tabular data;\n- `tidyr`: reshapes data for diagnostics and figures;\n- `ggplot2`: builds allele-frequency, fold-distribution, and genomic-relationship figures;\n- `knitr`: formats tables displayed in the tutorial;\n- `here`: builds project-relative file paths that do not depend on the local working directory.\n\n```{r packages, warning=FALSE, message=FALSE}\nlibrary(dplyr)   # Manipulate, transform, and summarize tables.\nlibrary(tidyr)   # Reshape data between formats.\nlibrary(ggplot2) # Build figures and heatmaps.\nlibrary(knitr)   # Format tables and R Markdown output.\nlibrary(here)    # Build portable project-relative paths.\n```\n\nAll tables in this module use `format_table()` for a consistent presentation. Tables occupy the available page width and use horizontal scrolling when their contents exceed that width.\n\n```{r table-formatting, include=FALSE}\nformat_table <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  table <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      table,\n      '</div>'\n    )\n  )\n}\n```'''
    text = replace_once(text, old_packages, new_packages, "en packages")

    old_params = '''The next step loads the preprocessing object and fixes the parameters used to construct the matrices and cross-validation design.\n\nFive folds are used because, with 150 individuals, 5-fold partitioning gives 30 validation individuals and 120 training individuals per fold while preserving family stratification. Each individual appears exactly once in validation; this is one family-stratified five-fold partition, not repeated cross-validation. `SEED_CV = 20260723` only reproduces the same allocation of individuals and has no inferential interpretation.\n\n`ALLELE_FREQUENCY_MIN = 0.05` retains allele-dosage columns with frequencies between 0.05 and 0.95 provided that dosage variance is also positive. Thus, very rare or nearly fixed alleles do not enter `M`. The call-rate threshold is inherited from Module 01 to record the same quality-control rule; loci reach this module after that decision has already been applied.'''
    new_params = '''The `preprocessing_object.rds` file produced in Module 01 supplies the individuals, phenotypes, families, and SSR loci used to construct the matrices.\n\nThree parameters are defined in this module:\n\n- `N_FOLDS = 5`: divides the 150 individuals into five validation groups of 30 individuals, leaving 120 training individuals per fold. Each individual appears in validation exactly once; this is not repeated cross-validation.\n- `SEED_CV = 20260723`: reproduces exactly the same family-stratified allocation across folds. The seed controls partition reproducibility only and has no inferential interpretation.\n- `ALLELE_FREQUENCY_MIN = 0.05`: retains allele-dosage columns with frequencies between 0.05 and 0.95 provided that dosage variation is positive. Very rare or nearly fixed alleles therefore do not enter `M`.\n\nThe call-rate threshold is recovered from Module 01 because locus filtering has already been applied before allele-dosage construction.'''
    text = replace_once(text, old_params, new_params, "en parameters")

    text = text.replace("no new filter is applied in this chunk.", "no new filter is applied in this check.")
    text = text.replace("calculated in the previous chunk", "calculated previously")
    text = text.replace("In the canonical dataset,", "In the analyzed dataset,")
    text = text.replace("according to the transductive design defined at the beginning of the module", "according to the transductive setting described at the beginning of the module")
    text = re.sub(r'(?<!::)\bkable\(', 'format_table(', text)

    anchors = [
        (
            '  format_table(caption = "Input data for matrix construction")\n```\n\n## 3. Allele-dosage coding',
            '  format_table(caption = "Input data for matrix construction")\n```\n\nThe check shows `r length(ids)` individuals, `r ncol(phenotypes)` phenotype traits, `r ncol(ssr_raw)` original SSR loci, and `r sum(locus_audit_full$Keep_locus)` loci retained after Module 01 quality control. Family remains represented by `r nlevels(metadata$FAM)` levels of `FAM`.\n\n## 3. Allele-dosage coding',
            "en input interpretation",
        ),
        (
            'dosage_full_raw[1:6, 1:8]\n```\n\n## 4. Allele frequencies and retention of dosage columns',
            'dosage_full_raw[1:6, 1:8]\n```\n\nThe coding produces `r ncol(dosage_full_raw)` dosage columns from the `r ncol(ssr_full)` retained loci. Within each column, values 0, 1, and 2 give the number of copies of the allele identified after `__A`; `NA` denotes a missing SSR call. One locus can produce more than two columns when more than two alleles are represented in the panel.\n\n## 4. Allele frequencies and retention of dosage columns',
            "en dosage interpretation",
        ),
        (
            '  caption = "Allele-dosage columns by SSR locus"\n)\n```\n\nThe histogram shows',
            '  caption = "Allele-dosage columns by SSR locus"\n)\n```\n\nOf the `r nrow(allele_audit_full)` initially coded allele columns, `r sum(allele_audit_full$Keep_allele)` satisfy both the frequency interval and positive-variation requirement. The table shows how many alleles were observed and retained at each locus.\n\nThe histogram shows',
            "en allele table interpretation",
        ),
        (
            '  theme_bw()\n```\n\n## 5. Marker matrix',
            '  theme_bw()\n```\n\nObserved allele frequencies range from `r sprintf("%.3f", min(allele_audit_full$Allele_frequency, na.rm = TRUE))` to `r sprintf("%.3f", max(allele_audit_full$Allele_frequency, na.rm = TRUE))`. Bars classified as not retained fail at least one of the defined criteria; the dashed lines display the frequency limits only.\n\n## 5. Marker matrix',
            "en allele plot interpretation",
        ),
        (
            '    caption = "Dimensions and centering of the marker matrix"\n  )\n```\n\n## 6. Genomic relationship matrix',
            '    caption = "Dimensions and centering of the marker matrix"\n  )\n```\n\nMatrix `M` contains `r nrow(M_full)` rows and `r ncol(M_full)` retained dosage columns. Its rank is `r qr(M_full)$rank`, below the number of columns because dosage columns from the same locus can be linearly dependent. The largest absolute column mean is `r format(max(abs(colMeans(M_full))), scientific = TRUE, digits = 3)`, confirming numerical centering.\n\n## 6. Genomic relationship matrix',
            "en M interpretation",
        ),
        (
            '    caption = "Numerical summary of the genomic relationship matrix"\n  )\n```\n\n## 7. Fixed-effect matrix',
            '    caption = "Numerical summary of the genomic relationship matrix"\n  )\n```\n\nMatrix `G` is numerically symmetric, with a maximum difference of `r format(max(abs(G_full - t(G_full))), scientific = TRUE, digits = 3)`. Its mean diagonal is `r sprintf("%.3f", mean(diag(G_full)))`, and its smallest eigenvalue is `r format(min(eigenvalues_G_full), scientific = TRUE, digits = 3)`. Negative values of very small magnitude are compatible with numerical rounding.\n\n## 7. Fixed-effect matrix',
            "en G interpretation",
        ),
        (
            '  format_table(caption = "Dimensions and ranks of the analytical matrices")\n```\n\n## 8. Five family-stratified folds',
            '  format_table(caption = "Dimensions and ranks of the analytical matrices")\n```\n\n`X`, `M`, and `G` all have `r length(ids)` rows, preserving the same individual order. `X` contains the intercept and columns required to represent `FAM`; `M` contains centered dosages; and `G` is the square relationship matrix among all individuals.\n\n## 8. Five family-stratified folds',
            "en matrix dimensions interpretation",
        ),
        (
            '  caption = "Sample sizes in cross-validation"\n)\n```\n\nThe family × fold table',
            '  caption = "Sample sizes in cross-validation"\n)\n```\n\nAll five folds contain `r unique(fold_summary$Validation_n)` validation individuals and `r unique(fold_summary$Training_n)` training individuals. Sample size is therefore constant across the five rounds.\n\nThe family × fold table',
            "en folds interpretation",
        ),
        (
            '  caption = "Number of individuals from each family in each fold"\n)\n```\n\nThe heatmap presents',
            '  caption = "Number of individuals from each family in each fold"\n)\n```\n\nThe largest difference between the maximum and minimum count for the same family across folds is `r max(family_balance)` individual. This confirms that stratification distributes each family as evenly as its size permits.\n\nThe heatmap presents',
            "en family balance interpretation",
        ),
        (
            '  theme_bw()\n```\n\n## 9. Use of folds in model fitting',
            '  theme_bw()\n```\n\nThe heatmap visually confirms the balance shown in the table: counts within a family differ by no more than the amount reported above. The figure describes fold composition and does not modify the partition.\n\n## 9. Use of folds in model fitting',
            "en fold heatmap interpretation",
        ),
        (
            '  format_table(caption = "Example of individual fold assignment")\n```\n\n## 10. Genomic relationship heatmap',
            '  format_table(caption = "Example of individual fold assignment")\n```\n\nThe preview shows only 15 sorted rows to facilitate inspection. The complete `cv_folds` table retains all 150 individuals and is used directly in Module 03.\n\n## 10. Genomic relationship heatmap',
            "en fold example interpretation",
        ),
        (
            '  theme_bw()\n```\n\n## 11. Diagnostics of the constructed matrices',
            '  theme_bw()\n```\n\nThe heatmap summarizes pairwise relationships in `G`. Because individual order is preserved and no clustering is applied, areas of higher or lower intensity should be interpreted as descriptive relationship patterns rather than groups inferred by the figure.\n\n## 11. Diagnostics of the constructed matrices',
            "en G heatmap interpretation",
        ),
        (
            '  caption = "Summary of matrices and cross-validation"\n)\n```\n\n## 12. Saving matrices and folds',
            '  caption = "Summary of matrices and cross-validation"\n)\n```\n\nThe final inventory collects the preceding checks in one table. For the analyzed data, `M` contains `r ncol(M_full)` columns and rank `r qr(M_full)$rank`, equal to the theoretical rank `r theoretical_rank_M`; dosage sums within loci and reconstruction of `G` have maximum errors close to zero, and all five folds retain the same training and validation sizes.\n\n## 12. Saving matrices and folds',
            "en inventory interpretation",
        ),
    ]
    for old, new, label in anchors:
        text = replace_once(text, old, new, label)

    if 'href="03_models_en.html"' not in text:
        text = text.rstrip() + '''\n\n<div style="display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;">\n<a href="01_preprocessing_en.html">← Module 01 — Preprocessing</a>\n<a href="03_models_en.html">Module 03 — Model fitting →</a>\n</div>\n'''
    return text


for path, fn in [
    (Path("analysis/02_matrices_pt.Rmd"), refine_pt),
    (Path("analysis/02_matrices_en.Rmd"), refine_en),
]:
    original = path.read_text(encoding="utf-8")
    refined = fn(original)
    if refined == original:
        raise RuntimeError(f"No changes made to {path}")
    path.write_text(refined, encoding="utf-8")

print("Module 02 didactic refinement prepared.")
