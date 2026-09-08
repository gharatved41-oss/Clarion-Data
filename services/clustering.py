import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from services.dataset_store import dataset_store
from utils.helpers import detect_column_types, sanitize_for_json, clean_numeric_series, clean_dataframe_numeric_columns

class ClusteringService:
    """Automatic K-Means Clustering Service with applicability checks."""

    @staticmethod
    def analyze_clusters(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"applicable": False, "reason": "Dataset not found"}

        if len(df) < 10:
            return {
                "applicable": False,
                "reason": "Insufficient valid observations (minimum 10 rows required)"
            }

        df_clean = clean_dataframe_numeric_columns(df)
        col_types = detect_column_types(df_clean)
        numeric_cols = [col for col, ctype in col_types.items() if ctype == 'numeric']

        # Filter out ID-like numeric columns or constant columns
        suitable_cols = []
        for col in numeric_cols:
            series = pd.to_numeric(df_clean[col], errors='coerce').dropna()
            if len(series) < 0.5 * len(df_clean):
                continue
            if series.nunique() <= 1:
                continue
            if series.nunique() == len(df_clean) and (series.max() - series.min() == len(df_clean) - 1):
                # Likely sequential index
                continue
            suitable_cols.append(col)

        if len(suitable_cols) < 2:
            return {
                "applicable": False,
                "reason": "Insufficient suitable numeric features (at least 2 required for clustering)"
            }

        # Extract numeric dataframe and handle missing values
        clean_sub = df_clean[suitable_cols].copy()
        for col in suitable_cols:
            clean_sub[col] = pd.to_numeric(clean_sub[col], errors='coerce')
            clean_sub[col] = clean_sub[col].fillna(clean_sub[col].median())

        # Check if all variance is zero after imputation
        if clean_sub.std().sum() == 0 or np.isnan(clean_sub.std().sum()):
            return {
                "applicable": False,
                "reason": "Numeric features have zero variance or non-numeric values"
            }

        # Standardize features
        scaler = StandardScaler()
        scaled_matrix = scaler.fit_transform(clean_sub)

        # Determine optimal clusters between 2 and min(6, len(df)-1)
        max_k = min(6, len(clean_sub) - 1)
        if max_k < 2:
            return {
                "applicable": False,
                "reason": "Not enough sample data points to form multiple clusters"
            }

        best_k = 2
        best_score = -1.0

        # Sample for silhouette score if dataset is very large
        if len(scaled_matrix) > 1000:
            sample_indices = np.random.choice(len(scaled_matrix), size=1000, replace=False)
            eval_matrix = scaled_matrix[sample_indices]
        else:
            eval_matrix = scaled_matrix

        for k in range(2, max_k + 1):
            try:
                kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels_temp = kmeans_temp.fit_predict(eval_matrix)
                score = silhouette_score(eval_matrix, labels_temp)
                if score > best_score:
                    best_score = score
                    best_k = k
            except Exception:
                continue

        # Fit final KMeans with optimal k
        final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        cluster_labels = final_kmeans.fit_predict(scaled_matrix)

        # Build cluster summaries
        clean_sub['cluster'] = cluster_labels
        clusters_summary = []

        for cluster_id in range(best_k):
            cluster_data = clean_sub[clean_sub['cluster'] == cluster_id]
            size = len(cluster_data)
            
            characteristics = {}
            for col in suitable_cols:
                characteristics[f"{col}_mean"] = round(float(cluster_data[col].mean()), 2)
                characteristics[f"{col}_std"] = round(float(cluster_data[col].std()), 2) if size > 1 else 0.0

            clusters_summary.append({
                "cluster": cluster_id,
                "size": size,
                "characteristics": characteristics
            })

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "applicable": True,
            "algorithm": "KMeans",
            "n_clusters": best_k,
            "features_used": suitable_cols,
            "clusters": clusters_summary,
            "cluster_assignments": cluster_labels.tolist()[:100]  # First 100 sample assignments
        })
