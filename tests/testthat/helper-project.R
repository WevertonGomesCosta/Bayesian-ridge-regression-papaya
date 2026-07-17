source(file.path("code", "00_config.R"))
source(file.path("code", "01_data_functions.R"))
source(file.path("code", "02_model_functions.R"))

configuracao_teste <- obter_configuracao("site")

if (!file.exists(configuracao_teste$arquivo_preprocessamento)) {
  executar_preprocessamento(configuracao_teste)
}

objeto_teste <- readRDS(configuracao_teste$arquivo_preprocessamento)
