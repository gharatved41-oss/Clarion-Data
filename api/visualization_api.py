from fastapi import APIRouter, HTTPException
from services.chart_engine import ChartEngineService

router = APIRouter(tags=["Version 3 - Visualization"])

@router.get("/dataset/{id}/charts")
def get_charts(id: str):
    res = ChartEngineService.recommend_charts(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.get("/dataset/{id}/chart-options")
def get_chart_options(id: str):
    res = ChartEngineService.get_chart_options(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
