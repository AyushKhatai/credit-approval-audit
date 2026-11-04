library(DBI)

USE_POSTGRES <- FALSE

get_con <- function() {
  if (USE_POSTGRES) {
    dbConnect(
      RPostgres::Postgres(),
      dbname   = "credit_db",
      host     = "localhost",
      port     = 5432,
      user     = "postgres",
      password = "YOUR_PASSWORD"
    )
  } else {
    dbConnect(RSQLite::SQLite(), "credit.db")
  }
}
