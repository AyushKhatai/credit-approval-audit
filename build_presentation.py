import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    NAVY = RGBColor(15, 23, 42)
    BLUE_DARK = RGBColor(30, 58, 138)
    BLUE_BRIGHT = RGBColor(37, 99, 235)
    TEAL = RGBColor(13, 148, 136)
    GRAY_TEXT = RGBColor(71, 85, 105)
    DARK_TEXT = RGBColor(30, 41, 59)
    WHITE = RGBColor(255, 255, 255)
    CARD_BG = RGBColor(241, 245, 249)
    LIGHT_BORDER = RGBColor(226, 232, 240)
    ACCENT_AMBER = RGBColor(217, 119, 6)

    def add_header(slide, tag, title, subtitle):
        # Tag
        tb_tag = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_tag = tb_tag.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = BLUE_BRIGHT

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

        # Subtitle
        if subtitle:
            tb_sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.35))
            tf_sub = tb_sub.text_frame
            tf_sub.word_wrap = True
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = GRAY_TEXT

    def add_card(slide, left, top, width, height, fill_color=WHITE, border_color=LIGHT_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        return shape

    # ==========================================================
    # SLIDE 1: Title Slide (Dark Theme)
    # ==========================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    # Title Card
    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "VIT UNIVERSITY • BMAT202P PROBABILITY AND STATISTICS PROJECT"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(96, 165, 250)
    p0.space_after = Pt(20)

    p1 = tf.add_paragraph()
    p1.text = "Predicting Credit Card Approval &\nAuditing Algorithmic Fairness"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(16)

    p2 = tf.add_paragraph()
    p2.text = "An End-to-End Framework: Database Engineering, 12 Supervised ML Classifiers, Non-Parametric Bootstrap/Permutation Fairness Auditing, and Interactive Shiny Decision Cockpit"
    p2.font.size = Pt(14)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(36)

    p3 = tf.add_paragraph()
    p3.text = "Author: Ayush Khatai (Reg No: 24BDS1106)  •  Faculty Guide: Prof. Jaganathan B\nB.Tech Computer Science and Engineering  •  UCI Credit Approval Benchmark Dataset"
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # 4 Quick Badges at bottom
    badges = [
        ("690 Applicants", "UCI Benchmark"),
        ("12 ML Models", "5-Fold 2-Rep CV"),
        ("0.918 Top AUC", "Random Forest"),
        ("Fairness Audit", "Bootstrap & Permutation")
    ]
    for i, (b_title, b_sub) in enumerate(badges):
        b_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0 + i*2.9), Inches(5.8), Inches(2.7), Inches(0.9))
        b_box.fill.solid()
        b_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
        b_box.line.color.rgb = RGBColor(51, 65, 85)
        btf = b_box.text_frame
        btf.word_wrap = True
        bp0 = btf.paragraphs[0]
        bp0.text = b_title
        bp0.font.size = Pt(13)
        bp0.font.bold = True
        bp0.font.color.rgb = RGBColor(147, 197, 253)
        bp1 = btf.add_paragraph()
        bp1.text = b_sub
        bp1.font.size = Pt(10)
        bp1.font.color.rgb = RGBColor(148, 163, 184)

    # ==========================================================
    # SLIDE 2: Executive Summary & Project Architecture
    # ==========================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "EXECUTIVE SUMMARY", "Project Objectives & Three-Stage Architecture", 
               "Systematic progression from raw data preprocessing to robust algorithmic auditing")

    # Left Column: Highlights
    left_card = add_card(s2, Inches(0.8), Inches(1.8), Inches(5.8), Inches(4.2))
    ltf = left_card.text_frame
    ltf.word_wrap = True
    lp = ltf.paragraphs[0]
    lp.text = "Core Problem Statement"
    lp.font.size = Pt(16)
    lp.font.bold = True
    lp.font.color.rgb = NAVY
    lp.space_after = Pt(10)

    bullets = [
        ("Financial Underwriting Automation: ", "Institutions deploy ML to accelerate credit approval, but models risk codifying and exacerbating historical demographic disparities."),
        ("Assignment 1 (DA1): ", "Exploratory analysis, class balance verification, missingness treatment via median/mode imputation on 690 UCI credit applications."),
        ("Assignment 2 (DA2): ", "ACID-compliant SQLite database engineering, feature engineering (log transforms, interaction ratios), and 12-model repeated CV benchmark."),
        ("Assignment 3 (DA3): ", "Algorithmic fairness audit (Demographic Parity, Equal Opportunity, Equalized Odds), uncertainty estimation, DeLong paired significance tests, and Shiny dashboard.")
    ]
    for b_title, b_desc in bullets:
        bp = ltf.add_paragraph()
        bp.space_after = Pt(8)
        run1 = bp.add_run()
        run1.text = b_title
        run1.font.bold = True
        run1.font.size = Pt(11)
        run1.font.color.rgb = BLUE_DARK
        run2 = bp.add_run()
        run2.text = b_desc
        run2.font.size = Pt(11)
        run2.font.color.rgb = DARK_TEXT

    # Right Column: Visual of Hero / KPI Screenshot
    if os.path.exists("screenshot_hero_kpis.png"):
        s2.shapes.add_picture("screenshot_hero_kpis.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # Bottom Banner
    bb = add_card(s2, Inches(0.8), Inches(6.2), Inches(11.7), Inches(0.8), fill_color=RGBColor(239, 246, 255), border_color=BLUE_BRIGHT)
    btf = bb.text_frame
    bp = btf.paragraphs[0]
    bp.text = "Key Project Takeaway: Random Forest leads performance (AUC 0.918), but top 8 models are statistically indistinguishable (DeLong p > 0.34). All observed subgroup fairness gaps are within chance variation (Holm p = 1.0)."
    bp.font.size = Pt(11)
    bp.font.bold = True
    bp.font.color.rgb = BLUE_DARK

    # ==========================================================
    # SLIDE 3: DA1 Dataset & Banking Proxies
    # ==========================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "ASSIGNMENT 1 (DA1)", "Dataset Understanding & Banking Attribute Proxies",
               "UCI Credit Approval dataset structure, privacy anonymization, and financial proxies")

    # Left Column: Table of Proxies
    c3 = add_card(s3, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.0))
    c3tf = c3.text_frame
    c3tf.word_wrap = True
    p = c3tf.paragraphs[0]
    p.text = "Banking Proxy Interpretations"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    proxies = [
        ("A1 (Categorical)", "a, b", "Applicant demographic / gender proxy (Audited)"),
        ("A2 (Continuous)", "13.75 - 80.25", "Applicant age proxy (Q1-Q4 Quartiles Audited)"),
        ("A3 (Continuous)", "0.0 - 28.0", "Debt / outstanding liability amount proxy"),
        ("A8 (Continuous)", "0.0 - 28.5", "Length of credit history / employment years"),
        ("A9 (Binary)", "t, f", "Prior default indicator (Single strongest predictor)"),
        ("A10 (Binary)", "t, f", "Employment status proxy"),
        ("A14 (Continuous)", "0 - 2000", "Credit card limit proxy"),
        ("A15 (Continuous)", "0 - 100,000", "Applicant annual income proxy (Severe skew)"),
        ("A16 (Target)", "+ / -", "Approval outcome: 307 Approved (44.5%), 383 Rejected")
    ]
    for col, vals, desc in proxies:
        cp = c3tf.add_paragraph()
        cp.space_after = Pt(4)
        r1 = cp.add_run()
        r1.text = f"{col} [{vals}]: "
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = BLUE_DARK
        r2 = cp.add_run()
        r2.text = desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    # Right Column: Visual of Target Distribution
    if os.path.exists("eda_01_target_distribution.png"):
        s3.shapes.add_picture("eda_01_target_distribution.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 4: DA1 Exploratory Data Analysis & Signals
    # ==========================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "ASSIGNMENT 1 (DA1)", "Exploratory Data Analysis: Risk Signals & Imputation",
               "Discovering dominant predictive factors and treating data quality issues")

    # Left: Explanation + Approval by A9
    c4 = add_card(s4, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c4tf = c4.text_frame
    c4tf.word_wrap = True
    p = c4tf.paragraphs[0]
    p.text = "Key Exploratory Findings"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    eda_points = [
        ("Prior Default Dominance (A9): ", "Applicants with prior default (A9 = 'f') face a 93% rejection rate. A9 accounts for over 60% of predictive power across all subsequent models."),
        ("Income & History Heavy Tails: ", "Income (A15) spans from 0 to 100,000 with severe right-skewness. Required log1p() transformations to prevent distortion in linear and neural models."),
        ("Missing Value Imputation: ", "Continuous attributes A2 (age) and A14 (limit) imputed using median. Categoricals A1, A4, A5, A6, A7 imputed using mode. Imputation statistics strictly locked to train split in DA2."),
        ("Low Multicollinearity: ", "Correlation heatmap revealed no pairwise continuous correlations above 0.40, confirming feature independence.")
    ]
    for b_title, b_desc in eda_points:
        bp = c4tf.add_paragraph()
        bp.space_after = Pt(8)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = BLUE_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = DARK_TEXT

    # Right: Approval by A9 Chart
    if os.path.exists("eda_04_approval_by_a9.png"):
        s4.shapes.add_picture("eda_04_approval_by_a9.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 5: DA2 Relational Database Engineering
    # ==========================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "ASSIGNMENT 2 (DA2)", "Relational Database Engineering in SQLite",
               "ACID-compliant normalization, parameterized SQL retrieval, and data governance")

    # Left Column: Database Architecture & Queries
    c5 = add_card(s5, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c5tf = c5.text_frame
    c5tf.word_wrap = True
    p = c5tf.paragraphs[0]
    p.text = "Relational Schema & SQL Implementation"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    db_points = [
        ("Database Normalization: ", "Partitioned raw data into two relational tables: 'applicants' (id PK, a1-a15 attributes) and 'decisions' (id PK/FK, outcome Approved/Rejected)."),
        ("Interoperable SQL: ", "Engineered portable SQL compatible with both local SQLite ('credit.db') and enterprise PostgreSQL via R DBI and dbConnect abstraction."),
        ("Integrity & Ingestion: ", "Foreign key constraints enforce referential integrity between applicant attributes and decision outcomes across all 690 records."),
        ("Parameterized Retrieval: ", "Employed sqlInterpolate() to execute secure, injection-safe SQL queries for subgroup approval auditing and model training extraction.")
    ]
    for b_title, b_desc in db_points:
        bp = c5tf.add_paragraph()
        bp.space_after = Pt(8)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = BLUE_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = DARK_TEXT

    # Right Column: Screenshot of DA2 Features / DB Section
    if os.path.exists("screenshot_da2_features.png"):
        s5.shapes.add_picture("screenshot_da2_features.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 6: DA2 Feature Engineering & Selection
    # ==========================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "ASSIGNMENT 2 (DA2)", "Feature Engineering & Random Forest Selection",
               "Non-linear feature synthesis and permutation importance feature selection")

    # Left Column: Features Created
    c6 = add_card(s6, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c6tf = c6.text_frame
    c6tf.word_wrap = True
    p = c6tf.paragraphs[0]
    p.text = "Engineered Feature Pipeline"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    fe_points = [
        ("Stratified 80/20 Train/Test Split: ", "552 training samples, 138 test samples. Imputation statistics strictly computed on training set to prevent data snooping."),
        ("Log Transformations: ", "log1p(A3), log1p(A8), log1p(A11), log1p(A14), log1p(A15) to compress severe right-skewed tails."),
        ("Zero-Indicator Indicators: ", "A11_pos and A15_pos binary flags capturing applicants with zero credit inquiries or zero declared income."),
        ("Financial Interaction Ratios: ", "A8_per_A2: Length of credit history normalized by age; A9_and_A10: Joint indicator for clean credit bureau and steady employment."),
        ("Permutation Selection: ", "Random Forest (500 trees) ranked features. A9 (0.122) and A9_and_A10 (0.078) lead. A12 had negative importance and was dropped; A1 ranked 20th.")
    ]
    for b_title, b_desc in fe_points:
        bp = c6tf.add_paragraph()
        bp.space_after = Pt(6)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = BLUE_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    # Right: Feature Importance Plot
    if os.path.exists("da2_feature_importance.png"):
        s6.shapes.add_picture("da2_feature_importance.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 7: DA2 Model Benchmarking
    # ==========================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "ASSIGNMENT 2 (DA2)", "12-Model Supervised Learning Benchmark",
               "Evaluating 12 classification architectures on identical cross-validation folds")

    # Left Column: Table of Top Models
    c7 = add_card(s7, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c7tf = c7.text_frame
    c7tf.word_wrap = True
    p = c7tf.paragraphs[0]
    p.text = "Held-Out Test Set Performance (N = 138)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(6)

    model_rows = [
        ("Random Forest (Top AUC)", "0.839", "0.823", "0.918", "0.939"),
        ("Elastic Net Logistic", "0.825", "0.803", "0.914", "0.938"),
        ("Linear Discriminant Analysis", "0.832", "0.824", "0.914", "0.932"),
        ("Bagged Trees (Top Acc)", "0.861", "0.848", "0.914", "0.922"),
        ("Logistic Regression", "0.832", "0.824", "0.913", "0.912"),
        ("Gradient Boosting (GBM)", "0.825", "0.806", "0.912", "0.949"),
        ("Neural Network (MLP)", "0.839", "0.828", "0.911", "0.924"),
        ("Support Vector Machine (RBF)", "0.832", "0.813", "0.908", "0.929"),
        ("Decision Tree (CART)", "0.825", "0.812", "0.880", "0.907"),
        ("Naive Bayes", "0.781", "0.746", "0.840", "0.880"),
        ("K-Nearest Neighbors", "0.781", "0.737", "0.826", "0.903")
    ]
    for m_name, acc, f1, auc, cv_auc in model_rows:
        mp = c7tf.add_paragraph()
        mp.space_after = Pt(2)
        r1 = mp.add_run()
        r1.text = f"• {m_name}: "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = BLUE_DARK
        r2 = mp.add_run()
        r2.text = f"AUC = {auc} | Acc = {acc} | F1 = {f1} (CV AUC: {cv_auc})"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT

    # Right: Model Comparison Chart
    if os.path.exists("da2_model_comparison.png"):
        s7.shapes.add_picture("da2_model_comparison.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 8: DA3 Algorithmic Fairness Audit Framework
    # ==========================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "ASSIGNMENT 3 (DA3)", "Algorithmic Fairness Audit: Rigorous Framework",
               "Evaluating demographic equity and uncertainty with bootstrap and permutation tests")

    # Left Column: Metrics
    c8 = add_card(s8, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c8tf = c8.text_frame
    c8tf.word_wrap = True
    p = c8tf.paragraphs[0]
    p.text = "Mathematical Fairness Criteria"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    fair_defs = [
        ("Demographic Parity Gap (DP): ", "Max difference in approval rates across subgroups: |P(Y_hat = 1 | G = g1) - P(Y_hat = 1 | G = g2)|. Evaluates whether selection rates are independent of group status."),
        ("Equal Opportunity Gap (EO): ", "Max difference in True Positive Rates (TPR) among truly qualified applicants: |TPR_g1 - TPR_g2|. Protects qualified applicants equally."),
        ("Equalized Odds: ", "Combined condition requiring both equal TPR and equal False Positive Rate (FPR) across cohorts."),
        ("Disparate Impact Ratio: ", "Ratio of min(approval rate) / max(approval rate), testing adherence to the EEOC 80% four-fifths rule."),
        ("1,000 Bootstrap Resamples: ", "Constructs 95% percentile confidence intervals for all fairness gaps and AUC estimates."),
        ("2,000 Permutation Shuffles: ", "Shuffles subgroup labels 2,000 times to establish the empirical null distribution (chance gap expectation).")
    ]
    for b_title, b_desc in fair_defs:
        bp = c8tf.add_paragraph()
        bp.space_after = Pt(6)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = BLUE_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_TEXT

    # Right: Fairness Gaps Visual
    if os.path.exists("da3_fairness_gaps.png"):
        s8.shapes.add_picture("da3_fairness_gaps.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 9: DA3 Fairness Results & Trade-Offs
    # ==========================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "ASSIGNMENT 3 (DA3)", "Audit Findings: Accuracy vs. Fairness Trade-Off",
               "Evaluating observed disparities against small-sample chance thresholds")

    # Left: Findings
    c9 = add_card(s9, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c9tf = c9.text_frame
    c9tf.word_wrap = True
    p = c9tf.paragraphs[0]
    p.text = "Empirical Audit Takeaways"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    audit_pts = [
        ("No Statistically Significant Bias: ", "All Holm-adjusted permutation p-values across all 12 models equal 1.0. Observed gaps (e.g. DP ~0.08, EO ~0.04) are fully consistent with small-sample sampling variance."),
        ("Underlying Base Rate Disparity: ", "In the ground-truth test data, true approval rates already differ: A1:a (51.1%) vs A1:b (41.3%), and Age Q1 (34.3%) vs Q4 (63.3%). A model striving for accuracy will reflect this."),
        ("Equal Opportunity vs Parity: ", "Forcing demographic parity would require rejecting qualified older applicants or approving unqualified younger applicants, violating equal opportunity."),
        ("Optimal Operating Models: ", "Elastic Net and Logistic Regression achieve optimal trade-off: high accuracy (82.5-83.2%), high AUC (0.914), and minimal Equal Opportunity gaps (0.037-0.045).")
    ]
    for b_title, b_desc in audit_pts:
        bp = c9tf.add_paragraph()
        bp.space_after = Pt(8)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = BLUE_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = DARK_TEXT

    # Right: Tradeoff Plot
    if os.path.exists("da3_tradeoff.png"):
        s9.shapes.add_picture("da3_tradeoff.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 10: DA3 Statistical Dominance & Equivalence
    # ==========================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "ASSIGNMENT 3 (DA3)", "Statistical Significance Testing (DeLong & McNemar)",
               "Is the top Random Forest model statistically better than simpler, explainable baselines?")

    # Left: Explanation & Regulatory Implications
    c10 = add_card(s10, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c10tf = c10.text_frame
    c10tf.word_wrap = True
    p = c10tf.paragraphs[0]
    p.text = "Paired Hypothesis Testing Results"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    sig_pts = [
        ("Paired DeLong ROC Test: ", "Assesses whether the test-set AUC difference between Random Forest and competitor models is statistically distinct on the exact same 138 applicants."),
        ("Exact McNemar Test: ", "Evaluates whether models make discordant errors (applicant-level classification disagreement)."),
        ("Statistical Equivalence of Top 8 Models: ", "DeLong p-values between Random Forest and Elastic Net (p = 0.71), LDA (p = 0.73), Bagged Trees (p = 0.68), Logistic Regression (p = 0.73), GBM (p = 0.42), and Neural Net (p = 0.64) are all non-significant."),
        ("Clear Underperformers: ", "Only KNN (p_adj = 0.005) and Naive Bayes (p_adj = 0.043) are statistically significantly inferior to Random Forest."),
        ("Regulatory & Compliance Implication: ", "Financial institutions can legally and safely adopt Elastic Net or Logistic Regression for 100% explainable credit decisions without forfeiting predictive power.")
    ]
    for b_title, b_desc in sig_pts:
        bp = c10tf.add_paragraph()
        bp.space_after = Pt(6)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = BLUE_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    # Right: Screenshot of Fairness / Tests section
    if os.path.exists("screenshot_da3_fairness.png"):
        s10.shapes.add_picture("screenshot_da3_fairness.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 11: DA3 Mitigation via Unawareness Experiment
    # ==========================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "ASSIGNMENT 3 (DA3)", "Mitigation Experiment: Fairness Through Unawareness",
               "Does omitting protected attribute A1 eliminate disparities or conceal them?")

    # Left: Explanation
    c11 = add_card(s11, Inches(0.8), Inches(1.8), Inches(5.8), Inches(5.1))
    c11tf = c11.text_frame
    c11tf.word_wrap = True
    p = c11tf.paragraphs[0]
    p.text = "The Fallacy of Demographic Unawareness"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)

    unaware_pts = [
        ("Experimental Design: ", "Retrained Logistic Regression, Elastic Net, and Random Forest on identical folds with A1 completely excluded from the feature matrix."),
        ("Negligible Decision Impact: ", "For Elastic Net, 0 out of 138 test predictions changed (0.0% flip rate). For Logistic Regression, 1 decision flipped (0.7%). For Random Forest, 2 flipped (1.5%)."),
        ("Fairness Gaps Persist: ", "Equal Opportunity gap remained virtually invariant (0.037 for Elastic Net)."),
        ("Why Unawareness Fails: ", "Remaining financial variables (credit history A8, prior default A9, employment A10, income A15) already encode subgroup signals via proxy correlation."),
        ("Governance Lesson: ", "Simply blinding a model to protected attributes does not create equity; explicit post-processing or threshold calibration is required.")
    ]
    for b_title, b_desc in unaware_pts:
        bp = c11tf.add_paragraph()
        bp.space_after = Pt(6)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = BLUE_DARK
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    # Right: Unawareness Plot
    if os.path.exists("da3_unawareness.png"):
        s11.shapes.add_picture("da3_unawareness.png", Inches(6.9), Inches(1.8), Inches(5.6))

    # ==========================================================
    # SLIDE 12: Shiny Decision Cockpit & Final Recommendations
    # ==========================================================
    s12 = prs.slides.add_slide(blank_layout)
    bg12 = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = NAVY
    bg12.line.fill.background()

    # Title Card
    tb = s12.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "ASSIGNMENT 3 (DA3) • DECISION COCKPIT & GOVERNANCE"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(96, 165, 250)

    p1 = tf.add_paragraph()
    p1.text = "Interactive Shiny Dashboard & Strategic Recommendations"
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    # Left Card: Dashboard Features
    c12_l = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c12_l.fill.solid()
    c12_l.fill.fore_color.rgb = RGBColor(30, 41, 59)
    c12_l.line.color.rgb = RGBColor(51, 65, 85)
    c12_ltf = c12_l.text_frame
    c12_ltf.word_wrap = True
    lp = c12_ltf.paragraphs[0]
    lp.text = "Interactive Shiny Cockpit (app.R)"
    lp.font.size = Pt(16)
    lp.font.bold = True
    lp.font.color.rgb = RGBColor(147, 197, 253)
    lp.space_after = Pt(10)

    dash_pts = [
        ("1. Model Performance: ", "Plotly forest plot with asymmetric 95% bootstrap CI for test AUCs."),
        ("2. Subgroup Audit: ", "Dynamic rate comparisons, disparity tiles, and empirical chance thresholds."),
        ("3. Trade-Off Explorer: ", "Interactive 2D frontier mapping accuracy against fairness gaps."),
        ("4. Hypothesis Matrix: ", "Real-time DeLong & McNemar p-value tables with Holm corrections."),
        ("5. Baseline Context: ", "Ground-truth demographic breakdown and audit limitations.")
    ]
    for d_title, d_desc in dash_pts:
        dp = c12_ltf.add_paragraph()
        dp.space_after = Pt(8)
        r1 = dp.add_run()
        r1.text = d_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(147, 197, 253)
        r2 = dp.add_run()
        r2.text = d_desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = RGBColor(203, 213, 225)

    # Right Card: Institutional Recommendations
    c12_r = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    c12_r.fill.solid()
    c12_r.fill.fore_color.rgb = RGBColor(30, 41, 59)
    c12_r.line.color.rgb = RGBColor(51, 65, 85)
    c12_rtf = c12_r.text_frame
    c12_rtf.word_wrap = True
    rp = c12_rtf.paragraphs[0]
    rp.text = "Strategic Recommendations for Credit Risk"
    rp.font.size = Pt(16)
    rp.font.bold = True
    rp.font.color.rgb = RGBColor(52, 211, 153)
    rp.space_after = Pt(10)

    rec_pts = [
        ("Deploy Explainable Models: ", "Because Elastic Net is statistically tied with Random Forest (DeLong p = 0.71), adopt Elastic Net to ensure full compliance with Adverse Action notice laws (ECOA / FCRA)."),
        ("Target Equal Opportunity: ", "Prioritize Equal Opportunity (equal TPR) rather than Demographic Parity to respect legitimate financial differences while protecting qualified applicants."),
        ("Reject Unawareness Defense: ", "Do not rely on omitting protected attributes; continuously monitor proxy variables and audit residual subgroup selection rates."),
        ("Continuous Dynamic Auditing: ", "Deploy interactive auditing cockpits (such as app.R) into continuous production MLOps pipelines.")
    ]
    for r_title, r_desc in rec_pts:
        rp = c12_rtf.add_paragraph()
        rp.space_after = Pt(8)
        r1 = rp.add_run()
        r1.text = r_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(52, 211, 153)
        r2 = rp.add_run()
        r2.text = r_desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = RGBColor(203, 213, 225)

    # Save
    out_file = "Credit_Approval_Fairness_Presentation.pptx"
    prs.save(out_file)
    print(f"Presentation saved successfully to: {out_file}")

if __name__ == "__main__":
    create_deck()
