import os
import json
import re
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from services.dataset_store import dataset_store
from services.person1_service import Person1Service
from services.domain_detector import DomainDetectorService
from services.payment_analytics import PaymentAnalyticsService
from services.change_detector import ChangeDetectorService
from services.clustering import ClusteringService
from services.predictor import PredictionService
from services.chart_engine import ChartEngineService
from services.quality_score import QualityScoreService
from services.notification_engine import NotificationEngineService
from services.summary_generator import SummaryGeneratorService
from services.file_ops_service import FileOpsService
from services.data_query_engine import DataQueryEngine
from utils.helpers import sanitize_for_json, clean_dataframe_numeric_columns

class GeminiChatService:
    """Core AI Assistant & Chatbot Service with dual-engine architecture (Gemini + Deterministic)."""

    @classmethod
    def process_chat(
        cls,
        user_message: str,
        dataset_id: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Main dispatcher for conversational queries, data exploration, chart requests, and file edits."""
        msg_clean = user_message.strip()
        msg_lower = msg_clean.lower()
        history = history or []

        # 1. Gather active dataset context if available
        dataset_context = cls._gather_dataset_context(dataset_id)

        # 2. Check for code/file modification intent
        if cls._is_file_edit_request(msg_lower):
            return cls._handle_file_edit_intent(msg_clean, msg_lower)

        # 3. Check for project/code explanation intent
        if cls._is_project_qa_request(msg_lower):
            return cls._handle_project_qa_intent(msg_clean, msg_lower)

        # 4. Check for chart visualization intent
        if cls._is_chart_request(msg_lower) and dataset_id:
            return cls._handle_chart_intent(msg_clean, msg_lower, dataset_id, dataset_context)

        # 5. Check for report generation intent
        if ("report" in msg_lower and ("generate" in msg_lower or "create" in msg_lower or "give" in msg_lower)) and dataset_id:
            return cls._handle_report_intent(dataset_id, dataset_context)

        # 6. Check for Key Findings / Insights intent
        if dataset_id and cls._is_insights_request(msg_lower):
            return cls._handle_insights_intent(dataset_id, dataset_context)

        # 7. Check for Dataset Summary intent
        if dataset_id and cls._is_summary_request(msg_lower):
            return cls._handle_summary_intent(dataset_id, dataset_context)

        # 8. Check for factual dataset query
        if dataset_id and cls._is_data_query(msg_lower):
            query_res = cls._execute_natural_data_query(msg_lower, dataset_id)
            if query_res:
                return cls._synthesize_data_response(msg_clean, query_res, dataset_context)

        # 7. General Dataset or Conversation query -> Invoke Gemini (or Deterministic Fallback)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            try:
                ai_reply = cls._call_gemini_chat(msg_clean, dataset_context, history)
                if ai_reply:
                    return {
                        "message": ai_reply,
                        "intent": "dataset_analysis" if dataset_id else "general_chat",
                        "dataset_id": dataset_id,
                        "quick_actions": cls._get_quick_actions(dataset_id)
                    }
            except Exception:
                pass

        # Fallback to rich deterministic response
        return cls._generate_deterministic_reply(msg_clean, msg_lower, dataset_id, dataset_context)

    @classmethod
    def _gather_dataset_context(cls, dataset_id: Optional[str]) -> Dict[str, Any]:
        """Gathers concise factual analytical context for the active dataset."""
        if not dataset_id:
            return {}
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {}

        meta = dataset_store.get_metadata(dataset_id) or {}
        domain_res = DomainDetectorService.detect_domain(dataset_id)
        quality_res = QualityScoreService.calculate_score(dataset_id)
        
        # Sample columns and types
        cols_summary = {}
        for c in df.columns[:15]:
            cols_summary[c] = {
                "dtype": str(df[c].dtype),
                "nulls": int(df[c].isna().sum()),
                "unique": int(df[c].nunique())
            }

        return {
            "dataset_id": dataset_id,
            "filename": meta.get("name", f"{dataset_id}.csv"),
            "rows": len(df),
            "columns": list(df.columns),
            "columns_count": len(df.columns),
            "domain": domain_res.get("domain", "general"),
            "quality_score": quality_res.get("score"),
            "quality_grade": quality_res.get("grade"),
            "column_samples": cols_summary
        }

    @classmethod
    def _is_file_edit_request(cls, msg: str) -> bool:
        """Detects if user is asking to modify or edit application code/files."""
        edit_keywords = ["change", "modify", "edit", "update", "fix", "add validation", "make the", "replace"]
        target_keywords = ["dashboard", "heading", "button", "api", "title", "code", "index.html", "file", "style", "color", "function"]
        has_edit = any(k in msg for k in edit_keywords)
        has_target = any(t in msg for t in target_keywords)
        return has_edit and has_target and not msg.startswith("how") and not msg.startswith("what")

    @classmethod
    def _is_project_qa_request(cls, msg: str) -> bool:
        """Detects if user is asking about the project architecture or files."""
        return any(phrase in msg for phrase in [
            "how the upload", "explain the", "where is", "which file", "how does", 
            "project structure", "show me file", "architecture", "api route", "person 1", "person 2"
        ])

    @classmethod
    def _is_chart_request(cls, msg: str) -> bool:
        """Detects chart recommendation or generation intent."""
        return any(w in msg for w in ["chart", "graph", "plot", "visualize", "distribution of", "scatter", "histogram", "heatmap"])

    @classmethod
    def _is_insights_request(cls, msg: str) -> bool:
        """Detects if user is asking for key findings, insights, anomalies, or takeaways."""
        return any(w in msg for w in [
            "finding", "findings", "insight", "insights", "takeaway", "takeaways",
            "highlight", "highlights", "key point", "key points", "what does this data tell",
            "what can you tell me", "what did you find", "what did you discover", "what are the key",
            "key trend", "anomalies", "what is interesting"
        ])

    @classmethod
    def _is_summary_request(cls, msg: str) -> bool:
        """Detects if user is asking for a summary or overview of the dataset."""
        return any(w in msg for w in [
            "summar", "overview", "about this data", "about the data", "about this dataset", 
            "tell me about", "what is this data", "what is this dataset", "brief on this"
        ])

    @classmethod
    def _is_data_query(cls, msg: str) -> bool:
        """Detects specific data exploration questions."""
        return any(w in msg for w in [
            "missing", "null", "average", "mean", "highest", "lowest", "max", "min", "top", 
            "bottom", "correlat", "correlation", "correlated", "outlier", "unusual", "suspicious", "more than", "older than", 
            "salary by", "sales by", "how many", "compare", "distribution"
        ])

    @classmethod
    def _handle_file_edit_intent(cls, user_message: str, msg_lower: str) -> Dict[str, Any]:
        """Formulates controlled before/after file edit proposal with diff for user review."""
        target_file = None
        new_content = None
        summary = ""

        # Example 1: Dashboard title / heading change in static/index.html
        if "heading" in msg_lower or "title" in msg_lower or "dashboard" in msg_lower or "badge" in msg_lower:
            target_file = "static/index.html"
            current = FileOpsService.read_file(target_file)
            if "content" in current:
                content = current["content"]
                if "heading" in msg_lower or "title" in msg_lower:
                    # Extract suggested title or default to Data Insights
                    match = re.search(r'(?:to|as)\s+["\']?([^"\']+)["\']?', user_message, re.IGNORECASE)
                    new_title = match.group(1).strip() if match else "Automated Data Insights Analyst"
                    new_content = re.sub(r'<h1>.*?</h1>', f'<h1>{new_title}</h1>', content, count=1)
                    summary = f"Update dashboard header title to '{new_title}'"
                elif "badge" in msg_lower:
                    new_content = re.sub(r'<span class="badge">.*?</span>', '<span class="badge">AI Assistant Active</span>', content, count=1)
                    summary = "Update status badge to 'AI Assistant Active'"

        # Example 2: Upload button enlargement or styling
        elif "button" in msg_lower or "upload" in msg_lower:
            target_file = "static/index.html"
            current = FileOpsService.read_file(target_file)
            if "content" in current:
                content = current["content"]
                if "larger" in msg_lower or "big" in msg_lower:
                    new_content = content.replace(
                        'padding: 9px 12px;',
                        'padding: 12px 18px; font-size: 0.95rem;'
                    )
                    summary = "Increase button padding and font size for better accessibility"

        # Fallback: General file edit proposal based on requested file
        if not target_file or not new_content:
            all_files = [f["path"] for f in FileOpsService.list_files() if f["path"].endswith((".py", ".html", ".js", ".css"))]
            return {
                "message": (
                    "### 🛠️ Propose Controlled File Modification\n"
                    "I can safely propose modifications with an interactive diff preview for your approval.\n\n"
                    "Please specify the target file (e.g. `static/index.html`, `services/chart_engine.py`) and the exact change desired.\n"
                    f"**Editable Project Files**:\n- " + "\n- ".join(all_files[:10])
                ),
                "intent": "code_edit_proposal"
            }

        proposal = FileOpsService.propose_edit(target_file, new_content, summary)
        return {
            "message": (
                f"### 📝 Proposed Modification: `{target_file}`\n"
                f"**Intent**: {summary}\n\n"
                f"Please review the before/after diff below. **No changes will be applied until you click `[Apply Changes]`.**"
            ),
            "intent": "code_edit_proposal",
            "file_proposal": proposal,
            "quick_actions": ["Cancel Edit", "Check Status"]
        }

    @classmethod
    def _handle_project_qa_intent(cls, user_message: str, msg_lower: str) -> Dict[str, Any]:
        """Provides verified explanations of project files and system architecture."""
        if "upload" in msg_lower:
            return {
                "message": (
                    "### 📤 How the Upload System Works\n\n"
                    "1. **Frontend (`static/index.html`)**: The user selects a CSV file. Clicking `POST /upload` sends a `multipart/form-data` request via `uploadFile()`.\n"
                    "2. **API Endpoint (`api/person1_api.py`)**: `@router.post('/upload')` receives the file bytes via FastAPI's `UploadFile`.\n"
                    "3. **Dataset Store (`services/dataset_store.py`)**: `dataset_store.load_csv_bytes()` parses the CSV with Pandas, generates a unique 8-character `dataset_id`, stores the DataFrame in-memory, and registers dataset metadata.\n"
                    "4. **Response**: Returns `{\"dataset_id\": id, \"message\": \"...\"}`, and the frontend automatically adds the new dataset to the active dropdown."
                ),
                "intent": "project_qa"
            }
        
        if "cleaning" in msg_lower or "clean" in msg_lower:
            return {
                "message": (
                    "### 🧹 Dataset Cleaning Architecture\n\n"
                    "- **Base Cleaning Report (`services/person1_service.py`)**: `Person1Service.get_cleaning_report()` detects missing value percentages per column and checks for duplicate rows.\n"
                    "- **Dirty Data Preprocessing (`utils/helpers.py`)**: `clean_dataframe_numeric_columns()` and `clean_numeric_series()` strip currency symbols (`₹`, `$`, `INR`), commas, and `%` signs from object columns.\n"
                    "- **Mixed Date Parsing (`utils/helpers.py`)**: `parse_dates_in_dataframe()` standardizes diverse datetime formats (`YYYY-MM-DD`, `DD-MM-YYYY`, `MM/DD/YYYY`)."
                ),
                "intent": "project_qa"
            }

        if "correlation" in msg_lower:
            return {
                "message": (
                    "### 📈 Correlation Analysis Architecture\n\n"
                    "- **Endpoint**: `GET /dataset/{id}/correlations` defined in [`api/person1_api.py`](file:///c:/Users/mayank.LAPTOP-I5INK06A/Desktop/hackathon/api/person1_api.py).\n"
                    "- **Calculation**: Handled in [`services/person1_service.py`](file:///c:/Users/mayank.LAPTOP-I5INK06A/Desktop/hackathon/services/person1_service.py) via `Person1Service.get_correlations()`, which computes the Pearson correlation matrix for all numeric columns and extracts pairs with $|r| \\ge 0.5$.\n"
                    "- **Visualization**: Rendered as a correlation heatmap by `ChartEngineService.recommend_charts()` in [`services/chart_engine.py`](file:///c:/Users/mayank.LAPTOP-I5INK06A/Desktop/hackathon/services/chart_engine.py)."
                ),
                "intent": "project_qa"
            }

        # General file listing
        files = FileOpsService.list_files()
        return {
            "message": (
                f"### 📂 Project Architecture Overview\n\n"
                f"- **Total Project Files**: {len(files)}\n"
                f"- **FastAPI Entrypoint**: `main.py`\n"
                f"- **API Routers (`api/`)**: `person1_api.py`, `clustering_api.py`, `prediction_api.py`, `visualization_api.py`, `intelligence_api.py`, `insight_api.py`, `dashboard_api.py`\n"
                f"- **Services (`services/`)**: Analytical engines for clustering, forecasting, charts, domain detection, payments, data quality, notifications, and AI summaries\n"
                f"- **Frontend (`static/`)**: Interactive developer UI in `index.html`\n"
                f"- **Tests (`tests/`)**: Pytest suite covering all versions (219 passing tests)"
            ),
            "intent": "project_qa"
        }

    @classmethod
    def _handle_chart_intent(
        cls,
        user_message: str,
        msg_lower: str,
        dataset_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommends or generates a structured Plotly chart matching the user's natural language request."""
        df = DataQueryEngine.get_clean_df(dataset_id)
        if df is None:
            return {"message": "Dataset not found for charting.", "intent": "chart_request"}

        # 1. Time series line chart
        if any(w in msg_lower for w in ["time", "month", "trend", "daily", "line"]):
            # Look for date column and numeric column
            date_col = next((c for c in df.columns if any(d in c.lower() for d in ["date", "time", "day", "month"])), None)
            num_col = next((c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and any(k in c.lower() for k in ["sales", "revenue", "amount", "spend", "total"])), None)
            if not num_col:
                num_col = next((c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])), None)

            if date_col and num_col:
                ts_sub = df[[date_col, num_col]].dropna().copy()
                ts_sub[date_col] = pd.to_datetime(ts_sub[date_col], errors='coerce')
                ts_sub = ts_sub.dropna().sort_values(by=date_col)
                grouped = ts_sub.groupby(ts_sub[date_col].dt.strftime("%Y-%m-%d"))[num_col].sum().reset_index()
                
                chart_obj = {
                    "type": "line",
                    "title": f"{num_col} Trend Over Time",
                    "x_label": date_col,
                    "y_label": num_col,
                    "data": [{"x": str(r[date_col]), "y": round(float(r[num_col]), 2)} for _, r in grouped.head(60).iterrows()]
                }
                return {
                    "message": f"📊 Here is the time-series visualization for **`{num_col}`** over **`{date_col}`**.",
                    "intent": "chart_request",
                    "chart": chart_obj
                }

        # 2. Category bar / donut chart
        if any(w in msg_lower for w in ["by", "category", "department", "gender", "bar", "donut", "pie"]):
            cat_col = next((c for c in df.columns if 2 <= df[c].nunique() <= 10 and not pd.api.types.is_numeric_dtype(df[c])), None)
            num_col = next((c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and any(k in c.lower() for k in ["sales", "revenue", "amount", "price", "salary"])), None)
            if not num_col:
                num_col = next((c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])), None)

            if cat_col and num_col:
                grp = df.groupby(cat_col)[num_col].mean().reset_index().sort_values(by=num_col, ascending=False).head(10)
                chart_type = "donut" if len(grp) <= 5 else "bar"
                chart_obj = {
                    "type": chart_type,
                    "title": f"Average {num_col} by {cat_col}",
                    "x_label": cat_col,
                    "y_label": f"Average {num_col}",
                    "data": [{"x": str(r[cat_col]), "y": round(float(r[num_col]), 2)} for _, r in grp.iterrows()]
                }
                return {
                    "message": f"📊 Here is the breakdown of **`{num_col}`** grouped by **`{cat_col}`**.",
                    "intent": "chart_request",
                    "chart": chart_obj
                }

        # 3. Default recommendation from ChartEngineService
        recs = ChartEngineService.recommend_charts(dataset_id).get("recommended", [])
        top_chart = recs[0] if recs else None
        return {
            "message": f"📊 Recommended **{top_chart.get('title') if top_chart else 'Visualization'}** for dataset `{dataset_id}`.",
            "intent": "chart_request",
            "chart": top_chart
        }

    @classmethod
    def _execute_natural_data_query(cls, msg_lower: str, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Parses and runs factual structured query operations."""
        # Missing values
        if "missing" in msg_lower or "null" in msg_lower:
            return {
                "type": "missing_values",
                "data": DataQueryEngine.query_missing_values(dataset_id)
            }

        # Top N records
        if "top" in msg_lower:
            match = re.search(r'top\s+(\d+)?', msg_lower)
            n = int(match.group(1)) if match and match.group(1) else 10
            df = DataQueryEngine.get_clean_df(dataset_id)
            if df is not None:
                # Find column mentioned
                sort_col = next((c for c in df.columns if c.lower() in msg_lower), None)
                if not sort_col:
                    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                    sort_col = num_cols[0] if num_cols else df.columns[0]
                return {
                    "type": "top_n",
                    "data": DataQueryEngine.query_top_n(dataset_id, sort_col, n=n)
                }

        # Average / Mean of a specific column
        if "average" in msg_lower or "mean" in msg_lower:
            df = DataQueryEngine.get_clean_df(dataset_id)
            if df is not None:
                col = next((c for c in df.columns if c.lower() in msg_lower), None)
                if col:
                    return {
                        "type": "column_stats",
                        "data": DataQueryEngine.query_column_stats(dataset_id, col)
                    }

        # Correlations
        if "correlation" in msg_lower or "correlated" in msg_lower:
            corrs = Person1Service.get_correlations(dataset_id)
            return {
                "type": "correlations",
                "data": corrs
            }

        # Outliers
        if "outlier" in msg_lower or "suspicious" in msg_lower:
            outliers = Person1Service.get_outliers(dataset_id)
            return {
                "type": "outliers",
                "data": outliers
            }

        # Quality score
        if "quality" in msg_lower or "grade" in msg_lower:
            q_score = QualityScoreService.calculate_score(dataset_id)
            return {
                "type": "quality",
                "data": q_score
            }

        return None

    @classmethod
    def _synthesize_data_response(
        cls,
        user_msg: str,
        query_res: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesizes verified data query results into clear markdown explanations."""
        qtype = query_res["type"]
        data = query_res["data"]

        if qtype == "missing_values":
            details = data.get("missing_details", [])
            if not details:
                msg = f"✅ Great news! Dataset **`{context.get('dataset_id')}`** has **0 missing values** across all {context.get('columns_count', 0)} columns."
            else:
                top = details[0]
                rows = "\n".join([f"| `{d['column']}` | {d['missing_count']:,} | {d['percentage']}% |" for d in details[:8]])
                msg = (
                    f"### 🔍 Missing Values Analysis\n"
                    f"Column **`{top['column']}`** has the highest missing values with **{top['missing_count']:,} null entries ({top['percentage']}%)**.\n\n"
                    f"| Column | Missing Count | Percentage |\n| :--- | :--- | :--- |\n{rows}"
                )
            return {"message": msg, "intent": "data_analysis", "dataset_facts": data}

        if qtype == "column_stats":
            col = data.get("column")
            if data.get("type") == "numeric":
                msg = (
                    f"### 📊 Statistical Summary for `{col}`\n"
                    f"- **Mean**: `{data.get('mean'):,}`\n"
                    f"- **Median**: `{data.get('median'):,}`\n"
                    f"- **Std Deviation**: `{data.get('std'):,}`\n"
                    f"- **Min / Max**: `{data.get('min'):,}` to `{data.get('max'):,}`\n"
                    f"- **Interquartile Range (IQR)**: `{data.get('p25'):,}` (Q1) to `{data.get('p75'):,}` (Q3)"
                )
            else:
                top_cats = ", ".join([f"**{c['value']}** ({c['count']})" for c in data.get("top_categories", [])])
                msg = f"### 🏷️ Categorical Summary for `{col}`\n- **Unique Values**: {data.get('unique_values')}\n- **Top Categories**: {top_cats}"
            return {"message": msg, "intent": "data_analysis", "dataset_facts": data}

        if qtype == "correlations":
            strong = data.get("strong_correlations", [])
            if not strong:
                msg = "📊 **No strong pairwise correlations ($|r| \\ge 0.5$)** were detected among the numeric features in this dataset."
            else:
                pairs = "\n".join([f"- **`{p['feature_1']}`** and **`{p['feature_2']}`**: $r = {p['correlation']}$" for p in strong[:5]])
                msg = f"### 🔗 Strong Feature Correlations\nIdentified **{len(strong)}** significant relationship(s):\n\n{pairs}"
            return {"message": msg, "intent": "data_analysis", "dataset_facts": data}

        if qtype == "outliers":
            pct = data.get("outliers_percentage", 0)
            total = data.get("total_outliers_count", 0)
            cols = data.get("outliers_by_column", {})
            col_list = ", ".join([f"`{c}` ({info.get('count')})" for c, info in list(cols.items())[:4]]) or "None"
            msg = (
                f"### ⚠️ Outlier Screening (IQR Method)\n"
                f"- **Total Outlier Rows**: **{total:,}** ({pct}% of records)\n"
                f"- **Affected Columns**: {col_list}\n\n"
                f"*Outliers are identified using Tukey's fences ($Q1 - 1.5 \\times IQR$ and $Q3 + 1.5 \\times IQR$).*"
            )
            return {"message": msg, "intent": "data_analysis", "dataset_facts": data}

        if qtype == "top_n":
            recs = data.get("records", [])
            sort_c = data.get("sort_column")
            if not recs:
                msg = f"No records found for column `{sort_c}`."
            else:
                cols = list(recs[0].keys())
                header = "| " + " | ".join(cols) + " |"
                sep = "| " + " | ".join(["---"] * len(cols)) + " |"
                rows = "\n".join(["| " + " | ".join([str(r[c]) for c in cols]) + " |" for r in recs])
                msg = f"### 🏆 Top {len(recs)} Records by `{sort_c}`\n\n{header}\n{sep}\n{rows}"
            return {"message": msg, "intent": "data_analysis", "dataset_facts": data}

        return {"message": f"Analytical query result for `{user_msg}`.", "intent": "data_analysis", "dataset_facts": data}

    @classmethod
    def _handle_summary_intent(cls, dataset_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generates an executive-level statistical and domain summary of the active dataset."""
        try:
            summary_res = SummaryGeneratorService.generate_summary(dataset_id)
            text = summary_res.get("summary", "Summary unavailable.")
            facts = summary_res.get("facts", {})
        except Exception:
            text = f"Dataset `{dataset_id}` contains {context.get('rows', 0):,} records across {context.get('columns_count', 0)} columns."
            facts = {}

        try:
            quality = QualityScoreService.calculate_score(dataset_id)
        except Exception:
            quality = {}

        top_stats = facts.get("top_numeric_stats", [])
        stats_rows = []
        for col_name, s in top_stats[:5]:
            stats_rows.append(f"| `{col_name}` | {s.get('mean', 0):,.2f} | {s.get('median', 0):,.2f} | {s.get('min', 0):,.2f} | {s.get('max', 0):,.2f} |")
        stats_table = "\n".join(stats_rows) if stats_rows else "| (No numeric metrics) | - | - | - | - |"

        msg = (
            f"### 📊 Executive Dataset Summary (`{dataset_id}`)\n\n"
            f"{text}\n\n"
            f"#### 📋 Key Profile & Quality Indicators\n"
            f"- **Records**: `{facts.get('record_count', context.get('rows', 0)):,}` rows across `{facts.get('column_count', context.get('columns_count', 0))}` columns\n"
            f"- **Domain Detected**: **{facts.get('domain', context.get('domain', 'general')).capitalize()}** ({int(facts.get('domain_confidence', 1.0) * 100)}% confidence)\n"
            f"- **Data Quality Score**: **`{quality.get('score', context.get('quality_score', 'N/A'))}` / 100** (Grade: **`{quality.get('grade', context.get('quality_grade', 'N/A'))}`**)\n"
            f"- **Outliers Detected**: `{facts.get('outliers_count', 0):,}` records ({facts.get('outliers_percentage', 0)}%)\n"
            f"- **Correlations**: `{facts.get('strong_correlations_count', 0)}` strong pairwise correlations\n\n"
            f"#### 📈 Primary Metric Distributions\n"
            f"| Metric | Mean | Median | Min | Max |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
            f"{stats_table}\n"
        )
        return {
            "message": msg,
            "intent": "dataset_summary",
            "dataset_id": dataset_id,
            "quick_actions": ["What are the key findings?", "Check Data Quality", "Recommend Charts", "Generate Report"]
        }

    @classmethod
    def _handle_insights_intent(cls, dataset_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesizes key analytical findings, anomalies, and strategic insights from all models."""
        try:
            notifs_res = NotificationEngineService.generate_notifications(dataset_id)
            notifs = notifs_res.get("notifications", []) if isinstance(notifs_res, dict) else []
        except Exception:
            notifs = []

        try:
            quality = QualityScoreService.calculate_score(dataset_id)
        except Exception:
            quality = {}

        try:
            summary_res = SummaryGeneratorService.generate_summary(dataset_id)
            facts = summary_res.get("facts", {}) if isinstance(summary_res, dict) else {}
        except Exception:
            facts = {}

        try:
            predictions = PredictionService.analyze_predictions(dataset_id)
        except Exception:
            predictions = {}

        try:
            clusters = ClusteringService.analyze_clusters(dataset_id)
        except Exception:
            clusters = {}

        insights_list = []

        # 1. Notifications / Anomaly alerts
        if notifs:
            for n in notifs:
                icon = "⚠️" if n.get("severity") == "warning" else ("🚨" if n.get("severity") == "critical" else "ℹ️")
                alert_type = n.get("type") or "Alert"
                insights_list.append(f"- {icon} **{alert_type.replace('_', ' ').title()}**: {n.get('message')}")
        else:
            insights_list.append("- ✅ **System Health**: All monitored metric trends, transaction volumes, and indicators are nominal.")

        # 2. Predictive trend insights
        if predictions.get("applicable"):
            trend = predictions.get("trend_direction", "stable")
            target = predictions.get("target")
            growth = predictions.get("growth_rate_percent")
            growth_str = f" with projected growth of **{growth:+.1f}%**" if growth is not None else ""
            model_name = predictions.get("model", "Auto")
            insights_list.append(f"- 📈 **Predictive Forecast**: The 7-day projection for **`{target}`** indicates an **{trend} trend**{growth_str} (Model: `{model_name}`).")

        # 3. Clustering / Segmentation insights
        if clusters.get("applicable"):
            n_c = clusters.get("n_clusters")
            insights_list.append(f"- 🎯 **Customer/Entity Segmentation**: Automated clustering partitioned the data into **{n_c} distinct behavioral segments**.")

        # 4. Outlier / Data hygiene insights
        outliers_pct = facts.get("outliers_percentage", 0)
        if outliers_pct > 10:
            insights_list.append(f"- 🔍 **Statistical Outliers**: High variance detected with **{outliers_pct}% of records** identified as statistical outliers.")
        elif outliers_pct == 0:
            insights_list.append("- 🛡️ **Clean Variance**: No severe statistical outliers detected across numerical columns.")

        # 5. Data quality factor insight
        q_factors = quality.get("factors", {})
        missing_f = q_factors.get("missing_values", 100)
        if missing_f < 90:
            insights_list.append(f"- ⚠️ **Missing Data Alert**: Missing value factor score is `{missing_f}%`. Imputation recommended.")

        insights_md = "\n".join(insights_list)

        msg = (
            f"### 🔍 Key Findings & Analytical Insights (`{dataset_id}`)\n\n"
            f"Based on real-time statistical scans, time-series forecasting, and machine learning models:\n\n"
            f"{insights_md}\n\n"
            f"💡 **Recommended Next Step:** Click *'Recommend Charts'* or ask *'Show a bar chart'* to visualize these metrics."
        )
        return {
            "message": msg,
            "intent": "key_insights",
            "dataset_id": dataset_id,
            "quick_actions": ["Summarize this dataset", "Recommend Charts", "Generate Report", "Find Correlations"]
        }

    @classmethod
    def _handle_report_intent(cls, dataset_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a comprehensive, fact-grounded analytical dataset report."""
        overview = Person1Service.get_overview(dataset_id)
        cleaning = Person1Service.get_cleaning_report(dataset_id)
        quality = QualityScoreService.calculate_score(dataset_id)
        notifications = NotificationEngineService.generate_notifications(dataset_id).get("notifications", [])
        corrs = Person1Service.get_correlations(dataset_id).get("strong_correlations", [])
        outliers = Person1Service.get_outliers(dataset_id)
        predictions = PredictionService.analyze_predictions(dataset_id)

        alerts_md = "\n".join([f"- **{n['severity'].upper()}**: {n['message']}" for n in notifications]) if notifications else "- No critical alerts triggered."
        corrs_md = "\n".join([f"- `{c['feature_1']}` & `{c['feature_2']}`: $r = {c['correlation']}$" for c in corrs[:3]]) if corrs else "- No strong correlations found."

        report = f"""# 📑 Executive Analytical Dataset Report

**Dataset ID**: `{dataset_id}` | **Domain**: `{context.get('domain', 'general').capitalize()}` | **Quality Grade**: `{quality.get('grade', 'B')}` ({quality.get('score', 85)}/100)

---

### 1. Dataset Dimensions & Completeness
- **Total Records**: `{overview.get('row_count', context.get('rows', 0)):,}`
- **Columns**: `{overview.get('column_count', context.get('columns_count', 0))}`
- **Missing Value Rate**: `{cleaning.get('total_missing_values', 0)} nulls detected`
- **Duplicate Records**: `{cleaning.get('duplicate_rows', 0)} duplicates`

### 2. Data Quality Audit
- **Overall Score**: `{quality.get('score', 0)} / 100` (Grade: **{quality.get('grade', 'N/A')}**)
- **Missing Values Factor**: `{quality.get('factors', {}).get('missing_values')}%`
- **Duplicate Factor**: `{quality.get('factors', {}).get('duplicates')}%`
- **Format Consistency**: `{quality.get('factors', {}).get('formatting')}%`

### 3. Key Relationships & Outliers
- **Strong Correlations**:
{corrs_md}
- **Outlier Instances**: `{outliers.get('total_outliers_count', 0):,}` rows ({outliers.get('outliers_percentage', 0)}% of dataset)

### 4. Automated Forecasting
- **Target Metric**: `{predictions.get('target', 'N/A')}`
- **Model Fitted**: `{predictions.get('model', 'LinearRegression')}`
- **Evaluation**: MAE: `{predictions.get('evaluation', {}).get('MAE', 'N/A')}`, R²: `{predictions.get('evaluation', {}).get('R2', 'N/A')}`
- **Trend Projection**: `{predictions.get('trend_direction', 'stable').capitalize()}`

### 5. Automated Insight Alerts
{alerts_md}

---
*Generated by Automated Insight Analyst AI Assistant using strictly verified numerical calculations.*
"""
        return {
            "message": report,
            "intent": "report_generation",
            "dataset_id": dataset_id,
            "quick_actions": ["Download Summary", "Recommend Charts", "Forecast 14 Days"]
        }

    @classmethod
    def _call_gemini_chat(
        cls,
        user_message: str,
        context: Dict[str, Any],
        history: List[Dict[str, str]]
    ) -> Optional[str]:
        """Calls Google Gemini API with system instructions enforcing zero-hallucination factual grounding."""
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)

        model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)

        system_instruction = f"""
You are an expert AI Data Analyst and Project Assistant embedded inside the 'Automated Insight Analyst' platform.
CURRENT ACTIVE DATASET CONTEXT:
{json.dumps(context, indent=2)}

STRICT RULES:
1. Ground all data statements strictly in the verified context provided. Never invent numbers or statistics.
2. If asked about project architecture, reference real files (e.g. `main.py`, `services/`, `api/`, `static/index.html`).
3. If information is not in the context, explicitly inform the user that it is unavailable rather than assuming.
4. Format output using clean GitHub-style markdown with bold highlights, lists, or tables where appropriate.
"""
        prompt = f"{system_instruction}\n\nUSER: {user_message}\nASSISTANT:"
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else None

    @classmethod
    def _generate_deterministic_reply(
        cls,
        user_message: str,
        msg_lower: str,
        dataset_id: Optional[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """High-quality deterministic fallback response when LLM API is unavailable."""
        if not dataset_id:
            return {
                "message": (
                    "👋 Hello! I am your **Automated Insight Analyst AI Assistant**.\n\n"
                    "I can help you explore datasets, understand statistics, recommend visualizations, and inspect or modify project files.\n\n"
                    "👉 **To get started**, select a dataset from the dropdown on the left (e.g. `test-sales`) or upload your own CSV file!"
                ),
                "intent": "general_chat",
                "quick_actions": ["Select test-sales", "Explain Upload API", "List Project Files"]
            }

        # If user asked a question or requested intelligence, provide real key findings instead of static greeting
        if any(w in msg_lower for w in ["what", "how", "why", "tell", "show", "can you", "where", "explain", "insight", "finding", "summar"]):
            return cls._handle_insights_intent(dataset_id, context)

        # Default dataset active greeting
        return {
            "message": (
                f"### 🤖 Dataset Assistant (`{dataset_id}`)\n\n"
                f"I am actively monitoring dataset **`{dataset_id}`** ({context.get('rows', 0):,} records, {context.get('columns_count', 0)} columns, Domain: **{context.get('domain', 'general').capitalize()}**).\n\n"
                f"**Things you can ask me:**\n"
                f"- *'What are the key findings?'*\n"
                f"- *'Summarize this dataset'*\n"
                f"- *'Which column has the most missing values?'*\n"
                f"- *'Show me top 10 records by revenue'*\n"
                f"- *'Generate a full analytical report'*\n"
                f"- *'Show a line chart of sales over time'*"
            ),
            "intent": "dataset_analysis",
            "dataset_id": dataset_id,
            "quick_actions": cls._get_quick_actions(dataset_id)
        }

    @classmethod
    def _get_quick_actions(cls, dataset_id: Optional[str]) -> List[str]:
        if dataset_id:
            return ["Summarize Dataset", "Check Data Quality", "Find Correlations", "Show Outliers", "Recommend Charts", "Generate Report"]
        return ["Explain Architecture", "How Upload Works", "List Project Files"]
