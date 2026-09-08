from fastapi import APIRouter, HTTPException
from services.clustering import ClusteringService

router = APIRouter(tags=["Version 1 - Clustering"])

@router.get("/dataset/{id}/clusters")
def get_clusters(id: str):
    res = ClusteringService.analyze_clusters(id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res
