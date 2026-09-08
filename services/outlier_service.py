"""Service for outlier and anomaly detection using IQR, Z-Score, and Isolation Forest."""
import logging
import math
import numpy as np
import pandas as pd
from fastapi import HTTPException, status
from sklearn.ensemble import IsolationForest

from app.schemas.dataset import (
    ColumnOutlierIQR,
    ColumnOutlierZScore,
    ColumnOutlierIsoForest,
    ColumnOutliersResult,
    OutlierSample,
    OutlierSummary,
    DatasetOutlierResponse,
)
from app.services.cleaning_service import CleaningService
from app.services.schema_service import SchemaService

logger = logging.getLogger("app.services.outlier_service")


def _safe_float(val) -> float | None:
    """Convert scalar to float, mapping NaN/Inf to None."""
    if val is None or pd.isna(val):
        return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 4)
    except (ValueError, TypeError):
        return None


class OutlierService:
    """Multi-method outlier and anomaly detection engine."""

    @classmethod
    def detect_outliers(
        cls,
        dataset_id: str,
        method: str = "all",
        z_threshold: float = 3.0,
        iso_contamination: float = 0.05
    ) -> DatasetOutlierResponse:
        """Execute outlier detection on cleaned dataset using specified method(s)."""
        method_norm = method.lower().strip()
        valid_methods = {"all", "iqr", "zscore", "isolation_forest"}
        if method_norm not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported outlier method '{method}'. Allowed methods: {', '.join(sorted(valid_methods))}."
            )

        df, _ = CleaningService.load_cleaned_dataset(dataset_id)
        schema_res = SchemaService.detect_schema(dataset_id)
        schema_map = {col.name: col.type for col in schema_res.columns}

        # Filter strictly to numeric columns
        numeric_cols = [
            str(col) for col in df.columns
            if schema_map.get(str(col)) == "numeric"
        ]

        total_rows = int(len(df))
        column_results: dict[str, ColumnOutliersResult] = {}
        all_affected_row_indices: set[int] = set()
        total_outlier_points = 0
        cols_with_outliers_set: set[str] = set()

        # Prepare numeric DataFrame for isolation forest
        numeric_df_valid = pd.DataFrame()

        for col in numeric_cols:
            num_series = pd.to_numeric(df[col], errors="coerce")
            valid = num_series.dropna()
            count = len(valid)

            if count < 4:
                continue

            numeric_df_valid[col] = num_series.fillna(valid.median() if count > 0 else 0)

            iqr_res: ColumnOutlierIQR | None = None
            zscore_res: ColumnOutlierZScore | None = None

            # 1. IQR Detection
            if method_norm in ("all", "iqr"):
                q1 = float(valid.quantile(0.25))
                q3 = float(valid.quantile(0.75))
                iqr = q3 - q1
                lower_bound = q1 - (1.5 * iqr)
                upper_bound = q3 + (1.5 * iqr)

                is_iqr_outlier = (num_series < lower_bound) | (num_series > upper_bound)
                affected_iqr = num_series[is_iqr_outlier].index.tolist()
                outlier_count = len(affected_iqr)

                sample_outliers = [
                    OutlierSample(row_index=int(idx), value=_safe_float(num_series.loc[idx]))
                    for idx in affected_iqr[:15]
                ]

                iqr_res = ColumnOutlierIQR(
                    q1=_safe_float(q1) or 0.0,
                    q3=_safe_float(q3) or 0.0,
                    iqr=_safe_float(iqr) or 0.0,
                    lower_bound=_safe_float(lower_bound) or 0.0,
                    upper_bound=_safe_float(upper_bound) or 0.0,
                    outlier_count=outlier_count,
                    outlier_percentage=round((outlier_count / count) * 100.0, 2) if count > 0 else 0.0,
                    sample_outliers=sample_outliers,
                    affected_rows=[int(i) for i in affected_iqr]
                )

                if outlier_count > 0:
                    cols_with_outliers_set.add(col)
                    total_outlier_points += outlier_count
                    all_affected_row_indices.update(affected_iqr)

            # 2. Z-Score Detection
            if method_norm in ("all", "zscore"):
                mean_val = float(valid.mean())
                std_val = float(valid.std())

                if std_val > 0:
                    z_scores = (num_series - mean_val) / std_val
                    is_z_outlier = z_scores.abs() > z_threshold
                    affected_z = num_series[is_z_outlier].index.tolist()
                    outlier_count = len(affected_z)
                    lower_bound = mean_val - (z_threshold * std_val)
                    upper_bound = mean_val + (z_threshold * std_val)
                else:
                    affected_z = []
                    outlier_count = 0
                    lower_bound = mean_val
                    upper_bound = mean_val

                sample_outliers = [
                    OutlierSample(row_index=int(idx), value=_safe_float(num_series.loc[idx]))
                    for idx in affected_z[:15]
                ]

                zscore_res = ColumnOutlierZScore(
                    mean=_safe_float(mean_val) or 0.0,
                    std=_safe_float(std_val) or 0.0,
                    threshold=float(z_threshold),
                    lower_bound=_safe_float(lower_bound) or 0.0,
                    upper_bound=_safe_float(upper_bound) or 0.0,
                    outlier_count=outlier_count,
                    outlier_percentage=round((outlier_count / count) * 100.0, 2) if count > 0 else 0.0,
                    sample_outliers=sample_outliers,
                    affected_rows=[int(i) for i in affected_z]
                )

                if method_norm == "zscore" and outlier_count > 0:
                    cols_with_outliers_set.add(col)
                    total_outlier_points += outlier_count
                    all_affected_row_indices.update(affected_z)

            column_results[col] = ColumnOutliersResult(
                column=col,
                iqr=iqr_res,
                z_score=zscore_res
            )

        # 3. Isolation Forest (Multivariate Anomaly Detection)
        iso_res: ColumnOutlierIsoForest | None = None
        if method_norm in ("all", "isolation_forest") and len(numeric_df_valid.columns) > 0 and len(numeric_df_valid) >= 5:
            try:
                clf = IsolationForest(
                    contamination=iso_contamination,
                    random_state=42,
                    n_estimators=100
                )
                preds = clf.fit_predict(numeric_df_valid)
                anomalous_indices = [int(i) for i in np.where(preds == -1)[0]]
                iso_count = len(anomalous_indices)
                iso_pct = round((iso_count / total_rows) * 100.0, 2) if total_rows > 0 else 0.0

                iso_res = ColumnOutlierIsoForest(
                    contamination=iso_contamination,
                    outlier_count=iso_count,
                    outlier_percentage=iso_pct,
                    affected_rows=anomalous_indices
                )

                if method_norm == "isolation_forest":
                    all_affected_row_indices = set(anomalous_indices)
                    total_outlier_points = iso_count
            except Exception as err:
                logger.warning(f"Isolation Forest execution failed: {err}")

        rows_with_outliers = len(all_affected_row_indices)
        pct_rows_with_outliers = round((rows_with_outliers / total_rows) * 100.0, 2) if total_rows > 0 else 0.0

        summary = OutlierSummary(
            total_outlier_data_points=total_outlier_points,
            rows_with_outliers_count=rows_with_outliers,
            rows_with_outliers_percentage=pct_rows_with_outliers,
            columns_with_outliers=sorted(list(cols_with_outliers_set))
        )

        return DatasetOutlierResponse(
            dataset_id=dataset_id,
            method=method_norm,
            summary=summary,
            columns=column_results,
            isolation_forest=iso_res
        )
