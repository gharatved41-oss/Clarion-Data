"""Automated test suite for Version 6.0: Automated Chart Visualizations (GET /dataset/{id}/visualizations)."""
import io
import pytest
from fastapi.testclient import TestClient


def test_visualizations_generation(client: TestClient):
    """Test automated generation of chart specifications (donut, bar, line, scatter, boxplot)."""
    csv_content = (
        "id,date,category,price,units\n"
        "1,2024-01-15,Electronics,120.50,10\n"
        "2,2024-01-20,Furniture,450.00,2\n"
        "3,2024-02-10,Electronics,99.99,15\n"
        "4,2024-02-15,Clothing,45.00,30\n"
        "5,2024-03-01,Furniture,500.00,3\n"
        "6,2024-03-12,Clothing,60.00,25\n"
        "7,2024-04-05,Electronics,150.00,8\n"
        "8,2024-04-18,Clothing,55.00,20\n"
    )
    files = {"file": ("vis_test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/visualizations")
    assert res.status_code == 200
    data = res.json()

    assert data["dataset_id"] == dataset_id
    assert data["total_recommendations"] > 0
    assert len(data["charts"]) == data["total_recommendations"]

    chart_types = [chart["chart_type"] for chart in data["charts"]]
    assert "donut" in chart_types
    assert "bar" in chart_types
    assert "line" in chart_types
    assert "scatter" in chart_types
    assert "boxplot" in chart_types

    # Validate donut structure
    donut = next(c for c in data["charts"] if c["chart_type"] == "donut")
    assert len(donut["series"]) > 0
    assert len(donut["series"][0]["data"]) > 0
    assert donut["series"][0]["data"][0]["secondary_value"] is not None  # percentage

    # Validate boxplot structure
    boxplot = next(c for c in data["charts"] if c["chart_type"] == "boxplot")
    assert len(boxplot["series"][0]["data"]) == 5  # Min, Q1, Median, Q3, Max


def test_visualizations_edge_case_no_categorical(client: TestClient):
    """Test visualizations when dataset contains only numeric columns."""
    csv_content = (
        "x,y,z\n"
        "10,20,30\n"
        "15,25,35\n"
        "20,30,40\n"
        "25,35,45\n"
        "30,40,50\n"
    )
    files = {"file": ("no_cat.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    up_res = client.post("/upload", files=files)
    assert up_res.status_code == 201
    dataset_id = up_res.json()["dataset_id"]

    res = client.get(f"/dataset/{dataset_id}/visualizations")
    assert res.status_code == 200
    data = res.json()
    chart_types = [chart["chart_type"] for chart in data["charts"]]
    # Should contain scatter and boxplot, but neither donut nor categorical-bivariate bar
    assert "donut" not in chart_types
    assert "bar" not in chart_types
    assert "scatter" in chart_types
    assert "boxplot" in chart_types


def test_visualizations_not_found(client: TestClient):
    """Test 404 response for non-existent dataset."""
    res = client.get("/dataset/non_existent_id/visualizations")
    assert res.status_code == 404
