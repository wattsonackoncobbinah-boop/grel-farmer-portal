import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_lottie import st_lottie
import time
import datetime
import calendar
import feedparser

# --- 1. CONFIG & PREDICTION LOGIC ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")

# These are your "Feature 1" inputs
global_market_trend = 1.65  # SICOM Price ($/kg)
prev_grel_price = 5.45      # Last month
usd_to_ghs = 13.50          # Exchange Rate

def predict_grel_price(global_price, exchange_rate):
    raw_conversion = global_price * exchange_rate
    # 0.75 is your "GREL Factor" - tune this as you learn their margins!
    predicted_price = raw_conversion * 0.75 
    return round(predicted_price, 2)

prediction = predict_grel_price(global_market_trend, usd_to_ghs)
LOGO_URL = "logo.png"

# --- 2. INITIALIZATION & SPLASH SCREEN ---
if 'initialized' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
            .stApp { background-color: #F2EDE4 !important; background-image: none !important; }
            .loading-text-fs { color: #2D2D2D !important; text-align: center; font-family: sans-serif; margin-top: 25px; font-weight: bold; }
            </style>
        """, unsafe_allow_html=True)
        st.write("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(LOGO_URL, use_container_width=True)
            st.markdown('<h1 class="loading-text-fs">BENJI LIMITED</h1>', unsafe_allow_html=True)
        
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.03) # Speed up slightly to 3 seconds total
            bar.progress(i + 1)
        time.sleep(0.5)
    placeholder.empty()
    st.session_state['initialized'] = True

# --- 3. STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stMetric"] { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MAIN DASHBOARD ---
st.title("🚜 BENJI GREL FARMER'S PORTAL")

# FEATURE 1 & 2: THE PREDICTION HUB (Mobile Optimized)
st.write("### 🔮 Early Insight: Next Price Forecast")
with st.container():
    p1, p2 = st.columns(2)
    with p1:
        delta_val = round(prediction - prev_grel_price, 2)
        st.metric(label="Predicted GREL Price", value=f"₵{prediction}", delta=f"{delta_val} vs Last Month")
    with p2:
        if delta_val > 0:
            st.success("### 📈 TREND: RISING\nAdvice: Consider holding stock for the announcement.")
        else:
            st.warning("### 📉 TREND: DIPPING\nAdvice: Clear current inventory soon.")

st.divider()

# --- 5. SIDEBAR, WEATHER, AND REST OF CONTENT ---
# (Keep your existing sidebar and TradingView code below this...)
# --- 6. SIDEBAR & WEATHER ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True) 
    st.header("App Settings")
    st.divider()
    
    target_town = st.text_input("📍 Weather Location:", value="Princess Town")
    condition = get_weather_status(target_town)
    
    if "rain" in condition or "shower" in condition:
        if rain_anim: st_lottie(rain_anim, height=150, key="rain")
        st.error("⚠️ **Rain Alert:** High washout risk.")
    elif "cloud" in condition or "overcast" in condition:
        if cloud_anim: st_lottie(cloud_anim, height=150, key="cloud")
        st.warning("☁️ **Cloudy Conditions**")
    else:
        if sun_anim: st_lottie(sun_anim, height=150, key="sun")
        st.success("☀️ **Clear Skies**")

# --- 7. PRICE REVEAL ---
st.divider()
today = datetime.date.today()
last_day = calendar.monthrange(today.year, today.month)[1]
days_left = last_day - today.day

current_price = 8.12
st.write("### 💰 Current Market Rate")
st.metric("GREL Grade A (April)", f"GH₵ {current_price}", delta="Stable")

if days_left <= 25: 
    st.subheader("📅 Next Month's Forecast")
    with st.expander("🔓 TAP HERE TO REVEAL MAY 2026 PREDICTION"):
        st.write("### Predicted Price: **GH₵ 8.14**")
        st.progress(85)
        if st.button("Confirm Reading"):
            st.balloons()
            st.toast("Price acknowledged!")
else:
    st.info(f"Next month's prediction unlocks in {days_left - 3} days.")

# --- 8. CHART & NEWS ---
st.subheader("📈 Live Global Rubber Market")
tradingview_html = """
<div style="height:600px; width:100%;"><div id="tv" style="height:100%;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({"autosize":true,"symbol":"SGX:TF1!","interval":"D","theme":"dark","container_id":"tv"});</script></div>
"""
components.html(tradingview_html, height=600)

st.divider()
st.subheader("📰 Rubber Industry News Hub")
col_local, col_int = st.columns(2)

with col_local:
    st.markdown("### Local Updates")
    st.info("**April 2026 Price:** TCDA fixed minimum at **GH₵ 9.11/kg**.")
    st.success("**Scholarships:** GREL awarded 33 students for the 2026 year.")

with col_int:
    st.markdown("### International Feed")
    feed = feedparser.parse("https://news.google.com/rss/search?q=rubber+market+Ghana&hl=en-GH&gl=GH&ceid=GH:en")
    for entry in feed.entries[:3]:
        st.markdown(f"**[{entry.title.split(' - ')[0]}]({entry.link})**")

st.divider()
st.info("💡 **Advice:** Use the **GH₵ 9.11** baseline for bargaining in the Western Region.")
