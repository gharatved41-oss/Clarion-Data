import pandas as pd
from typing import Dict, Any
from services.dataset_store import dataset_store
from utils.helpers import sanitize_for_json, detect_column_types

class QualityScoreService:
    """Data Quality Scoring Engine evaluating missingness, duplication, type consistency, and completeness."""

    @staticmethod
    def calculate_score(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"dataset_id": dataset_id, "score": 0, "grade": "F", "factors": {}}

        total_rows = len(df)
        total_cols = len(df.columns)
        total_cells = total_rows * total_cols

        if total_cells == 0:
            return {"dataset_id": dataset_id, "score": 0, "grade": "F", "factors": {}}

        # 1. Missing Values Score (Weight: 30%)
        missing_count = int(df.isna().sum().sum())
        missing_pct = missing_count / total_cells
        missing_score = max(0.0, 100.0 * (1.0 - (missing_pct * 2)))

        # 2. Duplicate Records Score (Weight: 25%)
        dup_count = int(df.duplicated().sum())
        dup_pct = dup_count / total_rows if total_rows > 0 else 0
        duplicate_score = max(0.0, 100.0 * (1.0 - (dup_pct * 3)))

        # 3. Formatting & Type Consistency Score (Weight: 25%)
        # Deduct points if columns have mixed string/numeric types or high unexpected NaN ratios after conversion
        col_types = detect_column_types(df)
        format_penalties = 0
        for col in df.columns:
            if col_types[col] == 'numeric':
                conv = pd.to_numeric(df[col], errors='coerce')
                orig_non_null = df[col].notna().sum()
                conv_non_null = conv.notna().sum()
                if orig_non_null > 0 and conv_non_null < orig_non_null:
                    format_penalties += (orig_non_null - conv_non_null)

        formatting_pct = format_penalties / total_cells if total_cells > 0 else 0
        formatting_score = max(0.0, 100.0 * (1.0 - (formatting_pct * 4)))

        # 4. Completeness Score (Weight: 20%)
        # Ratio of complete rows (no NaNs)
        complete_rows = int(df.dropna().shape[0])
        completeness_pct = complete_rows / total_rows if total_rows > 0 else 0
        completeness_score = round(completeness_pct * 100, 2)

        # Weighted Total Score
        final_score = round(
            (missing_score * 0.30) +
            (duplicate_score * 0.25) +
            (formatting_score * 0.25) +
            (completeness_score * 0.20),
            1
        )

        # Assign Grade
        if final_score >= 90:
            grade = "A"
        elif final_score >= 80:
            grade = "B"
        elif final_score >= 70:
            grade = "C"
        elif final_score >= 60:
            grade = "D"
        else:
            grade = "F"

        methodology = (
            "Data Quality Score (0-100) is calculated using weighted dataset evaluation metrics: "
            "Missing Values (30%), Duplicate Records (25%), Format/Type Consistency (25%), and Row Completeness (20%)."
        )

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "score": final_score,
            "grade": grade,
            "methodology": methodology,
            "factors": {
                "missing_values": round(missing_score, 1),
                "duplicates": round(duplicate_score, 1),
                "formatting": round(formatting_score, 1),
                "completeness": round(completeness_score, 1)
            }
        })
