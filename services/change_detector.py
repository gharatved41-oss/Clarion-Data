import pandas as pd
import numpy as np
from typing import Dict, Any
from services.dataset_store import dataset_store
from utils.helpers import detect_column_types, parse_dates_in_dataframe, sanitize_for_json

class ChangeDetectorService:
    """Time-based comparison engine (Daily, Weekly, Monthly) for key metrics & category changes."""

    @staticmethod
    def detect_changes(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"dataset_id": dataset_id, "error": "Dataset not found"}

        df_parsed, date_col = parse_dates_in_dataframe(df)
        if not date_col or df_parsed[date_col].notna().sum() < 5:
            return sanitize_for_json({
                "dataset_id": dataset_id,
                "applicable": False,
                "reason": "Insufficient date/time information for period comparison"
            })

        df_parsed[date_col] = pd.to_datetime(df_parsed[date_col])
        df_sorted = df_parsed.sort_values(by=date_col)

        col_types = detect_column_types(df_sorted)
        numeric_cols = [c for c, t in col_types.items() if t == 'numeric']
        cat_cols = [c for c, t in col_types.items() if t == 'categorical']

        if not numeric_cols:
            return sanitize_for_json({
                "dataset_id": dataset_id,
                "applicable": False,
                "reason": "No numeric metric found for change detection"
            })

        primary_metric = numeric_cols[0]
        for c in numeric_cols:
            if any(kw in c.lower() for kw in ['revenue', 'amount', 'sales', 'spend', 'clicks']):
                primary_metric = c
                break

        # Generate comparison functions for periods
        daily_change = ChangeDetectorService._compare_periods(df_sorted, date_col, primary_metric, cat_cols, freq="D")
        weekly_change = ChangeDetectorService._compare_periods(df_sorted, date_col, primary_metric, cat_cols, freq="W")
        monthly_change = ChangeDetectorService._compare_periods(df_sorted, date_col, primary_metric, cat_cols, freq="M")

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "applicable": True,
            "primary_metric": primary_metric,
            "daily": daily_change,
            "weekly": weekly_change,
            "monthly": monthly_change
        })

    @staticmethod
    def _compare_periods(df: pd.DataFrame, date_col: str, metric_col: str, cat_cols: list, freq: str) -> Dict[str, Any]:
        try:
            # Resample or group by period
            period_df = df.set_index(date_col).resample(freq).agg({
                metric_col: ['sum', 'count']
            }).dropna()

            if len(period_df) < 2:
                return {"message": f"Insufficient {freq} periods available for comparison"}

            latest = period_df.iloc[-1]
            previous = period_df.iloc[-2]

            latest_val = float(latest[(metric_col, 'sum')])
            prev_val = float(previous[(metric_col, 'sum')])

            latest_cnt = int(latest[(metric_col, 'count')])
            prev_cnt = int(previous[(metric_col, 'count')])

            metric_change_pct = ((latest_val - prev_val) / prev_val * 100) if prev_val > 0 else 0.0
            tx_change_pct = ((latest_cnt - prev_cnt) / prev_cnt * 100) if prev_cnt > 0 else 0.0

            # Detect category shifts if category columns exist
            new_categories = []
            if cat_cols:
                primary_cat = cat_cols[0]
                max_date = df[date_col].max()
                split_date = max_date - pd.Timedelta(days=7 if freq=="W" else 30 if freq=="M" else 1)
                
                recent_cats = set(df[df[date_col] >= split_date][primary_cat].dropna().unique())
                older_cats = set(df[df[date_col] < split_date][primary_cat].dropna().unique())
                new_categories = list(recent_cats - older_cats)

            return {
                f"{metric_col}_change_percent": round(metric_change_pct, 2),
                "transaction_change_percent": round(tx_change_pct, 2),
                "latest_period_sum": round(latest_val, 2),
                "previous_period_sum": round(prev_val, 2),
                "new_categories_detected": new_categories[:5]
            }
        except Exception:
            return {"message": f"Could not aggregate comparison for frequency {freq}"}
