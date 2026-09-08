import pytest
from services.payment_analytics import PaymentAnalyticsService

def test_payment_analytics_payment_dataset():
    res = PaymentAnalyticsService.analyze_payments("test-payment")
    assert res["applicable"] is True
    assert res["total_amount"] > 0
    assert "completed_amount" in res
    assert "pending_amount" in res
    assert "failed_amount" in res

def test_payment_analytics_healthcare_dataset():
    res = PaymentAnalyticsService.analyze_payments("test-healthcare")
    assert res["applicable"] is False
    assert "reason" in res
