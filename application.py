import time
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from textblob import TextBlob
import charts

st.set_page_config(
    page_title="NIFTY 50 Smart Screener",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# THEME A — Slate Clean CSS
# White cards, indigo accents, crisp typography
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Page background */
.stApp {
    background: #f0f2f8 !important;
}

/* Remove default streamlit padding */
.main .block-container {
    padding-top: 1.8rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e3e6f0 !important;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.2rem !important;
}

/* Headings */
h1, h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: #1a1f36 !important;
    letter-spacing: -.02em !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e3e6f0 !important;
    border-radius: 12px !important;
    padding: 18px 20px !important;
    transition: box-shadow .2s, transform .2s !important;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 16px rgba(57,73,171,0.08) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] > div {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: .08em !important;
    color: #9e9ea8 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #1a1f36 !important;
    letter-spacing: -.03em !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid #e3e6f0 !important;
    overflow: hidden !important;
    background: #fff !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: #f0f2f8 !important;
    border: 1px solid #d8dce8 !important;
    border-radius: 8px !important;
    color: #1a1f36 !important;
}

/* Radio nav */
[data-testid="stRadio"] label {
    padding: 9px 12px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    transition: all .15s !important;
    margin-bottom: 2px !important;
    display: block !important;
}
[data-testid="stRadio"] label:has(input:checked) {
    background: #e8eaf6 !important;
    color: #3949ab !important;
}
[data-testid="stRadio"] label:hover:not(:has(input:checked)) {
    background: #f0f2f8 !important;
    color: #1a1f36 !important;
}
[data-testid="stRadio"] input { display: none !important; }
[data-testid="stRadio"] > div { gap: 2px !important; }

/* Buttons */
.stButton button {
    background: #e8eaf6 !important;
    border: 1px solid #c5cae9 !important;
    border-radius: 8px !important;
    color: #3949ab !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all .15s !important;
}
.stButton button:hover {
    background: #c5cae9 !important;
    box-shadow: 0 2px 8px rgba(57,73,171,0.15) !important;
}

/* Download button */
.stDownloadButton button {
    background: #e8f5e9 !important;
    border: 1px solid #a5d6a7 !important;
    color: #2e7d32 !important;
    border-radius: 8px !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    letter-spacing: .05em !important;
    color: #9e9ea8 !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #3949ab !important;
    border-bottom: 2px solid #3949ab !important;
}

/* Slider */
[data-testid="stSlider"] .rc-slider-track { background: #3949ab !important; }
[data-testid="stSlider"] .rc-slider-handle {
    border-color: #3949ab !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 2px #3949ab !important;
}

/* Divider */
hr { border-color: #e3e6f0 !important; margin: 1.2rem 0 !important; }

/* Caption */
.stCaption {
    color: #9e9ea8 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
}

/* Progress bar */
[data-testid="stProgressBar"] > div > div {
    background: #3949ab !important;
    border-radius: 4px !important;
}

/* Info / warning / error */
.stAlert {
    border-radius: 10px !important;
    border-left: 3px solid !important;
}

/* Spinner */
[data-testid="stSpinner"] p { color: #3949ab !important; }

/* Plotly transparent bg */
.js-plotly-plot { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# NIFTY 50 — sector-wise
# =========================
NIFTY50_SECTORS = {
    "Financial Services":   ["HDFCBANK.NS","ICICIBANK.NS","KOTAKBANK.NS","AXISBANK.NS","SBIN.NS","BAJFINANCE.NS","BAJAJFINSV.NS","HDFCLIFE.NS","SBILIFE.NS","SHRIRAMFIN.NS","JIOFIN.NS"],
    "Information Technology": ["TCS.NS","INFY.NS","HCLTECH.NS","WIPRO.NS","TECHM.NS"],
    "Oil, Gas & Energy":    ["RELIANCE.NS","ONGC.NS","COALINDIA.NS","NTPC.NS","POWERGRID.NS"],
    "Automobile":           ["MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS","EICHERMOT.NS","TMPV.NS"],
    "Fast Moving Consumer Goods": ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS","TATACONSUM.NS"],
    "Healthcare":           ["SUNPHARMA.NS","CIPLA.NS","DRREDDY.NS","APOLLOHOSP.NS","MAXHEALTH.NS"],
    "Metals & Mining":      ["HINDALCO.NS","JSWSTEEL.NS","TATASTEEL.NS","ADANIENT.NS"],
    "Construction & Capital Goods": ["LT.NS","GRASIM.NS","ULTRACEMCO.NS","BEL.NS"],
    "Consumer Durables":    ["ASIANPAINT.NS","TITAN.NS"],
    "Telecommunication":    ["BHARTIARTL.NS"],
    "Services":             ["ADANIPORTS.NS","INDIGO.NS"],
}
ALL_STOCKS    = [s for v in NIFTY50_SECTORS.values() for s in v]
TICKER_SECTOR = {t: sec for sec, tickers in NIFTY50_SECTORS.items() for t in tickers}

SECTOR_COLORS = {
    "Financial Services":"#3949ab","Information Technology":"#0288d1",
    "Oil, Gas & Energy":"#f57c00","Automobile":"#7b1fa2",
    "Fast Moving Consumer Goods":"#c62828","Healthcare":"#2e7d32",
    "Metals & Mining":"#546e7a","Construction & Capital Goods":"#ad1457",
    "Consumer Durables":"#00838f","Telecommunication":"#558b2f","Services":"#6d4c41",
}

API_KEY = st.secrets["newsapi_key"]

# =========================
# HELPERS
# =========================
def flatten_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def compute_rsi(series, period=14):
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
    rs       = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def download_with_retry(ticker, period="6mo", retries=3, delay=1.5):
    for i in range(retries):
        try:
            df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
            df = flatten_df(df)
            if not df.empty:
                return df
        except Exception:
            pass
        if i < retries - 1:
            time.sleep(delay)
    return pd.DataFrame()

def get_sentiment(stock):
    try:
        name     = stock.replace(".NS","")
        url      = f"https://newsapi.org/v2/everything?q={name}&language=en&sortBy=publishedAt&apiKey={API_KEY}"
        articles = requests.get(url, timeout=5).json().get("articles",[])[:5]
        scores   = [TextBlob(a["title"]).sentiment.polarity for a in articles if a.get("title")]
        return round(sum(scores)/len(scores),2) if scores else 0.0
    except Exception:
        return 0.0

# HTML helpers
def signal_badge(signal):
    cfg = {
        "BUY":  ("#e8f5e9","#1b5e20","#a5d6a7"),
        "SELL": ("#ffebee","#b71c1c","#ef9a9a"),
        "HOLD": ("#fff8e1","#e65100","#ffcc80"),
    }
    bg,fg,bd = cfg.get(signal,("#f5f5f5","#333","#ccc"))
    return (f'<span style="background:{bg};color:{fg};border:1px solid {bd};'
            f'padding:2px 9px;border-radius:4px;font-size:11px;font-weight:700;'
            f'letter-spacing:.04em;font-family:\'JetBrains Mono\',monospace">{signal}</span>')

def sector_chip(sector):
    c = SECTOR_COLORS.get(sector,"#546e7a")
    return (f'<span style="background:{c}18;color:{c};border:1px solid {c}40;'
            f'padding:2px 10px;border-radius:4px;font-size:11px;font-weight:600">{sector}</span>')

def stat_pill(label, val, color):
    return (f'<div style="background:{color}12;border:1px solid {color}30;'
            f'border-radius:8px;padding:10px 14px;text-align:center">'
            f'<div style="font-size:20px;font-weight:700;color:{color}">{val}</div>'
            f'<div style="font-size:9px;color:{color}99;font-weight:700;letter-spacing:.07em;margin-top:2px">{label}</div>'
            f'</div>')

def page_header(title, sub=""):
    sub_html = f'<p style="font-size:12px;color:#9e9ea8;font-family:\'JetBrains Mono\',monospace;margin:3px 0 0">{sub}</p>' if sub else ""
    st.markdown(f'<div style="margin-bottom:1.4rem"><h1 style="font-size:22px;font-weight:700;color:#1a1f36;letter-spacing:-.02em;margin:0">{title}</h1>{sub_html}</div>', unsafe_allow_html=True)

def card_title(label, dot_color="#3949ab"):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:12px">'
        f'<div style="width:5px;height:5px;border-radius:50%;background:{dot_color}"></div>'
        f'<span style="font-size:10px;font-weight:700;letter-spacing:.09em;color:#9e9ea8">{label}</span>'
        f'</div>', unsafe_allow_html=True)

# =========================
# DATA (cached)
# =========================
@st.cache_data(ttl=1800)
def fetch_screener_data():
    results = []
    for stock in ALL_STOCKS:
        try:
            df = download_with_retry(stock, period="6mo")
            if df.empty or len(df) < 50: continue
            df = df.loc[:,~df.columns.duplicated()]
            if "Close" not in df.columns: continue
            df["MA50"] = df["Close"].rolling(50).mean()
            df["RSI"]  = compute_rsi(df["Close"])
            latest = df.iloc[-1]
            price,ma50,rsi = float(latest["Close"]),float(latest["MA50"]),float(latest["RSI"])
            if any(pd.isna(v) for v in [price,ma50,rsi]): continue
            if price > ma50 and rsi < 70:   signal = "BUY"
            elif price < ma50 and rsi > 30: signal = "SELL"
            else:                           signal = "HOLD"
            results.append({"Stock":stock,"Sector":TICKER_SECTOR.get(stock,"Other"),
                            "Price":round(price,2),"MA50":round(ma50,2),
                            "RSI":round(rsi,2),"Signal":signal})
        except Exception: continue
    return pd.DataFrame(results)

@st.cache_data(ttl=1800)
def fetch_gainers_losers():
    try:
        raw     = yf.download(ALL_STOCKS, period="1mo", progress=False, auto_adjust=True)
        close   = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        returns = close.pct_change().iloc[-1].dropna()
        return returns.sort_values(ascending=False).head(5), returns.sort_values().head(5)
    except Exception:
        return pd.Series(dtype=float), pd.Series(dtype=float)

@st.cache_data(ttl=900)
def fetch_chart_data(ticker):
    return download_with_retry(ticker, period="6mo")

# =========================
# LOAD
# =========================
with st.spinner("Loading NIFTY 50 data..."):
    df_screen       = fetch_screener_data()
    gainers, losers = fetch_gainers_losers()

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding-bottom:16px;border-bottom:1px solid #e3e6f0;margin-bottom:14px">
      <div style="width:32px;height:32px;background:#e8eaf6;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px">📊</div>
      <div>
        <div style="font-size:13px;font-weight:700;color:#1a1f36;letter-spacing:.02em">NIFTY 50</div>
        <div style="font-size:9px;color:#9e9ea8;letter-spacing:.09em;font-weight:600">SMART SCREENER</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("nav", [
        "🏠  Dashboard",
        "🔍  Screener",
        "📈  Stock Detail",
        "📰  News & Sentiment"
    ], label_visibility="collapsed")

    st.markdown('<div style="font-size:9px;font-weight:700;letter-spacing:.1em;color:#c5cae9;padding:16px 0 8px">FILTERS</div>', unsafe_allow_html=True)

    selected_sector  = st.selectbox("Sector", ["All Sectors"]+sorted(NIFTY50_SECTORS.keys()), label_visibility="collapsed")
    selected_signal  = st.selectbox("Signal", ["All","BUY","SELL","HOLD"], label_visibility="collapsed")
    rsi_min, rsi_max = st.slider("RSI Range", 0, 100, (0,100), label_visibility="collapsed")

    st.divider()

    if not df_screen.empty:
        bc = len(df_screen[df_screen["Signal"]=="BUY"])
        sc = len(df_screen[df_screen["Signal"]=="SELL"])
        hc = len(df_screen[df_screen["Signal"]=="HOLD"])
        st.markdown(
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:12px">'
            f'{stat_pill("BUY", bc, "#2e7d32")}'
            f'{stat_pill("SELL", sc, "#c62828")}'
            f'{stat_pill("HOLD", hc, "#e65100")}'
            f'</div>', unsafe_allow_html=True)

    if st.button("⟳  Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"  {len(ALL_STOCKS)} stocks · {len(NIFTY50_SECTORS)} sectors")

# =========================
# FILTERS
# =========================
df_f = df_screen.copy()
if selected_sector != "All Sectors" and not df_f.empty:
    df_f = df_f[df_f["Sector"]==selected_sector]
if selected_signal != "All" and not df_f.empty:
    df_f = df_f[df_f["Signal"]==selected_signal]
if not df_f.empty:
    df_f = df_f[(df_f["RSI"]>=rsi_min)&(df_f["RSI"]<=rsi_max)]

# =========================
# PAGE: DASHBOARD
# =========================
if "Dashboard" in page:
    page_header("NIFTY 50 Dashboard", "● Live · NSE India")

    if df_screen.empty:
        st.error("Data not available."); st.stop()
        st.stop()

    total   = len(df_screen)
    buys    = len(df_screen[df_screen["Signal"]=="BUY"])
    sells   = len(df_screen[df_screen["Signal"]=="SELL"])
    holds   = len(df_screen[df_screen["Signal"]=="HOLD"])
    avg_rsi = round(df_screen["RSI"].mean(),1)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("TOTAL STOCKS", total)
    c2.metric("BUY SIGNALS",  buys)
    c3.metric("SELL SIGNALS", sells)
    c4.metric("HOLD SIGNALS", holds)
    c5.metric("AVG RSI",      avg_rsi)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        card_title("TOP GAINERS · 1 MONTH", "#2e7d32")
        if not gainers.empty:
            st.dataframe(
                pd.DataFrame({"Stock":gainers.index,"Return":gainers.map("{:+.2%}".format).values}),
                use_container_width=True, hide_index=True)
        else:
            st.info("Data unavailable")

    with col2:
        card_title("TOP LOSERS · 1 MONTH", "#c62828")
        if not losers.empty:
            st.dataframe(
                pd.DataFrame({"Stock":losers.index,"Return":losers.map("{:+.2%}".format).values}),
                use_container_width=True, hide_index=True)
        else:
            st.info("Data unavailable")

    st.divider()
    card_title("SECTOR-WISE SIGNAL BREAKDOWN", "#3949ab")

    sec_sum = df_screen.groupby(["Sector","Signal"]).size().unstack(fill_value=0).reset_index()
    for c in ["BUY","SELL","HOLD"]:
        if c not in sec_sum.columns: sec_sum[c] = 0
    sec_sum["Total"] = sec_sum[["BUY","SELL","HOLD"]].sum(axis=1)
    sec_sum = sec_sum[["Sector","BUY","SELL","HOLD","Total"]].sort_values("BUY", ascending=False)

    st.dataframe(
        sec_sum.style
            .background_gradient(subset=["BUY"],  cmap="Greens")
            .background_gradient(subset=["SELL"], cmap="Reds")
            .background_gradient(subset=["HOLD"], cmap="YlOrBr"),
        use_container_width=True, hide_index=True)

# =========================
# PAGE: SCREENER
# =========================
elif "Screener" in page:
    page_header("Stock Screener", f"{len(df_f)} stocks · {selected_sector} · Signal: {selected_signal} · RSI {rsi_min}–{rsi_max}")

    if df_screen.empty:
        st.error("Data not available."); st.stop()

    if df_f.empty:
        st.warning("No stocks match the selected filters.")
    else:
        def color_sig(val):
            if val=="BUY":  return "color:#1b5e20;font-weight:700"
            if val=="SELL": return "color:#b71c1c;font-weight:700"
            return "color:#e65100;font-weight:700"

        st.dataframe(
            df_f.style.map(color_sig, subset=["Signal"]),
            use_container_width=True, hide_index=True,
            column_config={
                "RSI":   st.column_config.ProgressColumn("RSI",   min_value=0, max_value=100, format="%.1f"),
                "Price": st.column_config.NumberColumn("Price ₹", format="₹%.2f"),
                "MA50":  st.column_config.NumberColumn("MA50 ₹",  format="₹%.2f"),
            })

        csv = df_f.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️  Export CSV", csv, "screener.csv", "text/csv")

# =========================
# PAGE: STOCK DETAIL
# =========================
elif "Stock Detail" in page:
    page_header("Stock Detail")

    if df_screen.empty:
        st.error("Data not available."); st.stop()

    stock_list   = df_f["Stock"].tolist() if not df_f.empty else df_screen["Stock"].tolist()
    stock_choice = st.selectbox("Stock select karo", stock_list)
    row          = df_screen[df_screen["Stock"]==stock_choice]
    if row.empty:
        st.warning("Data not available for the selected stock."); st.stop()
    row = row.iloc[0]

    sector = TICKER_SECTOR.get(stock_choice,"—")
    st.markdown(f'<div style="margin-bottom:14px">{sector_chip(sector)}</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("PRICE",  f"₹{row['Price']}")
    c2.metric("MA50",   f"₹{row['MA50']}")
    c3.metric("RSI",    f"{row['RSI']}")
    c4.metric("SIGNAL", row["Signal"])

    st.divider()

    tab1, tab2 = st.tabs(["🕯️  Candlestick", "📉  RSI & Moving Averages"])
    chart_data  = fetch_chart_data(stock_choice)

    CHART_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fafbff",
        font=dict(family="JetBrains Mono",color="#6b7280",size=11),
        xaxis=dict(gridcolor="#e3e6f0",showgrid=True,linecolor="#e3e6f0"),
        yaxis=dict(gridcolor="#e3e6f0",showgrid=True,linecolor="#e3e6f0"),
        height=460,
    )

    with tab1:
        if not chart_data.empty:
            fig = charts.plot_candlestick(chart_data)
            fig.update_layout(
                title=dict(text=f"{stock_choice} — 6 Month", font=dict(family="Inter",size=13,color="#1a1f36")),
                **CHART_LAYOUT)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Data not available for chart")

    with tab2:
        if not chart_data.empty:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots

            chart_data["MA20"] = chart_data["Close"].rolling(20).mean()
            chart_data["MA50"] = chart_data["Close"].rolling(50).mean()
            chart_data["RSI"]  = compute_rsi(chart_data["Close"])

            fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                 row_heights=[0.65,0.35], vertical_spacing=0.06)
            fig2.add_trace(go.Scatter(x=chart_data.index, y=chart_data["Close"],
                           name="Close", line=dict(color="#3949ab",width=2)), row=1,col=1)
            fig2.add_trace(go.Scatter(x=chart_data.index, y=chart_data["MA20"],
                           name="MA20", line=dict(color="#f57c00",width=1.2,dash="dot")), row=1,col=1)
            fig2.add_trace(go.Scatter(x=chart_data.index, y=chart_data["MA50"],
                           name="MA50", line=dict(color="#ad1457",width=1.2,dash="dot")), row=1,col=1)
            fig2.add_trace(go.Scatter(x=chart_data.index, y=chart_data["RSI"],
                           name="RSI",  line=dict(color="#0288d1",width=1.5)), row=2,col=1)
            fig2.add_hline(y=70, line_dash="dash", line_color="#ef9a9a", row=2, col=1)
            fig2.add_hline(y=30, line_dash="dash", line_color="#a5d6a7", row=2, col=1)
            fig2.add_hrect(y0=30, y1=70, fillcolor="rgba(57,73,171,0.03)", line_width=0, row=2, col=1)
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fafbff",
                font=dict(family="JetBrains Mono",color="#6b7280",size=11),
                xaxis2=dict(gridcolor="#e3e6f0"), yaxis=dict(gridcolor="#e3e6f0"),
                yaxis2=dict(gridcolor="#e3e6f0",range=[0,100]),
                legend=dict(bgcolor="#fff",bordercolor="#e3e6f0",borderwidth=1,font=dict(size=11)),
                height=500)
            st.plotly_chart(fig2, use_container_width=True)

# =========================
# PAGE: NEWS & SENTIMENT
# =========================
elif "News" in page:
    page_header("News & Sentiment")

    stock_list   = df_screen["Stock"].tolist() if not df_screen.empty else ALL_STOCKS
    stock_choice = st.selectbox("Stock select karo", stock_list)

    with st.spinner("Fetching news..."):
        sentiment = get_sentiment(stock_choice)

    score_color = "#2e7d32" if sentiment>0.1 else ("#c62828" if sentiment<-0.1 else "#e65100")
    label       = "POSITIVE" if sentiment>0.1 else ("NEGATIVE" if sentiment<-0.1 else "NEUTRAL")
    sentiment_pct = int((sentiment+1)/2*100)

    s1, s2 = st.columns([1,3])
    with s1:
        st.markdown(
            f'<div style="background:{score_color}0d;border:1px solid {score_color}30;'
            f'border-radius:12px;padding:20px;text-align:center">'
            f'<div style="font-size:32px;font-weight:700;color:{score_color}">{sentiment}</div>'
            f'<div style="font-size:9px;letter-spacing:.1em;color:{score_color};margin-top:6px;font-weight:700">{label}</div>'
            f'</div>', unsafe_allow_html=True)

    with s2:
        st.markdown('<p style="font-size:10px;font-weight:700;letter-spacing:.08em;color:#9e9ea8;margin-bottom:8px">SENTIMENT GAUGE</p>', unsafe_allow_html=True)
        st.progress(sentiment_pct)
        st.caption("−1 = Bearish  ·  0 = Neutral  ·  +1 = Bullish")

    st.divider()
    card_title(f"LATEST HEADLINES — {stock_choice.replace('.NS','')}", "#3949ab")

    try:
        name     = stock_choice.replace(".NS","")
        url      = f"https://newsapi.org/v2/everything?q={name}&language=en&sortBy=publishedAt&pageSize=8&apiKey={API_KEY}"
        articles = requests.get(url, timeout=5).json().get("articles",[])
        if articles:
            for art in articles:
                title  = art.get("title","")
                source = art.get("source",{}).get("name","")
                link   = art.get("url","#")
                pub    = art.get("publishedAt","")[:10]
                pol    = TextBlob(title).sentiment.polarity if title else 0
                dot_c  = "#2e7d32" if pol>0.1 else ("#c62828" if pol<-0.1 else "#bdbdbd")
                st.markdown(f"""
                <div style="display:flex;gap:12px;padding:12px 0;border-bottom:1px solid #f0f2f8;align-items:flex-start">
                  <div style="width:6px;height:6px;border-radius:50%;background:{dot_c};margin-top:5px;flex-shrink:0"></div>
                  <div>
                    <a href="{link}" style="color:#1a1f36;font-size:13px;font-weight:500;text-decoration:none;line-height:1.5">{title}</a>
                    <div style="font-size:10px;color:#9e9ea8;margin-top:3px;font-family:'JetBrains Mono',monospace">{source} · {pub}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No news found for this stock.")
    except Exception as e:
        st.error(f"News error: {e}")

# Footer
st.sidebar.divider()
st.sidebar.caption("⚠️ Educational use only. Not financial advice.")