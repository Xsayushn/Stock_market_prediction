import yfinance as yf
import pandas as pd

def load_stock_data(symbol: str, start="2016-01-01", end="2026-01-01") -> pd.DataFrame:
    df = yf.download(symbol, start=start, end=end, progress=False)

    if df.empty:
        raise ValueError("No data found. Check symbol like AAPL / TSLA / TCS.NS / RELIANCE.NS")

    df.reset_index(inplace=True)
    return df
