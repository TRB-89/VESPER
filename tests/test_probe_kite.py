"""Unit tests for Zerodha Kite probe documentation stub."""

import os
from pathlib import Path
import pytest

from research.spike.probe_kite import KITE_DOC_STUB, check_kite_credentials, run_kite_probe


def test_kite_probe_stub_without_credentials(monkeypatch):
    monkeypatch.delenv("KITE_API_KEY", raising=False)
    monkeypatch.delenv("KITE_API_SECRET", raising=False)
    monkeypatch.delenv("KITE_ACCESS_TOKEN", raising=False)

    result = run_kite_probe(env_file_path=Path("non_existent_env"))
    assert result["status"] == "DOCUMENTATION_STUB_ONLY"
    assert "documentation" in result

    doc = result["documentation"]
    assert doc["pricing_url"] == "https://kite.trade/pricing"
    assert doc["terms_url"] == "https://kite.trade/terms"
    assert doc["terms_and_licensing"]["license_status"] == "HUMAN REVIEW REQUIRED"

    tiers = doc["product_tiers"]
    assert any("Personal Plan" in t["tier_name"] for t in tiers)
    assert any("Connect Plan" in t["tier_name"] for t in tiers)

    assert "rate_limit" in doc["historical_data_limits"]
