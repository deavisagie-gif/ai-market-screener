# AI-Powered Stock, Index & Gold Screener (Streamlit)
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

st.set_page_config(page_title="AI Market Screener", layout="wide")
st.title("📈 AI-Powered Market Screener")
st.write("Screens high-growth stocks, NASDAQ 100, Dow Jones & Gold using fundamentals + technicals")

# ---------------------------------
# Tickers (Stocks + Indices + Gold)
# ---------------------------------
TICKERS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "AMZN": "Amazon",
    "META": "Meta",
    "^NDX": "NASDAQ 100",
    "^DJI": "Dow Jones",
    "GC=F": "Gold Futures"
}

LOOKBACK = "1y"

# ---------------------------------
# Indicator Calculations
# ---------------------------------
def compute_indicators(df):
    df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()
    df["SMA50"] = SMAIndicator(df["Close"], window=50).sma_indicator()
    df["SMA200"] = SMAIndicator(df["Close"], window=200).sma_indicator()
    df["VOL_MA"] = df["Volume"].rolling(20).mean()
    return df

# ---------------------------------
# AI Scoring Logic
# ---------------------------------
def score_asset(latest, info):
    score = 0

    # Fundamentals (if available)
    pe = info.get("trailingPE")
    rev_growth = info.get("revenueGrowth", 0)
    roe = info.get("returnOnEquity", 0)

    if pe and pe < 35:
        score += 10
    if rev_growth and rev_growth > 0.15:
        score += 10
    if roe and roe > 0.15:
        score += 5

    # Momentum
    if 40 < latest["RSI"] < 70:
        score += 10

    # Trend
    if latest["Close"] > latest["SMA50"] > latest["SMA200"]:
        score += 15

    # Volume
    if latest["Volume"] > 1.5 * latest["VOL_MA"]:
        score += 10

    return score

# ---------------------------------
# Screener Execution
# ---------------------------------
st.sidebar.header("⚙️ Settings")
run = st.sidebar.button("Run Screener")

if run:
    results = []

    for ticker, name in TICKERS.items():
        try:
            asset = yf.Ticker(ticker)
            df = asset.history(period=LOOKBACK)

            if len(df) < 200:
                continue

            df = compute_indicators(df)
            latest = df.iloc[-1]
            info = asset.info

            score = score_asset(latest, info)

            results.append({
                "Asset": name,
                "Ticker": ticker,
                "Score": score,
                "Price": round(latest["Close"], 2),
                "RSI": round(latest["RSI"], 1),
                "P/E": info.get("trailingPE"),
                "Revenue Growth": info.get("revenueGrowth"),
            })
        except Exception:
            continue

    df_results = pd.DataFrame(results).sort_values("Score", ascending=False)

    st.subheader("🏆 Ranked Opportunities")
    st.dataframe(df_results, use_container_width=True)

    # Highlight Top Pick
    if not df_results.empty:
        top = df_results.iloc[0]
        st.success(f"🔥 Top Opportunity: {top['Asset']} ({top['Ticker']}) | Score: {top['Score']}")

# ---------------------------------
# Footer
# ---------------------------------
st.markdown("---")
st.caption("AI Screener | Fundamentals + Technicals | Educational Use Only")
