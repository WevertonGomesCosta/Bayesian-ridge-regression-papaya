from pathlib import Path

pt = Path("analysis/04_results_pt.Rmd")
en = Path("analysis/04_results_en.Rmd")

s = en.read_text(encoding="utf-8")
s = s.replace("table_html(", "format_table(")
s = s.replace(
    "- `ggplot2`: building the graphical diagnostic of the selection rule;",
    "- `ggplot2`: building performance and observed-versus-predicted figures;"
)
s = s.replace(
    "During derivation, no output directory is created; `output/results/m04/` is prepared only in Section 13, immediately before the results are persisted.",
    "During derivation, no output directory is created; revised results are persisted only in the final section and do not overwrite previous M04 outputs."
)
s = s.replace(
    "selection remains trait-specific and continues with complementary DIC\nand diagnostic evidence.",
    "selection remains trait-specific and is defined by OOF metrics; DIC is retained as complementary evidence."
)
en.write_text(s, encoding="utf-8", newline="\n")

s = pt.read_text(encoding="utf-8")
s = s.replace(
    "permanece específica por característica e continua com as evidências\ncomplementares de DIC e diagnóstico.",
    "permanece específica por característica e é definida pelas métricas OOF; o DIC é mantido como evidência complementar."
)
pt.write_text(s, encoding="utf-8", newline="\n")

for path in (pt, en):
    text = path.read_text(encoding="utf-8")
    forbidden = [
        "Automatic_candidate",
        "automatic candidate",
        "candidato automático",
        "Predictive_loss",
        "selection-rule-map",
        "selected-fold-figure",
        "runtime-figure",
        "main_multitrait_rank_profile",
        "provisional_review_required",
        "## 6. Stability across folds",
        "## 6. Estabilidade entre folds",
        "## 7. Computational time",
        "## 7. Tempo computacional",
    ]
    for item in forbidden:
        if item in text:
            raise RuntimeError(f"{path.name}: forbidden legacy item remains: {item}")

if "table_html(" in en.read_text(encoding="utf-8"):
    raise RuntimeError("English M04 still contains table_html()")

print("PASS: PT/EN normalization and legacy-content gate completed.")
