# VESPER v2.1 — Formal Research Data Request Specification

> **Submission Framework**: *Data List Under The NSE Data Sharing Policy For Research And Analysis* (Dated 28 July 2025, mandated by SEBI Circular SEBI/HO/MRD/MRD-PoD-1/P/CIR/2024/178 dated December 20, 2024)  
> **Project Title**: VESPER v2.1 (Quantitative Research in Indian Equities Market Microstructure, Factor Regimes & Derivatives Pricing)  
> **Target Universe**: Eight-Instrument Benchmark Cohort (`NIFTY 50`, `NIFTY BANK`, `RELIANCE`, `HDFCBANK`, `TCS`, `INFY`, `ICICIBANK`, `SBIN`)  
> **Historical Horizon**: 2015-01-01 to Present (~11.8 Years / 2,931 Trading Sessions)  
> **Governance Status**: **NSE TECHNICALLY APPROVED AS PRIMARY PROVIDER; FORMAL LEGAL ACCESS AUTHORIZATION & AUTOMATED INGESTION PERMISSION PENDING**

---

## 1. Executive Summary & Research Context

VESPER v2.1 is a rigorous, non-commercial quantitative finance research initiative investigating:
1. **Asset Pricing & Factor Regimes**: Long-term risk premia, momentum persistence, and volatility clustering in large-cap Indian equities.
2. **Corporate Action Price Formation**: The structural mechanics of stock splits, bonus share issuance, and corporate restructuring on liquidity and price discovery.
3. **Derivatives Market Quality & Volatility Skew**: Empirical modeling of implied volatility surfaces, option skew dynamics, and open interest concentration in Nifty index and single-stock options.
4. **Market Microstructure & Order Flow**: High-resolution study of effective spreads, trade size distribution, and institutional flow interactions.

To ensure pristine empirical provenance and eliminate the systematic distortion identified in third-party retail aggregators (e.g., Yahoo Finance's retroactive split adjustments and dropped holiday sessions), VESPER v2.1 formally applies under the **SEBI-mandated NSE Data Sharing Policy For Research And Analysis** (dated 28 July 2025).

---

## 2. Regulatory Alignment with SEBI / NSE Two-Basket Architecture

In strict compliance with the **NSE Data Sharing Policy For Research And Analysis** (28 July 2025), all data requested herein is drawn exclusively from the **First Basket (‘Data available for research’)**. Zero data is requested from the **Second Basket (‘Restricted Data’)**:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               NSE REGULATORY BASKET COMPLIANCE                                  │
├────────────────────────────────────────────────────────────────┬────────────────────────────────┤
│       FIRST BASKET: ELIGIBLE RESEARCH DATA REQUESTED           │ SECOND BASKET: RESTRICTED DATA │
│                   (Approved for Ingestion)                     │     (Strictly Excluded)        │
├────────────────────────────────────────────────────────────────┼────────────────────────────────┤
│ • Sub-Tier A (Freely Available on Exchange Website):           │ ✗ PAN-wise Trade Records       │
│   - Capital Market EOD Historical Bhavcopy (CM Series EQ)      │ ✗ Personal Identifiable Data   │
│   - Daily Historical Index Data (Nifty 50, Nifty Bank)         │ ✗ UCC / KYC Records            │
│   - Corporate Actions, Announcements & Financial Filings       │ ✗ Client Position Data w/ IDs  │
│   - Historical Bulk & Block Deals Archives                     │ ✗ TBT with Member/Client IDs   │
│   - FII / FPI & DII Daily Historical Trading Activity          │ ✗ Polling Participant Names    │
│   - Exchange Surveillance Actions (ASM / GSM / ESM)            │                                │
│                                                                │                                │
│ • Sub-Tier B (Voluminous Data; >2GB; Chargeable At Cost):      │                                │
│   - Multi-Year Bulk End of Day Data Archives (CM & F&O)        │                                │
│   - Historical Securities & Contracts Master (Lot sizes)       │                                │
│   - Historical Tick-by-Tick Orders & Trades (>6 Months Old,   │                                │
│     anonymized without member/client identifiers)              │                                │
└────────────────────────────────────────────────────────────────┴────────────────────────────────┘
```

---

## 3. Mapping Requested Datasets to VESPER Architecture Modules

Every requested dataset maps directly into one of the six core architectural components of **VESPER v2.1**:

```
                               ┌────────────────────────────────────────────────────────┐
                               │               VESPER v2.1 ARCHITECTURE                 │
                               └────────────────────────────────────────────────────────┘
                                                           │
         ┌───────────────────┬───────────────────┬─────────┴─────────┬───────────────────┬───────────────────┐
         ▼                   ▼                   ▼                   ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ VESPER Forecast │ │ VESPER Capital  │ │  VESPER Quant   │ │  VESPER Shield  │ │  VESPER Radar   │ │  VESPER Pulse   │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤ ├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ • CM EOD OHLCV  │ │ • Market Cap    │ │ • F&O Bhavcopy  │ │ • Surveillance  │ │ • FII/DII Daily │ │ • Anonymized    │
│ • Index Daily   │ │ • Demat Turnover│ │ • Open Interest │ │   Actions (ASM) │ │   Net Flows     │ │   TBT (>6mo)    │
│ • Corporate     │ │ • MFSS Mutual   │ │ • Contracts     │ │ • Margin Files  │ │ • Bulk & Block  │ │ • Trade Size    │
│   Actions (Adj) │ │   Fund Flows    │ │   Master Data   │ │ • Call Auction  │ │   Deals         │ │   Distribution  │
│ • Return Series │ │ • Mode Share    │ │ • Option Settle │ │ • Defaulter     │ │ • Category-Wise │ │ • Trading Mode  │
│   Calculations  │ │   Statistics    │ │   Prices (BSM)  │ │   Rosters       │ │   Open Interest │ │   Breakdowns    │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Detailed Functional Mapping
1. **VESPER Forecast** (Alpha Factors & Directional Prediction):
   - *Datasets*: Section 2.1(ii) Security-wise OHLC, Section 2.1(iii) CM Bhavcopy, Section 2.1(iv) Historical Index Data, Section 3(xii) Corporate Actions.
   - *Application*: Unadjusted price series formation, split/bonus ratio adjustments, momentum/mean-reversion features.
2. **VESPER Capital** (Portfolio Allocation & Sizing):
   - *Datasets*: Section 1(vii) Market Capitalisation, Section 1(ii) Demat Turnover, Section 2.1(v) MFSS Mutual Fund Subscription/Redemption, Section 2.1(viii) Trading Mode Shares.
   - *Application*: Liquidity-adjusted position sizing, index constituent weighting, institutional capital flow tracking.
3. **VESPER Quant** (Derivatives Pricing & Volatility Surfaces):
   - *Datasets*: Section 2.2(ii) Contract-wise price volume, Section 2.2(iii) F&O Bhavcopy & Open Interest, Voluminous Item 3 Historical Contracts Master.
   - *Application*: End-of-day Black-Scholes implied volatility solver, volatility skew modeling, term structure fitting, put-call ratio analysis.
4. **VESPER Shield** (Risk Governance & Capital Preservation):
   - *Datasets*: Section 6(i) Surveillance Measures (ASM / GSM / ESM), Section 6(iii) Margin Trading files, Section 7(iv) Periodic Call Auction Illiquid Securities, Section 7(viii) Defaulting Clients.
   - *Application*: Pre-trade execution filters, circuit breaker monitoring, automated trading bans on surveillance-flagged assets.
5. **VESPER Radar** (Institutional Footprint & Flow Surveillance):
   - *Datasets*: Section 2.1(ii) Bulk & Block Deals archives, Section 2.1(vii) FII/FPI & DII trading activity, Section 7(iii) Foreign Investment Limits in Listed Companies.
   - *Application*: Detection of institutional accumulation/distribution, smart-money flow factor creation.
6. **VESPER Pulse** (Market Microstructure & Execution Analytics):
   - *Datasets*: Voluminous Item 7 Tick-by-Tick Orders & Trades (>6 months historical, anonymized), Section 1(v) Average Trade Size, Section 2.1(viii) Colocation/Algo mode share.
   - *Application*: Order book dynamics, effective spread estimation, slippage modeling for execution optimization.

---

## 4. Prioritized Research Data Request (2015–Present Universe)

### Target Universe (8 Benchmark Instruments)
- **Benchmark Indices**: `NIFTY 50`, `NIFTY BANK`
- **Liquid Equities**: `RELIANCE`, `HDFCBANK`, `TCS`, `INFY`, `ICICIBANK`, `SBIN`

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              PRIORITIZED DATA REQUEST SPECIFICATION                                    │
├───────────┬─────────────────────────────────────────────────┬──────────────────────┬───────────────────┤
│ PRIORITY  │ DATASET DESCRIPTION                             │ REGULATORY CITATION  │ TARGET HORIZON    │
├───────────┼─────────────────────────────────────────────────┼──────────────────────┼───────────────────┤
│ **P1**    │ Capital Market EOD Bhavcopy (EQ Series)         │ First Basket 2.1(iii)│ 2015-01-01 to EOD │
│ (Critical)│ Historical Index EOD Data (Nifty 50, Bank Nifty)│ First Basket 2.1(iv) │ 2015-01-01 to EOD │
│           │ Corporate Actions (Splits, Bonuses, Mergers)    │ First Basket 3(xii)  │ 2015-01-01 to EOD │
├───────────┼─────────────────────────────────────────────────┼──────────────────────┼───────────────────┤
│ **P2**    │ Equity Derivatives (F&O) Daily Bhavcopy         │ First Basket 2.2(iii)│ 2015-01-01 to EOD │
│ (Core)    │ Contract Specifications & Securities Master     │ Voluminous Item 3    │ 2015-01-01 to EOD │
├───────────┼─────────────────────────────────────────────────┼──────────────────────┼───────────────────┤
│ **P3**    │ FII / FPI and DII Daily Historical Flows        │ First Basket 2.1(vii)│ 2015-01-01 to EOD │
│ (Signals) │ Bulk and Block Deals Historical Archives        │ First Basket 2.1(ii) │ 2015-01-01 to EOD │
│           │ Exchange Surveillance Measures (ASM/GSM lists)  │ First Basket 6(i)    │ 2015-01-01 to EOD │
├───────────┼─────────────────────────────────────────────────┼──────────────────────┼───────────────────┤
│ **P4**    │ Anonymized Tick-by-Tick Orders & Trades (TBT)   │ Voluminous Item 7    │ Selected Samples  │
│ (Micro)   │ (Strictly > 6 months old; without PII/broker IDs│ (Policy Note 3)      │ (Monthly Expiries)│
└───────────┴─────────────────────────────────────────────────┴──────────────────────┴───────────────────┘
```

---

## 5. Dataset Volume & Storage Estimation (Without Bulk Downloads)

In accordance with Phase 00 governance rules, volume estimates are derived mathematically from empirical per-session measurements without initiating unapproved bulk downloads:

### Mathematical Estimation Methodology
- Total Trading Sessions ($N$): **2,931 trading sessions** (2015-01-01 to 2026-11-16).
- Universe Size ($M$): **6 liquid equities + 2 benchmark indices**.

| Priority Tier | Dataset Component | Full Market Daily Compressed | Full Market Daily Uncompressed | 11.8-Year Full Market Raw Archive | 8-Instrument Filtered Parquet Payload |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **P1** | CM Equity Bhavcopy (Legacy + UDiFF) | ~100 KB / day | ~900 KB / day | ~293 MB (comp) / ~2.6 GB (raw) | **~5.2 MB** (2,931 rows × 6 stocks) |
| **P1** | Index Daily Files (`ind_close_all`) | ~15 KB / day | ~25 KB / day | ~44 MB (comp) / ~73 MB (raw) | **~0.2 MB** (2,931 rows × 2 indices) |
| **P1** | Corporate Actions Database | — | — | ~12 MB total | **~0.1 MB** (all events for 6 stocks) |
| **P2** | F&O Daily Bhavcopy (Futures & Options) | ~500 KB / day | ~3.5 MB / day | ~1.46 GB (comp) / ~10.2 GB (raw)| **~320 MB** (contracts for 8 underlyings) |
| **P2** | Securities / Contracts Master | — | — | ~150 MB total | **~12 MB** |
| **P3** | FII / DII Daily Flows & Bulk Deals | ~20 KB / day | ~50 KB / day | ~58 MB (comp) / ~146 MB (raw) | **~4.5 MB** |
| **P3** | Surveillance Actions (ASM/GSM) | ~10 KB / day | ~25 KB / day | ~29 MB (comp) / ~73 MB (raw) | **~1.0 MB** |
| **Subtotal** | **Core Research Ingestion (P1–P3)** | — | — | **~2.05 GB (comp) / ~13.2 GB (raw)**| **~343.2 MB (Parquet)** |
| **P4** | Anonymized TBT (Sample Expiry Cycles) | ~250 MB / day | ~1.8 GB / day | Bounded by sample request | **~15 GB** (Sample 60 trading days) |

### Key Storage Findings for Governance:
1. **Filtered Research Footprint**: The actual research footprint for the target 8-instrument universe across 11.8 years (P1 to P3) compresses into a remarkably compact **~343 MB Parquet store**.
2. **Voluminous Classification Boundary**: If full-market uncompressed EOD archives are requested in bulk, the dataset measures **~13.2 GB**, exceeding the 2 GB threshold and correctly placing it in **First Basket: Sub-Tier B (Chargeable at cost)**.
3. **Bandwidth & Compute Safeguard**: Storage and compute requirements are minimal and fully manageable on standard local NVMe infrastructure without requiring distributed cloud storage.

---

## 6. Academic Research Application Protocol & Covenants

To transition from technical approval to authorized legal ingestion, the following formal application procedure is observed:

### Application Workflow
1. **Submission Authority**: Application directed to the *NSE Research & Data Sharing Committee* (`datasharing@nse.co.in` / `research@nse.co.in`).
2. **Institutional Credentials**: Verification of non-commercial academic research status, lead researcher credentials, and project charter.
3. **Legal Undertaking & Covenants**:
   - **Covenant 1 (Non-Commercial Academic Use Only)**: The data will be used solely for econometric, statistical, and quantitative modeling research within the scope of VESPER v2.1.
   - **Covenant 2 (Strict Non-Redistribution)**: Zero external publication, redistribution, sub-licensing, or public hosting of raw or normalized tick/candle data.
   - **Covenant 3 (Zero Re-Identification)**: Complete prohibition on any attempt to reverse-engineer, correlate, or de-anonymize trading entities, client codes, or member identities in tick-by-tick records.
   - **Covenant 4 (Secure Storage & Retention)**: Data persisted on encrypted local storage with strict access control logging.
4. **Data Delivery Channel**:
   - Upon committee approval and cost determination for voluminous subsets, data is delivered via secure exchange SFTP or encrypted transfer tokens.

---

## 7. Formal Governance Sign-Off & Status

| Governance Dimension | Status | Detailed Determination |
| :--- | :---: | :--- |
| **NSE Technical Provider Status** | **APPROVED** | Verified URL routing, legacy and UDiFF parsers validated, 30/30 unit tests passing, zero data corruption. |
| **SEBI / NSE Policy Basket Alignment** | **COMPLIANT** | 100% of requested series reside in First Basket; zero Second Basket restricted data requested. |
| **Legal Access Authorization** | **PENDING** | Formal research application (`docs/nse_research_data_request.md`) prepared; awaiting exchange committee review. |
| **Automated Ingestion Permission** | **PENDING** | Automated multi-year bulk ingestion remains **locked** until formal exchange sign-off. |
| **Phase Boundary Enforcement** | **LOCKED** | Phase 00 is technically complete; Phase 01 remains locked pending authorization. |
