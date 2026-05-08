import streamlit as st
import yfinance as yf
import ta
import pandas as pd
from openai import OpenAI
import streamlit.components.v1 as components

# הגדרות עמוד ועיצוב עברית
st.set_page_config(page_title="סורק מניות AI", layout="wide")

st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div[data-testid="stSidebar"] { direction: rtl; text-align: right; }
    .stDataFrame { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

def get_ai_analysis(api_key, symbol, price, rsi, action):
    if not api_key: return "אנא הכנס מפתח API בתפריט הצד כדי לקבל ניתוח."
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        prompt = f"נתח את מניית {symbol}. מחיר: {price}$, RSI: {rsi}. המלצה טכנית: {action}. כתוב בעברית סיכום קצר למשקיע."
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except: return "שגיאה בחיבור לבינה המלאכותית."

def analyze_stock(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1mo")
        if data.empty: return None
        price = data['Close'].iloc[-1]
        rsi = ta.momentum.RSIIndicator(data["Close"]).rsi().iloc[-1]
        if rsi < 35: action = "קנייה 🚀"
        elif rsi > 65: action = "מכירה/שורט 📉"
        else: action = "המתנה ⚖️"
        return {"מניה": symbol, "מחיר": round(price, 2), "RSI": round(rsi, 2), "פעולה": action}
    except: return None

# ממשק המשתמש
st.title("🔥 סורק מניות AI - GOD MODE")

with st.sidebar:
    st.header("הגדרות")
    api_key = st.text_input("מפתח Grok API (xAI):", type="password")
    watchlist_text = st.text_area("רשימת מניות (פסיק בין אחת לשנייה):", "NVDA, TSLA, AAPL, AMZN")
    run_btn = st.button("🚀 הרץ סריקה עכשיו")

if run_btn:
    symbols = [s.strip().upper() for s in watchlist_text.split(",")]
    results = []
    with st.spinner('מנתח נתונים בזמן אמת...'):
        for sym in symbols:
            res = analyze_stock(sym)
            if res: results.append(res)
    
    if results:
        st.subheader("📊 תוצאות סריקה")
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        
        for s in results:
            with st.expander(f"🔍 ניתוח מעמיק למניית {s['מניה']}"):
                st.write(f"**מחיר:** ${s['מחיר']} | **RSI:** {s['RSI']}")
                if api_key:
                    st.write("**ניתוח Grok AI:**")
                    st.write(get_ai_analysis(api_key, s['מניה'], s['מחיר'], s['RSI'], s['פעולה']))
                else:
                    st.warning("הכנס מפתח API בתפריט הצד כדי לראות ניתוח AI כאן.")
