group_stats <- function(truth, predicted) {
  pos <- truth == "Approved"
  pp  <- predicted == "Approved"
  data.frame(
    n               = length(truth),
    n_true_approved = sum(pos),
    n_true_rejected = sum(!pos),
    approval_rate   = mean(pp),
    tpr             = if (any(pos))  mean(pp[pos])  else NA_real_,
    fpr             = if (any(!pos)) mean(pp[!pos]) else NA_real_,
    accuracy        = mean(pp == pos)
  )
}

group_table <- function(truth, predicted, group) {
  out <- lapply(split(seq_along(truth), group), function(idx) {
    cbind(group = as.character(group[idx[1]]),
          group_stats(truth[idx], predicted[idx]),
          stringsAsFactors = FALSE)
  })
  out <- do.call(rbind, out)
  rownames(out) <- NULL
  out
}

range_gap <- function(x) {
  x <- x[!is.na(x)]
  if (length(x) < 2) NA_real_ else max(x) - min(x)
}

gaps_fast <- function(pos, pp, g) {
  k     <- max(g)
  n_g   <- tabulate(g, k)
  n_pos <- tabulate(g[pos], k)
  n_neg <- tabulate(g[!pos], k)
  app   <- ifelse(n_g   > 0, tabulate(g[pp], k)        / n_g,   NA_real_)
  tpr   <- ifelse(n_pos > 0, tabulate(g[pp & pos], k)  / n_pos, NA_real_)
  fpr   <- ifelse(n_neg > 0, tabulate(g[pp & !pos], k) / n_neg, NA_real_)
  dp  <- range_gap(app)
  eo  <- range_gap(tpr)
  fp  <- range_gap(fpr)
  both <- c(eo, fp)
  mx  <- suppressWarnings(max(app, na.rm = TRUE))
  mn  <- suppressWarnings(min(app, na.rm = TRUE))
  c(dp_gap    = dp,
    eo_gap    = eo,
    eodds_gap = if (all(is.na(both))) NA_real_ else max(both, na.rm = TRUE),
    di_ratio  = if (is.finite(mx) && mx > 0) mn / mx else NA_real_)
}

fast_auc <- function(pos, prob) {
  n1 <- sum(pos)
  n0 <- sum(!pos)
  if (n1 == 0 || n0 == 0) return(NA_real_)
  r <- rank(prob)
  (sum(r[pos]) - n1 * (n1 + 1) / 2) / (n1 * n0)
}

ci95 <- function(x) unname(quantile(x, c(0.025, 0.975), na.rm = TRUE))

perm_p <- function(null_values, observed) {
  if (is.na(observed)) return(NA_real_)
  v <- null_values[!is.na(null_values)]
  (sum(v >= observed) + 1) / (length(v) + 1)
}
