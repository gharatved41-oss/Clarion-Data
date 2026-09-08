import pytest
import pandas as pd
from fastapi.testclient import TestClient
from main import app
from services.supabase_service import SupabaseService

client = TestClient(app)


def test_sanitize_column_name():
    assert SupabaseService.sanitize_column_name("Length of Stay") == "length_of_stay"
    assert SupabaseService.sanitize_column_name("Annual Revenue ($)") == "annual_revenue"
    assert SupabaseService.sanitize_column_name("1st_quarter") == "col_1st_quarter"
    assert SupabaseService.sanitize_column_name("   Age   ") == "age"
    assert SupabaseService.sanitize_column_name("Customer-ID#") == "customer_id"


def test_map_dtype_to_postgres():
    assert SupabaseService.map_dtype_to_postgres("int64") == "BIGINT"
    assert SupabaseService.map_dtype_to_postgres("float64") == "DOUBLE PRECISION"
    assert SupabaseService.map_dtype_to_postgres("bool") == "BOOLEAN"
    assert SupabaseService.map_dtype_to_postgres("datetime64[ns]") == "TIMESTAMPTZ"
    assert SupabaseService.map_dtype_to_postgres("object") == "TEXT"


def test_generate_sql_schema():
    df = pd.DataFrame({
        "Patient ID": [1, 2],
        "Age": [45, 60],
        "Satisfaction": [4.5, 3.8],
        "Discharged": [True, False]
    })
    sql = SupabaseService.generate_sql_schema(df, "patient_records")
    assert "CREATE TABLE IF NOT EXISTS public.patient_records" in sql
    assert "patient_id BIGINT" in sql
    assert "age BIGINT" in sql
    assert "satisfaction DOUBLE PRECISION" in sql
    assert "discharged BOOLEAN" in sql
    assert "id BIGSERIAL PRIMARY KEY" in sql


def test_prepare_dataframe_records():
    df = pd.DataFrame({
        "Patient Name": ["Alice", "Bob"],
        "Score": [10.5, float("nan")]
    })
    records, mapping = SupabaseService.prepare_dataframe_records(df)
    assert len(records) == 2
    assert records[0]["patient_name"] == "Alice"
    assert records[0]["score"] == 10.5
    assert records[1]["score"] is None  # NaN converted to None for JSON compatibility


def test_api_supabase_config():
    response = client.get("/supabase/config")
    assert response.status_code == 200
    data = response.json()
    assert "has_credentials" in data
    assert "supabase_url" in data


def test_api_supabase_verify_missing():
    response = client.post("/supabase/verify", json={"supabase_url": "", "supabase_key": ""})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False


def test_api_supabase_sql():
    response = client.get("/supabase/dataset/test-sales/sql?table_name=my_sales_data")
    assert response.status_code == 200
    data = response.json()
    assert data["table_name"] == "my_sales_data"
    assert "CREATE TABLE IF NOT EXISTS public.my_sales_data" in data["sql_schema"]
    assert data["rows_count"] > 0


def test_api_supabase_push_invalid_creds():
    response = client.post("/supabase/dataset/test-sales/push", json={
        "table_name": "test_table",
        "supabase_url": "https://invalid-project.supabase.co",
        "supabase_key": "invalid-key"
    })
    # Should gracefully return error status without crashing
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["error", "table_missing"]
