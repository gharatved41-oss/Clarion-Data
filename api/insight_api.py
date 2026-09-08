from fastapi import APIRouter, HTTPException
from services.summary_generator import SummaryGeneratorService
from services.notification_engine import NotificationEngineService
from services.quality_score import QualityScoreService

router = APIRouter(tags=["Version 5 - AI Insights, Notifications & Data Quality"])

@router.get("/dataset/{id}/summary")
def get_summary(id: str):
    res = SummaryGeneratorService.generate_summary(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/dataset/{id}/notifications")
def get_notifications(id: str):
    res = NotificationEngineService.generate_notifications(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/dataset/{id}/data-quality")
def get_data_quality(id: str):
    res = QualityScoreService.calculate_score(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
