"""
Supabase Integration API Router
Endpoints to verify credentials, generate PostgreSQL table DDL, and push dataset rows to Supabase.
"""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

from services.supabase_service import SupabaseService

router = APIRouter(prefix="/supabase", tags=["Supabase Cloud Database Sync"])


class SupabaseVerifyRequest(BaseModel):
    supabase_url: Optional[str] = Field(None, description="Supabase project URL, e.g. https://xyz.supabase.co")
    supabase_key: Optional[str] = Field(None, description="Supabase anon or service_role key")


class SupabasePushRequest(BaseModel):
    table_name: Optional[str] = Field(None, description="Target table name in Supabase")
    supabase_url: Optional[str] = Field(None, description="Optional override for Supabase project URL")
    supabase_key: Optional[str] = Field(None, description="Optional override for Supabase API key")
    use_cleaned: bool = Field(True, description="Whether to push cleaned dataset (default True) or raw")
    batch_size: int = Field(500, ge=50, le=2000, description="Records per batch insert")


@router.get("/config", summary="Get current Supabase environment configuration status")
async def get_supabase_config():
    """Returns whether Supabase credentials are pre-configured in environment variables."""
    return SupabaseService.get_default_credentials()


@router.post("/verify", summary="Verify Supabase URL and API Key connectivity")
async def verify_supabase_connection(req: Optional[SupabaseVerifyRequest] = None):
    """Test connection to a Supabase project instance using PostgREST authentication."""
    url = req.supabase_url if req else None
    key = req.supabase_key if req else None
    result = await SupabaseService.test_connection(url, key)
    return result


@router.get("/dataset/{dataset_id}/sql", summary="Generate PostgreSQL DDL for dataset")
async def get_dataset_sql_schema(dataset_id: str, table_name: Optional[str] = None):
    """Generate PostgreSQL CREATE TABLE DDL matching dataset columns and inferred data types."""
    from services.dataset_store import dataset_store
    df = dataset_store.get_dataset(dataset_id)
    if df is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{dataset_id}' not found."
        )

    t_name = table_name or f"clarion_{SupabaseService.sanitize_column_name(dataset_id)}"
    sql = SupabaseService.generate_sql_schema(df, t_name)
    return {
        "dataset_id": dataset_id,
        "table_name": SupabaseService.sanitize_column_name(t_name),
        "columns_count": len(df.columns),
        "rows_count": len(df),
        "sql_schema": sql
    }


@router.post("/dataset/{dataset_id}/push", summary="Push dataset records to Supabase PostgreSQL table")
async def push_dataset_to_supabase(dataset_id: str, req: SupabasePushRequest):
    """
    Batches and pushes all records from the specified dataset to a Supabase table.
    """
    try:
        res = await SupabaseService.push_dataset(
            dataset_id=dataset_id,
            table_name=req.table_name,
            supabase_url=req.supabase_url,
            supabase_key=req.supabase_key,
            use_cleaned=req.use_cleaned,
            batch_size=req.batch_size
        )
        return res
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push dataset to Supabase: {str(e)}"
        )
