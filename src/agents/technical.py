import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.config import get_llm
from src.tools.finance import get_stock_technicals

class TechnicalOutput(BaseModel):
    technical_score: float = Field(description="Score from 0.0 to 10.0 based on technical indicators (trend, moving averages).")
    summary: str = Field(description="Brief summary of the technical analysis.")
    trend: str = Field(description="Bullish, Bearish, or Sideways.")

def analyze_technicals(state: dict) -> dict:
    ticker = state["ticker"]
    asset_type = state.get("asset_type", "stock")
    technicals = get_stock_technicals(ticker)
    
    if "error" in technicals:
         return {"technical_score": 0.0, "technical_data": technicals, "technical_summary": technicals["error"]}
         
    llm = get_llm().with_structured_output(TechnicalOutput)
    
    asset_noun = "NAV" if asset_type == "mutual_fund" else "price"
    sys_prompt = f"You are an expert Technical Analyst. Evaluate the {asset_noun} trends and moving averages. Calculate a technical score out of 10.0. CRITICAL: Your summary MUST be strictly 2-3 sentences max. Do NOT write long paragraphs."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_prompt),
        ("user", "Technical data for {ticker}:\n{metrics}")
    ])
    
    try:
        response = (prompt | llm).invoke({"ticker": ticker, "metrics": json.dumps(technicals)})
        return {"technical_data": technicals, "technical_score": response.technical_score, "technical_summary": response.summary}
    except Exception as e:
        return {"technical_score": 5.0, "technical_summary": f"Failed: {str(e)}"}
