import pandas as pd

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Simple strategy:
    # BUY when RSI < 30 AND Close > MA_20
    # SELL when RSI > 70 OR Close < MA_20

    df["Signal"] = "HOLD"

    buy_condition = (df["RSI"] < 30) & (df["Close"] > df["MA_20"])
    sell_condition = (df["RSI"] > 70) | (df["Close"] < df["MA_20"])

    df.loc[buy_condition, "Signal"] = "BUY ✅"
    df.loc[sell_condition, "Signal"] = "SELL ❌"

    return df
