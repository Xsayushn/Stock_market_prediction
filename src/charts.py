import plotly.graph_objects as go
from plotly.subplots import make_subplots

def candlestick_chart(df):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.55, 0.2, 0.25]
    )

    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlestick"
        ),
        row=1, col=1
    )

    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA_20"], name="MA 20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MA_50"], name="MA 50"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], name="RSI"), row=2, col=1)

    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD"], name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MACD_Signal"], name="Signal"), row=3, col=1)

    fig.update_layout(height=800, xaxis_rangeslider_visible=False)
    return fig
