import pandas as pd
from src.indicators import compute_rsi, compute_macd

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["MA_10"] = df["Close"].rolling(10).mean()
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["MA_50"] = df["Close"].rolling(50).mean()

    df["Return"] = df["Close"].pct_change()
    df["Volatility"] = df["Return"].rolling(10).std()

    df["RSI"] = compute_rsi(df)
    macd, macd_signal, macd_hist = compute_macd(df)
    df["MACD"] = macd
    df["MACD_Signal"] = macd_signal
    df["MACD_Hist"] = macd_hist

    df = df.dropna()
    return df

def prepare_dataset(df: pd.DataFrame):
    df = df.copy()
    df["Target"] = df["Close"].shift(-1)
    df = df.dropna()

    feature_cols = [
        "Close", "MA_10", "MA_20", "MA_50",
        "Return", "Volatility",
        "RSI", "MACD", "MACD_Signal", "MACD_Hist"
    ]

    X = df[feature_cols]
    y = df["Target"]

    return X, y, df, feature_cols
