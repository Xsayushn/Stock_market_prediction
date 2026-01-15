import yfinance as yf
import pandas as pd

def load_stock_data(symbol: str, start="2018-01-01", end=None) -> pd.DataFrame:
    symbol = symbol.strip().upper().replace(" ", "")

    df = yf.download(symbol, start=start, end=end, progress=False)

    # ✅ Fix MultiIndex columns
    if not df.empty and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # ✅ Retry with 1 year data if empty
    if df.empty:
        df = yf.download(symbol, period="1y", progress=False)

        if not df.empty and isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    if df.empty:
        raise ValueError(f"No data found for symbol: {symbol}")

    df.reset_index(inplace=True)
    return df
