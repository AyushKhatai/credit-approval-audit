library(tidyverse)
library(naniar)
library(corrplot)

col_names <- paste0("A", 1:16)
credit <- read.csv("crx.data", header = FALSE, na.strings = "?", col.names = col_names, stringsAsFactors = FALSE)

credit$A16 <- factor(credit$A16, levels = c("+", "-"), labels = c("Approved", "Rejected"))
credit$approved_flag <- ifelse(credit$A16 == "Approved", 1, 0)

cat_cols <- c("A1", "A4", "A5", "A6", "A7", "A9", "A10", "A12", "A13")
credit[cat_cols] <- lapply(credit[cat_cols], as.factor)

num_cols <- c("A2", "A3", "A8", "A11", "A14", "A15")
credit[num_cols] <- lapply(credit[num_cols], as.numeric)

credit_clean <- credit
credit_clean$A2 <- ifelse(is.na(credit_clean$A2), median(credit_clean$A2, na.rm = TRUE), credit_clean$A2)
credit_clean$A14 <- ifelse(is.na(credit_clean$A14), median(credit_clean$A14, na.rm = TRUE), credit_clean$A14)

mode_impute <- function(x) {
  ux <- na.omit(as.character(x))
  names(which.max(table(ux)))
}
credit_clean$A1 <- ifelse(is.na(credit_clean$A1), mode_impute(credit_clean$A1), as.character(credit_clean$A1))
credit_clean$A7 <- ifelse(is.na(credit_clean$A7), mode_impute(credit_clean$A7), as.character(credit_clean$A7))
credit_clean$A1 <- as.factor(credit_clean$A1)
credit_clean$A7 <- as.factor(credit_clean$A7)

ggplot(credit_clean, aes(x = A16, fill = A16)) +
  geom_bar() +
  geom_text(stat = "count", aes(label = after_stat(count)), vjust = -0.4) +
  labs(title = "Distribution of Credit Approval Outcomes",
       x = "Outcome", y = "Number of Applicants") +
  theme_minimal() +
  theme(legend.position = "none")

credit_clean %>%
  select(A16, all_of(num_cols)) %>%
  pivot_longer(cols = all_of(num_cols), names_to = "attribute", values_to = "value") %>%
  ggplot(aes(x = A16, y = value, fill = A16)) +
  geom_boxplot(outlier.alpha = 0.3) +
  facet_wrap(~ attribute, scales = "free_y") +
  labs(title = "Continuous Attributes by Approval Outcome",
       x = "Outcome", y = "Value") +
  theme_minimal() +
  theme(legend.position = "none")

corr_matrix <- cor(credit_clean[, num_cols], use = "complete.obs")
corrplot(corr_matrix, method = "color", type = "upper",
         addCoef.col = "black", tl.col = "black", tl.srt = 45,
         title = "Correlation Heatmap of Continuous Attributes",
         mar = c(0, 0, 2, 0))

credit_clean %>%
  group_by(A9, A16) %>%
  summarise(n = n(), .groups = "drop") %>%
  group_by(A9) %>%
  mutate(pct = n / sum(n)) %>%
  ggplot(aes(x = A9, y = pct, fill = A16)) +
  geom_col(position = "fill") +
  scale_y_continuous(labels = scales::percent) +
  labs(title = "Approval Rate by A9 (Prior Default Proxy)",
       x = "A9", y = "Proportion", fill = "Outcome") +
  theme_minimal()

gg_miss_var(credit, show_pct = TRUE) +
  labs(title = "Missing Values by Attribute")

ggplot(credit_clean, aes(x = A15 + 1, fill = A16)) +
  geom_histogram(bins = 40, alpha = 0.7, position = "identity") +
  scale_x_log10() +
  labs(title = "Distribution of A15 (Income Proxy, log scale) by Outcome",
       x = "A15 (log scale)", y = "Count", fill = "Outcome") +
  theme_minimal()

write.csv(credit_clean, "credit_approval_clean.csv", row.names = FALSE)
