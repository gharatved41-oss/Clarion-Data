import pytest
from services.summary_generator import SummaryGeneratorService

def test_summary_sales():
    res = SummaryGeneratorService.generate_summary("test-sales")
    assert "summary" in res
    assert len(res["summary"]) > 20
    assert "facts" in res
    assert res["facts"]["record_count"] == 100

def test_summary_payment():
    res = SummaryGeneratorService.generate_summary("test-payment")
    assert "summary" in res
    assert "facts" in res
    assert res["facts"]["domain"] == "payment"
