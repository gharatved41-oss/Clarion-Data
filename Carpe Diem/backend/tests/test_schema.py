"""Automated test suite for Version 2: Intelligent Automatic Column-Type Detection."""
import io
import uuid
import pandas as pd
import pytest
from fastapi.testclient import TestClient


def test_schema_unseen_healthcare_dataset(client: TestClient):
    """Test schema detection on an unseen healthcare dataset with diverse column types."""
    csv_data = (
        "patient_id,body_temp,admission_date,ward,physician_notes\n"
        "PAT001,37.2,2026-01-10,ICU,Patient presented with elevated heart rate and dizziness.\n"
        "PAT002,36.5,2026-01-11,General,Routine physical examination completed with normal findings.\n"
        "PAT003,38.9,2026-01-12,ICU,Acute bacterial infection suspected blood tests ordered immediately.\n"
        "PAT004,36.8,2026-01-13,Emergency,Mild contusion observed on right shoulder rest recommended.\n"
        "PAT005,37.0,2026-01-14,General,Follow up consultation scheduled after two weeks of medication.\n"
    )
    files = {"file": ("healthcare.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    schema_res = client.get(f"/dataset/{dataset_id}/schema")
    assert schema_res.status_code == 200
    data = schema_res.json()
    assert data["dataset_id"] == dataset_id
    assert len(data["columns"]) == 5

    type_map = {col["name"]: col["type"] for col in data["columns"]}
    assert type_map["patient_id"] == "identifier"
    assert type_map["body_temp"] == "numeric"
    assert type_map["admission_date"] == "datetime"
    assert type_map["ward"] == "categorical"
    assert type_map["physician_notes"] == "text"


def test_schema_numbers_as_strings_and_currencies(client: TestClient):
    """Test detection of numbers stored with currencies ($/₹), percentages, and dates with slashes."""
    csv_data = (
        "record_uuid,salary,bonus_rate,joining_date,department,task_overview\n"
        f"{uuid.uuid4()},'$75,000','10%',15/05/2021,Finance,Reconciled quarterly financial ledger and balance sheet statements.\n"
        f"{uuid.uuid4()},'$82,500','15%',20/06/2022,Engineering,Engineered high throughput distributed data processing pipeline.\n"
        f"{uuid.uuid4()},'$90,000','12%',10/01/2020,Marketing,Directed omnichannel brand outreach campaign achieving record user engagement.\n"
        f"{uuid.uuid4()},'$68,000','8%',05/11/2023,Finance,Audited internal expenditure accounts and implemented budget optimizations.\n"
    )
    files = {"file": ("payroll.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    schema_res = client.get(f"/dataset/{dataset_id}/schema")
    assert schema_res.status_code == 200
    data = schema_res.json()

    type_map = {col["name"]: col["type"] for col in data["columns"]}
    assert type_map["record_uuid"] == "identifier"
    assert type_map["salary"] == "numeric"
    assert type_map["bonus_rate"] == "numeric"
    assert type_map["joining_date"] == "datetime"
    assert type_map["department"] == "categorical"
    assert type_map["task_overview"] == "text"


def test_schema_sequential_integers_as_ids(client: TestClient):
    """Test sequential integer IDs are recognized as identifiers and measurements as numeric."""
    csv_data = (
        "id,revenue_inr,margin_pct,status\n"
        "1,15000 INR,25.5%,ACTIVE\n"
        "2,25000 INR,30.0%,PENDING\n"
        "3,42000 INR,18.2%,ACTIVE\n"
        "4,18500 INR,22.1%,INACTIVE\n"
        "5,31000 INR,28.4%,ACTIVE\n"
    )
    files = {"file": ("transactions.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    schema_res = client.get(f"/dataset/{dataset_id}/schema")
    assert schema_res.status_code == 200
    data = schema_res.json()

    type_map = {col["name"]: col["type"] for col in data["columns"]}
    assert type_map["id"] == "identifier"
    assert type_map["revenue_inr"] == "numeric"
    assert type_map["margin_pct"] == "numeric"
    assert type_map["status"] == "categorical"


def test_schema_not_found(client: TestClient):
    """Test GET /dataset/{id}/schema returns 404 for unknown IDs."""
    res = client.get("/dataset/non-existent-schema-id/schema")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

