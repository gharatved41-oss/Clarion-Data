"""
Unified Person 1 API Router:
Dataset Upload, Structural Overview, Schema Detection, Data Cleaning & Audit,
Statistical Analysis, Correlations, Outliers, Visualizations, Insights, and Export.
"""
from typing import Literal
from fastapi import APIRouter, File, Query, UploadFile, status, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.dataset import (
    UploadResponse,
    DatasetOverviewResponse,
    DatasetSchemaResponse,
    CleaningReportResponse,
    DatasetAnalysisResponse,
    DatasetCorrelationResponse,
    DatasetOutlierResponse,
    DatasetVisualizationsResponse,
    DatasetInsightsResponse,
)
from app.schemas.health import HealthResponse
from app.services.upload_service import UploadService
from app.services.schema_service import SchemaService
from app.services.cleaning_service import CleaningService
from app.services.analysis_service import AnalysisService
from app.services.correlation_service import CorrelationService
from app.services.outlier_service import OutlierService
from app.services.visualization_service import VisualizationService
from app.services.insight_service import InsightService
from app.services.export_service import ExportService
from services.dataset_store import dataset_store

router = APIRouter(tags=["Person 1 - Analytical Base APIs"])


@router.get("/health", response_model=HealthResponse, summary="Perform system health check")
async def get_health() -> HealthResponse:
    """Return health status of the API."""
    return HealthResponse(status="ok")


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload dataset file (CSV, XLSX, XLS)"
)
@router.post(
    "/dataset/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
async def upload_dataset(file: UploadFile = File(...)) -> UploadResponse:
    """Accept a multipart/form-data dataset file, validate, store safely, and register metadata."""
    res = await UploadService.upload_dataset(file)
    try:
        raw_df, _ = UploadService.load_raw_dataset(res.dataset_id)
        dataset_store._datasets[res.dataset_id] = raw_df
        dataset_store._metadata[res.dataset_id] = {
            "name": res.filename,
            "rows": res.rows,
            "columns": res.columns
        }
    except Exception:
        pass
    return res


@router.get(
    "/dataset/{id}/overview",
    response_model=DatasetOverviewResponse,
    summary="Retrieve dataset structural overview, sample rows, and summary metrics"
)
async def get_dataset_overview(id: str) -> DatasetOverviewResponse:
    """Return rows, columns, names, missing values, duplicates, memory usage, and preview rows for a dataset ID."""
    return UploadService.get_dataset_overview(id)


@router.get(
    "/dataset/{id}/schema",
    response_model=DatasetSchemaResponse,
    summary="Automatically detect intelligent column types and confidence scores"
)
async def get_dataset_schema(id: str) -> DatasetSchemaResponse:
    """Analyze dataset columns and classify each as numeric, categorical, datetime, text, or identifier."""
    return SchemaService.detect_schema(id)


@router.get(
    "/dataset/{id}/cleaning-report",
    response_model=CleaningReportResponse,
    summary="Execute automated dataset cleaning and return comprehensive audit report"
)
async def get_cleaning_report(id: str, reclean: bool = False) -> CleaningReportResponse:
    """Perform non-destructive cleaning (missing values, duplicates, numbers/currencies/percentages, dates, casing) and return transformation audit trail."""
    return CleaningService.clean_dataset(id, force_reclean=reclean)


@router.get(
    "/dataset/{id}/analysis",
    response_model=DatasetAnalysisResponse,
    summary="Retrieve type-tailored descriptive statistics and distribution metrics"
)
async def get_dataset_analysis(id: str) -> DatasetAnalysisResponse:
    """Calculate mean, median, std, min, max, quartiles, and histogram bins for numeric columns; value frequencies for categorical; date ranges; and text stats."""
    return AnalysisService.analyze_dataset(id)


@router.get(
    "/dataset/{id}/correlations",
    response_model=DatasetCorrelationResponse,
    summary="Calculate numerical correlation matrix and extract significant associations"
)
async def get_dataset_correlations(
    id: str,
    method: Literal["pearson", "spearman"] = Query(
        "pearson",
        description="Correlation method: 'pearson' (linear) or 'spearman' (monotonic rank)"
    )
) -> DatasetCorrelationResponse:
    """Compute pairwise correlations across numeric columns and identify strong positive and negative relationships."""
    return CorrelationService.compute_correlations(id, method=method)


@router.get(
    "/dataset/{id}/outliers",
    response_model=DatasetOutlierResponse,
    summary="Detect dataset outliers and anomalies using IQR, Z-Score, and Isolation Forest"
)
async def get_dataset_outliers(
    id: str,
    method: Literal["all", "iqr", "zscore", "isolation_forest"] = Query(
        "all",
        description="Detection method: 'all', 'iqr', 'zscore', or 'isolation_forest'"
    ),
    z_threshold: float = Query(
        3.0,
        ge=1.0,
        le=10.0,
        description="Z-Score standard deviation threshold"
    ),
    contamination: float = Query(
        0.05,
        ge=0.01,
        le=0.5,
        description="Isolation Forest expected anomaly contamination proportion"
    )
) -> DatasetOutlierResponse:
    """Detect anomalies and outliers across numerical columns, reporting bounds, affected rows, and frequencies."""
    return OutlierService.detect_outliers(
        id,
        method=method,
        z_threshold=z_threshold,
        iso_contamination=contamination
    )


@router.get(
    "/dataset/{id}/visualizations",
    response_model=DatasetVisualizationsResponse,
    summary="Generate recommended chart visual specifications for cleaned data"
)
async def get_dataset_visualizations(id: str) -> DatasetVisualizationsResponse:
    """Analyze the cleaned dataset and recommend tailored charts (bar, line, scatter, donut, boxplot)."""
    return VisualizationService.generate_visualizations(id)


@router.get(
    "/dataset/{id}/insights",
    response_model=DatasetInsightsResponse,
    summary="Synthesize executive natural language findings and compute data quality score"
)
async def get_dataset_insights(id: str) -> DatasetInsightsResponse:
    """Evaluate overall dataset cleanliness (0-100 score) and extract automated narrative findings and recommendations."""
    return InsightService.generate_insights(id)


@router.get(
    "/dataset/{id}/export",
    summary="Download cleaned dataset in CSV or XLSX format"
)
async def export_cleaned_dataset(
    id: str,
    format: Literal["csv", "xlsx"] = Query(
        "csv",
        description="Export format: 'csv' or 'xlsx'"
    )
) -> StreamingResponse:
    """Stream download of the cleaned and normalized dataset."""
    return ExportService.export_dataset(id, format=format)
