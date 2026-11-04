library(tidyverse)
library(caret)
library(pROC)
library(DBI)
source("da2_db_config.R")

options(xgboost.use_altreplicable = FALSE)

d     <- readRDS("da2_data.rds")
train <- d$train
test  <- d$test
feats <- d$features

train_df <- train[, c("outcome", feats)]
test_df  <- test[,  c("outcome", feats)]
test_y   <- test$outcome

baseline <- max(prop.table(table(test_y)))
cat("Majority-class baseline accuracy:", round(baseline, 3), "\n")

set.seed(123)
folds <- createMultiFolds(train_df$outcome, k = 5, times = 2)

ctrl <- trainControl(
  method          = "repeatedcv",
  number          = 5,
  repeats         = 2,
  index           = folds,
  classProbs      = TRUE,
  summaryFunction = twoClassSummary,
  savePredictions = "final"
)

xgb_grid <- expand.grid(
  nrounds          = c(50, 100, 200),
  max_depth        = c(2, 3, 4),
  eta              = c(0.05, 0.1, 0.3),
  gamma            = 0,
  colsample_bytree = 0.8,
  min_child_weight = 1,
  subsample        = 0.8
)

p <- ncol(model.matrix(outcome ~ ., data = train_df)) - 1
rf_grid <- expand.grid(
  mtry          = unique(pmax(1, round(c(0.15, 0.3, 0.5) * p))),
  splitrule     = c("gini", "extratrees"),
  min.node.size = c(1, 5)
)

specs <- list(
  "Logistic Regression"    = list(method = "glm"),
  "Elastic Net Logistic"   = list(method = "glmnet", tuneLength = 5),
  "LDA"                    = list(method = "lda"),
  "KNN"                    = list(method = "knn", tuneLength = 10),
  "Naive Bayes"            = list(method = "naive_bayes"),
  "Decision Tree"          = list(method = "rpart", tuneLength = 10),
  "Bagged Trees"           = list(method = "treebag"),
  "Random Forest"          = list(method = "ranger", tuneGrid = rf_grid),
  "Gradient Boosting GBM"  = list(method = "gbm", tuneLength = 3, verbose = FALSE),
  "XGBoost"                = list(method = "xgbTree", tuneGrid = xgb_grid),
  "SVM Linear"             = list(method = "svmLinear", tuneLength = 4),
  "SVM RBF"                = list(method = "svmRadial", tuneLength = 5),
  "Neural Net MLP"         = list(method = "nnet", tuneLength = 4,
                                  trace = FALSE, MaxNWts = 5000, maxit = 300)
)

models <- list()
for (nm in names(specs)) {
  message("Training: ", nm)
  set.seed(123)
  models[[nm]] <- tryCatch(
    do.call(caret::train, c(
      list(outcome ~ ., data = train_df, trControl = ctrl,
           metric = "ROC", preProcess = c("zv", "center", "scale")),
      specs[[nm]]
    )),
    error = function(e) {
      message("  FAILED: ", nm, " -> ", conditionMessage(e))
      NULL
    }
  )
}
models <- Filter(Negate(is.null), models)
cat("\nModels trained successfully:", length(models), "of", length(specs), "\n")

cv_tbl <- data.frame(
  Model  = names(models),
  CV_AUC = sapply(models, function(m) getTrainPerf(m)$TrainROC),
  row.names = NULL
)
print(cv_tbl[order(-cv_tbl$CV_AUC), ])

rs <- resamples(models)
print(bwplot(rs, metric = "ROC", main = "Cross-validated AUC by model"))

test_df_x <- test_df[, feats, drop = FALSE]

eval_model <- function(m, nm) {
  pred <- predict(m, test_df_x)
  prob <- predict(m, test_df_x, type = "prob")[, "Approved"]
  cm   <- confusionMatrix(pred, test_y, positive = "Approved")
  roc_obj <- roc(response = test_y, predictor = prob,
                 levels = c("Rejected", "Approved"), direction = "<", quiet = TRUE)
  data.frame(
    Model     = nm,
    Accuracy  = as.numeric(cm$overall["Accuracy"]),
    Precision = as.numeric(cm$byClass["Precision"]),
    Recall    = as.numeric(cm$byClass["Recall"]),
    F1        = as.numeric(cm$byClass["F1"]),
    AUC       = as.numeric(auc(roc_obj))
  )
}

results <- bind_rows(lapply(names(models), function(nm) eval_model(models[[nm]], nm))) %>%
  left_join(cv_tbl, by = "Model") %>%
  arrange(desc(AUC))
results[, -1] <- round(results[, -1], 3)
print(results)

write.csv(results, "da2_model_results.csv", row.names = FALSE)

plot_df <- results %>%
  select(Model, Accuracy, F1, AUC) %>%
  pivot_longer(-Model, names_to = "Metric", values_to = "Value")
p <- ggplot(plot_df, aes(x = reorder(Model, Value), y = Value, fill = Metric)) +
  geom_col(position = "dodge") +
  coord_flip() +
  labs(title = "Test-set performance by model", x = NULL, y = "Score") +
  theme_minimal()
print(p)
ggsave("da2_model_comparison.png", p, width = 8, height = 6, dpi = 150)

pred_tbl <- data.frame(
  id       = test$id,
  true     = test_y,
  A1       = test$A1,
  A2_group = test$A2_group
)
for (nm in names(models)) {
  key <- make.names(nm)
  pred_tbl[[paste0(key, "_pred")]] <- predict(models[[nm]], test_df_x)
  pred_tbl[[paste0(key, "_prob")]] <- predict(models[[nm]], test_df_x, type = "prob")[, "Approved"]
}
write.csv(pred_tbl, "da2_test_predictions.csv", row.names = FALSE)

con <- get_con()
res_db <- results
names(res_db) <- tolower(names(res_db))
dbWriteTable(con, "model_results", res_db, overwrite = TRUE)

dbGetQuery(con, "
  SELECT model, accuracy, f1, auc
  FROM model_results
  ORDER BY auc DESC
  LIMIT 5")

dbDisconnect(con)
