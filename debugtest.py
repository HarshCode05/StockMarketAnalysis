import yfinance as yf
import pandas as pd

print("=== yfinance version ===")
print(yf.__version__)

print("\n=== Single stock test ===")
df = yf.download("RELIANCE.NS", period="3mo", progress=False, auto_adjust=True)
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Empty: {df.empty}")
if not df.empty:
    print(f"Last row:\n{df.iloc[-1]}")

print("\n=== MultiIndex check ===")
print(f"Is MultiIndex: {isinstance(df.columns, pd.MultiIndex)}")

if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
    print(f"After flatten: {df.columns.tolist()}")
    print(f"Close value: {df.iloc[-1]['Close']}")
    print(f"Type: {type(df.iloc[-1]['Close'])}")

print("\n=== Multi ticker test ===")
tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
raw = yf.download(tickers, period="5d", progress=False, auto_adjust=True)
print(f"Multi shape: {raw.shape}")
print(f"Multi columns type: {type(raw.columns)}")
print(f"Multi columns: {raw.columns.tolist()[:6]}")

if isinstance(raw.columns, pd.MultiIndex):
    close = raw["Close"]
    print(f"Close shape: {close.shape}")
    print(f"Returns:\n{close.pct_change().iloc[-1]}")