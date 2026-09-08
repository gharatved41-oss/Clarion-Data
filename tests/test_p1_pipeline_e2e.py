"""Comprehensive End-to-End Pipeline test suite covering all 15 required dataset edge cases."""
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def test_e2e_full_dirty_ecommerce_csv(client: TestClient):
    """Test full pipeline on the provided workspace dataset: test_ecommerce_dirty.csv."""
    csv_file_path = WORKSPACE_ROOT / "test_ecommerce_dirty.csv"
    assert csv_file_path.exists(), f"Expected {csv_file_path} to exist."

    with open(csv_file_path, "rb") as f:
        files = {"file": ("ecommerce_dirty.csv", f.read(), "text/csv")}

    # 1. Upload
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    # 2. Overview with sample rows
    ov_res = client.get(f"/dataset/{dataset_id}/overview")
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert ov_data["rows"] > 500
    assert len(ov_data["preview_rows"]) > 0

    # 3. Schema Detection
    schema_res = client.get(f"/dataset/{dataset_id}/schema")
    assert schema_res.status_code == 200
    schema_data = schema_res.json()
    col_types = {col["name"]: col["type"] for col in schema_data["columns"]}
    assert col_types.get("customer_id") == "identifier"
    assert col_types.get("age") == "numeric"
    assert col_types.get("gender") == "categorical"
    assert col_types.get("unit_price") == "numeric"
    assert col_types.get("order_date") == "datetime"

    # 4. Cleaning Report
    clean_res = client.get(f"/dataset/{dataset_id}/cleaning-report")
    assert clean_res.status_code == 200
    clean_data = clean_res.json()
    assert clean_data["duplicates_removed"] >= 0
    assert clean_data["currency_conversions"] > 0
    assert clean_data["capitalization_fixes"] > 0

    # 5. Statistical Analysis
    analysis_res = client.get(f"/dataset/{dataset_id}/analysis")
    assert analysis_res.status_code == 200
    analysis_data = analysis_res.json()
    assert len(analysis_data["numeric_analysis"]) > 0
    assert "age" in analysis_data["numeric_analysis"]
    assert "gender" in analysis_data["categorical_analysis"]

    # 6. Correlations
    corr_res = client.get(f"/dataset/{dataset_id}/correlations")
    assert corr_res.status_code == 200
    corr_data = corr_res.json()
    assert len(corr_data["matrix"]) > 0

    # 7. Outliers
    outlier_res = client.get(f"/dataset/{dataset_id}/outliers")
    assert outlier_res.status_code == 200
    outlier_data = outlier_res.json()
    assert outlier_data["summary"]["total_outlier_data_points"] > 0

    # 8. Visualizations (v6)
    vis_res = client.get(f"/dataset/{dataset_id}/visualizations")
    assert vis_res.status_code == 200
    vis_data = vis_res.json()
    assert vis_data["total_recommendations"] >= 3

    # 9. Executive Insights (v6)
    ins_res = client.get(f"/dataset/{dataset_id}/insights")
    assert ins_res.status_code == 200
    ins_data = ins_res.json()
    assert 0 <= ins_data["quality_score"]["overall_score"] <= 100
    assert len(ins_data["key_findings"]) > 0

    # 10. Cleaned Export (v6)
    exp_res = client.get(f"/dataset/{dataset_id}/export?format=csv")
    assert exp_res.status_code == 200
    assert "text/csv" in exp_res.headers["content-type"]
    assert len(exp_res.content) > 1000


def test_e2e_full_dirty_ecommerce_xlsx(client: TestClient):
    """Test full pipeline on the provided workspace Excel dataset: test_ecommerce_dirty.xlsx."""
    xlsx_file_path = WORKSPACE_ROOT / "test_ecommerce_dirty.xlsx"
    assert xlsx_file_path.exists(), f"Expected {xlsx_file_path} to exist."

    with open(xlsx_file_path, "rb") as f:
        files = {"file": ("ecommerce_dirty.xlsx", f.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    # Overview
    ov_res = client.get(f"/dataset/{dataset_id}/overview")
    assert ov_res.status_code == 200

    # Schema
    schema_res = client.get(f"/dataset/{dataset_id}/schema")
    assert schema_res.status_code == 200

    # Cleaning
    clean_res = client.get(f"/dataset/{dataset_id}/cleaning-report")
    assert clean_res.status_code == 200

    # Analysis
    analysis_res = client.get(f"/dataset/{dataset_id}/analysis")
    assert analysis_res.status_code == 200

    # Correlations
    corr_res = client.get(f"/dataset/{dataset_id}/correlations")
    assert corr_res.status_code == 200

    # Outliers
    out_res = client.get(f"/dataset/{dataset_id}/outliers")
    assert out_res.status_code == 200

    # Visualizations (v6)
    vis_res = client.get(f"/dataset/{dataset_id}/visualizations")
    assert vis_res.status_code == 200

    # Executive Insights (v6)
    ins_res = client.get(f"/dataset/{dataset_id}/insights")
    assert ins_res.status_code == 200

    # Cleaned Export XLSX (v6)
    exp_res = client.get(f"/dataset/{dataset_id}/export?format=xlsx")
    assert exp_res.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in exp_res.headers["content-type"]



def test_edge_case_no_numeric_columns(client: TestClient):
    """Test full pipeline when a dataset contains NO numeric columns."""
    csv_content = (
        "department,city,region\n"
        "Finance,New York,East\n"
        "Operations,Chicago,Midwest\n"
        "Human Resources,San Francisco,West\n"
        "Legal,Boston,East\n"
    )
    files = {"file": ("no_numeric.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up = client.post("/upload", files=files)
    assert up.status_code == 201
    d_id = up.json()["dataset_id"]

    # Analysis should contain categorical only
    an_res = client.get(f"/dataset/{d_id}/analysis")
    assert an_res.status_code == 200
    assert len(an_res.json()["numeric_analysis"]) == 0
    assert len(an_res.json()["categorical_analysis"]) == 3

    # Correlations should return gracefully with empty matrix
    corr_res = client.get(f"/dataset/{d_id}/correlations")
    assert corr_res.status_code == 200
    assert len(corr_res.json()["matrix"]) == 0

    # Outliers should return gracefully
    out_res = client.get(f"/dataset/{d_id}/outliers")
    assert out_res.status_code == 200
    assert out_res.json()["summary"]["total_outlier_data_points"] == 0


def test_edge_case_no_categorical_columns(client: TestClient):
    """Test full pipeline when a dataset contains ONLY numeric and identifier columns."""
    csv_content = (
        "id,score1,score2,score3\n"
        "1,10.5,20.0,30.5\n"
        "2,12.0,22.5,32.0\n"
        "3,15.5,25.0,35.5\n"
        "4,18.0,28.0,38.0\n"
        "5,20.5,30.5,40.5\n"
    )
    files = {"file": ("all_numeric.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up = client.post("/upload", files=files)
    assert up.status_code == 201
    d_id = up.json()["dataset_id"]

    an_res = client.get(f"/dataset/{d_id}/analysis")
    assert an_res.status_code == 200
    assert len(an_res.json()["categorical_analysis"]) == 0
    assert len(an_res.json()["numeric_analysis"]) == 3

    corr_res = client.get(f"/dataset/{d_id}/correlations")
    assert corr_res.status_code == 200
    assert len(corr_res.json()["matrix"]) == 3


def test_edge_case_heavy_missing_and_duplicates(client: TestClient):
    """Test dataset with heavy missing values, extreme duplicates, and strings as numbers."""
    csv_content = (
        "code,metric_a,metric_b\n"
        "C01,100,200\n"
        "C01,100,200\n"
        "C01,100,200\n"
        "C02,,400\n"
        "C03,300,\n"
        "C04,,\n"
    )
    files = {"file": ("heavy_dirty.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up = client.post("/upload", files=files)
    assert up.status_code == 201
    d_id = up.json()["dataset_id"]

    clean = client.get(f"/dataset/{d_id}/cleaning-report")
    assert clean.status_code == 200
    assert clean.json()["duplicates_removed"] == 2
    assert clean.json()["missing_values_handled"] > 0

    analysis = client.get(f"/dataset/{d_id}/analysis")
    assert analysis.status_code == 200
