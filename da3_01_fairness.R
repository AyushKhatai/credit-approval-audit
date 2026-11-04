library(dplyr)
library(tidyr)
library(ggplot2)
library(pROC)
source("da3_helpers.R")

B_BOOT <- 1000
B_PERM <- 2000
set.seed(2026)

pred <- read.csv("da2_test_predictions.csv", stringsAsFactors = FALSE)
res  <- read.csv("da2_model_results.csv",    stringsAsFactors = FALSE)

truth <- as.character(pred$true)
pos   <- truth == "Approved"
n     <- nrow(pred)
cat("Test applicants:", n, "| truly approved:", sum(pos), "\n")

keys     <- sub("_pred$", "", grep("_pred$", names(pred), value = TRUE))
name_map <- setNames(res$Model, make.names(res$Model))
display  <- unname(ifelse(keys %in% names(name_map), name_map[keys],
                          gsub(".", " ", keys, fixed = TRUE)))
cat("Models found:", length(keys), "\n")

group_vars <- c("A1", "A2_group")
for (gv in group_vars) pred[[gv]] <- as.character(pred[[gv]])

base_rates <- bind_rows(lapply(group_vars, function(gv) {
  data.frame(group_var = gv, group = pred[[gv]], approved = pos) %>%
    group_by(group_var, group) %>%
    summarise(n = n(), true_approval_rate = mean(approved), .groups = "drop")
}))

model_rows <- list()
group_rows <- list()
fair_rows  <- list()

for (i in seq_along(keys)) {
  key       <- keys[i]
  mname     <- display[i]
  predicted <- as.character(pred[[paste0(key, "_pred")]])
  prob      <- pred[[paste0(key, "_prob")]]
  pp        <- predicted == "Approved"
  message("Auditing: ", mname)

  acc <- mean(pp == pos)
  auc <- fast_auc(pos, prob)
  bs  <- replicate(B_BOOT, {
    idx <- sample.int(n, replace = TRUE)
    c(mean(pp[idx] == pos[idx]), fast_auc(pos[idx], prob[idx]))
  })
  model_rows[[i]] <- data.frame(
    model = mname,
    accuracy = acc, acc_lo = ci95(bs[1, ])[1], acc_hi = ci95(bs[1, ])[2],
    auc = auc,      auc_lo = ci95(bs[2, ])[1], auc_hi = ci95(bs[2, ])[2],
    cv_auc = res$CV_AUC[match(mname, res$Model)]
  )

  for (gv in group_vars) {
    g   <- as.integer(factor(pred[[gv]]))
    gt  <- group_table(truth, predicted, pred[[gv]])
    group_rows[[length(group_rows) + 1]] <- cbind(model = mname, group_var = gv, gt,
                                                  stringsAsFactors = FALSE)

    obs  <- gaps_fast(pos, pp, g)
    boot <- replicate(B_BOOT, {
      idx <- sample.int(n, replace = TRUE)
      gaps_fast(pos[idx], pp[idx], g[idx])
    })
    perm <- replicate(B_PERM, gaps_fast(pos, pp, sample(g)))

    fair_rows[[length(fair_rows) + 1]] <- data.frame(
      model = mname, group_var = gv, n_groups = max(g),
      dp_gap = obs["dp_gap"],
      dp_lo = ci95(boot["dp_gap", ])[1], dp_hi = ci95(boot["dp_gap", ])[2],
      dp_chance = mean(perm["dp_gap", ], na.rm = TRUE),
      dp_p = perm_p(perm["dp_gap", ], obs["dp_gap"]),
      eo_gap = obs["eo_gap"],
      eo_lo = ci95(boot["eo_gap", ])[1], eo_hi = ci95(boot["eo_gap", ])[2],
      eo_chance = mean(perm["eo_gap", ], na.rm = TRUE),
      eo_p = perm_p(perm["eo_gap", ], obs["eo_gap"]),
      eodds_gap = obs["eodds_gap"],
      di_ratio = obs["di_ratio"],
      row.names = NULL
    )
  }
}

model_summary <- bind_rows(model_rows)
group_metrics <- bind_rows(group_rows)
fair          <- bind_rows(fair_rows)

fair$dp_p_adj <- p.adjust(fair$dp_p, method = "holm")
fair$eo_p_adj <- p.adjust(fair$eo_p, method = "holm")

ref_i    <- which.max(model_summary$auc)
resp     <- factor(ifelse(pos, "Approved", "Rejected"), levels = c("Rejected", "Approved"))
roc_list <- lapply(keys, function(k)
  roc(response = resp, predictor = pred[[paste0(k, "_prob")]], quiet = TRUE,
      levels = c("Rejected", "Approved"), direction = "<"))
pp_ref   <- as.character(pred[[paste0(keys[ref_i], "_pred")]]) == "Approved"
ok_ref   <- pp_ref == pos

test_rows <- list()
for (j in seq_along(keys)) {
  if (j == ref_i) next
  ok_j <- (as.character(pred[[paste0(keys[j], "_pred")]]) == "Approved") == pos
  n_ref_only   <- sum(ok_ref & !ok_j)
  n_other_only <- sum(!ok_ref & ok_j)
  p_de <- tryCatch(roc.test(roc_list[[ref_i]], roc_list[[j]],
                            method = "delong", paired = TRUE)$p.value,
                   error = function(e) NA_real_)
  p_mc <- if (n_ref_only + n_other_only == 0) 1 else
    binom.test(n_ref_only, n_ref_only + n_other_only, 0.5)$p.value
  test_rows[[length(test_rows) + 1]] <- data.frame(
    ref_model = display[ref_i], model = display[j],
    auc = model_summary$auc[j],
    auc_diff = model_summary$auc[ref_i] - model_summary$auc[j],
    delong_p = p_de,
    ref_only_correct = n_ref_only, model_only_correct = n_other_only,
    mcnemar_exact_p = p_mc
  )
}
model_tests <- bind_rows(test_rows)
model_tests$delong_p_adj  <- p.adjust(model_tests$delong_p, method = "holm")
model_tests$mcnemar_p_adj <- p.adjust(model_tests$mcnemar_exact_p, method = "holm")

write.csv(model_summary, "da3_model_summary.csv",   row.names = FALSE)
write.csv(group_metrics, "da3_group_metrics.csv",   row.names = FALSE)
write.csv(fair,          "da3_fairness_summary.csv", row.names = FALSE)
write.csv(model_tests,   "da3_model_tests.csv",     row.names = FALSE)
write.csv(base_rates,    "da3_base_rates.csv",      row.names = FALSE)

gap_long <- bind_rows(
  fair %>% transmute(model, group_var, metric = "Approval-rate gap (demographic parity)",
                     gap = dp_gap, lo = dp_lo, hi = dp_hi),
  fair %>% transmute(model, group_var, metric = "Equal opportunity gap (TPR)",
                     gap = eo_gap, lo = eo_lo, hi = eo_hi)
)
p1 <- ggplot(gap_long, aes(x = reorder(model, gap), y = gap, ymin = lo, ymax = hi, colour = metric)) +
  geom_pointrange(position = position_dodge(width = 0.6), size = 0.35) +
  coord_flip() +
  facet_wrap(~ group_var, labeller = labeller(group_var = c(A1 = "Groups by A1", A2_group = "Groups by A2 quartile"))) +
  labs(title = "Fairness gaps by model (95% bootstrap interval)",
       x = NULL, y = "Gap (0 = groups treated equally)", colour = NULL) +
  theme_minimal() + theme(legend.position = "bottom")
ggsave("da3_fairness_gaps.png", p1, width = 10, height = 6, dpi = 150)

trade <- fair %>% left_join(model_summary, by = "model")
p2 <- ggplot(trade, aes(x = eo_gap, y = accuracy)) +
  geom_point(size = 2.5, colour = "#1F4E78") +
  geom_text(aes(label = model), size = 2.8, vjust = -0.8, check_overlap = TRUE) +
  facet_wrap(~ group_var, labeller = labeller(group_var = c(A1 = "Groups by A1", A2_group = "Groups by A2 quartile"))) +
  labs(title = "Accuracy vs fairness trade-off",
       x = "Equal opportunity gap (lower is fairer)", y = "Test accuracy") +
  theme_minimal()
ggsave("da3_tradeoff.png", p2, width = 10, height = 5.5, dpi = 150)

dir.create("da3_dashboard/data", recursive = TRUE, showWarnings = FALSE)
file.copy(c("da3_model_summary.csv", "da3_group_metrics.csv", "da3_fairness_summary.csv",
            "da3_model_tests.csv", "da3_base_rates.csv"),
          "da3_dashboard/data", overwrite = TRUE)

cat("\n--- Base rates (true labels) ---\n")
print(base_rates)
cat("\n--- Model summary ---\n")
print(model_summary %>% mutate(across(where(is.numeric), ~ round(.x, 3))))
cat("\n--- Fairness summary ---\n")
print(fair %>% mutate(across(where(is.numeric), ~ round(.x, 3))))
cat("\n--- Best model vs the rest ---\n")
print(model_tests %>% mutate(across(where(is.numeric), ~ round(.x, 3))))
