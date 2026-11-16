# VESPER v2.1 — Phase 00: Data Provider Provenance Report

> **Investigation Status**: Phase 00 Complete — Investigation Only (Not a Product)  
> **Target Project**: VESPER v2.1 (Personal Indian-Equities Quantitative Research Project)  
> **Evaluation Window**: 2015-01-01 to Latest Available Session (2026-11-16)  
> **Target Universe**:
> - Benchmark Indices: `NIFTY 50`, `NIFTY BANK`
> - Liquid Equities: `RELIANCE`, `HDFCBANK`, `TCS`, `INFY`, `ICICIBANK`, `SBIN`

---

## 1. Executive Summary & Recommendation

Phase 00 investigated six candidate data sources for the VESPER quantitative research pipeline:
1. **NSE Official Equity Bhavcopy** (Legacy CSV & Modern UDiFF formats) & Index Historical Files
2. **Yahoo Finance** (via `yfinance`, raw and adjusted feeds)
3. **Zerodha Kite Connect API** (Documentation and architecture stub)
4. **NSE Derivatives** (F&O Bhavcopy archives: futures, options, open interest, and implied volatility assessment)
5. **Reserve Bank of India DBIE** (Sovereign yield curve, T-Bill rates, policy rates, USD/INR FX reference rates)
6. **Clearing Corporation of India Limited (CCIL) & FBIL** (Interbank MIBOR, zero-coupon yield curves, repo settlement)

### Core Findings
- **Raw Exchange Data vs Adjusted Feeds**: Official NSE Bhavcopy provides true, unadjusted point-in-time exchange settlement data (`cm...bhav.csv.zip` and `BhavCopy_NSE_CM_...csv.zip`). Conversely, Yahoo Finance's base `Close` column **is not unadjusted**; Yahoo retroactively applies all subsequent stock splits and bonus issues to its historical OHLC series while multiplying volume by the cumulative split factor.
- **Index Data Discrepancies**: Yahoo Finance drops sessions for `^NSEI` that coincide with international market holidays (e.g. January 1) or weekend evening trading (Diwali Muhurat sessions), despite full cash equity market activity occurring on the NSE.
- **Derivatives & Volatility**: Historical daily NSE F&O bhavcopies contain complete contract-level settlement prices and **Open Interest (OI)**, but **Implied Volatility (IV) is completely absent** from all daily bhavcopy archives. IV must be computed via a quantitative Black-Scholes solver using sovereign risk-free discount curves (sourced from RBI DBIE) or captured via live intraday option-chain snapshots.
- **Web WAF & Bot Mitigation**: The main NSE web portal (`www.nseindia.com/api/...`) actively blocks automated requests with HTTP 503 / Akamai WAF challenges (`<meta content="noindex, nofollow" name="robots"/>`). In contrast, NSE's official archive servers (`archives.nseindia.com` and `nsearchives.nseindia.com`) reliably serve daily bhavcopy archives with HTTP 200 without anti-bot challenges when accessed under polite rate limits (>=2.0s delay).

### Provider Recommendation (Subject to Human Review)
- **Primary Source of Truth (EOD Quantitative Research & Backtesting)**: **NSE Official Bhavcopy (UDiFF & Legacy Archives)**.
  - *Rationale*: Free of cost, 100% point-in-time unadjusted truth directly from the exchange, zero corporate action distortion, includes ISINs, official settlement prices, deliverable quantities, and true trade counts.
- **Secondary Sanity Check & Fast Feature Prototyping**: **Yahoo Finance**.
  - *Rationale*: Instant multi-year bulk download capability; highly useful for cross-validating split-adjusted price trajectories, but must never be relied upon as the sole source of historical volume or unadjusted cash prices.
- **Live Execution & Intraday Signals (Future Phases)**: **Zerodha Kite Connect API**.
  - *Rationale*: Official broker API with WebSocket tick feeds and clean intraday minute candles for ₹500/month; ideal for signal generation and trade execution, but unsuited for bulk 10-year historical backtesting due to rate limits and absence of bulk download facilities.
- **Macro & Risk-Free Curves**: **RBI DBIE** (Primary, zero cost) supplemented by **CCIL delayed benchmarks**.

---

## 2. Provider Detailed Profiles

### Provider 1: NSE Equity Bhavcopy & Index Historical Data

| Field | Specification |
| :--- | :--- |
| **Provider Name** | National Stock Exchange of India (NSE) |
| **Asset Classes** | Cash Equities (EQ Series), Exchange Traded Funds, Benchmark Indices |
| **Historical Coverage** | Continuous daily coverage from June 2000 to present (~26 years). Evaluated 2015–present. |
| **Granularity** | Daily End-of-Day (EOD) OHLCV, Total Traded Value, Total Trades, Deliverable Quantity (UDiFF). |
| **Access Method** | Direct HTTP GET to official archive endpoints: <br>• Legacy (pre-July 2024): `https://archives.nseindia.com/content/historical/EQUITIES/<YYYY>/<MMM>/cm<DD><MMM><YYYY>bhav.csv.zip`<br>• Modern UDiFF (July 2024+): `https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_<YYYYMMDD>_F_0000.csv.zip`<br>• Indices: `https://archives.nseindia.com/content/indices/ind_close_all_<DDMMYYYY>.csv` |
| **Published Cost** | Free of charge via public archive servers. |
| **Official Terms URL** | `https://www.nseindia.com/terms-of-use` |
| **Quoted Terms Clauses** | **Storage & Use**: *"The Information on the Website is provided for personal, non-commercial use and informational purposes only."*<br>**Redistribution**: *"You may not copy, reproduce, recompile, decompile, disassemble, reverse engineer, distribute, publish, display, perform, modify, upload to, create derivative works from, transmit, or in any way exploit any part of the Website..."*<br>**Commercial Use**: Commercial redistribution or algorithmic feed reselling requires an official data vendor agreement with NSE Data & Analytics Ltd (NDAL). |
| **License Status** | **HUMAN REVIEW REQUIRED** |
| **Issues Found** | 1. Format migration on July 8, 2024 from legacy CSV to Unified Distributable File Format (UDiFF), altering column names (`SYMBOL` -> `TckrSymb`, `CLOSE` -> `ClsPric`). Both parsers implemented and verified.<br>2. Interactive website API (`/api/historical/...`) returns HTTP 503 / WAF block. Direct archive links must be used.<br>3. Rate limit of >= 2.0s strictly enforced. |

---

### Provider 2: Yahoo Finance (via yfinance)

| Field | Specification |
| :--- | :--- |
| **Provider Name** | Yahoo Finance (powered by ICE Data Services / Exchange feeds) |
| **Asset Classes** | Indian Equities (`<SYMBOL>.NS`), Indices (`^NSEI`, `^NSEBANK`) |
| **Historical Coverage** | Daily OHLCV back to 1996 for Nifty 50, 2000s for equities. Evaluated 2015-01-01 to present (23,435 rows downloaded). |
| **Granularity** | Daily OHLCV, Adjusted Close, Dividends, Stock Splits. |
| **Access Method** | REST API calls via `yfinance` Python wrapper querying `https://query1.finance.yahoo.com/v8/finance/chart/`. |
| **Published Cost** | Free of charge for basic personal usage. |
| **Official Terms URL** | `https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html` and `https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html` |
| **Quoted Terms Clauses** | **Personal Use Only**: *"Yahoo grants you a personal, non-assignable, and non-exclusive license to use the software and APIs... You may not copy, modify, distribute, sell, or lease any part of our Services or included software."*<br>**Prohibited Use**: Automated mass harvesting, scraping, or commercial indexing without express enterprise contract is prohibited under Section 8 (Conduct).<br>**Exchange Redistribution**: Downstream users remain bound by third-party exchange data rights (ICE / NSE). |
| **License Status** | **HUMAN REVIEW REQUIRED** |
| **Issues Found** | 1. **Silent Retroactive Split Adjustments**: The base `Close` column is split-adjusted, meaning it does not reflect historical cash settlement prices.<br>2. **Holiday Inconsistencies**: Drops 9 sessions on `^NSEI` (including New Year's Day and Diwali Muhurat sessions).<br>3. **Null Index Volume**: Volume for `^NSEI` and `^NSEBANK` is missing/NaN.<br>4. Unofficial API subject to endpoint discontinuation or IP throttling. |

---

### Provider 3: Zerodha Kite Connect API

| Field | Specification |
| :--- | :--- |
| **Provider Name** | Zerodha Broking Limited (Kite Connect API) |
| **Asset Classes** | NSE Equities, Indices, F&O, Currency, Commodity |
| **Historical Coverage** | Daily candles ~5–7+ years; Intraday minute candles ~1–2 years. |
| **Granularity** | Minute, multi-minute, hourly, and daily candles; live tick streaming via WebSocket. |
| **Access Method** | Programmatic REST API (`api.kite.trade`) requiring `api_key` and session `access_token` obtained via OAuth login flow. |
| **Published Cost** | **Personal Tier**: ₹0/month (order execution, margins, holdings; no market data).<br>**Connect Tier**: ₹500/month per API key (includes live WebSocket streaming and historical candle data; historical add-on fee eliminated).<br>**Developer Rebate**: 500 Developer Credits (worth ₹500) credited if monthly brokerage exceeds ₹2,000, making API free for active retail traders. |
| **Official Terms URL** | `https://kite.trade/terms` and `https://kite.trade/pricing` |
| **Quoted Terms Clauses** | **Redistribution Prohibition**: *"You shall not redistribute, sub-license, rent, lease, or resell the Kite Connect API or data received through the API to any third party."*<br>**Storage Limitation**: Caching and local database persistence permitted solely for the developer's direct execution algorithms; redistribution as a commercial database is strictly forbidden.<br>**Rate Limits**: Fixed ceiling of 3 requests per second per API key. |
| **License Status** | **HUMAN REVIEW REQUIRED** |
| **Issues Found** | 1. Credentials not present in `.env` (per Phase 00 rules, execution halted; comprehensive documentation stub produced).<br>2. No bulk-dump endpoint (requires iterating token-by-token across 60-day slices).<br>3. Requires active Zerodha trading account and daily manual or headless token login. |

---

### Provider 4: NSE Derivatives (Historical F&O Bhavcopy)

| Field | Specification |
| :--- | :--- |
| **Provider Name** | NSE Derivatives Market (Futures & Options) |
| **Asset Classes** | Index Futures (`FUTIDX`), Stock Futures (`FUTSTK`), Index Options (`OPTIDX`), Stock Options (`OPTSTK`) |
| **Historical Coverage** | Daily archives from June 2000 to present. |
| **Granularity** | Daily contract-level OHLC, Settlement Price, Traded Contracts, Turnover, Open Interest (OI), and Change in OI. |
| **Access Method** | HTTP GET from archive endpoints:<br>• Legacy (pre-July 2024): `https://archives.nseindia.com/content/historical/DERIVATIVES/<YYYY>/<MMM>/fo<DD><MMM><YYYY>bhav.csv.zip`<br>• Modern UDiFF (July 2024+): `https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_<YYYYMMDD>_F_0000.csv.zip` |
| **Published Cost** | Free public daily archives. |
| **Official Terms URL** | `https://www.nseindia.com/terms-of-use` |
| **License Status** | **HUMAN REVIEW REQUIRED** |
| **Open Interest Assessment** | **PRESENT**: Recorded in every daily bhavcopy (`OPEN_INT` and `CHG_IN_OI` in legacy; `OpnIntrst` and `ChngInOpnIntrst` in UDiFF). |
| **Implied Volatility Assessment** | **ABSENT**: Implied Volatility is **not recorded** in daily historical bhavcopies. Quantitative modeling requiring IV must compute Black-Scholes implied volatilities using underlying cash settlement and risk-free curves, or capture live option chains. |

---

### Provider 5: Reserve Bank of India DBIE (Database on Indian Economy)

| Field | Specification |
| :--- | :--- |
| **Provider Name** | Reserve Bank of India (RBI Data Warehouse) |
| **Key Series Available** | Policy Rates (Repo, Reverse Repo, MSF, Bank Rate); Overnight Call Rates (WACR); Triparty Repo (TREPS); 91-Day, 182-Day, 364-Day Treasury Bill primary auction cut-off yields; 10-Year Benchmark G-Sec Yield; Official FBIL/RBI FX Reference Rates (USD/INR, EUR/INR, GBP/INR, JPY/INR). |
| **Historical Coverage** | Decades of daily and monthly historical records (1970s–present). |
| **Format** | Static CSV downloads, Excel spreadsheets (`.xls` / `.xlsx`), HTML tables. |
| **Access Method** | Public web access (`https://dbie.rbi.org.in`, `https://data.rbi.org.in`). No API key required; automated batch scripts must handle session cookies. |
| **Published Cost** | Free of charge (Sovereign Open Public Data). |
| **Official Terms URL** | `https://www.rbi.org.in/commonman/English/Scripts/Disclaimer.aspx` |
| **Quoted Terms Clauses** | Public domain sovereign statistics. Free for personal, academic, and commercial research with mandatory attribution (*"Source: Reserve Bank of India"*). RBI disclaims liability for downstream quantitative or trading decisions. |
| **License Status** | **HUMAN REVIEW REQUIRED** |
| **Issues Found** | No high-availability streaming API; portal UI undergoes periodic redesigns requiring scraper maintenance. Ideal for daily EOD macro factor ingestion. |

---

### Provider 6: Clearing Corporation of India Limited (CCIL) & FBIL

| Field | Specification |
| :--- | :--- |
| **Provider Name** | CCIL & Financial Benchmarks India Private Limited (FBIL) |
| **Key Series Available** | FBIL Overnight MIBOR, 14-Day, 1-Month, 3-Month Term MIBOR; Sovereign Zero-Coupon Yield Curve (ZCYC); NDS-OM trade-weighted G-Sec settlement yields; TREPS money market settlement data; USD/INR Forward Premia curves. |
| **Historical Coverage** | Daily market settlement benchmarks from ~2004 to present. |
| **Format** | HTML tables, daily market summary PDFs, periodic Excel file dumps. |
| **Access Method** | Web portal queries (`https://www.ccilindia.com`, `https://www.fbil.org.in`). Direct programmatic FTP/SFTP institutional feeds require formal data vendor contracts. |
| **Published Cost** | Delayed public web tables are free; automated enterprise benchmark feeds require paid subscription (annual licensing fees apply). |
| **Official Terms URL** | `https://www.ccilindia.com/Disclaimer.aspx` and FBIL Terms |
| **Quoted Terms Clauses** | Strict benchmark copyright. *"The Benchmarks and settlement statistics are the exclusive intellectual property of CCIL/FBIL. Unauthorized copying, automated scraping, redistribution, or commercial display is strictly prohibited."* |
| **License Status** | **HUMAN REVIEW REQUIRED** |
| **Issues Found** | Strict anti-scraping controls on CCIL web pages. For VESPER research, delayed web observation or RBI DBIE proxy curves are recommended to avoid commercial licensing overhead. |

---

## 3. The 10 Gate Items Assessment

| Gate Item # | Description | Status | Linked Evidence & Validation Summary |
| :---: | :--- | :---: | :--- |
| **1** | **Historical data availability verified** | **PASS** | Evaluated 2015-01-01 to present (~11.8 years). Yahoo Finance covers 2,931 sessions for equities and 2,922 sessions for indices. NSE official archives verified continuously back to June 2000 (legacy format) and July 2024+ (UDiFF format). Linked: [docs/phase00_analysis_results.md#1-instrument-coverage-analysis](file:///c:/Users/TRB/Downloads/VESPER/docs/phase00_analysis_results.md#1-instrument-coverage-analysis). |
| **2** | **Licensing and costs verified** | **HUMAN REVIEW REQUIRED** | Published pricing, official terms URLs, and quoted clauses documented for all 6 providers. Free public options identified (NSE Bhavcopy, Yahoo Finance personal, RBI DBIE). Paid tiers documented (Kite Connect ₹500/mo, FBIL enterprise). Final legal and commercial review reserved for human decision. |
| **3** | **OHLCV samples downloaded** | **PASS** | 56 raw files retrieved and saved unchanged under `data/raw/spike/<provider>/<YYYYMMDD>/`. Complete SHA-256 hashes and byte sizes recorded in `data/raw/spike/manifest.csv`. 23,435 Yahoo rows and 192 NSE ground truth rows parsed and normalized. |
| **4** | **Trading timestamps validated** | **PASS** | Session dates verified against IST exchange calendar. Zero unexpected weekend sessions (all 12 weekend dates matched official Diwali Muhurat, Budget, or DR drill sessions). Zero timezone off-by-one errors. Publication windows established and formal `available_at` rule formulated. Linked: [docs/phase00_analysis_results.md#6-publication-timestamps--proposed-available_at-rule](file:///c:/Users/TRB/Downloads/VESPER/docs/phase00_analysis_results.md#6-publication-timestamps--proposed-available_at-rule). |
| **5** | **Corporate-action handling verified** | **PASS** | Verified official NSE ex-dates and adjustment ratios for all 5 candidate events: Reliance 2017 bonus (2017-09-07, 1:1), TCS 2018 bonus (2018-05-31, 1:1), Infosys 2018 bonus (2018-09-04, 1:1), HDFC Bank 2019 split (2019-09-19, 2:1), and HDFC Bank/HDFC 2023 merger (2023-07-13). Proved Yahoo's retroactive split adjustments match announced ratios. Linked: [docs/phase00_analysis_results.md#5-corporate-actions-audit-official-ex-dates--price-adjustments](file:///c:/Users/TRB/Downloads/VESPER/docs/phase00_analysis_results.md#5-corporate-actions-audit-official-ex-dates--price-adjustments). |
| **6** | **Cross-provider discrepancies documented** | **PASS** | Cross-matched 192 NSE ground truth rows against Yahoo raw rows. Established that indices and unsplit equities match to 0.0000% difference. Documented the 65 instances where Yahoo's pre-split prices deviate by 50% to 77% due to retroactive split and demerger factoring. Linked: [docs/phase00_analysis_results.md#4-cross-provider-discrepancy-analysis-nse-vs-yahoo](file:///c:/Users/TRB/Downloads/VESPER/docs/phase00_analysis_results.md#4-cross-provider-discrepancy-analysis-nse-vs-yahoo). |
| **7** | **Missing and duplicate records identified** | **PASS** | Ran automated test suite and validator on 23,627 records: 0 duplicate `(symbol, session_date)` pairs found. Identified exactly 9 sessions present in cash equity feeds but missing in Yahoo's `^NSEI` index feed. Linked: [docs/phase00_analysis_results.md#2-sessions-vs-nse-trading-calendar](file:///c:/Users/TRB/Downloads/VESPER/docs/phase00_analysis_results.md#2-sessions-vs-nse-trading-calendar). |
| **8** | **Derivatives data availability assessed** | **PASS** | Evaluated NSE F&O daily bhavcopies (legacy and modern UDiFF). Confirmed Open Interest (`OPEN_INT`, `OpnIntrst`) and Change in OI are present. Proved Implied Volatility (IV) is completely absent from all EOD bhavcopy files, defining requirement for Black-Scholes solver. Linked: [research/spike/probe_nse_fo.py](file:///c:/Users/TRB/Downloads/VESPER/research/spike/probe_nse_fo.py). |
| **9** | **Primary provider selected** | **HUMAN REVIEW REQUIRED** | Recommended Architecture: Hybrid model with **NSE Official Bhavcopy (UDiFF)** as the Primary Point-in-Time Ground Truth for backtesting and features, **Yahoo Finance** as Secondary fast cross-validation source, and **Zerodha Kite** for future live execution. Final provider selection reserved for human approval. |
| **10** | **Provenance report completed** | **PASS** | Completed comprehensive provenance audit report (`docs/phase00_provenance_report.md`), analysis results (`docs/phase00_analysis_results.md`), 30 passing unit tests, and reproduction harness. |

---

## 4. Open Risks & Mitigation Strategies

1. **Exchange Schema Drift (NSE UDiFF Transition)**
   - *Risk*: NSE circulars periodically update UDiFF field mappings or archive file URL formats.
   - *Mitigation*: The `research/spike/probe_nse.py` module isolates schema mapping into versioned parsers (`parse_legacy_bhavcopy`, `parse_udiff_bhavcopy`). The manifest records `parser_version` for every file to ensure deterministic re-parsing.
2. **Yahoo Finance Unadjusted Price Fallacy**
   - *Risk*: A quantitative researcher might assume Yahoo Finance's `Close` column represents unadjusted exchange trading prices, corrupting historical feature calculations (e.g. historical price levels, trading bands, moving averages).
   - *Mitigation*: Documented explicitly in Gate Item 6. VESPER v2.1 must use NSE Bhavcopy as the single source of truth for unadjusted cash settlement prices.
3. **Absence of Historical Implied Volatility in EOD Archives**
   - *Risk*: Volatility-based derivative strategies cannot directly load IV from historical bhavcopies.
   - *Mitigation*: Phase 01 / Phase 02 must incorporate a fast vectorized Black-Scholes / Bivalent IV solver that computes implied volatilities on the fly using option settlement prices, underlying spot prices, and RBI T-Bill risk-free yields.
4. **IP Blocking & Rate Limiting**
   - *Risk*: Bulk scraping of thousands of bhavcopies can trigger IP bans or temporary blacklisting.
   - *Mitigation*: Mandatory `>= 2.0s` delay enforced by `RateLimiter` in `common.py`. In Phase 01, local caching in DuckDB/Parquet will prevent redundant network fetches.

---

## 5. Exact Commands to Reproduce

All investigations, data downloads, tests, and analysis reports can be deterministically reproduced from a clean environment:

```bash
# 1. Clone repository and navigate to workspace
cd c:\Users\TRB\Downloads\VESPER

# 2. Verify dependencies
pip install pandas==3.1.1 pyarrow==26.0.1 duckdb==2.0.0 requests==2.34.2 yfinance==1.8.0 pytest==9.1.1

# 3. Run the automated test suite (30 tests)
pytest -v

# 4. Run the data fetch orchestrator (respects >=2.0s rate limit, saves raw payloads, writes manifest)
python -m research.spike.fetch_spike_data

# 5. Run the quantitative analysis pipeline (generates docs/phase00_analysis_results.md)
python -m research.spike.analyze
```

---
*Phase 00 Data Provider Spike is complete. Phase 01 remains locked pending human review of Gate Items 2 and 9.*
