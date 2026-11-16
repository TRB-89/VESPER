# VESPER v2.1 — Phase 00: Provider Licensing & Data Governance Matrix

> **Author**: Senior Quantitative Researcher, Financial Data Engineer & Data Governance Specialist  
> **Project**: VESPER v2.1 (Personal Indian-Equities Quantitative Research Project)  
> **Phase**: Phase 00 (Data Provider Spike Closure)  
> **Governance Directive**: Distinguish verified legal permissions from operational accessibility. **Public accessibility does not constitute unrestricted licensing permission.**

---

## 1. Overview & Governance Principles

In quantitative finance and algorithmic research, data provenance and licensing governance are as fundamental as model alpha. A data source that is technically accessible via an open HTTP endpoint or unofficial API may still carry strict contractual, legal, or intellectual property restrictions that prohibit automated harvesting, long-term persistence, commercialization, or redistribution.

This document records the official terms of service, published pricing, automated access restrictions, storage rights, redistribution rights, and formal governance classifications for all candidate providers evaluated in Phase 00.

---

## 2. Comprehensive Provider Licensing Matrix

| Provider | Published Cost | Official Terms URL | Automated Access Policy | Storage / Caching Rights | Redistribution & Commercial Rights | Governance Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NSE Official Bhavcopy (Cash & Index Archives)** | Free (Public archive servers) | [NSE Terms of Use](https://www.nseindia.com/terms-of-use) | **Archive servers** (`archives.nseindia.com`, `nsearchives.nseindia.com`): Accessible via HTTP GET without WAF challenges when adhering to polite rate limits (>=2.0s delay).<br>**Website API** (`www.nseindia.com/api`): Strictly protected by Akamai WAF / HTTP 503 bot detection (`robots: noindex, nofollow`). | Permitted for private, internal, non-commercial analytical caching. Mass persistent external distribution is unauthorized. | **Strictly Prohibited without Data Vendor License**. Section: *"The Information on the Website is provided for personal, non-commercial use and informational purposes only... You may not copy, reproduce, recompile, decompile, disassemble, reverse engineer, distribute, publish, display, perform, modify, upload to, create derivative works from, transmit, or in any way exploit any part of the Website..."* Commercial indexing or commercial redistribution requires a formal agreement with NSE Data & Analytics Ltd (NDAL). | **HUMAN REVIEW REQUIRED**<br>*(Permitted for personal research; commercial use prohibited)* |
| **Yahoo Finance (via yfinance)** | Free (Retail tier) | [Yahoo Terms of Service](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) and [Developer APIs Terms](https://policies.yahoo.com/us/en/yahoo/terms/product-atos/apiforydn/index.html) | No official public API key. Accessible via unofficial REST endpoints subject to rate throttling and IP blacklisting. `robots.txt` disallows internal API paths (`/_td_api`, `/caas/`, etc.). | Short-term client caching permitted for personal evaluation. Persistent multi-user archiving prohibited. | **Strictly Prohibited**. Data is licensed by Yahoo from third-party exchanges (ICE Data Services, NSE). Personal, non-commercial use only. Automated mass scraping and commercial redistribution violate Section 8 (Member Conduct). | **HUMAN REVIEW REQUIRED**<br>*(Permitted for personal cross-validation only; secondary status)* |
| **Zerodha Kite Connect API** | • **Personal**: ₹0/mo (no market data)<br>• **Connect**: ₹500/mo per API key (includes live ticks & historical candles)<br>• **Rebate**: ₹500 developer credit if monthly brokerage >= ₹2,000 | [Kite Terms](https://kite.trade/terms) and [Kite Pricing](https://kite.trade/pricing) | Formal REST API and WebSocket feed. Enforces strict rate limits: max 3 requests/sec per API key. Requires daily OAuth access token. | Caching permitted strictly for execution algorithms and portfolio analysis of the authenticated account. | **Strictly Prohibited**. Section 4: *"You shall not redistribute, sub-license, rent, lease, or resell the Kite Connect API or data received through the API to any third party."* API is strictly for individual personal algorithmic trading or approved institutional broker clients. | **HUMAN REVIEW REQUIRED**<br>*(Permitted for personal execution; unsuited for bulk 10-year backtests)* |
| **NSE Derivatives (F&O Bhavcopy)** | Free (Public archive servers) | [NSE Terms of Use](https://www.nseindia.com/terms-of-use) | Same as cash equity archive servers (`archives.nseindia.com`, `nsearchives.nseindia.com`). Continuous historical daily zip archives. | Permitted for personal internal research and backtesting. | Same as NSE Cash: Redistribution, public display, or commercial product packaging requires NDAL enterprise license. | **HUMAN REVIEW REQUIRED**<br>*(Permitted for personal research; commercial use prohibited)* |
| **Reserve Bank of India (RBI DBIE)** | Free (Public Sovereign Data) | [RBI Disclaimer & Rights](https://www.rbi.org.in/commonman/English/Scripts/Disclaimer.aspx) | Public web portal and direct CSV/XLS downloads. No API key required. No aggressive anti-bot challenge on public report URLs. | **Permitted**. Macroeconomic and sovereign interest rate data may be stored in local databases and persistent quantitative stores. | **Permitted with Attribution**. Public sovereign data. Permitted for analytical models and commercial research provided clear attribution is maintained: *"Source: Reserve Bank of India"*. RBI disclaims liability for financial decisions. | **VERIFIED PERMISSION**<br>*(Open public sovereign data for research & models)* |
| **CCIL & Financial Benchmarks India (FBIL)** | • Delayed web tables: Free<br>• Automated proprietary feed: Paid institutional subscription | [CCIL Disclaimer](https://www.ccilindia.com/Disclaimer.aspx) and [FBIL Terms](https://www.fbil.org.in) | Public portal web tables; automated scraping is discouraged and blocked by intermittent CAPTCHA. Direct FTP/API feeds require paid enterprise contract. | Delayed web data may be cached for internal personal study. Persistent benchmark feeds require contract. | **Strictly Prohibited without FBIL Data Vendor License**. MIBOR, Term MIBOR, ZCYC, and sovereign trade indices are proprietary benchmarks of FBIL/CCIL. Cannot be redistributed, republished, or packaged into commercial index products. | **HUMAN REVIEW REQUIRED**<br>*(Free delayed viewing only; commercial feeds require paid contract)* |

---

## 3. Verified Permissions vs Operational Assumptions

A rigorous quantitative data architecture must distinguish between what is **legally verified** versus what is an **operational assumption**:

### 1. The "Public Archive Fallacy" (NSE & Yahoo)
- **Operational Reality**: NSE daily bhavcopy archives (`archives.nseindia.com`) return HTTP 200 without authentication. Yahoo Finance endpoints return historical data instantly via `yfinance`.
- **Governance Finding**: **Public accessibility does not imply open redistribution or commercial rights.** Both providers explicitly reserve all intellectual property and forbid commercial redistribution, data reselling, or public dissemination under their binding Terms of Service.
- **VESPER Policy**: For Phase 00 and future personal quantitative research (private, internal, non-redistributed backtesting on local disk), usage is compliant with the "personal, non-commercial research" scope. Any future commercial offering, public dashboard, or external API of VESPER would require formal commercial licensing from NSE Data & Analytics Ltd (NDAL).

### 2. Verified Sovereign Public Data (RBI DBIE)
- **Operational Reality**: RBI DBIE provides macro interest rates, T-Bill yields, and reference foreign exchange rates.
- **Governance Finding**: **VERIFIED PERMISSION**. As sovereign statistical data published by India's central bank under open government information mandates, historical series can be ingested, cached, and used in quantitative risk models without licensing fees, requiring only proper citation.

### 3. Proprietary Benchmark Governance (CCIL / FBIL)
- **Operational Reality**: Daily MIBOR and Zero-Coupon Yield Curves (ZCYC) are posted on CCIL and FBIL websites.
- **Governance Finding**: **PROPRIETARY BENCHMARKS**. FBIL was established specifically to administer Indian financial benchmarks under SEBI/RBI regulatory oversight. These benchmarks are protected intellectual property. While delayed tables can be viewed for personal reference, programmatic daily bulk feeds require an institutional data agreement.
- **VESPER Policy**: In Phase 01, VESPER will derive risk-free curves directly from primary RBI DBIE Treasury Bill cut-off yields (which are open sovereign data) rather than scraping proprietary FBIL benchmarks, avoiding legal exposure.

---

## 4. Operational Cost Model

| Provider Role | Selected Source | Ongoing Phase 00/01 Data Cost | Setup / API Key Fees | Compute / Ingestion Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Cash & Index** | NSE Official Archives | ₹0 (Free public archives) | ₹0 | Minimal local compute / disk storage |
| **Primary Derivatives (F&O)** | NSE F&O Archives | ₹0 (Free public archives) | ₹0 | Minimal local compute / disk storage |
| **Secondary Cross-Validation**| Yahoo Finance | ₹0 (Retail personal tier) | ₹0 | Zero infrastructure cost |
| **Macro / Risk-Free Curves** | RBI DBIE | ₹0 (Public sovereign data) | ₹0 | Zero infrastructure cost |
| **Optional Future Live Execution** | Zerodha Kite Connect | ₹500 / month (Connect Tier) | ₹0 (Rebated if monthly brokerage >= ₹2,000) | Local WebSocket runner |
| **Total Immediate Data Outlay** | — | **₹0.00** | **₹0.00** | **Zero subscription costs incurred** |

---

## 5. Compliance Sign-Off Recommendation

1. **Phase 00 Data Ingestion Compliance**:
   - All Phase 00 downloads complied with domain-specific rate limits (`>= 2.0s` delay via `RateLimiter`).
   - Zero authentication controls, CAPTCHAs, or paywalls were bypassed or circumvented.
   - All downloaded data is stored in `data/raw/spike/` which is strictly git-ignored and excluded from version control.
2. **Provisional Architecture Approval**:
   - The provisional selection of **NSE Official Bhavcopy** (Primary) + **Yahoo Finance** (Secondary Cross-Validation) + **RBI DBIE** (Macro) + **Zerodha Kite** (Future Live Execution) is sound, cost-optimal (₹0 initial spend), and legally aligned with personal quantitative research boundaries.
