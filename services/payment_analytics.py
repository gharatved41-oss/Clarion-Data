import pandas as pd
import numpy as np
from typing import Dict, Any
from services.dataset_store import dataset_store
from services.domain_detector import DomainDetectorService
from utils.helpers import detect_column_types, parse_dates_in_dataframe, sanitize_for_json

class PaymentAnalyticsService:
    """Payment Analytics Service: Status breakdown, trends, and growth metrics."""

    @staticmethod
    def analyze_payments(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"applicable": False, "reason": "Dataset not found"}

        domain_info = DomainDetectorService.detect_domain(dataset_id)
        
        # Check payment fields
        cols_lower = [str(c).lower() for c in df.columns]
        amount_col = None
        status_col = None

        for col in df.columns:
            clow = str(col).lower()
            if clow in ['amount', 'payment_amount', 'tx_amount', 'value', 'price', 'total']:
                amount_col = col
            if clow in ['status', 'payment_status', 'tx_status', 'state']:
                status_col = col

        if not amount_col and domain_info["domain"] != "payment":
            return {
                "applicable": False,
                "reason": "Dataset does not appear to contain payment information"
            }

        if not amount_col:
            # Fallback to first numeric column
            col_types = detect_column_types(df)
            num_cols = [c for c, t in col_types.items() if t == 'numeric']
            if num_cols:
                amount_col = num_cols[0]
            else:
                return {
                    "applicable": False,
                    "reason": "No numerical payment amount feature detected"
                }

        amounts = pd.to_numeric(df[amount_col], errors='coerce').fillna(0.0)
        total_amount = float(amounts.sum())
        total_count = len(df)

        completed_amount = total_amount
        pending_amount = 0.0
        failed_amount = 0.0

        completed_count = total_count
        pending_count = 0
        failed_count = 0

        if status_col:
            statuses = df[status_col].astype(str).str.lower()
            
            comp_mask = statuses.str.contains('complete|success|paid')
            pend_mask = statuses.str.contains('pend|wait|hold')
            fail_mask = statuses.str.contains('fail|declin|cancel|error')

            completed_amount = float(amounts[comp_mask].sum())
            pending_amount = float(amounts[pend_mask].sum())
            failed_amount = float(amounts[fail_mask].sum())

            completed_count = int(comp_mask.sum())
            pending_count = int(pend_mask.sum())
            failed_count = int(fail_mask.sum())

        # Payment Trends
        df_parsed, date_col = parse_dates_in_dataframe(df)
        trend = []
        growth = {}

        if date_col and df_parsed[date_col].notna().sum() >= 5:
            df_parsed[date_col] = pd.to_datetime(df_parsed[date_col])
            df_parsed[amount_col] = amounts
            df_sorted = df_parsed.sort_values(by=date_col)

            # Daily trend
            daily_series = df_sorted.groupby(df_sorted[date_col].dt.strftime("%Y-%m-%d"))[amount_col].sum()
            for d_str, val in daily_series.items():
                trend.append({
                    "date": d_str,
                    "amount": round(float(val), 2)
                })

            # Calculate growth (recent half vs previous half)
            if len(daily_series) >= 2:
                mid_idx = len(daily_series) // 2
                first_half = daily_series.iloc[:mid_idx].sum()
                second_half = daily_series.iloc[mid_idx:].sum()

                change_pct = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0.0
                growth = {
                    "historical_trend": "upward" if change_pct > 0 else "downward" if change_pct < 0 else "flat",
                    "percentage_change": round(float(change_pct), 2),
                    "previous_period_amount": round(float(first_half), 2),
                    "current_period_amount": round(float(second_half), 2)
                }

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "applicable": True,
            "total_transactions": total_count,
            "total_amount": round(total_amount, 2),
            "completed_amount": round(completed_amount, 2),
            "pending_amount": round(pending_amount, 2),
            "failed_amount": round(failed_amount, 2),
            "completed_count": completed_count,
            "pending_count": pending_count,
            "failed_count": failed_count,
            "trend": trend[:60],
            "growth": growth
        })
