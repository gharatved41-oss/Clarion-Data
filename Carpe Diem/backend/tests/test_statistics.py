"""Automated test suite for Version 4: Statistical Analysis (GET /dataset/{id}/analysis)."""
import io
import pytest
from fastapi.testclient import TestClient


def test_statistical_analysis_success(client: TestClient):
    """Test statistical analysis returns tailored metrics for numeric, categorical, date, text, and identifier."""
    csv_content = (
        "user_id,username,age,score,rating,department,signup_date,notes\n"
        "USR001,alice,25,100.5,4.5,Engineering,2026-01-10,Great team contributor\n"
        "USR002,bob,30,85.0,3.8,Marketing,2026-02-15,Handles campaign operations\n"
        "USR003,carol,35,92.5,4.9,Engineering,2026-03-20,Lead system architect\n"
        "USR004,david,40,78.0,3.5,Sales,2026-04-25,Top revenue generator\n"
        "USR005,eve,45,95.0,4.2,Engineering,2026-05-30,Devops infrastructure lead\n"
    )
    files = {"file": ("stats_sample.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/analysis")
    assert res.status_code == 200
    data = res.json()

    assert data["dataset_id"] == dataset_id
    assert data["total_rows"] == 5
    assert data["total_columns"] == 8

    # 1. Numeric analysis
    numeric = data["numeric_analysis"]
    assert "age" in numeric
    assert "score" in numeric
    assert "rating" in numeric
    assert numeric["age"]["count"] == 5
    assert numeric["age"]["mean"] == 35.0
    assert numeric["age"]["median"] == 35.0
    assert numeric["age"]["min"] == 25.0
    assert numeric["age"]["max"] == 45.0
    assert numeric["age"]["std"] > 0
    assert len(numeric["age"]["histogram"]) > 0

    # 2. Categorical analysis
    categorical = data["categorical_analysis"]
    assert "department" in categorical
    assert categorical["department"]["count"] == 5
    assert categorical["department"]["unique_count"] == 3
    top_cats = categorical["department"]["top_categories"]
    assert len(top_cats) == 3
    assert top_cats[0]["category"] == "Engineering"
    assert top_cats[0]["count"] == 3
    assert top_cats[0]["percentage"] == 60.0

    # 3. Datetime analysis
    dt = data["datetime_analysis"]
    assert "signup_date" in dt
    assert dt["signup_date"]["count"] == 5
    assert dt["signup_date"]["min_date"] == "2026-01-10"
    assert dt["signup_date"]["max_date"] == "2026-05-30"
    assert dt["signup_date"]["range_days"] > 100

    # 4. Text analysis
    text = data["text_analysis"]
    assert "notes" in text or "username" in text
    col_name = "notes" if "notes" in text else "username"
    assert text[col_name]["count"] == 5
    assert text[col_name]["avg_word_count"] > 0

    # 5. Identifier analysis
    identifiers = data["identifier_analysis"]
    assert "user_id" in identifiers
    assert identifiers["user_id"]["count"] == 5
    assert identifiers["user_id"]["unique_count"] == 5
    assert identifiers["user_id"]["uniqueness_ratio"] == 1.0


def test_statistical_analysis_not_found(client: TestClient):
    """Test 404 response for unknown dataset ID."""
    res = client.get("/dataset/unknown-dataset-id/analysis")
    assert res.status_code == 404
