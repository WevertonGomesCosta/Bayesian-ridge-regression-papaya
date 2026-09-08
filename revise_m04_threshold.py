from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
FILES = {
    "pt": ROOT / "analysis" / "04_results_pt.Rmd",
    "en": ROOT / "analysis" / "04_results_en.Rmd",
}


def heading_pos(text, number):
    m = re.search(rf"^## {number}\. ", text, flags=re.M)
    if not m:
        raise RuntimeError(f"heading ## {number}. not found")
    return m.start()


def section(text, number):
    start = heading_pos(text, number)
    try:
        end = heading_pos(text, number + 1)
    except RuntimeError:
        end = len(text)
    return text[start:end].rstrip() + "\n\n"


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 occurrence, found {n}")
    return text.replace(old, new, 1)


def remove_subsection_42(text):
    m1 = re.search(r"^### 4\.2 ", text, flags=re.M)
    m2 = re.search(r"^### 4\.3 ", text, flags=re.M)
    if not m1 or not m2 or m2.start() <= m1.start():
        raise RuntimeError("could not isolate subsection 4.2")
    text = text[:m1.start()] + text[m2.start():]
    text = re.sub(r"^### 4\.3 ", "### 4.2 ", text, count=1, flags=re.M)
    text = re.sub(r"^### 4\.4 ", "### 4.3 ", text, count=1, flags=re.M)
    text = re.sub(r"^### 4\.5 ", "### 4.4 ", text, count=1, flags=re.M)
    return text


OBJECTIVE_PT = r'''## 1. Objetivo

A partir das predições OOF, métricas de desempenho e diagnósticos obtidos no
Módulo 03, este módulo final organiza a comparação dos métodos e a seleção
genômica em uma sequência mais direta: **comparar → escolher o método → definir
a elegibilidade da característica → interpretar os GEBVs → selecionar
indivíduos**.

A escolha do método é específica por característica e prioriza desempenho
preditivo: maior correlação OOF agrupada, seguida de menor RMSE e menor MAE; o
DIC é mantido como evidência complementar e critério final de desempate. Os
diagnósticos MCMC são resumidos como verificação global da adequação das
cadeias, mas não são transformados em uma regra de exclusão ou revisão.

A seleção de indivíduos é realizada apenas para características com evidência
preditiva mínima definida previamente. Nesta versão, uma característica é
elegível quando o método escolhido apresenta correlação OOF maior que 0,30 e
NRMSE menor que 1, isto é, RMSE inferior a um desvio-padrão fenotípico. A
proporção selecionada permanece em 20% dos indivíduos por característica
elegível.

Para facilitar a interpretação na escala original, o componente genômico OOF
centrado é preservado e também apresentado após a soma da média fenotípica da
característica. Essa transformação desloca a escala, mas não altera a ordenação
dos indivíduos dentro de uma característica.

'''

OBJECTIVE_EN = r'''## 1. Objective

Using the OOF predictions, performance metrics, and diagnostics obtained in
Module 03, this final module organizes model comparison and genomic selection
in a more direct sequence: **compare → choose the method → define trait
eligibility → interpret GEBVs → select individuals**.

Method choice is trait-specific and prioritizes predictive performance: highest
pooled OOF correlation, followed by lowest RMSE and lowest MAE; DIC is retained
as complementary evidence and a final tie-breaker. MCMC diagnostics are
summarized as a global check of chain adequacy, but they are not converted into
an exclusion or review rule.

Individuals are selected only for traits that meet a pre-defined minimum level
of predictive evidence. In this version, a trait is eligible when the selected
method has OOF correlation greater than 0.30 and NRMSE lower than 1, that is,
RMSE lower than one phenotypic standard deviation. The selected proportion
remains 20% of the individuals for each eligible trait.

To improve interpretation on the original trait scale, the centered OOF genomic
component is preserved and is also presented after adding the phenotypic trait
mean. This transformation shifts the scale but does not change the ranking of
individuals within a trait.

'''

SEC5_PT = r'''## 5. Escolha do método e elegibilidade para seleção

### 5.1 Critérios adotados

A escolha do método e a decisão de usar uma característica na seleção são duas
etapas distintas. Primeiro, os sete métodos são ordenados dentro de cada
característica pela correlação OOF agrupada; empates são resolvidos, nesta
ordem, por menor RMSE, menor MAE e menor DIC médio. Assim, não é criado um escore
artificial que misture métricas de naturezas diferentes.

Depois de escolhido o método, a característica é considerada elegível para
seleção apenas quando satisfaz simultaneamente dois critérios de desempenho:

\[
r_{OOF} > 0{,}30
\]

e

\[
NRMSE = \frac{RMSE}{s_y} < 1,
\]

em que \(s_y\) é o desvio-padrão fenotípico observado da característica. O
segundo critério exige que o erro do modelo seja menor que a dispersão
fenotípica observada e funciona como complemento ao limiar de correlação.

```{r selection-parameters}
CORRELATION_SELECTION_THRESHOLD <- 0.30
NRMSE_SELECTION_THRESHOLD <- 1.00
SELECTION_PROPORTION <- 0.20

selection_objective_map <- c(
  MMCOM = "increase",
  PRODCOM = "increase",
  PRODEF = "decrease",
  CF = "increase",
  DF = "increase",
  DCI = "decrease",
  EP = "increase",
  FFC = "increase",
  FFP = "increase",
  SS = "increase"
)

selection_objectives <- data.frame(
  Trait = traits,
  Selection_objective = unname(selection_objective_map[traits]),
  stringsAsFactors = FALSE
)

selection_parameters <- data.frame(
  Parâmetro = c(
    "Escolha do método",
    "Correlação OOF mínima",
    "NRMSE máximo",
    "Proporção selecionada"
  ),
  Regra = c(
    "Maior r; desempates por menor RMSE, menor MAE e menor DIC",
    "> 0,30",
    "< 1,00",
    "20% por característica elegível"
  ),
  stringsAsFactors = FALSE
)

tabela_html(
  selection_parameters,
  caption = "Parâmetros adotados para escolha do método e seleção genômica",
  col.names = c("Parâmetro", "Regra")
)
```

### 5.2 Método escolhido e elegibilidade por característica

A média e o desvio-padrão fenotípicos são calculados uma única vez por
característica a partir dos valores observados. A duplicação das observações
entre métodos é removida antes desse cálculo.

```{r final-model-selection}
trait_scale <- predictions |>
  distinct(Trait, IND, Observed) |>
  group_by(Trait) |>
  summarise(
    Phenotypic_mean = mean(Observed, na.rm = TRUE),
    Phenotypic_SD = sd(Observed, na.rm = TRUE),
    .groups = "drop"
  )

model_selection <- model_comparison |>
  group_by(Trait) |>
  arrange(desc(r), RMSE, MAE, Mean_DIC, .by_group = TRUE) |>
  slice(1L) |>
  ungroup() |>
  transmute(
    Trait,
    Selected_method = Method,
    r,
    p_value,
    RMSE,
    MAE,
    Bias,
    Slope,
    Mean_DIC,
    Delta_DIC,
    Wprob,
    ER
  ) |>
  left_join(trait_scale, by = "Trait") |>
  left_join(selection_objectives, by = "Trait") |>
  mutate(
    NRMSE = RMSE / Phenotypic_SD,
    Predictive_skill_vs_SD = 1 - NRMSE,
    Eligible_by_correlation = r > CORRELATION_SELECTION_THRESHOLD,
    Eligible_by_error = NRMSE < NRMSE_SELECTION_THRESHOLD,
    Selection_eligible = Eligible_by_correlation & Eligible_by_error
  ) |>
  arrange(match(Trait, traits))

eligible_traits <- model_selection |>
  filter(Selection_eligible) |>
  pull(Trait)
```

A tabela principal concentra as métricas necessárias para interpretar a escolha
do método e a elegibilidade, evitando tabelas paralelas para a mesma decisão.
O p-valor da correlação continua disponível no objeto científico, mas não é
usado como filtro de seleção.

```{r model-selection-table}
# DISPLAY-ONLY START
model_selection_display <- model_selection |>
  mutate(
    Método = unname(method_labels[Selected_method]),
    Objetivo = unname(selection_objective_labels[Selection_objective]),
    Elegível = if_else(Selection_eligible, "Sim", "Não")
  ) |>
  transmute(
    Trait,
    Método,
    Objetivo,
    r = sprintf("%.3f", r),
    RMSE = sprintf("%.3f", RMSE),
    NRMSE = sprintf("%.3f", NRMSE),
    MAE = sprintf("%.3f", MAE),
    Bias = sprintf("%.3f", Bias),
    Slope = sprintf("%.3f", Slope),
    DIC = sprintf("%.2f", Mean_DIC),
    Elegível
  )

tabela_html(
  model_selection_display,
  caption = "Método escolhido e elegibilidade para seleção por característica",
  col.names = c(
    "Característica", "Método", "Objetivo", "r", "RMSE", "NRMSE",
    "MAE", "Viés", "Inclinação", "DIC médio", "Elegível"
  )
)
# DISPLAY-ONLY END
```

### 5.3 Síntese dos diagnósticos MCMC

Os diagnósticos calculados no Módulo 03 são resumidos aqui sem criar uma etapa
de revisão. Uma cadeia é contabilizada como não sinalizada quando nenhum dos
parâmetros monitorados daquele ajuste recebeu `Review_flag` no objeto de origem.
O nome do campo é preservado por rastreabilidade, mas a interpretação nesta
seção é apenas de síntese diagnóstica.

```{r convergence-overview}
fit_convergence <- convergence |>
  group_by(Run_id, Trait, Method) |>
  summarise(
    Diagnostic_flag = any(Review_flag, na.rm = TRUE),
    .groups = "drop"
  )

convergence_overview <- data.frame(
  Nível = c("Ajustes", "Parâmetros monitorados"),
  Total = c(nrow(fit_convergence), nrow(convergence)),
  Sem_sinalização = c(
    sum(!fit_convergence$Diagnostic_flag),
    sum(!convergence$Review_flag, na.rm = TRUE)
  )
) |>
  mutate(
    Proporção_sem_sinalização = Sem_sinalização / Total
  )

tabela_html(
  convergence_overview,
  digits = 4,
  caption = "Síntese global dos diagnósticos MCMC",
  col.names = c("Nível", "Total", "Sem sinalização", "Proporção")
)
```

A predominância de ajustes e parâmetros sem sinalização sustenta a conclusão de
que a maioria das cadeias apresentou comportamento compatível com convergência
segundo os diagnósticos monitorados. Essa síntese não prova convergência de
todos os efeitos de marcador individualmente e não participa da escolha do
método.

### 5.4 Relação entre valores observados e preditos

Além das métricas numéricas, a relação observado × predito é mostrada para o
método escolhido em cada característica. A linha tracejada representa a relação
1:1; a linha ajustada representa a regressão linear dos valores observados sobre
as predições OOF. Desvios entre as duas ajudam a visualizar calibração, além da
associação resumida por \(r\).

```{r observed-predicted-figure, fig.width=12, fig.height=10, fig.alt="Gráficos de dispersão em painéis dos valores observados contra os valores OOF preditos pelo método escolhido em cada característica, com linha 1:1 e reta de regressão linear."}
selected_predictions <- predictions |>
  inner_join(
    model_selection |>
      select(Trait, Selected_method, r, Selection_eligible),
    by = "Trait"
  ) |>
  filter(Method == Selected_method) |>
  mutate(
    Method_label = unname(method_labels[Method]),
    Facet = paste0(
      Trait, " — ", Method_label,
      "\nr = ", sprintf("%.3f", r)
    )
  )

observed_predicted_plot <- selected_predictions |>
  ggplot(aes(x = Predicted, y = Observed)) +
  geom_abline(intercept = 0, slope = 1, linetype = 2, linewidth = 0.5) +
  geom_point(alpha = 0.65, size = 1.6) +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE, linewidth = 0.7) +
  facet_wrap(~ Facet, scales = "free", ncol = 2) +
  labs(
    x = "Valor OOF predito",
    y = "Valor observado",
    title = "Relação entre valores observados e preditos"
  ) +
  project_theme +
  theme(legend.position = "none")

observed_predicted_plot
```

'''

SEC5_EN = r'''## 5. Method choice and eligibility for selection

### 5.1 Adopted criteria

Method choice and the decision to use a trait for selection are two distinct
steps. First, the seven methods are ordered within each trait by pooled OOF
correlation; ties are resolved, in this order, by lower RMSE, lower MAE, and
lower mean DIC. Thus, no artificial score is created by mixing metrics with
different meanings.

After the method is chosen, the trait is considered eligible for selection only
when it simultaneously satisfies two performance criteria:

\[
r_{OOF} > 0.30
\]

and

\[
NRMSE = \frac{RMSE}{s_y} < 1,
\]

where \(s_y\) is the observed phenotypic standard deviation of the trait. The
second criterion requires model error to be lower than the observed phenotypic
dispersion and complements the correlation threshold.

```{r selection-parameters}
CORRELATION_SELECTION_THRESHOLD <- 0.30
NRMSE_SELECTION_THRESHOLD <- 1.00
SELECTION_PROPORTION <- 0.20

selection_objective_map <- c(
  MMCOM = "increase",
  PRODCOM = "increase",
  PRODEF = "decrease",
  CF = "increase",
  DF = "increase",
  DCI = "decrease",
  EP = "increase",
  FFC = "increase",
  FFP = "increase",
  SS = "increase"
)

selection_objectives <- data.frame(
  Trait = traits,
  Selection_objective = unname(selection_objective_map[traits]),
  stringsAsFactors = FALSE
)

selection_parameters <- data.frame(
  Parameter = c(
    "Method choice",
    "Minimum OOF correlation",
    "Maximum NRMSE",
    "Selected proportion"
  ),
  Rule = c(
    "Highest r; ties by lower RMSE, lower MAE, and lower DIC",
    "> 0.30",
    "< 1.00",
    "20% per eligible trait"
  ),
  stringsAsFactors = FALSE
)

table_html(
  selection_parameters,
  caption = "Parameters adopted for method choice and genomic selection",
  col.names = c("Parameter", "Rule")
)
```

### 5.2 Selected method and trait eligibility

The phenotypic mean and standard deviation are calculated once per trait from
the observed values. Duplicate observations across methods are removed before
this calculation.

```{r final-model-selection}
trait_scale <- predictions |>
  distinct(Trait, IND, Observed) |>
  group_by(Trait) |>
  summarise(
    Phenotypic_mean = mean(Observed, na.rm = TRUE),
    Phenotypic_SD = sd(Observed, na.rm = TRUE),
    .groups = "drop"
  )

model_selection <- model_comparison |>
  group_by(Trait) |>
  arrange(desc(r), RMSE, MAE, Mean_DIC, .by_group = TRUE) |>
  slice(1L) |>
  ungroup() |>
  transmute(
    Trait,
    Selected_method = Method,
    r,
    p_value,
    RMSE,
    MAE,
    Bias,
    Slope,
    Mean_DIC,
    Delta_DIC,
    Wprob,
    ER
  ) |>
  left_join(trait_scale, by = "Trait") |>
  left_join(selection_objectives, by = "Trait") |>
  mutate(
    NRMSE = RMSE / Phenotypic_SD,
    Predictive_skill_vs_SD = 1 - NRMSE,
    Eligible_by_correlation = r > CORRELATION_SELECTION_THRESHOLD,
    Eligible_by_error = NRMSE < NRMSE_SELECTION_THRESHOLD,
    Selection_eligible = Eligible_by_correlation & Eligible_by_error
  ) |>
  arrange(match(Trait, traits))

eligible_traits <- model_selection |>
  filter(Selection_eligible) |>
  pull(Trait)
```

The main table concentrates the metrics needed to interpret method choice and
eligibility, avoiding parallel tables for the same decision. The correlation
p-value remains available in the scientific object but is not used as a
selection filter.

```{r model-selection-table}
# DISPLAY-ONLY START
model_selection_display <- model_selection |>
  mutate(
    Method_label = unname(method_labels[Selected_method]),
    Objective = unname(selection_objective_labels[Selection_objective]),
    Eligible = if_else(Selection_eligible, "Yes", "No")
  ) |>
  transmute(
    Trait,
    Method_label,
    Objective,
    r = sprintf("%.3f", r),
    RMSE = sprintf("%.3f", RMSE),
    NRMSE = sprintf("%.3f", NRMSE),
    MAE = sprintf("%.3f", MAE),
    Bias = sprintf("%.3f", Bias),
    Slope = sprintf("%.3f", Slope),
    DIC = sprintf("%.2f", Mean_DIC),
    Eligible
  )

table_html(
  model_selection_display,
  caption = "Selected method and eligibility for selection by trait",
  col.names = c(
    "Trait", "Method", "Objective", "r", "RMSE", "NRMSE",
    "MAE", "Bias", "Slope", "Mean DIC", "Eligible"
  )
)
# DISPLAY-ONLY END
```

### 5.3 Summary of MCMC diagnostics

Diagnostics calculated in Module 03 are summarized here without creating a
review stage. A chain is counted as not flagged when none of the monitored
parameters in that fit received `Review_flag` in the source object. The field
name is preserved for traceability, but its interpretation here is only a
diagnostic summary.

```{r convergence-overview}
fit_convergence <- convergence |>
  group_by(Run_id, Trait, Method) |>
  summarise(
    Diagnostic_flag = any(Review_flag, na.rm = TRUE),
    .groups = "drop"
  )

convergence_overview <- data.frame(
  Level = c("Fits", "Monitored parameters"),
  Total = c(nrow(fit_convergence), nrow(convergence)),
  Without_flags = c(
    sum(!fit_convergence$Diagnostic_flag),
    sum(!convergence$Review_flag, na.rm = TRUE)
  )
) |>
  mutate(
    Proportion_without_flags = Without_flags / Total
  )

table_html(
  convergence_overview,
  digits = 4,
  caption = "Global summary of MCMC diagnostics",
  col.names = c("Level", "Total", "Without flags", "Proportion")
)
```

The predominance of fits and parameters without flags supports the conclusion
that most chains showed behavior compatible with convergence according to the
monitored diagnostics. This summary does not prove convergence of every marker
effect individually and does not participate in method choice.

### 5.4 Relationship between observed and predicted values

In addition to numerical metrics, observed versus predicted values are shown
for the selected method in each trait. The dashed line represents the 1:1
relationship; the fitted line is the linear regression of observed values on
the OOF predictions. Differences between the two help visualize calibration in
addition to the association summarized by \(r\).

```{r observed-predicted-figure, fig.width=12, fig.height=10, fig.alt="Faceted scatterplots of observed values against OOF values predicted by the selected method for each trait, with a 1:1 line and fitted linear regression."}
selected_predictions <- predictions |>
  inner_join(
    model_selection |>
      select(Trait, Selected_method, r, Selection_eligible),
    by = "Trait"
  ) |>
  filter(Method == Selected_method) |>
  mutate(
    Method_label = unname(method_labels[Method]),
    Facet = paste0(
      Trait, " — ", Method_label,
      "\nr = ", sprintf("%.3f", r)
    )
  )

observed_predicted_plot <- selected_predictions |>
  ggplot(aes(x = Predicted, y = Observed)) +
  geom_abline(intercept = 0, slope = 1, linetype = 2, linewidth = 0.5) +
  geom_point(alpha = 0.65, size = 1.6) +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE, linewidth = 0.7) +
  facet_wrap(~ Facet, scales = "free", ncol = 2) +
  labs(
    x = "OOF predicted value",
    y = "Observed value",
    title = "Relationship between observed and predicted values"
  ) +
  project_theme +
  theme(legend.position = "none")

observed_predicted_plot
```

'''

SEC7_PT = r'''## 7. GEBVs OOF e escala fenotípica interpretável

### 7.1 Componente genômico cross-fitted

O componente genômico de cada indivíduo continua sendo obtido no fold em que o
fenótipo desse indivíduo foi mascarado. Portanto, `GEBV_centered` é um escore
OOF cross-fitted e não um valor genético final proveniente de reajuste com os
150 fenótipos.

Para facilitar a leitura na unidade da característica, também é calculado:

\[
GEBV_{escala} = \bar{y} + GEBV_{centrado}.
\]

A soma da média fenotípica é um deslocamento de escala. Ela não altera a ordem
dos indivíduos e não deve ser confundida com a predição fenotípica completa,
pois outros componentes do modelo podem contribuir para `Predicted`.

```{r selected-oof-genomic-values}
selected_oof_genomic_values <- predictions |>
  inner_join(
    model_selection |>
      select(
        Trait, Selected_method, r, p_value, NRMSE,
        Selection_eligible, Selection_objective
      ),
    by = "Trait"
  ) |>
  filter(Method == Selected_method) |>
  left_join(trait_scale, by = "Trait") |>
  transmute(
    IND,
    Trait,
    Fold,
    Method,
    Observed,
    Predicted,
    Selection_objective,
    Selection_eligible,
    OOF_r = r,
    OOF_p_value = p_value,
    OOF_NRMSE = NRMSE,
    Phenotypic_mean,
    GEBV_centered = Genomic_component,
    GEBV_on_trait_scale = Phenotypic_mean + Genomic_component
  ) |>
  arrange(match(Trait, traits), IND)
```

'''

SEC7_EN = r'''## 7. OOF GEBVs and an interpretable phenotypic scale

### 7.1 Cross-fitted genomic component

The genomic component of each individual continues to be obtained in the fold
in which that individual's phenotype was masked. Therefore, `GEBV_centered` is
a cross-fitted OOF score and not a final genetic value from refitting all 150
phenotypes.

To facilitate interpretation in the trait unit, the following quantity is also
calculated:

\[
GEBV_{scale} = \bar{y} + GEBV_{centered}.
\]

Adding the phenotypic mean shifts the scale. It does not change the ordering of
individuals and should not be confused with the complete phenotypic prediction,
because other model components may contribute to `Predicted`.

```{r selected-oof-genomic-values}
selected_oof_genomic_values <- predictions |>
  inner_join(
    model_selection |>
      select(
        Trait, Selected_method, r, p_value, NRMSE,
        Selection_eligible, Selection_objective
      ),
    by = "Trait"
  ) |>
  filter(Method == Selected_method) |>
  left_join(trait_scale, by = "Trait") |>
  transmute(
    IND,
    Trait,
    Fold,
    Method,
    Observed,
    Predicted,
    Selection_objective,
    Selection_eligible,
    OOF_r = r,
    OOF_p_value = p_value,
    OOF_NRMSE = NRMSE,
    Phenotypic_mean,
    GEBV_centered = Genomic_component,
    GEBV_on_trait_scale = Phenotypic_mean + Genomic_component
  ) |>
  arrange(match(Trait, traits), IND)
```

'''

SEC8_PT = r'''## 8. Seleção de indivíduos nas características elegíveis

### 8.1 Ranking e intensidade de seleção

Somente as características que satisfazem simultaneamente `r > 0,30` e
`NRMSE < 1` entram nesta etapa. Em cada característica elegível, os indivíduos
são ordenados pelo GEBV na escala da característica, respeitando a direção de
melhoramento. Para características a reduzir, o sinal é invertido apenas para a
ordenação. A intensidade adotada permanece em 20% e `IND` é usado somente como
critério determinístico de desempate exato.

```{r genomic-ranking}
genomic_ranking <- selected_oof_genomic_values |>
  filter(Selection_eligible) |>
  mutate(
    Selection_score = case_when(
      Selection_objective == "increase" ~ GEBV_on_trait_scale,
      Selection_objective == "decrease" ~ -GEBV_on_trait_scale,
      TRUE ~ NA_real_
    )
  ) |>
  group_by(Trait) |>
  arrange(desc(Selection_score), IND, .by_group = TRUE) |>
  mutate(Rank = row_number()) |>
  ungroup() |>
  arrange(match(Trait, traits), Rank)

selection_sizes <- genomic_ranking |>
  count(Trait, name = "N_available") |>
  mutate(
    Selection_proportion = SELECTION_PROPORTION,
    N_selected = pmax(
      1L,
      as.integer(ceiling(Selection_proportion * N_available))
    )
  ) |>
  arrange(match(Trait, traits))

selected_individuals_by_trait <- genomic_ranking |>
  inner_join(selection_sizes, by = "Trait") |>
  filter(Rank <= N_selected) |>
  left_join(
    matrices_object$metadata |>
      select(IND, FAM),
    by = "IND"
  ) |>
  select(
    Trait, Rank, IND, FAM, Method, Selection_objective,
    GEBV_centered, GEBV_on_trait_scale, Selection_score,
    OOF_r, OOF_NRMSE, Selection_proportion,
    N_available, N_selected
  ) |>
  arrange(match(Trait, traits), Rank)
```

### 8.2 Prévia dos indivíduos selecionados

A tabela mostra os cinco primeiros indivíduos de cada característica elegível.
O objeto `selected_individuals_by_trait` mantém o conjunto completo dos 20%
selecionados.

```{r proportional-selection-preview}
# DISPLAY-ONLY START
selection_preview <- selected_individuals_by_trait |>
  group_by(Trait) |>
  slice_head(n = 5) |>
  ungroup() |>
  mutate(
    Método = unname(method_labels[Method]),
    Objetivo = unname(selection_objective_labels[Selection_objective])
  ) |>
  transmute(
    Trait,
    Rank,
    IND,
    FAM,
    Método,
    Objetivo,
    GEBV = sprintf("%.3f", GEBV_on_trait_scale),
    r = sprintf("%.3f", OOF_r),
    NRMSE = sprintf("%.3f", OOF_NRMSE)
  )

tabela_html(
  selection_preview,
  caption = "Cinco primeiros indivíduos selecionados por característica elegível",
  col.names = c(
    "Característica", "Rank", "IND", "FAM", "Método", "Objetivo",
    "GEBV + média", "r OOF", "NRMSE"
  )
)
# DISPLAY-ONLY END
```

'''

SEC8_EN = r'''## 8. Individual selection in eligible traits

### 8.1 Ranking and selection intensity

Only traits that simultaneously satisfy `r > 0.30` and `NRMSE < 1` enter this
stage. Within each eligible trait, individuals are ordered by the GEBV on the
trait scale while respecting the breeding objective. For traits to be reduced,
the sign is reversed only for ranking. The adopted selection intensity remains
20%, and `IND` is used only as a deterministic tie-breaker for exact ties.

```{r genomic-ranking}
genomic_ranking <- selected_oof_genomic_values |>
  filter(Selection_eligible) |>
  mutate(
    Selection_score = case_when(
      Selection_objective == "increase" ~ GEBV_on_trait_scale,
      Selection_objective == "decrease" ~ -GEBV_on_trait_scale,
      TRUE ~ NA_real_
    )
  ) |>
  group_by(Trait) |>
  arrange(desc(Selection_score), IND, .by_group = TRUE) |>
  mutate(Rank = row_number()) |>
  ungroup() |>
  arrange(match(Trait, traits), Rank)

selection_sizes <- genomic_ranking |>
  count(Trait, name = "N_available") |>
  mutate(
    Selection_proportion = SELECTION_PROPORTION,
    N_selected = pmax(
      1L,
      as.integer(ceiling(Selection_proportion * N_available))
    )
  ) |>
  arrange(match(Trait, traits))

selected_individuals_by_trait <- genomic_ranking |>
  inner_join(selection_sizes, by = "Trait") |>
  filter(Rank <= N_selected) |>
  left_join(
    matrices_object$metadata |>
      select(IND, FAM),
    by = "IND"
  ) |>
  select(
    Trait, Rank, IND, FAM, Method, Selection_objective,
    GEBV_centered, GEBV_on_trait_scale, Selection_score,
    OOF_r, OOF_NRMSE, Selection_proportion,
    N_available, N_selected
  ) |>
  arrange(match(Trait, traits), Rank)
```

### 8.2 Preview of selected individuals

The table shows the first five individuals for each eligible trait. The
`selected_individuals_by_trait` object retains the complete set of the selected
20%.

```{r proportional-selection-preview}
# DISPLAY-ONLY START
selection_preview <- selected_individuals_by_trait |>
  group_by(Trait) |>
  slice_head(n = 5) |>
  ungroup() |>
  mutate(
    Method_label = unname(method_labels[Method]),
    Objective = unname(selection_objective_labels[Selection_objective])
  ) |>
  transmute(
    Trait,
    Rank,
    IND,
    FAM,
    Method_label,
    Objective,
    GEBV = sprintf("%.3f", GEBV_on_trait_scale),
    r = sprintf("%.3f", OOF_r),
    NRMSE = sprintf("%.3f", OOF_NRMSE)
  )

table_html(
  selection_preview,
  caption = "First five selected individuals for each eligible trait",
  col.names = c(
    "Trait", "Rank", "IND", "FAM", "Method", "Objective",
    "GEBV + mean", "OOF r", "NRMSE"
  )
)
# DISPLAY-ONLY END
```

'''

SEC9_PT = r'''## 9. Recorrência entre características elegíveis

### 9.1 Definição

A recorrência é descritiva e usa somente os rankings das características que
passaram pelos dois limiares de elegibilidade. Para cada indivíduo, conta-se em
quantas dessas características ele aparece entre os 20% selecionados. A
frequência é calculada em relação ao número de características elegíveis; não é
construído um índice multicaracterístico nem são atribuídos pesos entre
características.

```{r multitrait-recurrence}
recurrence_counts <- selected_individuals_by_trait |>
  group_by(IND, FAM) |>
  summarise(
    N_traits = n(),
    Traits = paste(Trait, collapse = ", "),
    Best_rank = min(Rank),
    Mean_rank_present = mean(Rank),
    .groups = "drop"
  )

n_eligible_traits <- length(eligible_traits)

multitrait_recurrence <- matrices_object$metadata |>
  select(IND, FAM) |>
  left_join(recurrence_counts, by = c("IND", "FAM")) |>
  mutate(
    N_traits = tidyr::replace_na(N_traits, 0L),
    Traits = tidyr::replace_na(Traits, ""),
    Best_rank = if_else(N_traits == 0L, NA_integer_, Best_rank),
    Mean_rank_present = if_else(
      N_traits == 0L,
      NA_real_,
      Mean_rank_present
    ),
    Selection_frequency = if_else(
      n_eligible_traits > 0,
      N_traits / n_eligible_traits,
      0
    ),
    Recurrence_class = case_when(
      N_traits >= 4L ~ "high_4plus",
      N_traits == 3L ~ "intermediate_3",
      N_traits == 2L ~ "broad_2",
      N_traits == 1L ~ "specific_1",
      TRUE ~ "none_0"
    )
  ) |>
  arrange(desc(N_traits), FAM, IND)

recurrence_distribution <- multitrait_recurrence |>
  count(N_traits, Recurrence_class, name = "N_individuals") |>
  mutate(
    Proportion_of_population =
      N_individuals / nrow(matrices_object$metadata)
  ) |>
  arrange(desc(N_traits))

multitrait_candidates <- multitrait_recurrence |>
  filter(N_traits >= 2L) |>
  arrange(desc(N_traits), FAM, IND)
```

### 9.2 Distribuição da recorrência

```{r recurrence-distribution-table}
# DISPLAY-ONLY START
recurrence_class_labels <- c(
  high_4plus = "Alta (>=4)",
  intermediate_3 = "Intermediária (3)",
  broad_2 = "Ampla (2)",
  specific_1 = "Específica (1)",
  none_0 = "Nenhuma (0)"
)

recurrence_distribution_display <- recurrence_distribution |>
  mutate(
    Classe = unname(recurrence_class_labels[Recurrence_class])
  ) |>
  transmute(
    N_traits,
    Classe,
    N_individuals,
    Proportion_of_population = sprintf("%.3f", Proportion_of_population)
  )

tabela_html(
  recurrence_distribution_display,
  caption = "Distribuição dos indivíduos segundo a recorrência nas características elegíveis",
  col.names = c(
    "Número de características", "Classe", "Indivíduos",
    "Proporção da população"
  )
)
# DISPLAY-ONLY END
```

### 9.3 Indivíduos recorrentes

A tabela reúne os indivíduos selecionados em pelo menos duas características
elegíveis. Não é exibida uma tabela adicional com uma coluna de rank para cada
característica; as posições individuais permanecem disponíveis em
`selected_individuals_by_trait`.

```{r recurrent-candidates-table}
# DISPLAY-ONLY START
recurrent_candidates_display <- multitrait_candidates |>
  mutate(
    Classe = unname(recurrence_class_labels[Recurrence_class])
  ) |>
  transmute(
    IND,
    FAM,
    N_traits,
    Selection_frequency = sprintf("%.3f", Selection_frequency),
    Classe,
    Traits,
    Best_rank,
    Mean_rank_present = sprintf("%.2f", Mean_rank_present)
  )

tabela_html(
  recurrent_candidates_display,
  caption = "Indivíduos recorrentes em pelo menos duas características elegíveis",
  col.names = c(
    "IND", "FAM", "Número de características", "Frequência",
    "Classe", "Características", "Melhor rank", "Rank médio"
  )
)
# DISPLAY-ONLY END
```

'''

SEC9_EN = r'''## 9. Recurrence across eligible traits

### 9.1 Definition

Recurrence is descriptive and uses only rankings from traits that passed both
eligibility thresholds. For each individual, it counts how many of these traits
include the individual among the selected 20%. Frequency is calculated relative
to the number of eligible traits; no multi-trait selection index is constructed
and no weights are assigned across traits.

```{r multitrait-recurrence}
recurrence_counts <- selected_individuals_by_trait |>
  group_by(IND, FAM) |>
  summarise(
    N_traits = n(),
    Traits = paste(Trait, collapse = ", "),
    Best_rank = min(Rank),
    Mean_rank_present = mean(Rank),
    .groups = "drop"
  )

n_eligible_traits <- length(eligible_traits)

multitrait_recurrence <- matrices_object$metadata |>
  select(IND, FAM) |>
  left_join(recurrence_counts, by = c("IND", "FAM")) |>
  mutate(
    N_traits = tidyr::replace_na(N_traits, 0L),
    Traits = tidyr::replace_na(Traits, ""),
    Best_rank = if_else(N_traits == 0L, NA_integer_, Best_rank),
    Mean_rank_present = if_else(
      N_traits == 0L,
      NA_real_,
      Mean_rank_present
    ),
    Selection_frequency = if_else(
      n_eligible_traits > 0,
      N_traits / n_eligible_traits,
      0
    ),
    Recurrence_class = case_when(
      N_traits >= 4L ~ "high_4plus",
      N_traits == 3L ~ "intermediate_3",
      N_traits == 2L ~ "broad_2",
      N_traits == 1L ~ "specific_1",
      TRUE ~ "none_0"
    )
  ) |>
  arrange(desc(N_traits), FAM, IND)

recurrence_distribution <- multitrait_recurrence |>
  count(N_traits, Recurrence_class, name = "N_individuals") |>
  mutate(
    Proportion_of_population =
      N_individuals / nrow(matrices_object$metadata)
  ) |>
  arrange(desc(N_traits))

multitrait_candidates <- multitrait_recurrence |>
  filter(N_traits >= 2L) |>
  arrange(desc(N_traits), FAM, IND)
```

### 9.2 Recurrence distribution

```{r recurrence-distribution-table}
# DISPLAY-ONLY START
recurrence_class_labels <- c(
  high_4plus = "High (>=4)",
  intermediate_3 = "Intermediate (3)",
  broad_2 = "Broad (2)",
  specific_1 = "Specific (1)",
  none_0 = "None (0)"
)

recurrence_distribution_display <- recurrence_distribution |>
  mutate(
    Class = unname(recurrence_class_labels[Recurrence_class])
  ) |>
  transmute(
    N_traits,
    Class,
    N_individuals,
    Proportion_of_population = sprintf("%.3f", Proportion_of_population)
  )

table_html(
  recurrence_distribution_display,
  caption = "Distribution of individuals by recurrence across eligible traits",
  col.names = c(
    "Number of traits", "Class", "Individuals",
    "Population proportion"
  )
)
# DISPLAY-ONLY END
```

### 9.3 Recurrent individuals

The table includes individuals selected in at least two eligible traits. An
additional table with one rank column per trait is not displayed; individual
positions remain available in `selected_individuals_by_trait`.

```{r recurrent-candidates-table}
# DISPLAY-ONLY START
recurrent_candidates_display <- multitrait_candidates |>
  mutate(
    Class = unname(recurrence_class_labels[Recurrence_class])
  ) |>
  transmute(
    IND,
    FAM,
    N_traits,
    Selection_frequency = sprintf("%.3f", Selection_frequency),
    Class,
    Traits,
    Best_rank,
    Mean_rank_present = sprintf("%.2f", Mean_rank_present)
  )

table_html(
  recurrent_candidates_display,
  caption = "Individuals recurrent in at least two eligible traits",
  col.names = c(
    "IND", "FAM", "Number of traits", "Frequency",
    "Class", "Traits", "Best rank", "Mean rank"
  )
)
# DISPLAY-ONLY END
```

'''

SAVE_PT = r'''## 11. Persistência dos resultados revisados

Os resultados anteriores da versão `v1.0.5` não são sobrescritos. Esta revisão
é salva em um subdiretório próprio de M04, permitindo comparar ou recuperar a
estrutura anterior quando necessário.

```{r save-results}
threshold_results_dir <- here(
  "output", "results", "m04", "threshold_selection"
)
dir.create(threshold_results_dir, recursive = TRUE, showWarnings = FALSE)

write.csv(
  model_selection,
  file.path(threshold_results_dir, "model_selection.csv"),
  row.names = FALSE
)
write.csv(
  selected_oof_genomic_values,
  file.path(threshold_results_dir, "selected_oof_genomic_values.csv"),
  row.names = FALSE
)
write.csv(
  selected_individuals_by_trait,
  file.path(threshold_results_dir, "selected_individuals_by_trait.csv"),
  row.names = FALSE
)
write.csv(
  multitrait_recurrence,
  file.path(threshold_results_dir, "multitrait_recurrence.csv"),
  row.names = FALSE
)
write.csv(
  multitrait_candidates,
  file.path(threshold_results_dir, "multitrait_candidates.csv"),
  row.names = FALSE
)
write.csv(
  selected_oof_correlations,
  file.path(threshold_results_dir, "selected_oof_correlations.csv"),
  row.names = TRUE
)

module04_threshold_results <- list(
  model_comparison = model_comparison,
  model_selection = model_selection,
  convergence_overview = convergence_overview,
  rrblup_heritability_by_fold = rrblup_heritability_by_fold,
  rrblup_heritability_summary = rrblup_heritability_summary,
  selected_oof_genomic_values = selected_oof_genomic_values,
  genomic_ranking = genomic_ranking,
  selected_individuals_by_trait = selected_individuals_by_trait,
  multitrait_recurrence = multitrait_recurrence,
  multitrait_candidates = multitrait_candidates,
  selected_oof_correlations = selected_oof_correlations,
  settings = list(
    correlation_threshold = CORRELATION_SELECTION_THRESHOLD,
    nrmse_threshold = NRMSE_SELECTION_THRESHOLD,
    selection_proportion = SELECTION_PROPORTION,
    eligible_traits = eligible_traits
  )
)

saveRDS(
  module04_threshold_results,
  here("output", "results", "m04", "module04_threshold_results.rds")
)
```

'''

SAVE_EN = r'''## 11. Persistence of revised results

The previous results from version `v1.0.5` are not overwritten. This revision
is saved in its own M04 subdirectory, allowing the previous structure to be
compared or recovered when needed.

```{r save-results}
threshold_results_dir <- here(
  "output", "results", "m04", "threshold_selection"
)
dir.create(threshold_results_dir, recursive = TRUE, showWarnings = FALSE)

write.csv(
  model_selection,
  file.path(threshold_results_dir, "model_selection.csv"),
  row.names = FALSE
)
write.csv(
  selected_oof_genomic_values,
  file.path(threshold_results_dir, "selected_oof_genomic_values.csv"),
  row.names = FALSE
)
write.csv(
  selected_individuals_by_trait,
  file.path(threshold_results_dir, "selected_individuals_by_trait.csv"),
  row.names = FALSE
)
write.csv(
  multitrait_recurrence,
  file.path(threshold_results_dir, "multitrait_recurrence.csv"),
  row.names = FALSE
)
write.csv(
  multitrait_candidates,
  file.path(threshold_results_dir, "multitrait_candidates.csv"),
  row.names = FALSE
)
write.csv(
  selected_oof_correlations,
  file.path(threshold_results_dir, "selected_oof_correlations.csv"),
  row.names = TRUE
)

module04_threshold_results <- list(
  model_comparison = model_comparison,
  model_selection = model_selection,
  convergence_overview = convergence_overview,
  rrblup_heritability_by_fold = rrblup_heritability_by_fold,
  rrblup_heritability_summary = rrblup_heritability_summary,
  selected_oof_genomic_values = selected_oof_genomic_values,
  genomic_ranking = genomic_ranking,
  selected_individuals_by_trait = selected_individuals_by_trait,
  multitrait_recurrence = multitrait_recurrence,
  multitrait_candidates = multitrait_candidates,
  selected_oof_correlations = selected_oof_correlations,
  settings = list(
    correlation_threshold = CORRELATION_SELECTION_THRESHOLD,
    nrmse_threshold = NRMSE_SELECTION_THRESHOLD,
    selection_proportion = SELECTION_PROPORTION,
    eligible_traits = eligible_traits
  )
)

saveRDS(
  module04_threshold_results,
  here("output", "results", "m04", "module04_threshold_results.rds")
)
```

'''

FINAL_PT = r'''## 12. Interpretação final

A comparação passa a distinguir claramente três decisões. Primeiro, o método é
escolhido dentro de cada característica pelas métricas preditivas OOF, mantendo
o DIC como informação complementar. Segundo, apenas características com
`r > 0,30` e `NRMSE < 1` são consideradas suficientemente preditivas para a
seleção. Terceiro, dentro dessas características, os 20% de indivíduos mais
favoráveis são priorizados segundo a direção de melhoramento.

Os diagnósticos MCMC indicam comportamento compatível com convergência para a
grande maioria dos ajustes e parâmetros monitorados, sem serem usados como
filtro de decisão. A figura observado × predito acrescenta uma avaliação visual
de associação e calibração às métricas numéricas.

Os GEBVs OOF continuam sendo escores cross-fitted. A soma da média fenotípica os
coloca em uma escala mais interpretável, mas não os transforma em predições
fenotípicas completas e não altera os rankings. A recorrência entre
características permanece descritiva e não equivale a um índice de seleção
multicaracterístico.

As conclusões continuam condicionadas à população de melhoramento representada,
ao painel SSR disponível e ao desenho de validação empregado.
'''

FINAL_EN = r'''## 12. Final interpretation

The comparison now clearly separates three decisions. First, the method is
chosen within each trait using OOF predictive metrics, while DIC is retained as
complementary information. Second, only traits with `r > 0.30` and `NRMSE < 1`
are considered sufficiently predictive for selection. Third, within those
traits, the most favorable 20% of individuals are prioritized according to the
breeding objective.

MCMC diagnostics indicate behavior compatible with convergence for the large
majority of monitored fits and parameters without being used as a decision
filter. The observed-versus-predicted figure adds a visual assessment of
association and calibration to the numerical metrics.

OOF GEBVs remain cross-fitted scores. Adding the phenotypic mean places them on
a more interpretable scale, but does not turn them into complete phenotypic
predictions and does not change rankings. Recurrence across traits remains
descriptive and is not equivalent to a multi-trait selection index.

Conclusions remain conditional on the represented breeding population, the
available SSR panel, and the validation design used.
'''


def clean_prefix(text, lang):
    p1 = heading_pos(text, 1)
    p2 = heading_pos(text, 2)
    prefix = text[:p1] + (OBJECTIVE_PT if lang == "pt" else OBJECTIVE_EN) + text[p2:heading_pos(text, 5)]

    if lang == "pt":
        prefix = prefix.replace(
            "- `ggplot2`: construção do diagnóstico gráfico da regra de seleção;",
            "- `ggplot2`: construção dos gráficos de desempenho e de observado × predito;"
        )
        prefix = prefix.replace(
            "Durante a derivação, nenhum diretório de saída é criado; `output/results/m04/` é preparado somente na Seção 13, imediatamente antes da persistência dos resultados.",
            "Durante a derivação, nenhum diretório de saída é criado; os resultados revisados são persistidos somente na seção final e não sobrescrevem as saídas anteriores de M04."
        )
        prefix = prefix.replace(
            "### 3.2 Desempenho agrupado e variação entre folds",
            "### 3.2 Desempenho OOF agrupado"
        )
        start_phrase = "Há duas escalas de resumo nesta seção."
        replacement = (
            "`pooled_metrics` reúne as 150 predições OOF e fornece o desempenho global de cada combinação característica × método. "
            "`fold_summary` mantém os resumos herdados dos cinco folds para integrar o DIC e as métricas auxiliares na tabela de comparação; "
            "nenhuma regra de seleção é construída a partir da estabilidade entre folds.\n\n"
            "Os p-valores da correlação de Pearson permanecem apenas como contexto descritivo e não definem elegibilidade para seleção genômica.\n\n"
        )
        idx = prefix.find(start_phrase)
        if idx < 0:
            raise RuntimeError("PT pooled summary paragraph not found")
        end = prefix.find("## 4.", idx)
        prefix = prefix[:idx] + replacement + prefix[end:]
    else:
        prefix = prefix.replace(
            "- `ggplot2`: construction of the graphical diagnostic of the selection rule;",
            "- `ggplot2`: construction of performance and observed-versus-predicted figures;"
        )
        prefix = prefix.replace(
            "During derivation, no output directory is created; `output/results/m04/` is prepared only in Section 13, immediately before results are persisted.",
            "During derivation, no output directory is created; revised results are persisted only in the final section and do not overwrite previous M04 outputs."
        )
        prefix = prefix.replace(
            "### 3.2 Pooled performance and variation across folds",
            "### 3.2 Pooled OOF performance"
        )
        start_phrase = "There are two summary scales in this section."
        replacement = (
            "`pooled_metrics` combines the 150 OOF predictions and provides overall performance for each trait × method combination. "
            "`fold_summary` retains summaries inherited from the five folds to integrate DIC and auxiliary metrics in the comparison table; "
            "no selection rule is built from fold stability.\n\n"
            "Pearson-correlation p-values remain descriptive context only and do not define eligibility for genomic selection.\n\n"
        )
        idx = prefix.find(start_phrase)
        if idx < 0:
            raise RuntimeError("EN pooled summary paragraph not found")
        end = prefix.find("## 4.", idx)
        prefix = prefix[:idx] + replacement + prefix[end:]

    prefix = remove_subsection_42(prefix)

    old_theme = '''project_theme <- theme_gdocs() +
  theme(
    legend.position = "bottom",
    strip.text = element_text(face = "bold"),
    plot.title = element_text(face = "bold")
  )'''
    new_theme = '''project_theme <- theme_gdocs() +
  theme(
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.box = "horizontal",
    strip.text = element_text(face = "bold"),
    plot.title = element_text(face = "bold")
  )'''
    prefix = replace_once(prefix, old_theme, new_theme, f"{lang} project theme")

    old_plot_end = '''  project_theme +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))'''
    new_plot_end = '''  project_theme +
  guides(fill = guide_legend(nrow = 1, byrow = TRUE)) +
  theme(
    legend.direction = "horizontal",
    legend.box = "horizontal",
    axis.text.x = element_text(angle = 45, hjust = 1)
  )'''
    prefix = replace_once(prefix, old_plot_end, new_plot_end, f"{lang} predictive legend")

    if lang == "pt":
        prefix = prefix.replace(
            "permanece específica por característica e continua com as evidências\ncomplementares de DIC e diagnóstico.",
            "permanece específica por característica e é definida pelas métricas OOF; o DIC é mantido como evidência complementar."
        )
    else:
        prefix = prefix.replace(
            "remains trait-specific and continues with complementary DIC and diagnostic evidence.",
            "remains trait-specific and is defined by OOF metrics; DIC is retained as complementary evidence."
        )

    return prefix.rstrip() + "\n\n"


def renumber_heritability(sec):
    sec = re.sub(r"^## 8\. ", "## 6. ", sec, count=1, flags=re.M)
    sec = re.sub(r"^### 8\.([123]) ", r"### 6.\1 ", sec, flags=re.M)
    return sec


def clean_correlations(sec, lang):
    sec = re.sub(r"^## 12\. ", "## 10. ", sec, count=1, flags=re.M)
    sec = re.sub(r"^### 12\.1 ", "### 10.1 ", sec, count=1, flags=re.M)
    sec = sec.replace("Genomic_value", "GEBV_centered")
    needle = "selected_genomic_wide <- selected_oof_genomic_values |>\n  select(IND, Trait, GEBV_centered) |>"
    repl = "selected_genomic_wide <- selected_oof_genomic_values |>\n  filter(Selection_eligible) |>\n  select(IND, Trait, GEBV_centered) |>"
    sec = replace_once(sec, needle, repl, f"{lang} eligible correlation filter")
    if lang == "pt":
        sec = sec.replace(
            "## 10. Correlações entre valores genômicos OOF",
            "## 10. Correlações entre GEBVs OOF das características elegíveis"
        )
        sec = sec.replace(
            "title = \"Correlação entre valores genômicos OOF\"",
            "title = \"Correlação entre GEBVs OOF das características elegíveis\""
        )
    else:
        sec = sec.replace(
            "## 10. Correlations among OOF genomic values",
            "## 10. Correlations among OOF GEBVs of eligible traits"
        )
        sec = sec.replace(
            "title = \"Correlation among OOF genomic values\"",
            "title = \"Correlation among OOF GEBVs of eligible traits\""
        )
    return sec.rstrip() + "\n\n"


def transform(path, lang):
    text = path.read_text(encoding="utf-8")
    baseline = text

    prefix = clean_prefix(text, lang)
    herit = renumber_heritability(section(text, 8))
    corr = clean_correlations(section(text, 12), lang)

    if lang == "pt":
        rebuilt = prefix + SEC5_PT + herit + SEC7_PT + SEC8_PT + SEC9_PT + corr + SAVE_PT + FINAL_PT
    else:
        rebuilt = prefix + SEC5_EN + herit + SEC7_EN + SEC8_EN + SEC9_EN + corr + SAVE_EN + FINAL_EN

    required = [
        "CORRELATION_SELECTION_THRESHOLD <- 0.30",
        "NRMSE_SELECTION_THRESHOLD <- 1.00",
        "observed-predicted-figure",
        "GEBV_on_trait_scale",
        "threshold_selection",
        "guide_legend(nrow = 1, byrow = TRUE)",
    ]
    for item in required:
        if item not in rebuilt:
            raise RuntimeError(f"{path.name}: required item missing: {item}")

    forbidden = [
        "Automatic_candidate",
        "automatic candidate",
        "candidato automático",
        "Predictive_loss",
        "selection-rule-map",
        "selected-fold-figure",
        "runtime-figure",
        "main_multitrait_rank_profile",
        "provisional_review_required",
    ]
    for item in forbidden:
        if item in rebuilt:
            raise RuntimeError(f"{path.name}: forbidden legacy item remains: {item}")

    chunk_labels = re.findall(r"```\{r\s+([^,}\s]+)", rebuilt)
    duplicates = sorted({x for x in chunk_labels if chunk_labels.count(x) > 1})
    if duplicates:
        raise RuntimeError(f"{path.name}: duplicate chunk labels: {duplicates}")

    if rebuilt == baseline:
        raise RuntimeError(f"{path.name}: transformation made no changes")

    path.write_text(rebuilt.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"updated {path.relative_to(ROOT)}")


for lang, path in FILES.items():
    transform(path, lang)

print("PASS: M04 PT/EN revised; no other files were modified by this helper.")
