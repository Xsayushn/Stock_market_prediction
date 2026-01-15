import yfinance as yf
import pandas as pd

def load_stock_data(symbol: str, start="2018-01-01", end=None) -> pd.DataFrame:
    df = yf.download(symbol, start=start, end=end, progress=False)

    if df.empty:
        raise ValueError("No data found. Check symbol like AAPL / TSLA / TCS.NS / RELIANCE.NS")

    # ✅ Fix MultiIndex columns issue
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.reset_index(inplace=True)
    return df
