"""Automated test suite for Version 5b: Outlier Analysis (GET /dataset/{id}/outliers)."""
import io
import pytest
from fastapi.testclient import TestClient


def test_outlier_detection_iqr_and_zscore(client: TestClient):
    """Test IQR and Z-Score outlier detection on known synthetic outlier points."""
    # Column 'normal_val' has values around 10-15, plus two extreme outliers: 500.0 and -200.0
    csv_content = (
        "id,normal_val,stable_val\n"
        "1,10.0,5.0\n"
        "2,11.0,5.1\n"
        "3,12.0,5.0\n"
        "4,13.0,4.9\n"
        "5,14.0,5.0\n"
        "6,12.5,5.1\n"
        "7,11.5,5.0\n"
        "8,13.5,4.9\n"
        "9,10.5,5.0\n"
        "10,12.0,5.1\n"
        "11,10.2,5.0\n"
        "12,11.8,5.0\n"
        "13,12.2,5.1\n"
        "14,13.1,5.0\n"
        "15,11.0,4.9\n"
        "16,12.8,5.0\n"
        "17,10.9,5.1\n"
        "18,13.3,5.0\n"
        "19,11.4,4.9\n"
        "20,12.1,5.0\n"
        "21,500.0,5.0\n"  # Obvious positive outlier
        "22,-200.0,5.0\n"  # Obvious negative outlier
    )
    files = {"file": ("outliers_test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    # Request all methods
    res = client.get(f"/dataset/{dataset_id}/outliers?method=all")
    assert res.status_code == 200
    data = res.json()

    assert data["dataset_id"] == dataset_id
    assert "normal_val" in data["columns"]

    col_res = data["columns"]["normal_val"]

    # 1. IQR Verification
    assert col_res["iqr"] is not None
    iqr_data = col_res["iqr"]
    assert iqr_data["outlier_count"] >= 2
    assert 20 in iqr_data["affected_rows"] or 21 in iqr_data["affected_rows"]
    assert len(iqr_data["sample_outliers"]) >= 2
    assert iqr_data["lower_bound"] < 10.0
    assert iqr_data["upper_bound"] > 15.0

    # 2. Z-Score Verification
    assert col_res["z_score"] is not None
    z_data = col_res["z_score"]
    assert z_data["outlier_count"] >= 1  # 500 should definitely exceed z-cutoff

    # 3. Isolation Forest Verification
    assert data["isolation_forest"] is not None
    assert data["isolation_forest"]["outlier_count"] > 0

    # 4. Summary Verification
    summary = data["summary"]
    assert summary["total_outlier_data_points"] > 0
    assert summary["rows_with_outliers_count"] > 0
    assert "normal_val" in summary["columns_with_outliers"]


def test_outlier_detection_specific_methods(client: TestClient):
    """Test filtering by method: iqr, zscore, isolation_forest."""
    csv_content = (
        "id,val1,val2\n"
        "1,1.0,10.0\n"
        "2,1.2,10.1\n"
        "3,1.1,10.2\n"
        "4,1.3,10.0\n"
        "5,1.0,10.1\n"
        "6,1.2,10.0\n"
        "7,100.0,10.1\n"
    )
    files = {"file": ("method_test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res_iqr = client.get(f"/dataset/{dataset_id}/outliers?method=iqr")
    assert res_iqr.status_code == 200
    assert res_iqr.json()["method"] == "iqr"

    res_zscore = client.get(f"/dataset/{dataset_id}/outliers?method=zscore")
    assert res_zscore.status_code == 200
    assert res_zscore.json()["method"] == "zscore"

    res_iso = client.get(f"/dataset/{dataset_id}/outliers?method=isolation_forest")
    assert res_iso.status_code == 200
    assert res_iso.json()["method"] == "isolation_forest"


def test_outlier_detection_not_found(client: TestClient):
    """Test 404 for unknown dataset ID."""
    res = client.get("/dataset/non-existent-id/outliers")
    assert res.status_code == 404
