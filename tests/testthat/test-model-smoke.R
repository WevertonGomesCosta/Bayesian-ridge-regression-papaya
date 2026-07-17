testthat::test_that("RR-BLUP e GBLUP produzem predições finitas em um fold", {
  testthat::skip_if_not_installed("rrBLUP")

  y <- objeto_teste$fenotipos[, "MMCOM"]
  fold <- 1L
  treino <- which(objeto_teste$folds != fold)
  teste <- which(objeto_teste$folds == fold)
  prep <- objeto_teste$preparacao_folds[[fold]]
  x <- objeto_teste$matriz_efeitos_fixos$com_intercepto

  rr <- rrBLUP::mixed.solve(
    y = y[treino],
    X = x[treino, , drop = FALSE],
    Z = prep$marcadores[treino, , drop = FALSE]
  )
  pred_rr <- as.vector(x[teste, , drop = FALSE] %*% rr$beta) +
    as.vector(prep$marcadores[teste, , drop = FALSE] %*% rr$u)

  y_cv <- y
  y_cv[teste] <- NA_real_
  z <- diag(length(y))
  gb <- rrBLUP::mixed.solve(
    y = y_cv,
    X = x,
    Z = z,
    K = prep$matriz_g
  )
  pred_gb <- as.vector(x[teste, , drop = FALSE] %*% gb$beta) + gb$u[teste]

  testthat::expect_true(all(is.finite(pred_rr)))
  testthat::expect_true(all(is.finite(pred_gb)))
})

testthat::test_that("BGLR executa o contrato mínimo de BRR", {
  testthat::skip_if_not_installed("BGLR")

  configuracao <- obter_configuracao("smoke")
  configuracao$mcmc$n_iter <- 1500L
  configuracao$mcmc$burn_in <- 500L
  configuracao$mcmc$thin <- 5L

  y <- objeto_teste$fenotipos[, "MMCOM"]
  fold <- 1L
  treino <- which(objeto_teste$folds != fold)
  prep <- objeto_teste$preparacao_folds[[fold]]
  x <- objeto_teste$matriz_efeitos_fixos$sem_intercepto
  especificacao <- as.list(configuracao$catalogo_bayesiano[1L, , drop = FALSE])

  ajuste <- ajustar_bglr_unico(
    y = y[treino],
    efeitos_fixos_sem_intercepto = x[treino, , drop = FALSE],
    marcadores = prep$marcadores[treino, , drop = FALSE],
    especificacao_modelo = especificacao,
    configuracao = configuracao,
    semente = 20260717L
  )

  testthat::expect_true(is.finite(ajuste$ajuste$fit$DIC))
  testthat::expect_length(
    ajuste$ajuste$ETA[["marcadores"]]$b,
    ncol(prep$marcadores)
  )
})
