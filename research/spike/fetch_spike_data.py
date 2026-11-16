"""Data fetcher orchestrator for VESPER Phase 00 Data Provider Spike.

Fetches data for the Phase 00 universe (2015-01-01 to present):
- Yahoo Finance complete history (raw and adjusted) for 8 instruments
- NSE Equity Bhavcopy and Index Bhavcopy for key sample sessions and corporate action windows
Saves all raw files unchanged under data/raw/spike/<provider>/<YYYYMMDD>/,
appends rows to manifest, and exports normalized data for validation and analysis.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from research.spike.common import (
    DEFAULT_MANIFEST_PATH,
    DEFAULT_RAW_DIR,
    format_partition_date,
    save_raw_file,
)
from research.spike.probe_nse import (
    TARGET_EQUITY_UNIVERSE,
    TARGET_INDEX_UNIVERSE,
    fetch_nse_equity_session,
    fetch_nse_index_session,
)
from research.spike.probe_yahoo import (
    YAHOO_TICKER_MAP,
    fetch_all_yahoo_universe,
    fetch_yahoo_symbol,
)

# Key corporate action inspection dates and benchmark dates for NSE comparison
SAMPLE_NSE_SESSIONS: list[datetime.date] = [
    # 1. Reliance Bonus 1:1 around Sep 2017 (Ex-Date: 2017-09-07)
    datetime.date(2017, 9, 5),
    datetime.date(2017, 9, 6),
    datetime.date(2017, 9, 7),
    datetime.date(2017, 9, 8),
    datetime.date(2017, 9, 11),
    # 2. TCS Bonus 1:1 around May/Jun 2018 (Ex-Date: 2018-05-31)
    datetime.date(2018, 5, 29),
    datetime.date(2018, 5, 30),
    datetime.date(2018, 5, 31),
    datetime.date(2018, 6, 1),
    # 3. Infosys Bonus 1:1 around Sep 2018 (Ex-Date: 2018-09-04)
    datetime.date(2018, 9, 3),
    datetime.date(2018, 9, 4),
    datetime.date(2018, 9, 5),
    # 4. HDFC Bank Split 2:1 around Sep 2019 (Ex-Date: 2019-09-19)
    datetime.date(2019, 9, 17),
    datetime.date(2019, 9, 18),
    datetime.date(2019, 9, 19),
    datetime.date(2019, 9, 20),
    # 5. HDFC Bank / HDFC Merger around Jul 2023 (Ex-Date: 2023-07-13)
    datetime.date(2023, 7, 11),
    datetime.date(2023, 7, 12),
    datetime.date(2023, 7, 13),
    datetime.date(2023, 7, 14),
    # 6. Legacy vs UDiFF transition benchmarks
    datetime.date(2024, 1, 1),   # Early 2024 legacy format
    datetime.date(2024, 7, 5),   # Final legacy format session
    datetime.date(2024, 7, 8),   # UDiFF launch session
    datetime.date(2024, 7, 10),  # UDiFF session
]


def run_data_fetch(
    raw_dir: Path = DEFAULT_RAW_DIR,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    fetch_yahoo: bool = True,
    fetch_nse: bool = True,
) -> dict[str, Any]:
    """Execute spike data collection for Yahoo Finance and NSE."""
    results: dict[str, Any] = {}

    # 1. Fetch Yahoo Finance
    if fetch_yahoo:
        print("[1/2] Fetching Yahoo Finance data for universe (2015-01-01 to present)...")
        yahoo_raw_df, yahoo_adj_df, yahoo_errors = fetch_all_yahoo_universe(
            start_date="2015-01-01",
            raw_dir=raw_dir,
            manifest_path=manifest_path,
        )
        print(f"Yahoo fetch complete: {len(yahoo_raw_df)} raw rows, {len(yahoo_adj_df)} adjusted rows.")
        results["yahoo_raw"] = yahoo_raw_df
        results["yahoo_adjusted"] = yahoo_adj_df
        results["yahoo_errors"] = yahoo_errors

    # 2. Fetch NSE Sample Sessions
    if fetch_nse:
        print(f"[2/2] Fetching NSE bhavcopy & index samples across {len(SAMPLE_NSE_SESSIONS)} sessions...")
        nse_equity_dfs = []
        nse_index_dfs = []
        nse_errors = []

        for sdate in SAMPLE_NSE_SESSIONS:
            print(f"  Fetching NSE equity & index for session {sdate}...")
            eq_df, eq_err = fetch_nse_equity_session(
                session_date=sdate,
                symbols=TARGET_EQUITY_UNIVERSE,
                raw_dir=raw_dir,
                manifest_path=manifest_path,
            )
            if eq_df is not None:
                nse_equity_dfs.append(eq_df)
            elif eq_err:
                nse_errors.append({"date": str(sdate), "type": "equity", "error": eq_err})

            idx_df, idx_err = fetch_nse_index_session(
                session_date=sdate,
                indices=TARGET_INDEX_UNIVERSE,
                raw_dir=raw_dir,
                manifest_path=manifest_path,
            )
            if idx_df is not None:
                nse_index_dfs.append(idx_df)
            elif idx_err:
                nse_errors.append({"date": str(sdate), "type": "index", "error": idx_err})

        all_nse_eq = pd.concat(nse_equity_dfs, ignore_index=True) if nse_equity_dfs else pd.DataFrame()
        all_nse_idx = pd.concat(nse_index_dfs, ignore_index=True) if nse_index_dfs else pd.DataFrame()
        all_nse = pd.concat([all_nse_eq, all_nse_idx], ignore_index=True) if (not all_nse_eq.empty or not all_nse_idx.empty) else pd.DataFrame()

        print(f"NSE fetch complete: {len(all_nse)} total rows ({len(all_nse_eq)} equity, {len(all_nse_idx)} index).")
        results["nse"] = all_nse
        results["nse_errors"] = nse_errors

    return results


if __name__ == "__main__":
    run_data_fetch()
