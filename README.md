# Credit Approval Prediction & Algorithmic Fairness Audit

An end-to-end machine learning, database engineering, and algorithmic fairness pipeline on the UCI Credit Approval dataset.

---

## Pipeline Execution Order

To run the entire pipeline from raw data to the interactive dashboard, execute the scripts in the following exact sequence:

### 1. Data Ingestion & Preprocessing (DA1)
- **Script**: `da1_preprocessing.R`
- **Input**: `crx.data` (raw UCI Credit Approval dataset)
- **Operation**: Converts attribute types, recodes target approvals, performs median imputation on continuous variables (`A2`, `A14`), and mode imputation on categorical features (`A1`, `A4`, `A5`, `A6`, `A7`).
- **Output**: `credit_approval_clean.csv`

### 2. Exploratory Data Analysis (DA1)
- **Script**: `da1_eda.R`
- **Input**: `crx.data`
- **Operation**: Visualizes class balance, attribute distributions across outcomes, correlation heatmaps, proxy default relationships, and missing value patterns.
- **Output**: EDA plots and clean dataset export.

### 3. Relational Database Setup & SQL Ingestion (DA2)
- **Script**: `da2_01_database.R` (depends on `da2_db_config.R`)
- **Input**: `crx.data`
- **Operation**: Connects to SQLite (`credit.db`) / PostgreSQL, defines relational schemas for `applicants` and `decisions` linked by applicant ID, loads records, and executes SQL validation queries.
- **Output**: `credit.db` (populated relational database)

### 4. Feature Engineering & Feature Selection (DA2)
- **Script**: `da2_02_features.R` (depends on `da2_db_config.R`)
- **Input**: `credit.db`
- **Operation**: Retrieves joined records via SQL, performs stratified 80/20 train/test split, fits imputation statistics strictly on the training partition, creates log-transforms and interaction features, generates age quartile groupings (`A2_group`), filters near-zero variance and collinear predictors, and selects top features using Random Forest permutation importance.
- **Output**: `da2_data.rds`, `da2_feature_importance.csv`, `da2_feature_importance.png`

### 5. Multi-Model Training & Evaluation Suite (DA2)
- **Script**: `da2_03_models.R` (depends on `da2_db_config.R`)
- **Input**: `da2_data.rds`
- **Operation**: Configures identical 5-fold 2-repeat cross-validation folds, trains 13 classification models (Logistic Regression, Elastic Net, LDA, KNN, Naive Bayes, Decision Tree, Bagged Trees, Random Forest, GBM, XGBoost, SVM Linear, SVM Radial, Neural Net MLP), calculates test set accuracy, precision, recall, F1, and AUC, and records predictions.
- **Output**: `da2_model_results.csv`, `da2_model_comparison.png`, `da2_test_predictions.csv`, and writes results to `credit.db`.

### 6. Algorithmic Fairness Audit & Statistical Significance Testing (DA3)
- **Script**: `da3_01_fairness.R` (depends on `da3_helpers.R`)
- **Input**: `da2_test_predictions.csv`, `da2_model_results.csv`
- **Operation**: Evaluates Demographic Parity, Equal Opportunity, and Equalized Odds across anonymous group attributes (`A1` and `A2_group`). Computes 95% bootstrap confidence intervals, permutation p-values, paired DeLong tests, and McNemar tests with Holm adjustments. Copies dashboard assets.
- **Output**: `da3_model_summary.csv`, `da3_group_metrics.csv`, `da3_fairness_summary.csv`, `da3_model_tests.csv`, `da3_base_rates.csv`, `da3_fairness_gaps.png`, `da3_tradeoff.png`, `da3_dashboard/data/`

### 7. Fairness Mitigation via Unawareness (DA3)
- **Script**: `da3_02_without_A1.R` (depends on `da3_helpers.R`)
- **Input**: `da2_data.rds`
- **Operation**: Retrains representative models with and without protected attribute `A1` on identical folds, tracking changes in fairness gaps, accuracy, and applicant decision flips.
- **Output**: `da3_unawareness.csv`, `da3_unawareness.png`

### 8. Interactive Shiny Dashboard (DA3)
- **Script**: `app.R` (or `da3_dashboard/app.R`)
- **Launch Command**:
  ```R
  shiny::runApp()
  ```
- **Features**: Interactive exploration of model AUCs, per-group fairness disparities, accuracy vs. fairness trade-off frontiers, and paired statistical test matrices.

---

## Repository Structure

```
├── crx.data                  # UCI raw dataset
├── crx.names                 # Dataset documentation
├── da1_preprocessing.R       # [Step 1] Data cleaning & imputation
├── da1_eda.R                 # [Step 2] Exploratory data analysis
├── da2_db_config.R           # [Step 3 Helper] Database connection config
├── da2_01_database.R         # [Step 3] Relational schema & SQL ingestion
├── da2_02_features.R         # [Step 4] Feature engineering & selection
├── da2_03_models.R           # [Step 5] 13-model training & evaluation
├── da3_helpers.R             # [Step 6 Helper] Fairness & bootstrap utilities
├── da3_01_fairness.R         # [Step 6] Fairness audit & statistical testing
├── da3_02_without_A1.R       # [Step 7] Mitigation via feature removal
├── app.R                     # [Step 8] Interactive Shiny dashboard
├── da3_dashboard/            # Dashboard package directory
│   ├── app.R
│   └── data/                 # Exported metrics and audit summaries
├── credit.db                 # SQLite database
├── credit_approval_clean.csv # Preprocessed dataset
├── da2_data.rds              # Processed train/test partitions
└── README.md                 # Pipeline and running order documentation
```
