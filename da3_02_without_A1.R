library(caret)
library(dplyr)
library(ggplot2)
source("da3_helpers.R")

d     <- readRDS("da2_data.rds")
trn   <- d$train
tst   <- d$test
feats <- d$features
if (!"A1" %in% feats) message("A1 was not among the selected features, so removing it changes nothing.")

variants <- list("With A1" = feats, "Without A1" = setdiff(feats, "A1"))

truth <- as.character(tst$outcome)
pos   <- truth == "Approved"
group_vars <- c("A1", "A2_group")

set.seed(123)
folds <- createMultiFolds(trn$outcome, k = 5, times = 2)
ctrl  <- trainControl(method = "repeatedcv", number = 5, repeats = 2, index = folds,
                      classProbs = TRUE, summaryFunction = twoClassSummary)

rows  <- list()
preds <- list()

for (v in names(variants)) {
  train_df <- trn[, c("outcome", variants[[v]])]
  test_x   <- tst[, variants[[v]], drop = FALSE]

  p <- ncol(model.matrix(outcome ~ ., data = train_df)) - 1
  rf_grid <- expand.grid(mtry = unique(pmax(1, round(c(0.15, 0.3, 0.5) * p))),
                         splitrule = c("gini", "extratrees"), min.node.size = c(1, 5))

  specs <- list(
    "Logistic Regression"  = list(method = "glm"),
    "Elastic Net Logistic" = list(method = "glmnet", tuneLength = 5),
    "Random Forest"        = list(method = "ranger", tuneGrid = rf_grid)
  )

  for (m in names(specs)) {
    message("Training: ", m, " (", v, ")")
    set.seed(123)
    fit <- do.call(caret::train, c(
      list(outcome ~ ., data = train_df, trControl = ctrl, metric = "ROC",
           preProcess = c("zv", "center", "scale")),
      specs[[m]]))
    cls  <- as.character(predict(fit, test_x))
    prob <- predict(fit, test_x, type = "prob")[, "Approved"]
    preds[[paste(m, v)]] <- cls
    pp <- cls == "Approved"

    for (gv in group_vars) {
      g <- as.integer(factor(as.character(tst[[gv]])))
      gg <- gaps_fast(pos, pp, g)
      rows[[length(rows) + 1]] <- data.frame(
        model = m, variant = v, group_var = gv,
        accuracy = mean(pp == pos), auc = fast_auc(pos, prob),
        dp_gap = gg["dp_gap"], eo_gap = gg["eo_gap"], row.names = NULL)
    }
  }
}

out <- bind_rows(rows)

changed <- sapply(c("Logistic Regression", "Elastic Net Logistic", "Random Forest"), function(m)
  mean(preds[[paste(m, "With A1")]] != preds[[paste(m, "Without A1")]]))
out$pct_predictions_changed <- round(100 * changed[out$model], 1)

write.csv(out, "da3_unawareness.csv", row.names = FALSE)
print(out %>% mutate(across(where(is.numeric), ~ round(.x, 3))))

long <- out %>%
  tidyr::pivot_longer(c(dp_gap, eo_gap), names_to = "metric", values_to = "gap") %>%
  mutate(metric = recode(metric, dp_gap = "Approval-rate gap", eo_gap = "Equal opportunity gap"))
p <- ggplot(long, aes(x = model, y = gap, fill = variant)) +
  geom_col(position = "dodge") +
  facet_grid(metric ~ group_var) +
  labs(title = "Fairness gaps with and without A1", x = NULL, y = "Gap", fill = NULL) +
  theme_minimal() + theme(axis.text.x = element_text(angle = 20, hjust = 1))
ggsave("da3_unawareness.png", p, width = 9, height = 6, dpi = 150)
