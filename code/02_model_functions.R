# Funções de ajuste, validação e comparação dos modelos -----------------------

calcular_metricas_predicao <- function(observado, predito) {
  valido <- is.finite(observado) & is.finite(predito)
  observado <- observado[valido]
  predito <- predito[valido]

  correlacao <- NA_real_
  p_valor <- NA_real_
  intercepto <- NA_real_
  inclinacao <- NA_real_

  if (length(observado) >= 3L && stats::sd(observado) > 0 && stats::sd(predito) > 0) {
    teste <- suppressWarnings(stats::cor.test(observado, predito, method = "pearson"))
    correlacao <- unname(teste$estimate)
    p_valor <- teste$p.value
    calibracao <- stats::lm(observado ~ predito)
    intercepto <- unname(stats::coef(calibracao)[1L])
    inclinacao <- unname(stats::coef(calibracao)[2L])
  }

  data.frame(
    N = length(observado),
    Correlation = correlacao,
    Correlation_p_value = p_valor,
    RMSE = sqrt(mean((predito - observado)^2)),
    MAE = mean(abs(predito - observado)),
    Bias = mean(predito - observado),
    Calibration_intercept = intercepto,
    Calibration_slope = inclinacao,
    stringsAsFactors = FALSE
  )
}


validar_posto_efeitos_fixos <- function(matriz, contexto) {
  posto <- qr(matriz)$rank
  if (posto < ncol(matriz)) {
    stop(
      "Matriz de efeitos fixos sem posto completo em ", contexto,
      ": posto ", posto, " para ", ncol(matriz), " colunas."
    )
  }
  invisible(TRUE)
}


ler_tracos_bglr <- function(prefixo, maximo_linhas = 5000L) {
  arquivos <- Sys.glob(paste0(prefixo, "*.dat"))
  tracos <- list()

  for (arquivo in arquivos) {
    tabela <- try(utils::read.table(arquivo, header = TRUE), silent = TRUE)
    if (inherits(tabela, "try-error")) {
      tabela <- try(utils::read.table(arquivo, header = FALSE), silent = TRUE)
    }
    if (inherits(tabela, "try-error") || nrow(tabela) == 0L) {
      next
    }

    if (nrow(tabela) > maximo_linhas) {
      manter <- unique(round(seq.int(1L, nrow(tabela), length.out = maximo_linhas)))
      tabela <- tabela[manter, , drop = FALSE]
    }

    tracos[[basename(arquivo)]] <- tabela
  }

  tracos
}


ajustar_bglr_unico <- function(
    y,
    efeitos_fixos_sem_intercepto,
    marcadores,
    especificacao_modelo,
    configuracao,
    semente,
    capturar_tracos = FALSE) {
  modelo_bglr <- especificacao_modelo$BGLR_model
  eta_marcadores <- list(
    X = marcadores,
    model = modelo_bglr,
    saveEffects = FALSE
  )

  if (identical(especificacao_modelo$Model, "BayesB_pi1e-5")) {
    eta_marcadores$probIn <- as.numeric(especificacao_modelo$probIn)
    eta_marcadores$counts <- as.numeric(especificacao_modelo$counts)
  }

  eta <- list(
    efeitos_fixos = list(
      X = efeitos_fixos_sem_intercepto,
      model = "FIXED",
      saveEffects = FALSE
    ),
    marcadores = eta_marcadores
  )

  prefixo <- tempfile(
    pattern = paste0("bglr_", especificacao_modelo$Model, "_"),
    tmpdir = tempdir()
  )
  on.exit(unlink(Sys.glob(paste0(prefixo, "*")), force = TRUE), add = TRUE)

  set.seed(semente)
  inicio <- proc.time()[["elapsed"]]
  ajuste <- BGLR::BGLR(
    y = y,
    ETA = eta,
    nIter = configuracao$mcmc$n_iter,
    burnIn = configuracao$mcmc$burn_in,
    thin = configuracao$mcmc$thin,
    saveAt = prefixo,
    verbose = FALSE,
    rmExistingFiles = TRUE
  )
  tempo <- proc.time()[["elapsed"]] - inicio

  tracos <- if (capturar_tracos) ler_tracos_bglr(prefixo) else list()

  list(
    ajuste = ajuste,
    tempo_segundos = tempo,
    tracos = tracos
  )
}


executar_modelos_bayesianos <- function(objeto, configuracao) {
  if (!isTRUE(configuracao$mcmc$executar)) {
    stop("O perfil atual não autoriza a execução dos modelos Bayesianos.")
  }

  resultados_folds <- list()
  predicoes_folds <- list()
  resumos_completos <- list()
  valores_genomicos <- list()
  coeficientes <- list()
  tracos_brr <- list()
  indice_resultado <- 0L
  indice_completo <- 0L

  x_sem_intercepto <- objeto$matriz_efeitos_fixos$sem_intercepto
  catalogo <- configuracao$catalogo_bayesiano

  for (t in seq_len(ncol(objeto$fenotipos))) {
    nome_caracteristica <- colnames(objeto$fenotipos)[t]
    y <- objeto$fenotipos[, t]

    for (m in seq_len(nrow(catalogo))) {
      especificacao <- as.list(catalogo[m, , drop = FALSE])

      for (fold in seq_len(configuracao$n_folds)) {
        treino <- which(objeto$folds != fold)
        teste <- which(objeto$folds == fold)
        preparacao <- objeto$preparacao_folds[[fold]]

        validar_posto_efeitos_fixos(
          x_sem_intercepto[treino, , drop = FALSE],
          paste(nome_caracteristica, especificacao$Model, "fold", fold)
        )

        ajuste <- ajustar_bglr_unico(
          y = y[treino],
          efeitos_fixos_sem_intercepto = x_sem_intercepto[treino, , drop = FALSE],
          marcadores = preparacao$marcadores[treino, , drop = FALSE],
          especificacao_modelo = especificacao,
          configuracao = configuracao,
          semente = configuracao$semente + 100000L * t + 1000L * m + fold,
          capturar_tracos = FALSE
        )

        modelo <- ajuste$ajuste
        efeito_fixo <- as.vector(
          x_sem_intercepto[teste, , drop = FALSE] %*%
            modelo$ETA[["efeitos_fixos"]]$b
        )
        gebv <- as.vector(
          preparacao$marcadores[teste, , drop = FALSE] %*%
            modelo$ETA[["marcadores"]]$b
        )
        predito <- modelo$mu + efeito_fixo + gebv

        indice_resultado <- indice_resultado + 1L
        metricas <- calcular_metricas_predicao(y[teste], predito)
        resultados_folds[[indice_resultado]] <- cbind(
          data.frame(
            Trait = nome_caracteristica,
            Fold = fold,
            Model = especificacao$Model,
            Time_seconds = ajuste$tempo_segundos,
            stringsAsFactors = FALSE
          ),
          metricas
        )
        predicoes_folds[[indice_resultado]] <- data.frame(
          IND = objeto$ids[teste],
          Trait = nome_caracteristica,
          Fold = fold,
          Model = especificacao$Model,
          Observed = y[teste],
          Predicted = predito,
          GEBV = gebv,
          stringsAsFactors = FALSE
        )
      }

      preparacao <- objeto$preparacao_completa
      ajuste_completo <- ajustar_bglr_unico(
        y = y,
        efeitos_fixos_sem_intercepto = x_sem_intercepto,
        marcadores = preparacao$marcadores,
        especificacao_modelo = especificacao,
        configuracao = configuracao,
        semente = configuracao$semente + 100000L * t + 1000L * m + 999L,
        capturar_tracos = identical(especificacao$Model, "BRR")
      )

      modelo_completo <- ajuste_completo$ajuste
      gebv_completo <- as.vector(
        preparacao$marcadores %*% modelo_completo$ETA[["marcadores"]]$b
      )
      efeito_fixo_completo <- as.vector(
        x_sem_intercepto %*% modelo_completo$ETA[["efeitos_fixos"]]$b
      )
      ajustado_completo <- modelo_completo$mu + efeito_fixo_completo + gebv_completo

      h2 <- NA_real_
      variancia_aditiva <- NA_real_
      if (identical(especificacao$Model, "BRR")) {
        variancia_marcador <- mean(as.numeric(modelo_completo$ETA[["marcadores"]]$varB))
        variancia_aditiva <- variancia_marcador * preparacao$denominador
        h2 <- variancia_aditiva / (variancia_aditiva + modelo_completo$varE)
      }

      indice_completo <- indice_completo + 1L
      resumos_completos[[indice_completo]] <- data.frame(
        Trait = nome_caracteristica,
        Model = especificacao$Model,
        DIC = modelo_completo$fit$DIC,
        Effective_parameters = modelo_completo$fit$pD,
        Residual_variance = modelo_completo$varE,
        Additive_variance = variancia_aditiva,
        H2 = h2,
        Time_seconds = ajuste_completo$tempo_segundos,
        stringsAsFactors = FALSE
      )
      valores_genomicos[[indice_completo]] <- data.frame(
        IND = objeto$ids,
        Trait = nome_caracteristica,
        Model = especificacao$Model,
        GEBV = gebv_completo,
        Fitted = ajustado_completo,
        stringsAsFactors = FALSE
      )
      coeficientes[[paste(nome_caracteristica, especificacao$Model, sep = "__")]] <- list(
        mu = modelo_completo$mu,
        fixed_effects = modelo_completo$ETA[["efeitos_fixos"]]$b,
        marker_effects = modelo_completo$ETA[["marcadores"]]$b,
        marker_columns = colnames(preparacao$marcadores)
      )

      if (identical(especificacao$Model, "BRR")) {
        tracos_brr[[nome_caracteristica]] <- ajuste_completo$tracos
      }
    }
  }

  resumo_completo <- dplyr::bind_rows(resumos_completos) |>
    dplyr::group_by(.data$Trait) |>
    dplyr::mutate(
      Delta_DIC = .data$DIC - min(.data$DIC, na.rm = TRUE),
      DIC_weight = exp(-0.5 * .data$Delta_DIC) /
        sum(exp(-0.5 * .data$Delta_DIC), na.rm = TRUE),
      Evidence_ratio = max(.data$DIC_weight, na.rm = TRUE) / .data$DIC_weight
    ) |>
    dplyr::ungroup()

  resultado <- list(
    fold_metrics = dplyr::bind_rows(resultados_folds),
    predictions = dplyr::bind_rows(predicoes_folds),
    full_model_summary = resumo_completo,
    genomic_values = dplyr::bind_rows(valores_genomicos),
    coefficients = coeficientes,
    brr_traces = tracos_brr,
    configuration = configuracao
  )

  saveRDS(resultado, configuracao$arquivo_bayesiano)
  resultado
}


executar_rrblup <- function(objeto, configuracao) {
  resultados_folds <- list()
  predicoes_folds <- list()
  resumos_completos <- list()
  valores_genomicos <- list()
  coeficientes <- list()
  indice <- 0L

  x <- objeto$matriz_efeitos_fixos$com_intercepto

  for (t in seq_len(ncol(objeto$fenotipos))) {
    nome_caracteristica <- colnames(objeto$fenotipos)[t]
    y <- objeto$fenotipos[, t]

    for (fold in seq_len(configuracao$n_folds)) {
      treino <- which(objeto$folds != fold)
      teste <- which(objeto$folds == fold)
      preparacao <- objeto$preparacao_folds[[fold]]

      validar_posto_efeitos_fixos(
        x[treino, , drop = FALSE],
        paste(nome_caracteristica, "RRBLUP fold", fold)
      )

      inicio <- proc.time()[["elapsed"]]
      ajuste <- rrBLUP::mixed.solve(
        y = y[treino],
        X = x[treino, , drop = FALSE],
        Z = preparacao$marcadores[treino, , drop = FALSE],
        method = "REML"
      )
      tempo <- proc.time()[["elapsed"]] - inicio

      gebv <- as.vector(preparacao$marcadores[teste, , drop = FALSE] %*% ajuste$u)
      predito <- as.vector(x[teste, , drop = FALSE] %*% ajuste$beta) + gebv

      indice <- indice + 1L
      resultados_folds[[indice]] <- cbind(
        data.frame(
          Trait = nome_caracteristica,
          Fold = fold,
          Model = "RRBLUP",
          Time_seconds = tempo,
          stringsAsFactors = FALSE
        ),
        calcular_metricas_predicao(y[teste], predito)
      )
      predicoes_folds[[indice]] <- data.frame(
        IND = objeto$ids[teste],
        Trait = nome_caracteristica,
        Fold = fold,
        Model = "RRBLUP",
        Observed = y[teste],
        Predicted = predito,
        GEBV = gebv,
        stringsAsFactors = FALSE
      )
    }

    preparacao <- objeto$preparacao_completa
    inicio <- proc.time()[["elapsed"]]
    ajuste_completo <- rrBLUP::mixed.solve(
      y = y,
      X = x,
      Z = preparacao$marcadores,
      method = "REML"
    )
    tempo <- proc.time()[["elapsed"]] - inicio

    gebv_completo <- as.vector(preparacao$marcadores %*% ajuste_completo$u)
    ajustado_completo <- as.vector(x %*% ajuste_completo$beta) + gebv_completo
    variancia_aditiva <- ajuste_completo$Vu * preparacao$denominador
    h2 <- variancia_aditiva / (variancia_aditiva + ajuste_completo$Ve)

    resumos_completos[[t]] <- data.frame(
      Trait = nome_caracteristica,
      Model = "RRBLUP",
      Marker_effect_variance = ajuste_completo$Vu,
      Residual_variance = ajuste_completo$Ve,
      Additive_variance = variancia_aditiva,
      H2 = h2,
      Log_likelihood = ajuste_completo$LL,
      Time_seconds = tempo,
      stringsAsFactors = FALSE
    )
    valores_genomicos[[t]] <- data.frame(
      IND = objeto$ids,
      Trait = nome_caracteristica,
      Model = "RRBLUP",
      GEBV = gebv_completo,
      Fitted = ajustado_completo,
      stringsAsFactors = FALSE
    )
    coeficientes[[nome_caracteristica]] <- list(
      fixed_effects = ajuste_completo$beta,
      marker_effects = ajuste_completo$u,
      marker_columns = colnames(preparacao$marcadores)
    )
  }

  resultado <- list(
    fold_metrics = dplyr::bind_rows(resultados_folds),
    predictions = dplyr::bind_rows(predicoes_folds),
    full_model_summary = dplyr::bind_rows(resumos_completos),
    genomic_values = dplyr::bind_rows(valores_genomicos),
    coefficients = coeficientes,
    configuration = configuracao
  )

  saveRDS(resultado, configuracao$arquivo_rrblup)
  resultado
}


executar_gblup <- function(objeto, configuracao) {
  resultados_folds <- list()
  predicoes_folds <- list()
  resumos_completos <- list()
  valores_genomicos <- list()
  indice <- 0L
  n <- length(objeto$ids)
  z <- diag(n)
  dimnames(z) <- list(objeto$ids, objeto$ids)
  x <- objeto$matriz_efeitos_fixos$com_intercepto

  for (t in seq_len(ncol(objeto$fenotipos))) {
    nome_caracteristica <- colnames(objeto$fenotipos)[t]
    y <- objeto$fenotipos[, t]

    for (fold in seq_len(configuracao$n_folds)) {
      teste <- which(objeto$folds == fold)
      treino <- which(objeto$folds != fold)
      preparacao <- objeto$preparacao_folds[[fold]]
      y_validacao <- y
      y_validacao[teste] <- NA_real_

      validar_posto_efeitos_fixos(
        x[treino, , drop = FALSE],
        paste(nome_caracteristica, "GBLUP fold", fold)
      )

      inicio <- proc.time()[["elapsed"]]
      ajuste <- rrBLUP::mixed.solve(
        y = y_validacao,
        X = x,
        Z = z,
        K = preparacao$matriz_g,
        method = "REML"
      )
      tempo <- proc.time()[["elapsed"]] - inicio

      gebv <- as.vector(ajuste$u[teste])
      predito <- as.vector(x[teste, , drop = FALSE] %*% ajuste$beta) + gebv

      indice <- indice + 1L
      resultados_folds[[indice]] <- cbind(
        data.frame(
          Trait = nome_caracteristica,
          Fold = fold,
          Model = "GBLUP",
          Time_seconds = tempo,
          stringsAsFactors = FALSE
        ),
        calcular_metricas_predicao(y[teste], predito)
      )
      predicoes_folds[[indice]] <- data.frame(
        IND = objeto$ids[teste],
        Trait = nome_caracteristica,
        Fold = fold,
        Model = "GBLUP",
        Observed = y[teste],
        Predicted = predito,
        GEBV = gebv,
        stringsAsFactors = FALSE
      )
    }

    preparacao <- objeto$preparacao_completa
    inicio <- proc.time()[["elapsed"]]
    ajuste_completo <- rrBLUP::mixed.solve(
      y = y,
      X = x,
      Z = z,
      K = preparacao$matriz_g,
      method = "REML"
    )
    tempo <- proc.time()[["elapsed"]] - inicio

    gebv_completo <- as.vector(ajuste_completo$u)
    ajustado_completo <- as.vector(x %*% ajuste_completo$beta) + gebv_completo
    h2 <- ajuste_completo$Vu / (ajuste_completo$Vu + ajuste_completo$Ve)

    resumos_completos[[t]] <- data.frame(
      Trait = nome_caracteristica,
      Model = "GBLUP",
      Additive_variance = ajuste_completo$Vu,
      Residual_variance = ajuste_completo$Ve,
      H2 = h2,
      Log_likelihood = ajuste_completo$LL,
      Time_seconds = tempo,
      stringsAsFactors = FALSE
    )
    valores_genomicos[[t]] <- data.frame(
      IND = objeto$ids,
      Trait = nome_caracteristica,
      Model = "GBLUP",
      GEBV = gebv_completo,
      Fitted = ajustado_completo,
      stringsAsFactors = FALSE
    )
  }

  resultado <- list(
    fold_metrics = dplyr::bind_rows(resultados_folds),
    predictions = dplyr::bind_rows(predicoes_folds),
    full_model_summary = dplyr::bind_rows(resumos_completos),
    genomic_values = dplyr::bind_rows(valores_genomicos),
    relationship_matrix = objeto$preparacao_completa$matriz_g,
    configuration = configuracao
  )

  saveRDS(resultado, configuracao$arquivo_gblup)
  resultado
}


consolidar_comparacao_modelos <- function(
    objeto,
    resultado_bayesiano,
    resultado_rrblup,
    resultado_gblup,
    configuracao) {
  predicoes <- dplyr::bind_rows(
    resultado_bayesiano$predictions,
    resultado_rrblup$predictions,
    resultado_gblup$predictions
  )

  metricas_folds <- dplyr::bind_rows(
    resultado_bayesiano$fold_metrics,
    resultado_rrblup$fold_metrics,
    resultado_gblup$fold_metrics
  )

  metricas_oof <- predicoes |>
    dplyr::group_by(.data$Trait, .data$Model) |>
    dplyr::group_modify(
      ~ calcular_metricas_predicao(.x$Observed, .x$Predicted)
    ) |>
    dplyr::ungroup()

  resumo_folds <- metricas_folds |>
    dplyr::group_by(.data$Trait, .data$Model) |>
    dplyr::summarise(
      N_folds = dplyr::n(),
      Mean_correlation = mean(.data$Correlation, na.rm = TRUE),
      SD_correlation = stats::sd(.data$Correlation, na.rm = TRUE),
      Mean_RMSE = mean(.data$RMSE, na.rm = TRUE),
      Mean_MAE = mean(.data$MAE, na.rm = TRUE),
      Mean_bias = mean(.data$Bias, na.rm = TRUE),
      Mean_time_seconds = mean(.data$Time_seconds, na.rm = TRUE),
      .groups = "drop"
    )

  melhores_modelos <- metricas_oof |>
    dplyr::arrange(
      .data$Trait,
      dplyr::desc(.data$Correlation),
      .data$RMSE,
      .data$MAE
    ) |>
    dplyr::group_by(.data$Trait) |>
    dplyr::slice_head(n = 1L) |>
    dplyr::ungroup()

  resultado <- list(
    predictions = predicoes,
    fold_metrics = metricas_folds,
    out_of_fold_metrics = metricas_oof,
    fold_summary = resumo_folds,
    best_models = melhores_modelos,
    bayesian_dic = resultado_bayesiano$full_model_summary,
    configuration = configuracao
  )

  saveRDS(resultado, configuracao$arquivo_comparacao)
  utils::write.csv(
    metricas_oof,
    file.path("output", "out_of_fold_model_metrics.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(
    melhores_modelos,
    file.path("output", "best_model_by_trait.csv"),
    row.names = FALSE,
    na = ""
  )

  resultado
}


construir_tabelas_selecao <- function(
    objeto,
    resultado_bayesiano,
    resultado_rrblup,
    resultado_gblup,
    comparacao,
    configuracao) {
  valores <- dplyr::bind_rows(
    resultado_bayesiano$genomic_values,
    resultado_rrblup$genomic_values,
    resultado_gblup$genomic_values
  )

  melhores <- comparacao$best_models |>
    dplyr::select(.data$Trait, .data$Model)

  rankings <- valores |>
    dplyr::inner_join(melhores, by = c("Trait", "Model")) |>
    dplyr::left_join(
      data.frame(
        IND = objeto$metadados$IND,
        BL = as.character(objeto$metadados$BL),
        FAM = as.character(objeto$metadados$FAM),
        stringsAsFactors = FALSE
      ),
      by = "IND"
    ) |>
    dplyr::group_by(.data$Trait) |>
    dplyr::arrange(dplyr::desc(.data$GEBV), .data$IND, .by_group = TRUE) |>
    dplyr::mutate(Rank_high_value = dplyr::row_number()) |>
    dplyr::arrange(.data$GEBV, .data$IND, .by_group = TRUE) |>
    dplyr::mutate(Rank_low_value = dplyr::row_number()) |>
    dplyr::arrange(.data$Trait, .data$Rank_high_value, .by_group = TRUE) |>
    dplyr::ungroup()

  top_15 <- rankings |>
    dplyr::filter(.data$Rank_high_value <= 15L)

  extremos_15 <- rankings |>
    dplyr::filter(
      .data$Rank_high_value <= 15L | .data$Rank_low_value <= 15L
    ) |>
    dplyr::mutate(
      Ranking_side = dplyr::if_else(
        .data$Rank_high_value <= 15L,
        "high",
        "low"
      )
    )

  resultado <- list(
    all_genomic_values = valores,
    rankings_by_trait = rankings,
    top_15_by_trait = top_15,
    extreme_15_by_trait = extremos_15,
    multi_trait_index_status = paste(
      "Not calculated: selection directions and economic weights",
      "must be supplied by the breeding program."
    ),
    configuration = configuracao
  )

  saveRDS(resultado, configuracao$arquivo_selecao)
  utils::write.csv(
    rankings,
    file.path("output", "trait_specific_genomic_rankings.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(
    top_15,
    file.path("output", "top_15_candidates_by_trait.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(
    extremos_15,
    file.path("output", "high_and_low_15_candidates_by_trait.csv"),
    row.names = FALSE,
    na = ""
  )

  resultado
}
