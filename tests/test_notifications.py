import pytest
from services.notification_engine import NotificationEngineService

def test_notifications_sales():
    res = NotificationEngineService.generate_notifications("test-sales")
    assert "notifications" in res
    assert len(res["notifications"]) > 0
    assert "severity" in res["notifications"][0]

def test_notifications_payment():
    res = NotificationEngineService.generate_notifications("test-payment")
    assert "notifications" in res
    assert len(res["notifications"]) > 0

def test_notifications_outliers():
    res = NotificationEngineService.generate_notifications("test-outliers")
    assert "notifications" in res
    severities = [n["severity"] for n in res["notifications"]]
    assert "info" in severities or "warning" in severities or "critical" in severities
