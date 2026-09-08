# Data Processing & Core Analysis Module (Person 1)

This repository contains the backend service for **Person 1** of the automated data analytics platform.
It is responsible for the core data pipeline:

```
RAW DATA
   ↓
DATASET UPLOAD (v1)
   ↓
AUTOMATIC COLUMN-TYPE DETECTION (v2)
   ↓
AUTOMATIC DATA CLEANING (v3)
   ↓
STATISTICAL ANALYSIS (v4)
   ↓
CORRELATION ANALYSIS (v5a)
   ↓
OUTLIER ANALYSIS (v5b)
   ↓
AUTOMATED VISUALIZATIONS (v6)
   ↓
EXECUTIVE INSIGHTS & QUALITY SCORE (v6)
   ↓
CLEAN DATASET EXPORT (v6)
```

---

## 1. Project Purpose & Scope

Person 1 is strictly responsible for ingesting, validating, typing, cleaning, and extracting core statistical insights from tabular datasets (CSV, XLSX, XLS).
All endpoints provide clean, structured JSON contracts to be consumed by downstream frontend and analytics modules.

---

## 2. Architecture

The backend is built with **FastAPI** following a clean, modular, service-oriented architecture:

```
backend/
├── app/
│   ├── main.py                 # FastAPI application factory, CORS, and exception handlers
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Global settings & directory resolution
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py       # GET /health
│   │       └── dataset.py      # Dataset endpoints (Versions 1-5)
│   ├── services/               # Isolated domain logic per feature
│   ├── models/                 # Internal business models
│   ├── schemas/                # Pydantic request/response validation
│   └── utils/                  # Safe formatting and serialization helpers
├── data/
│   ├── uploads/                # Safe, untouched raw uploaded files
│   └── processed/              # Cleaned datasets and transformation records
├── tests/                      # Automated Pytest suite
├── requirements.txt            # Dependency manifest
└── README.md                   # System documentation
```

---

## 3. Installation

### Prerequisites
- Python 3.10+ (Tested on Python 3.12)
- PowerShell or Bash

### Setup Virtual Environment
```bash
# Navigate to the backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 4. How to Run

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API documentation (Swagger UI) is accessible at:
`http://127.0.0.1:8000/docs`

---

## 5. API List

| Version | Method | Endpoint | Description | Status |
|---|---|---|---|---|
| **v0** | `GET` | `/health` | Health check endpoint | **Active** |
| **v1** | `POST` | `/upload` | Multipart dataset file upload (CSV, XLSX, XLS) | **Active** |
| **v1** | `GET` | `/dataset/{id}/overview` | Dataset metadata, shape, nulls, duplicates, and preview rows | **Active** |
| **v2** | `GET` | `/dataset/{id}/schema` | Intelligent column type detection (numeric, categorical, datetime, text, identifier) | **Active** |
| **v3** | `GET` | `/dataset/{id}/cleaning-report`| Automatic cleaning and comprehensive audit trail | **Active** |
| **v4** | `GET` | `/dataset/{id}/analysis` | Descriptive statistics and histogram distribution bins | **Active** |
| **v5** | `GET` | `/dataset/{id}/correlations` | Pearson & Spearman correlations, matrices, and significant pairs | **Active** |
| **v5** | `GET` | `/dataset/{id}/outliers` | IQR, Z-Score, and Isolation Forest anomaly detection | **Active** |
| **v6** | `GET` | `/dataset/{id}/visualizations` | Automated tailored chart specifications (bar, line, scatter, donut, boxplot) | **Active** |
| **v6** | `GET` | `/dataset/{id}/insights` | Overall quality score (0-100), key findings, and actionable recommendations | **Active** |
| **v6** | `GET` | `/dataset/{id}/export` | Download normalized cleaned dataset in CSV or XLSX format | **Active** |


---

## 6. API Examples

### Health Check (v0)
```http
GET /health HTTP/1.1
Host: 127.0.0.1:8000
```
**Response (`200 OK`):**
```json
{
  "status": "ok"
}
```

### Dataset Upload (v1)
`POST /upload` accepts `multipart/form-data` with a `file` field (.csv, .xlsx, .xls).

**Response (`201 Created`):**
```json
{
  "dataset_id": "447659db-fdfa-4cfa-b863-3beecef9480a",
  "filename": "sales.csv",
  "rows": 1000,
  "columns": 12,
  "message": "Dataset uploaded successfully"
}
```

### Dataset Overview (v1)
`GET /dataset/{id}/overview`

**Response (`200 OK`):**
```json
{
  "dataset_id": "447659db-fdfa-4cfa-b863-3beecef9480a",
  "filename": "sales.csv",
  "rows": 1000,
  "columns": 12,
  "column_names": ["customer_id", "name", "age", "city", "purchase_amount"],
  "file_type": ".csv",
  "missing_values": 45,
  "duplicate_rows": 12,
  "memory_usage_bytes": 1048576
}
```

### Intelligent Column-Type Detection (v2)
`GET /dataset/{id}/schema`

Automatically classifies columns into: `numeric`, `categorical`, `datetime`, `text`, or `identifier`.

**Response (`200 OK`):**
```json
{
  "dataset_id": "ea91b261-9ec9-4959-994c-f50d6a824b30",
  "columns": [
    {
      "name": "customer_id",
      "type": "identifier",
      "confidence": 0.98,
      "original_dtype": "str",
      "unique_count": 780,
      "null_count": 0
    },
    {
      "name": "age",
      "type": "numeric",
      "confidence": 0.99,
      "original_dtype": "float64",
      "unique_count": 48,
      "null_count": 49
    },
    {
      "name": "gender",
      "type": "categorical",
      "confidence": 0.95,
      "original_dtype": "str",
      "unique_count": 10,
      "null_count": 39
    },
    {
      "name": "unit_price",
      "type": "numeric",
      "confidence": 0.99,
      "original_dtype": "str",
      "unique_count": 778,
      "null_count": 0
    },
    {
      "name": "order_date",
      "type": "datetime",
      "confidence": 0.99,
      "original_dtype": "str",
      "unique_count": 577,
      "null_count": 0
    },
    {
      "name": "customer_feedback",
      "type": "text",
      "confidence": 0.96,
      "original_dtype": "str",
      "unique_count": 20,
      "null_count": 78
    }
  ]
}
```

### Automatic Data Cleaning & Audit Report (v3)
`GET /dataset/{id}/cleaning-report`

Executes non-destructive data cleaning and returns the transformation audit log:

**Response (`200 OK`):**
```json
{
  "dataset_id": "fe1dbf80-ac18-4107-b9ce-7c105e234d48",
  "original_row_count": 800,
  "cleaned_row_count": 780,
  "original_column_count": 17,
  "missing_values_detected": 356,
  "missing_values_handled": 351,
  "duplicates_detected": 20,
  "duplicates_removed": 20,
  "numeric_conversions": 2278,
  "currency_conversions": 384,
  "percentage_conversions": 461,
  "date_conversions": 775,
  "whitespace_fixes": 450,
  "capitalization_fixes": 1545,
  "operations": [
    {
      "column": null,
      "operation": "duplicate_removal",
      "affected_rows": 20,
      "method": "exact_match",
      "details": "Identified and removed 20 exact duplicate rows."
    },
    {
      "column": "unit_price",
      "operation": "currency_conversion",
      "affected_rows": 190,
      "method": "currency_symbol_stripping",
      "details": "Stripped currency symbols (₹, $, INR, etc.) from 190 cells."
    },
    {
      "column": "discount",
      "operation": "percentage_conversion",
      "affected_rows": 461,
      "method": "percentage_normalization",
      "details": "Normalized 461 percentage cells to standard numeric scale (e.g., 10% -> 10.0)."
    },
    {
      "column": "gender",
      "operation": "category_normalization",
      "affected_rows": 317,
      "method": "case_and_frequency_consensus",
      "details": "Unified 317 casing inconsistencies into canonical representations."
    },
    {
      "column": "age",
      "operation": "missing_value_imputation",
      "affected_rows": 47,
      "method": "median",
      "details": "Imputed 47 missing numeric values using column median (34.0)."
    }
  ],
  "warnings": [
    "Column 'order_date' contained 5 unparseable date values converted to NaT.",
    "Column 'order_date' has 5 missing/invalid dates left un-imputed."
  ],
  "skipped_operations": [
    "Missing value imputation skipped for datetime column 'order_date'."
  ]
}
```

### Statistical Analysis (v4)
`GET /dataset/{id}/analysis`

Calculates descriptive statistics tailored to column types:

**Response (`200 OK`):**
```json
{
  "dataset_id": "fe1dbf80-ac18-4107-b9ce-7c105e234d48",
  "total_rows": 780,
  "total_columns": 17,
  "numeric_analysis": {
    "age": {
      "count": 780,
      "null_count": 0,
      "mean": 35.42,
      "median": 34.0,
      "min": 18.0,
      "max": 65.0,
      "std": 9.12,
      "variance": 83.17,
      "skewness": 0.24,
      "q1": 28.0,
      "q3": 42.0,
      "iqr": 14.0,
      "histogram": [
        {"bin_start": 18.0, "bin_end": 22.7, "count": 68},
        {"bin_start": 22.7, "bin_end": 27.4, "count": 112}
      ]
    }
  },
  "categorical_analysis": {
    "gender": {
      "count": 780,
      "null_count": 0,
      "unique_count": 2,
      "top_categories": [
        {"category": "Female", "count": 420, "percentage": 53.85},
        {"category": "Male", "count": 360, "percentage": 46.15}
      ]
    }
  },
  "datetime_analysis": {
    "order_date": {
      "count": 775,
      "null_count": 5,
      "min_date": "2026-01-01",
      "max_date": "2026-09-22",
      "range_days": 264,
      "yearly_distribution": {"2026": 775},
      "monthly_distribution": {"2026-01": 95, "2026-02": 88}
    }
  },
  "text_analysis": {
    "customer_feedback": {
      "count": 780,
      "null_count": 0,
      "unique_count": 25,
      "avg_word_count": 4.12,
      "avg_char_length": 26.8,
      "min_length": 9,
      "max_length": 45
    }
  },
  "identifier_analysis": {
    "customer_id": {
      "count": 780,
      "null_count": 0,
      "unique_count": 780,
      "uniqueness_ratio": 1.0
    }
  }
}
```

### Correlation Analysis (v5a)
`GET /dataset/{id}/correlations?method=pearson`

Computes pairwise numerical correlation matrix and highlights significant associations:

**Response (`200 OK`):**
```json
{
  "dataset_id": "fe1dbf80-ac18-4107-b9ce-7c105e234d48",
  "method": "pearson",
  "numeric_columns": ["quantity", "unit_price", "total_sales", "discount", "customer_rating"],
  "matrix": [
    [1.0, -0.0412, 0.6521, 0.0123, -0.0154],
    [-0.0412, 1.0, 0.7245, -0.0312, 0.0211],
    [0.6521, 0.7245, 1.0, -0.0187, 0.0094],
    [0.0123, -0.0312, -0.0187, 1.0, -0.0045],
    [-0.0154, 0.0211, 0.0094, -0.0045, 1.0]
  ],
  "strong_positive": [
    {
      "var1": "unit_price",
      "var2": "total_sales",
      "correlation": 0.7245,
      "strength": "Strong",
      "direction": "Positive"
    },
    {
      "var1": "quantity",
      "var2": "total_sales",
      "correlation": 0.6521,
      "strength": "Strong",
      "direction": "Positive"
    }
  ],
  "strong_negative": [],
  "important_pairs": [
    {
      "var1": "unit_price",
      "var2": "total_sales",
      "correlation": 0.7245,
      "strength": "Strong",
      "direction": "Positive"
    }
  ]
}
```

### Outlier Analysis (v5b)
`GET /dataset/{id}/outliers?method=all`

Detects anomalies using Interquartile Range (IQR), Z-Score, and Isolation Forest:

**Response (`200 OK`):**
```json
{
  "dataset_id": "fe1dbf80-ac18-4107-b9ce-7c105e234d48",
  "method": "all",
  "summary": {
    "total_outlier_data_points": 42,
    "rows_with_outliers_count": 38,
    "rows_with_outliers_percentage": 4.87,
    "columns_with_outliers": ["delivery_days", "total_sales"]
  },
  "columns": {
    "delivery_days": {
      "column": "delivery_days",
      "iqr": {
        "q1": 2.0,
        "q3": 6.0,
        "iqr": 4.0,
        "lower_bound": -4.0,
        "upper_bound": 12.0,
        "outlier_count": 28,
        "outlier_percentage": 3.59,
        "sample_outliers": [
          {"row_index": 14, "value": 30.0},
          {"row_index": 18, "value": 44.0}
        ],
        "affected_rows": [14, 18]
      },
      "z_score": {
        "mean": 4.82,
        "std": 5.41,
        "threshold": 3.0,
        "lower_bound": -11.41,
        "upper_bound": 21.05,
        "outlier_count": 8,
        "outlier_percentage": 1.03,
        "sample_outliers": [
          {"row_index": 14, "value": 30.0},
          {"row_index": 18, "value": 44.0}
        ],
        "affected_rows": [14, 18]
      }
    }
  },
  "isolation_forest": {
    "contamination": 0.05,
    "outlier_count": 39,
    "outlier_percentage": 5.0,
    "affected_rows": [14, 18, 52]
  }
}
```

### Automated Chart Visualizations (v6)
`GET /dataset/{id}/visualizations`

Synthesizes tailored SVG chart specifications based on schema properties:
- **Donut Charts**: Top categories and relative percentages for categorical variables.
- **Bivariate Bar Charts**: Average numeric values grouped across top categorical segments.
- **Line Charts**: Chronological observation volume over monthly periods.
- **Correlation Scatter Plots**: Co-variation between numeric pairs.
- **Boxplots**: 5-number distribution summary (Min, Q1, Median, Q3, Max).

**Response (`200 OK`):**
```json
{
  "dataset_id": "ea91b261-9ec9-4959-994c-f50d6a824b30",
  "total_recommendations": 5,
  "charts": [
    {
      "id": "donut_gender",
      "title": "Distribution of Gender",
      "chart_type": "donut",
      "x_axis_label": "gender",
      "y_axis_label": "Count & Percentage",
      "description": "Breakdown of observations across top 2 categories in 'gender'.",
      "series": [
        {
          "name": "gender",
          "data": [
            {"label": "Male", "value": 410, "secondary_value": 52.56},
            {"label": "Female", "value": 370, "secondary_value": 47.44}
          ]
        }
      ]
    }
  ]
}
```

### Executive Insights & Data Quality Scoring (v6)
`GET /dataset/{id}/insights`

Evaluates overall dataset integrity with a 0-100 composite score, letter grade, automated findings, and prescriptive recommendations.

**Response (`200 OK`):**
```json
{
  "dataset_id": "ea91b261-9ec9-4959-994c-f50d6a824b30",
  "quality_score": {
    "overall_score": 92,
    "grade": "A",
    "completeness_score": 98,
    "uniqueness_score": 92,
    "validity_score": 88
  },
  "key_findings": [
    {
      "category": "overview",
      "title": "Dataset Architecture (780 Records × 7 Attributes)",
      "description": "The dataset contains 780 observations across 7 attributes...",
      "impact": "positive"
    }
  ],
  "actionable_recommendations": [
    "Verify upstream data ingestion pipelines to prevent 25 duplicate records from reoccurring.",
    "Imputation resolved 18 missing values via median/mode strategies; review if source database schemas should enforce NOT NULL constraints."
  ]
}
```

### Clean Dataset Export (v6)
`GET /dataset/{id}/export?format={csv|xlsx}`

Streams the cleaned, normalized dataset as a downloadable file attachment.

---

## 7. Interactive Frontend Dashboard

A modern, responsive, glassmorphic dark-mode web application is embedded with the backend.
To access it:
1. Start the backend: `python -m uvicorn app.main:app --reload`
2. Open your web browser at: `http://127.0.0.1:8000/`

The dashboard allows users to:
1. Drag & drop CSV/XLSX/XLS datasets or load demo dirty data with one click.
2. View real-time upload status and parsing progress.
3. Review dataset structural metrics and live 5-row sample preview.
4. Inspect detected column types with confidence scores and original Pandas types.
5. Audit non-destructive data cleaning operations (currencies, percentages, casing, dates, duplicates).
6. Explore descriptive statistics and interactive distribution histograms.
7. Visualize numerical correlation matrices with interactive color heatmaps and ranked associations.
8. Inspect outliers via IQR, Z-Score, and Isolation Forest with affected row indices.
9. Examine automated SVG chart visualizations across distributions, bivariate bar charts, time-series, and boxplots.
10. Review the Executive Health Gauge (0-100 score and letter grade), key findings, and actionable recommendations.
11. Download the cleaned, deduplicated, and normalized dataset as CSV or Excel (.xlsx) with one click.

---

## 8. Pipeline Methodologies

- **Dataset Processing Pipeline:** Uploaded raw datasets are safely stored in `data/uploads/` with a unique UUID without mutating the original file. Cleaned versions are saved in `data/processed/`.
- **Column Detection Methodology (v2):** Rule- and heuristic-based classification into Numeric, Categorical, DateTime, Text, and Identifier with confidence scores.
- **Cleaning Methodology (v3):** Imputation of missing values (median for numeric, mode for categorical, placeholder for text), exact duplicate removal, normalization of currencies (₹, $, INR, USD), percentages, dates (ISO 8601), extra whitespace, and category capitalization.
- **Statistical Methodology (v4):** Type-specific aggregations (mean, median, std, min, max, count, quartiles, IQR, skewness) and distribution binning ready for visualization; categorical value frequency counting; date boundary calculation.
- **Correlation Methodology (v5a):** Pearson and Spearman correlation matrices with strength categorization (|r| from very weak to very strong), excluding identifier columns.
- **Outlier Methodology (v5b):** Non-destructive IQR ($1.5 \times \text{IQR}$), Z-Score ($|z| > 3$), and Isolation Forest multi-variate anomaly detection reporting affected row indices.
- **Automated Visualizations (v6):** Heuristic chart synthesizer selecting optimal chart paradigms (donut distributions, bivariate bars, time-series trends, paired scatter plots, and 5-number boxplots) tailored to detected column data types.
- **Executive Insights (v6):** Comprehensive 0-100 Data Quality Scoring (combining 40% Completeness, 30% Uniqueness, 30% Validity), automated analytical headline discovery, and actionable recommendations.
- **Dataset Export (v6):** In-memory buffered streaming export supporting both RFC 4180 CSV and OpenXML Excel (`.xlsx`) formats.

---

## 9. Testing Instructions

To execute the automated test suite covering all 37 tests (including upload, schema detection, cleaning, statistics, correlations, outliers, visualizations, insights, export, and end-to-end edge-case datasets):

```bash
# Ensure virtual environment is activated and you are in the backend directory:
pytest tests/ -v
```

---

## 10. Version History & Changelog

| Version | Milestone | Description |
|---|---|---|
| **v0.1.0** | System Foundation | FastAPI factory, CORS setup, structured error handling, and `/health` check. |
| **v1.0.0** | Feature 1 | File validation, multi-encoding CSV/XLSX loading, UUID dataset persistence, dataset overview, and sample preview rows. |
| **v2.0.0** | Feature 2 | Intelligent heuristic column-type detection (`numeric`, `categorical`, `datetime`, `text`, `identifier`) with confidence scoring. |
| **v3.0.0** | Feature 3 | Non-destructive automated data cleaning, missing value imputation, duplicate removal, currency/percentage conversions, casing consensus, date normalization, and audit report. |
| **v4.0.0** | Feature 4 | Type-aware statistical analysis: descriptive stats, quartiles, IQR, skewness, distribution histogram bins, category frequencies, and date ranges. |
| **v5.0.0** | Feature 5 & Frontend | Pearson & Spearman correlation matrix and relationship ranking; IQR, Z-Score, and Isolation Forest outlier detection; embedded glassmorphic dark-mode analytics dashboard. |
| **v6.0.0** | Feature 6 & Advanced Suite | Automated chart visualization recommendations (Bar, Line, Scatter, Donut, Boxplot), composite Data Quality Scoring (0-100), executive findings & recommendations, and clean dataset streaming export (CSV/XLSX). |
