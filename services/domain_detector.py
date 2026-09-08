import pandas as pd
from typing import Dict, Any, List
from services.dataset_store import dataset_store
from utils.helpers import detect_column_types, sanitize_for_json

class DomainDetectorService:
    """Automatic Domain Detection Engine based on column patterns, data types, and value distributions."""

    @staticmethod
    def detect_domain(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"dataset_id": dataset_id, "domain": "general", "confidence": 0.0, "evidence": ["Dataset not found"]}

        cols_lower = [str(c).lower() for c in df.columns]
        col_types = detect_column_types(df)
        evidence = []

        sales_score = 0.0
        payment_score = 0.0
        marketing_score = 0.0
        healthcare_score = 0.0

        # Domain Keyword Maps
        sales_keywords = ['sale', 'revenue', 'order', 'product', 'quantity', 'discount', 'sku', 'price', 'store', 'customer']
        payment_keywords = ['transaction', 'payment', 'fee', 'status', 'payer', 'card', 'bank', 'upi', 'merchant', 'completed', 'pending', 'failed']
        marketing_keywords = ['campaign', 'click', 'conversion', 'impression', 'cpc', 'ctr', 'ad', 'spend', 'channel', 'lead']
        healthcare_keywords = ['patient', 'doctor', 'hospital', 'diagnosis', 'bp', 'blood_pressure', 'cholesterol', 'bmi', 'age', 'treatment', 'dose', 'symptom']

        # 1. Column Name Pattern Matching
        for col in cols_lower:
            if any(kw in col for kw in sales_keywords):
                sales_score += 0.25
            if any(kw in col for kw in payment_keywords):
                payment_score += 0.25
            if any(kw in col for kw in marketing_keywords):
                marketing_score += 0.25
            if any(kw in col for kw in healthcare_keywords):
                healthcare_score += 0.25

        # 2. Value Inspection & Category Patterns
        for col in df.columns:
            series_str = df[col].dropna().astype(str).str.lower()
            unique_vals = set(series_str.head(100).unique())

            # Payment status values check
            if len({'completed', 'pending', 'failed', 'refunded', 'success'}.intersection(unique_vals)) > 0:
                payment_score += 0.4
                evidence.append(f"Payment status values detected in column '{col}'")

            # Payment method values check
            if len({'credit card', 'upi', 'paypal', 'bank transfer', 'stripe', 'debit'}.intersection(unique_vals)) > 0:
                payment_score += 0.3
                evidence.append(f"Payment method values detected in column '{col}'")

            # Marketing channel values check
            if len({'google ads', 'meta', 'facebook', 'linkedin', 'tiktok', 'seo'}.intersection(unique_vals)) > 0:
                marketing_score += 0.3
                evidence.append(f"Marketing channel values detected in column '{col}'")

            # Healthcare diagnosis / status check
            if len({'healthy', 'hypertension', 'diabetes', 'cardiac risk', 'cancer', 'outpatient'}.intersection(unique_vals)) > 0:
                healthcare_score += 0.4
                evidence.append(f"Healthcare diagnosis terms detected in column '{col}'")

        # 3. Data Structure Relationships
        has_date = any(t == 'datetime' for t in col_types.values())
        numeric_count = sum(1 for t in col_types.values() if t == 'numeric')

        if has_date:
            evidence.append("Date field detected")
        if numeric_count >= 1:
            evidence.append(f"{numeric_count} numeric fields detected")

        # Select Domain with Highest Score
        scores = {
            "sales": sales_score,
            "payment": payment_score,
            "marketing": marketing_score,
            "healthcare": healthcare_score
        }

        top_domain = max(scores, key=scores.get)
        top_score = scores[top_domain]

        if top_score < 0.3:
            return sanitize_for_json({
                "dataset_id": dataset_id,
                "domain": "general",
                "confidence": 0.5,
                "evidence": ["General tabular dataset with non-specific feature names"]
            })

        # Calculate confidence
        confidence = min(0.98, round(0.5 + (top_score * 0.3), 2))
        
        # Add matching evidence details
        if top_domain == "sales":
            evidence.append("Sales metrics (revenue, orders, product categories) detected")
        elif top_domain == "payment":
            evidence.append("Payment transaction fields (status, transaction IDs, payment methods) detected")
        elif top_domain == "marketing":
            evidence.append("Marketing campaign metrics (spend, clicks, conversions) detected")
        elif top_domain == "healthcare":
            evidence.append("Clinical or patient demographic metrics (age, blood pressure, diagnosis) detected")

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "domain": top_domain,
            "confidence": confidence,
            "evidence": list(set(evidence))
        })
