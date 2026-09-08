from fastapi import APIRouter, HTTPException
from services.domain_detector import DomainDetectorService
from services.payment_analytics import PaymentAnalyticsService
from services.change_detector import ChangeDetectorService

router = APIRouter(tags=["Version 4 - Domain, Payment & Change Intelligence"])

@router.get("/dataset/{id}/domain")
def get_domain(id: str):
    res = DomainDetectorService.detect_domain(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/dataset/{id}/payment-analytics")
def get_payment_analytics(id: str):
    res = PaymentAnalyticsService.analyze_payments(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/dataset/{id}/changes")
def get_changes(id: str):
    res = ChangeDetectorService.detect_changes(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
