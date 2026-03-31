import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Mahesh Intraday AI Trader",
    layout="wide",
    page_icon="🚀"
)

st.title("🚀 Mahesh Intraday AI Trader")
st.markdown("**5-Minute & 15-Minute Intraday Signals | AI Score | Live Charts**")
st.caption("Data Source: Yahoo Finance (Free) | Educational Purpose Only")

# Sidebar
st.sidebar.header("📊 Settings")
symbol = st.sidebar.text_input("Stock / Index Symbol", "^NSEI", help="Examples: RELIANCE.NS, HDFCBANK.NS, INFY.NS, ^NSEI, BANKNIFTY.NS")
interval = st.sidebar.selectbox("Time Interval", ["5m", "15m"], index=0)

if st.sidebar.button("🔄 Refresh Data Now"):
    st.rerun()

# Data Fetch
@st.cache_data(ttl=60)  # Har 60 seconds mein refresh
def get_data(sym, intv):
    try:
        data = yf.download(sym, period="5d", interval=intv, progress=False)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

data = get_data(symbol, interval)

if data.empty:
    st.warning("Data nahi mila. Symbol sahi daalo ya thoda wait karo.")
else:
    # Calculate Indicators
    data['RSI'] = ta.rsi(data['Close'], length=14)
    data['MACD'] = ta.macd(data['Close'])['MACD_12_26_9']
    data['VWAP'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])

    latest = data.iloc[-1]

    # AI Smart Score Calculation
    score = 0
    reasons = []

    if latest['Close'] > latest['VWAP']:
        score += 3
        reasons.append("✅ Price above VWAP (Bullish)")
    if latest['RSI'] < 40:
        score += 3
        reasons.append("✅ RSI Oversold")
    elif latest['RSI'] > 70:
        score -= 2
        reasons.append("❌ RSI Overbought")
    if latest['MACD'] > 0:
        score += 2
        reasons.append("✅ MACD Bullish")

    # Main Dashboard
    col1, col2, col3 = st.columns(3)

    with col1:
        change = latest['Close'] - data.iloc[-2]['Close']
        st.metric("Current Price", f"₹{latest['Close']:.2f}", f"{change:.2f}")

    with col2:
        st.metric("AI Intraday Score", f"{score}/10")
        if score >= 7:
            st.success("🔥 **STRONG BUY**")
        elif score >= 4:
            st.warning("🟡 **WATCH**")
        else:
            st.error("🔴 **SELL / AVOID**")

    with col3:
        st.metric("RSI", f"{latest['RSI']:.1f}")

    # Chart
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="OHLC"
    ))

    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['VWAP'], 
        line=dict(color='orange', width=2),
        name="VWAP"
    ))

    fig.update_layout(
        title=f"{symbol} - {interval} Intraday Chart",
        height=650,
        xaxis_title="Time",
        yaxis_title="Price (₹)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Signals
    st.subheader("📌 Current Trading Signals")
    for reason in reasons:
        st.write(reason)

    st.info("**Note:** Yeh sirf educational aur practice ke liye hai. Real trading se pehle paper trading zaroor karo. Data mein thoda delay ho sakta hai.")

# Footer
st.caption(f"Last Updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')} IST")
