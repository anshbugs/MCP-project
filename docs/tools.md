# Shared Tools & Data Fetching Layer

This document outlines the shared tools and data sources used by the LangGraph agents.

## Design Philosophy
Make the data fetching layer a **shared service/tool** used uniformly by all intelligence agents.

## 1. Yahoo Finance (`yfinance`)
- **Used by:** Fundamental Analyst Agent, Technical Analyst Agent
- **Description:** Primary source for market and financial data.
- **Data Points Collected:**
  - **Fundamentals:** Revenue growth, Net profit, EPS, PE ratio, Debt/Equity, ROE.
  - **Technicals:** Historical price history, Trading volume.
  - **Indicators (Derived or Fetched):** RSI, MACD, Moving averages (e.g., 50-day, 200-day).

## 2. Web Search & News (DuckDuckGo API / Scraping)
- **Used by:** Sentiment Analysis Agent
- **Description:** Primary source for qualitative sentiment analysis.
- **Data Points Collected:**
  - DuckDuckGo search results for the given stock/company.
  - Recent news headlines and financial press.
