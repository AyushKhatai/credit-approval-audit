library(tidyverse)

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

credit_clean$A4 <- ifelse(is.na(credit_clean$A4), mode_impute(credit_clean$A4), as.character(credit_clean$A4))
credit_clean$A5 <- ifelse(is.na(credit_clean$A5), mode_impute(credit_clean$A5), as.character(credit_clean$A5))
credit_clean$A6 <- ifelse(is.na(credit_clean$A6), mode_impute(credit_clean$A6), as.character(credit_clean$A6))
credit_clean$A4 <- as.factor(credit_clean$A4)
credit_clean$A5 <- as.factor(credit_clean$A5)
credit_clean$A6 <- as.factor(credit_clean$A6)

write.csv(credit_clean, "credit_approval_clean.csv", row.names = FALSE)
