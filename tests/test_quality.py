import pytest
from services.quality_score import QualityScoreService

def test_quality_sales():
    res = QualityScoreService.calculate_score("test-sales")
    assert "score" in res
    assert "grade" in res
    assert res["score"] >= 0 and res["score"] <= 100
    assert "missing_values" in res["factors"]

def test_quality_missing_values_dataset():
    res = QualityScoreService.calculate_score("test-missing_values")
    assert res["score"] < 95
    assert "factors" in res
