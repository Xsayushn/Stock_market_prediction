import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split

from src.data_loader import load_stock_data
from src.features import add_features, prepare_dataset
from src.model import train_model, evaluate_model, save_model, load_model, predict_next_days
from src.signals import generate_signals
from src.charts import candlestick_chart

st.set_page_config(page_title="Stock Predictor PRO", layout="wide")

st.title("📈 Stock Predictor PRO Dashboard")
st.write("✅ Candlestick + RSI + MACD + 7-day Forecast + Buy/Sell Signals + Model Save/Load")

# Sidebar
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.text_input("Stock Symbol", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
train_new = st.sidebar.checkbox("Train New Model", value=True)
forecast_days = st.sidebar.slider("Forecast Days", 1, 14, 7)

st.sidebar.markdown("---")
st.sidebar.info("Indian Stocks: use .NS like RELIANCE.NS, TCS.NS")

if st.sidebar.button("🚀 Run Dashboard"):

    # Load data
    df = load_stock_data(symbol, start=str(start_date))
    df_feat = add_features(df)
    df_signals = generate_signals(df_feat)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Charts", "🤖 Prediction", "📌 Signals"])

    # TAB 1 - Charts
    with tab1:
        st.subheader(f"📌 Candlestick Chart - {symbol}")
        fig = candlestick_chart(df_signals)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📄 Latest Data")
        st.dataframe(df_signals.tail(15), use_container_width=True)

    # TAB 2 - Prediction
    with tab2:
        st.subheader("🤖 ML Model Training & Forecast")

        X, y, final_df, feature_cols = prepare_dataset(df_feat)

        # Train/Test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        model = None

        if train_new:
            model = train_model(X_train, y_train)
            save_model(model)
            st.success("✅ Model trained and saved to models/stock_model.pkl")
        else:
            model = load_model()
            if model is None:
                st.warning("⚠️ No saved model found. Training new model now...")
                model = train_model(X_train, y_train)
                save_model(model)

        pred, mae, rmse = evaluate_model(model, X_test, y_test)

        col1, col2, col3 = st.columns(3)
        col1.metric("MAE", f"{mae:.4f}")
        col2.metric("RMSE", f"{rmse:.4f}")
        col3.metric("Data Points", f"{len(df_feat)}")

        # Predict next N days
        last_row = X.iloc[-1].values
        future_prices = predict_next_days(model, last_row, days=forecast_days)

        future_df = pd.DataFrame({
            "Day": [f"Day {i+1}" for i in range(forecast_days)],
            "Predicted Close": future_prices
        })

        st.subheader(f"📌 Next {forecast_days}-Day Forecast")
        st.dataframe(future_df, use_container_width=True)

        st.success(f"✅ Tomorrow predicted close for {symbol}: **{future_prices[0]:.2f}**")

    # TAB 3 - Signals
    with tab3:
        st.subheader("📌 Buy / Sell Signal Strategy")

        latest_signal = df_signals.iloc[-1]["Signal"]
        latest_rsi = df_signals.iloc[-1]["RSI"]
        latest_close = df_signals.iloc[-1]["Close"]

        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Close", f"{latest_close:.2f}")
        col2.metric("Latest RSI", f"{latest_rsi:.2f}")
        col3.metric("Signal", latest_signal)

        st.write("✅ Strategy Logic:")
        st.markdown("""
        - **BUY** when RSI < 30 and Close > MA20  
        - **SELL** when RSI > 70 or Close < MA20  
        - Else **HOLD**
        """)

        st.subheader("📄 Recent Signals")
        st.dataframe(df_signals[["Date", "Close", "RSI", "MA_20", "Signal"]].tail(25), use_container_width=True)

else:
    st.info("👈 Enter stock symbol, choose settings, then click **Run Dashboard**")
