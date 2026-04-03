# AI Equity Research Desk

A multi-agent decision intelligence system built for PMs and traders. This leverages LangGraph for complex agent orchestration, FastAPI for production routing, and Streamlit for stunning frontends.Helps compare stocks, answer investment questions, anaylses the risk and tells whether to invest or not.
https://mcp-projectgit-9xlhclkbjeeykskue9i9x6.streamlit.app/

## 🚀 Setup & Execution

### 1. Install Dependencies
Ensure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```

### 2. Verify `.env` File
Ensure your `.env` contains your API key at the root of the project:
```env
OPENROUTER_API_KEY=sk-or-...
```

### 3. Start the Backend API (Terminal 1)
Start the FastAPI intelligence engine:
```bash
uvicorn src.api.main:app --reload
```
The API will be available at `http://localhost:8000`. You can view the swagger docs at `http://localhost:8000/docs`.

### 4. Start the Streamlit UI (Terminal 2)
In a new terminal window, start the frontend dashboard:
```bash
streamlit run src/ui/app.py
```
This will automatically open your web browser to the application!

---
## Architecture
- **Data Layer:** `yfinance`, `duckduckgo-search`
- **Intelligence Layer:** 3 Specialized LangChain Agents (Fundamental, Technical, Sentiment)
- **Orchestration:** LangGraph parallel states
- **API Backend:** FastAPI
- **Frontend Dashboard:** Streamlit
