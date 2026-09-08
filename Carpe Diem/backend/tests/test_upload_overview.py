"""Automated test suite for Version 1: Dataset Upload and Overview."""
import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient


def test_upload_normal_csv_and_overview(client: TestClient):
    """Test uploading a standard CSV file and retrieving its overview."""
    csv_content = "id,name,age,score\n1,Alice,25,88.5\n2,Bob,30,92.0\n3,Charlie,35,79.5\n"
    files = {"file": ("students.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}

    upload_res = client.post("/upload", files=files)
    assert upload_res.status_code == 201
    data = upload_res.json()
    assert "dataset_id" in data
    assert data["filename"] == "students.csv"
    assert data["rows"] == 3
    assert data["columns"] == 4
    assert data["message"] == "Dataset uploaded successfully"

    dataset_id = data["dataset_id"]

    # Overview endpoint test
    overview_res = client.get(f"/dataset/{dataset_id}/overview")
    assert overview_res.status_code == 200
    ov_data = overview_res.json()
    assert ov_data["dataset_id"] == dataset_id
    assert ov_data["filename"] == "students.csv"
    assert ov_data["rows"] == 3
    assert ov_data["columns"] == 4
    assert ov_data["column_names"] == ["id", "name", "age", "score"]
    assert ov_data["file_type"] == ".csv"
    assert ov_data["missing_values"] == 0
    assert ov_data["duplicate_rows"] == 0
    assert ov_data["memory_usage_bytes"] > 0


def test_upload_normal_xlsx(client: TestClient):
    """Test uploading a standard XLSX file and verifying overview."""
    df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard"],
        "price": [1200.50, 25.00, 75.00],
        "in_stock": [True, True, False]
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)

    files = {"file": ("catalog.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/upload", files=files)
    assert res.status_code == 201
    data = res.json()
    assert data["filename"] == "catalog.xlsx"
    assert data["rows"] == 3
    assert data["columns"] == 3

    dataset_id = data["dataset_id"]
    ov_res = client.get(f"/dataset/{dataset_id}/overview")
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert ov_data["file_type"] == ".xlsx"
    assert ov_data["column_names"] == ["product", "price", "in_stock"]


def test_dataset_with_missing_and_duplicates(client: TestClient):
    """Test uploading a dataset with missing values and duplicate rows."""
    csv_content = (
        "customer_id,city,spend\n"
        "101,Mumbai,500\n"
        "102,,1200\n"
        "101,Mumbai,500\n"  # duplicate row
        "103,Delhi,\n"     # missing spend
        "104,Bangalore,750\n"
    )
    files = {"file": ("customers.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    upload_res = client.post("/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    ov_res = client.get(f"/dataset/{dataset_id}/overview")
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert ov_data["rows"] == 5
    assert ov_data["columns"] == 3
    assert ov_data["missing_values"] == 2  # one missing city, one missing spend
    assert ov_data["duplicate_rows"] == 1  # 1 duplicate row


def test_reject_unsupported_file_format(client: TestClient):
    """Test rejecting files with unsupported extensions (e.g. .txt, .json)."""
    files = {"file": ("notes.txt", io.BytesIO(b"some notes here"), "text/plain")}
    res = client.post("/upload", files=files)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]


def test_reject_empty_file(client: TestClient):
    """Test uploading an empty (0 bytes) file returns 400 Bad Request."""
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    res = client.post("/upload", files=files)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_reject_csv_with_no_rows(client: TestClient):
    """Test uploading a CSV with header only returns 400 Bad Request."""
    files = {"file": ("header_only.csv", io.BytesIO(b"col1,col2\n"), "text/csv")}
    res = client.post("/upload", files=files)
    assert res.status_code == 400
    assert "no rows" in res.json()["detail"].lower()


def test_overview_not_found(client: TestClient):
    """Test GET /dataset/{id}/overview returns 404 for unknown dataset IDs."""
    res = client.get("/dataset/non-existent-uuid-12345/overview")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

