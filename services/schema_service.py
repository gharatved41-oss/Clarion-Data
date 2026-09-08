"""Service for intelligent automatic column type detection."""
import re
import logging
from typing import Literal
import pandas as pd
import numpy as np

from app.schemas.dataset import ColumnSchema, DatasetSchemaResponse
from app.services.upload_service import UploadService

logger = logging.getLogger("app.services.schema_service")

# Regex pattern matching common identifier column names
ID_NAME_PATTERN = re.compile(
    r"(?i)(^|_|-)(id|uuid|guid|code|key|no|num|number)($|_|-)|^id$|_id$|id$"
)

# Regex pattern for UUID strings
UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

# Regex pattern for prefixed alphanumeric IDs (e.g. CUST0012, ORD_9981, EMP-104)
PREFIXED_ID_PATTERN = re.compile(
    r"^[A-Za-z]{2,8}[-_]?[0-9]{3,12}$"
)

# Column names that strongly suggest continuous numerical measurements, not identifiers
NUMERIC_MEASURE_KEYWORDS = {
    "price", "amount", "sales", "revenue", "cost", "rate", "score",
    "weight", "height", "age", "discount", "rating", "days", "time",
    "duration", "count", "quantity", "spend", "balance", "total", "fee", "tax"
}

# Column names that strongly suggest natural-language text fields
TEXT_KEYWORDS = {
    "feedback", "description", "comment", "comments", "review", "reviews",
    "notes", "summary", "message", "remark", "remarks", "reason", "complaint",
    "complaints", "details", "text", "transcript", "response", "bio", "name",
    "customer_name", "user_name", "employee_name", "first_name", "last_name"
}


class SchemaService:
    """Intelligent schema detection engine."""

    @classmethod
    def detect_schema(cls, dataset_id: str) -> DatasetSchemaResponse:
        """Load dataset and perform intelligent column type detection."""
        df, _ = UploadService.load_raw_dataset(dataset_id)
        column_schemas: list[ColumnSchema] = []

        for col in df.columns:
            schema = cls._detect_column_type(col, df[col])
            column_schemas.append(schema)

        return DatasetSchemaResponse(
            dataset_id=dataset_id,
            columns=column_schemas
        )

    @classmethod
    def _detect_column_type(cls, col_name: str, series: pd.Series) -> ColumnSchema:
        """Analyze a single column and determine its canonical data type."""
        col_str = str(col_name).strip()
        col_lower = col_str.lower()
        orig_dtype = str(series.dtype)
        total_len = len(series)
        null_count = int(series.isna().sum())
        non_null = series.dropna()
        valid_len = len(non_null)

        # Handle all-null columns
        if valid_len == 0:
            return ColumnSchema(
                name=col_str,
                type="text",
                confidence=0.50,
                original_dtype=orig_dtype,
                unique_count=0,
                null_count=total_len
            )

        unique_count = int(non_null.nunique())
        uniqueness_ratio = unique_count / valid_len if valid_len > 0 else 0.0

        # Sample for string and pattern analysis
        sample_size = min(valid_len, 200)
        sample = non_null.sample(sample_size, random_state=42) if valid_len > sample_size else non_null
        str_sample = sample.astype(str).str.strip()

        # Check if column name strongly indicates a numerical measurement
        name_tokens = set(re.split(r"[_\s\-]+", col_lower))
        is_measure_name = bool(name_tokens & NUMERIC_MEASURE_KEYWORDS)

        # ---------------------------------------------------------------------
        # 1. Identifier Detection
        # ---------------------------------------------------------------------
        # Do not classify as identifier if column name clearly indicates measurement/metric
        if not is_measure_name:
            has_id_name = bool(ID_NAME_PATTERN.search(col_lower))

            # UUID check
            uuid_matches = str_sample.apply(lambda s: bool(UUID_PATTERN.match(s))).mean()
            if uuid_matches > 0.8:
                return ColumnSchema(
                    name=col_str,
                    type="identifier",
                    confidence=0.99,
                    original_dtype=orig_dtype,
                    unique_count=unique_count,
                    null_count=null_count
                )

            # Prefixed alphanumeric ID check (e.g. CUST0697)
            prefixed_matches = str_sample.apply(lambda s: bool(PREFIXED_ID_PATTERN.match(s))).mean()
            if prefixed_matches > 0.7 and (uniqueness_ratio >= 0.8 or has_id_name):
                conf = 0.98 if has_id_name else 0.92
                return ColumnSchema(
                    name=col_str,
                    type="identifier",
                    confidence=conf,
                    original_dtype=orig_dtype,
                    unique_count=unique_count,
                    null_count=null_count
                )

            # Integer sequential or high uniqueness with ID name
            if has_id_name and (uniqueness_ratio >= 0.85 or unique_count >= 10):
                return ColumnSchema(
                    name=col_str,
                    type="identifier",
                    confidence=0.95,
                    original_dtype=orig_dtype,
                    unique_count=unique_count,
                    null_count=null_count
                )

            # Strictly monotonic sequential integers (e.g., 1, 2, 3...)
            if pd.api.types.is_integer_dtype(series) and uniqueness_ratio == 1.0:
                diffs = non_null.sort_values().diff().dropna()
                if (diffs == 1).mean() > 0.9:
                    return ColumnSchema(
                        name=col_str,
                        type="identifier",
                        confidence=0.94,
                        original_dtype=orig_dtype,
                        unique_count=unique_count,
                        null_count=null_count
                    )

        # ---------------------------------------------------------------------
        # 2. DateTime Detection
        # ---------------------------------------------------------------------
        # Already datetime dtype in pandas
        if pd.api.types.is_datetime64_any_dtype(series):
            return ColumnSchema(
                name=col_str,
                type="datetime",
                confidence=1.0,
                original_dtype=orig_dtype,
                unique_count=unique_count,
                null_count=null_count
            )

        # Check for date-like strings
        if series.dtype == object or isinstance(series.dtype, pd.StringDtype):
            date_separators = {"-", "/", ".", "T"}
            has_separators = str_sample.apply(lambda s: any(sep in s for sep in date_separators)).mean()

            if has_separators > 0.6:
                # Attempt parsing sample with pandas to_datetime
                try:
                    parsed_dates = pd.to_datetime(str_sample, errors="coerce", format="mixed")
                    valid_date_ratio = float(parsed_dates.notna().mean())
                    if valid_date_ratio >= 0.8:
                        # Verify year range is plausible (1900 - 2100)
                        years = parsed_dates.dt.year.dropna()
                        if len(years) > 0 and ((years >= 1900) & (years <= 2100)).mean() > 0.8:
                            confidence = float(round(0.90 + (0.09 * valid_date_ratio), 2))
                            return ColumnSchema(
                                name=col_str,
                                type="datetime",
                                confidence=confidence,
                                original_dtype=orig_dtype,
                                unique_count=unique_count,
                                null_count=null_count
                            )
                except Exception:
                    pass

        # ---------------------------------------------------------------------
        # 3. Numeric Detection
        # ---------------------------------------------------------------------
        # Already numeric dtype (int or float)
        if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
            return ColumnSchema(
                name=col_str,
                type="numeric",
                confidence=0.99,
                original_dtype=orig_dtype,
                unique_count=unique_count,
                null_count=null_count
            )

        # Numbers stored as strings (including currencies, percentages, commas)
        if series.dtype == object or isinstance(series.dtype, pd.StringDtype):
            cleaned_sample = (
                str_sample
                .str.replace(r'["\']', '', regex=True)
                .str.replace(r'[₹$€£¥]', '', regex=True)
                .str.replace(r'(?i)\s*(inr|usd|eur|gbp)\b', '', regex=True)
                .str.replace('%', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.strip()
            )
            converted_num = pd.to_numeric(cleaned_sample, errors="coerce")
            valid_num_ratio = float(converted_num.notna().mean())

            if valid_num_ratio >= 0.8:
                confidence = float(round(0.90 + (0.09 * valid_num_ratio), 2))
                return ColumnSchema(
                    name=col_str,
                    type="numeric",
                    confidence=confidence,
                    original_dtype=orig_dtype,
                    unique_count=unique_count,
                    null_count=null_count
                )

        # ---------------------------------------------------------------------
        # 4. Categorical vs. Text Detection
        # ---------------------------------------------------------------------
        # Measure text length and word count
        str_all = non_null.astype(str).str.strip()
        mean_len = float(str_all.str.len().mean())
        mean_words = float(str_all.str.split().str.len().mean())
        is_text_name = bool(name_tokens & TEXT_KEYWORDS)

        # Boolean columns or limited binary values
        if unique_count <= 2 and not is_text_name:
            return ColumnSchema(
                name=col_str,
                type="categorical",
                confidence=0.98,
                original_dtype=orig_dtype,
                unique_count=unique_count,
                null_count=null_count
            )

        # Explicit text / feedback / comment / name column
        if is_text_name:
            return ColumnSchema(
                name=col_str,
                type="text",
                confidence=0.96,
                original_dtype=orig_dtype,
                unique_count=unique_count,
                null_count=null_count
            )

        # Long natural-language text (descriptions, sentences, reviews)
        if mean_words >= 3.2 or mean_len >= 30:
            return ColumnSchema(
                name=col_str,
                type="text",
                confidence=0.95,
                original_dtype=orig_dtype,
                unique_count=unique_count,
                null_count=null_count
            )

        # Repeated categories (cities, departments, statuses, products, categories)
        if unique_count <= 60 or uniqueness_ratio <= 0.35:
            return ColumnSchema(
                name=col_str,
                type="categorical",
                confidence=0.95,
                original_dtype=orig_dtype,
                unique_count=unique_count,
                null_count=null_count
            )

        # Medium cardinality: check word count and length
        if mean_words <= 3 and mean_len < 30:
            if uniqueness_ratio < 0.65:
                return ColumnSchema(
                    name=col_str,
                    type="categorical",
                    confidence=0.90,
                    original_dtype=orig_dtype,
                    unique_count=unique_count,
                    null_count=null_count
                )
            else:
                return ColumnSchema(
                    name=col_str,
                    type="text",
                    confidence=0.90,
                    original_dtype=orig_dtype,
                    unique_count=unique_count,
                    null_count=null_count
                )

        return ColumnSchema(
            name=col_str,
            type="text",
            confidence=0.85,
            original_dtype=orig_dtype,
            unique_count=unique_count,
            null_count=null_count
        )
