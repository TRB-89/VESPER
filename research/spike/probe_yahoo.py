"""Yahoo Finance Provider Probe for VESPER Phase 00.

Fetches daily historical OHLCV for Indian equities and indices from 2015-01-01
to present using yfinance. Produces both raw and corporate-action-adjusted series
in normalized VESPER format.
"""

from __future__ import annotations

import datetime
from pathlib import Path
import time
from typing import Dict, Iterable, Optional, Tuple, Union

import pandas as pd
import yfinance as yf

from research.spike.common import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_RAW_DIR,
    GLOBAL_RATE_LIMITER,
    NORMALIZED_COLUMNS,
    get_utc_now_iso,
    normalize_records,
    save_raw_file,
)

YAHOO_TICKER_MAP: dict[str, str] = {
    "NIFTY 50": "^NSEI",
    "NIFTY BANK": "^NSEBANK",
    "RELIANCE": "RELIANCE.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
}

REVERSE_TICKER_MAP: dict[str, str] = {v: k for k, v in YAHOO_TICKER_MAP.items()}


def parse_yahoo_dataframe(
    df_raw: pd.DataFrame,
    standard_symbol: str,
    source_raw: str = "yahoo_raw",
    source_adj: str = "yahoo_adjusted",
    retrieved_at: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Parse raw yfinance DataFrame into separate raw and adjusted normalized DataFrames.

    Args:
        df_raw: MultiIndex or flat DataFrame returned by yf.download or yf.Ticker.history.
        standard_symbol: Standardized symbol (e.g. "RELIANCE", "NIFTY 50").
        source_raw: Source tag for raw prices.
        source_adj: Source tag for adjusted prices.
        retrieved_at: ISO-8601 UTC timestamp.

    Returns:
        (df_normalized_raw, df_normalized_adjusted)
    """
    if df_raw.empty:
        empty = pd.DataFrame(columns=NORMALIZED_COLUMNS)
        return empty, empty.copy()

    df = df_raw.copy()

    # Flatten multi-index columns if present (yfinance >= 0.2.x multi-level columns)
    if isinstance(df.columns, pd.MultiIndex):
        flat_cols = []
        for col in df.columns:
            if isinstance(col, tuple):
                flat_cols.append(col[0].strip().lower())
            else:
                flat_cols.append(str(col).strip().lower())
        df.columns = flat_cols
    else:
        df.columns = [str(c).strip().lower() for c in df.columns]

    # Handle Date / Index cleanly as a Series of Timestamps
    if "date" in df.columns:
        date_series = pd.Series(pd.to_datetime(df["date"]))
    else:
        date_series = pd.Series(pd.to_datetime(df.index))

    # Convert to IST exchange session date (Asia/Kolkata)
    if date_series.dt.tz is not None:
        ist_dates = date_series.dt.tz_convert("Asia/Kolkata").dt.date
    else:
        ist_dates = date_series.dt.date

    ts = retrieved_at or get_utc_now_iso()

    # Raw DataFrame
    raw_records = []
    adj_records = []

    has_adj = "adj close" in df.columns or "adj_close" in df.columns
    adj_col = "adj close" if "adj close" in df.columns else "adj_close"

    is_index = standard_symbol in ("NIFTY 50", "NIFTY BANK")

    for idx in range(len(df)):
        sdate = ist_dates.iloc[idx]
        o = float(df["open"].iloc[idx])
        h = float(df["high"].iloc[idx])
        l = float(df["low"].iloc[idx])
        c = float(df["close"].iloc[idx])
        vol_raw = df["volume"].iloc[idx] if "volume" in df.columns else None
        vol = None if (is_index or pd.isna(vol_raw)) else float(vol_raw)

        raw_records.append(
            {
                "symbol": standard_symbol,
                "session_date": sdate,
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": vol,
                "source": source_raw,
                "retrieved_at": ts,
            }
        )

        if has_adj and c > 0:
            adj_c = float(df[adj_col].iloc[idx])
            factor = adj_c / c
            adj_records.append(
                {
                    "symbol": standard_symbol,
                    "session_date": sdate,
                    "open": round(o * factor, 4),
                    "high": round(h * factor, 4),
                    "low": round(l * factor, 4),
                    "close": round(adj_c, 4),
                    "volume": vol,
                    "source": source_adj,
                    "retrieved_at": ts,
                }
            )
        else:
            adj_records.append(
                {
                    "symbol": standard_symbol,
                    "session_date": sdate,
                    "open": o,
                    "high": h,
                    "low": l,
                    "close": c,
                    "volume": vol,
                    "source": source_adj,
                    "retrieved_at": ts,
                }
            )

    df_norm_raw = normalize_records(raw_records, source=source_raw, retrieved_at=ts)
    df_norm_adj = normalize_records(adj_records, source=source_adj, retrieved_at=ts)

    return df_norm_raw, df_norm_adj


def fetch_yahoo_symbol(
    standard_symbol: str,
    start_date: str = "2015-01-01",
    end_date: Optional[str] = None,
    raw_dir: Path = DEFAULT_RAW_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Optional[str]]:
    """Fetch raw and adjusted OHLCV data from Yahoo Finance for a symbol.

    Args:
        standard_symbol: Standard universe symbol (e.g., 'RELIANCE').
        start_date: Start date YYYY-MM-DD.
        end_date: End date YYYY-MM-DD (defaults to today + 1 day).
        raw_dir: Base directory for raw files.
        manifest_path: Path to manifest CSV.

    Returns:
        (df_raw, df_adj, error_message)
    """
    ticker = YAHOO_TICKER_MAP.get(standard_symbol, standard_symbol)
    url_or_call = f"yfinance.download(ticker='{ticker}', start='{start_date}', end='{end_date or 'latest'}', auto_adjust=False)"

    # Rate limiting >= 2.0s
    GLOBAL_RATE_LIMITER.wait("https://query1.finance.yahoo.com")

    try:
        df = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
        )

        if df.empty:
            return None, None, f"NO_DATA: Yahoo Finance returned empty DataFrame for {ticker}"

        # Save raw content unchanged as CSV bytes
        raw_csv_bytes = df.to_csv().encode("utf-8")
        partition_date = datetime.date.today()
        clean_name = standard_symbol.replace(" ", "_")
        filename = f"{clean_name}_yahoo_raw.csv"

        save_raw_file(
            provider="yahoo",
            partition_date=partition_date,
            filename=filename,
            content=raw_csv_bytes,
            url_or_call=url_or_call,
            parser_version="yfinance_1.8.0",
            raw_base_dir=raw_dir,
            manifest_path=manifest_path,
        )

        df_raw, df_adj = parse_yahoo_dataframe(df, standard_symbol=standard_symbol)
        return df_raw, df_adj, None

    except Exception as e:
        return None, None, f"EXCEPTION: {type(e).__name__}: {str(e)}"


def fetch_all_yahoo_universe(
    symbols: Optional[Iterable[str]] = None,
    start_date: str = "2015-01-01",
    end_date: Optional[str] = None,
    raw_dir: Path = DEFAULT_RAW_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
) -> Tuple[pd.DataFrame, pd.DataFrame, dict[str, Optional[str]]]:
    """Fetch complete target universe from Yahoo Finance."""
    target_symbols = list(symbols or YAHOO_TICKER_MAP.keys())
    raw_dfs = []
    adj_dfs = []
    errors: dict[str, Optional[str]] = {}

    for sym in target_symbols:
        df_raw, df_adj, err = fetch_yahoo_symbol(
            standard_symbol=sym,
            start_date=start_date,
            end_date=end_date,
            raw_dir=raw_dir,
            manifest_path=manifest_path,
        )
        errors[sym] = err
        if df_raw is not None and not df_raw.empty:
            raw_dfs.append(df_raw)
        if df_adj is not None and not df_adj.empty:
            adj_dfs.append(df_adj)

    all_raw = pd.concat(raw_dfs, ignore_index=True) if raw_dfs else pd.DataFrame(columns=NORMALIZED_COLUMNS)
    all_adj = pd.concat(adj_dfs, ignore_index=True) if adj_dfs else pd.DataFrame(columns=NORMALIZED_COLUMNS)
    return all_raw, all_adj, errors
