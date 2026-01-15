import pandas as pd

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ✅ Ensure these are Series (not DataFrames)
    close = df["Close"].squeeze()
    ma20 = df["MA_20"].squeeze()
    rsi = df["RSI"].squeeze()

    df["Signal"] = "HOLD"

    buy_condition = (rsi < 30) & (close > ma20)
    sell_condition = (rsi > 70) | (close < ma20)

    df.loc[buy_condition, "Signal"] = "BUY ✅"
    df.loc[sell_condition, "Signal"] = "SELL ❌"

    return df
