"""Common contract for VESPER Phase 00 Data Provider Spike.

Provides raw payload persistence, manifest logging, and schema normalization
for all data provider probes.
"""

from __future__ import annotations

import csv
import datetime
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import time
from typing import Any, Iterable, Optional, Union
import urllib.parse

import pandas as pd
import requests

# Base paths
DEFAULT_RAW_DIR = Path("data/raw/spike")
DEFAULT_MANIFEST_PATH = Path("data/raw/spike/manifest.csv")

MANIFEST_HEADERS = [
    "provider",
    "url_or_call",
    "retrieved_at",
    "file_path",
    "sha256",
    "byte_size",
    "parser_version",
]

NORMALIZED_COLUMNS = [
    "symbol",
    "session_date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
    "retrieved_at",
]


@dataclass(frozen=True)
class ManifestRow:
    """Row recorded in the fetch manifest."""
    provider: str
    url_or_call: str
    retrieved_at: str  # ISO-8601 UTC
    file_path: str
    sha256: str
    byte_size: int
    parser_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format with 'Z' suffix."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_partition_date(date_val: Union[datetime.date, datetime.datetime, str]) -> str:
    """Format a date as YYYYMMDD string for directory partitioning."""
    if isinstance(date_val, (datetime.date, datetime.datetime)):
        return date_val.strftime("%Y%m%d")
    clean = str(date_val).replace("-", "").replace("/", "").strip()
    if len(clean) == 8 and clean.isdigit():
        return clean
    # Attempt parsing arbitrary date string
    try:
        parsed = pd.to_datetime(clean).date()
        return parsed.strftime("%Y%m%d")
    except Exception:
        return clean[:8]


def save_raw_file(
    provider: str,
    partition_date: Union[datetime.date, datetime.datetime, str],
    filename: str,
    content: bytes,
    url_or_call: str,
    parser_version: str,
    raw_base_dir: Path = DEFAULT_RAW_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    retrieved_at: Optional[str] = None,
) -> ManifestRow:
    """Save raw file unchanged under data/raw/spike/<provider>/<YYYYMMDD>/ and append manifest row.

    Args:
        provider: Provider identifier (e.g. 'nse', 'yahoo').
        partition_date: Date partition for directory (e.g. session date or fetch date).
        filename: Name of the raw file to save.
        content: Raw byte contents unchanged.
        url_or_call: URL or API method call string.
        parser_version: Semantic parser version string.
        raw_base_dir: Root directory for raw data.
        manifest_path: Path to CSV manifest file.
        retrieved_at: ISO UTC timestamp (defaults to current UTC time).

    Returns:
        ManifestRow recorded in manifest.
    """
    date_str = format_partition_date(partition_date)
    target_dir = raw_base_dir / provider / date_str
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    # Write raw content unchanged
    target_path.write_bytes(content)

    # Compute sha256 and byte size
    sha256_hash = hashlib.sha256(content).hexdigest()
    byte_size = len(content)
    timestamp = retrieved_at or get_utc_now_iso()

    # Manifest row with normalized relative path forward slashes
    rel_path = target_path.as_posix()
    row = ManifestRow(
        provider=provider,
        url_or_call=url_or_call,
        retrieved_at=timestamp,
        file_path=rel_path,
        sha256=sha256_hash,
        byte_size=byte_size,
        parser_version=parser_version,
    )

    append_to_manifest(row, manifest_path=manifest_path)
    return row


def append_to_manifest(row: ManifestRow, manifest_path: Path = DEFAULT_MANIFEST_PATH) -> None:
    """Append a ManifestRow to the manifest CSV file."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = manifest_path.exists() and manifest_path.stat().st_size > 0

    with open(manifest_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row.to_dict())


def read_manifest(manifest_path: Path = DEFAULT_MANIFEST_PATH) -> pd.DataFrame:
    """Read manifest as a DataFrame, returning empty DataFrame if not present."""
    if not manifest_path.exists() or manifest_path.stat().st_size == 0:
        return pd.DataFrame(columns=MANIFEST_HEADERS)
    return pd.read_csv(manifest_path)


def normalize_records(
    records: Union[pd.DataFrame, list[dict[str, Any]]],
    source: str,
    retrieved_at: Optional[str] = None,
) -> pd.DataFrame:
    """Normalize input records into the standardized VESPER schema.

    Schema:
        symbol: str
        session_date: datetime.date (IST exchange session)
        open: float
        high: float
        low: float
        close: float
        volume: Optional[float] (nullable for indices)
        source: str
        retrieved_at: str (ISO UTC)

    Args:
        records: DataFrame or list of dicts.
        source: Provider/pipeline identifier.
        retrieved_at: Fallback ISO UTC timestamp if not in records.

    Returns:
        Standardized pandas DataFrame.
    """
    if isinstance(records, pd.DataFrame):
        df = records.copy()
    else:
        df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=NORMALIZED_COLUMNS)

    # Standardize column names (lowercase, stripped)
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Handle required mappings / fallbacks
    if "symbol" not in df.columns:
        raise ValueError("Missing 'symbol' column in raw records.")
    if "session_date" not in df.columns:
        if "date" in df.columns:
            df["session_date"] = df["date"]
        elif "timestamp" in df.columns:
            df["session_date"] = df["timestamp"]
        else:
            raise ValueError("Missing date column ('session_date' or 'date').")

    # Symbols clean
    df["symbol"] = df["symbol"].astype(str).str.strip().str.upper()

    # Session dates -> datetime.date
    if not pd.api.types.is_datetime64_any_dtype(df["session_date"]):
        df["session_date"] = pd.to_datetime(df["session_date"]).dt.date
    else:
        df["session_date"] = df["session_date"].dt.date

    # Numeric OHLC
    for col in ["open", "high", "low", "close"]:
        if col not in df.columns:
            raise ValueError(f"Missing required price column: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

    # Volume (nullable for indices)
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    else:
        df["volume"] = None

    # Source & retrieved_at
    if "source" not in df.columns:
        df["source"] = source
    else:
        df["source"] = df["source"].fillna(source).astype(str)

    default_ts = retrieved_at or get_utc_now_iso()
    if "retrieved_at" not in df.columns:
        df["retrieved_at"] = default_ts
    else:
        df["retrieved_at"] = df["retrieved_at"].fillna(default_ts).astype(str)

    # Order and subset columns
    df = df[NORMALIZED_COLUMNS].reset_index(drop=True)
    return df


class RateLimiter:
    """Enforce minimum delay between HTTP requests per domain (default >= 2.0s)."""

    def __init__(self, min_delay_seconds: float = 2.0) -> None:
        self.min_delay_seconds = min_delay_seconds
        self._last_call_times: dict[str, float] = {}

    def wait(self, url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc or "default"
        now = time.monotonic()
        last_time = self._last_call_times.get(domain)

        if last_time is not None:
            elapsed = now - last_time
            if elapsed < self.min_delay_seconds:
                sleep_time = self.min_delay_seconds - elapsed
                time.sleep(sleep_time)

        self._last_call_times[domain] = time.monotonic()


# Global rate limiter instance
GLOBAL_RATE_LIMITER = RateLimiter(min_delay_seconds=2.0)
