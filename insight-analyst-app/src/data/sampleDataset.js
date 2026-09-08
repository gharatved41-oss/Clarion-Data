// High-fidelity synthetic dataset and telemetry metadata for Automated Insight Analyst

export const DATASET_METADATA = {
  filename: "q3_financials_2026.csv",
  size: "4.8 MB",
  rows: 14290,
  columns: 18,
  validity: "100% VALID",
  healthScore: 98.6,
  domain: "B2B SaaS Revenue & Subscription",
  confidence: 94.6,
  modelEngine: "SARIMAX Engine v4.18",
  lastProcessed: "2026-09-07 13:42:19 UTC",
  checksum: "sha256:7f8a92bc4e019a"
};

export const SCHEMA_COLUMNS = [
  { id: "row_id", name: "row_id", type: "Int64", nulls: 0, distinct: 14290, min: 1, max: 14290, mean: 7145.5, status: "KEY" },
  { id: "timestamp", name: "timestamp", type: "Timestamp[ns]", nulls: 0, distinct: 14290, min: "2026-01-01", max: "2026-09-30", mean: "—", status: "TEMPORAL" },
  { id: "customer_id", name: "customer_id", type: "Utf8", nulls: 0, distinct: 3420, min: "CUST-0001", max: "CUST-9994", mean: "—", status: "VALID" },
  { id: "cohort_group", name: "cohort_group", type: "Categorical[4]", nulls: 0, distinct: 4, min: "2024-Q1", max: "2026-Q2", mean: "—", status: "VALID" },
  { id: "subscription_tier", name: "subscription_tier", type: "Categorical[3]", nulls: 0, distinct: 3, min: "Starter", max: "Enterprise", mean: "—", status: "VALID" },
  { id: "contract_mrr_usd", name: "contract_mrr_usd", type: "Float64", nulls: 14, distinct: 1140, min: 450.00, max: 48500.00, mean: 4210.85, status: "FLAGGED_IQR" },
  { id: "net_retention_pct", name: "net_retention_pct", type: "Float64", nulls: 0, distinct: 380, min: 82.4, max: 146.8, mean: 118.4, status: "VALID" },
  { id: "expansion_velocity", name: "expansion_velocity", type: "Float64", nulls: 2, distinct: 520, min: -12.5, max: 84.2, mean: 22.1, status: "CLEANED" },
  { id: "seat_utilization_rate", name: "seat_utilization_rate", type: "Float64", nulls: 0, distinct: 94, min: 0.12, max: 1.00, mean: 0.84, status: "VALID" },
  { id: "churn_risk_score", name: "churn_risk_score", type: "Float64", nulls: 0, distinct: 100, min: 0.01, max: 0.94, mean: 0.14, status: "VALID" },
  { id: "support_tickets_30d", name: "support_tickets_30d", type: "Int32", nulls: 0, distinct: 22, min: 0, max: 42, mean: 2.8, status: "FLAGGED_IQR" },
  { id: "cac_payback_months", name: "cac_payback_months", type: "Float64", nulls: 0, distinct: 85, min: 4.2, max: 28.6, mean: 11.4, status: "VALID" }
];

export const RAW_RECORDS = [
  { row_id: 1001, timestamp: "2026-09-01 08:14:22", customer_id: "CUST-8491", cohort_group: "2025-Q3", subscription_tier: "Enterprise", contract_mrr_usd: 14250.00, net_retention_pct: 124.5, expansion_velocity: 31.4, seat_utilization_rate: 0.92, churn_risk_score: 0.04, support_tickets_30d: 1, cac_payback_months: 8.4, is_outlier: false },
  { row_id: 1002, timestamp: "2026-09-01 08:29:10", customer_id: "CUST-3920", cohort_group: "2025-Q1", subscription_tier: "Mid-Market", contract_mrr_usd: 5400.00, net_retention_pct: 112.0, expansion_velocity: 14.2, seat_utilization_rate: 0.88, churn_risk_score: 0.11, support_tickets_30d: 3, cac_payback_months: 10.2, is_outlier: false },
  { row_id: 1003, timestamp: "2026-09-01 09:05:44", customer_id: "CUST-1194", cohort_group: "2024-Q4", subscription_tier: "Starter", contract_mrr_usd: 850.00, net_retention_pct: 94.2, expansion_velocity: -2.1, seat_utilization_rate: 0.65, churn_risk_score: 0.42, support_tickets_30d: 6, cac_payback_months: 16.8, is_outlier: false },
  { row_id: 1004, timestamp: "2026-09-01 09:44:19", customer_id: "CUST-9921", cohort_group: "2025-Q4", subscription_tier: "Enterprise", contract_mrr_usd: 48500.00, net_retention_pct: 146.8, expansion_velocity: 84.2, seat_utilization_rate: 0.99, churn_risk_score: 0.01, support_tickets_30d: 0, cac_payback_months: 5.1, is_outlier: true, outlier_reason: "MRR > 3.5 IQR Upper Bound" },
  { row_id: 1005, timestamp: "2026-09-01 10:12:03", customer_id: "CUST-4412", cohort_group: "2026-Q1", subscription_tier: "Mid-Market", contract_mrr_usd: 4200.00, net_retention_pct: 108.4, expansion_velocity: 8.5, seat_utilization_rate: 0.79, churn_risk_score: 0.18, support_tickets_30d: 2, cac_payback_months: 11.0, is_outlier: false },
  { row_id: 1006, timestamp: "2026-09-01 11:30:51", customer_id: "CUST-7729", cohort_group: "2024-Q2", subscription_tier: "Enterprise", contract_mrr_usd: 22800.00, net_retention_pct: 138.2, expansion_velocity: 42.0, seat_utilization_rate: 0.95, churn_risk_score: 0.03, support_tickets_30d: 1, cac_payback_months: 7.2, is_outlier: false },
  { row_id: 1007, timestamp: "2026-09-01 12:01:14", customer_id: "CUST-6102", cohort_group: "2025-Q2", subscription_tier: "Starter", contract_mrr_usd: 450.00, net_retention_pct: 82.4, expansion_velocity: -12.5, seat_utilization_rate: 0.38, churn_risk_score: 0.88, support_tickets_30d: 42, cac_payback_months: 28.6, is_outlier: true, outlier_reason: "Support tickets > 4.2 IQR (Spike)" },
  { row_id: 1008, timestamp: "2026-09-01 13:18:49", customer_id: "CUST-5290", cohort_group: "2026-Q2", subscription_tier: "Mid-Market", contract_mrr_usd: 6800.00, net_retention_pct: 119.5, expansion_velocity: 24.8, seat_utilization_rate: 0.84, churn_risk_score: 0.08, support_tickets_30d: 1, cac_payback_months: 9.6, is_outlier: false },
  { row_id: 1009, timestamp: "2026-09-01 14:05:32", customer_id: "CUST-8831", cohort_group: "2025-Q3", subscription_tier: "Enterprise", contract_mrr_usd: 31200.00, net_retention_pct: 141.0, expansion_velocity: 51.2, seat_utilization_rate: 0.97, churn_risk_score: 0.02, support_tickets_30d: 2, cac_payback_months: 6.0, is_outlier: false },
  { row_id: 1010, timestamp: "2026-09-01 15:42:10", customer_id: "CUST-2914", cohort_group: "2024-Q3", subscription_tier: "Starter", contract_mrr_usd: 950.00, net_retention_pct: 101.2, expansion_velocity: 3.1, seat_utilization_rate: 0.72, churn_risk_score: 0.25, support_tickets_30d: 4, cac_payback_months: 14.2, is_outlier: false },
  { row_id: 1011, timestamp: "2026-09-01 16:15:00", customer_id: "CUST-6641", cohort_group: "2025-Q4", subscription_tier: "Enterprise", contract_mrr_usd: 18900.00, net_retention_pct: 129.4, expansion_velocity: 36.5, seat_utilization_rate: 0.91, churn_risk_score: 0.05, support_tickets_30d: 0, cac_payback_months: 7.9, is_outlier: false },
  { row_id: 1012, timestamp: "2026-09-01 17:04:22", customer_id: "CUST-4109", cohort_group: "2026-Q1", subscription_tier: "Mid-Market", contract_mrr_usd: 7200.00, net_retention_pct: 122.8, expansion_velocity: 28.0, seat_utilization_rate: 0.89, churn_risk_score: 0.07, support_tickets_30d: 1, cac_payback_months: 8.8, is_outlier: false }
];

export const EXECUTIVE_KPIS = [
  {
    id: "arr",
    label: "ANNUAL RECURRING REVENUE (ARR)",
    value: "$48.24M",
    change: "+24.8%",
    isPositive: true,
    subtext: "vs. Q3 2025 baseline ($38.65M)",
    telemetryCode: "TELEMETRY.METRIC.ARR_01",
    sparkline: [28, 31, 34, 38, 41, 44, 48.2]
  },
  {
    id: "nrr",
    label: "NET REVENUE RETENTION (NRR)",
    value: "118.4%",
    change: "+3.2pp",
    isPositive: true,
    subtext: "Enterprise Cohort top-tier (134.2%)",
    telemetryCode: "TELEMETRY.METRIC.NRR_02",
    sparkline: [112, 114, 115, 116, 117, 118, 118.4]
  },
  {
    id: "churn",
    label: "GROSS CHURN PROBABILITY",
    value: "2.14%",
    change: "-0.68pp",
    isPositive: true,
    subtext: "Loss prevention model confidence 96.2%",
    telemetryCode: "TELEMETRY.METRIC.CHURN_03",
    sparkline: [3.4, 3.1, 2.9, 2.6, 2.4, 2.2, 2.14]
  },
  {
    id: "cac",
    label: "CAC PAYBACK EFFICIENCY",
    value: "11.4 Mo",
    change: "-2.3 Mo",
    isPositive: true,
    subtext: "Optimal threshold < 14.0 months",
    telemetryCode: "TELEMETRY.METRIC.CAC_04",
    sparkline: [15.2, 14.1, 13.5, 12.8, 12.1, 11.6, 11.4]
  }
];

export const FORECAST_SERIES = [
  { date: "Jan 26", actual: 3.82, forecast: null, upper: null, lower: null },
  { date: "Feb 26", actual: 3.94, forecast: null, upper: null, lower: null },
  { date: "Mar 26", actual: 4.08, forecast: null, upper: null, lower: null },
  { date: "Apr 26", actual: 4.15, forecast: null, upper: null, lower: null },
  { date: "May 26", actual: 4.31, forecast: null, upper: null, lower: null },
  { date: "Jun 26", actual: 4.48, forecast: null, upper: null, lower: null },
  { date: "Jul 26", actual: 4.62, forecast: null, upper: null, lower: null },
  { date: "Aug 26", actual: 4.79, forecast: null, upper: null, lower: null },
  { date: "Sep 26", actual: 5.02, forecast: 5.02, upper: 5.02, lower: 5.02 },
  { date: "Oct 26", actual: null, forecast: 5.24, upper: 5.48, lower: 5.01 },
  { date: "Nov 26", actual: null, forecast: 5.49, upper: 5.82, lower: 5.16 },
  { date: "Dec 26", actual: null, forecast: 5.78, upper: 6.22, lower: 5.34 },
  { date: "Jan 27", actual: null, forecast: 6.05, upper: 6.61, lower: 5.49 },
  { date: "Feb 27", actual: null, forecast: 6.32, upper: 7.02, lower: 5.62 }
];

export const COHORT_RETENTION_MATRIX = [
  { cohort: "2024-Q3", m0: 100, m3: 94, m6: 91, m9: 89, m12: 88, m15: 87, m18: 86, m21: 85, m24: 85 },
  { cohort: "2024-Q4", m0: 100, m3: 95, m6: 92, m9: 91, m12: 90, m15: 89, m18: 88, m21: 88, m24: null },
  { cohort: "2025-Q1", m0: 100, m3: 96, m6: 94, m9: 93, m12: 92, m15: 91, m18: 91, m21: null, m24: null },
  { cohort: "2025-Q2", m0: 100, m3: 97, m6: 95, m9: 94, m12: 93, m15: 93, m18: null, m21: null, m24: null },
  { cohort: "2025-Q3", m0: 100, m3: 98, m6: 96, m9: 95, m12: 95, m15: null, m18: null, m21: null, m24: null },
  { cohort: "2025-Q4", m0: 100, m3: 98, m6: 97, m9: 96, m12: null, m15: null, m18: null, m21: null, m24: null },
  { cohort: "2026-Q1", m0: 100, m3: 99, m6: 98, m9: null, m12: null, m15: null, m18: null, m21: null, m24: null },
  { cohort: "2026-Q2", m0: 100, m3: 99, m6: null, m9: null, m12: null, m15: null, m18: null, m21: null, m24: null }
];

export const HYPOTHESES_LIST = [
  {
    id: "HYP-01",
    title: "Seat Utilization > 85% is a Strong Predictor of +34% Expansion MRR",
    domain: "Expansion Velocity",
    pValue: "p < 0.0001",
    effectSize: "Cohen's d = 1.42 (High)",
    sampleSize: "n = 3,420",
    status: "CONFIRMED",
    confidence: "99.4%",
    summary: "Accounts with active weekly seat utilization above 85% exhibit a 3.4x higher probability of contract expansion within 6 months compared to baseline (<70%)."
  },
  {
    id: "HYP-02",
    title: "Support Tickets > 5 in First 30 Days Correlates with 4.8x Churn Hazard",
    domain: "Retention & Churn",
    pValue: "p = 0.0012",
    effectSize: "Hazard Ratio = 4.81",
    sampleSize: "n = 1,840",
    status: "CONFIRMED",
    confidence: "98.8%",
    summary: "Early onboarding friction indicated by >5 unresolved tickets in days 1-30 results in sharp drop in day-90 renewal intent."
  },
  {
    id: "HYP-03",
    title: "Multi-Admin Enterprise Accounts Show 134% NRR vs 104% Single-Admin",
    domain: "Account Topology",
    pValue: "p = 0.0041",
    effectSize: "Cohen's d = 0.88 (Moderate)",
    sampleSize: "n = 980",
    status: "CONFIRMED",
    confidence: "96.5%",
    summary: "Spreading administrative credentials across >=3 department leads prevents single-champion churn vulnerability."
  },
  {
    id: "HYP-04",
    title: "Price Sensitivity Elasticity in Mid-Market is Inelastic (e = -0.32)",
    domain: "Pricing Optimization",
    pValue: "p = 0.0210",
    effectSize: "Elasticity = -0.32",
    sampleSize: "n = 2,110",
    status: "ACTIONABLE",
    confidence: "94.2%",
    summary: "A simulated 12% price indexation will yield +$3.4M net revenue with an anticipated churn penalty under <0.4%."
  }
];

export const AUDIT_TRAIL = [
  { id: "EVT-9041", timestamp: "2026-09-07 13:42:19", actor: "System Agent (Auto)", action: "SARIMAX Model Convergence", details: "AIC: 1420.4, BIC: 1468.2. Forecast projected for 6 months.", status: "SUCCESS" },
  { id: "EVT-9040", timestamp: "2026-09-07 13:41:55", actor: "Dr. Elena Vance (Quantitative Lead)", action: "Propagate IQR Threshold k=1.5", details: "Outlier filtering applied across 14,290 records. 28 rows flagged.", status: "SUCCESS" },
  { id: "EVT-9039", timestamp: "2026-09-07 13:40:02", actor: "System Agent (Auto)", action: "Automated Data Cleaning Pipeline", details: "Null imputation (median fill on contract_mrr_usd), whitespace trimming.", status: "SUCCESS" },
  { id: "EVT-9038", timestamp: "2026-09-07 13:38:12", actor: "System Ingestion", action: "Dataset Schema Ingestion", details: "File q3_financials_2026.csv (4.8MB) ingested and verified.", status: "SUCCESS" }
];
