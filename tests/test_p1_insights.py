"""Automated test suite for Version 6.0: Executive Insights & Data Quality Scoring (GET /dataset/{id}/insights)."""
import io
import pytest
from fastapi.testclient import TestClient


def test_insights_generation_and_quality_score(client: TestClient):
    """Test full insights calculation, quality scoring breakdown, findings, and recommendations."""
    csv_content = (
        "id,product,category,revenue,quantity\n"
        "1,Laptop,Electronics,1200.0,5\n"
        "2,Mouse,Electronics,25.0,20\n"
        "3,Desk,Furniture,350.0,2\n"
        "4,Chair,Furniture,150.0,6\n"
        "5,Monitor,Electronics,300.0,4\n"
        "6,Cable,Electronics,15.0,50\n"
        "7,Lamp,Furniture,45.0,10\n"
        "1,Laptop,Electronics,1200.0,5\n"  # duplicate row
    )
    files = {"file": ("insights_test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/insights")
    assert res.status_code == 200
    data = res.json()

    assert data["dataset_id"] == dataset_id
    assert "quality_score" in data
    quality = data["quality_score"]
    assert 0 <= quality["overall_score"] <= 100
    assert quality["grade"] in ["A+", "A", "B", "C", "D", "F"]
    assert 0 <= quality["completeness_score"] <= 100
    assert 0 <= quality["uniqueness_score"] <= 100
    assert 0 <= quality["validity_score"] <= 100

    # Verify findings are present
    assert len(data["key_findings"]) > 0
    categories = [f["category"] for f in data["key_findings"]]
    assert "overview" in categories

    # Verify actionable recommendations are present
    assert len(data["actionable_recommendations"]) > 0
    # Duplicate recommendation should be present because row 8 is duplicate
    assert any("duplicate" in rec.lower() for rec in data["actionable_recommendations"])


def test_insights_not_found(client: TestClient):
    """Test 404 response for non-existent dataset."""
    res = client.get("/dataset/non_existent_id/insights")
    assert res.status_code == 404
