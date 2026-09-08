import pytest
from fastapi.testclient import TestClient
from main import app
from services.file_ops_service import FileOpsService

client = TestClient(app)

def test_chat_general_greeting():
    response = client.post("/chat/message", json={"message": "Hello, how can you help me?"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["intent"] in ["general_chat", "dataset_analysis"]

def test_chat_dataset_missing_values():
    response = client.post("/chat/message", json={
        "message": "Which column has the most missing values?",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "missing" in data["message"].lower()

def test_chat_dataset_column_stats():
    response = client.post("/chat/message", json={
        "message": "What is the average revenue?",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert "revenue" in data["message"].lower()
    assert "mean" in data["message"].lower() or "average" in data["message"].lower()

def test_chat_dataset_correlations():
    response = client.post("/chat/message", json={
        "message": "Which variables are strongly correlated?",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert "correlation" in data["message"].lower()

def test_chat_dataset_outliers():
    response = client.post("/chat/message", json={
        "message": "Find unusual records or outliers",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert "outlier" in data["message"].lower()

def test_chat_dataset_top_records():
    response = client.post("/chat/message", json={
        "message": "Show top 5 records by revenue",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert "top" in data["message"].lower()
    assert "revenue" in data["message"].lower()

def test_chat_chart_recommendation():
    response = client.post("/chat/message", json={
        "message": "Show a graph of sales by month",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("intent") == "chart_request"
    assert "chart" in data
    assert data["chart"] is not None
    assert "type" in data["chart"]
    assert "data" in data["chart"]

def test_chat_report_generation():
    response = client.post("/chat/message", json={
        "message": "Generate a full report for this dataset",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("intent") == "report_generation"
    assert "report" in data["message"].lower()

def test_chat_project_qa():
    response = client.post("/chat/message", json={
        "message": "Explain how the upload API works"
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("intent") == "project_qa"
    assert "upload" in data["message"].lower()

def test_chat_project_files_endpoint():
    response = client.get("/chat/project-files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert len(data["files"]) > 5

def test_file_ops_security_blocks_traversal():
    assert FileOpsService._resolve_safe_path("../secret.txt") is None
    assert FileOpsService._resolve_safe_path("..\\..\\windows\\system32") is None
    assert FileOpsService._resolve_safe_path(".env") is None

def test_controlled_file_edit_workflow():
    # 1. Propose an edit
    proposal = FileOpsService.propose_edit(
        rel_path="README.md",
        new_content="# Test Content for Proposal Verification",
        summary="Test edit proposal verification"
    )
    assert "proposal_id" in proposal
    assert proposal["status"] == "pending_user_approval"
    p_id = proposal["proposal_id"]

    # 2. Cancel proposal
    cancel_res = client.post("/chat/cancel-edit", json={"proposal_id": p_id})
    assert cancel_res.status_code == 200

    # 3. Cancel again should fail
    cancel_res2 = client.post("/chat/cancel-edit", json={"proposal_id": p_id})
    assert cancel_res2.status_code == 400

def test_chat_key_findings():
    response = client.post("/chat/message", json={
        "message": "What are the key findings?",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "key_insights"
    assert "Key Findings" in data["message"]
    assert "System" in data["message"] or "nominal" in data["message"]

def test_chat_summarize_dataset():
    response = client.post("/chat/message", json={
        "message": "Summarize this dataset",
        "dataset_id": "test-sales"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "dataset_summary"
    assert "Executive Dataset Summary" in data["message"]
    assert "Profile" in data["message"] or "records" in data["message"]

