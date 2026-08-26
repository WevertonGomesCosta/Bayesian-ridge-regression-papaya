from pathlib import Path
import re
import subprocess

FILES = {
    "pt": Path("analysis/05_results_pt.Rmd"),
    "en": Path("analysis/05_results_en.Rmd"),
}

EXCLUDED_CHUNKS = {
    "setup",
    "packages",
    "formatacao-tabelas",
    "table-formatting",
}


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {count}")
    return text.replace(old, new, 1)


def remove_comment_lines(text, patterns):
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if any(re.fullmatch(pattern, stripped) for pattern in patterns):
            continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def replace_direct_kable(text, helper):
    return re.sub(r"(?<!::)\bkable\(", helper + "(", text)


def revise_pt(text):
    text = re.sub(
        r"\nO chunk oculto a seguir define apenas opções globais de renderização\.[^\n]*\n\n(?=```\{r setup)",
        "\n",
        text,
        count=1,
    )

    text = text.replace(
        "A sequência acompanha o raciocínio do tutorial:",
        "A sequência acompanha o raciocínio analítico:",
    )

    old_packages = '''O primeiro chunk carrega somente os pacotes usados para manipulação, tabelas e figuras. Não há chamada a `BGLR()` nem ajuste de qualquer modelo nesta página.\n\n```{r packages}\nsuppressPackageStartupMessages({\n  library(dplyr)\n  library(ggplot2)\n  library(knitr)\n  library(here)\n})\n```'''
    new_packages = '''Os pacotes utilizados têm funções distintas nesta etapa:\n\n- `dplyr`: organização, junção e transformação das tabelas de resultados;\n- `ggplot2`: construção das figuras de comparação e diagnóstico;\n- `knitr`: formatação das tabelas apresentadas na página;\n- `here`: construção de caminhos relativos ao projeto.\n\n```{r packages, warning=FALSE, message=FALSE}\nlibrary(dplyr)  # Organiza e transforma as tabelas de resultados.\nlibrary(ggplot2) # Constrói as figuras da síntese.\nlibrary(knitr)  # Formata as tabelas em R Markdown.\nlibrary(here)   # Constrói caminhos relativos ao projeto.\n```\n\n```{r formatacao-tabelas, include=FALSE}\ntabela_html <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  tabela <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      tabela,\n      '</div>'\n    )\n  )\n}\n```'''
    text = replace_once(text, old_packages, new_packages, "packages PT")

    text = text.replace(
        "Esses números ajudam o leitor a verificar o escopo da síntese antes de interpretar os painéis seguintes.",
        "Esses números verificam o escopo da síntese antes da interpretação dos painéis seguintes.",
    )

    text = text.replace(
        "essa proporção é uma regra configurável do tutorial, e não",
        "essa proporção é uma regra configurável desta análise, e não",
    )
    text = text.replace(
        "A leitura final deve manter a hierarquia estabelecida ao longo do tutorial:",
        "A leitura final deve manter a hierarquia estabelecida ao longo da análise:",
    )

    text = replace_direct_kable(text, "tabela_html")

    comment_patterns = [
        r"# Monta a tabela-resumo apresentada nesta seção\.",
        r"# Lista os valores correspondentes aos itens da tabela\.",
        r"# Formata a tabela para exibição no tutorial\.",
        r"# Constrói o gráfico usado na interpretação\.",
        r"# Constrói a visualização usada para interpretar os resultados desta seção\.",
        r"# Salva a saída consolidada para uso posterior\.",
        r"# Mantém e organiza as variáveis usadas no resultado\.",
        r"# Traduz o status interno de seleção para o rótulo apresentado ao leitor\.",
        r"# Mantém o vencedor por DIC com o rótulo legível do método\.",
    ]
    text = remove_comment_lines(text, comment_patterns)

    text = replace_once(
        text,
        "```{r selected-mu-data}",
        """`models_object$settings$burn_in / models_object$settings$thin` converte o burn-in da escala de iterações para a escala das amostras salvas. `setNames(model_selection$Selected_method, model_selection$Trait)` cria um vetor nomeado que recupera diretamente o método selecionado de cada característica. `vector(\"list\", length(traits))` pré-aloca as listas que receberão os resultados, e `seq_along(traits)` percorre os índices das dez características. Dentro do laço, `scan()` lê a cadeia salva de `mu`; `seq.int(burn_in_saved + 1L, length(mu_full))` conserva somente as amostras posteriores ao burn-in. A sequência de iterações é reconstruída com `seq.int(..., by = thin)`. `cumsum(posterior_mu) / seq_along(posterior_mu)` calcula a média acumulada usando toda a cadeia posterior, enquanto `seq.int(..., by = 100L)` reduz somente os pontos desenhados. Por fim, `density(posterior_mu, n = 512)` estima a densidade marginal usada na figura; `n = 512` controla a resolução da curva, não o número de amostras MCMC.\n\n```{r selected-mu-data}""",
        "MCMC explanation PT",
    )

    text = replace_once(
        text,
        "```{r runtime-figure, fig.width=11, fig.height=7}",
        """No código, `factor(Method, levels = methods)` fixa apenas a ordem visual dos métodos. `pmax(0, Mean_seconds - SD_seconds)` impede que a extremidade inferior da haste gráfica seja desenhada abaixo de zero segundos; o valor médio e o desvio-padrão originais permanecem inalterados.\n\n```{r runtime-figure, fig.width=11, fig.height=7}""",
        "runtime explanation PT",
    )

    text = replace_once(
        text,
        "```{r oof-correlation-figure, fig.width=10, fig.height=9}",
        """`as.table(selected_oof_correlations)` transforma a matriz 10 × 10 em combinações linha-coluna-valor; `as.data.frame()` converte essa estrutura em uma tabela longa e `names()` atribui os nomes das três colunas. `replace(Correlation, abs(Correlation) < 0.005, 0)` atua somente na coluna de rótulos. A estética `fill = Correlation` continua usando a correlação original, enquanto `sprintf(\"%.2f\", Correlation_label)` controla apenas o texto mostrado em cada célula.\n\n```{r oof-correlation-figure, fig.width=10, fig.height=9}""",
        "correlation explanation PT",
    )

    text = replace_once(
        text,
        "```{r proportional-selection-table}",
        """A tabela de tamanho do ranking é construída por duas junções. O primeiro `left_join()` acrescenta o objetivo de seleção de cada característica; o segundo acrescenta `r`, p-valor nominal e a classificação do sinal OOF. Como são `left_join()`, as características já presentes em `selection_sizes` permanecem como referência da apresentação. O p-valor é mostrado, mas não é usado para remover rankings.\n\n```{r proportional-selection-table}""",
        "ranking explanation PT",
    )

    text = replace_once(
        text,
        "```{r proportional-selection-preview}",
        """Na prévia, `group_by(Trait)` separa os rankings por característica, `slice_head(n = 5)` conserva somente as cinco primeiras linhas de cada grupo e `ungroup()` encerra o agrupamento antes da seleção das colunas exibidas. O objeto completo `selected_individuals_by_trait` não é truncado.\n\n```{r proportional-selection-preview}""",
        "ranking preview explanation PT",
    )

    text = replace_once(
        text,
        "```{r recurrence-distribution-table}",
        """`recurrence_class_labels[Recurrence_class]` traduz os códigos internos das classes sem recalcular `N_traits`. Na tabela seguinte, `filter(N_traits >= 3L)` reduz apenas a apresentação principal. O objeto `multitrait_candidates` recebido do Módulo 04 permanece definido por recorrência em pelo menos duas características.\n\n```{r recurrence-distribution-table}""",
        "recurrence explanation PT",
    )

    text = text.rstrip() + '''\n\n<div style="display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;">\n<a href="04_results_pt.html">← Módulo 04 — Comparação e seleção</a>\n<a href="index.html">Início →</a>\n</div>\n'''
    return text


def revise_en(text):
    text = re.sub(
        r"\nThe hidden chunk below defines only page-wide rendering options\.[^\n]*\n\n(?=```\{r setup)",
        "\n",
        text,
        count=1,
    )

    text = text.replace(
        "The sequence follows the tutorial reasoning:",
        "The sequence follows the analytical reasoning:",
    )

    old_packages = '''The first chunk loads only the packages used for manipulation, tables, and figures. There is no call to `BGLR()` and no model is fitted on this page.\n\n```{r packages}\nsuppressPackageStartupMessages({\n  library(dplyr)\n  library(ggplot2)\n  library(knitr)\n  library(here)\n})\n```'''
    new_packages = '''The packages used here have distinct roles:\n\n- `dplyr`: organizing, joining, and transforming result tables;\n- `ggplot2`: building comparison and diagnostic figures;\n- `knitr`: formatting the tables presented on the page;\n- `here`: building project-relative paths.\n\n```{r packages, warning=FALSE, message=FALSE}\nlibrary(dplyr)  # Organize and transform result tables.\nlibrary(ggplot2) # Build the synthesis figures.\nlibrary(knitr)  # Format tables in R Markdown.\nlibrary(here)   # Build project-relative paths.\n```\n\n```{r table-formatting, include=FALSE}\nformat_table <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  table <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      table,\n      '</div>'\n    )\n  )\n}\n```'''
    text = replace_once(text, old_packages, new_packages, "packages EN")

    text = text.replace(
        "These counts help the reader verify the scope of the synthesis before interpreting the following panels.",
        "These counts verify the scope of the synthesis before the following panels are interpreted.",
    )
    text = text.replace(
        "is a configurable tutorial rule rather than an estimated optimal intensity.",
        "is a configurable rule in this analysis rather than an estimated optimal intensity.",
    )
    text = text.replace(
        "The final reading should preserve the hierarchy established throughout the tutorial:",
        "The final reading should preserve the hierarchy established throughout the analysis:",
    )

    text = replace_direct_kable(text, "format_table")

    comment_patterns = [
        r"# Summarize the coverage of the consolidated results presented in this module\.",
        r"# Assemble the summary table presented in this section\.",
        r"# List the values corresponding to the table entries\.",
        r"# Format the table for display in the tutorial\.",
        r"# Build the figure used for interpretation\.",
        r"# Build the visualization used to interpret the results in this section\.",
        r"# Save the consolidated output for downstream use\.",
        r"# Keep and organize the variables used in the result\.",
        r"# Translate the internal selection status to the label presented to the reader\.",
        r"# Keep the DIC winner using the readable method label\.",
    ]
    text = remove_comment_lines(text, comment_patterns)

    text = replace_once(
        text,
        "```{r selected-mu-data}",
        """`models_object$settings$burn_in / models_object$settings$thin` converts burn-in from the iteration scale to the saved-sample scale. `setNames(model_selection$Selected_method, model_selection$Trait)` creates a named lookup that directly retrieves the selected method for each trait. `vector(\"list\", length(traits))` preallocates the result lists, and `seq_along(traits)` traverses the ten trait indices. Inside the loop, `scan()` reads the saved `mu` chain; `seq.int(burn_in_saved + 1L, length(mu_full))` retains only post-burn-in samples. Iteration numbers are reconstructed with `seq.int(..., by = thin)`. `cumsum(posterior_mu) / seq_along(posterior_mu)` computes the running mean from the full posterior chain, whereas `seq.int(..., by = 100L)` reduces only the points drawn. Finally, `density(posterior_mu, n = 512)` estimates the marginal density used in the figure; `n = 512` controls curve resolution, not the number of MCMC samples.\n\n```{r selected-mu-data}""",
        "MCMC explanation EN",
    )

    text = replace_once(
        text,
        "```{r runtime-figure, fig.width=11, fig.height=7}",
        """In the code, `factor(Method, levels = methods)` fixes only the visual ordering of methods. `pmax(0, Mean_seconds - SD_seconds)` prevents the lower end of the graphical error bar from being drawn below zero seconds; the original mean and standard deviation remain unchanged.\n\n```{r runtime-figure, fig.width=11, fig.height=7}""",
        "runtime explanation EN",
    )

    text = replace_once(
        text,
        "```{r oof-correlation-figure, fig.width=10, fig.height=9}",
        """`as.table(selected_oof_correlations)` converts the 10 × 10 matrix into row-column-value combinations; `as.data.frame()` converts that structure to long form, and `names()` assigns the three column names. `replace(Correlation, abs(Correlation) < 0.005, 0)` acts only on the label column. The `fill = Correlation` aesthetic continues to use the original correlation, while `sprintf(\"%.2f\", Correlation_label)` controls only the text printed in each cell.\n\n```{r oof-correlation-figure, fig.width=10, fig.height=9}""",
        "correlation explanation EN",
    )

    text = replace_once(
        text,
        "```{r proportional-selection-table}",
        """The ranking-size table is built with two joins. The first `left_join()` adds each trait's selection objective; the second adds `r`, nominal p-value, and the OOF-signal classification. Because both are `left_join()`, traits already present in `selection_sizes` remain the reference set for presentation. The p-value is displayed but is not used to remove rankings.\n\n```{r proportional-selection-table}""",
        "ranking explanation EN",
    )

    text = replace_once(
        text,
        "```{r proportional-selection-preview}",
        """In the preview, `group_by(Trait)` separates rankings by trait, `slice_head(n = 5)` keeps only the first five rows of each group, and `ungroup()` ends grouping before the displayed columns are selected. The complete `selected_individuals_by_trait` object is not truncated.\n\n```{r proportional-selection-preview}""",
        "ranking preview explanation EN",
    )

    text = replace_once(
        text,
        "```{r recurrence-distribution-table}",
        """`recurrence_class_labels[Recurrence_class]` translates the internal class codes without recalculating `N_traits`. In the following table, `filter(N_traits >= 3L)` reduces only the main presentation. The `multitrait_candidates` object received from Module 04 remains defined by recurrence in at least two traits.\n\n```{r recurrence-distribution-table}""",
        "recurrence explanation EN",
    )

    text = text.rstrip() + '''\n\n<div style="display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;">\n<a href="04_results_en.html">← Module 04 — Comparison and selection</a>\n<a href="index.html">Home →</a>\n</div>\n'''
    return text


def extract_chunks(text):
    out = {}
    pat = re.compile(r"```\{r\s+([^,}\s]+)[^}]*\}\n(.*?)\n```", re.S)
    for match in pat.finditer(text):
        label = match.group(1)
        if label in out:
            raise SystemExit(f"duplicate chunk: {label}")
        out[label] = match.group(2)
    return out


def normalize(code):
    lines = []
    for line in code.splitlines():
        if line.strip().startswith("#"):
            continue
        line = line.replace("tabela_html(", "kable(")
        line = line.replace("format_table(", "kable(")
        line = line.strip()
        if line:
            lines.append(line)
    return "\n".join(lines)


def validate_science(path, revised):
    base = subprocess.check_output(
        ["git", "show", f"origin/main:{path.as_posix()}"],
        text=True,
        encoding="utf-8",
    )
    base_chunks = extract_chunks(base)
    revised_chunks = extract_chunks(revised)

    for label, old_code in base_chunks.items():
        if label in EXCLUDED_CHUNKS:
            continue
        if label not in revised_chunks:
            raise SystemExit(f"missing analytical chunk: {path}::{label}")
        if normalize(old_code) != normalize(revised_chunks[label]):
            raise SystemExit(f"analytical code changed: {path}::{label}")

    extras = set(revised_chunks) - set(base_chunks) - EXCLUDED_CHUNKS
    if extras:
        raise SystemExit(f"unexpected analytical chunks in {path}: {sorted(extras)}")


def validate_editorial(text, lang):
    forbidden = [
        "O chunk oculto",
        "The hidden chunk",
        "O primeiro chunk",
        "The first chunk",
        "suppressPackageStartupMessages",
        "renderização do tutorial",
        "tutorial rendering",
        "exibição no tutorial",
        "display in the tutorial",
        "regra configurável do tutorial",
        "configurable tutorial rule",
        "o leitor",
        "the reader",
    ]
    hits = [term for term in forbidden if term in text]
    if hits:
        raise SystemExit(f"{lang}: forbidden editorial text remains: {hits}")

    direct_kable = re.findall(r"(?<!::)\bkable\(", text)
    if direct_kable:
        raise SystemExit(f"{lang}: direct kable() calls remain: {len(direct_kable)}")

    required = [
        "selected-mu-data",
        "runtime-figure",
        "oof-correlation-figure",
        "proportional-selection-table",
        "proportional-selection-preview",
        "recurrence-distribution-table",
        "N_traits >= 3L",
        "multitrait_candidates",
    ]
    for term in required:
        if term not in text:
            raise SystemExit(f"{lang}: required content missing: {term}")

    if lang == "PT":
        if 'href="04_results_pt.html"' not in text or 'href="index.html"' not in text:
            raise SystemExit("PT navigation missing")
    else:
        if 'href="04_results_en.html"' not in text or 'href="index.html"' not in text:
            raise SystemExit("EN navigation missing")


revised_files = {}
for lang, path in FILES.items():
    original = path.read_text(encoding="utf-8")
    revised = revise_pt(original) if lang == "pt" else revise_en(original)
    validate_science(path, revised)
    validate_editorial(revised, lang.upper())
    revised_files[path] = revised

for path, revised in revised_files.items():
    path.write_text(revised, encoding="utf-8", newline="\n")

print("[OK] Module 05 didactic revision applied atomically to PT/EN sources.")
print("[OK] All analytical chunks were preserved against origin/main.")
