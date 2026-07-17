raiz_projeto <- normalizePath(
  testthat::test_path("..", ".."),
  winslash = "/",
  mustWork = TRUE
)

source(file.path(raiz_projeto, "code", "00_config.R"))
source(file.path(raiz_projeto, "code", "01_data_functions.R"))
source(file.path(raiz_projeto, "code", "02_model_functions.R"))

diretorio_anterior <- setwd(raiz_projeto)
tryCatch(
  {
    configuracao_teste <- obter_configuracao("site")

    if (!file.exists(configuracao_teste$arquivo_preprocessamento)) {
      executar_preprocessamento(configuracao_teste)
    }

    objeto_teste <- readRDS(configuracao_teste$arquivo_preprocessamento)
  },
  finally = setwd(diretorio_anterior)
)
