import pytest
from services.chart_engine import ChartEngineService
from services.dashboard_builder import DashboardBuilderService

def test_chart_recommendations_sales():
    res = ChartEngineService.recommend_charts("test-sales")
    assert "recommended" in res
    assert len(res["recommended"]) > 0
    chart_types = [c["type"] for c in res["recommended"]]
    assert "line" in chart_types or "bar" in chart_types

def test_chart_options():
    res = ChartEngineService.get_chart_options("test-sales")
    assert "available_charts" in res
    assert len(res["available_charts"]) >= 3

def test_dashboard_builder_sales():
    res = DashboardBuilderService.build_dashboard("test-sales")
    assert res["dataset_id"] == "test-sales"
    assert "overview" in res
    assert "schema" in res
    assert "clusters" in res
    assert "predictions" in res
    assert "charts" in res
