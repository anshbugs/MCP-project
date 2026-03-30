import sys
import os
# Ensure Streamlit can resolve the 'src' module in the cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import requests
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# FastApi Backend URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Core UI | AI Equity Desk", page_icon="💬", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium Dark Theme & Glassmorphism ---
st.markdown("""
<style>
    .stApp { background-color: #0A0E17; }
    [data-testid="stSidebar"] { background-color: #0d121c !important; border-right: 1px solid rgba(255,255,255,0.05); }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Inter', sans-serif; font-weight: 600; letter-spacing: -0.5px; }
    div[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 700 !important; color: #00E676 !important; }
    
    /* Glassmorphism Inputs & Buttons */
    div[data-baseweb="input"] > div { background-color: #151a22 !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 8px; color: white !important; }
    .stButton>button { width: 100%; border-radius: 8px; background: linear-gradient(90deg, #00E676 0%, #00B0FF 100%); color: white; border: none; transition: all 0.3s ease; font-weight: 600; padding: 0.75rem !important; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0, 230, 118, 0.3); }
    
    /* Alerts & Chat Bubbles */
    div.stInfo, div.stSuccess, div.stWarning { background-color: rgba(21, 26, 34, 0.6) !important; border: 1px solid rgba(255, 255, 255, 0.05) !important; border-left: 4px solid #00E676 !important; backdrop-filter: blur(10px); color: #E0E6ED; border-radius: 6px; }
    .stChatMessage { background-color: #121824 !important; border: 1px solid rgba(255, 255, 255, 0.05) !important; padding: 1.5rem; border-radius: 12px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='text-align: center; color: #00E676 !important;'>⚡ Equity Desk</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
page = st.sidebar.radio("", ["💬 AI Chat Assistant", "🔍 Stock Analyzer", "📈 Mutual Fund Analyzer", "📊 Portfolio Dashboard", "⚖️ Compare Stocks"])
st.sidebar.markdown("---")
st.sidebar.info("System AI Status: Online\nData: Live via Yahoo/DDG")

def fetch_analysis(endpoint: str, payload: dict):
    from src.api.main import run_analysis, portfolio_analysis, compare_stocks
    from src.api.main import PortfolioRequest, CompareStocksRequest
    try:
        if endpoint == "analyze-stock":
            return run_analysis(payload["ticker"], "stock")
        elif endpoint == "analyze-mutual-fund":
            return run_analysis(payload["ticker"], "mutual_fund")
        elif endpoint == "portfolio-analysis":
            return portfolio_analysis(PortfolioRequest(stocks=payload["stocks"]))
        elif endpoint == "compare-stocks":
            return compare_stocks(CompareStocksRequest(stock1=payload["stock1"], stock2=payload["stock2"]))
    except Exception as e:
        st.error(f"❌ Error analyzing data: {e}")
        return None

def plot_premium_chart(ticker: str):
    """Generates a beautiful Dark Mode Plotly Candlestick Chart."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        if not hist.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'],
                increasing_line_color='#00E676', decreasing_line_color='#FF5252'
            )])
            fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              margin=dict(l=0, r=0, t=40, b=0), xaxis_rangeslider_visible=False,
                              title=dict(text=f"{ticker} — 6-Month Price Action", font=dict(color='#E0E6ED', size=20)))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No price history found for this ticker.")
    except Exception as e:
        st.warning(f"Could not load chart: {e}")

def render_premium_analysis(data: dict, asset_type: str, ticker: str):
    """Refactored rendering logic to inject flawlessly into both standard tabs and the chat tab!"""
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Final Conviction Score", f"{data['scores']['final']}/10", delta="AI Verified")
    with col2:
        rec = data['recommendation']
        if "Buy" in rec: st.metric("AI Verdict", rec, delta="Upgraded")
        elif "Avoid" in rec: st.metric("AI Verdict", rec, delta="-Downgraded", delta_color="inverse")
        else: st.metric("AI Verdict", rec)
    with col3: st.metric("Model Confidence", f"{int(data['confidence']*100)}%")
        
    fund_data = data.get("fundamental_data", {})
    if fund_data and "error" not in fund_data:
        st.markdown("### 📊 Asset Metrics")
        m1, m2, m3, m4 = st.columns(4)
        if asset_type == "stock":
            m1.metric("PE Ratio", f"{fund_data.get('trailingPE', 'N/A')}")
            m2.metric("Revenue Growth", f"{fund_data.get('revenueGrowth', 'N/A')}")
            m3.metric("Profit Margin", f"{fund_data.get('profitMargins', 'N/A')}")
            m4.metric("ROE", f"{fund_data.get('returnOnEquity', 'N/A')}")
        else:
            m1.metric("Yield", f"{fund_data.get('yield', 'N/A')}")
            m2.metric("Expense Ratio", f"{fund_data.get('expenseRatio', 'N/A')}")
            m3.metric("YTD Return", f"{fund_data.get('ytdReturn', 'N/A')}")
            m4.metric("MorningStar Rating", f"{fund_data.get('morningStarRating', 'N/A')} / 5")

    st.markdown("### 🧠 Executive PM Summary")
    st.info(data['summary'])
    
    st.markdown("### 📡 Agent Telemetry Sub-Scores")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Fundamental Agent", f"{data['scores']['fundamental']}/10")
    sc2.metric("Technical Agent", f"{data['scores']['technical']}/10")
    sc3.metric("Sentiment Agent", f"{data['scores']['sentiment']}/10")
    
    st.markdown("---")
    plot_premium_chart(ticker)

# --- ROUTES ---

if page == "💬 AI Chat Assistant":
    st.title("🙋‍♂️ AI Research Assistant")
    st.markdown("Chat with the LangGraph equity desk in plain English. Just ask 'How is Tata Motors doing?'")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display previous messages and their embedded UI analyses
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("analysis_data"):
                render_premium_analysis(msg["analysis_data"], msg.get("asset_type"), msg.get("ticker"))
                
    # Accept user input
    if prompt := st.chat_input("E.g., How is Reliance doing?"):
        # Add user string to history
        st.session_state.messages.append({"role": "user", "content": prompt, "analysis_data": None})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Extracting parameters and querying LangGraph..."):
                try:
                    from src.api.main import extract_ticker, ChatIntentRequest
                    intent = extract_ticker(ChatIntentRequest(query=prompt))
                    st.markdown(intent["reply"])
                    
                    if intent.get("ticker"):
                        ticker = intent["ticker"]
                        asset_type = intent["asset_type"]
                        endpoint = "analyze-mutual-fund" if asset_type == "mutual_fund" else "analyze-stock"
                        
                        data = fetch_analysis(endpoint, {"ticker": ticker})
                        if data:
                            render_premium_analysis(data, asset_type, ticker)
                            # Save state
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": intent["reply"],
                                "analysis_data": data,
                                "ticker": ticker,
                                "asset_type": asset_type
                            })
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": "Failed to pull analysis data."})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": intent["reply"]})
                        
                except Exception as e:
                    st.error(f"System Error: {e}")

elif page == "🔍 Stock Analyzer":
    st.markdown("## Intelligence Analyzer")
    ticker = st.text_input("ENTER TICKER (e.g., RELIANCE.NS, TSLA)", "RELIANCE.NS")
    
    if st.button("RUN INTELLIGENCE PROTOCOL", use_container_width=True):
        with st.spinner("AI Agents synthesizing market data..."):
            data = fetch_analysis("analyze-stock", {"ticker": ticker})
        if data:
            render_premium_analysis(data, "stock", ticker)

elif page == "📈 Mutual Fund Analyzer":
    st.markdown("## Mutual Fund Intelligence")
    ticker = st.text_input("ENTER MUTUAL FUND TICKER (e.g., VFINX, 0P00005WLZ.BO)", "VFINX")
    
    if st.button("RUN MUTUAL FUND PROTOCOL", use_container_width=True):
        with st.spinner("AI Agents synthesizing market data..."):
            data = fetch_analysis("analyze-mutual-fund", {"ticker": ticker})
        if data:
            render_premium_analysis(data, "mutual_fund", ticker)

elif page == "📊 Portfolio Dashboard":
    st.markdown("## Portfolio Intelligence")
    stocks_input = st.text_input("Enter Tickers (comma-separated)", "RELIANCE.NS, TATAMOTORS.NS, INFY.NS")
    
    if st.button("SCAN PORTFOLIO", use_container_width=True):
        tickers = [s.strip() for s in stocks_input.split(",") if s.strip()]
        with st.spinner("Scanning Portfolio..."):
            data = fetch_analysis("portfolio-analysis", {"stocks": tickers})
        if data:
            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            c1.metric("Portfolio Average", f"{data['portfolio_average_score']}/10")
            c2.metric("⭐ Alpha Performer", data['best_performer'], delta="Top Tier")
            c3.metric("⚠️ Liability", data['worst_performer'], delta="-Risk Detected", delta_color="inverse")
            
            st.markdown("---")
            st.markdown("### 📋 Deep Scans")
            for item in data['individual_analyses']:
                with st.expander(f"**{item['ticker']}**  —  Verdict: **{item['recommendation']}**  ({item['scores']['final']}/10)"):
                    st.write(item['summary'])

elif page == "⚖️ Compare Stocks":
    st.markdown("## Head-to-Head Alpha Screen")
    colA, colB = st.columns(2)
    with colA: stock1 = st.text_input("Asset Alpha", "TATAMOTORS.NS")
    with colB: stock2 = st.text_input("Asset Beta", "M&M.NS")
        
    if st.button("RUN COMBAT PROTOCOL", use_container_width=True):
        with st.spinner(f"Comparing {stock1} vs {stock2}..."):
            data = fetch_analysis("compare-stocks", {"stock1": stock1, "stock2": stock2})
        if data:
            st.success(f"🏆 **WINNER OVERALL**: {data['winner']}")
            st.markdown(f"**Direct Assessment:** {data['summary']}")
            
            st.markdown("---")
            s1_data = data["comparison"][stock1]
            s2_data = data["comparison"][stock2]
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"### {stock1}")
                st.metric("Final Score", f"{s1_data['scores']['final']}/10")
                st.metric("Recommendation", s1_data['recommendation'])
                st.info(s1_data['summary'])
            with c2:
                st.markdown(f"### {stock2}")
                st.metric("Final Score", f"{s2_data['scores']['final']}/10")
                st.metric("Recommendation", s2_data['recommendation'])
                st.info(s2_data['summary'])
