from pathlib import Path

FILES = {
    "analysis/01_preprocessing_pt.Rmd": [
        ("modelo estatístico definido para este tutorial", "modelo estatístico adotado nesta análise"),
        ("Os diagnósticos apresentados ao longo do módulo verificam", "Os diagnósticos verificam"),
        ("- `knitr`: formatação das tabelas apresentadas no tutorial;", "- `knitr`: formatação de tabelas em documentos R Markdown;"),
        ("Para manter a apresentação consistente, todas as tabelas são formatadas pela função `tabela_html()`. As tabelas ocupam a largura disponível da página e recebem rolagem horizontal quando o conteúdo ultrapassa essa largura. Essa função altera somente a apresentação; os dados permanecem inalterados.\n\n", ""),
        ("Os caminhos definidos a seguir organizam os arquivos de entrada e a pasta de saída; eles não constituem parâmetros estatísticos.\n\n", ""),
    ],
    "analysis/01_preprocessing_en.Rmd": [
        ("statistical model defined for this tutorial", "statistical model adopted in this analysis"),
        ("The diagnostics presented throughout the module verify", "The diagnostics verify"),
        ("- `knitr`: formats tables displayed in the tutorial;", "- `knitr`: formats tables in R Markdown documents;"),
        ("All tables in this module use `format_table()` for a consistent presentation. Tables occupy the available page width and use horizontal scrolling when their contents exceed that width. This helper changes presentation only; the underlying data are unchanged.\n\n", ""),
        ("The paths defined below organize the input files and output directory; they are not statistical parameters.\n\n", ""),
    ],
    "analysis/02_matrices_pt.Rmd": [
        ("Os diagnósticos apresentados ao longo do módulo verificam", "Os diagnósticos verificam"),
        ("- `knitr`: formatação das tabelas apresentadas no tutorial;", "- `knitr`: formatação de tabelas em documentos R Markdown;"),
        ("Para manter a apresentação consistente, todas as tabelas são formatadas pela função `tabela_html()`. As tabelas ocupam a largura disponível da página e recebem rolagem horizontal quando o conteúdo ultrapassa essa largura.\n\n", ""),
        ("# Constrói a matriz de desenho do único efeito fixo categórico do tutorial.", "# Constrói a matriz de desenho do único efeito fixo categórico da análise."),
    ],
    "analysis/02_matrices_en.Rmd": [
        ("Diagnostics throughout the module check", "The diagnostics check"),
        ("- `knitr`: formats tables displayed in the tutorial;", "- `knitr`: formats tables in R Markdown documents;"),
        ("All tables in this module use `format_table()` for a consistent presentation. Tables occupy the available page width and use horizontal scrolling when their contents exceed that width.\n\n", ""),
        ("# Build the design matrix for the tutorial's only categorical fixed effect.", "# Build the design matrix for the analysis's only categorical fixed effect."),
    ],
}

for file_name, replacements in FILES.items():
    path = Path(file_name)
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        count = text.count(old)
        if count != 1:
            raise RuntimeError(f"{file_name}: expected exactly one occurrence of {old!r}, found {count}")
        text = text.replace(old, new, 1)
    if text == original:
        raise RuntimeError(f"{file_name}: no change produced")
    path.write_text(text, encoding="utf-8")

# Public-prose patterns that should no longer occur in M01/M02 after this cleanup.
forbidden = [
    "Para manter a apresentação consistente",
    "todas as tabelas são formatadas pela função",
    "Essa função altera somente a apresentação",
    "Os caminhos definidos a seguir organizam",
    "All tables in this module use `format_table()` for a consistent presentation",
    "This helper changes presentation only",
    "The paths defined below organize",
    "o leitor",
    "the reader",
    "O chunk oculto",
    "The hidden chunk",
    "O primeiro chunk",
    "The first chunk",
    "suppressPackageStartupMessages",
]

for file_name in FILES:
    text = Path(file_name).read_text(encoding="utf-8")
    for phrase in forbidden:
        if phrase.lower() in text.lower():
            raise RuntimeError(f"{file_name}: forbidden meta-text remains: {phrase}")

print("PASS: content-only didactic cleanup applied to M01/M02 PT/EN")
