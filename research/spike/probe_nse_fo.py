"""NSE F&O (Futures & Options) Data Probe and Assessment for VESPER Phase 00.

Evaluates historical F&O bhavcopy availability, depth, and whether open interest (OI)
and implied volatility (IV) inputs are present in legacy and modern UDiFF formats.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import datetime
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import zipfile

import pandas as pd
import requests

from research.spike.common import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_RAW_DIR,
    GLOBAL_RATE_LIMITER,
    save_raw_file,
)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass(frozen=True)
class DerivativesAssessment:
    """Findings from the NSE F&O data assessment."""
    provider: str
    legacy_format_url_pattern: str
    udiff_format_url_pattern: str
    history_available_from: str
    depth_summary: str
    instruments_covered: list[str]
    open_interest_present: bool
    open_interest_fields: list[str]
    implied_volatility_present: bool
    implied_volatility_notes: str
    underlying_price_present: bool
    settlement_price_present: bool
    licensing_terms_url: str
    licensing_status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_derivatives_assessment() -> DerivativesAssessment:
    """Return the structured assessment of NSE F&O historical data."""
    return DerivativesAssessment(
        provider="nse_derivatives",
        legacy_format_url_pattern="https://archives.nseindia.com/content/historical/DERIVATIVES/<YYYY>/<MMM>/fo<DD><MMM><YYYY>bhav.csv.zip",
        udiff_format_url_pattern="https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_<YYYYMMDD>_F_0000.csv.zip",
        history_available_from="2000-06-12 (Index Futures launch) / continuous daily archives from 2015-present",
        depth_summary="All active derivative contracts for each session: 3 monthly expiries for futures (near, next, far); weekly & monthly expiries for index options; monthly expiries for stock options; complete strike ladder across CE and PE.",
        instruments_covered=[
            "FUTIDX (Index Futures: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY)",
            "OPTIDX (Index Options: Calls & Puts across all listed strike prices)",
            "FUTSTK (Single Stock Futures for permitted F&O securities)",
            "OPTSTK (Single Stock Options for permitted F&O securities)",
        ],
        open_interest_present=True,
        open_interest_fields=[
            "Legacy: OPEN_INT, CHG_IN_OI",
            "UDiFF: OpnIntrst, ChngInOpnIntrst",
        ],
        implied_volatility_present=False,
        implied_volatility_notes=(
            "Implied Volatility (IV) is NOT published in either legacy or UDiFF daily bhavcopy files. "
            "To incorporate IV into quantitative models, IV must be computed post-hoc via Black-Scholes / "
            "binomial models using option close/settle price, underlying price, and risk-free rates (e.g. from RBI/CCIL), "
            "or acquired via intraday option-chain snapshots."
        ),
        underlying_price_present=True,  # In UDiFF as UnderlyingPric; in legacy inferred from cash CM close
        settlement_price_present=True,   # SETTLE_PR in legacy, SttlmPric in UDiFF
        licensing_terms_url="https://www.nseindia.com/terms-of-use",
        licensing_status="HUMAN REVIEW REQUIRED",
    )


def parse_fo_legacy_csv(csv_text: str) -> pd.DataFrame:
    """Parse legacy NSE F&O bhavcopy CSV."""
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip().upper() for c in df.columns]
    return df


def parse_fo_udiff_csv(csv_text: str) -> pd.DataFrame:
    """Parse modern UDiFF NSE FO bhavcopy CSV."""
    df = pd.read_csv(io.StringIO(csv_text))
    df.columns = [c.strip() for c in df.columns]
    return df


def inspect_fo_fields(df: pd.DataFrame, is_udiff: bool = False) -> dict[str, Any]:
    """Inspect whether open interest and implied volatility fields exist in the DataFrame."""
    cols = [c.lower() for c in df.columns]
    has_oi = any("open_int" in c or "opnintrst" in c for c in cols)
    has_chg_oi = any("chg_in_oi" in c or "chnginopnintrst" in c for c in cols)
    has_iv = any("iv" in c or "implied" in c or "volatilit" in c for c in cols)

    return {
        "has_open_interest": has_oi,
        "has_change_in_oi": has_chg_oi,
        "has_implied_volatility": has_iv,
        "total_contracts": len(df),
        "columns_sample": list(df.columns)[:15],
    }
