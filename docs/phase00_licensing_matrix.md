# VESPER v2.1 — Phase 00: Provider Licensing & Data Governance Matrix

> **Author**: Senior Quantitative Researcher, Financial Data Engineer & Data Governance Specialist  
> **Project**: VESPER v2.1 (Personal Indian-Equities Quantitative Research Project)  
> **Phase**: Phase 00 (Data Provider Spike Closure & Policy Integration)  
> **Governance Directive**: Distinguish verified legal permissions from operational accessibility. **Public accessibility does not constitute unrestricted licensing permission.**

---

## 1. Overview & Regulatory Framework

In quantitative finance and algorithmic research, data provenance, regulatory compliance, and licensing governance are as foundational as mathematical alpha. A data source that is technically accessible via an open HTTP endpoint or unofficial API may still carry strict contractual, regulatory, or intellectual property restrictions that prohibit automated harvesting, long-term persistence, commercialization, or redistribution.

### Official Regulatory Mandate
On **December 20, 2024**, the Securities and Exchange Board of India (**SEBI**) issued its statutory circular on the *"Policy for sharing data for the purposes of research/analysis"*. In compliance with this directive, the National Stock Exchange of India released its official regulatory framework:
- **Title**: *Data List Under The NSE Data Sharing Policy For Research And Analysis*
- **Date**: **28 July 2025**
- **Regulatory Authority**: SEBI Circular dated December 20, 2024
- **Objective**: Establish non-commercial academic research data sharing mechanisms across Indian exchanges, categorizing exchange-held data into standardized regulatory "baskets".

This document records the official terms of service, published pricing, automated access restrictions, storage rights, redistribution rights, and formal governance classifications for all candidate providers evaluated in Phase 00, incorporating the official July 28, 2025 NSE Research Policy.

---

## 2. Comprehensive Provider Licensing Matrix

| Provider | Published Cost | Official Terms URL | Automated Access Policy | Storage / Caching Rights | Redistribution & Commercial Rights | Governance & Technical Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NSE Official Bhavcopy & Historical Archives** | • **Free Allowance**: Public archive files & web reports.<br>• **Voluminous (>2GB)**: Available at cost for academic research under July 2025 Policy.<br>• **Commercial**: Paid enterprise data vendor feed. | [NSE Terms of Use](https://www.nseindia.com/terms-of-use) and [NSE Data Sharing Policy (28 July 2025)](https://www.nseindia.com/all-reports) | **Archive servers** (`archives.nseindia.com`, `nsearchives.nseindia.com`): Accessible via HTTP GET without WAF challenges when adhering to polite rate limits (>=2.0s delay).<br>**Website API** (`www.nseindia.com/api`): Strictly protected by Akamai WAF / HTTP 503 bot detection (`robots: noindex, nofollow`). | Permitted for private, internal, non-commercial analytical caching. Mass persistent external distribution is unauthorized. | **Strictly Prohibited without Data Vendor License or Research Agreement**. Section: *"The Information on the Website is provided for personal, non-commercial use and informational purposes only... You may not copy, reproduce, recompile, decompile, disassemble, reverse engineer, distribute, publish, display, perform, modify, upload to, create derivative works from, transmit, or in any way exploit any part of the Website..."* Commercial indexing requires formal agreement with NSE Data & Analytics Ltd (NDAL). | **TECHNICALLY APPROVED PRIMARY PROVIDER**<br>*(Access authorization & automated bulk ingestion permission: **PENDING FORMAL NSE RESEARCH APPROVAL**)* |
| **Yahoo Finance (via yfinance)** | Free (Retail tier) | [Yahoo Terms of Service](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) and [Developer APIs Terms](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html) | No official public API key. Accessible via unofficial REST endpoints subject to rate throttling and IP blacklisting. `robots.txt` disallows internal API paths (`/_td_api`, `/caas/`, etc.). | Short-term client caching permitted for personal evaluation. Persistent multi-user archiving prohibited. | **Strictly Prohibited**. Data is licensed by Yahoo from third-party exchanges (ICE Data Services, NSE). Personal, non-commercial use only. Automated mass scraping and commercial redistribution violate Section 8 (Member Conduct). | **SECONDARY CROSS-VALIDATION ONLY**<br>*(Permitted for personal research sanity checks; secondary status)* |
| **Zerodha Kite Connect API** | • **Personal**: ₹0/mo (no market data)<br>• **Connect**: ₹500/mo per API key (includes live ticks & historical candles)<br>• **Rebate**: ₹500 developer credit if monthly brokerage >= ₹2,000 | [Kite Terms](https://kite.trade/terms) and [Kite Pricing](https://kite.trade/pricing) | Formal REST API and WebSocket feed. Enforces strict rate limits: max 3 requests/sec per API key. Requires daily OAuth access token. | Caching permitted strictly for execution algorithms and portfolio analysis of the authenticated account. | **Strictly Prohibited**. Section 4: *"You shall not redistribute, sub-license, rent, lease, or resell the Kite Connect API or data received through the API to any third party."* API is strictly for individual personal algorithmic trading or approved institutional broker clients. | **FUTURE OPTIONAL LIVE EXECUTION**<br>*(Credentials excluded in Phase 00; unsuited for bulk 10-year backtests)* |
| **NSE Derivatives (F&O Bhavcopy)** | Free public archives; Voluminous historical packages available under Research Policy. | [NSE Terms of Use](https://www.nseindia.com/terms-of-use) | Same as cash equity archive servers (`archives.nseindia.com`, `nsearchives.nseindia.com`). Continuous historical daily zip archives. | Permitted for personal internal research and backtesting. | Same as NSE Cash: Redistribution, public display, or commercial product packaging requires NDAL enterprise license. | **TECHNICALLY APPROVED (DERIVATIVES)**<br>*(Open Interest present; Implied Volatility absent, requires BSM engine)* |
| **Reserve Bank of India (RBI DBIE)** | Free (Public Sovereign Data) | [RBI Disclaimer & Rights](https://www.rbi.org.in/commonman/English/Scripts/Disclaimer.aspx) | Public web portal and direct CSV/XLS downloads. No API key required. No aggressive anti-bot challenge on public report URLs. | **Permitted**. Macroeconomic and sovereign interest rate data may be stored in local databases and persistent quantitative stores. | **Permitted with Attribution**. Public sovereign data. Permitted for analytical models and commercial research provided clear attribution is maintained: *"Source: Reserve Bank of India"*. RBI disclaims liability for financial decisions. | **VERIFIED PERMISSION (MACRO & RATES)**<br>*(Primary risk-free discount curves & macro factors)* |
| **CCIL & Financial Benchmarks India (FBIL)** | • Delayed web tables: Free<br>• Automated proprietary feed: Paid institutional subscription | [CCIL Disclaimer](https://www.ccilindia.com/Disclaimer.aspx) and [FBIL Terms](https://www.fbil.org.in) | Public portal web tables; automated scraping is discouraged and blocked by intermittent CAPTCHA. Direct FTP/API feeds require paid enterprise contract. | Delayed web data may be cached for internal personal study. Persistent benchmark feeds require contract. | **Strictly Prohibited without FBIL Data Vendor License**. MIBOR, Term MIBOR, ZCYC, and sovereign trade indices are proprietary benchmarks of FBIL/CCIL. Cannot be redistributed, republished, or packaged into commercial index products. | **FIXED-INCOME RESEARCH (SUBJECT TO FUTURE VERIFICATION)**<br>*(Delayed web viewing only; bulk ingestion deferred)* |

---

## 3. Official NSE Research Policy Dataset Classifications

Under the **NSE Data Sharing Policy For Research And Analysis** (dated 28 July 2025, pursuant to SEBI Circular Dec 20, 2024), exchange data is formally partitioned into two regulatory baskets:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│            SEBI / NSE DATA SHARING REGULATORY BASKETS (28 JULY 2025 POLICY)            │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
        ┌───────────────────────────────────┴───────────────────────────────────┐
        ▼                                                                       ▼
┌───────────────────────────────────────────────┐       ┌───────────────────────────────────────────────┐
│        FIRST BASKET: RESEARCH DATA            │       │       SECOND BASKET: RESTRICTED DATA          │
│          (Eligible for Research)              │       │          (Permanently Barred)                 │
├───────────────────────────────────────────────┤       ├───────────────────────────────────────────────┤
│ • Sub-Tier A: Freely Available Web Data       │       │ • PAN-wise Trade Records                      │
│   (Turnover, EOD Bhavcopy, Index history,     │       │ • Personal Identifiable Information (PII)     │
│    Corporate Filings, Surveillance lists)     │       │ • Unique Client Code (UCC) & KYC data         │
│ • Sub-Tier B: Voluminous Data (>2GB; At Cost) │       │ • Client-wise Position data with IDs          │
│   (Bulk multi-year EOD, Historical Master,    │       │ • Tick-by-Tick with broker/client identity    │
│    TBT orders/trades >6mo without PII)        │       │ • Polling participant/approved hedger names   │
└───────────────────────────────────────────────┘       └───────────────────────────────────────────────┘
```

### Detailed Basket Breakdown

#### First Basket: Sub-Tier A (Freely Available Research Data)
Minimum baseline data accessible via the exchange public website without subscription fees:
1. **Business Growth Data**: Daily, monthly, and annual statistics for turnover, demat securities traded, trade counts, securities traded, average trade size, market capitalization across cash, derivatives, and debt.
2. **Capital Markets Historical Reports**:
   - Securities available for trading
   - Daily historical bulk/block deals, security-wise OHLC, turnover
   - Daily/monthly report archives (Bhavcopy, market activity report, mode of trading, category flows, internet trading)
   - Historical index data (`niftyindices.com`)
   - MFSS trade statistics (mutual fund subscription/redemption)
   - FII/FPI and DII daily trading activity
3. **Equity Derivatives Reports**:
   - Contracts available for trading and contract specifications
   - Contract-wise price-volume data
   - Daily/monthly archives (bhavcopy, settlement prices, open interest, category-wise open interest)
4. **Currency, Commodity & Interest Rate Derivatives**:
   - Contract-wise price volume, daily bhavcopy, open interest, RBI reference rate statistics.
5. **Debt Segment**:
   - Negotiated WDM platform reports, corporate bonds trade archives, retail debt market bhavcopy.
6. **Listed Companies' Corporate Filings**:
   - Financial results (quarterly and annual)
   - Shareholding patterns
   - Corporate announcements and corporate actions (splits, bonuses, mergers, dividends)
   - Voting results, consolidated pledge, corporate governance reports
7. **Surveillance & Investor Awareness**:
   - Surveillance actions (ASM / GSM / ESM lists), margin trading files, periodic call auction illiquid securities list, defaulter members/clients list.

#### First Basket: Sub-Tier B (Voluminous Data; >2GB; Chargeable At Cost)
Voluminous records provisioned by the exchange for formal academic research at cost-recovery rates:
1. **Historical End-of-Day Data**: Comprehensive multi-year raw bhavcopy archives containing complete security and trade details across CM, WDM, and F&O segments.
2. **Bulk Corporate Data**: Machine-readable bulk corporate filing archives (fundamentals, announcements, shareholding history, governance).
3. **Historical Securities / Contracts Master**: Complete historical master records with contract specifications, lot sizes, and tick/quantity freeze limits.
4. **Historical Symbol-Wise & Instrument-Wise Turnover**: Comprehensive granular turnover archives.
5. **Tick-by-Tick (TBT) Historical Orders and Trades**:
   - *Policy Requirement*: Available **only for data older than 6 months** prior to the application date.
   - *Anonymization*: Stripped of all broker and client identification.

#### Second Basket: Restricted Data (Non-Shareable)
Under no circumstances may the following be shared with researchers or the public:
1. PAN-wise trade data across any segment.
2. Personal Identifiable Information (PII) of investors or market participants.
3. Unique Client Code (UCC) and KYC details.
4. Tick-by-tick order and trade data containing member or client identity.
5. Client-wise position data with member/client IDs.
6. Identity of polling participants or approved hedgers in commodity derivatives.

---

## 4. Mapping Eligible NSE Datasets to VESPER Modules

The eligible datasets from the First Basket map directly into the functional components of the **VESPER v2.1** quantitative architecture:

| VESPER Architecture Module | Functional Scope | Eligible NSE Research Policy Datasets | Policy Tier |
| :--- | :--- | :--- | :--- |
| **VESPER Forecast** | Directional returns, alpha factor calculation, trend models, multi-horizon price forecasting | • Capital Market Security-Wise Daily OHLCV<br>• Historical Index Data (Nifty 50, Nifty Bank)<br>• Contract-Wise Price-Volume Archives<br>• Corporate Action Adjustments (splits, bonuses) | First Basket (Freely Available / Voluminous EOD) |
| **VESPER Capital** | Portfolio sizing, capital allocation, rebalancing, market-cap classification, fund flow tracking | • Market Capitalisation Data<br>• Demat Turnover & Securities Traded<br>• MFSS Mutual Fund Subscription & Redemption Statistics<br>• Turnover Share by Trading Modes | First Basket (Freely Available) |
| **VESPER Quant** | Volatility surfaces, option pricing (BSM), term structure, cross-asset derivatives modeling | • F&O Daily Bhavcopy (Settlement Prices & Open Interest)<br>• Historical Contracts Master (Lot sizes, freeze limits)<br>• Currency & Interest Rate Derivatives Archives<br>• Sovereign T-Bill Yields (via RBI DBIE) | First Basket (Freely Available / Voluminous Master) |
| **VESPER Shield** | Drawdown control, risk management, circuit breakers, margin buffers, surveillance filters | • Exchange Surveillance Measures (ASM / GSM / ESM lists)<br>• Margin Trading Files & Haircuts<br>• Illiquid Securities Periodic Call Auction Lists<br>• Defaulting Clients & Expelled Members Rosters | First Basket (Freely Available Regulatory Reports) |
| **VESPER Radar** | Market surveillance, institutional flow tracking, block deal detection, regulatory disclosures | • FII/FPI & DII Daily Historical Trading Activity<br>• Bulk and Block Deals Archives<br>• Participant Category-Wise Open Interest (FII/DII/Pro/Client)<br>• Foreign Investment Limits in Listed Companies | First Basket (Freely Available / Voluminous FII) |
| **VESPER Pulse** | Market microstructure, order book dynamics, trade size distribution, execution efficiency | • Tick-by-Tick Orders & Trades (>6 months historical, anonymized)<br>• Total Trades Executed & Average Trade Size<br>• Trading Mode Breakdown (Colocation, Algo, Internet) | First Basket (Voluminous Chargeable >2GB) |

---

## 5. Verified Permissions vs Operational Assumptions

A rigorous quantitative data architecture must distinguish between what is **legally verified** versus what is an **operational assumption**:

### 1. The "Public Archive Fallacy" (NSE & Yahoo)
- **Operational Reality**: NSE daily bhavcopy archives (`archives.nseindia.com`) return HTTP 200 without authentication. Yahoo Finance endpoints return historical data instantly via `yfinance`.
- **Governance Finding**: **Public accessibility does not imply open redistribution or commercial rights.** Both providers explicitly reserve all intellectual property and forbid commercial redistribution, data reselling, or public dissemination under their binding Terms of Service.
- **VESPER Policy**: For Phase 00 and future personal quantitative research (private, internal, non-redistributed backtesting on local disk), usage is compliant with the "personal, non-commercial research" scope. Any future commercial offering, public dashboard, or external API of VESPER would require formal commercial licensing from NSE Data & Analytics Ltd (NDAL).

### 2. Formal Research Channel (July 2025 Policy)
- **Operational Reality**: The July 28, 2025 NSE Data Sharing Policy establishes a sanctioned, SEBI-mandated mechanism for researchers to obtain clean, official multi-year datasets directly from the exchange.
- **Governance Finding**: **FORMAL RESEARCH DATA PATH ESTABLISHED**. While bulk EOD and historical master data >2GB are chargeable at cost-recovery rates, this pathway provides clean institutional data provenance free from anti-scraping risks.
- **VESPER Status**: NSE is **Technically Approved as Primary Provider**. Legal access authorization and automated bulk ingestion permission remain **PENDING formal academic research application submission and exchange approval**.

### 3. Verified Sovereign Public Data (RBI DBIE)
- **Operational Reality**: RBI DBIE provides macro interest rates, T-Bill yields, and reference foreign exchange rates.
- **Governance Finding**: **VERIFIED PERMISSION**. As sovereign statistical data published by India's central bank under open government information mandates, historical series can be ingested, cached, and used in quantitative risk models without licensing fees, requiring only proper citation.

### 4. Proprietary Benchmark Governance (CCIL / FBIL)
- **Operational Reality**: Daily MIBOR and Zero-Coupon Yield Curves (ZCYC) are posted on CCIL and FBIL websites.
- **Governance Finding**: **PROPRIETARY BENCHMARKS**. FBIL was established specifically to administer Indian financial benchmarks under SEBI/RBI regulatory oversight. These benchmarks are protected intellectual property. While delayed tables can be viewed for personal reference, programmatic daily bulk feeds require an institutional data agreement.
- **VESPER Policy**: In Phase 01, VESPER will derive risk-free curves directly from primary RBI DBIE Treasury Bill cut-off yields (which are open sovereign data) rather than scraping proprietary FBIL benchmarks, avoiding legal exposure.

---

## 6. Academic Research Application Protocol

Under the SEBI / NSE Research Policy, academic and non-commercial quantitative researchers must follow a standardized application workflow:

```
┌────────────────────────────────────────────────────────────────────────┐
│               NSE RESEARCH DATA SHARING APPLICATION WORKFLOW           │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 1. RESEARCH PROJECT PROPOSAL                                           │
│ • Research synopsis, objectives, and quantitative methodology          │
│ • Specification of target universe (e.g. 8 liquid instruments, 2015+)  │
│ • Detailed mapping of requested datasets from First Basket             │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. APPLICANT CREDENTIALS & AFFILIATION                                 │
│ • Academic / institutional affiliation documentation                   │
│ • Lead researcher credentials & supervisory sign-off                   │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. LEGAL UNDERTAKING & NON-DISCLOSURE AGREEMENT (NDA)                  │
│ • Covenant: Data used strictly for non-commercial research/analysis    │
│ • Covenant: Absolute prohibition on data redistribution or reselling   │
│ • Covenant: Zero attempt to de-anonymize trade/order records           │
│ • Covenant: Secure storage, access logging, and post-project disposal  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. NSE COMMITTEE REVIEW & COST QUOTATION                               │
│ • Review by NSE Data Sharing Committee                                 │
│ • If payload > 2GB (Voluminous tier), cost-recovery quotation issued   │
│ • Data delivery via secure exchange SFTP / encrypted data transfer     │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 5. FORMAL AUTHORIZATION & REPOSITORY INGESTION                         │
│ • Official authorization certificate issued                            │
│ • Automated ingestion permission activated (Phase 01 unlocked)         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Current Governance Sign-Off Status

| Governance Dimension | Status | Justification & Safeguards |
| :--- | :---: | :--- |
| **NSE Technical Provider Status** | **APPROVED** | Verified URL structure, legacy/UDiFF parsers functional, zero validation errors across test suite. |
| **Legal Access Authorization** | **PENDING** | Requires formal submission and approval of `docs/nse_research_data_request.md` under the July 2025 Policy. |
| **Automated Ingestion Permission**| **PENDING** | Phase 01 bulk historical ingestion remains locked until formal approval is granted. |
| **Phase 00 Data Hygiene** | **PASSED** | Zero bulk downloads initiated; 56 raw sample files cataloged with SHA-256 in git-ignored `data/raw/spike/`. |
