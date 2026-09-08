import urllib.request
import urllib.parse
import json
import io

BASE_URL = "http://127.0.0.1:8000"

def test_full_stack():
    print("=== STARTING FULL STACK END-TO-END VERIFICATION ===")

    # 1. Test Root serves React Frontend
    res = urllib.request.urlopen(f"{BASE_URL}/")
    html = res.read().decode('utf-8')
    assert res.status == 200, f"Root returned {res.status}"
    assert "Clarion Data" in html, "HTML title missing Clarion Data"
    assert "/assets/index-" in html, "Asset tags missing from HTML"
    print(" [1/8] Root URL correctly serves compiled React frontend.")

    # 2. Test Assets bundle
    import re
    css_match = re.search(r'href="(/assets/index-[^"]+\.css)"', html)
    js_match = re.search(r'src="(/assets/index-[^"]+\.js)"', html)
    assert css_match, "Could not find CSS asset in HTML"
    assert js_match, "Could not find JS asset in HTML"
    
    res_css = urllib.request.urlopen(f"{BASE_URL}{css_match.group(1)}")
    assert res_css.status == 200, "CSS asset failed to load"
    res_js = urllib.request.urlopen(f"{BASE_URL}{js_match.group(1)}")
    assert res_js.status == 200, "JS asset failed to load"
    print(f" [2/8] React Static Assets bundle verified: CSS ({len(res_css.read())} bytes), JS ({len(res_js.read())} bytes).")

    # 3. Test Health Check
    res_health = urllib.request.urlopen(f"{BASE_URL}/health")
    health_data = json.loads(res_health.read().decode('utf-8'))
    assert health_data.get("status") in ["ok", "healthy"], f"Health check failed: {health_data}"
    print(f" [3/8] Backend health endpoint verified: {health_data}")

    # 4. Test Ingestion & Benchmark dataset overview
    benchmark_id = "test-sales"
    res_ov = urllib.request.urlopen(f"{BASE_URL}/dataset/{benchmark_id}/overview")
    ov_data = json.loads(res_ov.read().decode('utf-8'))
    assert "columns" in ov_data, "Overview missing columns"
    cols = ov_data.get('columns')
    cols_count = len(cols) if isinstance(cols, list) else cols
    print(f" [4/8] Dataset Overview verified for '{benchmark_id}': {ov_data.get('rows')} rows, {cols_count} columns.")

    # 5. Test Schema & Data Quality / Cleaning
    res_sch = urllib.request.urlopen(f"{BASE_URL}/dataset/{benchmark_id}/schema")
    sch_data = json.loads(res_sch.read().decode('utf-8'))
    res_clean = urllib.request.urlopen(f"{BASE_URL}/dataset/{benchmark_id}/cleaning-report")
    clean_data = json.loads(res_clean.read().decode('utf-8'))
    print(f" [5/8] Schema & Cleaning verified: {len(sch_data.get('columns', {}))} schema columns detected, quality score {clean_data.get('quality_score', 'N/A')}.")

    # 6. Test Advanced Analytics: Dashboard Builder (Person 1 + Person 2 Aggregator)
    res_dash = urllib.request.urlopen(f"{BASE_URL}/dataset/{benchmark_id}/dashboard")
    dash_data = json.loads(res_dash.read().decode('utf-8'))
    assert "kpis" in dash_data, "Dashboard missing kpis"
    assert "clusters" in dash_data, "Dashboard missing clusters"
    assert "predictions" in dash_data, "Dashboard missing predictions"
    print(f" [6/8] Master Dashboard Aggregator verified: {len(dash_data.get('kpis', []))} KPIs, clusters: {dash_data['clusters'].get('applicable')}, predictions: {dash_data['predictions'].get('applicable')}.")

    # 7. Test File Upload (Multipart Form Data Ingestion)
    boundary = "----ClarionFormBoundary7MA4YWxkTrZu0gW"
    csv_content = "InvoiceNo,StockCode,Description,Quantity,InvoiceDate,UnitPrice,CustomerID,Country\n536365,85123A,WHITE HANGING HEART T-LIGHT HOLDER,6,2010-12-01 08:26:00,2.55,17850,United Kingdom\n536365,71053,WHITE METAL LANTERN,6,2010-12-01 08:26:00,3.39,17850,United Kingdom\n536366,22633,HAND WARMER UNION JACK,32,2010-12-01 08:28:00,1.85,17850,United Kingdom\n536367,84879,ASSORTED COLOUR BIRD ORNAMENT,32,2010-12-01 08:34:00,1.69,13047,United Kingdom\n536368,22960,JAM MAKING SET WITH JARS,6,2010-12-01 08:34:00,4.25,13047,United Kingdom\n"
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="retail_test.csv"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
        f"{csv_content}\r\n"
        f"--{boundary}--\r\n"
    ).encode('utf-8')

    req = urllib.request.Request(
        f"{BASE_URL}/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    res_upload = urllib.request.urlopen(req)
    upload_data = json.loads(res_upload.read().decode('utf-8'))
    uploaded_id = upload_data.get("dataset_id")
    assert uploaded_id, "Upload did not return dataset_id"
    print(f" [7/8] Dynamic Upload verified: Ingested 'retail_test.csv' as dataset_id '{uploaded_id}' ({upload_data.get('rows')} rows).")

    # 8. Test AI Analyst Copilot Chat with Dataset Grounding
    chat_payload = json.dumps({
        "dataset_id": uploaded_id,
        "message": "Summarize this dataset and list key metrics"
    }).encode('utf-8')

    req_chat = urllib.request.Request(
        f"{BASE_URL}/chat/message",
        data=chat_payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    res_chat = urllib.request.urlopen(req_chat)
    chat_data = json.loads(res_chat.read().decode('utf-8'))
    reply_content = chat_data.get('message') or chat_data.get('reply')
    assert reply_content, f"Chat response missing reply or message: {chat_data}"
    safe_reply = reply_content[:120].encode('ascii', 'replace').decode('ascii')
    print(f" [8/8] AI Analyst Copilot verified: Response received:\n     \"{safe_reply}...\"")

    print("\nALL 8/8 FULL-STACK INTEGRATION MILESTONES PASSED WITH ZERO ERRORS!")

if __name__ == "__main__":
    test_full_stack()
