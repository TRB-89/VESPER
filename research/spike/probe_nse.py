"""NSE Equity Bhavcopy and Index Historical Data Probe for VESPER Phase 00.

Supports:
- Legacy equity bhavcopy: cm<DD><MMM><YYYY>bhav.csv.zip (pre-July 2024)
- Current UDiFF format: BhavCopy_NSE_CM_0_0_0_<YYYYMMDD>_F_0000.csv.zip (July 2024+)
- Unified full bhavcopy: sec_bhavdata_full_<DDMMYYYY>.csv
- Daily historical index data: ind_close_all_<DDMMYYYY>.csv
"""

from __future__ import annotations

import datetime
import io
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple, Union
import zipfile

import pandas as pd
import requests

from research.spike.common import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_RAW_DIR,
    GLOBAL_RATE_LIMITER,
    NORMALIZED_COLUMNS,
    get_utc_now_iso,
    normalize_records,
    save_raw_file,
)

TARGET_EQUITY_UNIVERSE = {
    "RELIANCE",
    "HDFCBANK",
    "TCS",
    "INFY",
    "ICICIBANK",
    "SBIN",
}

TARGET_INDEX_UNIVERSE = {
    "NIFTY 50",
    "NIFTY BANK",
}

INDEX_NAME_MAPPINGS = {
    "NIFTY 50": "NIFTY 50",
    "NIFTY BANK": "NIFTY BANK",
    "BANK NIFTY": "NIFTY BANK",
}

UDIFF_TRANSITION_DATE = datetime.date(2024, 7, 8)
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def parse_legacy_bhavcopy(
    csv_text: str,
    symbols: Optional[Iterable[str]] = None,
    session_date: Optional[datetime.date] = None,
    source: str = "nse_equity_legacy",
    retrieved_at: Optional[str] = None,
) -> pd.DataFrame:
    """Parse legacy NSE equity bhavcopy CSV (pre-July 2024).

    Columns: SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
    """
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip().upper() for c in df.columns]

    # Filter for EQ series (standard equity)
    if "SERIES" in df.columns:
        df = df[df["SERIES"].str.strip().str.upper() == "EQ"]

    target_syms = {s.upper() for s in symbols} if symbols else None
    if target_syms:
        df = df[df["SYMBOL"].str.strip().str.upper().isin(target_syms)]

    if df.empty:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)

    # Resolve date
    if session_date is not None:
        dates = [session_date] * len(df)
    else:
        dates = pd.to_datetime(df["TIMESTAMP"].str.strip(), format="%d-%b-%Y").dt.date

    records = []
    for idx, (_, row) in enumerate(df.iterrows()):
        records.append(
            {
                "symbol": str(row["SYMBOL"]).strip().upper(),
                "session_date": dates[idx] if isinstance(dates, list) else dates.iloc[idx],
                "open": row["OPEN"],
                "high": row["HIGH"],
                "low": row["LOW"],
                "close": row["CLOSE"],
                "volume": row["TOTTRDQTY"],
                "source": source,
                "retrieved_at": retrieved_at or get_utc_now_iso(),
            }
        )

    return normalize_records(records, source=source, retrieved_at=retrieved_at)


def parse_udiff_bhavcopy(
    csv_text: str,
    symbols: Optional[Iterable[str]] = None,
    source: str = "nse_equity_udiff",
    retrieved_at: Optional[str] = None,
) -> pd.DataFrame:
    """Parse modern UDiFF NSE CM bhavcopy CSV (July 2024+).

    Columns: TradDt,BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,ISIN,TckrSymb,SctySrs,OpnPric,HghPric,LwPric,ClsPric,TtlTradgVol,...
    """
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip() for c in df.columns]

    # Series EQ & Segment CM
    if "SctySrs" in df.columns:
        df = df[df["SctySrs"].astype(str).str.strip().str.upper() == "EQ"]

    target_syms = {s.upper() for s in symbols} if symbols else None
    if target_syms and "TckrSymb" in df.columns:
        df = df[df["TckrSymb"].astype(str).str.strip().str.upper().isin(target_syms)]

    if df.empty:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)

    records = []
    for _, row in df.iterrows():
        sdate = pd.to_datetime(str(row["TradDt"]).strip()).date()
        records.append(
            {
                "symbol": str(row["TckrSymb"]).strip().upper(),
                "session_date": sdate,
                "open": row["OpnPric"],
                "high": row["HghPric"],
                "low": row["LwPric"],
                "close": row["ClsPric"],
                "volume": row["TtlTradgVol"],
                "source": source,
                "retrieved_at": retrieved_at or get_utc_now_iso(),
            }
        )

    return normalize_records(records, source=source, retrieved_at=retrieved_at)


def parse_sec_bhavdata(
    csv_text: str,
    symbols: Optional[Iterable[str]] = None,
    source: str = "nse_equity_sec_bhavdata",
    retrieved_at: Optional[str] = None,
) -> pd.DataFrame:
    """Parse sec_bhavdata_full_<DDMMYYYY>.csv format."""
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip().upper() for c in df.columns]

    if "SERIES" in df.columns:
        df = df[df["SERIES"].str.strip().str.upper() == "EQ"]

    target_syms = {s.upper() for s in symbols} if symbols else None
    if target_syms:
        df = df[df["SYMBOL"].str.strip().str.upper().isin(target_syms)]

    if df.empty:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)

    records = []
    for _, row in df.iterrows():
        sdate = pd.to_datetime(str(row["DATE1"]).strip(), format="%d-%b-%Y").date()
        records.append(
            {
                "symbol": str(row["SYMBOL"]).strip().upper(),
                "session_date": sdate,
                "open": row["OPEN_PRICE"],
                "high": row["HIGH_PRICE"],
                "low": row["LOW_PRICE"],
                "close": row["CLOSE_PRICE"],
                "volume": row["TTL_TRD_QNTY"],
                "source": source,
                "retrieved_at": retrieved_at or get_utc_now_iso(),
            }
        )

    return normalize_records(records, source=source, retrieved_at=retrieved_at)


def parse_index_bhavcopy(
    csv_text: str,
    indices: Optional[Iterable[str]] = None,
    source: str = "nse_index",
    retrieved_at: Optional[str] = None,
) -> pd.DataFrame:
    """Parse NSE index daily file: ind_close_all_<DDMMYYYY>.csv.

    Columns: Index Name,Index Date,Open Index Value,High Index Value,Low Index Value,Closing Index Value,Points Change,Change(%),Volume,...
    """
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip() for c in df.columns]

    name_col = "Index Name"
    date_col = "Index Date"
    if name_col not in df.columns or date_col not in df.columns:
        raise ValueError(f"Unexpected index file format: {df.columns.tolist()}")

    df["NormName"] = df[name_col].str.strip().str.upper()

    target_indices = {s.upper() for s in (indices or TARGET_INDEX_UNIVERSE)}
    # Match standard index names
    mask = df["NormName"].isin(target_indices)
    filtered = df[mask]

    if filtered.empty:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)

    records = []
    for _, row in filtered.iterrows():
        raw_name = str(row[name_col]).strip().upper()
        standard_symbol = INDEX_NAME_MAPPINGS.get(raw_name, raw_name)
        sdate = pd.to_datetime(str(row[date_col]).strip(), format="%d-%m-%Y").date()
        vol = row.get("Volume")
        records.append(
            {
                "symbol": standard_symbol,
                "session_date": sdate,
                "open": row["Open Index Value"],
                "high": row["High Index Value"],
                "low": row["Low Index Value"],
                "close": row["Closing Index Value"],
                "volume": vol if pd.notna(vol) and str(vol).strip() not in ("-", "") else None,
                "source": source,
                "retrieved_at": retrieved_at or get_utc_now_iso(),
            }
        )

    return normalize_records(records, source=source, retrieved_at=retrieved_at)


def fetch_nse_equity_session(
    session_date: datetime.date,
    symbols: Optional[Iterable[str]] = None,
    raw_dir: Path = DEFAULT_RAW_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    session: Optional[requests.Session] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Fetch and normalize NSE equity bhavcopy for a specific session date.

    Returns:
        (DataFrame, None) on success
        (None, error_or_block_message) on failure or block
    """
    http = session or requests.Session()
    http.headers.update(DEFAULT_HEADERS)
    symbols_to_keep = set(symbols or TARGET_EQUITY_UNIVERSE)

    # Determine URL and format based on date
    if session_date >= UDIFF_TRANSITION_DATE:
        # Current UDiFF format
        date_str = session_date.strftime("%Y%m%d")
        url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
        filename = f"BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"
        parser_type = "udiff"
    else:
        # Legacy format
        dd = session_date.strftime("%d")
        mmm = session_date.strftime("%b").upper()
        yyyy = session_date.strftime("%Y")
        url = f"https://archives.nseindia.com/content/historical/EQUITIES/{yyyy}/{mmm}/cm{dd}{mmm}{yyyy}bhav.csv.zip"
        filename = f"cm{dd}{mmm}{yyyy}bhav.csv.zip"
        parser_type = "legacy"

    # Respect rate limiting >= 2.0s
    GLOBAL_RATE_LIMITER.wait(url)

    try:
        resp = http.get(url, timeout=15)
        if resp.status_code in (401, 403, 429, 503):
            return None, f"HTTP_BLOCKED: status {resp.status_code} on {url}"
        if resp.status_code == 404:
            return None, f"NOT_FOUND: status 404 on {url} (possible non-trading session/holiday)"
        if resp.status_code != 200:
            return None, f"HTTP_ERROR: status {resp.status_code} on {url}"

        # Save raw bytes unchanged
        save_raw_file(
            provider="nse",
            partition_date=session_date,
            filename=filename,
            content=resp.content,
            url_or_call=url,
            parser_version=f"nse_cm_{parser_type}_v1.0",
            raw_base_dir=raw_dir,
            manifest_path=manifest_path,
        )

        # Extract zipped CSV
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            csv_name = z.namelist()[0]
            csv_text = z.read(csv_name).decode("utf-8", errors="replace")

        if parser_type == "udiff":
            df = parse_udiff_bhavcopy(csv_text, symbols=symbols_to_keep)
        else:
            df = parse_legacy_bhavcopy(csv_text, symbols=symbols_to_keep, session_date=session_date)

        return df, None

    except Exception as e:
        return None, f"EXCEPTION: {type(e).__name__}: {str(e)}"


def fetch_nse_index_session(
    session_date: datetime.date,
    indices: Optional[Iterable[str]] = None,
    raw_dir: Path = DEFAULT_RAW_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    session: Optional[requests.Session] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Fetch and normalize NSE index data for a specific session date."""
    http = session or requests.Session()
    http.headers.update(DEFAULT_HEADERS)
    indices_to_keep = set(indices or TARGET_INDEX_UNIVERSE)

    ddmmyyyy = session_date.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/content/indices/ind_close_all_{ddmmyyyy}.csv"
    filename = f"ind_close_all_{ddmmyyyy}.csv"

    # Respect rate limiting >= 2.0s
    GLOBAL_RATE_LIMITER.wait(url)

    try:
        resp = http.get(url, timeout=15)
        if resp.status_code in (401, 403, 429, 503):
            return None, f"HTTP_BLOCKED: status {resp.status_code} on {url}"
        if resp.status_code == 404:
            return None, f"NOT_FOUND: status 404 on {url} (possible non-trading session/holiday)"
        if resp.status_code != 200:
            return None, f"HTTP_ERROR: status {resp.status_code} on {url}"

        # Save raw content unchanged
        save_raw_file(
            provider="nse",
            partition_date=session_date,
            filename=filename,
            content=resp.content,
            url_or_call=url,
            parser_version="nse_index_v1.0",
            raw_base_dir=raw_dir,
            manifest_path=manifest_path,
        )

        df = parse_index_bhavcopy(resp.text, indices=indices_to_keep)
        return df, None

    except Exception as e:
        return None, f"EXCEPTION: {type(e).__name__}: {str(e)}"
