import pandas as pd
import numpy as np
from typing import Dict, Any, List
from services.dataset_store import dataset_store
from services.clustering import ClusteringService
from utils.helpers import detect_column_types, parse_dates_in_dataframe, sanitize_for_json, clean_numeric_series, clean_dataframe_numeric_columns

class ChartEngineService:
    """Automatic Chart Recommendation & Structured Configuration Engine."""

    @staticmethod
    def recommend_charts(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"dataset_id": dataset_id, "recommended": []}

        df_parsed, date_col = parse_dates_in_dataframe(df)
        df_parsed = clean_dataframe_numeric_columns(df_parsed)
        col_types = detect_column_types(df_parsed)

        numeric_cols = [c for c, t in col_types.items() if t == 'numeric']
        cat_cols = [c for c, t in col_types.items() if t == 'categorical']

        # Ensure all numeric candidate columns are converted to clean float series
        for col in numeric_cols:
            df_parsed[col] = clean_numeric_series(df_parsed[col])

        # Filter numeric columns that have at least some non-null values
        numeric_cols = [c for c in numeric_cols if df_parsed[c].notna().sum() > 0]

        recommended = []

        # 1. Date + Numeric -> Line Chart
        if date_col and len(numeric_cols) > 0:
            target_num = numeric_cols[0]
            # Prioritize commercial metric names like revenue or sales if present
            for c in numeric_cols:
                if any(kw in c.lower() for kw in ['total_sales', 'revenue', 'amount', 'sales', 'spend', 'total']):
                    target_num = c
                    break

            ts_data = df_parsed[[date_col, target_num]].dropna().copy()
            try:
                ts_data[date_col] = pd.to_datetime(ts_data[date_col], format='mixed', errors='coerce')
            except Exception:
                ts_data[date_col] = pd.to_datetime(ts_data[date_col], errors='coerce')
            
            ts_data[target_num] = pd.to_numeric(ts_data[target_num], errors='coerce')
            ts_data = ts_data.dropna().sort_values(by=date_col)

            if len(ts_data) > 0:
                # Group daily
                grouped = ts_data.groupby(ts_data[date_col].dt.strftime("%Y-%m-%d"))[target_num].sum().reset_index()
                grouped.columns = ["x", "y"]

                recommended.append({
                    "id": "chart_line_time_series",
                    "type": "line",
                    "title": f"{target_num} Over Time",
                    "x_label": date_col,
                    "y_label": target_num,
                    "data": grouped.to_dict(orient="records")[:100]
                })

        # 2. Category + Numeric -> Bar / Column Chart
        if len(cat_cols) > 0 and len(numeric_cols) > 0:
            best_cat = cat_cols[0]
            target_num = numeric_cols[0]

            for c in numeric_cols:
                if any(kw in c.lower() for kw in ['total_sales', 'revenue', 'amount', 'sales', 'spend', 'total']):
                    target_num = c
                    break

            for c in cat_cols:
                if df_parsed[c].nunique() >= 2 and df_parsed[c].nunique() <= 12:
                    best_cat = c
                    break

            cat_df = df_parsed[[best_cat, target_num]].dropna().copy()
            cat_df[target_num] = pd.to_numeric(cat_df[target_num], errors='coerce')
            cat_df = cat_df.dropna()

            if len(cat_df) > 0:
                grouped_cat = cat_df.groupby(best_cat)[target_num].mean().reset_index()
                grouped_cat.columns = ["x", "y"]
                grouped_cat = grouped_cat.sort_values(by="y", ascending=False)

                chart_type = "donut" if df_parsed[best_cat].nunique() <= 5 else "bar"

                recommended.append({
                    "id": f"chart_cat_{best_cat}",
                    "type": chart_type,
                    "title": f"Average {target_num} by {best_cat}",
                    "x_label": best_cat,
                    "y_label": f"Average {target_num}",
                    "data": grouped_cat.to_dict(orient="records")
                })

        # 3. Multi-Numeric Correlation Heatmap
        if len(numeric_cols) >= 3:
            sub_num = df_parsed[numeric_cols[:6]].dropna().copy()
            for col in numeric_cols[:6]:
                sub_num[col] = pd.to_numeric(sub_num[col], errors='coerce')
            sub_num = sub_num.dropna()
            if len(sub_num) > 2:
                corr_mat = sub_num.corr().round(2).fillna(0.0).to_dict()
                recommended.append({
                    "id": "chart_correlation_heatmap",
                    "type": "heatmap",
                    "title": "Feature Correlation Heatmap",
                    "columns": numeric_cols[:6],
                    "matrix": corr_mat
                })

        # 4. Outlier Boxplot
        if len(numeric_cols) >= 1:
            target_num = numeric_cols[0]
            for c in numeric_cols:
                if any(kw in c.lower() for kw in ['total_sales', 'revenue', 'amount', 'sales', 'spend', 'total']):
                    target_num = c
                    break
            box_data = df_parsed[target_num].dropna().tolist()[:200]
            recommended.append({
                "id": "chart_outlier_box",
                "type": "boxplot",
                "title": f"Distribution & Outliers for {target_num}",
                "y_label": target_num,
                "data": box_data
            })

        # 5. Cluster Scatter Plot (if clustering applies)
        cluster_res = ClusteringService.analyze_clusters(dataset_id)
        if cluster_res.get("applicable") and len(cluster_res.get("features_used", [])) >= 2:
            feat1, feat2 = cluster_res["features_used"][:2]
            df_parsed[feat1] = clean_numeric_series(df_parsed[feat1])
            df_parsed[feat2] = clean_numeric_series(df_parsed[feat2])
            sub_cluster = df_parsed[[feat1, feat2]].dropna().copy()
            c_assignments = cluster_res.get("cluster_assignments", [])
            
            if len(c_assignments) >= len(sub_cluster):
                sub_cluster["cluster"] = c_assignments[:len(sub_cluster)]
            else:
                sub_cluster = sub_cluster.iloc[:len(c_assignments)].copy()
                sub_cluster["cluster"] = c_assignments
            
            scatter_data = []
            for _, row in sub_cluster.iterrows():
                scatter_data.append({
                    "x": float(row[feat1]),
                    "y": float(row[feat2]),
                    "cluster": int(row["cluster"])
                })

            recommended.append({
                "id": "chart_cluster_scatter",
                "type": "scatter",
                "title": f"Clusters ({feat1} vs {feat2})",
                "x_label": feat1,
                "y_label": feat2,
                "data": scatter_data[:150]
            })

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "recommended": recommended[:4] # Limit to top 2-4 recommendations
        })

    @staticmethod
    def get_chart_options(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"dataset_id": dataset_id, "available_charts": []}

        df_parsed, date_col = parse_dates_in_dataframe(df)
        col_types = detect_column_types(df_parsed)
        numeric_cols = [c for c, t in col_types.items() if t == 'numeric']
        cat_cols = [c for c, t in col_types.items() if t == 'categorical']
        dt_cols = [c for c, t in col_types.items() if t == 'datetime']
        if date_col and date_col not in dt_cols:
            dt_cols.append(date_col)

        available = [
            {
                "chart_type": "line",
                "title": "Time Series Line Chart",
                "description": "Visualize numeric metric trends across time",
                "x_options": dt_cols if dt_cols else list(df.columns),
                "y_options": numeric_cols
            },
            {
                "chart_type": "bar",
                "title": "Category Comparison Bar Chart",
                "description": "Compare numeric metrics across categorical buckets",
                "x_options": cat_cols if cat_cols else list(df.columns),
                "y_options": numeric_cols
            },
            {
                "chart_type": "scatter",
                "title": "Correlation Scatter Plot",
                "description": "Analyze relationship between two numeric features",
                "x_options": numeric_cols,
                "y_options": numeric_cols
            },
            {
                "chart_type": "histogram",
                "title": "Distribution Histogram",
                "description": "View frequency distribution of a numeric column",
                "x_options": numeric_cols,
                "y_options": []
            }
        ]

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "available_charts": available
        })
