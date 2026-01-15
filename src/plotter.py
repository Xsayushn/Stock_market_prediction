import matplotlib.pyplot as plt
import pandas as pd

def plot_close_price(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["Close"])
    ax.set_title("Closing Price Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close Price")
    return fig

def plot_predictions(y_test, pred):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(y_test.values, label="Actual")
    ax.plot(pred, label="Predicted")
    ax.set_title("Prediction vs Actual")
    ax.legend()
    return fig
