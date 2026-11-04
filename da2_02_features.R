library(tidyverse)
library(caret)
library(ranger)
library(DBI)
source("da2_db_config.R")

con <- get_con()
df <- dbGetQuery(con, "
  SELECT a.*, d.outcome
  FROM applicants a
  JOIN decisions d ON a.id = d.id
  ORDER BY a.id")
dbDisconnect(con)

names(df) <- toupper(names(df))
df <- df %>% rename(id = ID, outcome = OUTCOME)

cat_cols <- c("A1", "A4", "A5", "A6", "A7", "A9", "A10", "A12", "A13")
num_cols <- c("A2", "A3", "A8", "A11", "A14", "A15")

df$outcome <- factor(df$outcome, levels = c("Approved", "Rejected"))
dim(df)

set.seed(42)
train_idx <- createDataPartition(df$outcome, p = 0.8, list = FALSE)
train <- df[train_idx, ]
test  <- df[-train_idx, ]
table(train$outcome)
table(test$outcome)

mode_of <- function(x) {
  x <- x[!is.na(x)]
  names(which.max(table(x)))
}
medians <- sapply(train[num_cols], median, na.rm = TRUE)
modes   <- sapply(train[cat_cols], mode_of)

impute <- function(d) {
  for (v in num_cols) d[[v]][is.na(d[[v]])] <- medians[[v]]
  for (v in cat_cols) d[[v]][is.na(d[[v]])] <- modes[[v]]
  d
}
train <- impute(train)
test  <- impute(test)

all_levels <- lapply(df[cat_cols], function(x) sort(unique(na.omit(x))))
to_factor <- function(d) {
  for (v in cat_cols) d[[v]] <- factor(d[[v]], levels = all_levels[[v]])
  d
}
train <- to_factor(train)
test  <- to_factor(test)

colSums(is.na(train))
colSums(is.na(test))

age_breaks <- quantile(train$A2, probs = seq(0, 1, 0.25))
age_breaks[1] <- -Inf
age_breaks[5] <- Inf

engineer <- function(d) {
  d %>% mutate(
    A3_log  = log1p(A3),
    A8_log  = log1p(A8),
    A11_log = log1p(A11),
    A14_log = log1p(A14),
    A15_log = log1p(A15),
    A11_pos = factor(ifelse(A11 > 0, "yes", "no"), levels = c("no", "yes")),
    A15_pos = factor(ifelse(A15 > 0, "yes", "no"), levels = c("no", "yes")),
    A8_per_A2 = A8 / A2,
    A9_and_A10 = factor(ifelse(A9 == "t" & A10 == "t", "yes", "no"), levels = c("no", "yes")),
    A2_group = cut(A2, breaks = age_breaks, labels = c("Q1", "Q2", "Q3", "Q4"))
  )
}
train <- engineer(train)
test  <- engineer(test)

candidate_features <- setdiff(names(train), c("id", "outcome", "A2_group"))

nzv <- nearZeroVar(train[, candidate_features], saveMetrics = TRUE)
print(nzv[nzv$nzv, ])
candidate_features <- setdiff(candidate_features, rownames(nzv)[nzv$nzv])

num_feats <- candidate_features[sapply(train[, candidate_features], is.numeric)]
cor_mat   <- cor(train[, num_feats])
drop_corr <- findCorrelation(cor_mat, cutoff = 0.90, names = TRUE)
cat("Dropped for high correlation:", drop_corr, "\n")
candidate_features <- setdiff(candidate_features, drop_corr)

rf_data <- train[, c("outcome", candidate_features)]
set.seed(42)
rf  <- ranger(outcome ~ ., data = rf_data, num.trees = 500, importance = "permutation")
imp <- sort(rf$variable.importance, decreasing = TRUE)
print(round(imp, 4))

selected <- names(imp)[imp > 0]
if (length(selected) < 5) selected <- names(imp)[1:5]
cat("Selected", length(selected), "of", length(candidate_features), "features:\n")
print(selected)

imp_df <- data.frame(feature = names(imp), importance = as.numeric(imp)) %>%
  mutate(kept = feature %in% selected)
p <- ggplot(imp_df, aes(x = reorder(feature, importance), y = importance, fill = kept)) +
  geom_col() +
  coord_flip() +
  labs(title = "Feature importance (random forest, permutation)",
       x = "Feature", y = "Importance", fill = "Selected") +
  theme_minimal()
print(p)
ggsave("da2_feature_importance.png", p, width = 7, height = 5, dpi = 150)

write.csv(imp_df, "da2_feature_importance.csv", row.names = FALSE)
saveRDS(list(train = train, test = test,
             features = selected,
             all_features = candidate_features),
        "da2_data.rds")
