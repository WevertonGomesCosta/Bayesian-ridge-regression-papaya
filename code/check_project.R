# Verificações leves do contrato de dados e da estrutura do projeto.

source(file.path("code", "00_config.R"))
source(file.path("code", "01_data_functions.R"))
source(file.path("code", "02_model_functions.R"))

configuracao <- obter_configuracao("site")

hashes_esperados <- c(
  papaya_ssr_genotypes.xlsx = "ffd891bc4b7599eaa38760f5e828e05a945198d8a68783f1493a8df575fe68a1",
  papaya_phenotypes_2024_2025.xlsx = "5fbbc48ecd934f9fffda65d28db5bf1c9a7921d5a6bed9f04df043073f5b77ef"
)

for (nome in names(hashes_esperados)) {
  caminho <- file.path("data", nome)
  observado <- digest::digest(caminho, algo = "sha256", file = TRUE)
  stopifnot(identical(observado, unname(hashes_esperados[[nome]])))
}

objeto <- executar_preprocessamento(configuracao)

stopifnot(length(objeto$ids) == 150L)
stopifnot(length(unique(objeto$ids)) == 150L)
stopifnot(ncol(objeto$codigos_ssr) == 35L)
stopifnot(sum(is.na(objeto$codigos_ssr)) == 126L)
stopifnot(ncol(objeto$fenotipos) == 10L)
stopifnot(!anyNA(objeto$fenotipos))
stopifnot("144B" %in% objeto$ids)
stopifnot(ncol(objeto$dosagens_ssr) == 72L)

testthat::test_dir(
  file.path("tests", "testthat"),
  reporter = testthat::ProgressReporter$new()
)

message("Contrato de dados e testes do projeto validados.")
