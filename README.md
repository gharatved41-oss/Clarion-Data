# Automated Insight Analyst - Backend API (Person 2 Implementation)

The **Automated Insight Analyst** backend transforms unknown spreadsheet datasets into rich domain intelligence, statistical models, ML forecasts, chart recommendations, alert notifications, data quality scores, and AI summaries.

This repository contains the complete, modular Person 2 backend services and APIs, fully integrated with Person 1's analytical base endpoints.

---

## 1. Project Structure

```
hackathon/
├── main.py                          # FastAPI Application Entrypoint
├── requirements.txt                 # Backend Python Dependencies
├── .env.example                     # Environment Configuration Template
├── README.md                        # Project Documentation
│
├── api/                             # FastAPI Routers
│   ├── person1_api.py               # Person 1 base APIs (Upload, Overview, Schema, Clean, Stats, Corrs, Outliers)
│   ├── clustering_api.py            # GET /dataset/{id}/clusters (Version 1)
│   ├── prediction_api.py            # GET /dataset/{id}/predictions (Version 2)
│   ├── visualization_api.py         # GET /dataset/{id}/charts & /chart-options (Version 3)
│   ├── intelligence_api.py          # GET /dataset/{id}/domain, /payment-analytics, /changes (Version 4)
│   ├── insight_api.py               # GET /dataset/{id}/summary, /notifications, /data-quality (Version 5)
│   └── dashboard_api.py             # GET /dataset/{id}/dashboard (Version 3 Master Aggregator)
│
├── services/                        # Business Logic & Machine Learning Services
│   ├── dataset_store.py             # In-memory Dataset & Benchmark Storage Engine
│   ├── person1_service.py           # Person 1 Analytical Calculation Service
│   ├── clustering.py                # Automatic K-Means Clustering Service
│   ├── predictor.py                 # Time-Series & Tabular ML Forecasting Regressor Service
│   ├── chart_engine.py              # Structured Plotly-Compatible Chart Recommendation Engine
│   ├── domain_detector.py           # Domain Detection Engine (Sales, Payment, Marketing, Healthcare, General)
│   ├── payment_analytics.py         # Payment Overview, Breakdown, Trends & Growth Service
│   ├── change_detector.py           # Time-Based Comparison Engine (Daily, Weekly, Monthly)
│   ├── quality_score.py             # 4-Factor Data Quality Scoring Engine (0-100 & Letter Grade)
│   ├── notification_engine.py       # Severity-Rated Insight Alert Engine (Info, Warning, Critical)
│   ├── summary_generator.py         # Fact-Based AI Insight & Gemini LLM Summary Generator
│   └── dashboard_builder.py         # Master Aggregation Service for Frontend Dashboard
│
├── models/
│   └── schemas.py                   # Pydantic Response & Request Schemas
│
├── utils/
│   ├── helpers.py                   # JSON Casting, Datetime Parsing & Column Classification
│   └── test_datasets.py             # Generator for 11 Benchmark Evaluation Datasets
│
├── static/
│   └── index.html                   # Developer Interactive Testing Web Interface
│
└── tests/                           # Pytest Unit & Integration Test Suite (215 tests)
    ├── test_clustering.py           # Version 1 Tests
    ├── test_predictions.py          # Version 2 Tests
    ├── test_charts.py               # Version 3 Tests
    ├── test_domain.py               # Version 4 Domain Tests
    ├── test_payment.py              # Version 4 Payment Tests
    ├── test_changes.py              # Version 4 Change Tests
    ├── test_quality.py              # Version 5 Quality Tests
    ├── test_notifications.py        # Version 5 Notification Tests
    ├── test_summary.py              # Version 5 Summary Tests
    └── test_integration.py          # Version 6 End-to-End Integration Suite across 11 Datasets
```

---

## 2. API Endpoints

### Person 1 APIs (Consumed by Person 2)
- `POST /upload` - Upload raw CSV dataset
- `GET /dataset/{id}/overview` - Row count, column count, memory usage, sample rows
- `GET /dataset/{id}/schema` - Column names, detected data types, null count, unique count
- `GET /dataset/{id}/cleaning-report` - Missing values summary, duplicates check
- `GET /dataset/{id}/analysis` - Basic numeric column statistics (mean, std, min, median, max, skewness)
- `GET /dataset/{id}/correlations` - Pearson correlation matrix & strong correlation pairs
- `GET /dataset/{id}/outliers` - IQR-based outlier counts, thresholds, and row indices

### Person 2 APIs (My Assigned Modules)
- `GET /dataset/{id}/clusters` - K-Means cluster assignments, cluster sizes, characteristics
- `GET /dataset/{id}/predictions` - Time-series or tabular forecasting (MAE, RMSE, R², forecast steps)
- `GET /dataset/{id}/charts` - Top 2-4 recommended Plotly-compatible chart configurations
- `GET /dataset/{id}/chart-options` - Chart selector metadata for custom frontend pickers
- `GET /dataset/{id}/domain` - Domain detection (sales, payment, marketing, healthcare, general) & evidence
- `GET /dataset/{id}/payment-analytics` - Total, completed, pending, failed payment breakdown & daily trends
- `GET /dataset/{id}/changes` - Daily, weekly, monthly period percentage changes & category emergence
- `GET /dataset/{id}/summary` - Fact-grounded natural language summary (Gemini LLM / Rule fallback)
- `GET /dataset/{id}/notifications` - Info, Warning, Critical automated alerts
- `GET /dataset/{id}/data-quality` - Quality score (0-100), letter grade (A-F), and factor breakdown
- `GET /dataset/{id}/dashboard` - Master aggregated payload for single-request dashboard rendering

---

## 3. How Person 1's APIs are Consumed

Person 2 modules consume Person 1's analytical outputs through clean service interfaces (`Person1Service` in `services/person1_service.py`):
1. `dashboard_builder.py` invokes `Person1Service.get_overview()`, `get_schema()`, `get_cleaning_report()`, `get_analysis()`, `get_correlations()`, and `get_outliers()` to aggregate baseline stats into the dashboard.
2. `notification_engine.py` consumes `Person1Service.get_outliers()` to raise outlier ratio warnings.
3. `summary_generator.py` consumes Person 1 overview, statistical analysis, correlation pairs, and outlier reports to construct deterministic factual grounding before calling Gemini LLM.

Person 1's code is strictly isolated in `services/person1_service.py` and `api/person1_api.py`, ensuring zero overwriting or breakage when merging with Person 1's repository.

---

## 4. Example API Responses

### GET /dataset/test-sales/clusters
```json
{
  "dataset_id": "test-sales",
  "applicable": true,
  "algorithm": "KMeans",
  "n_clusters": 3,
  "features_used": ["revenue", "quantity", "discount_percent"],
  "clusters": [
    {
      "cluster": 0,
      "size": 34,
      "characteristics": {
        "revenue_mean": 482.15,
        "quantity_mean": 4.2
      }
    }
  ]
}
```

### GET /dataset/test-sales/predictions
```json
{
  "dataset_id": "test-sales",
  "applicable": true,
  "target": "revenue",
  "date_column": "order_date",
  "prediction_type": "time_series_forecasting",
  "model": "LinearRegression",
  "evaluation": {
    "MAE": 42.15,
    "RMSE": 58.32,
    "R2": 0.8912,
    "MAPE_percent": 4.12
  },
  "forecast": [
    {
      "date": "2025-04-11",
      "step": 1,
      "predicted_value": 2150.45
    }
  ]
}
```

### GET /dataset/test-sales/data-quality
```json
{
  "dataset_id": "test-sales",
  "score": 98.5,
  "grade": "A",
  "factors": {
    "missing_values": 100.0,
    "duplicates": 100.0,
    "formatting": 100.0,
    "completeness": 100.0
  }
}
```

---

## 5. Required Environment Variables

Copy `.env.example` to `.env`:

```env
# Optional LLM API Key (Falls back automatically to rule-based summary if not provided)
GEMINI_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash
PORT=8000
ENVIRONMENT=development
```

---

## 6. How to Run Locally

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Start the FastAPI Backend**:
```bash
uvicorn main:app --reload --port 8000
```

3. **Open Developer Interface & API Docs**:
- Developer UI: [http://localhost:8000/](http://localhost:8000/)
- OpenAPI / Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 7. How to Test

Run the full automated test suite (215 tests covering unit & 11 benchmark datasets):

```bash
python -m pytest tests/ -v
```

### Benchmark Test Datasets Included
1. `test-sales` (Sales activity)
2. `test-payment` (Transaction/Payment records)
3. `test-marketing` (Campaign clicks & spend)
4. `test-healthcare` (Clinical & diagnostic data)
5. `test-unseen_tabular` (Arbitrary random features)
6. `test-no_dates` (Dataset without date column)
7. `test-insufficient_numerics` (Categorical/ID heavy)
8. `test-missing_values` (30%+ missing cells)
9. `test-outliers` (High extreme values)
10. `test-unsuitable_clustering` (Identifier/single category)
11. `test-unsuitable_prediction` (Pure random noise)

---

## 8. Instructions for Frontend Team

1. **Single Request Loading**: For rendering the primary dataset dashboard page, use `GET /dataset/{id}/dashboard`. It contains overview, schema, KPIs, recommended charts, predictions, notifications, domain info, quality score, and summary text.
2. **Chart Rendering**: `charts` items return Plotly-compatible JSON objects containing `type`, `title`, `x_label`, `y_label`, and `data` array.
3. **Chart Selector**: Call `GET /dataset/{id}/chart-options` to populate dropdown pickers allowing users to custom-build line, bar, scatter, or histogram charts.
4. **Soft Failures Handling**: Check `applicable: false` on `clusters`, `predictions`, and `payment-analytics`. Render a user-friendly fallback badge (e.g., "Forecasting not applicable for this dataset type") using the provided `reason` string.

---

## 9. Deployment Notes for Vercel

To deploy on Vercel:
1. Create a `vercel.json` in root:
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```
2. Ensure `requirements.txt` is present in the repository root.
3. Set environment variable `GEMINI_API_KEY` in Vercel project settings.
