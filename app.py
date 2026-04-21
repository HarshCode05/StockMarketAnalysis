import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from textblob import TextBlob
import charts

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="NIFTY 50 Screener",
    page_icon="📊",
    layout="wide"
)

st.title("📊 NIFTY 50 Smart Screener Dashboard")

API_KEY = st.secrets["newsapi_key"]

# =========================
# NIFTY 50 LIST
# =========================
nifty50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS"
]

# =========================
# HELPERS
# =========================
def flatten_df(df: pd.DataFrame) -> pd.DataFrame:
    """Yfinance MultiIndex columns fix"""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs       = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_sentiment(stock: str) -> float:
    try:
        ticker_name = stock.replace(".NS", "")
        url = (
            f"https://newsapi.org/v2/everything"
            f"?q={ticker_name}&language=en&sortBy=publishedAt&apiKey={API_KEY}"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        articles = response.json().get("articles", [])[:5]
        scores   = [
            TextBlob(a.get("title", "")).sentiment.polarity
            for a in articles if a.get("title")
        ]
        return round(sum(scores) / len(scores), 2) if scores else 0.0
    except Exception:
        return 0.0

# =========================
# SCREENER — cache sirf data fetch karta hai, NO UI inside
# ✅ FIX: st.progress() ko cache ke BAHAR rakha
# =========================
@st.cache_data(ttl=600)
def fetch_screener_data() -> pd.DataFrame:
    """Pure data function — no Streamlit UI calls inside"""
    results = []
    for stock in nifty50:
        try:
            df = yf.download(stock, period="3mo", progress=False, auto_adjust=True)
            df = flatten_df(df)

            if df.empty or len(df) < 50:
                continue

            df["MA50"] = df["Close"].rolling(50).mean()
            df["RSI"]  = compute_rsi(df["Close"])

            latest = df.iloc[-1]
            price  = float(latest["Close"])
            ma50   = float(latest["MA50"])
            rsi    = float(latest["RSI"])

            if pd.isna(price) or pd.isna(ma50) or pd.isna(rsi):
                continue

            if price > ma50 and rsi < 70:
                signal = "BUY"
            elif price < ma50 and rsi > 30:
                signal = "SELL"
            else:
                signal = "HOLD"

            results.append({
                "Stock":  stock,
                "Price":  round(price, 2),
                "MA50":   round(ma50, 2),
                "RSI":    round(rsi, 2),
                "Signal": signal,
            })
        except Exception:
            continue

    return pd.DataFrame(results)

# Progress bar BAHAR — Streamlit UI ke saath safe
progress_bar = st.progress(0, text="📡 Stocks scan ho rahe hain...")
df_screen    = fetch_screener_data()
progress_bar.empty()

# =========================
# TOP GAINERS / LOSERS
# ✅ FIX: MultiIndex handle kiya + empty check
# =========================
@st.cache_data(ttl=600)
def fetch_gainers_losers():
    raw = yf.download(nifty50, period="5d", progress=False, auto_adjust=True)

    # MultiIndex hoga jab multiple tickers — ["Close"] se slice karo
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]]

    returns = close.pct_change().iloc[-1].dropna()
    gainers = returns.sort_values(ascending=False).head(5)
    losers  = returns.sort_values().head(5)
    return gainers, losers

gainers, losers = fetch_gainers_losers()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Top Gainers")
    if not gainers.empty:
        st.dataframe(
            pd.DataFrame({"Stock": gainers.index, "Return": gainers.map("{:+.2%}".format).values}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Data available nahi")

with col2:
    st.subheader("🔻 Top Losers")
    if not losers.empty:
        st.dataframe(
            pd.DataFrame({"Stock": losers.index, "Return": losers.map("{:+.2%}".format).values}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Data available nahi")

st.divider()

# =========================
# SIGNAL FILTER
# =========================
st.subheader("🔍 Signal Filter")

if df_screen.empty:
    st.error("❌ Koi bhi stock data nahi mila. Internet connection ya yfinance check karo.")
    st.stop()

option      = st.selectbox("Signal filter karo", ["All", "BUY", "SELL", "HOLD"])
df_filtered = df_screen.copy()

if option != "All":
    df_filtered = df_filtered[df_filtered["Signal"] == option]

def color_signal(val):
    if val == "BUY":  return "color: #00c853; font-weight: bold"
    if val == "SELL": return "color: #ff1744; font-weight: bold"
    return "color: #ffab00; font-weight: bold"

if not df_filtered.empty:
    st.dataframe(
        df_filtered.style.map(color_signal, subset=["Signal"]),
        use_container_width=True, hide_index=True
    )
else:
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)

st.caption(f"📋 {len(df_filtered)} stocks dikh rahe hain")
st.divider()

# =========================
# STOCK DETAIL
# =========================
if df_filtered.empty:
    st.warning("⚠️ Koi stock match nahi kiya is filter se")
    st.stop()

stock_choice = st.selectbox("📌 Stock select karo detail ke liye", df_filtered["Stock"].tolist())
row          = df_filtered[df_filtered["Stock"] == stock_choice].iloc[0]

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("💰 Price",  f"₹{row['Price']}")
col_b.metric("📊 MA50",   f"₹{row['MA50']}")
col_c.metric("📉 RSI",    f"{row['RSI']}")
col_d.metric("🚦 Signal", row["Signal"])

# =========================
# CANDLESTICK CHART
# =========================
@st.cache_data(ttl=300)
def fetch_chart_data(ticker: str) -> pd.DataFrame:
    df = yf.download(ticker, period="6mo", progress=False, auto_adjust=True)
    return flatten_df(df)

chart_data = fetch_chart_data(stock_choice)

if not chart_data.empty:
    fig = charts.plot_candlestick(chart_data)
    fig.update_layout(
        title=f"{stock_choice} — 6 Month Candlestick Chart",
        template="plotly_dark",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("❌ Chart data nahi mila")

# =========================
# NEWS SENTIMENT
# =========================
st.divider()
st.subheader(f"📰 News Sentiment — {stock_choice.replace('.NS', '')}")

with st.spinner("News fetch ho rahi hai..."):
    sentiment = get_sentiment(stock_choice)

if sentiment > 0.1:
    st.success(f"✅ Positive Sentiment: **{sentiment}** (Bullish news)")
elif sentiment < -0.1:
    st.error(f"🔴 Negative Sentiment: **{sentiment}** (Bearish news)")
else:
    st.warning(f"😐 Neutral Sentiment: **{sentiment}**")

sentiment_pct = int((sentiment + 1) / 2 * 100)
st.progress(sentiment_pct, text=f"Sentiment Score: {sentiment} (−1 = bearish, +1 = bullish)")

st.divider()
st.caption("⚠️ Yeh dashboard sirf educational purpose ke liye hai. Koi bhi investment decision apni research se karo.")