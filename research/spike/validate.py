"""Data validation suite for VESPER Phase 00 Data Provider Spike.

Provides structured check functions and reporting for duplicate records,
nonpositive prices, negative volume, invalid OHLC, missing sessions,
anomalous gaps, and timezone/weekend date shifts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import datetime
from typing import Any, Iterable, Optional, Set

import pandas as pd


@dataclass(frozen=True)
class ValidationIssue:
    """Structured validation finding."""
    check_name: str
    severity: str  # "ERROR" or "WARNING"
    symbol: Optional[str]
    session_date: Optional[datetime.date]
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if isinstance(d["session_date"], (datetime.date, datetime.datetime)):
            d["session_date"] = str(d["session_date"])
        return d


@dataclass
class ValidationReport:
    """Summary report of dataset validation."""
    total_rows: int
    total_symbols: int
    is_valid: bool
    issues: list[ValidationIssue]
    summary_by_check: dict[str, int]
    issues_by_severity: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_rows": self.total_rows,
            "total_symbols": self.total_symbols,
            "is_valid": self.is_valid,
            "summary_by_check": self.summary_by_check,
            "issues_by_severity": self.issues_by_severity,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def get_known_nse_special_weekend_dates() -> set[datetime.date]:
    """Return set of historically known valid NSE weekend sessions (e.g. Budget/Muhurat/DR drill)."""
    return {
        datetime.date(2015, 2, 28),   # Union Budget (Saturday)
        datetime.date(2015, 11, 11),  # Diwali Muhurat
        datetime.date(2016, 10, 30),  # Diwali Muhurat (Sunday)
        datetime.date(2017, 10, 19),  # Diwali Muhurat
        datetime.date(2018, 11, 7),   # Diwali Muhurat
        datetime.date(2019, 10, 27),  # Diwali Muhurat (Sunday)
        datetime.date(2020, 2, 1),    # Union Budget (Saturday)
        datetime.date(2020, 11, 14),  # Diwali Muhurat (Saturday)
        datetime.date(2021, 11, 4),   # Diwali Muhurat
        datetime.date(2022, 10, 24),  # Diwali Muhurat
        datetime.date(2023, 11, 12),  # Diwali Muhurat (Sunday)
        datetime.date(2024, 1, 20),   # Ram Mandir consecration advance session (Saturday)
        datetime.date(2024, 3, 2),    # DR live switch session (Saturday)
        datetime.date(2024, 5, 18),   # DR live switch session (Saturday)
        datetime.date(2024, 11, 1),   # Diwali Muhurat
        datetime.date(2025, 2, 1),    # Union Budget (Saturday)
    }


def check_duplicates(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check for duplicate (symbol, session_date) pairs."""
    issues: list[ValidationIssue] = []
    if df.empty or "symbol" not in df.columns or "session_date" not in df.columns:
        return issues

    dups = df[df.duplicated(subset=["symbol", "session_date"], keep=False)]
    for (sym, sdate), grp in dups.groupby(["symbol", "session_date"]):
        issues.append(
            ValidationIssue(
                check_name="duplicate_symbol_session",
                severity="ERROR",
                symbol=str(sym),
                session_date=sdate if isinstance(sdate, datetime.date) else pd.to_datetime(sdate).date(),
                message=f"Duplicate records found for symbol {sym} on session {sdate} ({len(grp)} occurrences)",
                details={"count": len(grp)},
            )
        )
    return issues


def check_nonpositive_prices(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check for nonpositive (<=0) or NaN prices in open, high, low, close."""
    issues: list[ValidationIssue] = []
    if df.empty:
        return issues

    price_cols = [c for c in ["open", "high", "low", "close"] if c in df.columns]
    for _, row in df.iterrows():
        sym = row.get("symbol")
        sdate = row.get("session_date")
        if isinstance(sdate, (datetime.datetime, pd.Timestamp)):
            sdate = sdate.date()

        bad_fields: dict[str, float] = {}
        for col in price_cols:
            val = row[col]
            if pd.isna(val) or val <= 0:
                bad_fields[col] = float(val) if pd.notna(val) else None

        if bad_fields:
            issues.append(
                ValidationIssue(
                    check_name="nonpositive_price",
                    severity="ERROR",
                    symbol=str(sym) if sym is not None else None,
                    session_date=sdate,
                    message=f"Nonpositive or null price for {sym} on {sdate}: {bad_fields}",
                    details={"invalid_columns": bad_fields},
                )
            )
    return issues


def check_negative_volume(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check for negative volume. (Nullable volume for indices is valid)."""
    issues: list[ValidationIssue] = []
    if df.empty or "volume" not in df.columns:
        return issues

    neg_vol = df[df["volume"].notna() & (df["volume"] < 0)]
    for _, row in neg_vol.iterrows():
        sdate = row["session_date"]
        if isinstance(sdate, (datetime.datetime, pd.Timestamp)):
            sdate = sdate.date()
        issues.append(
            ValidationIssue(
                check_name="negative_volume",
                severity="ERROR",
                symbol=str(row.get("symbol")),
                session_date=sdate,
                message=f"Negative volume {row['volume']} for {row.get('symbol')} on {sdate}",
                details={"volume": float(row["volume"])},
            )
        )
    return issues


def check_invalid_ohlc(df: pd.DataFrame) -> list[ValidationIssue]:
    """Check that high is highest and low is lowest: low <= min(open, close) and max(open, close) <= high."""
    issues: list[ValidationIssue] = []
    if df.empty:
        return issues

    cols = ["open", "high", "low", "close"]
    if not all(c in df.columns for c in cols):
        return issues

    # low <= open, low <= close, high >= open, high >= close, low <= high
    cond = (
        (df["low"] > df["open"])
        | (df["low"] > df["close"])
        | (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["low"] > df["high"])
    )
    invalid_rows = df[cond]

    for _, row in invalid_rows.iterrows():
        sdate = row["session_date"]
        if isinstance(sdate, (datetime.datetime, pd.Timestamp)):
            sdate = sdate.date()
        issues.append(
            ValidationIssue(
                check_name="invalid_ohlc",
                severity="ERROR",
                symbol=str(row.get("symbol")),
                session_date=sdate,
                message=f"Inconsistent OHLC for {row.get('symbol')} on {sdate}: O={row['open']}, H={row['high']}, L={row['low']}, C={row['close']}",
                details={
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                },
            )
        )
    return issues


def check_missing_sessions(
    df: pd.DataFrame,
    calendar: Iterable[datetime.date],
) -> list[ValidationIssue]:
    """Check if any expected trading sessions in calendar are missing for each symbol."""
    issues: list[ValidationIssue] = []
    if df.empty or "symbol" not in df.columns or "session_date" not in df.columns:
        return issues

    expected_dates = set(calendar)
    for sym, grp in df.groupby("symbol"):
        actual_dates = set(
            d.date() if isinstance(d, (datetime.datetime, pd.Timestamp)) else d
            for d in grp["session_date"]
        )
        # Check missing dates within symbol's min and max date range (or overall calendar)
        min_date = min(actual_dates) if actual_dates else min(expected_dates)
        max_date = max(actual_dates) if actual_dates else max(expected_dates)
        in_range_expected = {d for d in expected_dates if min_date <= d <= max_date}
        missing = sorted(in_range_expected - actual_dates)

        for m_date in missing:
            issues.append(
                ValidationIssue(
                    check_name="missing_session",
                    severity="WARNING",
                    symbol=str(sym),
                    session_date=m_date,
                    message=f"Expected trading session {m_date} missing for {sym}",
                    details={"missing_date": str(m_date)},
                )
            )
    return issues


def check_gaps(
    df: pd.DataFrame,
    max_allowed_calendar_gap_days: int = 5,
) -> list[ValidationIssue]:
    """Check for suspicious multi-day gaps between consecutive sessions."""
    issues: list[ValidationIssue] = []
    if df.empty or "symbol" not in df.columns or "session_date" not in df.columns:
        return issues

    for sym, grp in df.groupby("symbol"):
        sorted_dates = sorted(
            set(
                d.date() if isinstance(d, (datetime.datetime, pd.Timestamp)) else d
                for d in grp["session_date"]
            )
        )
        for i in range(len(sorted_dates) - 1):
            d1 = sorted_dates[i]
            d2 = sorted_dates[i + 1]
            diff = (d2 - d1).days
            if diff > max_allowed_calendar_gap_days:
                issues.append(
                    ValidationIssue(
                        check_name="session_gap",
                        severity="WARNING",
                        symbol=str(sym),
                        session_date=d1,
                        message=f"Gap of {diff} calendar days between {d1} and {d2} for {sym}",
                        details={"from_date": str(d1), "to_date": str(d2), "gap_days": diff},
                    )
                )
    return issues


def check_timezone_weekend_shifts(
    df: pd.DataFrame,
    allowed_weekend_dates: Optional[Set[datetime.date]] = None,
) -> list[ValidationIssue]:
    """Check for session dates falling on weekends (Saturdays/Sundays) indicating timezone shifting."""
    issues: list[ValidationIssue] = []
    if df.empty or "session_date" not in df.columns:
        return issues

    if allowed_weekend_dates is None:
        allowed_weekend_dates = get_known_nse_special_weekend_dates()

    for _, row in df.iterrows():
        sdate = row["session_date"]
        if isinstance(sdate, (datetime.datetime, pd.Timestamp)):
            sdate = sdate.date()

        # weekday(): Monday=0, Sunday=6. Saturday=5, Sunday=6
        if sdate.weekday() in (5, 6) and sdate not in allowed_weekend_dates:
            day_name = "Saturday" if sdate.weekday() == 5 else "Sunday"
            issues.append(
                ValidationIssue(
                    check_name="weekend_or_shifted_session",
                    severity="ERROR",
                    symbol=str(row.get("symbol")),
                    session_date=sdate,
                    message=f"Session date {sdate} is a {day_name} (not a known special session) for {row.get('symbol')}. Likely timezone conversion artifact.",
                    details={"weekday": day_name, "raw_date": str(sdate)},
                )
            )
    return issues


def validate_dataset(
    df: pd.DataFrame,
    calendar: Optional[Iterable[datetime.date]] = None,
    allowed_weekend_dates: Optional[Set[datetime.date]] = None,
    max_allowed_calendar_gap_days: int = 5,
) -> ValidationReport:
    """Run all validation checks and return a structured ValidationReport."""
    issues: list[ValidationIssue] = []

    if df.empty:
        return ValidationReport(
            total_rows=0,
            total_symbols=0,
            is_valid=True,
            issues=[],
            summary_by_check={},
            issues_by_severity={"ERROR": 0, "WARNING": 0},
        )

    # 1. Duplicates
    issues.extend(check_duplicates(df))

    # 2. Nonpositive prices
    issues.extend(check_nonpositive_prices(df))

    # 3. Negative volume
    issues.extend(check_negative_volume(df))

    # 4. Invalid OHLC
    issues.extend(check_invalid_ohlc(df))

    # 5. Timezone & weekend shifts
    issues.extend(check_timezone_weekend_shifts(df, allowed_weekend_dates=allowed_weekend_dates))

    # 6. Gaps
    issues.extend(check_gaps(df, max_allowed_calendar_gap_days=max_allowed_calendar_gap_days))

    # 7. Missing sessions against trading calendar (if provided)
    if calendar is not None:
        issues.extend(check_missing_sessions(df, calendar=calendar))

    # Compute summary
    summary_by_check: dict[str, int] = {}
    severity_counts = {"ERROR": 0, "WARNING": 0}
    for issue in issues:
        summary_by_check[issue.check_name] = summary_by_check.get(issue.check_name, 0) + 1
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    total_rows = len(df)
    total_symbols = df["symbol"].nunique() if "symbol" in df.columns else 0
    is_valid = severity_counts["ERROR"] == 0

    return ValidationReport(
        total_rows=total_rows,
        total_symbols=total_symbols,
        is_valid=is_valid,
        issues=issues,
        summary_by_check=summary_by_check,
        issues_by_severity=severity_counts,
    )
