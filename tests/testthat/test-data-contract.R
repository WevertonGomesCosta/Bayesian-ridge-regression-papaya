testthat::test_that("identificadores genotípicos e fenotípicos permanecem alinhados", {
  testthat::expect_length(objeto_teste$ids, 150L)
  testthat::expect_equal(length(unique(objeto_teste$ids)), 150L)
  testthat::expect_identical(objeto_teste$ids, rownames(objeto_teste$fenotipos))
  testthat::expect_true("144B" %in% objeto_teste$ids)
  testthat::expect_false(anyNA(objeto_teste$fenotipos))
})

testthat::test_that("inventário SSR corresponde às planilhas auditadas", {
  testthat::expect_equal(dim(objeto_teste$codigos_ssr), c(150L, 35L))
  testthat::expect_equal(sum(is.na(objeto_teste$codigos_ssr)), 126L)
  testthat::expect_equal(ncol(objeto_teste$dosagens_ssr), 72L)
  testthat::expect_false(
    objeto_teste$auditoria$locos$Keep_locus[
      objeto_teste$auditoria$locos$Locus == "P6K1129CC"
    ]
  )
})

testthat::test_that("oito folds são balanceados e preservam todas as famílias no treino", {
  tamanhos <- tabulate(objeto_teste$folds, nbins = 8L)
  testthat::expect_lte(max(tamanhos) - min(tamanhos), 1L)

  for (fold in seq_len(8L)) {
    treino <- objeto_teste$folds != fold
    testthat::expect_setequal(
      unique(as.character(objeto_teste$metadados$FAM[treino])),
      levels(objeto_teste$metadados$FAM)
    )
  }
})
