import yfinance as yf
import pandas as pd

data = yf.download("AAPL", start="2020-01-01", end="2025-01-01")
print(data.head())
