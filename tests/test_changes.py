import pytest
from services.change_detector import ChangeDetectorService

def test_change_detector_sales():
    res = ChangeDetectorService.detect_changes("test-sales")
    assert res["applicable"] is True
    assert "daily" in res
    assert "weekly" in res
    assert "monthly" in res

def test_change_detector_no_dates():
    res = ChangeDetectorService.detect_changes("test-no_dates")
    assert res["applicable"] is False
    assert "reason" in res
