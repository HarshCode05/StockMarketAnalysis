# 📊 NIFTY 50 Smart Screener

A real-time stock screening and analysis dashboard for all **NIFTY 50** stocks built with **Python** and **Streamlit**. Get live BUY/SELL/HOLD signals, candlestick charts, RSI analysis, and news sentiment — all in one place.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?style=flat-square&logo=streamlit)
![yFinance](https://img.shields.io/badge/yFinance-live%20data-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 🖥️ Live Demo

> 🔗https://stockmarket-nifty50-analysis.streamlit.app/

---

## ✨ Features

### 🏠 Dashboard
- Live summary metrics — total stocks, BUY / SELL / HOLD counts, average RSI
- Top 5 **Gainers** and **Losers** over the last month
- Sector-wise signal breakdown table with color-coded heatmap

### 🔍 Stock Screener
- Screen all 50 NIFTY stocks with real-time signals
- Filter by **Sector**, **Signal** (BUY/SELL/HOLD), and **RSI Range**
- Export filtered results to **CSV** with one click

### 📈 Stock Detail
- **Candlestick chart** for any stock (6-month view)
- **RSI + Moving Averages** chart (MA20 & MA50) with overbought/oversold zones
- Live price, MA50, RSI, and signal metrics per stock

### 📰 News & Sentiment
- Fetches latest news headlines via **NewsAPI**
- **TextBlob sentiment analysis** on each headline
- Visual sentiment gauge (Bearish → Neutral → Bullish)

---

## 🧠 Signal Logic

| Condition | Signal |
|---|---|
| Price > MA50 **and** RSI < 70 | 🟢 **BUY** |
| Price < MA50 **and** RSI > 30 | 🔴 **SELL** |
| Everything else | 🟡 **HOLD** |

> Signals are based on 6-month historical data with 14-period RSI (EWM method).

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Python` | Core language |
| `Streamlit` | Web app framework |
| `yFinance` | Live stock data from Yahoo Finance |
| `Pandas` | Data processing & RSI computation |
| `Plotly` | Interactive candlestick & RSI charts |
| `TextBlob` | News headline sentiment analysis |
| `NewsAPI` | Fetching latest stock-related news |

---

## 📁 Project Structure

```
StockMarketAnalysis/
├── application.py   ← Main Streamlit app (all pages, logic, UI)
├── charts.py        ← Candlestick chart helper using Plotly
├── .streamlit/
│   └── secrets.toml ← API key (not committed to GitHub)
└── requirements.txt ← Python dependencies
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/HarshCode05/StockMarketAnalysis.git
cd StockMarketAnalysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your NewsAPI key

Create a file `.streamlit/secrets.toml`:
```toml
newsapi_key = "your_newsapi_key_here"
```

Get a free API key at 👉 https://newsapi.org

### 4. Run the app
```bash
streamlit run application.py
```

Open http://localhost:8501 in your browser.

---

## 📦 requirements.txt

```
streamlit
yfinance
pandas
requests
textblob
plotly
```

---

## 🌐 Deploy on Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to https://streamlit.io/cloud and sign in with GitHub
3. Click **"New app"** → select this repo → set `application.py` as main file
4. In **"Secrets"**, add:
   ```
   newsapi_key = "your_key_here"
   ```
5. Click **Deploy** — live in ~2 minutes! 🎉

---

## ⚠️ Disclaimer

> This project is built for **educational purposes only**.
> It is **not** financial advice. Do not make real investment decisions based on this tool.
> Always consult a SEBI-registered financial advisor before investing.

---

## 👨‍💻 Author

**Harsh Agrawal**
[GitHub](https://github.com/HarshCode05) ·[Email](mailto:harshagrawal050903@gmail.com)