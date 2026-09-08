import pytest
from fastapi.testclient import TestClient
from main import app
from utils.test_datasets import generate_test_datasets

client = TestClient(app)

BENCHMARK_DATASET_IDS = [
    "test-sales",
    "test-payment",
    "test-marketing",
    "test-healthcare",
    "test-unseen_tabular",
    "test-no_dates",
    "test-insufficient_numerics",
    "test-missing_values",
    "test-outliers",
    "test-unsuitable_clustering",
    "test-unsuitable_prediction"
]

PERSON1_ENDPOINTS = [
    "/dataset/{id}/overview",
    "/dataset/{id}/schema",
    "/dataset/{id}/cleaning-report",
    "/dataset/{id}/analysis",
    "/dataset/{id}/correlations",
    "/dataset/{id}/outliers"
]

PERSON2_ENDPOINTS = [
    "/dataset/{id}/clusters",
    "/dataset/{id}/predictions",
    "/dataset/{id}/charts",
    "/dataset/{id}/chart-options",
    "/dataset/{id}/domain",
    "/dataset/{id}/payment-analytics",
    "/dataset/{id}/changes",
    "/dataset/{id}/summary",
    "/dataset/{id}/notifications",
    "/dataset/{id}/data-quality",
    "/dataset/{id}/dashboard"
]

@pytest.mark.parametrize("ds_id", BENCHMARK_DATASET_IDS)
@pytest.mark.parametrize("endpoint", PERSON1_ENDPOINTS + PERSON2_ENDPOINTS)
def test_all_endpoints_on_all_benchmark_datasets(ds_id, endpoint):
    url = endpoint.format(id=ds_id)
    response = client.get(url)
    assert response.status_code == 200, f"Endpoint {url} failed with status {response.status_code}: {response.text}"
    json_data = response.json()
    assert isinstance(json_data, dict), f"Endpoint {url} did not return a valid JSON object"

def test_file_upload_flow():
    csv_content = b"id,name,val1,val2\n1,Alpha,10.5,20.0\n2,Beta,15.2,30.0\n3,Gamma,12.0,25.0\n4,Delta,18.0,35.0\n5,Epsilon,22.0,40.0\n6,Zeta,19.0,38.0\n7,Eta,25.0,50.0\n8,Theta,30.0,60.0\n9,Iota,28.0,55.0\n10,Kappa,35.0,70.0\n"
    response = client.post(
        "/upload",
        files={"file": ("test_upload.csv", csv_content, "text/csv")}
    )
    assert response.status_code in (200, 201)
    res = response.json()
    assert "dataset_id" in res
    
    new_id = res["dataset_id"]
    dash_res = client.get(f"/dataset/{new_id}/dashboard")
    assert dash_res.status_code == 200

def test_xlsx_file_upload_flow():
    import os
    xlsx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_ecommerce_dirty.xlsx")
    if os.path.exists(xlsx_path):
        with open(xlsx_path, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("test_ecommerce_dirty.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        assert response.status_code in (200, 201)
        res = response.json()
        assert "dataset_id" in res
        new_id = res["dataset_id"]
        dash_res = client.get(f"/dataset/{new_id}/dashboard")
        assert dash_res.status_code == 200
        overview_res = client.get(f"/dataset/{new_id}/overview")
        assert overview_res.status_code == 200
        assert overview_res.json().get("row_count") == 800

