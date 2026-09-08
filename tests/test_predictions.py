import pytest
import os
import pandas as pd
from services.predictor import PredictionService
from services.dataset_store import dataset_store

def test_prediction_sales():
    res = PredictionService.analyze_predictions("test-sales")
    assert res["applicable"] is True
    assert res["target"] is not None
    assert res["date_column"] is not None
    assert "evaluation" in res
    assert "MAE" in res["evaluation"]
    assert len(res["forecast"]) > 0

def test_prediction_payment():
    res = PredictionService.analyze_predictions("test-payment")
    assert res["applicable"] is True
    assert "forecast" in res

def test_prediction_nodates():
    res = PredictionService.analyze_predictions("test-no_dates")
    assert res["applicable"] is True
    assert res["prediction_type"] == "tabular_regression"
    assert "feature_importance" in res
    assert isinstance(res["feature_importance"], dict)

def test_prediction_unsuitable():
    res = PredictionService.analyze_predictions("test-unsuitable_prediction")
    assert res["applicable"] is False
    assert "reason" in res

def test_prediction_custom_target_and_steps():
    # Test explicitly passing target and custom horizon steps
    res = PredictionService.analyze_predictions("test-sales", target="quantity", steps=14)
    assert res["applicable"] is True
    assert res["target"] == "quantity"
    assert len(res["forecast"]) == 14

def test_prediction_confidence_bounds():
    # Verify 95% confidence intervals exist on forecast points
    res = PredictionService.analyze_predictions("test-sales")
    assert res["applicable"] is True
    first_point = res["forecast"][0]
    assert "lower_bound" in first_point
    assert "upper_bound" in first_point
    assert first_point["lower_bound"] <= first_point["predicted_value"]
    assert first_point["upper_bound"] >= first_point["predicted_value"]

def test_prediction_trend_intelligence():
    # Verify trend direction and growth rate metrics
    res = PredictionService.analyze_predictions("test-sales")
    assert res["applicable"] is True
    assert res["trend_direction"] in ["increasing", "decreasing", "stable"]
    assert "growth_rate_percent" in res
    assert res["confidence_level"] in ["high", "medium", "low"]
    assert "available_targets" in res
    assert len(res["available_targets"]) > 0

def test_prediction_dirty_dataset_handling():
    # Test prediction on real-world dirty ecommerce dataset
    csv_path = "test_ecommerce_dirty.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        ds_id = dataset_store.save_dataset(df, "test_ecommerce_dirty.csv")
        res = PredictionService.analyze_predictions(ds_id)
        assert res["applicable"] is True
        # Verify that total_sales is prioritized as the target now that currency strings are sanitized
        assert res["target"] == "total_sales"
        assert len(res["forecast"]) == 7
        assert res["forecast"][0]["predicted_value"] > 0
