import yfinance as yf
from typing import Dict, Any
import pandas as pd

def get_stock_fundamentals(ticker: str) -> Dict[str, Any]:
    """Fetch fundamental data for a given stock ticker from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "revenueGrowth": info.get("revenueGrowth"),
            "profitMargins": info.get("profitMargins"),
            "trailingEps": info.get("trailingEps"),
            "forwardPE": info.get("forwardPE"),
            "trailingPE": info.get("trailingPE"),
            "debtToEquity": info.get("debtToEquity"),
            "returnOnEquity": info.get("returnOnEquity"),
            "summary": "Data fetched successfully from Yahoo Finance.",
        }
    except Exception as e:
        return {"error": f"Failed to fetch stock fundamentals for {ticker}: {str(e)}"}

def get_mf_fundamentals(ticker: str) -> Dict[str, Any]:
    """Fetch fundamental data for a Mutual Fund from Yahoo Finance."""
    try:
        mf = yf.Ticker(ticker)
        info = mf.info
        return {
            "ticker": ticker,
            "fundFamily": info.get("fundFamily"),
            "categoryName": info.get("categoryName"),
            "yield": info.get("yield"),
            "ytdReturn": info.get("ytdReturn"),
            "threeYearAverageReturn": info.get("threeYearAverageReturn"),
            "fiveYearAverageReturn": info.get("fiveYearAverageReturn"),
            "expenseRatio": info.get("expenseRatio"),
            "morningStarRating": info.get("morningStarOverallRating"),
            "totalAssets": info.get("totalAssets"),
            "nav": info.get("navPrice"),
            "summary": "MF Data fetched successfully from Yahoo Finance."
        }
    except Exception as e:
        return {"error": f"Failed to fetch MF fundamentals for {ticker}: {str(e)}"}

def get_stock_technicals(ticker: str) -> Dict[str, Any]:
    """Fetch technical indicator data (prices/NAV, moving averages)."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            return {"error": f"No price history found for {ticker}."}
            
        current_price = hist['Close'].iloc[-1]
        
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
        ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None
        
        trend = "Sideways"
        if ma_50 and ma_200:
            if current_price > ma_50 and ma_50 > ma_200:
                trend = "Bullish"
            elif current_price < ma_50 and ma_50 < ma_200:
                trend = "Bearish"
                
        return {
            "ticker": ticker,
            "current_price": current_price,
            "ma_50": ma_50,
            "ma_200": ma_200,
            "trend": trend,
            "summary": "Technical data fetched successfully."
        }
    except Exception as e:
        return {"error": f"Failed to fetch technicals for {ticker}: {str(e)}"}
