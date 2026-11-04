library(shiny)
library(plotly)
library(dplyr)

data_dir <- if (dir.exists("da3_dashboard/data")) "da3_dashboard/data" else if (dir.exists("data")) "data" else "."
rd <- function(f) read.csv(file.path(data_dir, f), stringsAsFactors = FALSE)

model_summary <- rd("da3_model_summary.csv")
group_metrics <- rd("da3_group_metrics.csv")
fair          <- rd("da3_fairness_summary.csv")
tests         <- rd("da3_model_tests.csv")
base_rates    <- rd("da3_base_rates.csv")

group_labels <- c(A1 = "A1 (2 groups)", A2_group = "A2 quartile (4 groups)")
model_names  <- model_summary$model[order(-model_summary$auc)]

fmt  <- function(x, d = 3) formatC(x, format = "f", digits = d)
pfmt <- function(p) ifelse(is.na(p), "NA", ifelse(p < 0.001, "< 0.001", fmt(p, 3)))

tile <- function(title, value, note = NULL) {
  div(class = "well", style = "text-align:center; padding:10px;",
      h5(title, style = "margin-top:0; color:#555;"),
      h3(value, style = "margin:4px 0; color:#1F4E78;"),
      if (!is.null(note)) p(note, style = "font-size:12px; color:#777; margin-bottom:0;"))
}

ui <- navbarPage(
  "Credit Approval: Model Performance & Fairness Audit",

  tabPanel("Overview",
    fluidRow(column(12,
      h4("What this dashboard shows"),
      p("Twelve classification models were trained on the UCI Credit Approval data (690 applicants) and",
        "tested on 137 applicants they had never seen. This dashboard compares their accuracy and checks",
        "whether each model treats applicant groups equally."),
      p(strong("Groups are anonymous."), "The dataset hides what each column means, so 'A1' and 'A2 quartile'",
        "are just two ways to split applicants into groups. They are not confirmed gender or age groups.")
    )),
    fluidRow(
      column(7, h4("AUC by model (95% bootstrap interval)"), plotlyOutput("auc_plot", height = "420px")),
      column(5, h4("Test-set metrics"), tableOutput("model_table"))
    )
  ),

  tabPanel("Fairness by model",
    sidebarLayout(
      sidebarPanel(width = 3,
        selectInput("model", "Model", choices = model_names, selected = model_names[1]),
        radioButtons("gvar", "Group column", choices = setNames(names(group_labels), group_labels)),
        helpText("A gap of 0 means the groups are treated equally. The 'chance' value is the gap you would",
                 "see from random variation alone with groups this small.")
      ),
      mainPanel(width = 9,
        uiOutput("tiles"),
        fluidRow(
          column(7, plotlyOutput("group_plot", height = "380px")),
          column(5, h5("Per-group numbers"), tableOutput("group_table"))
        )
      )
    )
  ),

  tabPanel("Accuracy vs fairness",
    sidebarLayout(
      sidebarPanel(width = 3,
        radioButtons("gvar2", "Group column", choices = setNames(names(group_labels), group_labels)),
        radioButtons("gap_type", "Fairness gap",
                     choices = c("Equal opportunity gap" = "eo", "Approval-rate gap" = "dp")),
        radioButtons("perf", "Performance measure", choices = c("Accuracy" = "accuracy", "AUC" = "auc")),
        helpText("Models toward the top-left are both accurate and fair. Horizontal bars show the 95%",
                 "bootstrap interval of the gap.")
      ),
      mainPanel(width = 9, plotlyOutput("trade_plot", height = "520px"))
    )
  ),

  tabPanel("Is the best model really better?",
    fluidRow(column(12,
      uiOutput("test_intro"),
      tableOutput("test_table"),
      helpText("DeLong test compares AUCs; the exact McNemar test compares which applicants each model gets",
               "right. p-values are Holm-adjusted for the number of comparisons. A large adjusted p-value means",
               "the data cannot separate the two models.")
    ))
  ),

  tabPanel("Base rates & limitations",
    fluidRow(
      column(5,
        h4("True approval rate by group (test set)"),
        tableOutput("base_table"),
        helpText("If the real approval rates already differ between groups, some gap in model decisions is",
                 "expected. Equal opportunity compares only applicants who truly were approved.")
      ),
      column(7,
        h4("Limitations"),
        tags$ul(
          tags$li("Column meanings are hidden, so the groups are anonymous, not confirmed demographic groups."),
          tags$li("The labels are the bank's past decisions, not verified defaults, so any historical bias is in the labels."),
          tags$li("The test set has 137 applicants. Group sizes are small, so gaps are noisy; use the intervals and chance values."),
          tags$li("Intervals for a gap are skewed because a gap cannot be negative; the chance comparison is the better evidence."),
          tags$li("XGBoost could not be trained, so 12 of 13 planned models are compared.")
        )
      )
    )
  )
)

server <- function(input, output, session) {

  output$auc_plot <- renderPlotly({
    d <- model_summary %>% mutate(model = factor(model, levels = rev(model[order(auc)])))
    plot_ly(d, x = ~auc, y = ~model, type = "scatter", mode = "markers",
            marker = list(color = "#1F4E78", size = 9),
            error_x = list(type = "data", symmetric = FALSE,
                           array = ~(auc_hi - auc), arrayminus = ~(auc - auc_lo), color = "#7a9cc0"),
            text = ~paste0(model, "<br>AUC ", fmt(auc), " (", fmt(auc_lo), " to ", fmt(auc_hi), ")"),
            hoverinfo = "text") %>%
      layout(xaxis = list(title = "Test AUC"), yaxis = list(title = ""),
             margin = list(l = 150))
  })

  output$model_table <- renderTable({
    model_summary %>% arrange(desc(auc)) %>%
      transmute(Model = model, Accuracy = fmt(accuracy), AUC = fmt(auc), `CV AUC` = fmt(cv_auc))
  }, striped = TRUE, spacing = "s")

  sel_fair <- reactive(fair %>% filter(model == input$model, group_var == input$gvar))
  sel_group <- reactive(group_metrics %>% filter(model == input$model, group_var == input$gvar))

  output$tiles <- renderUI({
    f <- sel_fair(); req(nrow(f) == 1)
    verdict <- function(p) if (!is.na(p) && p < 0.05) "larger than chance" else "within chance variation"
    fluidRow(
      column(3, tile("Approval-rate gap", fmt(f$dp_gap),
                     paste0("95% interval ", fmt(f$dp_lo), " to ", fmt(f$dp_hi)))),
      column(3, tile("Equal opportunity gap", fmt(f$eo_gap),
                     paste0("95% interval ", fmt(f$eo_lo), " to ", fmt(f$eo_hi)))),
      column(3, tile("Gap expected by chance", paste0(fmt(f$dp_chance, 2), " / ", fmt(f$eo_chance, 2)),
                     "approval-rate / equal opportunity")),
      column(3, tile("Verdict (unadjusted)", verdict(f$eo_p),
                     paste0("p = ", pfmt(f$dp_p), " (approval), ", pfmt(f$eo_p), " (equal opp.)")))
    )
  })

  output$group_plot <- renderPlotly({
    g <- sel_group(); req(nrow(g) > 0)
    d <- bind_rows(
      g %>% transmute(group, metric = "Approval rate (all applicants)", value = approval_rate),
      g %>% transmute(group, metric = "True positive rate (truly approved)", value = tpr))
    plot_ly(d, x = ~group, y = ~value, color = ~metric, type = "bar",
            colors = c("#1F4E78", "#e08a1e"),
            text = ~fmt(value, 2), textposition = "outside") %>%
      layout(barmode = "group", yaxis = list(title = "Rate", range = c(0, 1.1)),
             xaxis = list(title = group_labels[[input$gvar]]),
             legend = list(orientation = "h", y = -0.2))
  })

  output$group_table <- renderTable({
    sel_group() %>%
      transmute(Group = group, N = n, `Truly approved` = n_true_approved,
                `Approval rate` = fmt(approval_rate, 2), TPR = fmt(tpr, 2),
                FPR = fmt(fpr, 2), Accuracy = fmt(accuracy, 2))
  }, striped = TRUE, spacing = "s")

  output$trade_plot <- renderPlotly({
    f <- fair %>%
      filter(group_var == input$gvar2) %>%
      left_join(model_summary, by = "model")

    gap <- f[[paste0(input$gap_type, "_gap")]]
    lo   <- f[[paste0(input$gap_type, "_lo")]]
    hi   <- f[[paste0(input$gap_type, "_hi")]]
    perf <- f[[input$perf]]

    gap_label <- if (input$gap_type == "eo") {
      "Equal opportunity gap"
    } else {
      "Approval-rate gap"
    }

    perf_label <- if (input$perf == "accuracy") {
      "Test accuracy"
    } else {
      "Test AUC"
    }

    hover_info <- paste0(
      "<b>", f$model, "</b>",
      "<br>", gap_label, ": ", fmt(gap),
      "<br>", perf_label, ": ", fmt(perf),
      "<br>95% gap interval: ", fmt(lo), " to ", fmt(hi)
    )

    plot_ly(
      x = gap,
      y = perf,
      type = "scatter",
      mode = "markers",
      marker = list(
        color = "#1F4E78",
        size = 11,
        opacity = 0.85
      ),
      error_x = list(
        type = "data",
        symmetric = FALSE,
        array = hi - gap,
        arrayminus = gap - lo,
        color = "#b7c7da"
      ),
      hovertext = hover_info,
      hoverinfo = "text"
    ) %>%
      layout(
        xaxis = list(
          title = paste0(gap_label, " (lower is more equal)")
        ),
        yaxis = list(title = perf_label),
        showlegend = FALSE,
        margin = list(l = 75, r = 30, b = 80, t = 30)
      )
  })

  output$test_intro <- renderUI({
    p(strong("Reference model: ", tests$ref_model[1]), " (highest test AUC), compared with every other model on the same 137 test applicants.")
  })

  output$test_table <- renderTable({
    tests %>% arrange(delong_p) %>%
      transmute(Model = model, AUC = fmt(auc), `AUC difference` = fmt(auc_diff),
                `DeLong p (adj.)` = pfmt(delong_p_adj),
                `Reference right, model wrong` = ref_only_correct,
                `Model right, reference wrong` = model_only_correct,
                `McNemar p (adj.)` = pfmt(mcnemar_p_adj))
  }, striped = TRUE, spacing = "s")

  output$base_table <- renderTable({
    base_rates %>% transmute(`Group column` = group_var, Group = group, N = n,
                             `True approval rate` = fmt(true_approval_rate, 2))
  }, striped = TRUE, spacing = "s")
}

shinyApp(ui, server)
