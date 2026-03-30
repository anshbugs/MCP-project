from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.config import get_llm
from src.tools.search import fetch_market_news

class SentimentOutput(BaseModel):
    sentiment_score: float = Field(description="Score from 0.0 to 10.0 based on news sentiment (10 is extremely positive).")
    summary: str = Field(description="Brief summary of the market sentiment.")
    market_sentiment: str = Field(description="Positive, Neutral, or Negative.")

def analyze_sentiment(state: dict) -> dict:
    ticker = state["ticker"]
    asset_type = state.get("asset_type", "stock")
    news = fetch_market_news(ticker, asset_type=asset_type)
    
    llm = get_llm().with_structured_output(SentimentOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an elite Sentiment Analyst. Review recent news and headlines. Assign a sentiment score from 0.0 to 10.0 representing the market's bullishness or bearishness. CRITICAL: Your summary MUST be strictly 2-3 sentences max. Do NOT write long paragraphs."),
        ("user", "Recent news results for {ticker}:\n{news}")
    ])
    
    try:
        response = (prompt | llm).invoke({"ticker": ticker, "news": news})
        return {"sentiment_data": {"news": news}, "sentiment_score": response.sentiment_score, "sentiment_summary": response.summary}
    except Exception as e:
        return {"sentiment_score": 5.0, "sentiment_summary": f"Failed to analyze sentiment: {str(e)}"}
