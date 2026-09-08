"""
Service bridging Person 1's complete data processing & core analysis pipeline
with Person 2's advanced intelligence, forecasting, clustering, and summary engines.
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from app.services.upload_service import UploadService
from app.services.schema_service import SchemaService
from app.services.cleaning_service import CleaningService
from app.services.analysis_service import AnalysisService
from app.services.correlation_service import CorrelationService
from app.services.outlier_service import OutlierService
from services.dataset_store import dataset_store
from utils.helpers import sanitize_for_json

logger = logging.getLogger("services.person1_service")


class Person1Service:
    """
    Implements analytical services corresponding to Person 1's responsibilities:
    Overview, Schema, Data Cleaning & Report, Statistical Analysis, Correlation Analysis, Outlier Detection.
    Delegates to the official Carpe Diem Person 1 core engines while preserving full
    backward-compatibility for Person 2 consumers (dashboard, notifications, chat, summaries).
    """

    @classmethod
    def get_overview(cls, dataset_id: str) -> Dict[str, Any]:
        """Fetch dataset structural overview with dual schema compatibility."""
        try:
            df = dataset_store.get_dataset(dataset_id)
            if df is None:
                return {"error": "Dataset not found"}

            ov = UploadService.get_dataset_overview(dataset_id)
            ov_dict = ov.model_dump()

            schema_res = SchemaService.detect_schema(dataset_id)
            type_counts = {"numeric": 0, "categorical": 0, "datetime": 0, "identifier": 0}
            for col in schema_res.columns:
                t = col.type
                if t in type_counts:
                    type_counts[t] += 1
                elif t == "text":
                    type_counts["categorical"] += 1

            ov_dict.update({
                "row_count": ov.rows,
                "column_count": ov.columns,
                "numeric_columns_count": type_counts["numeric"],
                "categorical_columns_count": type_counts["categorical"],
                "datetime_columns_count": type_counts["datetime"],
                "identifier_columns_count": type_counts["identifier"],
                "sample": ov_dict.get("preview_rows", [])
            })
            return sanitize_for_json(ov_dict)
        except Exception as exc:
            logger.error(f"Error in get_overview for {dataset_id}: {exc}")
            df = dataset_store.get_dataset(dataset_id)
            if df is None:
                return {"error": "Dataset not found"}
            sample_head = df.head(5).to_dict(orient="records")
            return sanitize_for_json({
                "dataset_id": dataset_id,
                "filename": f"{dataset_id}.csv",
                "rows": len(df),
                "row_count": len(df),
                "columns": len(df.columns),
                "column_count": len(df.columns),
                "column_names": [str(c) for c in df.columns],
                "file_type": ".csv",
                "missing_values": int(df.isna().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
                "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
                "preview_rows": sample_head,
                "sample": sample_head
            })

    @classmethod
    def get_schema(cls, dataset_id: str) -> Dict[str, Any]:
        """Fetch intelligent schema detection with dual compatibility."""
        try:
            df = dataset_store.get_dataset(dataset_id)
            if df is None:
                return {"error": "Dataset not found"}

            schema_res = SchemaService.detect_schema(dataset_id)
            res_dict = schema_res.model_dump()

            legacy_schema = []
            for col in schema_res.columns:
                legacy_schema.append({
                    "column_name": col.name,
                    "detected_type": col.type,
                    "raw_dtype": col.original_dtype,
                    "null_count": col.null_count,
                    "unique_count": col.unique_count
                })
            res_dict["schema"] = legacy_schema
            return sanitize_for_json(res_dict)
        except Exception as exc:
            logger.error(f"Error in get_schema for {dataset_id}: {exc}")
            return {"error": str(exc)}

    @classmethod
    def get_cleaning_report(cls, dataset_id: str, force_reclean: bool = False) -> Dict[str, Any]:
        """Execute automated cleaning and return comprehensive audit report."""
        try:
            df = dataset_store.get_dataset(dataset_id)
            if df is None:
                return {"error": "Dataset not found"}

            report_res = CleaningService.clean_dataset(dataset_id, force_reclean=force_reclean)
            rep_dict = report_res.model_dump()

            rep_dict.update({
                "total_rows": rep_dict["original_row_count"],
                "total_columns": rep_dict["original_column_count"],
                "total_missing_cells": rep_dict["missing_values_detected"],
                "duplicate_rows": rep_dict["duplicates_detected"]
            })
            return sanitize_for_json(rep_dict)
        except Exception as exc:
            logger.error(f"Error in get_cleaning_report for {dataset_id}: {exc}")
            return {"error": str(exc)}

    @classmethod
    def get_analysis(cls, dataset_id: str) -> Dict[str, Any]:
        """Retrieve type-tailored descriptive statistics and distribution metrics."""
        try:
            df = dataset_store.get_dataset(dataset_id)
            if df is None:
                return {"error": "Dataset not found"}

            analysis_res = AnalysisService.analyze_dataset(dataset_id)
            res_dict = analysis_res.model_dump()

            numeric_stats = {}
            for col, n_stat in (res_dict.get("numeric_analysis") or {}).items():
                numeric_stats[col] = {
                    "count": n_stat.get("count", 0),
                    "mean": n_stat.get("mean"),
                    "std": n_stat.get("std"),
                    "min": n_stat.get("min"),
                    "p25": n_stat.get("q1"),
                    "median": n_stat.get("median"),
                    "p75": n_stat.get("q3"),
                    "max": n_stat.get("max"),
                    "skewness": n_stat.get("skewness")
                }
            res_dict["numeric_stats"] = numeric_stats
            return sanitize_for_json(res_dict)
        except Exception as exc:
            logger.error(f"Error in get_analysis for {dataset_id}: {exc}")
            return {"error": str(exc)}

    @classmethod
    def get_correlations(cls, dataset_id: str, method: str = "pearson") -> Dict[str, Any]:
        """Compute numerical correlation matrix and extract significant associations."""
        try:
            df = dataset_store.get_dataset(dataset_id)
            if df is None:
                return {"error": "Dataset not found"}

            corr_res = CorrelationService.compute_correlations(dataset_id, method=method)
            res_dict = corr_res.model_dump()

            strong_corrs = []
            for p in (res_dict.get("important_pairs") or []):
                strong_corrs.append({
                    "feature_1": p["var1"],
                    "feature_2": p["var2"],
                    "correlation": p["correlation"],
                    "strength": f"{p['strength'].lower()} {p['direction'].lower()}"
                })
            res_dict["strong_correlations"] = strong_corrs
            return sanitize_for_json(res_dict)
        except Exception as exc:
            logger.error(f"Error in get_correlations for {dataset_id}: {exc}")
            return {"error": str(exc)}

    @classmethod
    def get_outliers(
        cls,
        dataset_id: str,
        method: str = "all",
        z_threshold: float = 3.0,
        contamination: float = 0.05
    ) -> Dict[str, Any]:
        """Detect dataset outliers using IQR, Z-Score, and Isolation Forest."""
        try:
            df = dataset_store.get_dataset(dataset_id)
            if df is None:
                return {"error": "Dataset not found"}

            outliers_res = OutlierService.detect_outliers(
                dataset_id,
                method=method,
                z_threshold=z_threshold,
                iso_contamination=contamination
            )
            res_dict = outliers_res.model_dump()

            summary = res_dict.get("summary", {})
            total_outliers = summary.get("total_outlier_data_points", 0)
            rows_pct = summary.get("rows_with_outliers_percentage", 0.0)

            outliers_by_col = {}
            for col, col_data in (res_dict.get("columns") or {}).items():
                iqr_info = col_data.get("iqr")
                if iqr_info and iqr_info.get("outlier_count", 0) > 0:
                    outliers_by_col[col] = {
                        "count": iqr_info["outlier_count"],
                        "lower_threshold": iqr_info["lower_bound"],
                        "upper_threshold": iqr_info["upper_bound"],
                        "sample_outlier_indices": iqr_info.get("affected_rows", [])[:10]
                    }
                elif col_data.get("z_score") and col_data["z_score"].get("outlier_count", 0) > 0:
                    z_info = col_data["z_score"]
                    outliers_by_col[col] = {
                        "count": z_info["outlier_count"],
                        "lower_threshold": z_info["lower_bound"],
                        "upper_threshold": z_info["upper_bound"],
                        "sample_outlier_indices": z_info.get("affected_rows", [])[:10]
                    }

            res_dict.update({
                "total_outliers_count": total_outliers,
                "outliers_percentage": rows_pct,
                "outliers_by_column": outliers_by_col
            })
            return sanitize_for_json(res_dict)
        except Exception as exc:
            logger.error(f"Error in get_outliers for {dataset_id}: {exc}")
            return {"error": str(exc)}

