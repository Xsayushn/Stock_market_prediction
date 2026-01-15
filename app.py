import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

from src.auth import require_login, logout_button
from src.data_loader import load_stock_data
from src.features import add_features, prepare_dataset
from src.signals import generate_signals
from src.charts import candlestick_chart
from src.watchlist import get_watchlist, add_to_watchlist, remove_from_watchlist
from src.models_ml import get_model, rmse
from src.forecast import forecast_next_days
from src.sentiment import analyze_news_sentiment

# ---------------- UI STYLE ----------------
st.set_page_config(page_title="Stock Predictor PRO+", layout="wide")

st.markdown("""
<style>
    .block-container {padding-top: 1.2rem;}
    [data-testid="stSidebar"] {background-color: #111827;}
    [data-testid="stSidebar"] * {color: white;}
    .stButton>button {border-radius: 12px; padding: 8px 16px;}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
require_login()
username = st.session_state["username"]

st.title("📈 Stock Predictor PRO+ Dashboard")
st.caption("✅ Watchlist + News Sentiment + Candlestick + RSI/MACD + 7-day Forecast + CSV Export + Login")

logout_button()

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Controls")

watchlist = get_watchlist(username)

default_symbol = watchlist[0] if len(watchlist) > 0 else "AAPL"
symbol = st.sidebar.text_input("Stock Symbol", default_symbol)

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
forecast_days = st.sidebar.slider("Forecast Days", 1, 14, 7)

model_name = st.sidebar.selectbox(
    "Select Model",
    ["Linear Regression", "Random Forest", "XGBoost (optional)", "LSTM (optional)"]
)

run_btn = st.sidebar.button("🚀 Run Dashboard")

# Watchlist manage
st.sidebar.markdown("---")
st.sidebar.subheader("⭐ Watchlist")

if st.sidebar.button("➕ Add to Watchlist"):
    add_to_watchlist(username, symbol)
    st.sidebar.success("Added ✅")

if watchlist:
    remove_symbol = st.sidebar.selectbox("Remove Symbol", watchlist)
    if st.sidebar.button("🗑 Remove"):
        remove_from_watchlist(username, remove_symbol)
        st.sidebar.success("Removed ✅")

st.sidebar.markdown("---")
st.sidebar.info("🇮🇳 NSE examples: RELIANCE.NS / TCS.NS / INFY.NS")

# ---------------- MAIN ----------------
if not run_btn:
    st.info("👈 Select stock + model and click **Run Dashboard**")
    st.stop()

# Load + Feature Engineering
df = load_stock_data(symbol, start=str(start_date))
df_feat = add_features(df)
df_signals = generate_signals(df_feat)

# NEWS SENTIMENT
st.subheader("📰 Live News Sentiment")
sent_avg, news_items = analyze_news_sentiment(symbol)

colA, colB, colC = st.columns(3)
colA.metric("Average Sentiment", f"{sent_avg:.3f}")

if sent_avg > 0.1:
    colB.success("✅ Positive News")
elif sent_avg < -0.1:
    colB.error("❌ Negative News")
else:
    colB.warning("⚠️ Neutral News")

colC.metric("Articles Fetched", str(len(news_items)))

if news_items:
    news_df = pd.DataFrame(news_items)[["title", "published", "sentiment", "link"]]
    st.dataframe(news_df, use_container_width=True)

st.markdown("---")

# TABS
tab1, tab2, tab3 = st.tabs(["📊 Charts", "🤖 Forecast & Export", "📌 Signals"])

# TAB 1
with tab1:
    st.subheader(f"📌 Candlestick + RSI + MACD : {symbol}")
    st.plotly_chart(candlestick_chart(df_signals), use_container_width=True)
    st.subheader("📄 Latest Data")
    st.dataframe(df_signals.tail(20), use_container_width=True)

# TAB 2
with tab2:
    st.subheader("🤖 Model Forecast (Next Days)")

    X, y, final_df, feature_cols = prepare_dataset(df_feat)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Model selection
    model = get_model(model_name)

    if model is None:
        st.error("❌ XGBoost not installed. Run: pip install xgboost")
        st.stop()

    if model == "LSTM":
        st.warning("⚠️ LSTM is optional & needs TensorFlow + sequence code. For now use RandomForest.")
        st.stop()

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    r = rmse(y_test.values, preds)

    c1, c2, c3 = st.columns(3)
    c1.metric("Model", model_name)
    c2.metric("MAE", f"{mae:.4f}")
    c3.metric("RMSE", f"{r:.4f}")

    # Future Forecast
    last_row = X.iloc[-1].values
    future_prices = forecast_next_days(model, last_row, days=forecast_days)

    future_df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(forecast_days)],
        "Predicted Close": future_prices
    })

    st.subheader(f"📌 Next {forecast_days}-day Forecast")
    st.dataframe(future_df, use_container_width=True)
    st.success(f"✅ Tomorrow predicted close: **{future_prices[0]:.2f}**")

    # Save prediction to CSV
    os.makedirs("exports", exist_ok=True)
    filename = f"exports/{symbol}_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    future_df.to_csv(filename, index=False)

    st.download_button(
        "⬇️ Download Forecast CSV",
        data=future_df.to_csv(index=False).encode("utf-8"),
        file_name=os.path.basename(filename),
        mime="text/csv"
    )

# TAB 3
with tab3:
    st.subheader("📌 Buy / Sell Signal")

    latest = df_signals.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Close", f"{latest['Close']:.2f}")
    col2.metric("RSI", f"{latest['RSI']:.2f}")
    col3.metric("Signal", latest["Signal"])

    st.markdown("""
✅ Strategy:
- **BUY** when RSI < 30 and Close > MA20  
- **SELL** when RSI > 70 or Close < MA20  
- Else HOLD
""")

    st.dataframe(df_signals[["Date", "Close", "RSI", "MA_20", "Signal"]].tail(25), use_container_width=True)
