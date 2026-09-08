"""Service for numerical correlation matrix calculation and relationship extraction."""
import logging
import math
import numpy as np
import pandas as pd
from fastapi import HTTPException, status

from app.schemas.dataset import (
    CorrelationPair,
    DatasetCorrelationResponse,
)
from app.services.cleaning_service import CleaningService
from app.services.schema_service import SchemaService

logger = logging.getLogger("app.services.correlation_service")


def _classify_relationship(r: float) -> tuple[str, str]:
    """Return (strength, direction) given a correlation coefficient."""
    abs_r = abs(r)
    if abs_r >= 0.80:
        strength = "Very Strong"
    elif abs_r >= 0.60:
        strength = "Strong"
    elif abs_r >= 0.40:
        strength = "Moderate"
    else:
        strength = "Weak"

    if r > 0.05:
        direction = "Positive"
    elif r < -0.05:
        direction = "Negative"
    else:
        direction = "None"

    return strength, direction


class CorrelationService:
    """Correlation matrix and association extraction engine."""

    @classmethod
    def compute_correlations(
        cls, dataset_id: str, method: str = "pearson"
    ) -> DatasetCorrelationResponse:
        """Compute pairwise correlations across numerical columns of cleaned dataset."""
        if method.lower() not in ("pearson", "spearman"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported correlation method '{method}'. Supported methods are: pearson, spearman."
            )

        df, _ = CleaningService.load_cleaned_dataset(dataset_id)
        schema_res = SchemaService.detect_schema(dataset_id)
        schema_map = {col.name: col.type for col in schema_res.columns}

        # Select only numeric columns (strictly excluding identifiers, dates, etc.)
        numeric_cols = [
            str(col) for col in df.columns
            if schema_map.get(str(col)) == "numeric"
        ]

        # Verify numerical dtype in dataframe
        valid_numeric_cols = []
        for col in numeric_cols:
            try:
                num_series = pd.to_numeric(df[col], errors="coerce")
                if num_series.dropna().count() >= 2:
                    df[col] = num_series
                    valid_numeric_cols.append(col)
            except Exception:
                pass

        if len(valid_numeric_cols) < 2:
            return DatasetCorrelationResponse(
                dataset_id=dataset_id,
                method=method.lower(),
                numeric_columns=valid_numeric_cols,
                matrix=[],
                strong_positive=[],
                strong_negative=[],
                important_pairs=[],
                message="Dataset has fewer than 2 valid numeric columns; correlation analysis cannot be computed."
            )

        # Compute correlation matrix
        corr_df = df[valid_numeric_cols].corr(method=method.lower())

        # Construct serializable matrix
        matrix: list[list[float | None]] = []
        for row_idx, r_col in enumerate(valid_numeric_cols):
            row_vals: list[float | None] = []
            for col_idx, c_col in enumerate(valid_numeric_cols):
                val = corr_df.loc[r_col, c_col]
                if pd.isna(val) or math.isnan(val) or math.isinf(val):
                    row_vals.append(None)
                else:
                    row_vals.append(round(float(val), 4))
            matrix.append(row_vals)

        # Extract unique variable pairs (upper triangle excluding diagonal)
        pairs: list[CorrelationPair] = []
        strong_pos: list[CorrelationPair] = []
        strong_neg: list[CorrelationPair] = []

        for i in range(len(valid_numeric_cols)):
            for j in range(i + 1, len(valid_numeric_cols)):
                col1 = valid_numeric_cols[i]
                col2 = valid_numeric_cols[j]
                val = corr_df.loc[col1, col2]

                if pd.isna(val) or math.isnan(val) or math.isinf(val):
                    continue

                r = round(float(val), 4)
                strength, direction = _classify_relationship(r)
                pair = CorrelationPair(
                    var1=col1,
                    var2=col2,
                    correlation=r,
                    strength=strength,
                    direction=direction,
                )
                pairs.append(pair)

                if r >= 0.60:
                    strong_pos.append(pair)
                elif r <= -0.60:
                    strong_neg.append(pair)

        # Sort pairs
        strong_pos.sort(key=lambda p: p.correlation, reverse=True)
        strong_neg.sort(key=lambda p: p.correlation)
        # Important pairs sorted by absolute correlation magnitude
        important_pairs = sorted(pairs, key=lambda p: abs(p.correlation), reverse=True)

        return DatasetCorrelationResponse(
            dataset_id=dataset_id,
            method=method.lower(),
            numeric_columns=valid_numeric_cols,
            matrix=matrix,
            strong_positive=strong_pos,
            strong_negative=strong_neg,
            important_pairs=important_pairs,
        )
