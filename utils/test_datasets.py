import pandas as pd
import numpy as np
from typing import Dict

def generate_test_datasets() -> Dict[str, pd.DataFrame]:
    """Generates 11 distinct benchmark datasets for thorough testing."""
    np.random.seed(42)
    datasets = {}

    # 1. Sales Dataset
    dates = pd.date_range(start="2025-01-01", periods=100, freq="D")
    sales_df = pd.DataFrame({
        "order_id": [f"ORD-{i:04d}" for i in range(100)],
        "order_date": dates,
        "region": np.random.choice(["North", "South", "East", "West"], 100),
        "product_category": np.random.choice(["Electronics", "Clothing", "Home", "Toys"], 100),
        "revenue": np.round(np.random.uniform(50, 2000, 100) + np.linspace(10, 500, 100), 2),
        "quantity": np.random.randint(1, 20, 100),
        "discount_percent": np.random.choice([0, 5, 10, 15, 20], 100)
    })
    datasets["sales"] = sales_df

    # 2. Payment Dataset
    payment_dates = pd.date_range(start="2025-02-01", periods=80, freq="D")
    payment_df = pd.DataFrame({
        "transaction_id": [f"TXN-{1000+i}" for i in range(80)],
        "transaction_date": payment_dates,
        "payment_method": np.random.choice(["Credit Card", "UPI", "Bank Transfer", "PayPal"], 80),
        "status": np.random.choice(["Completed", "Pending", "Failed"], 80, p=[0.7, 0.2, 0.1]),
        "amount": np.round(np.random.exponential(1500, 80) + 100, 2),
        "fee": np.round(np.random.uniform(2, 50, 80), 2)
    })
    datasets["payment"] = payment_df

    # 3. Marketing Dataset
    mkt_dates = pd.date_range(start="2025-03-01", periods=60, freq="D")
    spend = np.random.uniform(100, 5000, 60)
    clicks = (spend * np.random.uniform(0.5, 1.5, 60)).astype(int) + 10
    conversions = (clicks * np.random.uniform(0.02, 0.1, 60)).astype(int)
    marketing_df = pd.DataFrame({
        "campaign_id": [f"CMP-{i}" for i in range(60)],
        "date": mkt_dates,
        "channel": np.random.choice(["Google Ads", "Meta", "LinkedIn", "TikTok"], 60),
        "spend": np.round(spend, 2),
        "clicks": clicks,
        "conversions": conversions
    })
    datasets["marketing"] = marketing_df

    # 4. Healthcare Dataset
    healthcare_df = pd.DataFrame({
        "patient_id": [f"PAT-{i:03d}" for i in range(120)],
        "age": np.random.randint(18, 85, 120),
        "bmi": np.round(np.random.normal(27, 5, 120), 1),
        "blood_pressure": np.random.randint(90, 160, 120),
        "cholesterol": np.random.randint(150, 300, 120),
        "diagnosis": np.random.choice(["Healthy", "Hypertension", "Diabetes", "Cardiac Risk"], 120)
    })
    datasets["healthcare"] = healthcare_df

    # 5. Unseen / Random Tabular Dataset
    unseen_df = pd.DataFrame({
        "feature_alpha": np.random.normal(50, 15, 90),
        "feature_beta": np.random.uniform(0, 1, 90),
        "feature_gamma": np.random.exponential(10, 90),
        "category_group": np.random.choice(["Group A", "Group B", "Group C"], 90)
    })
    datasets["unseen_tabular"] = unseen_df

    # 6. Dataset Without Dates
    nodates_df = pd.DataFrame({
        "store_id": [f"STR-{i}" for i in range(50)],
        "store_size_sqft": np.random.randint(1000, 50000, 50),
        "employee_count": np.random.randint(5, 100, 50),
        "annual_sales": np.random.uniform(500000, 10000000, 50),
        "city": np.random.choice(["New York", "London", "Tokyo", "Paris"], 50)
    })
    datasets["no_dates"] = nodates_df

    # 7. Dataset With Insufficient Numeric Features
    insufficient_num_df = pd.DataFrame({
        "user_id": [f"USR-{i}" for i in range(40)],
        "username": [f"user_{i}" for i in range(40)],
        "status": np.random.choice(["Active", "Inactive", "Banned"], 40),
        "age": np.random.randint(18, 65, 40)
    })
    datasets["insufficient_numerics"] = insufficient_num_df

    # 8. Dataset With Many Missing Values
    missing_df = pd.DataFrame({
        "item_id": [f"ITM-{i}" for i in range(70)],
        "val_a": [np.nan if i % 3 == 0 else np.random.rand() * 100 for i in range(70)],
        "val_b": [np.nan if i % 2 == 0 else np.random.rand() * 50 for i in range(70)],
        "category": [None if i % 4 == 0 else "Cat1" for i in range(70)]
    })
    datasets["missing_values"] = missing_df

    # 9. Dataset With Outliers
    outliers_vals = np.random.normal(100, 10, 100)
    outliers_vals[5] = 50000.0  # Massive outlier
    outliers_vals[25] = -20000.0 # Massive negative outlier
    outliers_df = pd.DataFrame({
        "record_id": range(100),
        "metric_x": outliers_vals,
        "metric_y": np.random.normal(50, 5, 100)
    })
    datasets["outliers"] = outliers_df

    # 10. Dataset Unsuitable for Clustering
    unsuitable_cluster_df = pd.DataFrame({
        "serial_no": range(1, 30),
        "code_name": [f"Code_{i}" for i in range(1, 30)],
        "tag": ["Standard"] * 29
    })
    datasets["unsuitable_clustering"] = unsuitable_cluster_df

    # 11. Dataset Unsuitable for Prediction
    unsuitable_pred_df = pd.DataFrame({
        "id": range(15),
        "random_noise": np.random.choice(["A", "B", "C"], 15),
        "flag": [True, False] * 7 + [True]
    })
    datasets["unsuitable_prediction"] = unsuitable_pred_df

    return datasets
