# Configuração compartilhada do projeto ---------------------------------------

obter_configuracao <- function(modo = Sys.getenv("PAPAYA_RUN_MODE", "site")) {
  modo <- tolower(trimws(modo))

  if (!modo %in% c("site", "smoke", "full")) {
    stop("PAPAYA_RUN_MODE deve ser 'site', 'smoke' ou 'full'.")
  }

  perfis_mcmc <- list(
    site = list(executar = FALSE, n_iter = NA_integer_, burn_in = NA_integer_, thin = NA_integer_),
    smoke = list(executar = TRUE, n_iter = 5000L, burn_in = 1000L, thin = 5L),
    full = list(executar = TRUE, n_iter = 1000000L, burn_in = 200000L, thin = 4L)
  )

  dicionario_caracteristicas <- data.frame(
    Trait = c("MMCOM", "PRODCOM", "PRODEF", "CF", "DF", "DCI", "EP", "FFC", "FFP", "SS"),
    Description_en = c(
      "Mean mass of commercial fruit",
      "Production of commercial fruit",
      "Production of defective fruit",
      "Fruit length",
      "Fruit diameter",
      "Internal-cavity diameter",
      "Mean pulp thickness",
      "External fruit firmness",
      "Internal pulp firmness",
      "Soluble solids"
    ),
    Description_pt = c(
      "Massa média de frutos comerciais",
      "Produção de frutos comerciais",
      "Produção de frutos defeituosos",
      "Comprimento do fruto",
      "Diâmetro do fruto",
      "Diâmetro da cavidade interna",
      "Espessura média da polpa",
      "Firmeza externa do fruto",
      "Firmeza interna da polpa",
      "Sólidos solúveis"
    ),
    Unit = c("kg", "kg", "kg", "cm", "cm", "cm", "cm", "N", "N", "°Brix"),
    stringsAsFactors = FALSE
  )

  catalogo_bayesiano <- data.frame(
    Model = c("BRR", "BayesA", "BayesB", "BayesB_pi1e-5", "BayesC", "BL"),
    BGLR_model = c("BRR", "BayesA", "BayesB", "BayesB", "BayesC", "BL"),
    probIn = c(NA, NA, NA, 1 - 1e-5, NA, NA),
    counts = c(NA, NA, NA, 1e6, NA, NA),
    stringsAsFactors = FALSE
  )

  list(
    modo = modo,
    mcmc = perfis_mcmc[[modo]],
    semente = 20260717L,
    n_folds = 8L,
    taxa_chamada_minima = 0.90,
    frequencia_alelica_minima = 0.05,
    arquivo_genotipos = file.path("data", "papaya_ssr_genotypes.xlsx"),
    arquivo_fenotipos = file.path("data", "papaya_phenotypes_2024_2025.xlsx"),
    arquivo_preprocessamento = file.path("output", "preprocessed_papaya_ssr.rds"),
    arquivo_bayesiano = file.path("output", "bayesian_results.rds"),
    arquivo_rrblup = file.path("output", "rrblup_results.rds"),
    arquivo_gblup = file.path("output", "gblup_results.rds"),
    arquivo_comparacao = file.path("output", "model_comparison_results.rds"),
    arquivo_selecao = file.path("output", "genomic_selection_results.rds"),
    dicionario_caracteristicas = dicionario_caracteristicas,
    catalogo_bayesiano = catalogo_bayesiano
  )
}
