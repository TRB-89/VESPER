"""Unit tests for Phase 00 analysis module."""

import datetime
from pathlib import Path
import pytest

from research.spike.analyze import (
    CORPORATE_ACTION_CANDIDATES,
    load_all_local_nse_records,
    run_complete_analysis,
)


def test_corporate_action_candidates_structure():
    assert len(CORPORATE_ACTION_CANDIDATES) == 5
    symbols = {c["symbol"] for c in CORPORATE_ACTION_CANDIDATES}
    assert "RELIANCE" in symbols
    assert "TCS" in symbols
    assert "INFY" in symbols
    assert "HDFCBANK" in symbols

    # Check verified ex-dates
    reliance = [c for c in CORPORATE_ACTION_CANDIDATES if c["symbol"] == "RELIANCE"][0]
    assert reliance["verified_ex_date"] == datetime.date(2017, 9, 7)
    assert reliance["announced_ratio"] == 2.0


def test_load_all_local_nse_records():
    df_nse = load_all_local_nse_records()
    # At least our downloaded sample should be loaded
    assert len(df_nse) > 0
    assert "symbol" in df_nse.columns
    assert "session_date" in df_nse.columns


def test_run_complete_analysis(tmp_path: Path, monkeypatch):
    test_out = tmp_path / "test_analysis.md"
    monkeypatch.setattr("research.spike.analyze.OUTPUT_DOC_PATH", test_out)

    report_text = run_complete_analysis()
    assert test_out.exists()
    assert "1. Instrument Coverage Analysis" in report_text
    assert "2. Sessions vs NSE Trading Calendar" in report_text
    assert "3. Data Integrity & Validation Audit" in report_text
    assert "4. Cross-Provider Discrepancy Analysis" in report_text
    assert "5. Corporate Actions Audit" in report_text
    assert "6. Publication Timestamps" in report_text
