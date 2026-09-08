from fastapi import APIRouter, HTTPException
from services.dashboard_builder import DashboardBuilderService

router = APIRouter(tags=["Version 3 - Dashboard"])

@router.get("/dataset/{id}/dashboard")
def get_dashboard(id: str):
    res = DashboardBuilderService.build_dashboard(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
