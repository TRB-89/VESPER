"""Unit tests for RBI DBIE and CCIL availability assessments."""

import pytest

from research.spike.probe_rbi_ccil import get_ccil_assessment, get_rbi_dbie_assessment


def test_rbi_dbie_assessment():
    rbi = get_rbi_dbie_assessment()
    assert rbi.provider_id == "rbi_dbie"
    assert "https://dbie.rbi.org.in" in rbi.portal_urls
    assert rbi.license_status == "HUMAN REVIEW REQUIRED"
    assert len(rbi.series_available) >= 4
    assert any("Policy Rates" in s["series_name"] for s in rbi.series_available)
    assert any("Sovereign Yields" in s["series_name"] for s in rbi.series_available)
    assert "CSV" in rbi.formats_available


def test_ccil_assessment():
    ccil = get_ccil_assessment()
    assert ccil.provider_id == "ccil_fbil"
    assert "https://www.ccilindia.com" in ccil.portal_urls
    assert ccil.license_status == "HUMAN REVIEW REQUIRED"
    assert len(ccil.series_available) >= 4
    assert any("MIBOR" in s["details"] for s in ccil.series_available)
    assert any("ZCYC" in s["details"] for s in ccil.series_available)
    assert "proprietary" in ccil.redistribution_terms.lower()
