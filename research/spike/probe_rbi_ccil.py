"""RBI DBIE and CCIL Data Availability Assessment for VESPER Phase 00.

Per project rules:
- Availability assessment only (what series exist, format, history, access method, terms).
- No bulk download.
- Terms recorded with official URLs, quoted clauses, and marked HUMAN REVIEW REQUIRED.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, List


@dataclass(frozen=True)
class MacroProviderAssessment:
    """Findings for macro & fixed-income data providers (RBI DBIE, CCIL)."""
    provider_id: str
    organization_name: str
    portal_urls: list[str]
    terms_url: str
    license_status: str
    cost: str
    series_available: list[dict[str, str]]
    formats_available: list[str]
    historical_depth: str
    access_methods: list[str]
    storage_terms: str
    redistribution_terms: str
    commercial_terms: str
    suitability_for_vesper: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_rbi_dbie_assessment() -> MacroProviderAssessment:
    """Structured assessment of Reserve Bank of India DBIE portal."""
    return MacroProviderAssessment(
        provider_id="rbi_dbie",
        organization_name="Reserve Bank of India (Database on Indian Economy / RBI Data Warehouse)",
        portal_urls=[
            "https://dbie.rbi.org.in",
            "https://data.rbi.org.in",
            "https://www.rbi.org.in",
        ],
        terms_url="https://www.rbi.org.in/commonman/English/Scripts/Disclaimer.aspx",
        license_status="HUMAN REVIEW REQUIRED",
        cost="Free (Public Sovereign Data)",
        series_available=[
            {
                "series_name": "Policy Rates",
                "details": "Repo Rate, Reverse Repo Rate, Marginal Standing Facility (MSF), Bank Rate",
            },
            {
                "series_name": "Money Market Rates",
                "details": "Weighted Average Call Rate (WACR), Triparty Repo (TREPS) rate, Market Repo rate",
            },
            {
                "series_name": "Sovereign Yields",
                "details": "91-Day, 182-Day, 364-Day Treasury Bill primary auction cut-off yields; 10-year G-Sec benchmark yields",
            },
            {
                "series_name": "Foreign Exchange Reference Rates",
                "details": "Daily FBIL/RBI reference rates for USD/INR, EUR/INR, GBP/INR, JPY/INR",
            },
        ],
        formats_available=["CSV", "XLS / XLSX", "HTML data tables"],
        historical_depth="Extensive historical depth (1970s-present for macro series, 1990s-present for daily interest rates/T-Bills).",
        access_methods=[
            "Manual web query and file download",
            "Direct report export to CSV/XLS",
            "No public REST API with formal API keys; automated requests require custom HTTP scrapers vulnerable to portal structure changes",
        ],
        storage_terms="Permitted for academic, personal, and internal operational data stores.",
        redistribution_terms="Public domain government data; redistribution allowed with clear citation: 'Source: Reserve Bank of India'.",
        commercial_terms="Permitted for analysis and commercial algorithms provided RBI is disclaimed from liability.",
        suitability_for_vesper="High value for risk-free discount rate curve, T-Bill rates, and macro factor regime modeling. Daily ingestion batch pipeline recommended in Phase 01.",
    )


def get_ccil_assessment() -> MacroProviderAssessment:
    """Structured assessment of Clearing Corporation of India Limited (CCIL)."""
    return MacroProviderAssessment(
        provider_id="ccil_fbil",
        organization_name="Clearing Corporation of India Limited (CCIL) & Financial Benchmarks India Pvt Ltd (FBIL)",
        portal_urls=[
            "https://www.ccilindia.com",
            "https://www.fbil.org.in",
        ],
        terms_url="https://www.ccilindia.com/Disclaimer.aspx",
        license_status="HUMAN REVIEW REQUIRED",
        cost="Delayed web summaries free; programmatic / institutional raw feeds require paid annual subscription license.",
        series_available=[
            {
                "series_name": "Interbank Benchmarks (FBIL)",
                "details": "Overnight MIBOR, 14-day, 1-month, 3-month Term MIBOR",
            },
            {
                "series_name": "Government Securities Settlement",
                "details": "Daily NDS-OM trade-weighted G-Sec yields, Sovereign Zero Coupon Yield Curve (ZCYC), Sovereign Bond Index",
            },
            {
                "series_name": "Money Market Settlement",
                "details": "TREPS volume, trades, and weighted average repo rate settlement data",
            },
            {
                "series_name": "Derivatives & Forex Settlement",
                "details": "USD/INR Forward Premia curves, Overnight Indexed Swap (OIS) / MIFOR swap curves",
            },
        ],
        formats_available=["HTML web tables", "Daily PDF market summaries", "Periodic Excel downloads"],
        historical_depth="Daily settlement data from ~2004 to present.",
        access_methods=[
            "Manual web portal inspection",
            "Web scraping (active anti-scraping and CAPTCHA present on some sub-pages)",
            "Direct institutional SFTP/API feeds (requires formal FBIL contract)",
        ],
        storage_terms="End-of-day caching permitted for personal internal research; mass persistent external archiving requires commercial agreement.",
        redistribution_terms="Strictly prohibited. Benchmarks (MIBOR, ZCYC) are proprietary assets of FBIL/CCIL. Cannot be redistributed or displayed publicly.",
        commercial_terms="Commercial usage in financial products or trading benchmarks requires a formal FBIL Data Vendor License.",
        suitability_for_vesper="Essential institutional benchmark for zero-coupon sovereign yield curve and MIBOR. In Phase 00, validated as available; in Phase 01, public delayed tables or RBI DBIE proxies can be used for zero cost.",
    )
