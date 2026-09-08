from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from services.predictor import PredictionService

router = APIRouter(tags=["Version 2 - Prediction & Forecasting"])

@router.get("/dataset/{id}/predictions")
def get_predictions(
    id: str,
    target: Optional[str] = Query(None, description="Optional target column name to forecast"),
    steps: int = Query(7, ge=1, le=90, description="Forecast horizon steps (days)"),
    model_type: Optional[str] = Query(None, description="Specific regression model (e.g. LinearRegression, Ridge, RandomForestRegressor, GradientBoostingRegressor)")
):
    res = PredictionService.analyze_predictions(id, target=target, steps=steps, model_type=model_type)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

