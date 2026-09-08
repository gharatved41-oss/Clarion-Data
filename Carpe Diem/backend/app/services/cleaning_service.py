"""Service handling automated, reproducible, and audited dataset cleaning."""
import json
import logging
import re
from pathlib import Path
import pandas as pd
import numpy as np
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.dataset import CleaningOperation, CleaningReportResponse
from app.services.upload_service import UploadService
from app.services.schema_service import SchemaService

logger = logging.getLogger("app.services.cleaning_service")


class CleaningService:
    """Automated data cleaning engine."""

    @classmethod
    def clean_dataset(cls, dataset_id: str, force_reclean: bool = False) -> CleaningReportResponse:
        """Execute full cleaning pipeline on a raw dataset and persist processed artifacts."""
        processed_dir = settings.processed_dir / dataset_id
        report_file = processed_dir / "cleaning_report.json"
        cleaned_csv_file = processed_dir / "cleaned.csv"

        # Return cached report if already processed and not forcing reclean
        if not force_reclean and report_file.exists() and cleaned_csv_file.exists():
            with open(report_file, "r", encoding="utf-8") as f:
                return CleaningReportResponse(**json.load(f))

        # Load raw untouched dataset
        raw_df, meta = UploadService.load_raw_dataset(dataset_id)
        df = raw_df.copy()

        # Run intelligent schema detection
        schema_res = SchemaService.detect_schema(dataset_id)
        schema_map = {col.name: col.type for col in schema_res.columns}

        orig_row_count = int(len(df))
        orig_col_count = int(len(df.columns))
        missing_detected = int(df.isna().sum().sum())

        operations: list[CleaningOperation] = []
        warnings: list[str] = []
        skipped_ops: list[str] = []

        duplicates_detected = 0
        duplicates_removed = 0
        numeric_conversions = 0
        currency_conversions = 0
        percentage_conversions = 0
        date_conversions = 0
        whitespace_fixes = 0
        capitalization_fixes = 0
        missing_handled = 0

        # ---------------------------------------------------------------------
        # 1. Exact Duplicate Row Removal
        # ---------------------------------------------------------------------
        duplicates_detected = int(df.duplicated().sum())
        if duplicates_detected > 0:
            df = df.drop_duplicates().reset_index(drop=True)
            duplicates_removed = duplicates_detected
            operations.append(CleaningOperation(
                column=None,
                operation="duplicate_removal",
                affected_rows=duplicates_detected,
                method="exact_match",
                details=f"Identified and removed {duplicates_detected} exact duplicate rows."
            ))

        # ---------------------------------------------------------------------
        # 2. Whitespace Trimming (All String / Object Columns)
        # ---------------------------------------------------------------------
        for col in df.columns:
            if df[col].dtype == object or isinstance(df[col].dtype, pd.StringDtype):
                s = df[col]
                has_whitespace = s.dropna().astype(str).str.contains(r"^\s+|\s+$", regex=True)
                ws_count = int(has_whitespace.sum())
                if ws_count > 0:
                    df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
                    whitespace_fixes += ws_count
                    operations.append(CleaningOperation(
                        column=col,
                        operation="whitespace_trimming",
                        affected_rows=ws_count,
                        method="strip",
                        details=f"Removed extra leading and trailing whitespace from {ws_count} cells."
                    ))

        # ---------------------------------------------------------------------
        # 3. Currency, Percentage & Numeric Formats
        # ---------------------------------------------------------------------
        for col in df.columns:
            col_type = schema_map.get(col, "text")

            if col_type == "numeric" and (df[col].dtype == object or isinstance(df[col].dtype, pd.StringDtype)):
                series_str = df[col].dropna().astype(str)

                # Check for currency symbols / suffixes
                has_curr = series_str.str.contains(r"(?i)[₹$€£¥]|\b(?:inr|usd|eur|gbp)\b", regex=True)
                curr_count = int(has_curr.sum())
                if curr_count > 0:
                    currency_conversions += curr_count
                    operations.append(CleaningOperation(
                        column=col,
                        operation="currency_conversion",
                        affected_rows=curr_count,
                        method="currency_symbol_stripping",
                        details=f"Stripped currency symbols (₹, $, INR, etc.) from {curr_count} cells."
                    ))

                # Check for percentages
                has_pct = series_str.str.contains(r"%", regex=False)
                pct_count = int(has_pct.sum())
                if pct_count > 0:
                    percentage_conversions += pct_count
                    operations.append(CleaningOperation(
                        column=col,
                        operation="percentage_conversion",
                        affected_rows=pct_count,
                        method="percentage_normalization",
                        details=f"Normalized {pct_count} percentage cells to standard numeric scale (e.g., 10% -> 10.0)."
                    ))

                # General numeric conversion: strip quotes, commas, symbols, spaces
                cleaned_numeric = (
                    df[col].astype(str)
                    .str.replace(r'["\']', '', regex=True)
                    .str.replace(r'[₹$€£¥]', '', regex=True)
                    .str.replace(r'\s*(?:inr|usd|eur|gbp)\b', '', case=False, regex=True)
                    .str.replace('%', '', regex=False)
                    .str.replace(',', '', regex=False)
                    .str.strip()
                )
                # Preserve existing NaNs
                cleaned_numeric = cleaned_numeric.replace(r"^(nan|none|null|)$", np.nan, regex=True)
                num_series = pd.to_numeric(cleaned_numeric, errors="coerce")

                valid_converted = int(num_series.notna().sum())
                numeric_conversions += valid_converted
                df[col] = num_series
                operations.append(CleaningOperation(
                    column=col,
                    operation="numeric_conversion",
                    affected_rows=valid_converted,
                    method="to_numeric",
                    details=f"Converted {valid_converted} formatted string values into float/integer numeric representation."
                ))

        # ---------------------------------------------------------------------
        # 4. Date Normalization (ISO 8601: YYYY-MM-DD)
        # ---------------------------------------------------------------------
        for col in df.columns:
            col_type = schema_map.get(col, "text")

            if col_type == "datetime":
                parsed_dt = pd.to_datetime(df[col], errors="coerce", format="mixed")
                valid_dates = int(parsed_dt.notna().sum())
                invalid_dates = int(df[col].notna().sum()) - valid_dates

                if invalid_dates > 0:
                    warnings.append(f"Column '{col}' contained {invalid_dates} unparseable date values converted to NaT.")

                # Format to standard ISO 8601 string representation
                df[col] = parsed_dt.dt.strftime("%Y-%m-%d")
                date_conversions += valid_dates
                operations.append(CleaningOperation(
                    column=col,
                    operation="date_normalization",
                    affected_rows=valid_dates,
                    method="iso_8601",
                    details=f"Normalized {valid_dates} dates to standard ISO 8601 (YYYY-MM-DD)."
                ))

        # ---------------------------------------------------------------------
        # 5. Inconsistent Capitalization & Category Normalization
        # ---------------------------------------------------------------------
        for col in df.columns:
            col_type = schema_map.get(col, "text")

            if col_type == "categorical" and (df[col].dtype == object or isinstance(df[col].dtype, pd.StringDtype)):
                non_null = df[col].dropna().astype(str).str.strip()
                if len(non_null) == 0:
                    continue

                # Build case normalization dictionary
                groups = {}
                for val in non_null.unique():
                    lower_key = val.lower()
                    groups.setdefault(lower_key, []).append(val)

                val_counts = non_null.value_counts()
                mapping = {}
                col_cap_fixes = 0

                for lower_key, variants in groups.items():
                    if len(variants) > 1:
                        # Choose canonical: True Title Case if present, else capitalize
                        title_variants = [v for v in variants if v.istitle()]
                        if title_variants:
                            # Pick the most frequent title-cased variant
                            canonical = max(title_variants, key=lambda x: val_counts.get(x, 0))
                        else:
                            # If no title-cased variant existed, format the most frequent as Title Case
                            most_frequent = max(variants, key=lambda x: val_counts.get(x, 0))
                            canonical = most_frequent.title()

                        for v in variants:
                            if v != canonical:
                                mapping[v] = canonical
                                col_cap_fixes += int((non_null == v).sum())

                if col_cap_fixes > 0:
                    df[col] = df[col].replace(mapping)
                    capitalization_fixes += col_cap_fixes
                    operations.append(CleaningOperation(
                        column=col,
                        operation="category_normalization",
                        affected_rows=col_cap_fixes,
                        method="case_and_frequency_consensus",
                        details=f"Unified {col_cap_fixes} casing inconsistencies into canonical representations."
                    ))

        # ---------------------------------------------------------------------
        # 6. Missing Value Imputation
        # ---------------------------------------------------------------------
        for col in df.columns:
            null_count = int(df[col].isna().sum())
            if null_count == 0:
                continue

            col_type = schema_map.get(col, "text")

            if col_type == "numeric":
                median_val = df[col].dropna().median()
                if pd.isna(median_val):
                    median_val = 0.0
                else:
                    median_val = round(float(median_val), 2)
                df[col] = df[col].fillna(median_val)
                missing_handled += null_count
                operations.append(CleaningOperation(
                    column=col,
                    operation="missing_value_imputation",
                    affected_rows=null_count,
                    method="median",
                    details=f"Imputed {null_count} missing numeric values using column median ({median_val})."
                ))

            elif col_type == "categorical":
                modes = df[col].dropna().mode()
                mode_val = modes.iloc[0] if not modes.empty else "Unknown"
                df[col] = df[col].fillna(mode_val)
                missing_handled += null_count
                operations.append(CleaningOperation(
                    column=col,
                    operation="missing_value_imputation",
                    affected_rows=null_count,
                    method="mode",
                    details=f"Imputed {null_count} missing categorical values using mode ('{mode_val}')."
                ))

            elif col_type == "text":
                placeholder = "Not Provided"
                df[col] = df[col].fillna(placeholder)
                missing_handled += null_count
                operations.append(CleaningOperation(
                    column=col,
                    operation="missing_value_imputation",
                    affected_rows=null_count,
                    method="placeholder",
                    details=f"Imputed {null_count} missing text values with '{placeholder}' to preserve text integrity."
                ))

            elif col_type == "identifier":
                skipped_ops.append(f"Missing value imputation skipped for identifier column '{col}'.")
                warnings.append(f"Column '{col}' is an identifier; {null_count} missing values were left untouched to protect entity integrity.")

            elif col_type == "datetime":
                # For dates, avoid inventing fake dates; forward fill or leave explicit NaT / placeholder
                skipped_ops.append(f"Missing value imputation skipped for datetime column '{col}'.")
                warnings.append(f"Column '{col}' has {null_count} missing/invalid dates left un-imputed.")

        # ---------------------------------------------------------------------
        # 7. Persist Cleaned Dataset & Audit Report
        # ---------------------------------------------------------------------
        processed_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(cleaned_csv_file, index=False, encoding="utf-8")

        report = CleaningReportResponse(
            dataset_id=dataset_id,
            original_row_count=orig_row_count,
            cleaned_row_count=int(len(df)),
            original_column_count=orig_col_count,
            missing_values_detected=missing_detected,
            missing_values_handled=missing_handled,
            duplicates_detected=duplicates_detected,
            duplicates_removed=duplicates_removed,
            numeric_conversions=numeric_conversions,
            currency_conversions=currency_conversions,
            percentage_conversions=percentage_conversions,
            date_conversions=date_conversions,
            whitespace_fixes=whitespace_fixes,
            capitalization_fixes=capitalization_fixes,
            operations=operations,
            warnings=warnings,
            skipped_operations=skipped_ops
        )

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        logger.info(f"Dataset {dataset_id} cleaned successfully: {orig_row_count} -> {len(df)} rows.")
        return report

    @classmethod
    def load_cleaned_dataset(cls, dataset_id: str) -> tuple[pd.DataFrame, CleaningReportResponse]:
        """Retrieve cleaned DataFrame and cleaning report, triggering cleaning if needed."""
        processed_dir = settings.processed_dir / dataset_id
        cleaned_csv_file = processed_dir / "cleaned.csv"
        report_file = processed_dir / "cleaning_report.json"

        if not cleaned_csv_file.exists() or not report_file.exists():
            report = cls.clean_dataset(dataset_id)
        else:
            with open(report_file, "r", encoding="utf-8") as f:
                report = CleaningReportResponse(**json.load(f))

        df = pd.read_csv(cleaned_csv_file)
        return df, report
