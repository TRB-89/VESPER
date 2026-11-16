"""Unit tests for NSE equity bhavcopy and index parsers."""

import datetime
import pandas as pd
import pytest

from research.spike.common import NORMALIZED_COLUMNS
from research.spike.probe_nse import (
    parse_index_bhavcopy,
    parse_legacy_bhavcopy,
    parse_sec_bhavdata,
    parse_udiff_bhavcopy,
)

LEGACY_BHAVCOPY_SAMPLE = """SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
RELIANCE,EQ,2500.0,2520.0,2490.0,2510.0,2512.0,2495.0,1500000,3765000000,15-JAN-2024,45000,INE002A01018
RELIANCE,BL,2505.0,2505.0,2505.0,2505.0,2505.0,2495.0,500000,1252500000,15-JAN-2024,1,INE002A01018
INFY,EQ,1600.0,1625.0,1595.0,1615.0,1618.0,1590.0,800000,1292000000,15-JAN-2024,25000,INE009A01021
XYZ,EQ,10.0,11.0,9.5,10.5,10.5,10.0,10000,105000,15-JAN-2024,100,INE000000000
"""

UDIFF_BHAVCOPY_SAMPLE = """TradDt,BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,ISIN,TckrSymb,SctySrs,XpryDt,FininstrmActlXpryDt,StrkPric,OptnTp,FinInstrmNm,OpnPric,HghPric,LwPric,ClsPric,LastPric,PrvsClsgPric,UndrlygPric,SttlmPric,OpnIntrst,ChngInOpnIntrst,TtlTradgVol,TtlTrfVal,TtlNbOfTxsExctd,SsnId,NewBrdLotQty,Rmks,Rsvd1,Rsvd2,Rsvd3,Rsvd4
2024-07-10,2024-07-10,CM,NSE,STK,2885,INE002A01018,RELIANCE,EQ,,,,,RELIANCE IND LTD,3180.0,3200.0,3170.0,3195.0,3196.0,3175.0,,,0,0,2500000,7987500000,80000,1,1,,,
2024-07-10,2024-07-10,CM,NSE,STK,2885,INE002A01018,RELIANCE,BL,,,,,RELIANCE IND LTD,3185.0,3185.0,3185.0,3185.0,3185.0,3175.0,,,0,0,100000,318500000,1,1,1,,,
2024-07-10,2024-07-10,CM,NSE,STK,1594,INE009A01021,INFY,EQ,,,,,INFOSYS LTD,1650.0,1675.0,1640.0,1660.0,1662.0,1645.0,,,0,0,1200000,1992000000,50000,1,1,,,
"""

INDEX_BHAVCOPY_SAMPLE = """Index Name,Index Date,Open Index Value,High Index Value,Low Index Value,Closing Index Value,Points Change,Change(%),Volume,Turnover (Rs. Cr.),P/E,P/B,Div Yield
Nifty 50,15-01-2024,21800.5,21900.0,21750.0,21850.0,100.0,0.46,180000000,15000.0,23.5,3.9,1.25
Nifty Bank,15-01-2024,48000.0,48300.0,47900.0,48150.0,250.0,0.52,-,8000.0,16.2,2.8,0.95
Nifty IT,15-01-2024,36000.0,36500.0,35900.0,36300.0,400.0,1.11,50000000,4500.0,28.0,6.5,1.80
"""


def test_parse_legacy_bhavcopy():
    df = parse_legacy_bhavcopy(LEGACY_BHAVCOPY_SAMPLE, symbols=["RELIANCE", "INFY"])
    assert len(df) == 2
    assert list(df.columns) == NORMALIZED_COLUMNS

    reliance = df[df["symbol"] == "RELIANCE"].iloc[0]
    assert reliance["session_date"] == datetime.date(2024, 1, 15)
    assert reliance["open"] == 2500.0
    assert reliance["high"] == 2520.0
    assert reliance["low"] == 2490.0
    assert reliance["close"] == 2510.0
    assert reliance["volume"] == 1500000.0
    assert reliance["source"] == "nse_equity_legacy"


def test_parse_udiff_bhavcopy():
    df = parse_udiff_bhavcopy(UDIFF_BHAVCOPY_SAMPLE, symbols=["RELIANCE"])
    assert len(df) == 1
    row = df.iloc[0]
    assert row["symbol"] == "RELIANCE"
    assert row["session_date"] == datetime.date(2024, 7, 10)
    assert row["open"] == 3180.0
    assert row["high"] == 3200.0
    assert row["low"] == 3170.0
    assert row["close"] == 3195.0
    assert row["volume"] == 2500000.0
    assert row["source"] == "nse_equity_udiff"


def test_parse_index_bhavcopy():
    df = parse_index_bhavcopy(INDEX_BHAVCOPY_SAMPLE, indices=["NIFTY 50", "NIFTY BANK"])
    assert len(df) == 2

    nifty50 = df[df["symbol"] == "NIFTY 50"].iloc[0]
    assert nifty50["session_date"] == datetime.date(2024, 1, 15)
    assert nifty50["close"] == 21850.0
    assert nifty50["volume"] == 180000000.0

    niftybank = df[df["symbol"] == "NIFTY BANK"].iloc[0]
    assert niftybank["session_date"] == datetime.date(2024, 1, 15)
    assert niftybank["close"] == 48150.0
    # '-' volume becomes None/null
    assert pd.isna(niftybank["volume"])
