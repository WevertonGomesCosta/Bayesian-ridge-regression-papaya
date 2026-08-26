from pathlib import Path
import re

FILES = {
    "pt": Path("analysis/04_results_pt.Rmd"),
    "en": Path("analysis/04_results_en.Rmd"),
}


def replace_exact(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {n}")
    return text.replace(old, new, 1)


def insert_before(text, marker, block, label):
    if block.strip() in text:
        return text
    n = text.count(marker)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one marker, found {n}")
    return text.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def common_checks(text, lang):
    bad = [
        "suppressPackageStartupMessages",
        "O chunk oculto", "The hidden chunk",
        "O primeiro chunk", "The first chunk",
        "renderização do tutorial", "tutorial rendering",
        "exibição no tutorial", "display in the tutorial",
        "regra configurável do tutorial", "configurable tutorial rule",
    ]
    for term in bad:
        if term.lower() in text.lower():
            raise SystemExit(f"{lang}: residual meta wording: {term}")

    required = [
        "DIC_COMPETITIVE_THRESHOLD <- 2",
        "SELECTION_PROPORTION <- 0.20",
        'OOF_predictive_direction = if_else(',
        "r > 0",
        "filter(N_traits >= 2L)",
        "Competitive_for_selection =",
        "Automatic_candidate =",
        "RRBLUP_automatic_candidate",
        "Predictive_accuracy = Correlation / sqrt(H2)",
    ]
    for term in required:
        if term not in text:
            raise SystemExit(f"{lang}: missing scientific rule: {term}")


def revise_pt(text):
    text = replace_exact(
        text,
        "O chunk oculto a seguir define apenas opções globais de renderização da página. Ele não recalcula métricas, não seleciona modelos e não altera os resultados recebidos do Módulo 03.\n\n",
        "",
        "remove setup meta PT",
    )

    old_packages = '''O primeiro chunk carrega apenas os pacotes usados para manipulação tabular, organização das saídas e renderização do tutorial. Nenhum modelo BGLR é ajustado neste módulo.\n\n```{r packages}\nsuppressPackageStartupMessages({\n  library(dplyr)\n  library(tidyr)\n  library(knitr)\n  library(here)\n})\n```'''
    new_packages = '''Os pacotes utilizados têm funções distintas nesta etapa:\n\n- `dplyr`: agrupamento, junção, ordenação e resumo das tabelas de resultados;\n- `tidyr`: reorganização de tabelas entre formatos longo e largo;\n- `knitr`: formatação de tabelas em documentos R Markdown;\n- `here`: construção de caminhos relativos ao projeto.\n\n```{r packages, warning=FALSE, message=FALSE}\nlibrary(dplyr) # Agrupamento, junção e resumo de tabelas.\nlibrary(tidyr) # Reorganização entre formatos longo e largo.\nlibrary(knitr) # Formatação de tabelas em documentos R Markdown.\nlibrary(here)  # Construção de caminhos relativos ao projeto.\n```\n\n```{r formatacao-tabelas, include=FALSE}\ntabela_html <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  tabela <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      tabela,\n      '</div>'\n    )\n  )\n}\n```'''
    text = replace_exact(text, old_packages, new_packages, "packages PT")

    text = text.replace(
        "O módulo usa dois objetos consolidados: `matrices_object.rds`, que fornece fenótipos, metadados e definições herdadas do Módulo 02, e `models_object.rds`, que fornece métricas por fold, predições OOF e diagnósticos MCMC produzidos no Módulo 03. O chunk abaixo apenas carrega essas estruturas e cria o diretório das saídas derivadas.",
        "O módulo usa dois objetos consolidados: `matrices_object.rds`, que fornece fenótipos, metadados e definições herdadas do Módulo 02, e `models_object.rds`, que fornece métricas por fold, predições OOF e diagnósticos MCMC produzidos no Módulo 03. `readRDS()` recupera esses objetos preservando suas estruturas internas; `dir.create(..., recursive = TRUE)` garante que o diretório das saídas derivadas exista antes da gravação dos resultados.",
    )

    text = text.replace("# Monta a tabela-resumo apresentada nesta seção.\n", "")
    text = text.replace("# Formata a tabela para exibição no tutorial.\n", "")
    text = re.sub(r"(?<!knitr::)\bkable\(", "tabela_html(", text)

    anchor = "As métricas principais são recalculadas com as 150 predições fora da amostra\nde cada combinação característica × método. Cada indivíduo contribui uma única\npredição OOF para cada método."
    addition = anchor + "\n\n`group_by(Trait, Method)` separa as predições por característica e método, e `summarise()` reduz as 150 linhas OOF de cada grupo às métricas agregadas. A correlação `r`, RMSE, MAE, viés e inclinação usam exatamente essas 150 predições. Para a correlação de Pearson, `t_value = r * sqrt((N - 2) / (1 - r^2))` transforma `r` na estatística t com `N - 2` graus de liberdade, e `2 * pt(..., lower.tail = FALSE)` obtém o p-valor bicaudal. Esse p-valor é nominal e descritivo porque os conjuntos de treinamento dos folds se sobrepõem."
    text = replace_exact(text, anchor, addition, "pooled explanation PT")

    anchor = "`Wprob` é utilizado aqui como um peso de suporte relativo derivado do DIC.\nEle não é interpretado como uma probabilidade posterior calibrada de um modelo."
    addition = anchor + "\n\nNo código, `Delta_DIC = Mean_DIC - min(Mean_DIC)` fixa o melhor DIC médio da característica em zero. `log_weight = -0.5 * Delta_DIC` implementa o expoente da fórmula. Antes de exponenciar, `max(log_weight)` é subtraído de todos os log-pesos; essa translação evita problemas numéricos e não altera as razões relativas. Depois, `Wprob = stable_weight / sum(stable_weight)` normaliza os pesos para soma 1, e `ER = max(Wprob) / Wprob` expressa quantas vezes o maior peso relativo supera o peso de cada método."
    text = replace_exact(text, anchor, addition, "Wprob explanation PT")

    anchor = "A regra de um erro-padrão é aplicada à correlação e ao RMSE médios entre folds. Para cada característica, a tolerância de correlação usa o desvio-padrão entre folds do método com a maior `Mean_fold_r`, dividido por `sqrt(5)`; analogamente, a tolerância de RMSE usa o método com o menor `Mean_fold_RMSE`. A candidate must satisfy both tolerances simultaneously." if False else "A regra de um erro-padrão é aplicada à correlação e ao RMSE médios entre folds. Para cada característica, a tolerância de correlação usa o desvio-padrão entre folds do método com a maior `Mean_fold_r`, dividido por `sqrt(5)`; analogamente, a tolerância de RMSE usa o método com o menor `Mean_fold_RMSE`."
    if anchor in text:
        addition = anchor + " `which.max(Mean_fold_r)` localiza o método que define a referência de correlação e `which.min(Mean_fold_RMSE)` localiza a referência de RMSE. Como `N_FOLDS = 5`, dividir o desvio-padrão correspondente por `sqrt(N_FOLDS)` produz a tolerância descritiva usada na regra. Um método precisa satisfazer simultaneamente `Within_one_SE_r` e `Within_one_SE_RMSE` para ser classificado como preditivamente competitivo."
        text = replace_exact(text, anchor, addition, "one-SE explanation PT")

    anchor = "Entre os candidatos automáticos, RR-BLUP recebe prioridade como escolha explícita de parcimônia e referência de contração homogênea; essa prioridade não implica superioridade estatística universal do RR-BLUP. Se RR-BLUP não for candidato automático, os demais são ordenados pela correlação OOF agrupada, seguida de RMSE, MAE e DIC. Na ausência de qualquer candidato automático, o vencedor preditivo é mantido apenas como escolha provisória que requer revisão."
    addition = anchor + "\n\nNo código, `filter(Automatic_candidate)` mantém somente os métodos que passaram simultaneamente pelos critérios preditivos, de DIC e de convergência monitorada. `slice(1L)` retém o primeiro método após a ordenação de prioridade. Em seguida, `coalesce(Automatic_selected_method, Predictive_winner)` usa o candidato automático quando ele existe e, apenas quando esse valor é ausente, recorre ao vencedor preditivo provisório."
    text = replace_exact(text, anchor, addition, "selection hierarchy PT")

    text = text.replace(
        "essa proporção é uma regra configurável do tutorial, e não\numa intensidade ótima estimada.",
        "essa proporção é uma regra configurável desta análise, e não\numa intensidade ótima estimada.",
    )

    anchor = "A ordenação usa `IND` apenas como critério secundário determinístico quando dois escores são exatamente iguais. A proporção selecionada permanece fixa mesmo se houver empate no limite; `Exact_boundary_tie = TRUE` apenas informa que o último incluído e o primeiro excluído possuem o mesmo escore e, portanto, não há evidência genômica para distingui-los naquele corte."
    addition = anchor + "\n\n`ceiling(SELECTION_PROPORTION * N_available)` arredonda para cima o número correspondente à proporção definida, enquanto `pmax(1L, ...)` garante pelo menos um candidato quando houver indivíduos disponíveis. Na tabela de corte, `lead(Selection_score)` desloca o escore seguinte para a mesma linha do candidato atual; `first(N_selected)` identifica a posição do último selecionado e permite comparar diretamente esse escore com o primeiro não selecionado."
    text = replace_exact(text, anchor, addition, "ranking explanation PT")

    anchor = "As classes de recorrência são convenções descritivas: alta para quatro ou mais características, intermediária para três, ampla para duas, específica para uma e nenhuma para zero. O objeto `multitrait_candidates` conserva indivíduos recorrentes em pelo menos duas características para não descartar informação potencialmente útil nos módulos seguintes. Esses pontos de corte organizam a apresentação e não são limiares de significância estatística."
    addition = anchor + "\n\nApós o `left_join()` com todos os indivíduos, `replace_na()` transforma contagens ausentes em zero e listas de características ausentes em texto vazio. `Selection_frequency = N_traits / length(positive_oof_traits)` usa como denominador apenas as características com OOF positivo. `pivot_wider()` reorganiza os ranks específicos para uma coluna por característica, e `filter(N_traits >= 2L)` define o objeto completo de candidatos recorrentes usado nas etapas seguintes."
    text = replace_exact(text, anchor, addition, "recurrence explanation PT")

    anchor = "Estas correlações descrevem a associação entre os valores genômicos OOF produzidos pelos métodos selecionados em cada característica. Como características diferentes podem usar métodos diferentes e os valores são cross-fitted, a matriz resume associação entre escores preditos, não covariância genética estimada conjuntamente. Portanto, ela não deve ser interpretada como matriz de correlações genéticas de um modelo multivariado."
    addition = anchor + "\n\n`pivot_wider(names_from = Trait, values_from = Genomic_value)` coloca as dez características em colunas e mantém uma linha por indivíduo. `as.matrix(...[, traits, drop = FALSE])` seleciona essas colunas na ordem definida por `traits` e preserva a estrutura matricial; `cor()` calcula então as correlações de Pearson entre as colunas de escores OOF."
    text = replace_exact(text, anchor, addition, "correlation explanation PT")

    anchor = "O chunk final grava CSVs individuais para inspeção das principais derivações e um `module04_results.rds` consolidado para consumo programático pelo Módulo 05. Esses arquivos contêm resultados derivados das saídas do Módulo 03; nenhum modelo genômico é reajustado nesta etapa."
    addition = "Ao final, `write.csv(..., row.names = FALSE)` grava as tabelas derivadas sem acrescentar uma coluna artificial de números de linha. A matriz de correlações preserva seus nomes de linha com `row.names = TRUE`. `saveRDS()` reúne as principais tabelas, regras e objetos em `module04_results.rds`, preservando suas classes para leitura direta no Módulo 05. Nenhum modelo genômico é reajustado nesta etapa."
    text = replace_exact(text, anchor, addition, "save explanation PT")

    text = insert_before(
        text,
        "## 3. Desempenho preditivo OOF",
        "Com os resultados completos do Módulo 03, a tabela deve representar 350 combinações característica × fold × método nas métricas, 10.500 predições OOF e 700 diagnósticos escalares MCMC. Esses totais confirmam que as derivações seguintes partem da mesma cobertura usada no ajuste dos modelos.",
        "input interpretation PT",
    )
    text = insert_before(
        text,
        "## 4. DIC e suporte relativo dos métodos",
        "A prévia ordena primeiro as características e, dentro de cada uma, prioriza maior `r` e menor RMSE. Ela permite verificar diretamente que a comparação preditiva principal utiliza as 150 predições OOF reunidas, e não a média simples das cinco correlações por fold.",
        "pooled preview interpretation PT",
    )
    text = insert_before(
        text,
        "## 5. Seleção do método por característica",
        "Na comparação conjunta, métodos com DIC próximos podem apresentar desempenhos OOF diferentes e o método de maior `Wprob` não precisa ser o de maior correlação preditiva. Por isso, ajuste Bayesiano e capacidade preditiva permanecem critérios complementares, não intercambiáveis.",
        "comparison interpretation PT",
    )
    text = insert_before(
        text,
        "## 7. Tempo computacional",
        "A prévia por fold deve ser lida procurando mudanças de sinal da correlação e dispersões marcantes de RMSE/MAE. Como os folds compartilham grande parte do treinamento, essas diferenças são diagnósticos descritivos de estabilidade e não réplicas independentes.",
        "fold interpretation PT",
    )
    text = insert_before(
        text,
        "## 9. Valores genômicos OOF e direção de seleção",
        "O resumo do RR-BLUP/BRR deve ser interpretado característica por característica: `Mean_H2` descreve o análogo de herdabilidade derivado dos componentes do modelo, enquanto `Mean_predictive_accuracy` resume a razão `Correlation / sqrt(H2)` entre folds. Essa razão não é uma correlação convencional e pode ficar fora do intervalo [0, 1].",
        "heritability interpretation PT",
    )
    text = insert_before(
        text,
        "## 12. Correlações entre valores genômicos OOF",
        "A distribuição de recorrência informa quantos indivíduos aparecem em zero, uma, duas ou mais listas de seleção. O objeto `multitrait_candidates` mantém o critério completo de pelo menos duas características; nenhuma dessas contagens transforma a recorrência em índice multicaracterística.",
        "recurrence interpretation PT",
    )
    text = insert_before(
        text,
        "## 13. Gravação dos resultados",
        "A matriz resultante deve ser lida como associação entre escores OOF: valores positivos indicam indivíduos que tendem a receber escores na mesma direção entre duas características, e valores negativos indicam direções opostas. A interpretação não é de correlação genética conjunta.",
        "correlation interpretation PT",
    )

    nav = '''<div style="display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;">\n<a href="03_models_pt.html">← Módulo 03 — Ajuste dos modelos</a>\n<a href="05_results_pt.html">Módulo 05 — Síntese dos resultados →</a>\n</div>'''
    if nav not in text:
        text = text.rstrip() + "\n\n" + nav + "\n"

    common_checks(text, "PT")
    if re.search(r"(?<!knitr::)\bkable\(", text):
        raise SystemExit("PT: direct public kable() remains")
    return text


def revise_en(text):
    text = replace_exact(
        text,
        "The hidden chunk below defines only page-wide rendering options. It does not recompute metrics, select models, or alter the results received from Module 03.\n\n",
        "",
        "remove setup meta EN",
    )

    old_packages = '''The first chunk loads only the packages used for tabular manipulation, output organization, and tutorial rendering. No BGLR model is fitted in this module.\n\n```{r packages}\nsuppressPackageStartupMessages({\n  library(dplyr)\n  library(tidyr)\n  library(knitr)\n  library(here)\n})\n```'''
    new_packages = '''The packages used here have distinct roles:\n\n- `dplyr`: grouping, joining, ordering, and summarizing result tables;\n- `tidyr`: reshaping tables between long and wide formats;\n- `knitr`: formatting tables in R Markdown documents;\n- `here`: building project-relative file paths.\n\n```{r packages, warning=FALSE, message=FALSE}\nlibrary(dplyr) # Group, join, and summarize tables.\nlibrary(tidyr) # Reshape data between long and wide formats.\nlibrary(knitr) # Format tables in R Markdown documents.\nlibrary(here)  # Build project-relative paths.\n```\n\n```{r table-formatting, include=FALSE}\nformat_table <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  table <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      table,\n      '</div>'\n    )\n  )\n}\n```'''
    text = replace_exact(text, old_packages, new_packages, "packages EN")

    text = text.replace(
        "The module uses two consolidated objects: `matrices_object.rds`, which supplies phenotypes, metadata, and definitions inherited from Module 02, and `models_object.rds`, which supplies fold-level metrics, OOF predictions, and MCMC diagnostics produced in Module 03. The chunk below only loads these structures and creates the directory for derived outputs.",
        "The module uses two consolidated objects: `matrices_object.rds`, which supplies phenotypes, metadata, and definitions inherited from Module 02, and `models_object.rds`, which supplies fold-level metrics, OOF predictions, and MCMC diagnostics produced in Module 03. `readRDS()` restores these objects while preserving their internal structures, and `dir.create(..., recursive = TRUE)` ensures that the derived-output directory exists before results are written.",
    )

    text = text.replace("# Summarize the coverage of the model-fitting results received from Module 03.\n", "")
    text = text.replace("# Format the table for display in the tutorial.\n", "")
    text = re.sub(r"(?<!knitr::)\bkable\(", "format_table(", text)

    anchor = "The main metrics are recalculated using the 150 out-of-fold predictions for\neach trait × method combination. Each individual contributes one OOF\nprediction for every method."
    addition = anchor + "\n\n`group_by(Trait, Method)` separates predictions by trait and method, and `summarise()` reduces the 150 OOF rows in each group to aggregate metrics. Correlation `r`, RMSE, MAE, bias, and slope use exactly those 150 predictions. For Pearson correlation, `t_value = r * sqrt((N - 2) / (1 - r^2))` transforms `r` into a t statistic with `N - 2` degrees of freedom, and `2 * pt(..., lower.tail = FALSE)` gives the two-sided p-value. This p-value remains nominal and descriptive because training sets overlap across folds."
    text = replace_exact(text, anchor, addition, "pooled explanation EN")

    anchor = "`Wprob` is used here as a DIC-derived relative-support weight. It is not\ninterpreted as a calibrated posterior probability of a model."
    addition = anchor + "\n\nIn the code, `Delta_DIC = Mean_DIC - min(Mean_DIC)` sets the best mean DIC within the trait to zero. `log_weight = -0.5 * Delta_DIC` implements the exponent in the formula. Before exponentiation, `max(log_weight)` is subtracted from every log-weight; this translation improves numerical stability without changing relative ratios. `Wprob = stable_weight / sum(stable_weight)` then normalizes the weights to sum to 1, and `ER = max(Wprob) / Wprob` expresses how many times the largest relative weight exceeds each method's weight."
    text = replace_exact(text, anchor, addition, "Wprob explanation EN")

    anchor = "The one-standard-error rule is applied to mean fold correlation and RMSE. For each trait, the correlation tolerance uses the across-fold standard deviation of the method with the largest `Mean_fold_r`, divided by `sqrt(5)`; analogously, the RMSE tolerance uses the method with the smallest `Mean_fold_RMSE`. A candidate must satisfy both tolerances simultaneously."
    addition = anchor + " `which.max(Mean_fold_r)` locates the method that defines the correlation reference, while `which.min(Mean_fold_RMSE)` locates the RMSE reference. Because `N_FOLDS = 5`, dividing the corresponding standard deviation by `sqrt(N_FOLDS)` produces the descriptive tolerance used by the rule. A method must satisfy both `Within_one_SE_r` and `Within_one_SE_RMSE` to be predictively competitive."
    text = replace_exact(text, anchor, addition, "one-SE explanation EN")

    anchor = "Among automatic candidates, RR-BLUP receives priority as an explicit parsimony choice and homogeneous-shrinkage benchmark; this priority does not imply universal statistical superiority of RR-BLUP. If RR-BLUP is not an automatic candidate, the remaining candidates are ordered by pooled OOF correlation followed by RMSE, MAE, and DIC. When no automatic candidate exists, the predictive winner is retained only as a provisional choice requiring review."
    addition = anchor + "\n\nIn the code, `filter(Automatic_candidate)` keeps only methods that simultaneously pass the predictive, DIC, and monitored-convergence conditions. `slice(1L)` retains the first method after priority ordering. Then `coalesce(Automatic_selected_method, Predictive_winner)` uses the automatic candidate when it exists and falls back to the provisional predictive winner only when that value is missing."
    text = replace_exact(text, anchor, addition, "selection hierarchy EN")

    text = text.replace(
        "this proportion is a configurable tutorial rule, not\nan estimated optimal selection intensity.",
        "this proportion is a configurable rule in this analysis, not\nan estimated optimal selection intensity.",
    )

    anchor = "`IND` is used only as a deterministic secondary ordering criterion when two scores are exactly equal. The selected proportion remains fixed even when a tie occurs at the boundary; `Exact_boundary_tie = TRUE` only records that the last included and first excluded candidates have the same score, so their genomic evidence does not distinguish them at that cutoff."
    addition = anchor + "\n\n`ceiling(SELECTION_PROPORTION * N_available)` rounds the target count upward, while `pmax(1L, ...)` guarantees at least one candidate when individuals are available. In the cutoff table, `lead(Selection_score)` moves the next score onto the current row; `first(N_selected)` identifies the last selected position so that its score can be compared directly with the first excluded score."
    text = replace_exact(text, anchor, addition, "ranking explanation EN")

    anchor = "Recurrence classes are descriptive conventions: high for four or more traits, intermediate for three, broad for two, specific for one, and none for zero. The `multitrait_candidates` object retains individuals recurring in at least two traits so potentially useful information is not discarded in later modules. These cutoffs organize presentation and are not statistical-significance thresholds."
    addition = anchor + "\n\nAfter the `left_join()` with all individuals, `replace_na()` converts missing counts to zero and missing trait lists to empty text. `Selection_frequency = N_traits / length(positive_oof_traits)` uses only traits with positive OOF correlation in the denominator. `pivot_wider()` places trait-specific ranks in separate columns, and `filter(N_traits >= 2L)` defines the complete recurrent-candidate object used downstream."
    text = replace_exact(text, anchor, addition, "recurrence explanation EN")

    anchor = "These correlations describe associations among OOF genomic values produced by the selected method for each trait. Since different traits may use different methods and the values are cross-fitted, the matrix summarizes association among predicted scores rather than jointly estimated genetic covariance. It therefore should not be interpreted as a genetic-correlation matrix from a multivariate model."
    addition = anchor + "\n\n`pivot_wider(names_from = Trait, values_from = Genomic_value)` places the ten traits in columns while retaining one row per individual. `as.matrix(...[, traits, drop = FALSE])` selects those columns in the order defined by `traits` and preserves matrix structure; `cor()` then computes Pearson correlations among the OOF-score columns."
    text = replace_exact(text, anchor, addition, "correlation explanation EN")

    anchor = "The final chunk writes individual CSV files for inspection of the main derivations and a consolidated `module04_results.rds` for programmatic use by Module 05. These files contain results derived from Module 03 outputs; no genomic model is refitted at this stage."
    addition = "At the end, `write.csv(..., row.names = FALSE)` writes the derived tables without adding an artificial row-number column. The correlation matrix preserves its row labels with `row.names = TRUE`. `saveRDS()` collects the main tables, rules, and objects in `module04_results.rds`, preserving their classes for direct reading in Module 05. No genomic model is refitted at this stage."
    text = replace_exact(text, anchor, addition, "save explanation EN")

    text = insert_before(
        text,
        "## 3. OOF predictive performance",
        "With complete Module 03 results, the table should represent 350 trait × fold × method combinations in the metrics, 10,500 OOF predictions, and 700 scalar MCMC diagnostics. These totals confirm that the following derivations start from the same coverage used for model fitting.",
        "input interpretation EN",
    )
    text = insert_before(
        text,
        "## 4. DIC and relative support for the methods",
        "The preview orders traits first and then prioritizes larger `r` and smaller RMSE within each trait. It verifies directly that the primary predictive comparison uses all 150 pooled OOF predictions rather than a simple average of the five fold correlations.",
        "pooled preview interpretation EN",
    )
    text = insert_before(
        text,
        "## 5. Selecting a method for each trait",
        "In the joint comparison, methods with similar DIC can have different OOF performance, and the method with the largest `Wprob` need not have the largest predictive correlation. Bayesian fit and predictive ability therefore remain complementary rather than interchangeable criteria.",
        "comparison interpretation EN",
    )
    text = insert_before(
        text,
        "## 7. Computational time",
        "The fold-level preview should be read for changes in correlation sign and marked RMSE/MAE dispersion. Because folds share most of their training data, these differences are descriptive stability diagnostics rather than independent replications.",
        "fold interpretation EN",
    )
    text = insert_before(
        text,
        "## 9. OOF genomic values and selection direction",
        "The RR-BLUP/BRR summary should be interpreted trait by trait: `Mean_H2` describes the model-derived heritability analogue, while `Mean_predictive_accuracy` summarizes `Correlation / sqrt(H2)` across folds. This ratio is not a conventional correlation and may lie outside [0, 1].",
        "heritability interpretation EN",
    )
    text = insert_before(
        text,
        "## 12. Correlations among OOF genomic values",
        "The recurrence distribution reports how many individuals occur in zero, one, two, or more selection lists. The `multitrait_candidates` object keeps the full threshold of at least two traits; none of these counts turns recurrence into a multi-trait selection index.",
        "recurrence interpretation EN",
    )
    text = insert_before(
        text,
        "## 13. Saving results",
        "The resulting matrix should be read as association among OOF scores: positive values indicate individuals tending to receive scores in the same direction for two traits, whereas negative values indicate opposing directions. The interpretation is not joint genetic correlation.",
        "correlation interpretation EN",
    )

    nav = '''<div style="display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;">\n<a href="03_models_en.html">← Module 03 — Model fitting</a>\n<a href="05_results_en.html">Module 05 — Results synthesis →</a>\n</div>'''
    if nav not in text:
        text = text.rstrip() + "\n\n" + nav + "\n"

    common_checks(text, "EN")
    if re.search(r"(?<!knitr::)\bkable\(", text):
        raise SystemExit("EN: direct public kable() remains")
    return text


for lang, path in FILES.items():
    text = path.read_text(encoding="utf-8")
    revised = revise_pt(text) if lang == "pt" else revise_en(text)
    path.write_text(revised, encoding="utf-8", newline="\n")

print("Module 04 didactic revision applied to PT/EN sources.")
