# Instala e registra o ambiente reprodutível declarado em DESCRIPTION.

options(repos = c(CRAN = "https://cloud.r-project.org"))

if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv")
}

renv::activate()
renv::load(project = getwd())

biblioteca_projeto <- normalizePath(
  renv::paths$library(project = getwd()),
  winslash = "/",
  mustWork = FALSE
)
biblioteca_ativa <- normalizePath(
  .libPaths()[1L],
  winslash = "/",
  mustWork = FALSE
)

if (!identical(biblioteca_ativa, biblioteca_projeto)) {
  stop(
    "A biblioteca renv do projeto não está ativa. Esperada: ",
    biblioteca_projeto,
    "; observada: ",
    biblioteca_ativa
  )
}

descricao <- read.dcf("DESCRIPTION")
campos <- c("Depends", "Imports")
texto_dependencias <- paste(descricao[1L, campos], collapse = ",")
dependencias <- trimws(unlist(strsplit(texto_dependencias, ",", fixed = TRUE)))
dependencias <- sub("\\s*\\(.*\\)$", "", dependencias)
dependencias <- setdiff(unique(dependencias[nzchar(dependencias)]), "R")

renv::install(dependencias)
renv::snapshot(type = "explicit", prompt = FALSE)

message("Ambiente instalado e renv.lock atualizado.")
