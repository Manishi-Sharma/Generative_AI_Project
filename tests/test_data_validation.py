import pytest
from modules.data_validation import DataValidator
from utils.validators import sanitize_number, is_valid_url

def test_sanitize_number_units_and_currencies():
    assert sanitize_number("$12.5 Billion") == 12.5e9
    assert sanitize_number("₹ 5,000 Cr") == 5000e7
    assert sanitize_number("450.25 M") == 450.25e6
    assert sanitize_number("-15.4%") == -15.4
    assert sanitize_number("invalid") is None

def test_is_valid_url():
    assert is_valid_url("https://www.sec.gov") is True
    assert is_valid_url("http://localhost:8501") is True
    assert is_valid_url("not-a-url") is False
    assert is_valid_url(None) is False

def test_data_validator_deduplication():
    records = [
        {
            "metric_name": "Revenue",
            "value": 100.0,
            "source_name": "Web Page Content",
            "status": "PUBLIC INFORMATION FOUND"
        },
        {
            "metric_name": "Revenue",
            "value": 105.0,
            "source_name": "U.S. SEC EDGAR (10-K Filing)",
            "status": "PUBLIC INFORMATION FOUND"
        }
    ]

    cleaned = DataValidator.deduplicate_and_clean(records)
    # Should select SEC EDGAR as higher fidelity
    assert len(cleaned) == 1
    assert cleaned[0]["value"] == 105.0
    assert "SEC EDGAR" in cleaned[0]["source_name"]

def test_audit_sanity_checks():
    # Net profit > revenue triggers sanity note
    anomalous_data = {
        "Revenue": 1000.0,
        "Net Profit": 2500.0
    }
    warnings = DataValidator.audit_sanity(anomalous_data)
    assert any("Net Profit exceeds Revenue" in w for w in warnings)
