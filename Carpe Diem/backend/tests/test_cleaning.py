"""Automated test suite for Version 3: Automatic Data Cleaning & Transformation Audit Report."""
import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient


def test_automatic_cleaning_pipeline(client: TestClient):
    """Test full automated cleaning on an intentionally dirty dataset."""
    dirty_csv = (
        "emp_id,emp_name,department,salary,tax_pct,joining_date,city,performance_notes\n"
        'EMP001, John Doe ,Sales,"₹55,000",10 %,2026-01-15, Mumbai ,Consistently exceeded monthly sales quotas.\n'
        'EMP002,Jane Smith,SALES,"62,000 INR","12%",15/02/2026,mumbai,Spearheaded marketing outreach.\n'
        'EMP003,Bob Wilson,sales,"$48,000",8%,03/10/2026,MUMBAI,Supported client account transitions.\n'
        'EMP001, John Doe ,Sales,"₹55,000",10 %,2026-01-15, Mumbai ,Consistently exceeded monthly sales quotas.\n'  # Duplicate
        'EMP004,Alice Brown,IT,"75,000",,2026/04/20,Delhi,Architected resilient microservice architecture.\n'  # Missing tax
        'EMP005,Charlie Black,Engineering,,15%,12-05-2026,DELHI,\n'  # Missing salary and notes
    )
    files = {"file": ("dirty_staff.csv", io.BytesIO(dirty_csv.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    # Request cleaning report
    clean_res = client.get(f"/dataset/{dataset_id}/cleaning-report")
    assert clean_res.status_code == 200
    report = clean_res.json()

    # Verify report statistics
    assert report["dataset_id"] == dataset_id
    assert report["original_row_count"] == 6
    assert report["cleaned_row_count"] == 5  # 1 duplicate removed
    assert report["duplicates_detected"] == 1
    assert report["duplicates_removed"] == 1
    assert report["whitespace_fixes"] > 0
    assert report["capitalization_fixes"] > 0
    assert report["currency_conversions"] > 0
    assert report["percentage_conversions"] > 0
    assert report["numeric_conversions"] > 0
    assert report["date_conversions"] > 0
    assert report["missing_values_handled"] > 0
    assert len(report["operations"]) > 0

    # Verify operations contains specific techniques
    op_names = [op["operation"] for op in report["operations"]]
    assert "duplicate_removal" in op_names
    assert "whitespace_trimming" in op_names
    assert "currency_conversion" in op_names
    assert "percentage_conversion" in op_names
    assert "category_normalization" in op_names
    assert "missing_value_imputation" in op_names

    # Check that cleaned CSV file was generated and persisted
    from app.services.cleaning_service import CleaningService
    cleaned_df, cached_report = CleaningService.load_cleaned_dataset(dataset_id)
    assert len(cleaned_df) == 5

    # Check city casing is unified
    cities = set(cleaned_df["city"].unique())
    assert "mumbai" not in cities
    assert "MUMBAI" not in cities
    assert "Mumbai" in cities

    # Check department casing is unified
    departments = set(cleaned_df["department"].unique())
    assert "sales" not in departments
    assert "SALES" not in departments
    assert "Sales" in departments

    # Check salaries are converted to numeric and median imputed
    assert pd.api.types.is_numeric_dtype(cleaned_df["salary"])
    assert cleaned_df["salary"].isna().sum() == 0

    # Check tax_pct is numeric scale (e.g. 10.0, 12.0)
    assert pd.api.types.is_numeric_dtype(cleaned_df["tax_pct"])
    assert cleaned_df["tax_pct"].isna().sum() == 0
    assert cleaned_df["tax_pct"].min() >= 0.0

    # Check dates are standardized to YYYY-MM-DD
    for d in cleaned_df["joining_date"]:
        assert len(d) == 10
        assert d[4] == "-" and d[7] == "-"


def test_cleaning_report_not_found(client: TestClient):
    """Test GET /dataset/{id}/cleaning-report returns 404 for unknown IDs."""
    res = client.get("/dataset/non-existent-clean-id/cleaning-report")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
