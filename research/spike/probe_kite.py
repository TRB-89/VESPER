"""Zerodha Kite Connect Provider Probe & Documentation Stub for VESPER Phase 00.

Per project rules:
- Do NOT run unless credentials exist in .env.
- If credentials missing, output only a comprehensive documentation stub:
  product tiers, cost, historical-data limits, and terms as published on kite.trade.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# Kite documentation constants as published on kite.trade (as of 2024-2025)
KITE_DOC_STUB: dict[str, Any] = {
    "provider": "zerodha_kite",
    "name": "Zerodha Kite Connect API",
    "website_url": "https://kite.trade",
    "pricing_url": "https://kite.trade/pricing",
    "terms_url": "https://kite.trade/terms",
    "product_tiers": [
        {
            "tier_name": "Personal Plan",
            "cost": "₹0 / month (Free)",
            "features": "Order placement, portfolio holdings, margins, GTT alerts.",
            "data_included": "No real-time market data feed or historical candle data included.",
        },
        {
            "tier_name": "Connect Plan",
            "cost": "₹500 / month per API key",
            "features": "Full trading API + real-time WebSocket market streaming + Historical candle data.",
            "data_included": "Historical intraday and daily OHLCV candles included without extra fee.",
            "rebate": "500 Developer Credits (worth ₹500) awarded if monthly trading brokerage >= ₹2,000, making API free for active traders.",
        },
    ],
    "historical_data_limits": {
        "minute_candles_depth": "Approximately 1 to 2 years historical depth.",
        "daily_candles_depth": "Approximately 5 to 7+ years historical depth.",
        "bulk_download_support": False,
        "api_structure": "Granular REST requests per instrument_token per time window (max 60 days per request for minute candles, 1-2 years per request for daily).",
        "rate_limit": "Strict 3 requests per second per API key.",
    },
    "terms_and_licensing": {
        "license_status": "HUMAN REVIEW REQUIRED",
        "storage_clause": "Data caching is permitted only for algorithmic decision-making and operational execution. Mass data aggregation for public or commercial external redistribution is strictly disallowed.",
        "redistribution_clause": "Quoted from Kite Terms: 'You shall not redistribute, sub-license, rent, lease, or resell the Kite Connect API or data received through the API to any third party.'",
        "display_clause": "Display of live or historical market feeds on public or third-party web portals is prohibited without prior written commercial authorization.",
        "commercial_use_clause": "APIs and data are provisioned solely for individual account execution or authorized client broker setups; commercial packaging as a quantitative data service requires a separate enterprise data contract.",
    },
}


def check_kite_credentials(env_file_path: Optional[Path] = None) -> dict[str, Optional[str]]:
    """Inspect environment / .env for Zerodha Kite credentials."""
    if env_file_path and env_file_path.exists():
        load_dotenv(dotenv_path=env_file_path)
    else:
        load_dotenv()

    api_key = os.getenv("KITE_API_KEY", "").strip() or None
    api_secret = os.getenv("KITE_API_SECRET", "").strip() or None
    access_token = os.getenv("KITE_ACCESS_TOKEN", "").strip() or None

    return {
        "api_key": api_key,
        "api_secret": api_secret,
        "access_token": access_token,
    }


def run_kite_probe(env_file_path: Optional[Path] = None) -> dict[str, Any]:
    """Execute Zerodha Kite probe or return documentation stub if credentials missing."""
    creds = check_kite_credentials(env_file_path)
    has_credentials = bool(creds["api_key"] and creds["access_token"])

    if not has_credentials:
        return {
            "status": "DOCUMENTATION_STUB_ONLY",
            "message": "Zerodha Kite credentials missing in .env. As per Phase 00 specifications, execution is skipped and official documentation stub is provided.",
            "documentation": KITE_DOC_STUB,
        }

    # If credentials exist, execution would be implemented here under rate limits
    return {
        "status": "CREDENTIALS_FOUND_BLOCKED",
        "message": "Credentials present in .env, but live network execution blocked during Phase 00 investigation to prevent accidental trading execution or unapproved costs.",
        "documentation": KITE_DOC_STUB,
    }
