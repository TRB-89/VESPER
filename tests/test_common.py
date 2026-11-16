import datetime
import hashlib
from pathlib import Path
import time
import pandas as pd
import pytest

from research.spike.common import (
    NORMALIZED_COLUMNS,
    ManifestRow,
    RateLimiter,
    append_to_manifest,
    format_partition_date,
    normalize_records,
    read_manifest,
    save_raw_file,
)


def test_format_partition_date():
    assert format_partition_date(datetime.date(2024, 1, 15)) == "20240115"
    assert format_partition_date("2024-01-15") == "20240115"
    assert format_partition_date("20240115") == "20240115"


def test_save_raw_file_and_manifest(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    manifest_path = tmp_path / "manifest.csv"

    test_content = b"COL1,COL2\nVAL1,VAL2\n"
    expected_sha = hashlib.sha256(test_content).hexdigest()
    expected_size = len(test_content)

    row = save_raw_file(
        provider="test_prov",
        partition_date="2024-01-15",
        filename="test_file.csv",
        content=test_content,
        url_or_call="https://example.com/api",
        parser_version="1.0.0",
        raw_base_dir=raw_dir,
        manifest_path=manifest_path,
        retrieved_at="2024-01-15T10:00:00Z",
    )

    assert row.provider == "test_prov"
    assert row.sha256 == expected_sha
    assert row.byte_size == expected_size
    assert row.parser_version == "1.0.0"

    saved_file = raw_dir / "test_prov" / "20240115" / "test_file.csv"
    assert saved_file.exists()
    assert saved_file.read_bytes() == test_content

    # Verify manifest
    manifest_df = read_manifest(manifest_path)
    assert len(manifest_df) == 1
    assert manifest_df.iloc[0]["provider"] == "test_prov"
    assert manifest_df.iloc[0]["sha256"] == expected_sha
    assert int(manifest_df.iloc[0]["byte_size"]) == expected_size


def test_normalize_records_equity():
    raw_data = [
        {
            "symbol": "reliance ",
            "date": "2024-01-15",
            "open": "2500.5",
            "high": "2520.0",
            "low": "2490.0",
            "close": "2510.25",
            "volume": 1234567,
        }
    ]
    df = normalize_records(raw_data, source="test_source", retrieved_at="2024-01-15T12:00:00Z")

    assert list(df.columns) == NORMALIZED_COLUMNS
    assert len(df) == 1
    row = df.iloc[0]
    assert row["symbol"] == "RELIANCE"
    assert row["session_date"] == datetime.date(2024, 1, 15)
    assert row["open"] == 2500.5
    assert row["high"] == 2520.0
    assert row["low"] == 2490.0
    assert row["close"] == 2510.25
    assert row["volume"] == 1234567.0
    assert row["source"] == "test_source"
    assert row["retrieved_at"] == "2024-01-15T12:00:00Z"


def test_normalize_records_index_null_volume():
    raw_data = [
        {
            "symbol": "NIFTY 50",
            "session_date": datetime.date(2024, 1, 15),
            "open": 21500.0,
            "high": 21600.0,
            "low": 21450.0,
            "close": 21550.0,
            "volume": None,
        }
    ]
    df = normalize_records(raw_data, source="nse_index")
    assert pd.isna(df.iloc[0]["volume"])
    assert df.iloc[0]["symbol"] == "NIFTY 50"


def test_normalize_records_missing_required_column():
    invalid_data = [{"symbol": "INFY", "date": "2024-01-15", "open": 1500.0}]
    with pytest.raises(ValueError, match="Missing required price column"):
        normalize_records(invalid_data, source="test")


def test_rate_limiter():
    limiter = RateLimiter(min_delay_seconds=0.05)
    t0 = time.monotonic()
    limiter.wait("https://api.example.com/item1")
    limiter.wait("https://api.example.com/item2")
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.045
