import streamlit as st
import pandas as pd
import os
import joblib
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
from src.report_pdf import create_pdf_report


# ✅ No guessing. Only clean input.
def normalize_symbol(sym: str) -> str:
    return sym.strip().upper().replace(" ", "")


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
st.caption("✅ Watchlist + News Sentiment + Candlestick + RSI/MACD + Forecast + Export CSV/PDF")

logout_button()


# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Controls")

watchlist = get_watchlist(username)

st.sidebar.subheader("⭐ Watchlist")
if len(watchlist) > 0:
    selected_from_watchlist = st.sidebar.selectbox("Select from Watchlist", watchlist)
else:
    selected_from_watchlist = None
    st.sidebar.info("No watchlist yet. Add your first stock ✅")

manual_symbol = st.sidebar.text_input("Or enter symbol manually", "")

# ✅ Decide symbol (NO auto .NS)
if manual_symbol.strip() != "":
    symbol = normalize_symbol(manual_symbol)
elif selected_from_watchlist:
    symbol = normalize_symbol(selected_from_watchlist)
else:
    symbol = "AAPL"

st.sidebar.success(f"Using Symbol: {symbol}")

start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
forecast_days = st.sidebar.slider("Forecast Days", 1, 14, 7)

model_name = st.sidebar.selectbox(
    "Select Model",
    ["Linear Regression", "Random Forest"]
)

run_btn = st.sidebar.button("🚀 Run Dashboard")


# ✅ Watchlist buttons
st.sidebar.markdown("---")

if st.sidebar.button("➕ Add Selected Symbol"):
    add_to_watchlist(username, symbol)
    st.sidebar.success(f"Added {symbol} ✅")
    st.rerun()

if len(watchlist) > 0:
    remove_symbol = st.sidebar.selectbox("Remove Symbol", watchlist, key="remove_symbol")
    if st.sidebar.button("🗑 Remove Selected"):
        remove_from_watchlist(username, remove_symbol)
        st.sidebar.success(f"Removed {remove_symbol} ✅")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("🇺🇸 US: AAPL, TSLA, MSFT")
st.sidebar.info("🇮🇳 NSE: RELIANCE.NS, TCS.NS, INFY.NS")


# ---------------- MAIN ----------------
if not run_btn:
    st.info("👈 Select stock + model and click **Run Dashboard**")
    st.stop()


# ---------------- LOAD DATA ----------------
try:
    df = load_stock_data(symbol, start=str(start_date))
except Exception as e:
    st.error(f"❌ Failed to load stock data for: {symbol}")
    st.warning("✅ Examples: AAPL, TSLA, RELIANCE.NS, TCS.NS")
    st.exception(e)
    st.stop()


# ---------------- FEATURES ----------------
df_feat = add_features(df)
df_signals = generate_signals(df_feat)
latest = df_signals.iloc[-1]


# ---------------- NEWS SENTIMENT ----------------
st.subheader("📰 Live News Sentiment")

try:
    sent_avg, news_items = analyze_news_sentiment(symbol)
except Exception:
    sent_avg, news_items = 0.0, []
    st.warning("⚠️ News sentiment unavailable (RSS issue).")

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


# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Charts", "🤖 Forecast & Export", "📌 Signals"])


# TAB 1 - Charts
with tab1:
    st.subheader(f"📌 Candlestick + RSI + MACD : {symbol}")
    st.plotly_chart(candlestick_chart(df_signals), use_container_width=True)

    st.subheader("📄 Latest Data")
    st.dataframe(df_signals.tail(20), use_container_width=True)


# TAB 2 - Forecast + Export
with tab2:
    st.subheader("🤖 Model Forecast + Export")

    X, y, final_df, feature_cols = prepare_dataset(df_feat)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = get_model(model_name)
    model.fit(X_train, y_train)

    # ✅ Save model properly
    os.makedirs("models", exist_ok=True)
    safe_model_name = model_name.replace(" ", "_")
    model_path = f"models/{symbol}_{safe_model_name}.pkl"
    joblib.dump(model, model_path)

    st.success(f"✅ Model saved: {model_path}")

    # Evaluate
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r = rmse(y_test.values, preds)

    c1, c2, c3 = st.columns(3)
    c1.metric("Model", model_name)
    c2.metric("MAE", f"{mae:.4f}")
    c3.metric("RMSE", f"{r:.4f}")

    # Forecast future
    last_row = X.iloc[-1].values
    future_prices = forecast_next_days(model, last_row, days=forecast_days)

    future_df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(forecast_days)],
        "Predicted Close": future_prices
    })

    st.subheader(f"📌 Next {forecast_days}-day Forecast")
    st.dataframe(future_df, use_container_width=True)
    st.success(f"✅ Tomorrow predicted close: **{future_prices[0]:.2f}**")

    # ✅ Forecast CSV
    st.download_button(
        "⬇️ Download Forecast CSV",
        data=future_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{symbol}_forecast.csv",
        mime="text/csv"
    )

    # ✅ Full Report CSV (last 200 rows)
    report_df = df_signals[[
        "Date", "Open", "High", "Low", "Close",
        "MA_20", "MA_50", "RSI", "MACD", "MACD_Signal", "Signal"
    ]].tail(200)

    st.download_button(
        "⬇️ Download Full Report CSV",
        data=report_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{symbol}_full_report.csv",
        mime="text/csv"
    )

    # ✅ PDF Export
    try:
        pdf_path = create_pdf_report(symbol, future_df, latest["Signal"], sent_avg)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇️ Download PDF Report",
                data=f,
                file_name=f"{symbol}_report.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.warning("⚠️ PDF export failed (font/unicode issue). CSV export still works ✅")
        st.exception(e)


# TAB 3 - Signals
with tab3:
    st.subheader("📌 Buy / Sell Signal")

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

    st.dataframe(
        df_signals[["Date", "Close", "RSI", "MA_20", "Signal"]].tail(25),
        use_container_width=True
    )
