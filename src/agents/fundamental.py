import json
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.config import get_llm
from src.tools.finance import get_stock_fundamentals, get_mf_fundamentals

class FundamentalOutput(BaseModel):
    fundamental_score: float = Field(description="Score from 0.0 to 10.0 based on fundamental strength.")
    summary: str = Field(description="Brief summary of the fundamental analysis.")
    verdict: str = Field(description="Verdict: Strong, Moderate, or Weak.")

def analyze_fundamentals(state: dict) -> dict:
    ticker = state["ticker"]
    asset_type = state.get("asset_type", "stock")
    
    if asset_type == "mutual_fund":
        fundamentals = get_mf_fundamentals(ticker)
        sys_prompt = "You are an expert Mutual Fund Analyst. Analyze the fund metrics (returns, ratings, expense ratio). Calculate a strict fundamental score out of 10.0."
    else:
        fundamentals = get_stock_fundamentals(ticker)
        sys_prompt = "You are an expert Fundamental Analyst at a top-tier hedge fund. Analyze the provided financial metrics. Calculate a highly critical fundamental score out of 10.0."

    if "error" in fundamentals:
         return {"fundamental_score": 0.0, "fundamental_data": fundamentals, "fundamental_summary": fundamentals["error"]}
         
    llm = get_llm().with_structured_output(FundamentalOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_prompt + " CRITICAL: Your summary MUST be strictly 2-3 sentences max. Do NOT write long paragraphs."),
        ("user", "Metrics for {ticker}:\n{metrics}")
    ])
    
    try:
        response = (prompt | llm).invoke({"ticker": ticker, "metrics": json.dumps(fundamentals)})
        return {"fundamental_data": fundamentals, "fundamental_score": response.fundamental_score, "fundamental_summary": response.summary}
    except Exception as e:
        return {"fundamental_score": 5.0, "fundamental_summary": f"Failed to analyze fundamentals: {str(e)}"}
