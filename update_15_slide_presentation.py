import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def update_presentation():
    pptx_path = "Credit_Approval_Presentation.pptx"
    prs = Presentation(pptx_path)
    print(f"Loaded {pptx_path} with {len(prs.slides)} slides.")

    # Colors
    NAVY = RGBColor(31, 78, 120)       # #1F4E78
    DARK_BLUE = RGBColor(20, 53, 82)   # #143552
    BLUE_ACCENT = RGBColor(37, 99, 235)# #2563EB
    DARK_TEXT = RGBColor(30, 41, 59)   # #1E293B
    MUTED_TEXT = RGBColor(100, 116, 139)# #64748B
    CARD_BG = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(226, 232, 240) # #E2E8F0

    # -------------------------------------------------------------
    # 1. UPDATE SLIDE 6 (04 — EXPLORATORY DATA ANALYSIS)
    # -------------------------------------------------------------
    slide6 = prs.slides[5]

    # Adjust title and subtitle position slightly to give more room for 6 graphs
    # Shape 0: Category tag
    # Shape 1: Title
    # Shape 2: Subtitle
    slide6.shapes[0].top = Inches(0.40)
    slide6.shapes[1].top = Inches(0.68)
    slide6.shapes[1].height = Inches(0.45)
    slide6.shapes[2].top = Inches(1.15)
    slide6.shapes[2].height = Inches(0.35)

    # Remove old images, captions, and callout boxes (shapes 6 to end)
    to_remove = [slide6.shapes[i]._element for i in range(len(slide6.shapes) - 1, 5, -1)]
    for el in to_remove:
        el.getparent().remove(el)

    print("Removed old shapes from Slide 6. Adding 6 EDA visualization cards...")

    # Data for the 6 EDA graphs
    eda_graphs = [
        {
            "img": "eda_01_target_distribution.png",
            "title": "1. Target Balance (A16)",
            "desc": "307 Approved (44.5%) vs 383 Rejected (55.5%). Target is well-balanced; no synthetic oversampling (SMOTE) needed."
        },
        {
            "img": "eda_02_continuous_boxplots.png",
            "title": "2. Continuous Attributes by Outcome",
            "desc": "Strong right-skewness and outliers in A3, A8, and A15. Credit history length (A8) separates outcomes most visibly."
        },
        {
            "img": "eda_03_correlation_heatmap.png",
            "title": "3. Correlation Heatmap",
            "desc": "Low pairwise collinearity across continuous features (all |r| < 0.40), confirming predictor independence for modeling."
        },
        {
            "img": "eda_04_approval_by_a9.png",
            "title": "4. Prior Default Proxy (A9)",
            "desc": "Dominant predictor: A9='t' approved 78.7% of the time, while A9='f' approved only 7.0% (over 90% rejection rate)."
        },
        {
            "img": "eda_05_missing_values.png",
            "title": "5. Missing Value Pattern",
            "desc": "67 missing cells across 7 columns (max 1.9% per column, 5% of rows overall). Imputed via median (num) and mode (cat)."
        },
        {
            "img": "eda_06_income_distribution.png",
            "title": "6. Income Proxy (A15, Log Scale)",
            "desc": "Severe right skew (0 to 100k). Log1p scaling reveals stark separation: higher earners approved at much higher rates."
        }
    ]

    # Grid Geometry for 6 cards (3 columns x 2 rows)
    # Available area: left 0.65" to 12.68" (width 12.03"), top 1.60" to 6.85" (height 5.25")
    col_w = Inches(3.82)
    gap_x = Inches(0.28)
    row_h = Inches(2.48)
    gap_y = Inches(0.22)
    start_x = Inches(0.65)
    start_y = Inches(1.62)

    for i, g in enumerate(eda_graphs):
        col_idx = i % 3
        row_idx = i // 3
        card_x = start_x + col_idx * (col_w + gap_x)
        card_y = start_y + row_idx * (row_h + gap_y)

        # Background card shape
        card = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_x, card_y, col_w, row_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        # Image inside card
        img_path = g["img"]
        if os.path.exists(img_path):
            img_x = card_x + Inches(0.08)
            img_y = card_y + Inches(0.08)
            img_w = col_w - Inches(0.16)
            img_h = Inches(1.58)
            slide6.shapes.add_picture(img_path, img_x, img_y, img_w, img_h)

        # Text block (Title + Description)
        tb_x = card_x + Inches(0.10)
        tb_y = card_y + Inches(1.68)
        tb_w = col_w - Inches(0.20)
        tb_h = Inches(0.72)
        tb = slide6.shapes.add_textbox(tb_x, tb_y, tb_w, tb_h)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Title paragraph
        p0 = tf.paragraphs[0]
        p0.text = g["title"]
        p0.font.bold = True
        p0.font.size = Pt(9.5)
        p0.font.color.rgb = NAVY
        p0.space_after = Pt(2)

        # Description paragraph
        p1 = tf.add_paragraph()
        p1.text = g["desc"]
        p1.font.size = Pt(8.0)
        p1.font.color.rgb = DARK_TEXT

    # -------------------------------------------------------------
    # 2. INJECT COMPREHENSIVE 3-SPEAKER SCRIPT INTO SLIDE NOTES
    # -------------------------------------------------------------
    scripts = {
        0: (
            "[SPEAKER 1: INTRODUCTION & PROJECT SETUP]\n\n"
            "\"Hello everyone, and welcome. Today, our team is presenting our comprehensive data science project: "
            "'Credit Approval Prediction & Algorithmic Fairness Audit.'\n\n"
            "Automated credit underwriting is increasingly deployed by banks to make rapid, objective lending decisions. "
            "However, when credit risk models are trained on historical data, they risk inheriting and reinforcing historical "
            "disparities against vulnerable demographic cohorts. Our goal in this project was to construct an end-to-end data pipeline "
            "using the benchmark Quinlan Credit Approval dataset from the UCI repository—spanning data cleaning, relational SQLite database "
            "engineering, a 12-model machine learning benchmark, and a statistical fairness audit.\n\n"
            "Our presentation is divided equally among three speakers: I am Speaker 1, covering the problem motivation, data profile, and pipeline architecture. "
            "Speaker 2 will walk you through our exploratory findings, relational database, feature selection, and machine learning benchmark. "
            "Finally, Speaker 3 will guide you through our multi-metric fairness audit, statistical hypothesis testing, mitigation experiments, and our interactive Shiny dashboard. "
            "Let us begin with our agenda.\""
        ),
        1: (
            "[SPEAKER 1: AGENDA & PRESENTATION ROADMAP]\n\n"
            "\"On Slide 2, you see our 8-part roadmap, mirroring the logical structure of our course assignments.\n\n"
            "We begin with Part 1: framing the underwriting dilemma and understanding the dataset's structure. "
            "Next, we move to engineering: exploring risk signals through 6 exploratory visualizations, establishing an ACID-compliant SQLite relational store, "
            "engineering domain features, and training 12 distinct machine learning classifiers on identical repeated cross-validation folds.\n\n"
            "In the second half, we transition to governance: auditing models on Demographic Parity, Equal Opportunity, and Equalized Odds, "
            "testing whether the top model is statistically superior, experimenting with 'fairness through unawareness,' and demonstrating our interactive Shiny dashboard. "
            "Let's move to Slide 3 to look at the central research question.\""
        ),
        2: (
            "[SPEAKER 1: THE RESEARCH QUESTION & ACCURACY-FAIRNESS DILEMMA]\n\n"
            "\"Slide 3 establishes our core question: Can an automated system predict credit card approval with high accuracy while treating applicant groups fairly?\n\n"
            "In traditional financial machine learning, predictive accuracy and algorithmic equity are frequently framed as a zero-sum trade-off—the assumption being "
            "that making a model fairer must inevitably hurt its profitability or accuracy. We set out to rigorously test whether this conflict is real.\n\n"
            "Our methodology benchmarks 12 algorithms under identical cross-validation folds, picks the best model based on held-out test AUC, and audits every classifier "
            "across three complementary mathematical fairness definitions. Crucially, as highlighted in the key insight box, accuracy and fairness do not conflict here! "
            "Our top models are also among the fairest by Equal Opportunity, and the largest disparities we observe stem from underlying base-rate differences in the data itself.\""
        ),
        3: (
            "[SPEAKER 1: DATASET PROFILE & ANONYMIZATION]\n\n"
            "\"Moving to Slide 4, we examine our dataset: the UCI Credit Approval benchmark, comprising 690 applications across 15 predictor attributes and a binary decision target.\n\n"
            "To safeguard confidential banking operations, the original attribute names and values were masked. Drawing upon credit scoring literature, we mapped continuous attributes "
            "A2, A3, A8, A11, A14, and A15 to financial proxies including applicant age, debt liabilities, credit history length, credit limits, and income. "
            "Notice that the target distribution is well-balanced: 307 approvals (44.5%) versus 383 rejections (55.5%), ensuring models don't suffer from majority-class collapse.\n\n"
            "Crucially, because attributes are masked, we audit two anonymous demographic proxies: A1, with two levels widely read as gender in academic literature, "
            "and A2 quartile, representing four equal-frequency age cohorts. Missing values were concentrated in 67 cells across 7 columns (under 1.9% per column), "
            "which we handle cleanly through median and mode imputation.\""
        ),
        4: (
            "[SPEAKER 1: PIPELINE ARCHITECTURE & LEAKAGE CONTROL]\n\n"
            "\"Slide 5 displays our modular, eight-stage pipeline architecture. Every stage is implemented as a standalone, re-runnable R script producing intermediate artifacts on disk.\n\n"
            "We begin with Step 1 preprocessing in da1_preprocessing.R, Step 2 EDA in da1_eda.R, and Step 3 database ingestion in da2_01_database.R. "
            "Steps 4 and 5 handle feature engineering and model training, while Steps 6 and 7 perform our statistical fairness audit and mitigation experiments, culminating in Step 8's interactive Shiny dashboard.\n\n"
            "A paramount engineering consideration throughout is strict leakage prevention: all imputation statistics (medians for continuous columns and modes for categorical columns) "
            "as well as age-quartile cut points were calculated strictly on the training partition before being mapped to test data. Random seeds were locked at 42, 123, and 2026 across all scripts.\n\n"
            "I now hand the presentation over to Speaker 2 to explore our EDA visualizations, database architecture, and machine learning models.\""
        ),
        5: (
            "[SPEAKER 2: EXPLORATORY DATA ANALYSIS (ALL 6 GRAPHS)]\n\n"
            "\"Thank you, Speaker 1. Moving to Slide 6, we present our complete exploratory data analysis, featuring all six visualizations that reveal the underlying mechanics of the credit dataset.\n\n"
            "Starting with Graph 1 in the top-left: Class Balance confirms that 44.5% of applicants are approved and 55.5% rejected, establishing an un-skewed benchmark with a naive majority baseline of 55.5%.\n\n"
            "Graph 2 shows Continuous Attributes by Outcome: continuous attributes exhibit significant positive skew and heavy outliers, particularly in debt (A3), credit history (A8), and income (A15). Notice that attribute A8 provides the clearest visual separation between approved and rejected applicants.\n\n"
            "Graph 3 displays our Pearson Correlation Heatmap: pairwise correlations between continuous variables are modest—all absolute values fall below 0.40—confirming that our continuous attributes provide distinct, non-redundant predictive signals.\n\n"
            "Graph 4 highlights our single most decisive discovery: Prior Default Proxy A9. Applicants with a clean credit history (A9 = 't') achieve an approval rate of 78.7%, whereas applicants with prior defaults (A9 = 'f') face an overwhelming 93.0% rejection rate (only 7.0% approved). Attribute A9 alone accounts for over 60% of total model predictive variance!\n\n"
            "Graph 5 visualizes Missing Value Patterns: missingness affects only 5% of rows and at most 1.9% of any individual column, confirming that simple median and mode imputation does not distort the data distribution.\n\n"
            "Finally, Graph 6 shows Income (A15) on a log scale: raw income spans from zero to 100,000. Applying a log1p transformation stabilizes the heavy tail and exposes clear outcome separation, where high-earning applicants are approved at substantially higher rates.\""
        ),
        6: (
            "[SPEAKER 2: DATABASE ENGINEERING IN SQLITE]\n\n"
            "\"In Assignment 2, we moved away from flat CSV files to an enterprise-style relational architecture in SQLite, stored in 'credit.db'.\n\n"
            "As shown on Slide 7, we normalized the dataset into two related tables: 'applicants', holding the primary key ID and attributes A1 through A15, "
            "and 'decisions', holding the ID as a foreign key linked to the approval outcome. This separation enforces referential integrity, eliminates update anomalies, "
            "and simulates real-world banking infrastructure where customer attributes and credit committee decisions are stored in distinct corporate systems.\n\n"
            "Using R's DBI interface, our code abstracts database connectivity via get_con(), enabling an instant switch between local SQLite and production PostgreSQL. "
            "We executed automated validation queries—confirming exactly 690 matching records across both tables—and utilized sqlInterpolate() for injection-safe, parameterized analytical queries.\""
        ),
        7: (
            "[SPEAKER 2: FEATURE ENGINEERING & SELECTION]\n\n"
            "\"Slide 8 demonstrates our feature engineering and selection workflow. Raw variables rarely tell the whole financial story, so we synthesized five domain feature families:\n\n"
            "First, log1p transforms for right-skewed columns A3, A8, A11, A14, and A15; second, binary zero-indicator flags A11_pos and A15_pos to isolate non-zero inquiries and income; "
            "third, an interaction ratio A8_per_A2 measuring credit history length relative to applicant age; fourth, a compound indicator A9_and_A10 representing applicants who possess both a clean credit record and steady employment; "
            "and fifth, age-quartile groups Q1 through Q4 reserved exclusively for fairness auditing.\n\n"
            "We then applied a three-step selection filter: nearZeroVar removed no features; collinearity screening pruned no features over 0.90 correlation; and a 500-tree Random Forest permutation test ranked importance. "
            "As seen on the plot, prior default A9 (importance 0.122) and the A9_and_A10 interaction (0.078) lead the hierarchy. Attribute A12 had negative importance and was eliminated, while demographic attribute A1 ranked 20th with near-zero importance.\""
        ),
        8: (
            "[SPEAKER 2: 12-MODEL BENCHMARK & LEADERBOARD]\n\n"
            "\"Slide 9 presents our machine learning benchmark. We trained 12 classification algorithms: Logistic Regression, Elastic Net, LDA, KNN, Naive Bayes, Decision Trees, Bagged Trees, "
            "Random Forest, Gradient Boosting, SVM Linear, SVM Radial, and a Multi-Layer Perceptron Neural Network.\n\n"
            "Crucially, every single algorithm was trained under identical 5-fold cross-validation repeated twice, evaluated using the ROC AUC metric. Centering, scaling, and zero-variance filters were applied strictly inside each fold.\n\n"
            "Looking at the performance chart and table: Random Forest achieved the top test AUC of 0.918 with 83.9% accuracy, while Bagged Trees delivered the highest raw accuracy at 86.1% (AUC 0.914). "
            "However, notice how tightly the top eight models cluster: Elastic Net, LDA, Bagged Trees, Logistic Regression, GBM, and Neural Nets all achieve test AUCs between 0.911 and 0.914. "
            "Only KNN (AUC 0.826) and Naive Bayes (AUC 0.840) lag substantially.\n\n"
            "I now pass the presentation to Speaker 3 to examine whether our top-performing models are fair across applicant subgroups.\""
        ),
        9: (
            "[SPEAKER 3: ALGORITHMIC FAIRNESS AUDIT FRAMEWORK]\n\n"
            "\"Thank you, Speaker 2. Moving to Slide 10, we begin our algorithmic fairness audit.\n\n"
            "In financial lending regulation, fairness cannot be captured by any single metric. We evaluated three foundational mathematical criteria across two subgroup variables: attribute A1 (2 groups) and age quartiles (4 groups).\n\n"
            "First, Demographic Parity evaluates the difference in raw approval rates between groups, testing whether approval is independent of demographic membership. "
            "Second, Equal Opportunity evaluates the True Positive Rate gap specifically among applicants who were truly qualified for credit. "
            "Third, Equalized Odds bounds both the True Positive Rate gap and the False Positive Rate gap simultaneously.\n\n"
            "Furthermore, because our held-out test set contains 138 applicants, raw gap metrics are subject to sampling noise. To establish rigorous uncertainty bounds, "
            "we computed non-parametric 95% confidence intervals using 1,000 bootstrap resamples. As seen in the figure on the right, the bootstrap intervals for all leading models overlap heavily, "
            "proving that small numerical differences in fairness gaps between algorithms are largely noise.\""
        ),
        10: (
            "[SPEAKER 3: FAIRNESS PROFILES & PERMUTATION TESTING]\n\n"
            "\"Slide 11 delves deeper into the statistical significance of these fairness disparities.\n\n"
            "To test whether observed gaps are genuine bias or merely random sampling variance, we ran 2,000 permutation label shuffles to calculate empirical null distributions—measuring the gap size expected purely by chance. "
            "When we apply the standard Holm-Bonferroni correction for multiple hypothesis testing, every single equal-opportunity gap across all 12 models yields an adjusted p-value of 1.0! "
            "In other words, none of the models exhibit statistically significant discrimination on attribute A1.\n\n"
            "Equally important is our discovery regarding age quartiles: while models display apparent approval gaps of 26% to 37% between age bands, this is directly explained by ground-truth base rates in the data! "
            "In the real test data, older applicants in quartile Q4 approve at 63.3%, whereas younger applicants in quartile Q1 approve at only 34.3%. A model striving for predictive accuracy will naturally reflect this true economic difference.\""
        ),
        11: (
            "[SPEAKER 3: ACCURACY VERSUS FAIRNESS TRADE-OFF]\n\n"
            "\"Slide 12 brings accuracy and fairness together onto a single 2D trade-off frontier. The horizontal axis represents the Equal Opportunity gap—where points further left indicate greater equity—and the vertical axis represents test accuracy.\n\n"
            "The top-left quadrant is the ideal operating zone for any financial institution: combining high predictive accuracy with minimal demographic disparity. "
            "Notice where our models land: Bagged Trees, Random Forest, Logistic Regression, and Elastic Net all populate the upper-left territory. "
            "Specifically, regularized linear models like Elastic Net achieve 82.5% accuracy with an equal-opportunity gap of only 0.037. "
            "Conversely, Naive Bayes and KNN languish in the lower-right quadrant with low accuracy and high disparity.\n\n"
            "This empirical evidence disproves the common belief that high predictive accuracy forces a bank to compromise on fairness.\""
        ),
        12: (
            "[SPEAKER 3: STATISTICAL DOMINANCE (DELONG & MCNEMAR TESTS)]\n\n"
            "\"On Slide 13, we confront a vital question for credit risk teams: Is our top-ranked Random Forest model statistically superior to simpler alternatives, or is its lead just sampling chance?\n\n"
            "To answer this, we conducted paired DeLong tests on ROC AUC and exact McNemar tests on classification discordance across the exact same 138 test applicants. "
            "The verdict is striking: only KNN (p = 0.005) and Naive Bayes (p = 0.043) are statistically significantly inferior to Random Forest. "
            "Every other model—including Elastic Net (p = 0.71), LDA (p = 0.73), Bagged Trees (p = 0.68), Logistic Regression (p = 0.73), and Neural Networks (p = 0.64)—is statistically indistinguishable from Random Forest!\n\n"
            "This has profound regulatory implications: under Equal Credit Opportunity Act (ECOA) and FCRA Adverse Action rules, banks must provide specific, explainable reasons for credit denial. "
            "Because Elastic Net is statistically tied with Random Forest, institutions can deploy fully explainable regularized linear models without forfeiting any predictive performance!\""
        ),
        13: (
            "[SPEAKER 3: MITIGATION VIA UNAWARENESS EXPERIMENT]\n\n"
            "\"Slide 14 evaluates a widespread compliance heuristic known as 'fairness through unawareness'—the practice of simply dropping protected attributes like A1 from model training.\n\n"
            "We retrained Logistic Regression, Elastic Net, and Random Forest on identical cross-validation folds with attribute A1 completely excluded. The results demonstrate the fallacy of unawareness: "
            "For Elastic Net, exactly zero out of 138 test predictions changed (0.0% flip rate). For Logistic Regression, only a single applicant's decision flipped (0.7%). For Random Forest, only two decisions flipped (1.5%). "
            "Accuracy remained unchanged, and equal-opportunity gaps barely shifted.\n\n"
            "Why does hiding A1 fail to move the needle? Because remaining financial variables—such as credit history A8, prior default A9, employment A10, and income A15—already correlate with and proxy demographic characteristics. "
            "Blinding an algorithm to protected attributes provides false legal comfort while allowing historical proxy disparities to persist unmonitored.\""
        ),
        14: (
            "[SPEAKER 3: SHINY DECISION COCKPIT & STRATEGIC RECOMMENDATIONS]\n\n"
            "\"Finally, on Slide 15, we showcase our delivery artifact: an interactive decision cockpit built in R Shiny and Plotly, launched via app.R.\n\n"
            "The dashboard provides five dedicated tabs for risk officers and compliance auditors: Tab 1 presents an overview forest plot with bootstrap error bars; "
            "Tab 2 provides per-group approval rate bars and disparity tiles against empirical chance; Tab 3 features a dynamic 2D trade-off explorer; "
            "Tab 4 computes real-time DeLong and McNemar hypothesis testing tables; and Tab 5 details ground-truth base rates and methodological caveats.\n\n"
            "To summarize our project, we offer four strategic recommendations for credit risk automation:\n"
            "1. Deploy Explainable Models: Since Elastic Net matches Random Forest statistically, use regularized linear models for transparent Adverse Action notices.\n"
            "2. Prioritize Equal Opportunity over Demographic Parity to respect legitimate credit differences while protecting qualified applicants.\n"
            "3. Reject Demographic Unawareness as a sufficient compliance defense; actively monitor outcome disparities across proxy features.\n"
            "4. Embed Continuous Auditing Cockpits into MLOps pipelines to monitor drift and fairness dynamically in production.\n\n"
            "Thank you very much for your attention. We are now delighted to open the floor to your questions.\""
        )
    }

    print("Injecting comprehensive 3-speaker video presentation scripts into slide notes...")
    for idx, script_text in scripts.items():
        slide = prs.slides[idx]
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = script_text

    # Save presentation
    prs.save(pptx_path)
    print(f"Successfully saved updated presentation to {pptx_path}!")

if __name__ == "__main__":
    update_presentation()
