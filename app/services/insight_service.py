"""Service for automated executive natural-language insights and data quality scoring."""
import logging
from app.schemas.dataset import (
    DataQualityScore,
    InsightFinding,
    DatasetInsightsResponse,
)
from app.services.upload_service import UploadService
from app.services.schema_service import SchemaService
from app.services.cleaning_service import CleaningService
from app.services.analysis_service import AnalysisService
from app.services.correlation_service import CorrelationService
from app.services.outlier_service import OutlierService

logger = logging.getLogger("app.services.insight_service")


class InsightService:
    """Automated analytical narrative synthesis and data quality evaluation engine."""

    @classmethod
    def generate_insights(cls, dataset_id: str) -> DatasetInsightsResponse:
        """Analyze all pipeline outputs and produce holistic executive findings and recommendations."""
        overview = UploadService.get_dataset_overview(dataset_id)
        cleaning_report = CleaningService.clean_dataset(dataset_id)
        analysis = AnalysisService.analyze_dataset(dataset_id)
        correlations = CorrelationService.compute_correlations(dataset_id)
        outliers = OutlierService.detect_outliers(dataset_id)

        # ---------------------------------------------------------------------
        # 1. Calculate Data Quality Score
        # ---------------------------------------------------------------------
        total_cells = max(1, overview.rows * overview.columns)
        missing_rate = (overview.missing_values / total_cells) * 100.0
        completeness_score = max(0, min(100, int(round(100.0 - missing_rate))))

        dup_rate = (overview.duplicate_rows / max(1, overview.rows)) * 100.0
        uniqueness_score = max(0, min(100, int(round(100.0 - (dup_rate * 2.5)))))

        outlier_pct = outliers.summary.rows_with_outliers_percentage
        validity_score = max(0, min(100, int(round(100.0 - (outlier_pct * 1.5)))))

        overall_score = int(round(
            (0.40 * completeness_score) +
            (0.30 * uniqueness_score) +
            (0.30 * validity_score)
        ))

        if overall_score >= 95:
            grade = "A+"
        elif overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"

        quality = DataQualityScore(
            overall_score=overall_score,
            grade=grade,
            completeness_score=completeness_score,
            uniqueness_score=uniqueness_score,
            validity_score=validity_score
        )

        # ---------------------------------------------------------------------
        # 2. Synthesize Key Findings
        # ---------------------------------------------------------------------
        findings: list[InsightFinding] = []

        # Scope finding
        findings.append(InsightFinding(
            category="overview",
            title=f"Dataset Architecture ({overview.rows:,} Records × {overview.columns} Attributes)",
            description=(
                f"The dataset contains {overview.rows:,} observations across {overview.columns} attributes, "
                f"encompassing {len(analysis.numeric_analysis)} numeric features, "
                f"{len(analysis.categorical_analysis)} categorical dimensions, and "
                f"{len(analysis.datetime_analysis)} temporal fields."
            ),
            impact="positive" if overview.rows > 100 else "medium"
        ))

        # Categorical concentration finding
        for col, cat_stat in analysis.categorical_analysis.items():
            if cat_stat.top_categories:
                top_cat = cat_stat.top_categories[0]
                if top_cat.percentage >= 30.0:
                    findings.append(InsightFinding(
                        category="concentration",
                        title=f"High Concentration in '{col}' ({top_cat.category})",
                        description=(
                            f"The '{top_cat.category}' category accounts for {top_cat.percentage}% "
                            f"({top_cat.count:,} rows) of all '{col}' entries across {cat_stat.unique_count} distinct categories."
                        ),
                        impact="medium"
                    ))
                    break

        # Correlation finding
        if correlations.strong_positive:
            top_pos = correlations.strong_positive[0]
            findings.append(InsightFinding(
                category="correlation",
                title=f"Strong Linear Association: {top_pos.var1} & {top_pos.var2}",
                description=(
                    f"A strong positive correlation (r = {top_pos.correlation}) exists between '{top_pos.var1}' "
                    f"and '{top_pos.var2}', indicating that increases in one directly correspond with proportional increases in the other."
                ),
                impact="high"
            ))

        if correlations.strong_negative:
            top_neg = correlations.strong_negative[0]
            findings.append(InsightFinding(
                category="correlation",
                title=f"Inverse Association: {top_neg.var1} & {top_neg.var2}",
                description=(
                    f"An inverse negative correlation (r = {top_neg.correlation}) exists between '{top_neg.var1}' "
                    f"and '{top_neg.var2}'."
                ),
                impact="medium"
            ))

        # Outlier finding
        if outliers.summary.total_outlier_data_points > 0:
            top_outlier_col = outliers.summary.columns_with_outliers[0] if outliers.summary.columns_with_outliers else "various columns"
            findings.append(InsightFinding(
                category="outlier",
                title=f"Outlier Anomaly Density ({outliers.summary.rows_with_outliers_percentage}% of Rows)",
                description=(
                    f"Detected {outliers.summary.total_outlier_data_points} outlier data points affecting "
                    f"{outliers.summary.rows_with_outliers_count} rows ({outliers.summary.rows_with_outliers_percentage}%). "
                    f"Primary concentration observed in '{top_outlier_col}'."
                ),
                impact="high" if outliers.summary.rows_with_outliers_percentage > 5.0 else "medium"
            ))

        # Time series finding
        for col, dt_stat in analysis.datetime_analysis.items():
            if dt_stat.min_date and dt_stat.max_date:
                findings.append(InsightFinding(
                    category="time_trend",
                    title=f"Temporal Coverage: {dt_stat.range_days} Days ({col})",
                    description=(
                        f"Data records span from {dt_stat.min_date} to {dt_stat.max_date}, "
                        f"covering {dt_stat.range_days} total active days across {len(dt_stat.monthly_distribution)} active calendar months."
                    ),
                    impact="positive"
                ))
                break

        # ---------------------------------------------------------------------
        # 3. Actionable Recommendations
        # ---------------------------------------------------------------------
        recommendations: list[str] = []

        if cleaning_report.duplicates_removed > 0:
            recommendations.append(
                f"Verify upstream data ingestion pipelines to prevent {cleaning_report.duplicates_removed} duplicate records from reoccurring."
            )

        if cleaning_report.missing_values_handled > 0:
            recommendations.append(
                f"Imputation resolved {cleaning_report.missing_values_handled} missing values via median/mode strategies; review if source database schemas should enforce NOT NULL constraints."
            )

        if outliers.summary.total_outlier_data_points > 0:
            recommendations.append(
                f"Investigate high-leverage outliers in '{outliers.summary.columns_with_outliers[:2]}' before feeding data into downstream regression or machine learning models."
            )

        if correlations.strong_positive:
            recommendations.append(
                f"Leverage the strong dependency between '{correlations.strong_positive[0].var1}' and '{correlations.strong_positive[0].var2}' for predictive modeling or cross-feature validation."
            )

        recommendations.append(
            "Export the cleaned dataset artifact for downstream reporting, BI dashboards, or machine learning training pipelines."
        )

        return DatasetInsightsResponse(
            dataset_id=dataset_id,
            quality_score=quality,
            key_findings=findings,
            actionable_recommendations=recommendations
        )
