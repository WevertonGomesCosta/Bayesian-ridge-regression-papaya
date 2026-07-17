# Funções leves para as páginas do relatório --------------------------------

carregar_resultado <- function(caminho) {
  if (file.exists(caminho)) readRDS(caminho) else NULL
}


tabela_relatorio <- function(
    dados,
    legenda = NULL,
    digitos = 3L,
    rolagem = FALSE,
    altura = "420px") {
  tabela <- kableExtra::kbl(
    dados,
    format = "html",
    digits = digitos,
    caption = legenda,
    escape = FALSE,
    align = "l"
  ) |>
    kableExtra::kable_styling(
      bootstrap_options = c("striped", "hover", "condensed", "responsive"),
      full_width = FALSE,
      position = "left"
    )

  if (rolagem) {
    tabela <- kableExtra::scroll_box(tabela, width = "100%", height = altura)
  }

  tabela
}


tema_relatorio <- function() {
  ggthemes::theme_gdocs(base_size = 11) +
    ggplot2::theme(
      legend.position = "bottom",
      strip.text = ggplot2::element_text(face = "bold"),
      plot.title.position = "plot"
    )
}


mensagem_resultado_ausente <- function(caminho, idioma = c("en", "pt")) {
  idioma <- match.arg(idioma)

  if (idioma == "pt") {
    paste0(
      "> **Resultado ainda não calculado.** O arquivo `", caminho,
      "` será criado pelos perfis `smoke` ou `full`. O perfil `site` ",
      "mantém a construção rápida e não inicia análises pesadas.\n"
    )
  } else {
    paste0(
      "> **Result not calculated yet.** File `", caminho,
      "` is created by the `smoke` or `full` profiles. The `site` profile ",
      "keeps website builds lightweight and does not start heavy analyses.\n"
    )
  }
}


resumir_metricas_folds <- function(metricas) {
  metricas |>
    dplyr::group_by(.data$Trait, .data$Model) |>
    dplyr::summarise(
      Mean_correlation = mean(.data$Correlation, na.rm = TRUE),
      SD_correlation = stats::sd(.data$Correlation, na.rm = TRUE),
      Mean_RMSE = mean(.data$RMSE, na.rm = TRUE),
      Mean_MAE = mean(.data$MAE, na.rm = TRUE),
      Mean_bias = mean(.data$Bias, na.rm = TRUE),
      Mean_time_seconds = mean(.data$Time_seconds, na.rm = TRUE),
      .groups = "drop"
    )
}
