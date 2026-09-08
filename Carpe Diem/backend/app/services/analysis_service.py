"""Service for comprehensive, type-aware statistical analysis across dataset columns."""
import logging
import math
import numpy as np
import pandas as pd
from fastapi import HTTPException, status

from app.schemas.dataset import (
    DatasetAnalysisResponse,
    NumericStats,
    HistogramBin,
    CategoricalStats,
    CategoryFrequency,
    DateTimeStats,
    TextStats,
    IdentifierStats,
)
from app.services.cleaning_service import CleaningService
from app.services.schema_service import SchemaService

logger = logging.getLogger("app.services.analysis_service")


def _safe_float(val) -> float | None:
    """Convert numpy/pandas scalar to float, mapping NaN/Inf to None."""
    if val is None or pd.isna(val):
        return None
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 4)
    except (ValueError, TypeError):
        return None


class AnalysisService:
    """Statistical analysis engine providing tailored metrics per column type."""

    @classmethod
    def analyze_dataset(cls, dataset_id: str) -> DatasetAnalysisResponse:
        """Execute full statistical analysis on the cleaned dataset."""
        df, _ = CleaningService.load_cleaned_dataset(dataset_id)
        schema_res = SchemaService.detect_schema(dataset_id)
        schema_map = {col.name: col.type for col in schema_res.columns}

        total_rows = int(len(df))
        total_cols = int(len(df.columns))

        numeric_analysis: dict[str, NumericStats] = {}
        categorical_analysis: dict[str, CategoricalStats] = {}
        datetime_analysis: dict[str, DateTimeStats] = {}
        text_analysis: dict[str, TextStats] = {}
        identifier_analysis: dict[str, IdentifierStats] = {}

        for col in df.columns:
            col_str = str(col)
            col_type = schema_map.get(col_str, "text")
            series = df[col]

            if col_type == "numeric":
                numeric_analysis[col_str] = cls._analyze_numeric(series)
            elif col_type == "categorical":
                categorical_analysis[col_str] = cls._analyze_categorical(series)
            elif col_type == "datetime":
                datetime_analysis[col_str] = cls._analyze_datetime(series)
            elif col_type == "identifier":
                identifier_analysis[col_str] = cls._analyze_identifier(series)
            else:  # text
                text_analysis[col_str] = cls._analyze_text(series)

        return DatasetAnalysisResponse(
            dataset_id=dataset_id,
            total_rows=total_rows,
            total_columns=total_cols,
            numeric_analysis=numeric_analysis,
            categorical_analysis=categorical_analysis,
            datetime_analysis=datetime_analysis,
            text_analysis=text_analysis,
            identifier_analysis=identifier_analysis,
        )

    @staticmethod
    def _analyze_numeric(series: pd.Series) -> NumericStats:
        """Calculate descriptive metrics and histogram bins for numeric series."""
        # Ensure series is numeric
        num_s = pd.to_numeric(series, errors="coerce")
        valid = num_s.dropna()

        count = int(len(valid))
        null_count = int(num_s.isna().sum())

        if count == 0:
            return NumericStats(
                count=0,
                null_count=null_count,
            )

        mean_val = _safe_float(valid.mean())
        median_val = _safe_float(valid.median())
        min_val = _safe_float(valid.min())
        max_val = _safe_float(valid.max())
        std_val = _safe_float(valid.std()) if count > 1 else 0.0
        var_val = _safe_float(valid.var()) if count > 1 else 0.0

        skew_val = _safe_float(valid.skew()) if count > 2 else 0.0
        q1_val = _safe_float(valid.quantile(0.25))
        q3_val = _safe_float(valid.quantile(0.75))
        iqr_val = _safe_float(q3_val - q1_val) if q1_val is not None and q3_val is not None else None

        # Calculate histogram bins (up to 10 bins)
        histogram_bins: list[HistogramBin] = []
        if min_val is not None and max_val is not None and count > 1:
            if min_val == max_val:
                histogram_bins.append(HistogramBin(
                    bin_start=min_val,
                    bin_end=max_val,
                    count=count
                ))
            else:
                num_bins = min(10, max(3, int(np.ceil(np.sqrt(count)))))
                try:
                    counts, bin_edges = np.histogram(valid, bins=num_bins)
                    for i in range(len(counts)):
                        b_start = _safe_float(bin_edges[i]) or 0.0
                        b_end = _safe_float(bin_edges[i + 1]) or 0.0
                        histogram_bins.append(HistogramBin(
                            bin_start=b_start,
                            bin_end=b_end,
                            count=int(counts[i])
                        ))
                except Exception as err:
                    logger.warning(f"Failed to generate histogram bins: {err}")

        return NumericStats(
            count=count,
            null_count=null_count,
            mean=mean_val,
            median=median_val,
            min=min_val,
            max=max_val,
            std=std_val,
            variance=var_val,
            skewness=skew_val,
            q1=q1_val,
            q3=q3_val,
            iqr=iqr_val,
            histogram=histogram_bins,
        )

    @staticmethod
    def _analyze_categorical(series: pd.Series) -> CategoricalStats:
        """Calculate counts, frequencies, and percentages for categorical variables."""
        non_null = series.dropna().astype(str)
        count = int(len(non_null))
        null_count = int(series.isna().sum())
        unique_count = int(non_null.nunique())

        top_categories: list[CategoryFrequency] = []
        if count > 0:
            val_counts = non_null.value_counts().head(10)
            for cat, cnt in val_counts.items():
                pct = round((cnt / count) * 100.0, 2)
                top_categories.append(CategoryFrequency(
                    category=str(cat),
                    count=int(cnt),
                    percentage=pct
                ))

        return CategoricalStats(
            count=count,
            null_count=null_count,
            unique_count=unique_count,
            top_categories=top_categories,
        )

    @staticmethod
    def _analyze_datetime(series: pd.Series) -> DateTimeStats:
        """Calculate date boundaries, duration, and time distributions."""
        parsed = pd.to_datetime(series, errors="coerce")
        valid = parsed.dropna()

        count = int(len(valid))
        null_count = int(len(series) - count)

        if count == 0:
            return DateTimeStats(
                count=0,
                null_count=null_count,
            )

        min_dt = valid.min()
        max_dt = valid.max()
        range_days = int((max_dt - min_dt).total_seconds() // 86400) if min_dt and max_dt else 0

        # Yearly distribution
        yearly_counts = valid.dt.year.value_counts().to_dict()
        yearly_dist = {str(k): int(v) for k, v in sorted(yearly_counts.items())}

        # Monthly distribution (YYYY-MM)
        monthly_counts = valid.dt.to_period("M").astype(str).value_counts().to_dict()
        monthly_dist = {str(k): int(v) for k, v in sorted(monthly_counts.items())}

        return DateTimeStats(
            count=count,
            null_count=null_count,
            min_date=min_dt.strftime("%Y-%m-%d") if min_dt else None,
            max_date=max_dt.strftime("%Y-%m-%d") if max_dt else None,
            range_days=range_days,
            yearly_distribution=yearly_dist,
            monthly_distribution=monthly_dist,
        )

    @staticmethod
    def _analyze_text(series: pd.Series) -> TextStats:
        """Calculate length and word distributions for natural-language text fields."""
        non_null = series.dropna().astype(str)
        count = int(len(non_null))
        null_count = int(series.isna().sum())
        unique_count = int(non_null.nunique())

        if count == 0:
            return TextStats(
                count=0,
                null_count=null_count,
                unique_count=0,
            )

        char_lens = non_null.str.len()
        word_counts = non_null.str.split().str.len()

        return TextStats(
            count=count,
            null_count=null_count,
            unique_count=unique_count,
            avg_word_count=_safe_float(word_counts.mean()),
            avg_char_length=_safe_float(char_lens.mean()),
            min_length=int(char_lens.min()),
            max_length=int(char_lens.max()),
        )

    @staticmethod
    def _analyze_identifier(series: pd.Series) -> IdentifierStats:
        """Calculate uniqueness ratios and count metrics for identifiers."""
        non_null = series.dropna().astype(str)
        count = int(len(non_null))
        null_count = int(series.isna().sum())
        unique_count = int(non_null.nunique())
        ratio = round(unique_count / count, 4) if count > 0 else 0.0

        return IdentifierStats(
            count=count,
            null_count=null_count,
            unique_count=unique_count,
            uniqueness_ratio=ratio,
        )
