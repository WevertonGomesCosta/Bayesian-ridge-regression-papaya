# Funções de leitura, auditoria e codificação dos dados -----------------------

ler_dados_mamao <- function(arquivo_genotipos, arquivo_fenotipos) {
  genes <- readxl::read_excel(
    arquivo_genotipos,
    sheet = "Genes",
    col_names = FALSE,
    na = c("", "NA")
  )

  genealex <- readxl::read_excel(
    arquivo_genotipos,
    sheet = "Genealex",
    col_names = FALSE,
    na = c("", "NA")
  )

  fenotipos <- readxl::read_excel(
    arquivo_fenotipos,
    sheet = "Médias_IND_artigo",
    na = c("", "NA")
  )

  n_individuos <- nrow(genes)
  n_locos <- ncol(genes) - 1L
  linhas_individuos <- 4L:(3L + n_individuos)
  colunas_locos_genealex <- seq.int(3L, 2L + 2L * n_locos, by = 2L)

  ids <- trimws(as.character(genealex[[2L]][linhas_individuos]))
  nomes_locos <- as.character(unlist(
    genealex[3L, colunas_locos_genealex],
    use.names = FALSE
  ))

  codigos_ssr <- as.matrix(genes[, -1L, drop = FALSE])
  storage.mode(codigos_ssr) <- "numeric"
  codigos_ssr[codigos_ssr == -9] <- NA_real_
  rownames(codigos_ssr) <- ids
  colnames(codigos_ssr) <- nomes_locos

  fenotipos$IND <- trimws(as.character(fenotipos$IND))
  posicao_fenotipo <- match(ids, fenotipos$IND)

  if (anyNA(posicao_fenotipo)) {
    stop("Há indivíduos genotipados sem correspondência na tabela fenotípica.")
  }

  fenotipos <- fenotipos[posicao_fenotipo, , drop = FALSE]
  rownames(fenotipos) <- fenotipos$IND

  caracteristicas <- c(
    "MMCOM", "PRODCOM", "PRODEF", "CF", "DF",
    "DCI", "EP", "FFC", "FFP", "SS"
  )

  colunas_ausentes <- setdiff(c("IND", "BL", "FAM", caracteristicas), names(fenotipos))
  if (length(colunas_ausentes) > 0L) {
    stop("Colunas fenotípicas ausentes: ", paste(colunas_ausentes, collapse = ", "))
  }

  matriz_fenotipos <- as.matrix(fenotipos[, caracteristicas, drop = FALSE])
  storage.mode(matriz_fenotipos) <- "numeric"
  rownames(matriz_fenotipos) <- fenotipos$IND

  metadados <- data.frame(
    IND = fenotipos$IND,
    BL = factor(fenotipos$BL, levels = sort(unique(fenotipos$BL))),
    FAM = factor(fenotipos$FAM, levels = sort(unique(fenotipos$FAM))),
    stringsAsFactors = FALSE,
    row.names = fenotipos$IND
  )

  list(
    ids = ids,
    codigos_ssr = codigos_ssr,
    fenotipos = matriz_fenotipos,
    metadados = metadados,
    grupos_genes = as.integer(genes[[1L]]),
    nomes_locos = nomes_locos
  )
}


codificar_dosagens_ssr <- function(codigos_ssr) {
  matrizes_locos <- vector("list", ncol(codigos_ssr))
  mapa_colunas <- vector("list", ncol(codigos_ssr))

  for (j in seq_len(ncol(codigos_ssr))) {
    codigos <- codigos_ssr[, j]
    ausente <- is.na(codigos)
    alelo_1 <- floor(codigos / 10)
    alelo_2 <- codigos %% 10
    alelos <- sort(unique(c(alelo_1[!ausente], alelo_2[!ausente])))

    dosagens <- vapply(
      alelos,
      function(alelo) {
        valor <- as.numeric(alelo_1 == alelo) + as.numeric(alelo_2 == alelo)
        valor[ausente] <- NA_real_
        valor
      },
      numeric(nrow(codigos_ssr))
    )

    if (is.null(dim(dosagens))) {
      dosagens <- matrix(dosagens, ncol = 1L)
    }

    nomes_colunas <- paste0(colnames(codigos_ssr)[j], "__A", alelos)
    colnames(dosagens) <- nomes_colunas
    rownames(dosagens) <- rownames(codigos_ssr)

    matrizes_locos[[j]] <- dosagens
    mapa_colunas[[j]] <- data.frame(
      Locus = colnames(codigos_ssr)[j],
      Allele = alelos,
      Marker_column = nomes_colunas,
      stringsAsFactors = FALSE
    )
  }

  list(
    dosagens = do.call(cbind, matrizes_locos),
    mapa_colunas = do.call(rbind, mapa_colunas)
  )
}


auditar_marcadores_ssr <- function(
    codigos_ssr,
    dosagens,
    mapa_colunas,
    taxa_chamada_minima = 0.90,
    frequencia_alelica_minima = 0.05) {
  auditoria_locos <- data.frame(
    Locus = colnames(codigos_ssr),
    N_individuals = nrow(codigos_ssr),
    N_called = colSums(!is.na(codigos_ssr)),
    Call_rate = colMeans(!is.na(codigos_ssr)),
    N_genotype_classes = vapply(
      seq_len(ncol(codigos_ssr)),
      function(j) length(unique(stats::na.omit(codigos_ssr[, j]))),
      integer(1)
    ),
    stringsAsFactors = FALSE
  )

  auditoria_locos$Pass_call_rate <- auditoria_locos$Call_rate >= taxa_chamada_minima
  auditoria_locos$Polymorphic <- auditoria_locos$N_genotype_classes >= 2L
  auditoria_locos$Keep_locus <- auditoria_locos$Pass_call_rate & auditoria_locos$Polymorphic

  auditoria_alelos <- mapa_colunas
  auditoria_alelos$Allele_frequency <- vapply(
    auditoria_alelos$Marker_column,
    function(nome) mean(dosagens[, nome], na.rm = TRUE) / 2,
    numeric(1)
  )
  auditoria_alelos$Dosage_sd <- vapply(
    auditoria_alelos$Marker_column,
    function(nome) stats::sd(dosagens[, nome], na.rm = TRUE),
    numeric(1)
  )
  auditoria_alelos$Pass_frequency <-
    auditoria_alelos$Allele_frequency >= frequencia_alelica_minima &
    auditoria_alelos$Allele_frequency <= (1 - frequencia_alelica_minima)
  auditoria_alelos$Variable <- is.finite(auditoria_alelos$Dosage_sd) &
    auditoria_alelos$Dosage_sd > 0
  auditoria_alelos$Keep_allele <- auditoria_alelos$Pass_frequency &
    auditoria_alelos$Variable &
    auditoria_alelos$Locus %in% auditoria_locos$Locus[auditoria_locos$Keep_locus]

  colunas_mantidas <- auditoria_alelos$Marker_column[auditoria_alelos$Keep_allele]

  auditoria_individuos <- data.frame(
    IND = rownames(codigos_ssr),
    N_loci = ncol(codigos_ssr),
    N_called = rowSums(!is.na(codigos_ssr)),
    Call_rate = rowMeans(!is.na(codigos_ssr)),
    stringsAsFactors = FALSE
  )

  list(
    locos = auditoria_locos,
    alelos = auditoria_alelos,
    individuos = auditoria_individuos,
    colunas_mantidas = colunas_mantidas,
    dosagens_filtradas = dosagens[, colunas_mantidas, drop = FALSE]
  )
}


criar_folds_estratificados <- function(familia, k = 8L, semente = 20260717L) {
  familia <- factor(familia)
  folds <- integer(length(familia))
  niveis <- levels(familia)

  set.seed(semente)

  for (s in seq_along(niveis)) {
    indices <- which(familia == niveis[s])
    n <- length(indices)
    repeticoes_completas <- n %/% k
    restante <- n %% k

    rotulos <- rep(seq_len(k), each = repeticoes_completas)
    if (restante > 0L) {
      inicio <- ((s - 1L) * restante) %% k
      extras <- ((inicio + seq_len(restante) - 1L) %% k) + 1L
      rotulos <- c(rotulos, extras)
    }

    folds[indices] <- sample(rotulos, size = n, replace = FALSE)
  }

  if (any(tabulate(folds, nbins = k) == 0L)) {
    stop("A alocação estratificada produziu fold vazio.")
  }

  folds
}


criar_matriz_efeitos_fixos <- function(metadados) {
  matriz <- stats::model.matrix(~ BL + FAM, data = metadados)
  rownames(matriz) <- metadados$IND

  list(
    com_intercepto = matriz,
    sem_intercepto = matriz[, colnames(matriz) != "(Intercept)", drop = FALSE]
  )
}


preparar_marcadores_treino <- function(dosagens, indices_treino) {
  indices_treino <- sort(unique(as.integer(indices_treino)))
  medias_treino <- colMeans(dosagens[indices_treino, , drop = FALSE], na.rm = TRUE)
  colunas_validas <- is.finite(medias_treino)

  dosagens <- dosagens[, colunas_validas, drop = FALSE]
  medias_treino <- medias_treino[colunas_validas]

  for (j in seq_len(ncol(dosagens))) {
    ausentes <- is.na(dosagens[, j])
    dosagens[ausentes, j] <- medias_treino[j]
  }

  desvios_treino <- apply(
    dosagens[indices_treino, , drop = FALSE],
    2L,
    stats::sd
  )
  colunas_variaveis <- is.finite(desvios_treino) & desvios_treino > 0
  dosagens <- dosagens[, colunas_variaveis, drop = FALSE]
  medias_treino <- medias_treino[colunas_variaveis]

  centralizadas <- sweep(dosagens, 2L, medias_treino, FUN = "-")
  frequencias <- medias_treino / 2
  denominador <- sum(2 * frequencias * (1 - frequencias))

  if (!is.finite(denominador) || denominador <= 0) {
    stop("Não foi possível obter denominador positivo para a matriz genômica.")
  }

  matriz_g <- tcrossprod(centralizadas) / denominador
  matriz_g <- (matriz_g + t(matriz_g)) / 2
  dimnames(matriz_g) <- list(rownames(dosagens), rownames(dosagens))

  list(
    marcadores = centralizadas,
    matriz_g = matriz_g,
    medias_treino = medias_treino,
    frequencias = frequencias,
    denominador = denominador,
    colunas = colnames(centralizadas)
  )
}


executar_preprocessamento <- function(configuracao) {
  dir.create("output", showWarnings = FALSE, recursive = TRUE)

  dados <- ler_dados_mamao(
    configuracao$arquivo_genotipos,
    configuracao$arquivo_fenotipos
  )

  codificacao <- codificar_dosagens_ssr(dados$codigos_ssr)
  auditoria <- auditar_marcadores_ssr(
    dados$codigos_ssr,
    codificacao$dosagens,
    codificacao$mapa_colunas,
    taxa_chamada_minima = configuracao$taxa_chamada_minima,
    frequencia_alelica_minima = configuracao$frequencia_alelica_minima
  )

  folds <- criar_folds_estratificados(
    dados$metadados$FAM,
    k = configuracao$n_folds,
    semente = configuracao$semente
  )

  matriz_efeitos_fixos <- criar_matriz_efeitos_fixos(dados$metadados)

  preparacao_folds <- lapply(seq_len(configuracao$n_folds), function(fold) {
    indices_treino <- which(folds != fold)
    preparar_marcadores_treino(
      auditoria$dosagens_filtradas,
      indices_treino = indices_treino
    )
  })
  names(preparacao_folds) <- paste0("Fold_", seq_len(configuracao$n_folds))

  preparacao_completa <- preparar_marcadores_treino(
    auditoria$dosagens_filtradas,
    indices_treino = seq_len(nrow(auditoria$dosagens_filtradas))
  )

  objeto <- list(
    ids = dados$ids,
    metadados = dados$metadados,
    fenotipos = dados$fenotipos,
    codigos_ssr = dados$codigos_ssr,
    dosagens_ssr = auditoria$dosagens_filtradas,
    auditoria = auditoria,
    folds = folds,
    matriz_efeitos_fixos = matriz_efeitos_fixos,
    preparacao_folds = preparacao_folds,
    preparacao_completa = preparacao_completa,
    configuracao = configuracao
  )

  saveRDS(objeto, configuracao$arquivo_preprocessamento)
  utils::write.csv(
    auditoria$locos,
    file.path("output", "marker_qc_by_locus.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(
    auditoria$alelos,
    file.path("output", "marker_qc_by_allele.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(
    auditoria$individuos,
    file.path("output", "marker_qc_by_individual.csv"),
    row.names = FALSE,
    na = ""
  )

  objeto
}
