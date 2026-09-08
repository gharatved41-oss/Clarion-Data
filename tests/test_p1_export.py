"""Automated test suite for Version 6.0: Clean Dataset Export (GET /dataset/{id}/export)."""
import io
import pytest
import pandas as pd
from fastapi.testclient import TestClient


def test_export_cleaned_csv(client: TestClient):
    """Test downloading cleaned dataset as CSV."""
    csv_content = (
        "id,product,price,discount,date\n"
        "1,Widget A,$100.50,10%,2024-01-01\n"
        "2,Widget B,$200.00,15%,2024-01-02\n"
        "1,Widget A,$100.50,10%,2024-01-01\n"  # Duplicate row
    )
    files = {"file": ("raw_export.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/export?format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "attachment; filename=" in res.headers["content-disposition"]
    assert f"cleaned_{dataset_id[:8]}.csv" in res.headers["content-disposition"]

    # Verify content parsed from exported stream
    exported_df = pd.read_csv(io.StringIO(res.text))
    # Deduplication should have reduced 3 rows to 2 rows
    assert len(exported_df) == 2
    # Price should be numeric (stripped $)
    assert exported_df["price"].dtype.kind in "fc" or exported_df["price"].iloc[0] == 100.5
    # Discount should be numeric (stripped %)
    assert exported_df["discount"].dtype.kind in "fc" or exported_df["discount"].iloc[0] == 10.0


def test_export_cleaned_xlsx(client: TestClient):
    """Test downloading cleaned dataset as Excel XLSX."""
    csv_content = (
        "item,score\n"
        "Alpha,95.5\n"
        "Beta,88.0\n"
    )
    files = {"file": ("simple.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/export?format=xlsx")
    assert res.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res.headers["content-type"]
    assert f"cleaned_{dataset_id[:8]}.xlsx" in res.headers["content-disposition"]

    # Parse Excel bytes
    excel_df = pd.read_excel(io.BytesIO(res.content), sheet_name="Cleaned Data")
    assert len(excel_df) == 2
    assert "item" in excel_df.columns
    assert "score" in excel_df.columns


def test_export_invalid_format(client: TestClient):
    """Test 422/400 validation error on invalid export format."""
    csv_content = "a,b\n1,2\n"
    files = {"file": ("simple.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/export?format=parquet")
    # FastAPI Literal query validation returns 422
    assert res.status_code == 422


def test_export_not_found(client: TestClient):
    """Test 404 response for non-existent dataset."""
    res = client.get("/dataset/non_existent_id/export?format=csv")
    assert res.status_code == 404
