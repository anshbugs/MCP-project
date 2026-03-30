from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.agents.orchestrator import analyst_graph
from src.tools.db import init_db, get_cached_query, insert_cached_query, get_recent_analysis, insert_analysis
import json

# Initialize SQLite Database Schema
init_db()

app = FastAPI(
    title="AI Equity Research Desk API", 
    description="Multi-agent financial intelligence system with strict SQLite LLM Caching Layer.",
    version="1.0.0"
)

# Request Models
class AnalyzeStockRequest(BaseModel):
    ticker: str

class AnalyzeMutualFundRequest(BaseModel):
    ticker: str

class PortfolioRequest(BaseModel):
    stocks: List[str]

class CompareStocksRequest(BaseModel):
    stock1: str
    stock2: str

class ChatIntentRequest(BaseModel):
    query: str

class ChatIntentResponse(BaseModel):
    ticker: Optional[str] = None
    asset_type: Optional[str] = None
    reply: str

@app.post("/extract-ticker", response_model=ChatIntentResponse)
def extract_ticker(req: ChatIntentRequest):
    # 1. Inspect Cache to save NLP LLM Cost
    cached = get_cached_query(req.query)
    if cached:
        return cached

    from src.config import get_llm
    from pydantic import Field
    from langchain_core.prompts import ChatPromptTemplate
    
    class IntentExtraction(BaseModel):
        ticker: Optional[str] = Field(None, description="The financial ticker symbol (e.g. RELIANCE.NS, VFINX) if provided. Use .NS for Indian stocks by default. None if ignored.")
        asset_type: Optional[str] = Field("stock", description="'stock', 'mutual_fund', or 'none'")
        reply: str = Field(description="Conversational acknowledgement like 'Analyzing Reliance Industries for you...'")
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI equity assistant. Extract the exact stock/fund ticker from the user query. Default to .NS for Indian companies."),
        ("user", "{query}")
    ])
    
    llm = get_llm().with_structured_output(IntentExtraction)
    try:
        res = (prompt | llm).invoke({"query": req.query})
        ticker_val = res.ticker if res.ticker else None
        asset_type_val = res.asset_type if res.asset_type in ["stock", "mutual_fund"] else "stock"
        
        insert_cached_query(req.query, ticker_val, asset_type_val, res.reply)
        
        return {
            "ticker": ticker_val,
            "asset_type": asset_type_val,
            "reply": res.reply
        }
    except Exception as e:
        return {"reply": "I couldn't perfectly parse that symbol. Please reframe."}

# Helper to execute the parallel agent graph
def run_analysis(ticker: str, asset_type: str = "stock") -> dict:
    try:
        ticker_upper = ticker.upper()
        
        # 1. DB CACHE LAYER INTERCEPT (saves full run)
        cached = get_recent_analysis(ticker_upper)
        if cached:
            try:
                fund_data = json.loads(cached.get("fundamental_data_json", "{}"))
            except:
                fund_data = {}
                
            return {
                "ticker": cached["ticker"],
                "summary": cached["pm_summary"] + "\n\n*(⚡ Processed instantly via local Database cache)*",
                "scores": {
                    "fundamental": cached["fundamental_score"],
                    "technical": cached["technical_score"],
                    "sentiment": cached["sentiment_score"],
                    "final": cached["final_score"]
                },
                "recommendation": cached["recommendation"],
                "confidence": 0.99,
                "fundamental_data": fund_data
            }
            
        # 2. RUN FULL AGENTS (No Cache found or over 12hrs)
        initial_state = {"ticker": ticker_upper, "asset_type": asset_type}
        result = analyst_graph.invoke(initial_state)
        
        # --- Log the raw data fetched by agents ---
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker_upper,
            "asset_type": asset_type,
            "fundamental_data": result.get("fundamental_data"),
            "technical_data": result.get("technical_data"),
            "sentiment_data": result.get("sentiment_data")
        }
        try:
            with open("data_fetched_log.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Failed to log data: {e}")
            
        # --- Google Sheets Integration ---
        from src.tools.sheets import append_to_sheet
        append_to_sheet([
            datetime.now().isoformat(),
            ticker_upper,
            asset_type,
            result.get("final_score", 0.0),
            result.get("recommendation", "N/A"),
            result.get("fundamental_score", 0.0),
            result.get("technical_score", 0.0),
            result.get("sentiment_score", 0.0),
            result.get("final_summary", "No summary generated.")
        ])
        
        # --- SQLite Database Storage Integration ---
        insert_analysis({
            "ticker": ticker_upper,
            "asset_type": asset_type,
            "final_score": result.get("final_score", 0.0),
            "recommendation": result.get("recommendation", "N/A"),
            "fundamental_score": result.get("fundamental_score", 0.0),
            "technical_score": result.get("technical_score", 0.0),
            "sentiment_score": result.get("sentiment_score", 0.0),
            "final_summary": result.get("final_summary", "No summary generated."),
            "fundamental_data": result.get("fundamental_data", {})
        })
        
        f_score = result.get("fundamental_score", 0.0)
        t_score = result.get("technical_score", 0.0)
        s_score = result.get("sentiment_score", 0.0)
        
        import statistics
        scores = [f_score, t_score, s_score]
        try:
            variance = statistics.variance(scores)
            confidence = max(0.0, min(1.0, 1.0 - (variance / 20.0))) 
        except Exception:
            confidence = 0.8
             
        return {
            "ticker": ticker_upper,
            "summary": result.get("final_summary", "No summary generated."),
            "scores": {
                "fundamental": f_score,
                "technical": t_score,
                "sentiment": s_score,
                "final": result.get("final_score", 0.0)
            },
            "recommendation": result.get("recommendation", "N/A"),
            "confidence": round(confidence, 2),
            "fundamental_data": result.get("fundamental_data", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed for {ticker}: {str(e)}")

@app.post("/analyze-stock")
def analyze_stock(req: AnalyzeStockRequest):
    return run_analysis(req.ticker, asset_type="stock")

@app.post("/analyze-mutual-fund")
def analyze_mutual_fund(req: AnalyzeMutualFundRequest):
    return run_analysis(req.ticker, asset_type="mutual_fund")

@app.post("/portfolio-analysis")
def portfolio_analysis(req: PortfolioRequest):
    results = []
    overall_score = 0.0
    best_stock = None
    worst_stock = None
    best_score = -1.0
    worst_score = 11.0

    if not req.stocks:
        raise HTTPException(status_code=400, detail="Stock list cannot be empty.")

    for ticker in req.stocks:
        analysis = run_analysis(ticker)
        results.append(analysis)
        score = analysis["scores"]["final"]
        overall_score += score
        
        if score > best_score:
            best_score = score
            best_stock = ticker
        
        if score < worst_score:
            worst_score = score
            worst_stock = ticker

    avg_score = round(overall_score / len(req.stocks), 2)
    
    return {
        "portfolio_average_score": avg_score,
        "best_performer": best_stock,
        "worst_performer": worst_stock,
        "individual_analyses": results
    }

@app.post("/compare-stocks")
def compare_stocks(req: CompareStocksRequest):
    analysis1 = run_analysis(req.stock1)
    analysis2 = run_analysis(req.stock2)
    
    score1 = analysis1["scores"]["final"]
    score2 = analysis2["scores"]["final"]
    
    better_stock = req.stock1 if score1 >= score2 else req.stock2
    
    return {
        "winner": better_stock,
        "comparison": {
            req.stock1: analysis1,
            req.stock2: analysis2
        },
        "summary": f"Based on our final aggregator scoring, {better_stock} is the better buy currently."
    }
