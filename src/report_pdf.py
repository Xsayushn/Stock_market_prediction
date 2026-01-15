from fpdf import FPDF
import pandas as pd
import os

def safe_text(text: str) -> str:
    """
    Remove emojis / unsupported unicode characters for PDF fonts like Helvetica.
    """
    if text is None:
        return ""
    return (
        str(text)
        .replace("✅", "BUY")
        .replace("❌", "SELL")
        .replace("⭐", "")
        .replace("📈", "")
        .replace("📌", "")
        .replace("📰", "")
        .encode("latin-1", "ignore")
        .decode("latin-1")
    )

def create_pdf_report(symbol: str, forecast_df: pd.DataFrame, signal_text: str, sentiment_score: float):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt=safe_text(f"Stock Report - {symbol}"), ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=safe_text(f"Sentiment Score: {sentiment_score:.3f}"), ln=True)
    pdf.cell(200, 10, txt=safe_text(f"Latest Signal: {signal_text}"), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Forecast (Next Days):", ln=True)

    pdf.set_font("Arial", size=10)
    for _, row in forecast_df.iterrows():
        line = f"{row['Day']} -> {float(row['Predicted Close']):.2f}"
        pdf.cell(200, 8, txt=safe_text(line), ln=True)

    os.makedirs("exports", exist_ok=True)
    file_path = f"exports/{symbol}_report.pdf"
    pdf.output(file_path)
    return file_path
