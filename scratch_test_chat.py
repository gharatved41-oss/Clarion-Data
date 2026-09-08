import os
import pytest
from services.dataset_store import dataset_store
from services.gemini_chat_service import GeminiChatService

def test_graph_age_and_cost():
    # Use real dataset 59eb72de-8363-46a9-b44e-9abf7d4d1109
    ds_id = "59eb72de-8363-46a9-b44e-9abf7d4d1109"
    res = GeminiChatService.process_chat("show me graph for age and cost", dataset_id=ds_id)
    print("RES INTENT:", res.get("intent"))
    print("CHART:", res.get("chart", {}).get("type"), res.get("chart", {}).get("title"))
    print("MSG:", res.get("message")[:200])

if __name__ == "__main__":
    test_graph_age_and_cost()
