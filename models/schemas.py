from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Clustering Schema
class ClusterCharacteristic(BaseModel):
    cluster: int
    size: int
    characteristics: Dict[str, float]

class ClusteringResponse(BaseModel):
    dataset_id: str
    applicable: bool
    reason: Optional[str] = None
    algorithm: Optional[str] = "KMeans"
    n_clusters: Optional[int] = None
    features_used: Optional[List[str]] = None
    clusters: Optional[List[Dict[str, Any]]] = None

# Prediction Schema
class EvaluationMetrics(BaseModel):
    MAE: Optional[float] = None
    RMSE: Optional[float] = None
    R2: Optional[float] = None
    MAPE: Optional[float] = None

class ForecastPoint(BaseModel):
    date: Optional[str] = None
    step: Optional[int] = None
    predicted_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class PredictionResponse(BaseModel):
    applicable: bool
    reason: Optional[str] = None
    dataset_id: Optional[str] = None
    target: Optional[str] = None
    date_column: Optional[str] = None
    prediction_type: Optional[str] = None
    model: Optional[str] = None
    evaluation: Optional[Dict[str, float]] = None
    forecast: Optional[List[Dict[str, Any]]] = None
    trend_direction: Optional[str] = None
    growth_rate_percent: Optional[float] = None
    confidence_level: Optional[str] = None
    available_targets: Optional[List[str]] = None
    feature_importance: Optional[Dict[str, float]] = None

# Visualization Schema
class ChartConfig(BaseModel):
    type: str
    title: str
    x: Optional[str] = None
    y: Optional[str] = None
    data: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None

class ChartsResponse(BaseModel):
    dataset_id: str
    recommended: List[Dict[str, Any]]

class ChartOptionsResponse(BaseModel):
    dataset_id: str
    available_charts: List[Dict[str, Any]]

# Domain & Intelligence Schemas
class DomainResponse(BaseModel):
    dataset_id: str
    domain: str
    confidence: float
    evidence: List[str]

class PaymentAnalyticsResponse(BaseModel):
    applicable: bool
    reason: Optional[str] = None
    dataset_id: Optional[str] = None
    total_amount: Optional[float] = None
    completed_amount: Optional[float] = None
    pending_amount: Optional[float] = None
    failed_amount: Optional[float] = None
    trend: Optional[List[Dict[str, Any]]] = None
    growth: Optional[Dict[str, Any]] = None

class ChangesResponse(BaseModel):
    dataset_id: str
    daily: Optional[Dict[str, Any]] = None
    weekly: Optional[Dict[str, Any]] = None
    monthly: Optional[Dict[str, Any]] = None

# Insight Schemas
class SummaryResponse(BaseModel):
    dataset_id: str
    summary: str
    facts: Dict[str, Any]

class NotificationItem(BaseModel):
    severity: str
    type: str
    message: str

class NotificationsResponse(BaseModel):
    dataset_id: str
    notifications: List[NotificationItem]

class QualityFactor(BaseModel):
    score: float
    detail: str

class DataQualityResponse(BaseModel):
    dataset_id: str
    score: float
    grade: str
    factors: Dict[str, float]

# Re-export Person 1 Schemas
from models.person1_schemas import *

