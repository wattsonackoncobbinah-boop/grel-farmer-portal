import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_lottie import st_lottie
import time
import datetime
import calendar
import feedparser
import base64

# --- 1. CONFIG & LOGO SETUP ---
LOGO_URL = "logo.png"
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")

# --- 2. ROBUST ANIMATION LOADER (Crash Protection) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Pre-load animations outside the main loop
sun_anim = load_lottieurl("https://lottie.host/8044737d-2b9a-4c91-95c5-7f414e21a8f9/SgLqT1v7rR.json")
rain_anim = load_lottieurl("https://lottie.host/6770f90c-6627-4c4c-859a-1c05d89f7831/L66XpXv9jI.json")
cloud_anim = load_lottieurl("https://lottie.host/5f5e27a6-2035-4200-8800-476719e7104b/Zp0p9r9jX0.json")

def get_weather_status(city):
    try:
        response = requests.get(f"https://wttr.in/{city}?format=%C", timeout=5)
        return response.text.lower()
    except:
        return "sunny"

# --- 3. INITIALIZATION & SPLASH SCREEN ---
if 'initialized' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        # Keep the CSS for the loading text
        st.markdown("""
            <style>
            .loading-text { text-align: center; color: black; margin-top: 20px; }
            </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # USE NATIVE STREAMLIT COMMAND (Most Reliable)
        # This will center the logo automatically
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=400,height=700)
        
        st.markdown('<h2 class="loading-text">🚀 Loading Farmer Insights...</h2>', unsafe_allow_html=True)
        
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.05)
            bar.progress(i + 1)
        time.sleep(0.5)
        
    placeholder.empty()
    st.session_state['initialized'] = True
    
# --- 4. BACKGROUND & SIDEBAR STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; background-attachment: fixed;
    }
    h1, h2, h3, p, span, label, .stMetric, [data-testid="stMetricValue"] {
        color: white !important; text-shadow: 2px 2px 4px #000000;
    }
    [data-testid="stSidebar"] { background-color: rgba(0, 70, 0, 0.9); }
    </style>
    """, unsafe_allow_html=True)

# --- 5. MAIN CONTENT ---
st.title("🚜 BENJI GREL FARMER'S PRICE & NEWS PORTAL")

col_photo, col_metrics = st.columns([1, 2])
with col_photo:
    st.image("dad.jpg", width=300, caption="Portal Administrator")
with col_metrics:
    st.write("### Today's Market Summary")
    m1, m2 = st.columns(2)
    m1.metric("Global Rubber", "$1.62", "+0.04")
    m2.metric("GREL Grade A", "7.40 GHS", "-0.10")

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
