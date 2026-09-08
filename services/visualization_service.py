"""Service for automated visualization recommendations and chart specification synthesis."""
import logging
import math
import numpy as np
import pandas as pd

from app.schemas.dataset import (
    ChartDataPoint,
    ChartSeries,
    ChartSpecification,
    DatasetVisualizationsResponse,
)
from app.services.cleaning_service import CleaningService
from app.services.schema_service import SchemaService

logger = logging.getLogger("app.services.visualization_service")


def _safe_float(v) -> float | None:
    if v is None or pd.isna(v):
        return None
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 2)
    except (ValueError, TypeError):
        return None


class VisualizationService:
    """Automated chart recommendation and payload construction engine."""

    @classmethod
    def generate_visualizations(cls, dataset_id: str) -> DatasetVisualizationsResponse:
        """Analyze dataset structure and generate tailored visual specifications."""
        df, _ = CleaningService.load_cleaned_dataset(dataset_id)
        schema_res = SchemaService.detect_schema(dataset_id)
        schema_map = {col.name: col.type for col in schema_res.columns}

        numeric_cols = [c for c in df.columns if schema_map.get(str(c)) == "numeric"]
        categorical_cols = [c for c in df.columns if schema_map.get(str(c)) == "categorical"]
        datetime_cols = [c for c in df.columns if schema_map.get(str(c)) == "datetime"]

        charts: list[ChartSpecification] = []

        # ---------------------------------------------------------------------
        # 1. Categorical Distribution (Donut / Pie Chart)
        # ---------------------------------------------------------------------
        if categorical_cols:
            cat_col = categorical_cols[0]
            val_counts = df[cat_col].dropna().value_counts().head(8)
            total = int(val_counts.sum())

            if total > 0:
                data_points = [
                    ChartDataPoint(
                        label=str(k),
                        value=int(v),
                        secondary_value=_safe_float((v / total) * 100.0)
                    )
                    for k, v in val_counts.items()
                ]
                charts.append(ChartSpecification(
                    id=f"donut_{cat_col}",
                    title=f"Distribution of {cat_col.replace('_', ' ').title()}",
                    chart_type="donut",
                    x_axis_label=cat_col,
                    y_axis_label="Count & Percentage",
                    description=f"Breakdown of observations across top {len(data_points)} categories in '{cat_col}'.",
                    series=[ChartSeries(name=cat_col, data=data_points)]
                ))

        # ---------------------------------------------------------------------
        # 2. Aggregated Bivariate Comparison (Bar Chart: Numeric by Category)
        # ---------------------------------------------------------------------
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]

            try:
                # Group by top categories and compute mean
                top_cats = df[cat_col].value_counts().head(8).index
                grouped = (
                    df[df[cat_col].isin(top_cats)]
                    .groupby(cat_col)[num_col]
                    .mean()
                    .dropna()
                    .sort_values(ascending=False)
                )

                if len(grouped) > 0:
                    data_points = [
                        ChartDataPoint(
                            label=str(k),
                            value=_safe_float(v) or 0.0
                        )
                        for k, v in grouped.items()
                    ]
                    charts.append(ChartSpecification(
                        id=f"bar_{cat_col}_{num_col}",
                        title=f"Average {num_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}",
                        chart_type="bar",
                        x_axis_label=cat_col.replace('_', ' ').title(),
                        y_axis_label=f"Avg {num_col.replace('_', ' ').title()}",
                        description=f"Compares the average magnitude of '{num_col}' across dominant segments of '{cat_col}'.",
                        series=[ChartSeries(name=f"Avg {num_col}", data=data_points)]
                    ))
            except Exception as err:
                logger.warning(f"Could not build bivariate bar chart: {err}")

        # ---------------------------------------------------------------------
        # 3. Time Series Trends (Line Chart)
        # ---------------------------------------------------------------------
        if datetime_cols:
            dt_col = datetime_cols[0]
            try:
                parsed_dates = pd.to_datetime(df[dt_col], errors="coerce").dropna()
                if len(parsed_dates) >= 4:
                    monthly = parsed_dates.dt.to_period("M").value_counts().sort_index()
                    if len(monthly) >= 2:
                        data_points = [
                            ChartDataPoint(
                                label=str(period),
                                value=int(count)
                            )
                            for period, count in monthly.items()
                        ]
                        charts.append(ChartSpecification(
                            id=f"line_trend_{dt_col}",
                            title=f"Activity Volume Over Time ({dt_col.replace('_', ' ').title()})",
                            chart_type="line",
                            x_axis_label="Period (Month)",
                            y_axis_label="Observation Volume",
                            description=f"Chronological trend of recorded activity grouped monthly across '{dt_col}'.",
                            series=[ChartSeries(name="Monthly Volume", data=data_points)]
                        ))
            except Exception as err:
                logger.warning(f"Could not build time-series trend line chart: {err}")

        # ---------------------------------------------------------------------
        # 4. Correlation Scatter Plot
        # ---------------------------------------------------------------------
        if len(numeric_cols) >= 2:
            num1 = numeric_cols[0]
            num2 = numeric_cols[1]
            try:
                # Sample up to 50 paired data points
                sub_df = df[[num1, num2]].dropna()
                sample_size = min(len(sub_df), 50)
                sampled = sub_df.sample(sample_size, random_state=42) if len(sub_df) > sample_size else sub_df

                data_points = [
                    ChartDataPoint(
                        label=f"Row {idx}",
                        value=_safe_float(row[num1]) or 0.0,
                        secondary_value=_safe_float(row[num2]) or 0.0
                    )
                    for idx, row in sampled.iterrows()
                ]

                charts.append(ChartSpecification(
                    id=f"scatter_{num1}_{num2}",
                    title=f"Correlation Scatter: {num1.replace('_', ' ').title()} vs {num2.replace('_', ' ').title()}",
                    chart_type="scatter",
                    x_axis_label=num1.replace('_', ' ').title(),
                    y_axis_label=num2.replace('_', ' ').title(),
                    description=f"Visualizes the linear or non-linear co-variation between '{num1}' and '{num2}'.",
                    series=[ChartSeries(name=f"{num1} vs {num2}", data=data_points)]
                ))
            except Exception as err:
                logger.warning(f"Could not build scatter plot: {err}")

        # ---------------------------------------------------------------------
        # 5. Boxplot 5-Number Distribution Summary
        # ---------------------------------------------------------------------
        for num_col in numeric_cols[:2]:
            s = pd.to_numeric(df[num_col], errors="coerce").dropna()
            if len(s) >= 4:
                q1 = _safe_float(s.quantile(0.25)) or 0.0
                med = _safe_float(s.median()) or 0.0
                q3 = _safe_float(s.quantile(0.75)) or 0.0
                min_v = _safe_float(s.min()) or 0.0
                max_v = _safe_float(s.max()) or 0.0

                data_points = [
                    ChartDataPoint(label="Min", value=min_v),
                    ChartDataPoint(label="Q1 (25%)", value=q1),
                    ChartDataPoint(label="Median (50%)", value=med),
                    ChartDataPoint(label="Q3 (75%)", value=q3),
                    ChartDataPoint(label="Max", value=max_v),
                ]

                charts.append(ChartSpecification(
                    id=f"boxplot_{num_col}",
                    title=f"Quantile Summary for {num_col.replace('_', ' ').title()}",
                    chart_type="boxplot",
                    x_axis_label="Quantile Benchmark",
                    y_axis_label=num_col.replace('_', ' ').title(),
                    description=f"5-number summary (Min, Q1, Median, Q3, Max) illustrating the spread and skewness of '{num_col}'.",
                    series=[ChartSeries(name=num_col, data=data_points)]
                ))

        return DatasetVisualizationsResponse(
            dataset_id=dataset_id,
            total_recommendations=len(charts),
            charts=charts
        )
