"""Automated test suite for Version 5a: Correlation Analysis (GET /dataset/{id}/correlations)."""
import io
import pytest
from fastapi.testclient import TestClient


def test_correlations_linear_relationships(client: TestClient):
    """Test correlation matrix calculation, strong positive and negative relationship extraction."""
    # x and y strongly positive (y = 2x + noise)
    # x and z strongly negative (z = -3x + noise)
    # w is random noise
    csv_content = (
        "id,x,y,z,w,category\n"
        "1,10.0,20.2,-30.1,5.5,Alpha\n"
        "2,20.0,40.1,-60.2,2.1,Beta\n"
        "3,30.0,59.8,-90.0,8.3,Alpha\n"
        "4,40.0,80.5,-120.4,1.2,Beta\n"
        "5,50.0,99.9,-150.1,9.0,Alpha\n"
        "6,60.0,120.2,-180.3,4.4,Beta\n"
    )
    files = {"file": ("corr_data.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    # Test Pearson (default)
    res = client.get(f"/dataset/{dataset_id}/correlations")
    assert res.status_code == 200
    data = res.json()

    assert data["dataset_id"] == dataset_id
    assert data["method"] == "pearson"
    assert "x" in data["numeric_columns"]
    assert "y" in data["numeric_columns"]
    assert "z" in data["numeric_columns"]
    assert "id" not in data["numeric_columns"]  # Identifier should be excluded
    assert "category" not in data["numeric_columns"]  # Categorical excluded

    # Verify matrix dimension
    dim = len(data["numeric_columns"])
    assert len(data["matrix"]) == dim
    for row in data["matrix"]:
        assert len(row) == dim

    # Check strong positive pairs
    strong_pos = data["strong_positive"]
    assert len(strong_pos) > 0
    # x and y should be strong positive (> 0.99)
    xy_pair = next((p for p in strong_pos if (p["var1"] == "x" and p["var2"] == "y") or (p["var1"] == "y" and p["var2"] == "x")), None)
    assert xy_pair is not None
    assert xy_pair["correlation"] > 0.95
    assert xy_pair["direction"] == "Positive"
    assert xy_pair["strength"] == "Very Strong"

    # Check strong negative pairs
    strong_neg = data["strong_negative"]
    assert len(strong_neg) > 0
    # x and z should be strong negative (< -0.95)
    xz_pair = next((p for p in strong_neg if (p["var1"] == "x" and p["var2"] == "z") or (p["var1"] == "z" and p["var2"] == "x")), None)
    assert xz_pair is not None
    assert xz_pair["correlation"] < -0.95
    assert xz_pair["direction"] == "Negative"
    assert xz_pair["strength"] == "Very Strong"

    # Test Spearman method
    res_spearman = client.get(f"/dataset/{dataset_id}/correlations?method=spearman")
    assert res_spearman.status_code == 200
    assert res_spearman.json()["method"] == "spearman"


def test_correlations_insufficient_columns(client: TestClient):
    """Test correlation returns empty matrix with message when <2 numeric columns."""
    csv_content = (
        "name,city,department\n"
        "Alice,Mumbai,Sales\n"
        "Bob,Delhi,IT\n"
        "Charlie,Kolkata,HR\n"
    )
    files = {"file": ("no_numeric.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/correlations")
    assert res.status_code == 200
    data = res.json()
    assert len(data["matrix"]) == 0
    assert data["message"] is not None
    assert "fewer than 2" in data["message"].lower()
