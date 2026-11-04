source("da2_db_config.R")

raw <- read.csv("crx.data", header = FALSE, na.strings = "?", col.names = paste0("a", 1:16), stringsAsFactors = FALSE)
raw$id <- seq_len(nrow(raw))

con <- get_con()

dbExecute(con, "DROP TABLE IF EXISTS decisions")
dbExecute(con, "DROP TABLE IF EXISTS applicants")

dbExecute(con, "
CREATE TABLE applicants (
  id  INTEGER PRIMARY KEY,
  a1  TEXT,
  a2  DOUBLE PRECISION,
  a3  DOUBLE PRECISION,
  a4  TEXT,
  a5  TEXT,
  a6  TEXT,
  a7  TEXT,
  a8  DOUBLE PRECISION,
  a9  TEXT,
  a10 TEXT,
  a11 INTEGER,
  a12 TEXT,
  a13 TEXT,
  a14 INTEGER,
  a15 INTEGER
)")

dbExecute(con, "
CREATE TABLE decisions (
  id      INTEGER PRIMARY KEY REFERENCES applicants(id),
  outcome TEXT
)")

applicants_df <- raw[, c("id", paste0("a", 1:15))]
decisions_df <- data.frame(
  id = raw$id,
  outcome = ifelse(raw$a16 == "+", "Approved", "Rejected")
)

dbWriteTable(con, "applicants", applicants_df, append = TRUE)
dbWriteTable(con, "decisions", decisions_df, append = TRUE)

dbListTables(con)
dbGetQuery(con, "SELECT COUNT(*) AS n_applicants FROM applicants")
dbGetQuery(con, "SELECT COUNT(*) AS n_decisions FROM decisions")

dbGetQuery(con, "
  SELECT a.id, a.a1, a.a2, a.a9, a.a10, a.a15, d.outcome
  FROM applicants a
  JOIN decisions d ON a.id = d.id
  ORDER BY a.id
  LIMIT 5")

dbGetQuery(con, "
  SELECT outcome, COUNT(*) AS n
  FROM decisions
  GROUP BY outcome")

dbGetQuery(con, "
  SELECT a.a9,
         COUNT(*) AS n,
         ROUND(100.0 * SUM(CASE WHEN d.outcome = 'Approved' THEN 1 ELSE 0 END) / COUNT(*), 1) AS approval_pct
  FROM applicants a
  JOIN decisions d ON a.id = d.id
  GROUP BY a.a9
  ORDER BY approval_pct DESC")

dbGetQuery(con, "
  SELECT a.a1,
         COUNT(*) AS n,
         ROUND(100.0 * SUM(CASE WHEN d.outcome = 'Approved' THEN 1 ELSE 0 END) / COUNT(*), 1) AS approval_pct
  FROM applicants a
  JOIN decisions d ON a.id = d.id
  WHERE a.a1 IS NOT NULL
  GROUP BY a.a1")

dbGetQuery(con, "
  SELECT d.outcome,
         ROUND(AVG(a.a2), 2)  AS avg_a2,
         ROUND(AVG(a.a15), 1) AS avg_a15
  FROM applicants a
  JOIN decisions d ON a.id = d.id
  GROUP BY d.outcome")

dbGetQuery(con, "
  SELECT SUM(CASE WHEN a1  IS NULL THEN 1 ELSE 0 END) AS a1_missing,
         SUM(CASE WHEN a2  IS NULL THEN 1 ELSE 0 END) AS a2_missing,
         SUM(CASE WHEN a4  IS NULL THEN 1 ELSE 0 END) AS a4_missing,
         SUM(CASE WHEN a5  IS NULL THEN 1 ELSE 0 END) AS a5_missing,
         SUM(CASE WHEN a6  IS NULL THEN 1 ELSE 0 END) AS a6_missing,
         SUM(CASE WHEN a7  IS NULL THEN 1 ELSE 0 END) AS a7_missing,
         SUM(CASE WHEN a14 IS NULL THEN 1 ELSE 0 END) AS a14_missing
  FROM applicants")

q7 <- sqlInterpolate(con, "
  SELECT a.id, a.a2, a.a15, d.outcome
  FROM applicants a
  JOIN decisions d ON a.id = d.id
  WHERE a.a15 > ?min_a15
  ORDER BY a.a15 DESC
  LIMIT 10", min_a15 = 1000)
dbGetQuery(con, q7)

dbDisconnect(con)
