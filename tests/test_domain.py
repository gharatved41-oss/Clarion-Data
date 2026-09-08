import pytest
from services.domain_detector import DomainDetectorService

def test_domain_sales():
    res = DomainDetectorService.detect_domain("test-sales")
    assert res["domain"] == "sales"
    assert res["confidence"] > 0.5
    assert len(res["evidence"]) > 0

def test_domain_payment():
    res = DomainDetectorService.detect_domain("test-payment")
    assert res["domain"] == "payment"
    assert res["confidence"] > 0.5

def test_domain_marketing():
    res = DomainDetectorService.detect_domain("test-marketing")
    assert res["domain"] == "marketing"
    assert res["confidence"] > 0.5

def test_domain_healthcare():
    res = DomainDetectorService.detect_domain("test-healthcare")
    assert res["domain"] == "healthcare"
    assert res["confidence"] > 0.5

def test_domain_unseen():
    res = DomainDetectorService.detect_domain("test-unseen_tabular")
    assert "domain" in res
