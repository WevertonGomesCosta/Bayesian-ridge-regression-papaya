# Canonical M03 single-execution fitting pipeline

# Execute explicitly with:

#   Rscript --vanilla analysis/03_models_fit.R



suppressPackageStartupMessages({
  library(BGLR)
  library(coda)
  library(digest)
  library(dplyr)
  library(knitr)
  library(here)
})

MATRICES_FILE <- here(
  "output",
  "matrices",
  "matrices_object.rds"
)

OUTPUT_DIR <- here(
  "output",
  "models"
)


BGLR_DIR <- file.path(
  OUTPUT_DIR,
  "bglr"
)

N_ITER <- 1000000L
BURN_IN <- 200000L
THIN <- 4L
R2_PRIOR <- 0.5

RAW_SAVED_SAMPLES <- floor(
  N_ITER / THIN
)

BURN_IN_SAVED_SAMPLES <- floor(
  BURN_IN / THIN
)

RETAINED_SAMPLES <-
  RAW_SAVED_SAMPLES -
  BURN_IN_SAVED_SAMPLES

PIPELINE_VERSION <-
  "module03-full-v4-bl-fixed"


SEED_BASE <- 202608050L

BAYESB2_ZERO_PROBABILITY <- 1e-5
BAYESB2_PROB_IN <-
  1 - BAYESB2_ZERO_PROBABILITY
BAYESB2_COUNTS <- 1e6

ESS_REVIEW_THRESHOLD <- 1000
GEWEKE_REVIEW_THRESHOLD <- 2

BL_LAMBDA_TYPE <- "FIXED"
BL_LAMBDA_TOLERANCE_REL <- 1e-10


dir.create(
  BGLR_DIR,
  recursive = TRUE,
  showWarnings = FALSE
)

matrices_object <- readRDS(
  MATRICES_FILE
)

ids <- matrices_object$ids
metadata <- matrices_object$metadata
phenotypes <- matrices_object$phenotypes
trait_dictionary <- matrices_object$trait_dictionary
X <- matrices_object$X
M <- matrices_object$M
G <- matrices_object$G
cv_folds <- matrices_object$cv_folds

traits <- colnames(
  phenotypes
)

X_fixed <- X[
  ,
  colnames(X) != "(Intercept)",
  drop = FALSE
]

method_names <- c(
  "RRBLUP",
  "BayesA",
  "BayesB",
  "BayesB2",
  "BayesC",
  "BL",
  "GBLUP"
)

method_labels <- c(
  RRBLUP = "RR-BLUP",
  BayesA = "BayesA",
  BayesB = "BayesB",
  BayesB2 = "BayesB2",
  BayesC = "BayesC",
  BL = "Bayesian Lasso",
  GBLUP = "GBLUP"
)

model_catalogue <- data.frame(
  Method = method_names,
  Label = unname(
    method_labels[
      method_names
    ]
  ),
  BGLR_component = c(
    "BRR",
    "BayesA",
    "BayesB",
    "BayesB",
    "BayesC",
    "BL",
    "RKHS"
  ),
  Genomic_input = c(
    "M",
    "M",
    "M",
    "M",
    "M",
    "M",
    "G"
  ),
  Main_assumption = c(
    "Common Gaussian variance for all marker effects",
    "Marker-specific scaled-t variances",
    "Scaled-t slab and a point mass at zero",
    "BayesB with zero-effect probability near 1e-5",
    "Common Gaussian slab and a point mass at zero",
    "Double-exponential marginal prior; lambda fixed at BGLR-calibrated lambda0",
    "Genomic values structured by G"
  )
)

# BGLR counts both ETA terms when it allocates R2 to the BL component:
# one family FIXED term and one genomic BL term.
BL_N_LINEAR_TERMS <- 2L
BL_COMPONENT_R2 <- R2_PRIOR / BL_N_LINEAR_TERMS

# Exact BGLR default calibration used by setLT.BL when lambda is omitted.
# M is global, so MSx and lambda0 are global constants across traits/folds.
BL_MSX <-
  sum(
    apply(
      M,
      2,
      function(x) sum(x^2)
    )
  ) / nrow(M) -
  sum(
    colMeans(M)^2
  )

BL_LAMBDA_SQUARED <-
  2 *
  (1 - R2_PRIOR) /
  BL_COMPONENT_R2 *
  BL_MSX

BL_LAMBDA <- sqrt(
  BL_LAMBDA_SQUARED
)

BL_LAMBDA_TOLERANCE <- max(
  1e-12,
  abs(BL_LAMBDA) *
    BL_LAMBDA_TOLERANCE_REL
)

stopifnot(
  is.finite(BL_COMPONENT_R2),
  BL_COMPONENT_R2 > 0,
  is.finite(BL_MSX),
  BL_MSX > 0,
  is.finite(BL_LAMBDA),
  BL_LAMBDA > 0
)

ETA_models <- list(
  RRBLUP = list(
    fixed = list(
      X = X_fixed,
      model = "FIXED"
    ),
    genomic = list(
      X = M,
      model = "BRR"
    )
  ),
  BayesA = list(
    fixed = list(
      X = X_fixed,
      model = "FIXED"
    ),
    genomic = list(
      X = M,
      model = "BayesA"
    )
  ),
  BayesB = list(
    fixed = list(
      X = X_fixed,
      model = "FIXED"
    ),
    genomic = list(
      X = M,
      model = "BayesB"
    )
  ),
  BayesB2 = list(
    fixed = list(
      X = X_fixed,
      model = "FIXED"
    ),
    genomic = list(
      X = M,
      model = "BayesB",
      probIn = BAYESB2_PROB_IN,
      counts = BAYESB2_COUNTS
    )
  ),
  BayesC = list(
    fixed = list(
      X = X_fixed,
      model = "FIXED"
    ),
    genomic = list(
      X = M,
      model = "BayesC"
    )
  ),
  BL = list(
    fixed = list(
      X = X_fixed,
      model = "FIXED"
    ),
    genomic = list(
      X = M,
      model = "BL",
      type = BL_LAMBDA_TYPE,
      lambda = BL_LAMBDA
    )
  ),
  GBLUP = list(
    fixed = list(
      X = X_fixed,
      model = "FIXED"
    ),
    genomic = list(
      K = G,
      model = "RKHS"
    )
  )
)

genomic_trace_suffix <- c(
  RRBLUP = "ETA_genomic_varB.dat",
  BayesA = "ETA_genomic_ScaleBayesA.dat",
  BayesB = "ETA_genomic_parBayesB.dat",
  BayesB2 = "ETA_genomic_parBayesB.dat",
  BayesC = "ETA_genomic_parBayesC.dat",
  BL = "mu.dat",
  GBLUP = "ETA_genomic_varU.dat"
)

genomic_trace_header <- c(
  RRBLUP = FALSE,
  BayesA = FALSE,
  BayesB = TRUE,
  BayesB2 = TRUE,
  BayesC = TRUE,
  BL = FALSE,
  GBLUP = FALSE
)

genomic_trace_column <- c(
  RRBLUP = 1L,
  BayesA = 1L,
  BayesB = 2L,
  BayesB2 = 2L,
  BayesC = 2L,
  BL = 1L,
  GBLUP = 1L
)

genomic_trace_parameter <- c(
  RRBLUP = "Marker_variance",
  BayesA = "Scale",
  BayesB = "Scale",
  BayesB2 = "Scale",
  BayesC = "Marker_variance",
  BL = "Intercept",
  GBLUP = "Genomic_variance"
)

run_design <- expand.grid(
  Trait = traits,
  Fold = seq_len(
    matrices_object$settings$n_folds
  ),
  Method = method_names,
  stringsAsFactors = FALSE
)

run_design <- run_design[
  order(
    match(
      run_design$Trait,
      traits
    ),
    run_design$Fold,
    match(
      run_design$Method,
      method_names
    )
  ),
]

rownames(run_design) <- NULL

run_design$Run_number <- seq_len(
  nrow(run_design)
)

run_design$Seed <-
  SEED_BASE +
  run_design$Run_number

analysis_settings <- list(
  pipeline_version = PIPELINE_VERSION,
  n_iter = N_ITER,
  burn_in = BURN_IN,
  thin = THIN,
  R2 = R2_PRIOR,
  seed_base = SEED_BASE,
  bayesb2_zero_probability = BAYESB2_ZERO_PROBABILITY,
  bayesb2_prob_in = BAYESB2_PROB_IN,
  bayesb2_counts = BAYESB2_COUNTS,
  bl_lambda_type = BL_LAMBDA_TYPE,
  bl_n_linear_terms = BL_N_LINEAR_TERMS,
  bl_component_R2 = BL_COMPONENT_R2,
  bl_msx = BL_MSX,
  bl_lambda_squared = BL_LAMBDA_SQUARED,
  bl_lambda = BL_LAMBDA,
  bl_lambda_tolerance = BL_LAMBDA_TOLERANCE,
  bl_tau2_warning_policy = "review_not_structural",
  traits = traits,
  folds = seq_len(
    matrices_object$settings$n_folds
  ),
  methods = method_names
)

analysis_signature <- substr(
  digest::digest(
    list(
      ids = ids,
      phenotypes = phenotypes,
      X = X,
      M = M,
      G = G,
      cv_folds = cv_folds,
      settings = analysis_settings
    ),
    algo = "sha256"
  ),
  1,
  16
)

run_design$Signature <- analysis_signature

run_design$Run_id <- paste(
  run_design$Trait,
  paste0("F", run_design$Fold),
  run_design$Method,
  sep = "_"
)

write.csv(
  run_design,
  file.path(OUTPUT_DIR, "run_design.csv"),
  row.names = FALSE
)

metric_parts <- vector("list", nrow(run_design))
prediction_parts <- vector("list", nrow(run_design))
genomic_value_parts <- vector("list", nrow(run_design))
convergence_parts <- vector("list", nrow(run_design))

for (run_index in seq_len(nrow(run_design))) {
  trait_name <-
    run_design$Trait[
      run_index
    ]

  fold_number <-
    run_design$Fold[
      run_index
    ]

  method_name <-
    run_design$Method[
      run_index
    ]

  run_id <-
    run_design$Run_id[
      run_index
    ]

  cat(sprintf("[%03d/%03d] %s\n", run_index, nrow(run_design), run_id))

  run_seed <-
    run_design$Seed[
      run_index
    ]

  bglr_run_dir <- file.path(
    BGLR_DIR,
    trait_name,
    paste0(
      "F",
      fold_number
    ),
    method_name
  )

  dir.create(
    bglr_run_dir,
    recursive = TRUE,
    showWarnings = FALSE
  )

  save_prefix <- file.path(
    bglr_run_dir,
    "bglr_"
  )

  unlink(
    Sys.glob(
      paste0(
        save_prefix,
        "*"
      )
    )
  )

  y_observed <- phenotypes[
    ,
    trait_name
  ]

  names(y_observed) <- ids

  validation_index <- which(
    cv_folds$Fold == fold_number
  )

  training_index <- which(
    cv_folds$Fold != fold_number
  )

  y_model <- y_observed
  y_model[validation_index] <- NA_real_

  set.seed(
    run_seed
  )

  fit_start <- proc.time()[["elapsed"]]

  run_warning_messages <- character(0)

  fit <- withCallingHandlers(
    BGLR::BGLR(
      y = y_model,
      ETA = ETA_models[[method_name]],
      response_type = "gaussian",
      nIter = N_ITER,
      burnIn = BURN_IN,
      thin = THIN,
      R2 = R2_PRIOR,
      saveAt = save_prefix,
      verbose = FALSE,
      rmExistingFiles = TRUE
    ),
    warning = function(w) {
      run_warning_messages <<- c(
        run_warning_messages,
        conditionMessage(w)
      )
      invokeRestart(
        "muffleWarning"
      )
    }
  )

  fit_end <- proc.time()[["elapsed"]]

  tau2_warning_count <- sum(
    grepl(
      "tau2 was not updated",
      run_warning_messages,
      fixed = TRUE
    )
  )

  lambda_update_warning_count <- sum(
    grepl(
      "lambda was not updated",
      run_warning_messages,
      fixed = TRUE
    )
  )

  bl_lambda_observed <- NA_real_
  bl_lambda_max_abs_error <- NA_real_
  bl_lambda_native_value <- NA_real_
  bl_lambda_native_unique <- NA_integer_
  bl_lambda_native_serialization_error <- NA_real_
  bl_lambda_native_valid <- NA
  bl_lambda_valid <- NA

  if (method_name == "BL") {
    # The analytical contract is checked against the in-memory BGLR object.
    # The native text file is intentionally not used for full-precision
    # equality because BGLR serializes this trace with limited text precision.
    bl_lambda_observed <- as.numeric(
      fit$ETA$genomic$lambda
    )

    bl_lambda_max_abs_error <- abs(
      bl_lambda_observed -
        BL_LAMBDA
    )

    bl_lambda_trace_full <- scan(
      paste0(
        save_prefix,
        "ETA_genomic_lambda.dat"
      ),
      quiet = TRUE
    )

    bl_lambda_native_unique <- length(
      unique(
        bl_lambda_trace_full
      )
    )

    bl_lambda_native_value <- if (
      length(
        bl_lambda_trace_full
      ) > 0L
    ) {
      bl_lambda_trace_full[1]
    } else {
      NA_real_
    }

    bl_lambda_native_serialization_error <- if (
      is.finite(
        bl_lambda_native_value
      )
    ) {
      abs(
        bl_lambda_native_value -
          BL_LAMBDA
      )
    } else {
      Inf
    }

    bl_lambda_native_valid <-
      length(
        bl_lambda_trace_full
      ) == RAW_SAVED_SAMPLES &&
      all(
        is.finite(
          bl_lambda_trace_full
        )
      ) &&
      all(
        bl_lambda_trace_full > 0
      ) &&
      bl_lambda_native_unique == 1L

    bl_lambda_valid <-
      length(
        bl_lambda_observed
      ) == 1L &&
      is.finite(
        bl_lambda_observed
      ) &&
      bl_lambda_observed > 0 &&
      bl_lambda_max_abs_error <=
        BL_LAMBDA_TOLERANCE &&
      bl_lambda_native_valid

    if (!bl_lambda_valid) {
      stop(
        "BL FIXED-lambda contract failed for ",
        run_id
      )
    }

    if (lambda_update_warning_count > 0L) {
      stop(
        "Unexpected lambda-update warning under BL type=FIXED for ",
        run_id
      )
    }
  }

  predicted_validation <- fit$yHat[
    validation_index
  ]

  observed_validation <- y_observed[
    validation_index
  ]

  fixed_component <- as.vector(
    X_fixed %*%
      fit$ETA$fixed$b
  )

  genomic_component <- as.vector(
    fit$yHat -
      fit$mu -
      fixed_component
  )

  genomic_value_table <- data.frame(
    Run_id = rep(
      run_id,
      length(ids)
    ),
    Signature = rep(
      analysis_signature,
      length(ids)
    ),
    IND = ids,
    Trait = rep(
      trait_name,
      length(ids)
    ),
    Fold = rep(
      fold_number,
      length(ids)
    ),
    Method = rep(
      method_name,
      length(ids)
    ),
    Genomic_value =
      genomic_component
  )

  prediction_table <- data.frame(
    Run_id = run_id,
    Signature = analysis_signature,
    IND = ids[
      validation_index
    ],
    Trait = trait_name,
    Fold = fold_number,
    Method = method_name,
    Observed = observed_validation,
    Predicted = predicted_validation,
    Fixed_component =
      fixed_component[
        validation_index
      ],
    Genomic_component =
      genomic_component[
        validation_index
      ]
  )

  posterior_prob_in <- c(
    fit$ETA$genomic$probIn,
    NA_real_
  )[1]

  metric_table <- data.frame(
    Run_id = run_id,
    Signature = analysis_signature,
    Trait = trait_name,
    Fold = fold_number,
    Method = method_name,
    Seed = run_seed,
    Training_n = length(
      training_index
    ),
    Validation_n = length(
      validation_index
    ),
    Correlation = cor(
      observed_validation,
      predicted_validation
    ),
    RMSE = sqrt(
      mean(
        (
          observed_validation -
            predicted_validation
        )^2
      )
    ),
    MAE = mean(
      abs(
        observed_validation -
          predicted_validation
      )
    ),
    Prediction_bias = mean(
      predicted_validation -
        observed_validation
    ),
    Regression_slope =
      cov(
        observed_validation,
        predicted_validation
      ) /
      var(
        predicted_validation
      ),
    DIC = fit$fit$DIC,
    Effective_parameters =
      fit$fit$pD,
    Log_likelihood_at_posterior_mean =
      fit$fit$
        logLikAtPostMean,
    Posterior_mean =
      fit$mu,
    Posterior_mean_SD = c(
      fit$SD.mu,
      NA_real_
    )[1],
    Residual_variance =
      fit$varE,
    Residual_variance_SD = c(
      fit$SD.varE,
      NA_real_
    )[1],
    BL_lambda =
      bl_lambda_observed,
    BL_lambda_native_value =
      bl_lambda_native_value,
    BL_lambda_native_serialization_error =
      bl_lambda_native_serialization_error,
    BL_lambda_native_valid =
      bl_lambda_native_valid,
    BL_lambda_valid =
      bl_lambda_valid,
    BGLR_warning_count =
      length(
        run_warning_messages
      ),
    Tau2_warning_count =
      tau2_warning_count,
    Lambda_update_warning_count =
      lambda_update_warning_count,
    Posterior_probIn =
      posterior_prob_in,
    Elapsed_seconds =
      fit_end - fit_start,
    Finite_predictions = all(
      is.finite(
        predicted_validation
      )
    )
  )

  metric_table$Finite_metrics <- all(
    is.finite(
      as.numeric(
        metric_table[
          ,
          c(
            "Correlation",
            "RMSE",
            "MAE",
            "Prediction_bias",
            "Regression_slope",
            "DIC",
            "Effective_parameters",
            "Log_likelihood_at_posterior_mean",
            "Posterior_mean",
            "Residual_variance",
            "Elapsed_seconds"
          )
        ]
      )
    )
  )

  residual_trace_full <- scan(
    paste0(
      save_prefix,
      "varE.dat"
    ),
    quiet = TRUE
  )

  genomic_trace_table_full <- read.table(
    paste0(
      save_prefix,
      genomic_trace_suffix[
        method_name
      ]
    ),
    header =
      genomic_trace_header[
        method_name
      ],
    check.names = FALSE
  )

  genomic_trace_full <-
    genomic_trace_table_full[
      ,
      genomic_trace_column[
        method_name
      ]
    ]

  posterior_sample_indices <- seq.int(
    from =
      BURN_IN_SAVED_SAMPLES +
      1L,
    to = length(
      residual_trace_full
    )
  )

  residual_trace <-
    residual_trace_full[
      posterior_sample_indices
    ]

  genomic_trace <-
    genomic_trace_full[
      posterior_sample_indices
    ]

  trace_matrix <- cbind(
    Residual_variance =
      residual_trace,
    Genomic_parameter =
      genomic_trace
  )

  trace_object <- coda::mcmc(
    trace_matrix,
    start = BURN_IN + THIN,
    thin = THIN
  )

  trace_ess <- coda::effectiveSize(
    trace_object
  )

  trace_geweke <- coda::geweke.diag(
    trace_object
  )$z

  trace_parameter_names <- c(
    "Residual_variance",
    unname(
      genomic_trace_parameter[
        method_name
      ]
    )
  )

  convergence_table <- data.frame(
    Run_id = rep(
      run_id,
      length(
        trace_parameter_names
      )
    ),
    Signature = rep(
      analysis_signature,
      length(
        trace_parameter_names
      )
    ),
    Trait = rep(
      trait_name,
      length(
        trace_parameter_names
      )
    ),
    Fold = rep(
      fold_number,
      length(
        trace_parameter_names
      )
    ),
    Method = rep(
      method_name,
      length(
        trace_parameter_names
      )
    ),
    Parameter =
      trace_parameter_names,
    Retained_samples = rep(
      nrow(
        trace_matrix
      ),
      length(
        trace_parameter_names
      )
    ),
    Posterior_mean = colMeans(
      trace_matrix
    ),
    Posterior_SD = apply(
      trace_matrix,
      2,
      sd
    ),
    Effective_sample_size = as.numeric(
      trace_ess
    ),
    Geweke_Z = as.numeric(
      trace_geweke
    )
  )

  convergence_table$Review_flag <-
    !is.finite(
      convergence_table$
        Effective_sample_size
    ) |
    convergence_table$
      Effective_sample_size <
      ESS_REVIEW_THRESHOLD |
    !is.finite(
      convergence_table$
        Geweke_Z
    ) |
    abs(
      convergence_table$
        Geweke_Z
    ) >
      GEWEKE_REVIEW_THRESHOLD

  metric_parts[[run_index]] <- metric_table
  prediction_parts[[run_index]] <- prediction_table
  genomic_value_parts[[run_index]] <- genomic_value_table
  convergence_parts[[run_index]] <- convergence_table

  fit <- NULL
  trace_object <- NULL

  gc(
    verbose = FALSE
  )
}

cv_metrics_by_fold <- bind_rows(metric_parts)
cv_predictions <- bind_rows(prediction_parts)
genomic_values_by_fold <- bind_rows(genomic_value_parts)
convergence_diagnostics <- bind_rows(convergence_parts)

convergence_summary <- convergence_diagnostics |>
  group_by(Method) |>
  summarise(
    Runs = n_distinct(Run_id),
    Parameters_reviewed = n(),
    Parameters_flagged = sum(Review_flag),
    Runs_with_flags = n_distinct(Run_id[Review_flag]),
    Minimum_ESS = min(Effective_sample_size, na.rm = TRUE),
    Median_ESS = median(Effective_sample_size, na.rm = TRUE),
    Maximum_absolute_Geweke = max(abs(Geweke_Z), na.rm = TRUE),
    .groups = "drop"
  )

convergence_summary$Method_label <-
  unname(method_labels[convergence_summary$Method])

expected_fits <- nrow(run_design)
expected_predictions <-
  length(ids) * length(traits) * length(method_names)

stopifnot(
  expected_fits == 350L,
  nrow(cv_metrics_by_fold) == expected_fits,
  nrow(cv_predictions) == expected_predictions,
  nrow(genomic_values_by_fold) == length(ids) * expected_fits,
  nrow(convergence_diagnostics) == 2L * expected_fits,
  length(unique(cv_metrics_by_fold$Signature)) == 1L,
  identical(unique(cv_metrics_by_fold$Signature), analysis_signature)
)

write.csv(cv_predictions, file.path(OUTPUT_DIR, "cv_predictions.csv"), row.names = FALSE)
write.csv(genomic_values_by_fold, file.path(OUTPUT_DIR, "genomic_values_by_fold.csv"), row.names = FALSE)
write.csv(cv_metrics_by_fold, file.path(OUTPUT_DIR, "cv_metrics_by_fold.csv"), row.names = FALSE)
write.csv(convergence_diagnostics, file.path(OUTPUT_DIR, "convergence_diagnostics.csv"), row.names = FALSE)
write.csv(convergence_summary, file.path(OUTPUT_DIR, "convergence_summary.csv"), row.names = FALSE)

saveRDS(
  list(
    signature = analysis_signature,
    settings = analysis_settings,
    run_design = run_design,
    model_catalogue = model_catalogue,
    trait_dictionary = trait_dictionary,
    predictions = cv_predictions,
    genomic_values_by_fold = genomic_values_by_fold,
    metrics_by_fold = cv_metrics_by_fold,
    convergence_diagnostics = convergence_diagnostics
  ),
  file.path(OUTPUT_DIR, "models_object.rds")
)

# Remove obsolete artifacts from the former resumable architecture only
# after all canonical outputs have been written successfully.




cat("\\nM03 single-execution pipeline completed.\\n")
cat("Signature:", analysis_signature, "\\n")
cat("Fits:", nrow(cv_metrics_by_fold), "\\n")
cat("Predictions:", nrow(cv_predictions), "\\n")
cat("BGLR directory:", BGLR_DIR, "\\n")
