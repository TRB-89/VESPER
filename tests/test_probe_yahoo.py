"""Unit tests for Yahoo Finance probe parser."""

import datetime
import pandas as pd
import pytest

from research.spike.common import NORMALIZED_COLUMNS
from research.spike.probe_yahoo import parse_yahoo_dataframe


def test_parse_yahoo_dataframe_equity():
    dates = pd.date_range("2024-01-01", periods=2, freq="D", tz="Asia/Kolkata")
    data = {
        "open": [100.0, 105.0],
        "high": [105.0, 110.0],
        "low": [98.0, 102.0],
        "close": [102.0, 108.0],
        "adj close": [51.0, 54.0],  # 2:1 split adjustment
        "volume": [1000000, 1200000],
    }
    raw_df = pd.DataFrame(data, index=dates)

    df_raw, df_adj = parse_yahoo_dataframe(raw_df, standard_symbol="TCS")

    assert list(df_raw.columns) == NORMALIZED_COLUMNS
    assert list(df_adj.columns) == NORMALIZED_COLUMNS

    assert len(df_raw) == 2
    assert len(df_adj) == 2

    # Check raw
    assert df_raw.iloc[0]["symbol"] == "TCS"
    assert df_raw.iloc[0]["session_date"] == datetime.date(2024, 1, 1)
    assert df_raw.iloc[0]["close"] == 102.0
    assert df_raw.iloc[0]["source"] == "yahoo_raw"
    assert df_raw.iloc[0]["volume"] == 1000000.0

    # Check adjusted (factor = 51.0 / 102.0 = 0.5)
    assert df_adj.iloc[0]["symbol"] == "TCS"
    assert df_adj.iloc[0]["close"] == 51.0
    assert df_adj.iloc[0]["open"] == 50.0  # 100.0 * 0.5
    assert df_adj.iloc[0]["source"] == "yahoo_adjusted"


def test_parse_yahoo_dataframe_index_null_volume():
    dates = pd.date_range("2024-01-01", periods=1, freq="D")
    data = {
        "open": [21500.0],
        "high": [21600.0],
        "low": [21400.0],
        "close": [21550.0],
        "adj close": [21550.0],
        "volume": [0],  # Often 0 or irrelevant for indices
    }
    raw_df = pd.DataFrame(data, index=dates)

    df_raw, df_adj = parse_yahoo_dataframe(raw_df, standard_symbol="NIFTY 50")
    assert pd.isna(df_raw.iloc[0]["volume"])
    assert pd.isna(df_adj.iloc[0]["volume"])
    assert df_raw.iloc[0]["symbol"] == "NIFTY 50"


def test_parse_yahoo_dataframe_multiindex_columns():
    dates = pd.date_range("2024-01-01", periods=1, freq="D")
    cols = pd.MultiIndex.from_tuples(
        [
            ("Open", "RELIANCE.NS"),
            ("High", "RELIANCE.NS"),
            ("Low", "RELIANCE.NS"),
            ("Close", "RELIANCE.NS"),
            ("Adj Close", "RELIANCE.NS"),
            ("Volume", "RELIANCE.NS"),
        ]
    )
    data = [[2500.0, 2520.0, 2480.0, 2510.0, 2510.0, 500000]]
    raw_df = pd.DataFrame(data, index=dates, columns=cols)

    df_raw, df_adj = parse_yahoo_dataframe(raw_df, standard_symbol="RELIANCE")
    assert len(df_raw) == 1
    assert df_raw.iloc[0]["close"] == 2510.0
    assert df_raw.iloc[0]["symbol"] == "RELIANCE"
