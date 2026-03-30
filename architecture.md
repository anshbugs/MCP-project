# Architecture: Multi-Agent Financial Intelligence System

## 1. System Overview (Big Picture)
The system is designed as a mini AI equity research desk. It leverages a multi-agent financial intelligence architecture composed of several interconnected layers.

- **Data Layer:** Yahoo Finance + Web Search (DuckDuckGo)
- **Intelligence Layer:** Specialized analysis agents
- **Orchestration Layer:** LangGraph
- **API Layer:** FastAPI
- **UI Layer:** Streamlit

### High-Level Architecture Diagram
```mermaid
graph TD
    subgraph UI Layer
        A[Streamlit UI]
    end

    subgraph API Layer
        B[FastAPI Server]
        B1[/analyze-stock] -.-> B
        B2[/portfolio-analysis] -.-> B
        B3[/compare-stocks] -.-> B
    end

    subgraph Orchestration Layer
        C[LangGraph Orchestrator<br/>Master Node Agent]
    end

    subgraph Intelligence Layer
        D[Fundamental Agent]
        E[Technical Agent]
        F[Sentiment Agent]
        G[Data Fetch Agent]
    end

    subgraph Data Sources
        H[Yahoo Finance API]
        I[DuckDuckGo Search]
    end

    A -->|Query / Dashboard| B
    B -->|API Calls| C
    C -->|Parallel Execution| D
    C -->|Parallel Execution| E
    C -->|Parallel Execution| F
    
    D --> G
    E --> G
    F --> G

    G --> H
    G --> I
```

---

## 2. Core Components Breakdown

### 2.1 Master Node (Orchestrator Agent - LangGraph)
This acts as the brain of the system, managing intent classification and agent orchestration.
- **Responsibilities:**
  - **Intent Classification:** Understand user query intent (Single stock, Portfolio, Comparison).
  - **Orchestration:** Trigger relevant agents in parallel.
  - **Aggregation:** Collect and aggregate results from all agents.
  - **Generation:** Generate the final answer containing a Summary, Recommendation, and Confidence score.

### 2.2 Fundamental Analyst Agent
- **Input:** Stock ticker (e.g., RELIANCE.NS)
- **Data Sources:** Yahoo Finance (Revenue growth, Net profit, EPS, PE ratio, Debt/Equity, ROE).
- **Responsibilities:** Analyze the core financials of a company.
- **Output:** Fundamental score (e.g., /10), Summary, Verdict (Strong/Moderate/Weak), Key metrics.

### 2.3 Technical Analyst Agent
- **Data Sources:** Price history, Common Indicators (RSI, MACD, Moving averages - 50 MA, 200 MA).
- **Responsibilities:** Identify trends, entry/exit signals from historical price action.
- **Output:** Trend (Bullish/Bearish/Sideways), Signals (e.g., "RSI overbought"), Entry suggestion, Technical score.

### 2.4 Sentiment Analysis Agent
- **Data Sources:** DuckDuckGo search results, News headlines.
- **Processing:** LLM-based sentiment classification, Score aggregation based on recent news and discussion.
- **Output:** Sentiment score, News summary, Market sentiment (Positive/Neutral/Negative).

### 2.5 Data Fetching Layer (Shared Tool)
- **Tools:** `yfinance` (Yahoo Finance API), DuckDuckGo API/Scraping.
- **Design:** Implemented as a shared service or tool that is utilized uniformly by all intelligence agents.

---

## 3. LangGraph Flow Design

### Execution Pipeline
```
START
  ↓
Intent Classifier
  ↓
Parallel Execution:
   ├── Fundamental Agent
   ├── Technical Agent
   └── Sentiment Agent
  ↓
Aggregator Node
  ↓
Final Response Generator
  ↓
END
```

### Execution Logic by Use Case
1. **Single Stock Query:** Run all 3 agents for the stock -> Aggregate to a single summary.
2. **Portfolio Query:** Loop through stocks -> Run agents per stock -> Aggregate portfolio-level metrics (Average score, Best/Worst performer).
3. **Comparison Query:** Run agents for both stocks -> Use a Comparative Analysis Node to provide side-by-side metrics and a final recommendation.

---

## 4. Aggregation & Scoring Logic
The Aggregator Node differentiates the system by combining signals into a unified metric.

### Example Scoring Formula
```text
Final Score = (0.40 × Fundamental Score) + 
              (0.35 × Technical Score) + 
              (0.25 × Sentiment Score)
```

### Recommendation Logic
| Score Range | Recommendation |
| ----------- | -------------- |
| > 8         | Strong Buy     |
| 6 – 8       | Buy            |
| 4 – 6       | Hold           |
| < 4         | Avoid          |

---

## 5. FastAPI Backend Design

### Key Endpoints
1. **Stock Analysis**
   - `POST /analyze-stock`
   - Body: `{"ticker": "RELIANCE.NS"}`
2. **Portfolio Analysis**
   - `POST /portfolio-analysis`
   - Body: `{"stocks": ["TATAMOTORS.NS", "M&M.NS", "INFY.NS"]}`
3. **Compare Stocks**
   - `POST /compare-stocks`
   - Body: `{"stock1": "TATAMOTORS.NS", "stock2": "M&M.NS"}`

### Unified Response Format
```json
{
  "summary": "...",
  "scores": {
    "fundamental": 8.0,
    "technical": 7.5,
    "sentiment": 8.5,
    "final": 8.0
  },
  "recommendation": "Buy",
  "confidence": 0.82
}
```

---

## 6. Streamlit UI Design

### Pages
1. **🔍 Stock Analyzer:** Input ticker to see Score, Charts, and Final Recommendation.
2. **📊 Portfolio Dashboard:** Input multiple stocks to view Overall portfolio score, Best/Worst stock, and Allocation visuals (Pie charts).
3. **⚖️ Compare Stocks:** Side-by-side comparison of metrics with a final declared winner.

---

## 7. Technology Stack

| Layer | Technology |
| --- | --- |
| **UI** | Streamlit |
| **Backend** | FastAPI |
| **Orchestration** | LangGraph |
| **LLM** | OpenAI / OpenRouter |
| **Data Source (Market)** | Yahoo Finance (`yfinance`) |
| **Data Source (Web/News)** | DuckDuckGo |
| **Deployment** | Render / Railway |

---

## 8. Advanced / Bonus Features (PM-Level Polish)
- **Explainability Layer:** Explain "Why this recommendation?" highlighting top 3 signals and potential risks.
- **Confidence Score:** Derived from data completeness and agent agreement.
- **Memory Layer:** Retain past queries and track portfolio development over time.
- **Alerts:** Automated monitoring to trigger "Notify when stock becomes BUY" alerts.
