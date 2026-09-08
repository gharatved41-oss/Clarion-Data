import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from services.dataset_store import dataset_store
from utils.helpers import clean_dataframe_numeric_columns, sanitize_for_json

class DataQueryEngine:
    """Safe, high-performance analytical query and statistical reasoning engine for datasets."""

    SYNONYM_MAP = {
        "cost": ["cost", "charges", "charge", "expense", "expenses", "price", "amount", "fee", "bill", "spend"],
        "revenue": ["revenue", "sales", "total_sales", "income", "turnover", "gross"],
        "age": ["age", "years", "old", "demographic"],
        "gender": ["gender", "sex"],
        "stay": ["stay", "length_of_stay", "los", "duration", "days"],
        "readmission": ["readmission", "readmit", "readmitted"],
        "condition": ["condition", "diagnosis", "disease", "illness", "disorder"],
        "procedure": ["procedure", "surgery", "treatment", "operation", "intervention"],
        "outcome": ["outcome", "result", "status", "discharge"],
        "satisfaction": ["satisfaction", "score", "rating", "csat", "nps"],
        "profit": ["profit", "margin", "net"],
        "salary": ["salary", "wage", "compensation", "pay"],
    }

    @staticmethod
    def get_clean_df(dataset_id: str) -> Optional[pd.DataFrame]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return None
        return clean_dataframe_numeric_columns(df)

    @classmethod
    def find_mentioned_columns(cls, df: pd.DataFrame, text: str) -> List[str]:
        """Intelligently identifies DataFrame columns referenced in user queries."""
        if df is None or not text:
            return []

        text_lower = text.lower()
        matched = []
        col_map = {c.lower(): c for c in df.columns}
        normalized_cols = {c.lower().replace("_", " "): c for c in df.columns}

        # 1. Exact phrase/name match
        for norm_name, orig_col in normalized_cols.items():
            pattern = r'\b' + re.escape(norm_name) + r'\b'
            if re.search(pattern, text_lower):
                if orig_col not in matched:
                    matched.append(orig_col)

        for col_l, orig_col in col_map.items():
            pattern = r'\b' + re.escape(col_l) + r'\b'
            if re.search(pattern, text_lower):
                if orig_col not in matched:
                    matched.append(orig_col)

        # 2. Semantic synonym match
        words = re.findall(r'\b[a-z0-9_]+\b', text_lower)
        for w in words:
            for syn_group, syn_list in cls.SYNONYM_MAP.items():
                if w in syn_list:
                    # Find if any column name contains or equals one of the synonyms
                    for col in df.columns:
                        col_l = col.lower()
                        if any(s in col_l for s in syn_list) and col not in matched:
                            matched.append(col)

        return matched

    @staticmethod
    def query_bivariate_analysis(
        dataset_id: str,
        col_x: str,
        col_y: str
    ) -> Dict[str, Any]:
        """Computes comprehensive correlation, linear regression, and coordinates for 2 numeric features."""
        df = DataQueryEngine.get_clean_df(dataset_id)
        if df is None:
            return {"error": "Dataset not found"}

        if col_x not in df.columns or col_y not in df.columns:
            return {"error": f"Columns not found: '{col_x}', '{col_y}'"}

        sub = df[[col_x, col_y]].dropna().copy()
        sub[col_x] = pd.to_numeric(sub[col_x], errors='coerce')
        sub[col_y] = pd.to_numeric(sub[col_y], errors='coerce')
        valid = sub.dropna()

        if len(valid) < 2:
            return {"error": "Insufficient valid numeric pairs for analysis."}

        x = valid[col_x]
        y = valid[col_y]

        # Pearson correlation
        r = float(x.corr(y))
        if np.isnan(r):
            r = 0.0

        # Linear regression slope & intercept
        var_x = float(x.var())
        cov_xy = float(x.cov(y))
        slope = (cov_xy / var_x) if var_x > 0 else 0.0
        intercept = float(y.mean() - slope * x.mean())

        # Subsample points for scatter plot (max 80 points, deterministic)
        sample_size = min(len(valid), 80)
        sample_df = valid.sample(n=sample_size, random_state=42) if len(valid) > 80 else valid
        sample_df = sample_df.sort_values(by=col_x)

        points = [
            {"x": round(float(row[col_x]), 1), "y": round(float(row[col_y]), 2)}
            for _, row in sample_df.iterrows()
        ]

        # Natural cohort brackets across col_x
        brackets = []
        try:
            x_min, x_max = float(x.min()), float(x.max())
            if x_max - x_min > 5:
                # 3 Cohorts
                b1 = x_min + (x_max - x_min) * 0.33
                b2 = x_min + (x_max - x_min) * 0.66
                cohorts = [
                    (f"{x_min:.0f}–{b1:.0f}", valid[x <= b1]),
                    (f"{b1:.0f}–{b2:.0f}", valid[(x > b1) & (x <= b2)]),
                    (f"{b2:.0f}–{x_max:.0f}", valid[x > b2]),
                ]
                for label, c_df in cohorts:
                    if len(c_df) > 0:
                        brackets.append({
                            "bracket": label,
                            "count": len(c_df),
                            "mean": round(float(c_df[col_y].mean()), 2),
                            "median": round(float(c_df[col_y].median()), 2)
                        })
        except Exception:
            brackets = []

        # Interpretation of correlation
        abs_r = abs(r)
        if abs_r >= 0.7:
            strength = "Strong"
        elif abs_r >= 0.4:
            strength = "Moderate"
        elif abs_r >= 0.2:
            strength = "Weak"
        else:
            strength = "Negligible"
        direction = "Positive" if r >= 0 else "Negative"

        chart_payload = {
            "type": "scatter",
            "title": f"{col_x} vs. {col_y} Correlation",
            "x_label": col_x,
            "y_label": col_y,
            "correlation": round(r, 3),
            "slope": round(slope, 3),
            "intercept": round(intercept, 2),
            "data": points,
            "brackets": brackets
        }

        return sanitize_for_json({
            "feature_x": col_x,
            "feature_y": col_y,
            "sample_count": len(valid),
            "correlation": round(r, 3),
            "relationship": f"{strength} {direction}",
            "slope": round(slope, 3),
            "intercept": round(intercept, 2),
            "stats_x": {
                "min": round(float(x.min()), 2),
                "max": round(float(x.max()), 2),
                "mean": round(float(x.mean()), 2),
                "median": round(float(x.median()), 2),
            },
            "stats_y": {
                "min": round(float(y.min()), 2),
                "max": round(float(y.max()), 2),
                "mean": round(float(y.mean()), 2),
                "median": round(float(y.median()), 2),
            },
            "brackets": brackets,
            "chart": chart_payload
        })

    @staticmethod
    def query_group_comparison(
        dataset_id: str,
        group_col: str,
        metric_col: str,
        agg_func: str = "mean",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Calculates group statistics and prepares bar chart structure."""
        df = DataQueryEngine.get_clean_df(dataset_id)
        if df is None:
            return {"error": "Dataset not found"}

        if group_col not in df.columns or metric_col not in df.columns:
            return {"error": f"Columns not found: group='{group_col}', metric='{metric_col}'"}

        sub = df[[group_col, metric_col]].dropna().copy()
        sub[metric_col] = pd.to_numeric(sub[metric_col], errors='coerce')
        valid = sub.dropna()

        if len(valid) == 0:
            return {"error": "No valid data for comparison."}

        grouped = valid.groupby(group_col)[metric_col].agg(
            count='count',
            mean='mean',
            median='median',
            min='min',
            max='max'
        ).reset_index()

        grouped = grouped.sort_values(by="mean", ascending=False).head(limit)

        results = []
        chart_data = []
        for _, row in grouped.iterrows():
            g_name = str(row[group_col])
            mean_val = round(float(row['mean']), 2)
            results.append({
                "group": g_name,
                "count": int(row['count']),
                "mean": mean_val,
                "median": round(float(row['median']), 2),
                "min": round(float(row['min']), 2),
                "max": round(float(row['max']), 2),
            })
            chart_data.append({"x": g_name, "y": mean_val})

        chart_payload = {
            "type": "bar",
            "title": f"Average {metric_col} by {group_col}",
            "x_label": group_col,
            "y_label": f"Average {metric_col}",
            "data": chart_data
        }

        return sanitize_for_json({
            "group_column": group_col,
            "metric_column": metric_col,
            "aggregation": agg_func,
            "groups_count": len(results),
            "results": results,
            "chart": chart_payload
        })

    @staticmethod
    def query_distribution(dataset_id: str, column_name: str, bins: int = 8) -> Dict[str, Any]:
        """Calculates frequency histogram bins and summary percentiles for numeric features."""
        df = DataQueryEngine.get_clean_df(dataset_id)
        if df is None:
            return {"error": "Dataset not found"}

        if column_name not in df.columns:
            return {"error": f"Column '{column_name}' not found."}

        series = pd.to_numeric(df[column_name], errors='coerce').dropna()
        if len(series) < 2:
            return {"error": f"Insufficient numeric values in '{column_name}'"}

        counts, bin_edges = np.histogram(series, bins=bins)
        chart_data = []
        for i in range(len(counts)):
            label = f"{bin_edges[i]:.1f}–{bin_edges[i+1]:.1f}"
            chart_data.append({"x": label, "y": int(counts[i])})

        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        outliers_count = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())

        chart_payload = {
            "type": "histogram",
            "title": f"Distribution of {column_name}",
            "x_label": column_name,
            "y_label": "Frequency (Count)",
            "data": chart_data
        }

        return sanitize_for_json({
            "column": column_name,
            "count": len(series),
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "std": round(float(series.std()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "q1": round(q1, 2),
            "q3": round(q3, 2),
            "iqr": round(iqr, 2),
            "outliers_count": outliers_count,
            "bins": chart_data,
            "chart": chart_payload
        })

    @staticmethod
    def query_conditional_metric(
        dataset_id: str,
        metric_col: str,
        filter_col: str,
        operator: str,
        threshold: float,
        agg_func: str = "mean"
    ) -> Dict[str, Any]:
        """Calculates aggregated metrics on filtered cohorts (e.g. average cost for age > 50)."""
        df = DataQueryEngine.get_clean_df(dataset_id)
        if df is None:
            return {"error": "Dataset not found"}

        if metric_col not in df.columns or filter_col not in df.columns:
            return {"error": f"Columns not found: metric='{metric_col}', filter='{filter_col}'"}

        sub = df[[metric_col, filter_col]].dropna().copy()
        sub[metric_col] = pd.to_numeric(sub[metric_col], errors='coerce')
        sub[filter_col] = pd.to_numeric(sub[filter_col], errors='coerce')
        valid = sub.dropna()

        f_series = valid[filter_col]
        if operator == ">":
            mask = f_series > threshold
        elif operator == ">=":
            mask = f_series >= threshold
        elif operator == "<":
            mask = f_series < threshold
        elif operator == "<=":
            mask = f_series <= threshold
        else:
            mask = f_series == threshold

        cohort = valid[mask]
        if len(cohort) == 0:
            return {"error": f"No records matched condition: {filter_col} {operator} {threshold}"}

        cohort_metric = cohort[metric_col]
        all_metric = valid[metric_col]

        cohort_mean = float(cohort_metric.mean())
        all_mean = float(all_metric.mean())
        diff = cohort_mean - all_mean
        diff_pct = (diff / all_mean * 100) if all_mean != 0 else 0.0

        chart_payload = {
            "type": "bar",
            "title": f"Cohort Comparison: {metric_col}",
            "x_label": "Cohort",
            "y_label": f"Average {metric_col}",
            "data": [
                {"x": "Entire Dataset", "y": round(all_mean, 2)},
                {"x": f"{filter_col} {operator} {threshold:.0f}", "y": round(cohort_mean, 2)}
            ]
        }

        return sanitize_for_json({
            "metric_column": metric_col,
            "filter_column": filter_col,
            "condition": f"{filter_col} {operator} {threshold}",
            "cohort_count": len(cohort),
            "total_count": len(valid),
            "cohort_percentage": round((len(cohort) / len(valid)) * 100, 1),
            "cohort_mean": round(cohort_mean, 2),
            "cohort_median": round(float(cohort_metric.median()), 2),
            "cohort_min": round(float(cohort_metric.min()), 2),
            "cohort_max": round(float(cohort_metric.max()), 2),
            "dataset_mean": round(all_mean, 2),
            "difference": round(diff, 2),
            "difference_percentage": round(diff_pct, 1),
            "chart": chart_payload
        })

    @staticmethod
    def query_top_n(dataset_id: str, sort_col: str, n: int = 5, ascending: bool = False) -> Dict[str, Any]:
        """Safely retrieves top/bottom N records sorted by a column."""
        df = DataQueryEngine.get_clean_df(dataset_id)
        if df is None:
            return {"error": "Dataset not found"}

        matched_col = next((c for c in df.columns if c.lower() == sort_col.lower()), None)
        if not matched_col:
            return {"error": f"Sort column '{sort_col}' not found."}

        n = max(1, min(25, int(n)))
        sorted_df = df.sort_values(by=matched_col, ascending=ascending).head(n)

        # Select most informative 5 columns
        key_cols = [matched_col]
        for c in df.columns:
            if c != matched_col and len(key_cols) < 5:
                key_cols.append(c)

        records = sorted_df[key_cols].to_dict(orient="records")
        return sanitize_for_json({
            "sort_column": matched_col,
            "ascending": ascending,
            "count": len(records),
            "records": records
        })

    @staticmethod
    def query_missing_values(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"error": "Dataset not found"}

        total_rows = len(df)
        missing_info = []
        for col in df.columns:
            null_cnt = int(df[col].isna().sum())
            if null_cnt > 0:
                missing_info.append({
                    "column": col,
                    "missing_count": null_cnt,
                    "percentage": round((null_cnt / total_rows) * 100, 2)
                })

        missing_info.sort(key=lambda x: x["missing_count"], reverse=True)
        return sanitize_for_json({
            "total_rows": total_rows,
            "columns_with_missing": len(missing_info),
            "missing_details": missing_info
        })

    @staticmethod
    def query_column_stats(dataset_id: str, column_name: str) -> Dict[str, Any]:
        df = DataQueryEngine.get_clean_df(dataset_id)
        if df is None:
            return {"error": "Dataset not found"}

        matched_col = next((c for c in df.columns if c.lower() == column_name.lower()), None)
        if not matched_col:
            return {"error": f"Column '{column_name}' not found."}

        series = df[matched_col].dropna()
        if len(series) == 0:
            return {"error": f"Column '{matched_col}' contains only null values."}

        if pd.api.types.is_numeric_dtype(series):
            return sanitize_for_json({
                "column": matched_col,
                "type": "numeric",
                "count": len(series),
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "p25": round(float(series.quantile(0.25)), 2),
                "p75": round(float(series.quantile(0.75)), 2)
            })
        else:
            top_vals = series.value_counts().head(5).to_dict()
            return sanitize_for_json({
                "column": matched_col,
                "type": "categorical_or_text",
                "count": len(series),
                "unique_values": int(series.nunique()),
                "top_categories": [{"value": str(k), "count": int(v)} for k, v in top_vals.items()]
            })
