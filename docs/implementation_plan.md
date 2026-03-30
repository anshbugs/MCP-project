# Implementation Plan

## Goal Description
The goal is to implement Phase 0 and Phase 1 of the multi-agent financial intelligence system. This covers initializing the project environment and building the foundational Data Fetching Layer, which includes necessary tools for Yahoo Finance and web searching.

## User Review Required
- Please review the proposed directory structure below.
- Confirm if `yfinance` and `duckduckgo-search` libraries are acceptable for the tools in Phase 1.

## Proposed Changes

### Phase 0: Project Setup
We will initialize the basic structure and install dependencies.
#### [NEW] `requirements.txt`
Will include standard libraries: `langchain`, `langgraph`, `yfinance`, `duckduckgo-search`, `fastapi`, `streamlit`, `python-dotenv`, `openai`.
#### [NEW] `src/` directory structure
- `src/tools/` (Data fetching logic)
- `src/agents/` (The LangGraph nodes)
- `src/api/` (FastAPI backend)
- `src/ui/` (Streamlit frontend)
- `src/config.py` (Centralized config like LLM models and API keys)

### Phase 1: Data Fetching Layer
We will build the shared tools that the agents will use.
#### [NEW] `src/tools/finance.py`
Functions to fetch:
- Company fundamentals (PE, Debt/Equity, ROE, etc.)
- Historical price data and simple moving averages (50, 200).
#### [NEW] `src/tools/search.py`
Functions to fetch:
- Market news and headlines via DuckDuckGo.

## Verification Plan
### Automated Tests
- Create a quick script `test_tools.py` in the root or `tests/` directory to assert that `finance.py` and `search.py` successfully pull data for a sample ticker (e.g., "RELIANCE.NS").
