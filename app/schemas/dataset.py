"""Pydantic schemas for dataset operations."""
from typing import Any
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response returned upon successful dataset upload."""
    dataset_id: str = Field(..., description="Unique identifier for the uploaded dataset")
    filename: str = Field(..., description="Original filename of the uploaded file")
    rows: int = Field(..., description="Number of rows in the dataset")
    columns: int = Field(..., description="Number of columns in the dataset")
    message: str = Field(default="Dataset uploaded successfully", description="Status message")


class DatasetOverviewResponse(BaseModel):
    """Response returned for dataset overview inspection."""
    dataset_id: str = Field(..., description="Unique identifier for the dataset")
    filename: str = Field(..., description="Original filename of the dataset")
    rows: int = Field(..., description="Total number of rows")
    columns: int = Field(..., description="Total number of columns")
    column_names: list[str] = Field(..., description="List of column names")
    file_type: str = Field(..., description="File format/extension (e.g., .csv, .xlsx)")
    missing_values: int = Field(..., description="Total count of missing/null values across all cells")
    duplicate_rows: int = Field(..., description="Total count of exact duplicate rows")
    memory_usage_bytes: int = Field(..., description="Memory footprint of the dataset in bytes")
    preview_rows: list[dict[str, Any]] = Field(default_factory=list, description="Sample/preview rows from the dataset")
    row_count: int | None = Field(None, description="Alias for rows (Person 2 compatibility)")
    column_count: int | None = Field(None, description="Alias for columns (Person 2 compatibility)")


class ColumnSchema(BaseModel):
    """Schema metadata for an individual column."""
    name: str = Field(..., description="Column header name")
    type: str = Field(..., description="Detected column type: numeric, categorical, datetime, text, or identifier")
    confidence: float = Field(..., description="Detection confidence score between 0.0 and 1.0")
    original_dtype: str = Field(..., description="Underlying pandas data type")
    unique_count: int = Field(..., description="Number of unique non-null values")
    null_count: int = Field(..., description="Number of null/missing values")


class DatasetSchemaResponse(BaseModel):
    """Response returned for dataset schema detection."""
    dataset_id: str = Field(..., description="Unique identifier for the dataset")
    columns: list[ColumnSchema] = Field(..., description="List of detected column specifications")


class CleaningOperation(BaseModel):
    """Individual recorded data transformation."""
    column: str | None = Field(None, description="Target column name, or null for dataset-level operations")
    operation: str = Field(..., description="Name of the cleaning operation performed")
    affected_rows: int = Field(..., description="Number of rows modified by this operation")
    method: str | None = Field(None, description="Imputation or transformation technique used")
    details: str | None = Field(None, description="Detailed explanation of the transformation")


class CleaningReportResponse(BaseModel):
    """Comprehensive audit report of all cleaning operations applied to a dataset."""
    dataset_id: str = Field(..., description="Unique identifier of the dataset")
    original_row_count: int = Field(..., description="Number of rows before cleaning")
    cleaned_row_count: int = Field(..., description="Number of rows after cleaning")
    original_column_count: int = Field(..., description="Number of columns")
    missing_values_detected: int = Field(..., description="Total missing cells detected in raw data")
    missing_values_handled: int = Field(..., description="Total missing cells imputed or resolved")
    duplicates_detected: int = Field(..., description="Total duplicate rows found")
    duplicates_removed: int = Field(..., description="Total duplicate rows removed")
    numeric_conversions: int = Field(..., description="Total cells converted from string/formatted to numeric")
    currency_conversions: int = Field(..., description="Total currency cells stripped and converted")
    percentage_conversions: int = Field(..., description="Total percentage cells converted")
    date_conversions: int = Field(..., description="Total date cells normalized to ISO 8601")
    whitespace_fixes: int = Field(..., description="Total cells with leading/trailing whitespace removed")
    capitalization_fixes: int = Field(..., description="Total categorical cells normalized for case consistency")
    operations: list[CleaningOperation] = Field(..., description="Detailed list of all cleaning transformations")
    warnings: list[str] = Field(default_factory=list, description="Warnings or notices generated during cleaning")
    skipped_operations: list[str] = Field(default_factory=list, description="Operations intentionally omitted for safety")


# =============================================================================
# FEATURE 4: Statistical Analysis Schemas
# =============================================================================

class HistogramBin(BaseModel):
    """Bin specification for numeric histogram plotting."""
    bin_start: float = Field(..., description="Lower boundary of the bin (inclusive)")
    bin_end: float = Field(..., description="Upper boundary of the bin (exclusive)")
    count: int = Field(..., description="Number of observations falling into this bin")


class NumericStats(BaseModel):
    """Descriptive statistics for a numeric column."""
    count: int = Field(..., description="Number of non-null observations")
    null_count: int = Field(..., description="Number of missing observations")
    mean: float | None = Field(None, description="Arithmetic mean")
    median: float | None = Field(None, description="50th percentile / median")
    min: float | None = Field(None, description="Minimum observed value")
    max: float | None = Field(None, description="Maximum observed value")
    std: float | None = Field(None, description="Sample standard deviation")
    variance: float | None = Field(None, description="Sample variance")
    skewness: float | None = Field(None, description="Distribution skewness metric")
    q1: float | None = Field(None, description="25th percentile")
    q3: float | None = Field(None, description="75th percentile")
    iqr: float | None = Field(None, description="Interquartile range (Q3 - Q1)")
    histogram: list[HistogramBin] = Field(default_factory=list, description="Histogram distribution buckets")


class CategoryFrequency(BaseModel):
    """Value count and frequency for a category."""
    category: str = Field(..., description="Category label")
    count: int = Field(..., description="Frequency count")
    percentage: float = Field(..., description="Proportion of non-null observations (0.0 - 100.0)")


class CategoricalStats(BaseModel):
    """Descriptive statistics for a categorical column."""
    count: int = Field(..., description="Number of non-null observations")
    null_count: int = Field(..., description="Number of missing observations")
    unique_count: int = Field(..., description="Number of distinct categories")
    top_categories: list[CategoryFrequency] = Field(default_factory=list, description="Top categories ranked by frequency")


class DateTimeStats(BaseModel):
    """Descriptive statistics for a date/time column."""
    count: int = Field(..., description="Number of non-null date values")
    null_count: int = Field(..., description="Number of missing/invalid dates")
    min_date: str | None = Field(None, description="Earliest recorded date (ISO string)")
    max_date: str | None = Field(None, description="Latest recorded date (ISO string)")
    range_days: int | None = Field(None, description="Timespan span in days")
    yearly_distribution: dict[str, int] = Field(default_factory=dict, description="Counts grouped by year")
    monthly_distribution: dict[str, int] = Field(default_factory=dict, description="Counts grouped by month")


class TextStats(BaseModel):
    """Descriptive statistics for a natural-language text column."""
    count: int = Field(..., description="Number of non-null text records")
    null_count: int = Field(..., description="Number of missing text records")
    unique_count: int = Field(..., description="Number of unique text values")
    avg_word_count: float | None = Field(None, description="Average word count per entry")
    avg_char_length: float | None = Field(None, description="Average character length per entry")
    min_length: int | None = Field(None, description="Minimum string length")
    max_length: int | None = Field(None, description="Maximum string length")


class IdentifierStats(BaseModel):
    """Descriptive metrics for an identifier column."""
    count: int = Field(..., description="Total non-null identifiers")
    null_count: int = Field(..., description="Missing identifiers")
    unique_count: int = Field(..., description="Count of distinct identifiers")
    uniqueness_ratio: float = Field(..., description="Uniqueness ratio (unique / count)")


class DatasetAnalysisResponse(BaseModel):
    """Comprehensive statistical analysis response covering all detected column categories."""
    dataset_id: str = Field(..., description="Unique dataset identifier")
    total_rows: int = Field(..., description="Total rows analyzed")
    total_columns: int = Field(..., description="Total columns analyzed")
    numeric_analysis: dict[str, NumericStats] = Field(default_factory=dict, description="Stats per numeric column")
    categorical_analysis: dict[str, CategoricalStats] = Field(default_factory=dict, description="Stats per categorical column")
    datetime_analysis: dict[str, DateTimeStats] = Field(default_factory=dict, description="Stats per datetime column")
    text_analysis: dict[str, TextStats] = Field(default_factory=dict, description="Stats per text column")
    identifier_analysis: dict[str, IdentifierStats] = Field(default_factory=dict, description="Stats per identifier column")
    numeric_stats: dict[str, Any] = Field(default_factory=dict, description="Alias for numeric_analysis (Person 2 compatibility)")


# =============================================================================
# FEATURE 5: Correlation Analysis Schemas
# =============================================================================

class CorrelationPair(BaseModel):
    """Pairwise correlation metric between two variables."""
    var1: str = Field(..., description="First variable name")
    var2: str = Field(..., description="Second variable name")
    correlation: float = Field(..., description="Correlation coefficient (-1.0 to 1.0)")
    strength: str = Field(..., description="Strength classification: Very Strong, Strong, Moderate, Weak")
    direction: str = Field(..., description="Direction: Positive, Negative, None")


class DatasetCorrelationResponse(BaseModel):
    """Pairwise correlation analysis response."""
    dataset_id: str = Field(..., description="Unique dataset identifier")
    method: str = Field(default="pearson", description="Correlation calculation method (e.g., pearson, spearman)")
    numeric_columns: list[str] = Field(default_factory=list, description="Ordered list of numerical variables included")
    matrix: list[list[float | None]] = Field(default_factory=list, description="2D correlation matrix grid corresponding to numeric_columns")
    strong_positive: list[CorrelationPair] = Field(default_factory=list, description="Variable pairs with strong positive linear association")
    strong_negative: list[CorrelationPair] = Field(default_factory=list, description="Variable pairs with strong negative linear association")
    important_pairs: list[CorrelationPair] = Field(default_factory=list, description="Ranked variable pairs ordered by correlation magnitude")
    message: str | None = Field(None, description="Optional informational message (e.g. if insufficient numeric columns exist)")
    strong_correlations: list[dict[str, Any]] = Field(default_factory=list, description="Alias for important_pairs (Person 2 compatibility)")


# =============================================================================
# FEATURE 5: Outlier Detection Schemas
# =============================================================================

class OutlierSample(BaseModel):
    """Sample outlier observation."""
    row_index: int = Field(..., description="Zero-based row index in cleaned dataset")
    value: float | str | None = Field(None, description="Outlier value observed")


class ColumnOutlierIQR(BaseModel):
    """IQR (Interquartile Range) outlier detection results for a column."""
    q1: float = Field(..., description="25th percentile")
    q3: float = Field(..., description="75th percentile")
    iqr: float = Field(..., description="Interquartile range (Q3 - Q1)")
    lower_bound: float = Field(..., description="Lower fence (Q1 - 1.5 * IQR)")
    upper_bound: float = Field(..., description="Upper fence (Q3 + 1.5 * IQR)")
    outlier_count: int = Field(..., description="Number of outlier observations")
    outlier_percentage: float = Field(..., description="Percentage of values identified as outliers")
    sample_outliers: list[OutlierSample] = Field(default_factory=list, description="Sample outlier records")
    affected_rows: list[int] = Field(default_factory=list, description="Row indices of affected records")


class ColumnOutlierZScore(BaseModel):
    """Z-Score outlier detection results for a column."""
    mean: float = Field(..., description="Sample mean")
    std: float = Field(..., description="Sample standard deviation")
    threshold: float = Field(default=3.0, description="Standard deviation cutoff threshold")
    lower_bound: float = Field(..., description="Lower threshold (mean - threshold * std)")
    upper_bound: float = Field(..., description="Upper threshold (mean + threshold * std)")
    outlier_count: int = Field(..., description="Number of outlier observations")
    outlier_percentage: float = Field(..., description="Percentage of values identified as outliers")
    sample_outliers: list[OutlierSample] = Field(default_factory=list, description="Sample outlier records")
    affected_rows: list[int] = Field(default_factory=list, description="Row indices of affected records")


class ColumnOutlierIsoForest(BaseModel):
    """Isolation Forest anomaly detection results."""
    contamination: float = Field(default=0.05, description="Expected proportion of anomalies")
    outlier_count: int = Field(..., description="Total anomalies identified")
    outlier_percentage: float = Field(..., description="Percentage of rows identified as anomalous")
    affected_rows: list[int] = Field(default_factory=list, description="Row indices flagged as anomalies")


class ColumnOutliersResult(BaseModel):
    """Combined outlier metrics for an individual column."""
    column: str = Field(..., description="Target column name")
    iqr: ColumnOutlierIQR | None = Field(None, description="IQR results if computed")
    z_score: ColumnOutlierZScore | None = Field(None, description="Z-Score results if computed")


class OutlierSummary(BaseModel):
    """High-level summary of all detected outliers across the dataset."""
    total_outlier_data_points: int = Field(..., description="Total individual outlier cell values identified")
    rows_with_outliers_count: int = Field(..., description="Count of distinct rows containing at least one outlier")
    rows_with_outliers_percentage: float = Field(..., description="Percentage of rows containing at least one outlier")
    columns_with_outliers: list[str] = Field(default_factory=list, description="Names of columns exhibiting outliers")


class DatasetOutlierResponse(BaseModel):
    """Outlier analysis response."""
    dataset_id: str = Field(..., description="Unique dataset identifier")
    method: str = Field(..., description="Detection method executed (iqr, zscore, isolation_forest, all)")
    summary: OutlierSummary = Field(..., description="Aggregate outlier metrics")
    columns: dict[str, ColumnOutliersResult] = Field(default_factory=dict, description="Per-column outlier statistics")
    isolation_forest: ColumnOutlierIsoForest | None = Field(None, description="Multivariate Isolation Forest results if requested")
    total_outliers_count: int | None = Field(None, description="Alias for summary.total_outlier_data_points")
    outliers_percentage: float | None = Field(None, description="Alias for summary.rows_with_outliers_percentage")
    outliers_by_column: dict[str, Any] = Field(default_factory=dict, description="Alias for column outlier metrics")


# =============================================================================
# FEATURE 6: Visualization & Chart Recommendation Schemas
# =============================================================================

class ChartDataPoint(BaseModel):
    """Individual data observation in a chart series."""
    label: str | float = Field(..., description="Category name, bin label, or independent coordinate")
    value: float | int = Field(..., description="Primary numerical measure")
    secondary_value: float | int | None = Field(None, description="Secondary coordinate for scatter or ranges")
    group: str | None = Field(None, description="Optional segmentation grouping")


class ChartSeries(BaseModel):
    """Data series container for charting."""
    name: str = Field(..., description="Series label")
    data: list[ChartDataPoint] = Field(default_factory=list, description="List of plot points")


class ChartSpecification(BaseModel):
    """Structured visual specification for frontends and visualization engines."""
    id: str = Field(..., description="Unique chart identifier")
    title: str = Field(..., description="Human-readable chart title")
    chart_type: str = Field(..., description="Chart category: bar, horizontal_bar, line, scatter, donut, boxplot")
    x_axis_label: str = Field(..., description="Label for horizontal axis")
    y_axis_label: str = Field(..., description="Label for vertical axis")
    description: str = Field(..., description="Narrative purpose of the chart")
    series: list[ChartSeries] = Field(default_factory=list, description="Series datasets for visualization")


class DatasetVisualizationsResponse(BaseModel):
    """Visualizations collection response."""
    dataset_id: str = Field(..., description="Unique dataset identifier")
    total_recommendations: int = Field(..., description="Number of tailored charts generated")
    charts: list[ChartSpecification] = Field(default_factory=list, description="Recommended visual specifications")


# =============================================================================
# FEATURE 6: Executive Insights Schemas
# =============================================================================

class DataQualityScore(BaseModel):
    """Composite dataset cleanliness and integrity evaluation."""
    overall_score: int = Field(..., description="Overall health score from 0 to 100")
    grade: str = Field(..., description="Letter grade (A+, A, B, C, D, F)")
    completeness_score: int = Field(..., description="Completeness score based on non-null cell ratio")
    uniqueness_score: int = Field(..., description="Score based on duplicate row ratio")
    validity_score: int = Field(..., description="Score based on data sanity and outlier presence")


class InsightFinding(BaseModel):
    """Discovered analytical pattern or headline insight."""
    category: str = Field(..., description="Insight scope: overview, concentration, correlation, outlier, time_trend")
    title: str = Field(..., description="Concise headline")
    description: str = Field(..., description="Detailed narrative explanation")
    impact: str = Field(default="medium", description="Significance: high, medium, low, positive")


class DatasetInsightsResponse(BaseModel):
    """Executive automated insights and quality assessment response."""
    dataset_id: str = Field(..., description="Unique dataset identifier")
    quality_score: DataQualityScore = Field(..., description="Overall dataset health evaluation")
    key_findings: list[InsightFinding] = Field(default_factory=list, description="Automated analytical discoveries")
    actionable_recommendations: list[str] = Field(default_factory=list, description="Prescriptive guidance for analysts")
