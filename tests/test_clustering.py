import pytest
from services.clustering import ClusteringService

def test_clustering_sales():
    res = ClusteringService.analyze_clusters("test-sales")
    assert res["applicable"] is True
    assert res["algorithm"] == "KMeans"
    assert res["n_clusters"] >= 2
    assert "revenue" in [f.lower() for f in res["features_used"]] or "quantity" in [f.lower() for f in res["features_used"]]
    assert len(res["clusters"]) == res["n_clusters"]

def test_clustering_insufficient_numerics():
    res = ClusteringService.analyze_clusters("test-insufficient_numerics")
    assert res["applicable"] is False
    assert "reason" in res

def test_clustering_unsuitable():
    res = ClusteringService.analyze_clusters("test-unsuitable_clustering")
    assert res["applicable"] is False
    assert "reason" in res

def test_clustering_healthcare():
    res = ClusteringService.analyze_clusters("test-healthcare")
    assert res["applicable"] is True
    assert res["n_clusters"] >= 2
