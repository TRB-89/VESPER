# VESPER v2.1 — Indian Equities Quantitative Research Project

## Phase 00: Data Provider Spike

Phase 00 is an exploratory spike and provenance audit, evaluating potential data providers for Indian equity market research (2015-01-01 to present). It evaluates data sources, data integrity, corporate action handling, licensing terms, and historical availability.

> **Note**: Phase 00 is an investigation, not a production trading system. No trading models, databases, or frontends are built during this phase.

---

### Prerequisites

- Python 3.11+
- Virtual environment or package manager with dependencies installed:
  - `pandas==3.1.1`
  - `pyarrow==26.0.1`
  - `duckdb==2.0.0`
  - `requests==2.34.2`
  - `yfinance==1.8.0`
  - `pytest==9.1.1`

Install dependencies via:
```bash
pip install -r <(python -c "import tomllib; [print(d) for d in tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']]")
# or simply:
pip install pandas pyarrow duckdb requests yfinance pytest
```

---

### Project Structure

```
VESPER/
├── pyproject.toml        # Pinned project dependencies and tool configurations
├── .gitignore            # Ignores data/, .env, caches, etc.
├── .env.example          # Template for local environment variables
├── README.md             # Project documentation and execution instructions
├── data/raw/             # Raw downloaded data storage (git-ignored)
├── docs/                 # Provenance reports and analysis documentation
├── research/
│   └── spike/            # Spike modules, contracts, validators, and provider probes
└── tests/                # Unit and integration test suite
```

---

### Running the Tests

To run the complete test suite:
```bash
pytest -v
```

---

### Running Provider Probes & Analysis

Once implemented, individual probes and analysis scripts in `research/spike/` can be executed directly with Python:
```bash
python -m research.spike.probe_nse
python -m research.spike.probe_yahoo
python -m research.spike.analyze
```
