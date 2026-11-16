"""Unit tests for Phase 00 data validation rules.

Tests are written first to establish the validation contract before implementation.
"""

import datetime
import pandas as pd
import pytest

from research.spike.common import normalize_records
from research.spike.validate import (
    ValidationIssue,
    ValidationReport,
    check_duplicates,
    check_gaps,
    check_invalid_ohlc,
    check_missing_sessions,
    check_negative_volume,
    check_nonpositive_prices,
    check_timezone_weekend_shifts,
    validate_dataset,
)


@pytest.fixture
def clean_records() -> pd.DataFrame:
    records = [
        {
            "symbol": "RELIANCE",
            "session_date": datetime.date(2024, 1, 15),  # Monday
            "open": 2500.0,
            "high": 2550.0,
            "low": 2490.0,
            "close": 2540.0,
            "volume": 1000000,
        },
        {
            "symbol": "RELIANCE",
            "session_date": datetime.date(2024, 1, 16),  # Tuesday
            "open": 2540.0,
            "high": 2560.0,
            "low": 2520.0,
            "close": 2550.0,
            "volume": 950000,
        },
        {
            "symbol": "RELIANCE",
            "session_date": datetime.date(2024, 1, 17),  # Wednesday
            "open": 2550.0,
            "high": 2570.0,
            "low": 2530.0,
            "close": 2560.0,
            "volume": 1100000,
        },
    ]
    return normalize_records(records, source="test")


def test_clean_records_pass_validation(clean_records):
    calendar = [
        datetime.date(2024, 1, 15),
        datetime.date(2024, 1, 16),
        datetime.date(2024, 1, 17),
    ]
    report = validate_dataset(clean_records, calendar=calendar)
    assert report.is_valid is True
    assert len(report.issues) == 0
    assert report.total_rows == 3


def test_check_duplicates():
    records = [
        {
            "symbol": "TCS",
            "session_date": datetime.date(2024, 1, 15),
            "open": 3800.0,
            "high": 3850.0,
            "low": 3790.0,
            "close": 3820.0,
            "volume": 500000,
        },
        {
            "symbol": "TCS",
            "session_date": datetime.date(2024, 1, 15),  # Duplicate date!
            "open": 3810.0,
            "high": 3860.0,
            "low": 3800.0,
            "close": 3830.0,
            "volume": 600000,
        },
    ]
    df = normalize_records(records, source="test")
    issues = check_duplicates(df)
    assert len(issues) == 1
    assert issues[0].check_name == "duplicate_symbol_session"
    assert issues[0].symbol == "TCS"
    assert issues[0].session_date == datetime.date(2024, 1, 15)


def test_check_nonpositive_prices():
    records = [
        {
            "symbol": "INFY",
            "session_date": datetime.date(2024, 1, 15),
            "open": 0.0,  # Zero open
            "high": 1500.0,
            "low": -5.0,  # Negative low
            "close": 1490.0,
            "volume": 200000,
        }
    ]
    df = normalize_records(records, source="test")
    issues = check_nonpositive_prices(df)
    assert len(issues) >= 1
    assert any(i.check_name == "nonpositive_price" for i in issues)


def test_check_negative_volume():
    records = [
        {
            "symbol": "SBIN",
            "session_date": datetime.date(2024, 1, 15),
            "open": 600.0,
            "high": 610.0,
            "low": 595.0,
            "close": 605.0,
            "volume": -1000,  # Negative volume
        },
        {
            "symbol": "NIFTY 50",  # Index with null volume is valid
            "session_date": datetime.date(2024, 1, 15),
            "open": 21500.0,
            "high": 21600.0,
            "low": 21400.0,
            "close": 21550.0,
            "volume": None,
        },
    ]
    df = normalize_records(records, source="test")
    issues = check_negative_volume(df)
    assert len(issues) == 1
    assert issues[0].symbol == "SBIN"
    assert issues[0].check_name == "negative_volume"


def test_check_invalid_ohlc():
    records = [
        {
            # High is lower than open
            "symbol": "ICICIBANK",
            "session_date": datetime.date(2024, 1, 15),
            "open": 1000.0,
            "high": 980.0,
            "low": 950.0,
            "close": 970.0,
            "volume": 100000,
        },
        {
            # Low is higher than close
            "symbol": "ICICIBANK",
            "session_date": datetime.date(2024, 1, 16),
            "open": 1000.0,
            "high": 1050.0,
            "low": 1010.0,
            "close": 990.0,
            "volume": 100000,
        },
    ]
    df = normalize_records(records, source="test")
    issues = check_invalid_ohlc(df)
    assert len(issues) == 2
    assert all(i.check_name == "invalid_ohlc" for i in issues)


def test_check_missing_sessions():
    records = [
        {
            "symbol": "HDFCBANK",
            "session_date": datetime.date(2024, 1, 15),
            "open": 1600.0,
            "high": 1620.0,
            "low": 1590.0,
            "close": 1610.0,
            "volume": 500000,
        },
        {
            # Missing 2024-01-16
            "symbol": "HDFCBANK",
            "session_date": datetime.date(2024, 1, 17),
            "open": 1610.0,
            "high": 1630.0,
            "low": 1600.0,
            "close": 1620.0,
            "volume": 550000,
        },
    ]
    df = normalize_records(records, source="test")
    calendar = [
        datetime.date(2024, 1, 15),
        datetime.date(2024, 1, 16),
        datetime.date(2024, 1, 17),
    ]
    issues = check_missing_sessions(df, calendar=calendar)
    assert len(issues) == 1
    assert issues[0].check_name == "missing_session"
    assert issues[0].session_date == datetime.date(2024, 1, 16)
    assert issues[0].symbol == "HDFCBANK"


def test_check_gaps():
    records = [
        {
            "symbol": "RELIANCE",
            "session_date": datetime.date(2024, 1, 1),
            "open": 2500.0,
            "high": 2550.0,
            "low": 2490.0,
            "close": 2540.0,
            "volume": 1000000,
        },
        {
            # 14 days gap
            "symbol": "RELIANCE",
            "session_date": datetime.date(2024, 1, 15),
            "open": 2540.0,
            "high": 2560.0,
            "low": 2520.0,
            "close": 2550.0,
            "volume": 950000,
        },
    ]
    df = normalize_records(records, source="test")
    issues = check_gaps(df, max_allowed_calendar_gap_days=5)
    assert len(issues) == 1
    assert issues[0].check_name == "session_gap"
    assert issues[0].symbol == "RELIANCE"


def test_check_timezone_weekend_shifts():
    records = [
        {
            # 2024-01-20 is a Saturday
            "symbol": "RELIANCE",
            "session_date": datetime.date(2024, 1, 20),
            "open": 2500.0,
            "high": 2550.0,
            "low": 2490.0,
            "close": 2540.0,
            "volume": 1000000,
        },
        {
            # 2024-01-21 is a Sunday
            "symbol": "RELIANCE",
            "session_date": datetime.date(2024, 1, 21),
            "open": 2500.0,
            "high": 2550.0,
            "low": 2490.0,
            "close": 2540.0,
            "volume": 1000000,
        },
    ]
    df = normalize_records(records, source="test")
    issues = check_timezone_weekend_shifts(df, allowed_weekend_dates=set())
    assert len(issues) == 2
    assert all(i.check_name == "weekend_or_shifted_session" for i in issues)
