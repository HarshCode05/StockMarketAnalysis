def top_gainers_losers(data):
    returns = data.pct_change().iloc[-1]
    
    gainers = returns.sort_values(ascending=False).head(5)
    losers = returns.sort_values().head(5)
    
    return gainers, losers