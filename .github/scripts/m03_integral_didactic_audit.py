from pathlib import Path


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected exactly one target, found {n}")
    return text.replace(old, new, 1)


FILES = {
    "analysis/03_models_pt.Rmd": "pt",
    "analysis/03_models_en.Rmd": "en",
}

for filename, lang in FILES.items():
    p = Path(filename)
    text = p.read_text(encoding="utf-8")

    if lang == "pt":
        text = replace_once(
            text,
            "O chunk oculto a seguir define apenas opções de renderização compartilhadas pela página. Ele não ajusta modelos, não lê resultados e não executa cadeias MCMC.\n\n",
            "",
            "remove hidden-chunk meta PT",
        )
        old_packages = '''O primeiro chunk carrega os pacotes usados no ajuste Bayesiano (`BGLR`), nos diagnósticos de cadeia (`coda`), na manipulação tabular e na construção da página. Nenhum modelo é ajustado nesta etapa.\n\n```{r packages}\nsuppressPackageStartupMessages({\n  library(BGLR)\n  library(coda)\n  library(dplyr)\n  library(knitr)\n  library(here)\n})\n```'''
        new_packages = '''Os pacotes utilizados têm funções distintas:\n\n- `BGLR`: ajuste dos modelos de regressão Bayesiana, RR-BLUP/BRR e GBLUP;\n- `coda`: cálculo dos diagnósticos das cadeias MCMC, incluindo ESS e Geweke;\n- `dplyr`: organização, seleção e resumo das tabelas de resultados;\n- `knitr`: formatação das tabelas apresentadas no documento;\n- `here`: construção de caminhos relativos ao projeto.\n\n```{r packages, warning=FALSE, message=FALSE}\nlibrary(BGLR)  # Ajuste dos modelos de predição genômica.\nlibrary(coda)  # Diagnósticos das cadeias MCMC.\nlibrary(dplyr) # Manipulação e resumo de tabelas.\nlibrary(knitr) # Formatação de tabelas.\nlibrary(here)  # Caminhos relativos ao projeto.\n```\n\n```{r formatacao-tabelas, include=FALSE}\ntabela_html <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  tabela <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      tabela,\n      '</div>'\n    )\n  )\n}\n```'''
        text = replace_once(text, old_packages, new_packages, "packages PT")
        text = text.replace("  kable(", "  tabela_html(")
        text = text.replace("kable(\n", "tabela_html(\n")
        text = text.replace("|>\n  # Formata a tabela para exibição no tutorial.\n  tabela_html(", "|>\n  tabela_html(")

        text = replace_once(
            text,
            "A tabela seguinte funciona como ponto de controle entre os Módulos 02 e 03. Ela confirma que fenótipos, `X`, `M`, `G` e a tabela de folds possuem dimensões compatíveis antes de qualquer ajuste; nenhum objeto é filtrado ou reconstruído neste chunk.",
            "A tabela seguinte confirma que os objetos recebidos do Módulo 02 possuem dimensões compatíveis antes de qualquer ajuste. `nrow()` conta os indivíduos representados em cada objeto e `ncol()` informa quantas características, efeitos, marcadores, indivíduos relacionados ou campos estão armazenados. Nenhum objeto é filtrado ou reconstruído nesta conferência.",
            "input summary prose PT",
        )
        text = replace_once(
            text,
            '  tabela_html(caption = "Estrutura das entradas do Módulo 03")\n```',
            '  tabela_html(caption = "Estrutura das entradas do Módulo 03")\n```\n\nAs cinco entradas mantêm os mesmos `r nrow(phenotypes)` indivíduos. A matriz fenotípica contém `r ncol(phenotypes)` características, `X` contém `r ncol(X)` colunas do desenho de família e intercepto, `M` possui `r ncol(M)` colunas de dosagem centralizadas e `G` é quadrada com `r ncol(G)` colunas. Essa compatibilidade permite usar a mesma ordem de indivíduos em todos os ajustes.',
            "input summary interpretation PT",
        )
        text = replace_once(
            text,
            "O chunk abaixo apenas remove a coluna redundante e mostra quais colunas de família entram no preditor.\n\n```{r family-fixed-effect}\nX_fixed <- X[\n  ,\n  colnames(X) != \"(Intercept)\",\n  drop = FALSE\n]\n\ncolnames(X_fixed)\n```",
            "A expressão `colnames(X) != \"(Intercept)\"` produz um vetor lógico que é `FALSE` somente para a coluna de intercepto. Esse vetor é usado em `X[, ..., drop = FALSE]` para manter todas as linhas e apenas as colunas de família; `drop = FALSE` preserva o resultado como matriz.\n\n```{r family-fixed-effect}\nX_fixed <- X[\n  ,\n  colnames(X) != \"(Intercept)\",\n  drop = FALSE\n]\n\ndata.frame(Coluna_de_familia = colnames(X_fixed)) |>\n  tabela_html(caption = \"Colunas de família usadas como efeitos fixos\")\n```\n\nApós a remoção do intercepto, `X_fixed` contém `r ncol(X_fixed)` colunas de contraste de família. Essas colunas entram como um único termo fixo comum aos sete métodos.",
            "family fixed PT",
        )
        text = replace_once(
            text,
            "Foram utilizadas 1.000.000 de iterações, descarte inicial de 200.000 iterações e thinning igual a 4, seguindo a configuração principal da análise de referência [@silva2021brrguava]. O parâmetro global de alocação de variância do BGLR foi definido como `R2 = 0.5`.\n\n`SEED_BASE = 202608050` não é um hiperparâmetro do modelo: ele apenas inicia uma sequência determinística de sementes, à qual o número de cada ajuste é somado para que as 350 combinações sejam reproduzíveis sem compartilhar a mesma semente. As quantidades de amostras salvas e mantidas são derivadas de iterações, burn-in e thinning e, portanto, não constituem escolhas adicionais.\n\nA parametrização BayesB2 fixa a probabilidade de efeito zero em `1e-5`, equivalente a `probIn = 0.99999`, com `counts = 1e6` para concentrar fortemente essa probabilidade de inclusão; a motivação é detalhada na Seção 6.4. Os limiares `ESS < 1000` e `|Geweke Z| > 2` são usados somente para sinalizar cadeias que merecem revisão, nunca como exclusão automática. Para o Lasso Bayesiano, `BL_LAMBDA_TYPE = \"FIXED\"` antecipa que o lambda calculado na Seção 6.6 permanecerá constante durante cada cadeia.",
            "Os parâmetros centrais das cadeias são:\n\n- `N_ITER = 1.000.000`: número total de iterações de cada cadeia;\n- `BURN_IN = 200.000`: iterações iniciais descartadas antes dos diagnósticos;\n- `THIN = 4`: mantém uma amostra a cada quatro iterações;\n- `R2_PRIOR = 0.5`: parâmetro global de alocação de variância usado pelo BGLR;\n- `SEED_BASE = 202608050`: início da sequência determinística de sementes. Cada ajuste soma seu número sequencial a essa base, de modo que as 350 combinações recebem sementes diferentes e reproduzíveis.\n\nA configuração de iterações, burn-in e thinning segue a análise de referência [@silva2021brrguava]. Como `floor(N_ITER / THIN)` calcula quantas amostras são gravadas e `floor(BURN_IN / THIN)` quantas pertencem ao burn-in, `RETAINED_SAMPLES` é uma quantidade derivada, não um parâmetro adicional.\n\nOutras definições específicas são:\n\n- `BAYESB2_ZERO_PROBABILITY = 1e-5`, equivalente a `probIn = 0.99999`;\n- `BAYESB2_COUNTS = 1e6`, que concentra fortemente a priori de `probIn`;\n- `ESS_REVIEW_THRESHOLD = 1000` e `GEWEKE_REVIEW_THRESHOLD = 2`, usados somente como sinais de revisão, não como critérios automáticos de exclusão;\n- `BL_LAMBDA_TYPE = \"FIXED\"`, indicando que o lambda calculado na Seção 6.6 permanece constante durante a cadeia.",
            "MCMC prose PT",
        )
        text = replace_once(
            text,
            '  tabela_html(caption = "Configuração MCMC utilizada nos sete métodos")\n```',
            '  tabela_html(caption = "Configuração MCMC utilizada nos sete métodos")\n```\n\nA configuração resulta em `r RAW_SAVED_SAMPLES` amostras escalares gravadas por cadeia e `r RETAINED_SAMPLES` amostras após a remoção da parcela correspondente ao burn-in. Os mesmos valores de iteração, burn-in, thinning e `R2` são usados em todos os 350 ajustes.',
            "MCMC interpretation PT",
        )
        text = replace_once(
            text,
            "A tabela a seguir deve ser lida como um mapa entre o nome usado no tutorial, o componente correspondente no BGLR e a entrada genômica utilizada. Seis métodos operam diretamente sobre `M`; o GBLUP usa `G`. As subseções seguintes explicam o que muda na priori ou na representação do componente genômico.",
            "A tabela a seguir relaciona cada método ao componente correspondente do BGLR e à entrada genômica utilizada. Seis métodos operam diretamente sobre `M`; o GBLUP usa `G`. As subseções seguintes explicam o que muda na priori ou na representação do componente genômico.",
            "catalogue prose PT",
        )
        text = replace_once(
            text,
            '  tabela_html(caption = "Métodos de predição genômica avaliados")\n```',
            '  tabela_html(caption = "Métodos de predição genômica avaliados")\n```\n\nA principal diferença entre os seis métodos de regressão está na priori dos efeitos dos marcadores. O GBLUP muda a representação: em vez de estimar efeitos individuais das colunas de `M`, modela diretamente o vetor de valores genômicos com covariância definida por `G`.',
            "catalogue interpretation PT",
        )
        text = replace_once(
            text,
            "```{r bl-lambda}\n# Divide R2 entre os dois termos lineares do preditor: família e componente genômico BL.",
            "No código, `apply(M, 2, function(x) sum(x^2))` percorre as colunas de `M` (`2` indica a margem das colunas) e calcula a soma dos quadrados em cada uma. A soma desses valores, dividida por `nrow(M)`, fornece o primeiro termo de `MS_x`; `sum(colMeans(M)^2)` fornece o segundo. Em seguida, `sqrt()` transforma `BL_LAMBDA_SQUARED` em `BL_LAMBDA`.\n\n```{r bl-lambda}\n# Divide R2 entre os dois termos lineares do preditor: família e componente genômico BL.",
            "BL calculation explanation PT",
        )
        text = text.replace("Neste tutorial, \\(\\lambda\\) é fixado nessa", "Nesta análise, \\(\\lambda\\) é fixado nessa")
        text = replace_once(
            text,
            "O termo de família é comum aos sete métodos. Em seguida, cada modelo recebe o componente genômico correspondente. Na lista `ETA_models`, `fixed` identifica o termo de família e `genomic` identifica o termo que diferencia os métodos. `X = M` é usado nas regressões por marcadores; `K = G` é usado no GBLUP. Somente BayesB2 e BL recebem argumentos adicionais porque suas parametrizações foram explicitamente fixadas nas seções anteriores.",
            "O argumento `ETA` do BGLR recebe uma lista de termos do preditor. `family_term <- list(X = X_fixed, model = \"FIXED\")` associa a matriz de contrastes de família a coeficientes fixos. Em `ETA_models`, cada método contém dois elementos nomeados: `fixed`, comum aos sete modelos, e `genomic`, que define a parte genômica.\n\nNas regressões por marcadores, `X = M` fornece as dosagens centralizadas e `model` escolhe a priori correspondente (`BRR`, `BayesA`, `BayesB`, `BayesC` ou `BL`). No GBLUP, `K = G` fornece diretamente a matriz de covariância ao componente `RKHS`. BayesB2 acrescenta `probIn` e `counts`; BL acrescenta `type = \"FIXED\"` e `lambda = BL_LAMBDA`. Assim, a estrutura de intercepto e família permanece constante e somente a especificação genômica muda entre métodos.",
            "ETA explanation PT",
        )
        text = replace_once(
            text,
            "As mesmas sete especificações são aplicadas às dez características e aos cinco folds. O produto cartesiano gera 350 linhas: 50 ajustes por método, correspondentes a dez características em cinco folds. Depois de ordenar as combinações de forma estável, cada linha recebe um número sequencial, uma semente exclusiva e um `Run_id` legível. A semente controla apenas a reprodução da cadeia daquela combinação; ela não modifica os folds.",
            "As mesmas sete especificações são aplicadas às dez características e aos cinco folds. `expand.grid(Trait = traits, Fold = ..., Method = method_names)` constrói o produto cartesiano dessas três dimensões, produzindo 350 linhas: 50 ajustes por método.\n\nA expressão `order(match(run_design$Trait, traits), run_design$Fold, match(run_design$Method, method_names))` reorganiza as linhas na ordem definida pelos vetores originais de características e métodos e, dentro deles, por fold. `seq_len(nrow(run_design))` atribui o número sequencial do ajuste; a semente é `SEED_BASE + Run_number`; e `paste(..., sep = \"_\")` combina característica, fold e método em um identificador legível. A semente controla apenas a reprodução da cadeia daquela combinação; ela não modifica os folds.",
            "run design PT",
        )
        text = replace_once(
            text,
            '  tabela_html(caption = "Número de ajustes por método")\n```',
            '  tabela_html(caption = "Número de ajustes por método")\n```\n\nCada método aparece em `r nrow(run_design) / length(method_names)` combinações, totalizando `r nrow(run_design)` ajustes. Como a mesma grade de característica × fold é usada para todos os métodos, as comparações posteriores partem do mesmo desenho de validação.',
            "run design interpretation PT",
        )
        text = replace_once(
            text,
            "O bloco abaixo percorre as combinações de característica, fold e método. Antes do laço, o tutorial mapeia quais arquivos escalares nativos do BGLR serão usados nos diagnósticos. `genomic_trace_suffix` identifica o arquivo, `genomic_trace_header` informa se ele possui cabeçalho, `genomic_trace_column` seleciona a coluna escalar e `genomic_trace_parameter` fornece o rótulo apresentado posteriormente.",
            "O ajuste percorre as combinações de característica, fold e método. Antes do laço, quatro vetores nomeados mapeiam os arquivos escalares nativos do BGLR usados nos diagnósticos: `genomic_trace_suffix` identifica o arquivo, `genomic_trace_header` informa se ele possui cabeçalho, `genomic_trace_column` seleciona a coluna escalar e `genomic_trace_parameter` fornece o rótulo apresentado posteriormente.",
            "trace intro PT",
        )
        old_fit_intro = '''O chunk `fit-models` contém o procedimento completo de reprodução dos 350 ajustes, mas permanece com `eval=FALSE` na página. Isso evita que uma renderização rotineira do tutorial reinicie as cadeias MCMC e sobrescreva seus arquivos. Para uma reprodução integral a partir do zero, este é o bloco que deve ser executado deliberadamente depois que os Módulos 01 e 02 tiverem produzido seus objetos.\n\nEm cada execução, o código mascara somente os 30 fenótipos do fold corrente, chama `BGLR()` com a especificação correspondente, registra tempo e avisos, recupera as predições dos indivíduos mascarados e decompõe `yHat` em intercepto, efeito fixo de família e componente genômico. Os arquivos escalares gravados pelo BGLR incluem amostras salvas durante o burn-in; por isso o código remove explicitamente as primeiras `BURN_IN_SAVED_SAMPLES` linhas antes de calcular ESS e Geweke.'''
        new_fit_intro = '''Os 350 ajustes são computacionalmente intensivos. O bloco completo de ajuste permanece com `eval=FALSE`, de modo que a reconstrução das páginas não reinicia as cadeias nem sobrescreve seus arquivos. Para reproduzir a análise do zero, esse bloco deve ser executado deliberadamente depois da geração dos objetos dos Módulos 01 e 02.\n\nA sequência de cada ajuste pode ser acompanhada diretamente no código:\n\n1. **Selecionar característica e fold.** `validation_index <- which(cv_folds$Fold == fold_number)` localiza os 30 candidatos de validação e `training_index` localiza os demais 120. A cópia `y_model` recebe `NA` somente nas posições de validação; assim, o fenótipo do candidato não participa do próprio ajuste.\n2. **Escolher a especificação e ajustar o BGLR.** `ETA_models[[method_name]]` recupera o `ETA` do método corrente. `BGLR::BGLR()` recebe a resposta mascarada, `nIter`, `burnIn`, `thin`, `R2` e o prefixo dos arquivos da cadeia. `withCallingHandlers()` permite registrar mensagens de aviso sem interromper o laço.\n3. **Recuperar predições e componentes.** `fit$yHat[validation_index]` fornece as predições OOF. O produto matricial `X_fixed %*% fit$ETA$fixed$b` calcula o componente fixo de família. Como `yHat = mu + componente fixo + componente genômico`, a diferença `fit$yHat - fit$mu - fixed_component` recupera o componente genômico.\n4. **Calcular métricas.** `cor()` fornece a correlação observado–predito; RMSE é a raiz da média dos erros quadráticos; MAE é a média dos erros absolutos; `mean(predicted - observed)` mede viés; e `cov(observed, predicted) / var(predicted)` fornece a inclinação da regressão de observado sobre predito. DIC e `pD` são recuperados do ajuste Bayesiano e não são métricas OOF.\n5. **Registrar parâmetros disponíveis.** Expressões como `c(fit$ETA$genomic$probIn, NA_real_)[1]` retornam o parâmetro quando ele existe e `NA` quando o método não o fornece, permitindo uma tabela comum aos sete modelos.\n6. **Ler e recortar as cadeias.** `scan()` lê a cadeia escalar da variância residual; `read.table()` lê o arquivo escalar específico do método. `seq.int(BURN_IN_SAVED_SAMPLES + 1L, ...)` seleciona somente as amostras posteriores ao burn-in e `cbind()` reúne as duas séries.\n7. **Calcular diagnósticos.** `coda::mcmc()` associa às amostras o início e o thinning da cadeia. `effectiveSize()` estima o tamanho efetivo da amostra e `geweke.diag()` calcula a estatística de Geweke.\n\nOs arquivos escalares nativos do BGLR contêm também as amostras gravadas durante o burn-in; por isso a remoção de `BURN_IN_SAVED_SAMPLES` ocorre explicitamente antes dos diagnósticos.'''
        text = replace_once(text, old_fit_intro, new_fit_intro, "fit intro PT")
        text = replace_once(
            text,
            "Como os chunks de ajuste permanecem desativados durante a renderização, as tabelas produzidas previamente pelo procedimento completo são lidas de `output/models/`. Assim, esta parte da página pode ser reconstruída para inspeção e apresentação sem executar novamente as 350 cadeias.",
            "As tabelas consolidadas produzidas pelos 350 ajustes são lidas de `output/models/`. `read.csv(..., check.names = FALSE)` recupera cada arquivo sem modificar seus nomes de colunas. Isso permite inspecionar predições, valores genômicos, métricas e diagnósticos a partir das saídas persistidas, sem recalcular as cadeias MCMC.",
            "combine results PT",
        )
        text = replace_once(
            text,
            '  tabela_html(digits = 4, caption = "Exemplo das predições fora da amostra")\n```',
            '  tabela_html(digits = 4, caption = "Exemplo das predições fora da amostra")\n```\n\nCada linha corresponde a um indivíduo quando seu fenótipo estava mascarado. A soma do intercepto, do componente fixo de família e do componente genômico reproduz a predição total armazenada em `Predicted`.',
            "prediction interpretation PT",
        )
        text = replace_once(
            text,
            '  tabela_html(digits = 4, caption = "Exemplo das métricas obtidas por fold")\n```',
            '  tabela_html(digits = 4, caption = "Exemplo das métricas obtidas por fold")\n```\n\nAs linhas mostram que cada combinação característica–fold–método recebe simultaneamente métricas OOF de capacidade preditiva e critérios Bayesianos de ajuste. Esses dois grupos de medidas respondem a perguntas diferentes e são comparados separadamente no Módulo 04.',
            "metrics interpretation PT",
        )
        text = replace_once(
            text,
            '  tabela_html(caption = "Dimensões das principais saídas do ajuste")\n```',
            '  tabela_html(caption = "Dimensões das principais saídas do ajuste")\n```\n\nOs totais esperados são confirmados pelas quatro tabelas consolidadas: `r nrow(cv_metrics_by_fold)` ajustes, `r nrow(cv_predictions)` predições OOF, `r nrow(genomic_values_by_fold)` valores genômicos por fold e `r nrow(convergence_diagnostics)` diagnósticos escalares.',
            "output size interpretation PT",
        )
        text = replace_once(
            text,
            '    caption = "Resumo dos diagnósticos MCMC por método"\n  )\n```',
            '    caption = "Resumo dos diagnósticos MCMC por método"\n  )\n```\n\nO resumo informa quantas cadeias foram avaliadas e quantas ultrapassaram pelo menos um limiar de triagem em cada método. `Minimum_ESS`, `Median_ESS` e `Maximum_absolute_Geweke` descrevem a intensidade dos sinais de autocorrelação ou instabilidade, sem transformar os limiares em testes formais de validade.',
            "convergence summary interpretation PT",
        )
        text = replace_once(
            text,
            '    caption = "Cadeias destacadas pelos diagnósticos ESS ou Geweke"\n  )\n```',
            '    caption = "Cadeias destacadas pelos diagnósticos ESS ou Geweke"\n  )\n```\n\nA tabela detalhada localiza exatamente característica, fold, método e parâmetro associados a cada sinalização. As linhas destacadas orientam inspeção adicional; não determinam exclusão automática de ajustes ou predições.',
            "flags interpretation PT",
        )
        text = replace_once(
            text,
            "Após os diagnósticos, a tabela de convergência é atualizada com os indicadores de revisão, o resumo por método é gravado e o objeto final é reunido para uso nos módulos seguintes. Assim como o ajuste, este chunk permanece com `eval=FALSE` na renderização: ele deve ser executado quando as tabelas primárias forem regeneradas, para atualizar `models_object.rds` de forma coerente com aquelas saídas.",
            "Após os diagnósticos, a tabela de convergência é atualizada com os indicadores de revisão, o resumo por método é gravado e `models_object.rds` reúne configurações, desenho dos ajustes, catálogo dos métodos, predições, valores genômicos, métricas e diagnósticos. Esse bloco acompanha a regeneração completa dos ajustes e permanece com `eval=FALSE`; quando os resultados primários forem recalculados, ele deve ser executado para manter o objeto final coerente com as tabelas gravadas.",
            "save prose PT",
        )
        text = replace_once(
            text,
            "O Módulo 04 utiliza as predições OOF, as métricas por fold, os valores\ngenômicos e os diagnósticos MCMC obtidos aqui para comparar os métodos e\nconstruir os resultados genômicos derivados.",
            "O Módulo 04 utiliza as predições OOF, as métricas por fold, os valores\ngenômicos e os diagnósticos MCMC obtidos aqui para comparar os métodos e\nconstruir os resultados genômicos derivados.\n\n<div style=\"display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;\">\n<a href=\"02_matrices_pt.html\">← Módulo 02 — Construção das matrizes</a>\n<a href=\"04_results_pt.html\">Módulo 04 — Comparação e seleção →</a>\n</div>",
            "navigation PT",
        )
        text = text.replace("  # Lista os valores correspondentes aos itens da tabela.\n", "")
        text = text.replace("# Monta a tabela apresentada nesta seção.\n", "")
        text = text.replace("  # Descreve a estrutura de efeitos adotada por cada método.\n", "")
        text = text.replace("# Prepara as informações usadas nos diagnósticos das cadeias MCMC.\n", "")
        text = text.replace("# Monta a tabela-resumo apresentada nesta seção.\n", "")
        text = text.replace("  # Conta o número de registros produzido em cada saída do módulo.\n", "")
    else:
        text = replace_once(
            text,
            "The hidden chunk below defines only page-wide rendering options. It does not fit models, read results, or run MCMC chains.\n\n",
            "",
            "remove hidden-chunk meta EN",
        )
        old_packages = '''The first chunk loads the packages used for Bayesian fitting (`BGLR`), chain diagnostics (`coda`), tabular manipulation, and page construction. No model is fitted at this stage.\n\n```{r packages}\nsuppressPackageStartupMessages({\n  library(BGLR)\n  library(coda)\n  library(dplyr)\n  library(knitr)\n  library(here)\n})\n```'''
        new_packages = '''The packages used here have distinct roles:\n\n- `BGLR`: fits Bayesian regression, RR-BLUP/BRR, and GBLUP models;\n- `coda`: computes MCMC diagnostics, including ESS and Geweke statistics;\n- `dplyr`: organizes, selects, and summarizes result tables;\n- `knitr`: formats the tables presented in the document;\n- `here`: builds project-relative file paths.\n\n```{r packages, warning=FALSE, message=FALSE}\nlibrary(BGLR)  # Fit genomic prediction models.\nlibrary(coda)  # Diagnose MCMC chains.\nlibrary(dplyr) # Manipulate and summarize tables.\nlibrary(knitr) # Format tables.\nlibrary(here)  # Build project-relative paths.\n```\n\n```{r table-formatting, include=FALSE}\nformat_table <- function(x, caption = NULL, digits = getOption("digits"), col.names = NA) {\n  table <- knitr::kable(\n    x,\n    format = "html",\n    caption = caption,\n    digits = digits,\n    col.names = col.names,\n    table.attr = paste0(\n      'class="table table-striped table-hover" ',\n      'style="width:100%; margin-bottom:0;"'\n    )\n  )\n  knitr::asis_output(\n    paste0(\n      '<div style="width:100%; overflow-x:auto; margin-bottom:1.25rem;">',\n      table,\n      '</div>'\n    )\n  )\n}\n```'''
        text = replace_once(text, old_packages, new_packages, "packages EN")
        text = text.replace("  kable(", "  format_table(")
        text = text.replace("kable(\n", "format_table(\n")
        text = text.replace("|>\n  # Format the table for display in the tutorial.\n  format_table(", "|>\n  format_table(")

        text = replace_once(
            text,
            "The following table acts as a checkpoint between Modules 02 and 03. It confirms that phenotypes, `X`, `M`, `G`, and the fold table have compatible dimensions before any fit; no object is filtered or reconstructed in this chunk.",
            "The following table confirms that the objects received from Module 02 have compatible dimensions before any fit. `nrow()` counts the individuals represented in each object, while `ncol()` reports how many traits, effects, markers, related individuals, or fields are stored. No object is filtered or reconstructed in this check.",
            "input summary prose EN",
        )
        text = replace_once(
            text,
            '  format_table(caption = "Structure of the Module 03 inputs")\n```',
            '  format_table(caption = "Structure of the Module 03 inputs")\n```\n\nAll five inputs retain the same `r nrow(phenotypes)` individuals. The phenotype matrix contains `r ncol(phenotypes)` traits, `X` contains `r ncol(X)` family-design and intercept columns, `M` contains `r ncol(M)` centered dosage columns, and `G` is square with `r ncol(G)` columns. This compatibility allows the same individual order to be used throughout model fitting.',
            "input summary interpretation EN",
        )
        text = replace_once(
            text,
            "The chunk below only removes the redundant column and displays the family columns that enter the predictor.\n\n```{r family-fixed-effect}\nX_fixed <- X[\n  ,\n  colnames(X) != \"(Intercept)\",\n  drop = FALSE\n]\n\ncolnames(X_fixed)\n```",
            "The expression `colnames(X) != \"(Intercept)\"` produces a logical vector that is `FALSE` only for the intercept column. It is used in `X[, ..., drop = FALSE]` to retain every row and only the family columns; `drop = FALSE` preserves the result as a matrix.\n\n```{r family-fixed-effect}\nX_fixed <- X[\n  ,\n  colnames(X) != \"(Intercept)\",\n  drop = FALSE\n]\n\ndata.frame(Family_column = colnames(X_fixed)) |>\n  format_table(caption = \"Family columns used as fixed effects\")\n```\n\nAfter the intercept is removed, `X_fixed` contains `r ncol(X_fixed)` family-contrast columns. These columns enter as one fixed term shared by all seven methods.",
            "family fixed EN",
        )
        text = replace_once(
            text,
            "The analysis uses 1,000,000 iterations, a burn-in of 200,000 iterations, and a thinning interval of 4, following the main configuration of the reference analysis [@silva2021brrguava]. The global BGLR prior-allocation parameter is set to `R2 = 0.5`.\n\n`SEED_BASE = 202608050` is not a model hyperparameter: it only starts a deterministic seed sequence, to which the run number is added so that all 350 combinations are reproducible without sharing the same seed. The numbers of saved and retained samples are derived from iterations, burn-in, and thinning and therefore are not additional choices.\n\nThe BayesB2 parameterization fixes the zero-effect probability at `1e-5`, equivalent to `probIn = 0.99999`, with `counts = 1e6` to strongly concentrate that inclusion probability; the rationale is detailed in Section 6.4. Thresholds `ESS < 1000` and `|Geweke Z| > 2` only flag chains for review and never act as automatic exclusion rules. For the Bayesian Lasso, `BL_LAMBDA_TYPE = \"FIXED\"` anticipates that the lambda calculated in Section 6.6 remains constant during each chain.",
            "The central chain settings are:\n\n- `N_ITER = 1,000,000`: total iterations in each chain;\n- `BURN_IN = 200,000`: initial iterations discarded before diagnostics;\n- `THIN = 4`: retains one draw every four iterations;\n- `R2_PRIOR = 0.5`: BGLR's global prior-allocation parameter;\n- `SEED_BASE = 202608050`: start of the deterministic seed sequence. Each run adds its sequential number to this base, giving all 350 combinations different and reproducible seeds.\n\nThe iteration, burn-in, and thinning configuration follows the reference analysis [@silva2021brrguava]. Because `floor(N_ITER / THIN)` gives the number of saved draws and `floor(BURN_IN / THIN)` gives the number belonging to burn-in, `RETAINED_SAMPLES` is derived rather than an additional parameter.\n\nOther method-specific definitions are:\n\n- `BAYESB2_ZERO_PROBABILITY = 1e-5`, equivalent to `probIn = 0.99999`;\n- `BAYESB2_COUNTS = 1e6`, strongly concentrating the `probIn` prior;\n- `ESS_REVIEW_THRESHOLD = 1000` and `GEWEKE_REVIEW_THRESHOLD = 2`, used only as review flags rather than automatic exclusion rules;\n- `BL_LAMBDA_TYPE = \"FIXED\"`, indicating that the lambda calculated in Section 6.6 remains constant during the chain.",
            "MCMC prose EN",
        )
        text = replace_once(
            text,
            '  format_table(caption = "MCMC settings used for the seven methods")\n```',
            '  format_table(caption = "MCMC settings used for the seven methods")\n```\n\nThis configuration yields `r RAW_SAVED_SAMPLES` scalar draws written per chain and `r RETAINED_SAMPLES` draws after the burn-in portion is removed. The same iteration, burn-in, thinning, and `R2` settings are used in all 350 fits.',
            "MCMC interpretation EN",
        )
        text = replace_once(
            text,
            "The following table is a map between the name used in the tutorial, the corresponding BGLR component, and the genomic input supplied to the fit. Six methods operate directly on `M`; GBLUP uses `G`. The subsections that follow explain how the prior or genomic representation changes across methods.",
            "The following table relates each method to its BGLR component and the genomic input supplied to the fit. Six methods operate directly on `M`; GBLUP uses `G`. The subsections that follow explain how the prior or genomic representation changes across methods.",
            "catalogue prose EN",
        )
        text = replace_once(
            text,
            '  format_table(caption = "Genomic prediction methods evaluated")\n```',
            '  format_table(caption = "Genomic prediction methods evaluated")\n```\n\nThe main distinction among the six regression methods is the prior assigned to marker effects. GBLUP changes the representation: instead of estimating effects for individual columns of `M`, it models the genomic-value vector directly with covariance defined by `G`.',
            "catalogue interpretation EN",
        )
        text = replace_once(
            text,
            "```{r bl-lambda}\n# Split R2 across the two linear predictor terms: family and the BL genomic component.",
            "In the code, `apply(M, 2, function(x) sum(x^2))` traverses the columns of `M` (`2` selects the column margin) and calculates the sum of squares for each. Their sum divided by `nrow(M)` gives the first term of `MS_x`; `sum(colMeans(M)^2)` gives the second. Finally, `sqrt()` converts `BL_LAMBDA_SQUARED` into `BL_LAMBDA`.\n\n```{r bl-lambda}\n# Split R2 across the two linear predictor terms: family and the BL genomic component.",
            "BL calculation explanation EN",
        )
        text = text.replace("In this tutorial, \\(\\lambda\\) is fixed at this", "In this analysis, \\(\\lambda\\) is fixed at this")
        text = replace_once(
            text,
            "The family term is common to all seven methods. Each model then receives its corresponding genomic component. In `ETA_models`, `fixed` identifies the family term and `genomic` identifies the term that differentiates methods. `X = M` is used for marker regressions, whereas `K = G` is used for GBLUP. Only BayesB2 and BL receive additional arguments because their parameterizations were explicitly fixed in the preceding sections.",
            "BGLR's `ETA` argument receives a list of predictor terms. `family_term <- list(X = X_fixed, model = \"FIXED\")` associates the family-contrast matrix with fixed coefficients. Within `ETA_models`, every method contains two named elements: `fixed`, shared by all seven models, and `genomic`, which defines the genomic component.\n\nFor marker regressions, `X = M` supplies the centered dosages and `model` selects the corresponding prior (`BRR`, `BayesA`, `BayesB`, `BayesC`, or `BL`). In GBLUP, `K = G` supplies the covariance matrix directly to the `RKHS` component. BayesB2 additionally supplies `probIn` and `counts`; BL supplies `type = \"FIXED\"` and `lambda = BL_LAMBDA`. Thus, intercept and family structure remain unchanged while only the genomic specification varies across methods.",
            "ETA explanation EN",
        )
        text = replace_once(
            text,
            "The same seven specifications are applied to all ten traits and five folds. Their Cartesian product creates 350 rows: 50 fits per method, corresponding to ten traits across five folds. After the combinations are placed in a stable order, every row receives a sequential run number, a unique seed, and a readable `Run_id`. The seed controls reproducibility of that chain only; it does not alter the folds.",
            "The same seven specifications are applied to all ten traits and five folds. `expand.grid(Trait = traits, Fold = ..., Method = method_names)` builds the Cartesian product of these three dimensions, producing 350 rows: 50 fits per method.\n\nThe expression `order(match(run_design$Trait, traits), run_design$Fold, match(run_design$Method, method_names))` restores the order defined by the original trait and method vectors and, within them, by fold. `seq_len(nrow(run_design))` assigns the sequential run number; the seed is `SEED_BASE + Run_number`; and `paste(..., sep = \"_\")` combines trait, fold, and method into a readable identifier. The seed controls reproducibility of that chain only; it does not alter the folds.",
            "run design EN",
        )
        text = replace_once(
            text,
            '  format_table(caption = "Number of fits by method")\n```',
            '  format_table(caption = "Number of fits by method")\n```\n\nEach method appears in `r nrow(run_design) / length(method_names)` combinations, for `r nrow(run_design)` fits overall. Because the same trait × fold grid is used for every method, downstream comparisons start from the same validation design.',
            "run design interpretation EN",
        )
        text = replace_once(
            text,
            "The block below iterates over the trait, fold, and method combinations. Before the loop, the tutorial maps the native BGLR scalar files used for diagnostics. `genomic_trace_suffix` identifies the file, `genomic_trace_header` states whether it has a header, `genomic_trace_column` selects the scalar column, and `genomic_trace_parameter` supplies the label shown downstream.",
            "Model fitting iterates over the trait, fold, and method combinations. Before the loop, four named vectors map the native BGLR scalar files used for diagnostics: `genomic_trace_suffix` identifies the file, `genomic_trace_header` states whether it has a header, `genomic_trace_column` selects the scalar column, and `genomic_trace_parameter` supplies the label shown downstream.",
            "trace intro EN",
        )
        old_fit_intro = '''The `fit-models` chunk contains the complete procedure for reproducing all 350 fits, but remains `eval=FALSE` in the page. This prevents routine tutorial rendering from restarting the MCMC chains and overwriting their files. For a full reproduction from scratch, this is the block that must be run deliberately after Modules 01 and 02 have produced their objects.\n\nFor each run, the code masks only the 30 phenotypes in the current fold, calls `BGLR()` with the corresponding specification, records elapsed time and warnings, recovers predictions for the masked individuals, and decomposes `yHat` into intercept, fixed family effect, and genomic component. The scalar files written by BGLR include saved draws from burn-in iterations, so the code explicitly removes the first `BURN_IN_SAVED_SAMPLES` rows before computing ESS and Geweke diagnostics.'''
        new_fit_intro = '''The 350 fits are computationally intensive. The complete fitting block remains `eval=FALSE`, so rebuilding the pages does not restart the chains or overwrite their files. To reproduce the analysis from scratch, this block must be run deliberately after Modules 01 and 02 have produced their objects.\n\nEach fit follows a sequence that can be read directly from the code:\n\n1. **Select the trait and fold.** `validation_index <- which(cv_folds$Fold == fold_number)` locates the 30 validation candidates and `training_index` locates the other 120. The copy `y_model` receives `NA` only at validation positions, so a candidate's phenotype does not contribute to its own fit.\n2. **Select the specification and fit BGLR.** `ETA_models[[method_name]]` retrieves the current method's `ETA`. `BGLR::BGLR()` receives the masked response, `nIter`, `burnIn`, `thin`, `R2`, and the chain-file prefix. `withCallingHandlers()` records warning messages without interrupting the loop.\n3. **Recover predictions and components.** `fit$yHat[validation_index]` gives the OOF predictions. The matrix product `X_fixed %*% fit$ETA$fixed$b` calculates the fixed family component. Because `yHat = mu + fixed component + genomic component`, `fit$yHat - fit$mu - fixed_component` recovers the genomic component.\n4. **Calculate metrics.** `cor()` gives observed–predicted correlation; RMSE is the square root of mean squared error; MAE is mean absolute error; `mean(predicted - observed)` measures bias; and `cov(observed, predicted) / var(predicted)` gives the slope from regressing observed on predicted values. DIC and `pD` come from the Bayesian fit and are not OOF metrics.\n5. **Record available method-specific parameters.** Expressions such as `c(fit$ETA$genomic$probIn, NA_real_)[1]` return the parameter when it exists and `NA` when the method does not provide it, allowing one common result table across methods.\n6. **Read and trim chains.** `scan()` reads the residual-variance scalar chain; `read.table()` reads the method-specific scalar file. `seq.int(BURN_IN_SAVED_SAMPLES + 1L, ...)` keeps only post-burn-in draws and `cbind()` joins both series.\n7. **Calculate diagnostics.** `coda::mcmc()` attaches chain start and thinning information. `effectiveSize()` estimates effective sample size and `geweke.diag()` calculates the Geweke statistic.\n\nNative BGLR scalar files also contain draws saved during burn-in, which is why `BURN_IN_SAVED_SAMPLES` is removed explicitly before diagnostics.'''
        text = replace_once(text, old_fit_intro, new_fit_intro, "fit intro EN")
        text = replace_once(
            text,
            "Because the fitting chunks remain disabled during rendering, tables previously produced by the complete fitting procedure are read from `output/models/`. This allows the inspection and presentation sections of the page to be rebuilt without running all 350 chains again.",
            "The consolidated tables produced by the 350 fits are read from `output/models/`. `read.csv(..., check.names = FALSE)` restores each file without changing its column names. This makes predictions, genomic values, metrics, and diagnostics available from persisted outputs without recalculating the MCMC chains.",
            "combine results EN",
        )
        text = replace_once(
            text,
            '  format_table(digits = 4, caption = "Example of out-of-fold predictions")\n```',
            '  format_table(digits = 4, caption = "Example of out-of-fold predictions")\n```\n\nEach row corresponds to an individual when its phenotype was masked. The intercept, fixed family component, and genomic component together reproduce the total prediction stored in `Predicted`.',
            "prediction interpretation EN",
        )
        text = replace_once(
            text,
            '  format_table(digits = 4, caption = "Example of fold-level model metrics")\n```',
            '  format_table(digits = 4, caption = "Example of fold-level model metrics")\n```\n\nEach trait–fold–method combination therefore carries both OOF predictive metrics and Bayesian fit criteria. These two groups of measures answer different questions and are compared separately in Module 04.',
            "metrics interpretation EN",
        )
        text = replace_once(
            text,
            '  format_table(caption = "Dimensions of the main model-fitting outputs")\n```',
            '  format_table(caption = "Dimensions of the main model-fitting outputs")\n```\n\nThe four consolidated tables confirm the expected totals: `r nrow(cv_metrics_by_fold)` fits, `r nrow(cv_predictions)` OOF predictions, `r nrow(genomic_values_by_fold)` fold-level genomic values, and `r nrow(convergence_diagnostics)` scalar diagnostics.',
            "output size interpretation EN",
        )
        text = replace_once(
            text,
            '    caption = "Summary of MCMC diagnostics by method"\n  )\n```',
            '    caption = "Summary of MCMC diagnostics by method"\n  )\n```\n\nThe summary reports how many chains were evaluated and how many crossed at least one screening threshold for each method. `Minimum_ESS`, `Median_ESS`, and `Maximum_absolute_Geweke` describe the strength of autocorrelation or stability signals without treating the thresholds as formal validity tests.',
            "convergence summary interpretation EN",
        )
        text = replace_once(
            text,
            '    caption = "Chains highlighted by ESS or Geweke diagnostics"\n  )\n```',
            '    caption = "Chains highlighted by ESS or Geweke diagnostics"\n  )\n```\n\nThe detailed table identifies the exact trait, fold, method, and parameter associated with each flag. Highlighted rows guide additional inspection; they do not automatically exclude fits or predictions.',
            "flags interpretation EN",
        )
        text = replace_once(
            text,
            "After the diagnostics, the convergence table is updated with review flags, the method-level summary is saved, and the final object is assembled for downstream modules. Like model fitting, this chunk remains `eval=FALSE` during rendering: it should be run when the primary tables are regenerated so that `models_object.rds` is updated consistently with those outputs.",
            "After diagnostics, the convergence table is updated with review flags, the method-level summary is saved, and `models_object.rds` collects settings, run design, method catalogue, predictions, genomic values, metrics, and diagnostics. This block accompanies complete regeneration of the fits and remains `eval=FALSE`; when primary results are recalculated, it should be executed so the final object stays consistent with the written tables.",
            "save prose EN",
        )
        text = replace_once(
            text,
            "Module 04 uses the OOF predictions, fold-level metrics, genomic values, and MCMC\ndiagnostics obtained here to compare methods and derive downstream genomic\nresults.",
            "Module 04 uses the OOF predictions, fold-level metrics, genomic values, and MCMC\ndiagnostics obtained here to compare methods and derive downstream genomic\nresults.\n\n<div style=\"display:flex; justify-content:space-between; gap:1rem; margin-top:2rem; padding-top:1rem; border-top:1px solid #ddd;\">\n<a href=\"02_matrices_en.html\">← Module 02 — Matrix construction</a>\n<a href=\"04_results_en.html\">Module 04 — Comparison and selection →</a>\n</div>",
            "navigation EN",
        )
        text = text.replace("  # List the values corresponding to the table entries.\n", "")
        text = text.replace("# Assemble the table presented in this section.\n", "")
        text = text.replace("  # Describe the effect structure adopted by each method.\n", "")
        text = text.replace("# Prepare the information used in the MCMC chain diagnostics.\n", "")
        text = text.replace("# Assemble the summary table presented in this section.\n", "")
        text = text.replace("  # Count the number of records produced in each module output.\n", "")

    p.write_text(text, encoding="utf-8")
