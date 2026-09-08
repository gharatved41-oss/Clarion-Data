import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from services.dataset_store import dataset_store
from services.person1_service import Person1Service
from services.domain_detector import DomainDetectorService
from services.clustering import ClusteringService
from services.predictor import PredictionService
from services.change_detector import ChangeDetectorService
from utils.helpers import sanitize_for_json

load_dotenv()

class SummaryGeneratorService:
    """Fact-based AI Summary & Natural Language Insight Generator."""

    @staticmethod
    def generate_summary(dataset_id: str) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"dataset_id": dataset_id, "summary": "Dataset not found.", "facts": {}}

        # STEP 1: Python calculates all factual analytical results
        try:
            overview = Person1Service.get_overview(dataset_id)
        except Exception:
            overview = {}

        domain_res = DomainDetectorService.detect_domain(dataset_id)

        try:
            analysis = Person1Service.get_analysis(dataset_id)
        except Exception:
            analysis = {}

        try:
            correlations = Person1Service.get_correlations(dataset_id)
        except Exception:
            correlations = {}

        try:
            outliers = Person1Service.get_outliers(dataset_id)
        except Exception:
            outliers = {}

        clusters = ClusteringService.analyze_clusters(dataset_id)
        predictions = PredictionService.analyze_predictions(dataset_id)
        changes = ChangeDetectorService.detect_changes(dataset_id)

        facts = {
            "record_count": overview.get("row_count", 0),
            "column_count": overview.get("column_count", 0),
            "domain": domain_res.get("domain", "general"),
            "domain_confidence": domain_res.get("confidence", 0.5),
            "top_numeric_stats": list(analysis.get("numeric_stats", {}).items())[:3],
            "strong_correlations_count": len(correlations.get("strong_correlations", [])),
            "strong_correlations": correlations.get("strong_correlations", [])[:3],
            "outliers_count": outliers.get("total_outliers_count", 0),
            "outliers_percentage": outliers.get("outliers_percentage", 0),
            "clustering_applicable": clusters.get("applicable", False),
            "n_clusters": clusters.get("n_clusters", 0),
            "prediction_applicable": predictions.get("applicable", False),
            "prediction_target": predictions.get("target"),
            "prediction_model": predictions.get("model"),
            "prediction_r2": predictions.get("evaluation", {}).get("R2"),
            "changes": changes.get("daily", {})
        }

        # STEP 2: Try LLM generation via Gemini API if key exists; else use deterministic generator
        summary_text = None
        api_key = os.getenv("GEMINI_API_KEY")

        if api_key and api_key != "your_gemini_api_key_here":
            try:
                summary_text = SummaryGeneratorService._generate_with_gemini(facts, api_key)
            except Exception:
                summary_text = None

        if not summary_text:
            summary_text = SummaryGeneratorService._generate_deterministic_summary(facts)

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "summary": summary_text,
            "facts": facts
        })

    @staticmethod
    def _generate_with_gemini(facts: Dict[str, Any], api_key: str) -> str:
        """Invokes Google Gemini API with strict factual grounding instructions."""
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)

        prompt = f"""
You are an expert AI Data Analyst. Summarize the following structured analytical facts into a clear, concise natural language overview (paragraph form, 3-5 sentences).

FACTS:
{json.dumps(facts, indent=2)}

STRICT RULES:
1. Base your summary ONLY on the provided facts above. Do NOT invent numbers or trends.
2. Do NOT claim causation (e.g. do not say "X caused Y"); only mention correlations or observed patterns.
3. Include record count, detected domain, major metric insights, correlations, outliers, and prediction results if applicable.
"""
        response = model.generate_content(prompt)
        return response.text.strip()

    @staticmethod
    def _generate_deterministic_summary(facts: Dict[str, Any]) -> str:
        """Deterministic rule-based summary generator when LLM API key is not present."""
        domain = facts["domain"].capitalize()
        recs = facts["record_count"]
        cols = facts["column_count"]

        parts = [
            f"The dataset contains {recs:,} records across {cols} columns and appears to represent {domain.lower()} activity."
        ]

        # Metric highlights
        if facts["top_numeric_stats"]:
            first_stat_col, first_stat_vals = facts["top_numeric_stats"][0]
            mean_val = round(first_stat_vals.get("mean", 0), 2)
            parts.append(f"The primary numeric metric '{first_stat_col}' exhibits an average value of {mean_val:,.2f}.")

        # Correlation insights
        corr_cnt = facts["strong_correlations_count"]
        if corr_cnt > 0:
            top_corr = facts["strong_correlations"][0]
            f1, f2 = top_corr["feature_1"], top_corr["feature_2"]
            val = top_corr["correlation"]
            parts.append(f"A strong correlation of {val} was identified between {f1} and {f2}.")
        else:
            parts.append("No strong pairwise column correlations were detected.")

        # Outliers insights
        out_cnt = facts["outliers_count"]
        out_pct = facts["outliers_percentage"]
        if out_cnt > 0:
            parts.append(f"Statistical screening detected {out_cnt} outlier instances ({out_pct}% of total records).")

        # Predictions/Clustering insights
        if facts["prediction_applicable"]:
            target = facts["prediction_target"]
            model = facts["prediction_model"]
            parts.append(f"Automated forecasting successfully fitted a {model} model for target metric '{target}'.")
        elif facts["clustering_applicable"]:
            n_c = facts["n_clusters"]
            parts.append(f"Unsupervised clustering grouped the dataset into {n_c} distinct sub-segments.")

        return " ".join(parts)
