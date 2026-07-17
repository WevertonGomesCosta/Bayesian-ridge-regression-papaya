testthat::test_that("dosagens alélicas somam dois em chamadas diploides", {
  codificacao <- codificar_dosagens_ssr(objeto_teste$codigos_ssr)

  for (loco in colnames(objeto_teste$codigos_ssr)) {
    colunas <- codificacao$mapa_colunas$Marker_column[
      codificacao$mapa_colunas$Locus == loco
    ]
    chamado <- !is.na(objeto_teste$codigos_ssr[, loco])
    soma <- rowSums(codificacao$dosagens[chamado, colunas, drop = FALSE])
    testthat::expect_equal(unname(soma), rep(2, sum(chamado)))
  }
})

testthat::test_that("matrizes de marcador e relacionamento são numericamente válidas", {
  preparacao <- objeto_teste$preparacao_completa
  testthat::expect_false(anyNA(preparacao$marcadores))
  testthat::expect_equal(preparacao$matriz_g, t(preparacao$matriz_g), tolerance = 1e-10)
  autovalores <- eigen(preparacao$matriz_g, symmetric = TRUE, only.values = TRUE)$values
  testthat::expect_gte(min(autovalores), -1e-8)
})

testthat::test_that("efeitos fixos têm posto completo em todos os treinamentos", {
  x <- objeto_teste$matriz_efeitos_fixos$com_intercepto
  for (fold in seq_len(8L)) {
    treino <- objeto_teste$folds != fold
    testthat::expect_equal(qr(x[treino, , drop = FALSE])$rank, ncol(x))
  }
})
