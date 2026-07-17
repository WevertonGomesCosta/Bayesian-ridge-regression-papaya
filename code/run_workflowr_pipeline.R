# Executa as páginas workflowr na ordem analítica e linguística definida.

argumentos <- commandArgs(trailingOnly = TRUE)
modo <- if (length(argumentos) == 0L) "site" else tolower(argumentos[[1L]])

if (!modo %in% c("site", "smoke", "full")) {
  stop("Uso: Rscript code/run_workflowr_pipeline.R [site|smoke|full]")
}

Sys.setenv(PAPAYA_RUN_MODE = modo)

paginas_ingles <- c(
  "analysis/01_preprocessing_en.Rmd",
  "analysis/02_bayesian_models_en.Rmd",
  "analysis/03_rrblup_en.Rmd",
  "analysis/04_gblup_en.Rmd",
  "analysis/05_model_comparison_en.Rmd",
  "analysis/06_genomic_selection_en.Rmd"
)

paginas_portugues <- c(
  "analysis/01_preprocessing_pt.Rmd",
  "analysis/02_bayesian_models_pt.Rmd",
  "analysis/03_rrblup_pt.Rmd",
  "analysis/04_gblup_pt.Rmd",
  "analysis/05_model_comparison_pt.Rmd",
  "analysis/06_genomic_selection_pt.Rmd"
)

paginas_institucionais <- c(
  "analysis/index.Rmd",
  "analysis/about.Rmd",
  "analysis/license.Rmd"
)

paginas <- c(paginas_ingles, paginas_portugues, paginas_institucionais)
ausentes <- paginas[!file.exists(paginas)]

if (length(ausentes) > 0L) {
  stop("Páginas ausentes: ", paste(ausentes, collapse = ", "))
}

message("Construindo o site no modo: ", modo)
workflowr::wflow_build(paginas, view = FALSE)
print(workflowr::wflow_status())
