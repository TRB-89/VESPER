"""Unit tests for NSE F&O probe and assessment."""

import pandas as pd
import pytest

from research.spike.probe_nse_fo import (
    get_derivatives_assessment,
    inspect_fo_fields,
    parse_fo_legacy_csv,
    parse_fo_udiff_csv,
)

SAMPLE_LEGACY_FO_CSV = """INSTRUMENT,SYMBOL,EXPIRY_DT,STRIKE_PR,OPTION_TYP,OPEN,HIGH,LOW,CLOSE,SETTLE_PR,CONTRACTS,VAL_INLAKH,OPEN_INT,CHG_IN_OI,TIMESTAMP
FUTIDX,BANKNIFTY,25-Jan-2024,0,XX,48580.0,48869.0,48389.4,48535.7,48535.7,120422,878243.28,2052195,-25530,01-JAN-2024
OPTIDX,BANKNIFTY,25-Jan-2024,48000.0,CE,950.0,1120.0,880.0,1015.0,1015.0,25000,18000.0,450000,15000,01-JAN-2024
"""

SAMPLE_UDIFF_FO_CSV = """TradDt,BizDt,Sgmt,Src,FinInstrmTp,FinInstrmId,ISIN,TckrSymb,SctySrs,XpryDt,FininstrmActlXpryDt,StrkPric,OptnTp,FinInstrmNm,OpnPric,HghPric,LwPric,ClsPric,LastPric,PrvsClsgPric,UndrlygPric,SttlmPric,OpnIntrst,ChngInOpnIntrst,TtlTradgVol,TtlTrfVal,TtlNbOfTxsExctd,SsnId,NewBrdLotQty,Rmks,Rsvd1,Rsvd2,Rsvd3,Rsvd4
2024-07-10,2024-07-10,FO,NSE,IDF,118791,IN0000000000,NIFTY,XX,2024-07-25,,0.0,XX,NIFTY FUT,24400.0,24500.0,24350.0,24450.0,24455.0,24380.0,24420.0,24450.0,15000000,250000,120000,1467000000,45000,1,25,,,
"""


def test_derivatives_assessment_structure():
    assessment = get_derivatives_assessment()
    assert assessment.provider == "nse_derivatives"
    assert assessment.open_interest_present is True
    assert assessment.implied_volatility_present is False
    assert assessment.licensing_status == "HUMAN REVIEW REQUIRED"
    assert len(assessment.instruments_covered) >= 4


def test_inspect_legacy_fo_fields():
    df = parse_fo_legacy_csv(SAMPLE_LEGACY_FO_CSV)
    result = inspect_fo_fields(df, is_udiff=False)
    assert result["has_open_interest"] is True
    assert result["has_change_in_oi"] is True
    assert result["has_implied_volatility"] is False
    assert result["total_contracts"] == 2


def test_inspect_udiff_fo_fields():
    df = parse_fo_udiff_csv(SAMPLE_UDIFF_FO_CSV)
    result = inspect_fo_fields(df, is_udiff=True)
    assert result["has_open_interest"] is True
    assert result["has_change_in_oi"] is True
    assert result["has_implied_volatility"] is False
    assert result["total_contracts"] == 1
