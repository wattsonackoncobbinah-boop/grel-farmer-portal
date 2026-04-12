import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_lottie import st_lottie
import time
import datetime
import calendar
import feedparser
import base64

# --- 1. CONFIG & LOGO SETUP (MUST BE FIRST) ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")
LOGO_URL = "logo.png"

# --- 2. UPDATED PREDICTION ENGINE (APRIL 2026 DATA) ---
global_market_trend = 1.76  # Current SICOM Average ($/kg)
usd_to_ghs = 14.23          # Current Bank of Ghana Exchange Rate
current_grel_gate_price = 8.30 # Actual Local Market Price (April 2026)
tcda_min_price = 9.11       # Official TCDA Minimum Floor (Dry Equivalent)

def predict_grel_price(global_price, exchange_rate):
    """
    Standard TCDA/GREL Formula:
    k_factor (0.365) accounts for outgrower overhead.
    """
    k_factor = 0.365
    predicted_dry = global_price * exchange_rate * k_factor
    return max(round(predicted_dry, 2), tcda_min_price)

prediction_dry = predict_grel_price(global_market_trend, usd_to_ghs)

# --- 3. ROBUST ANIMATION LOADER ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

sun_anim = load_lottieurl("https://lottie.host/8044737d-2b9a-4c91-95c5-7f414e21a8f9/SgLqT1v7rR.json")
rain_anim = load_lottieurl("https://lottie.host/6770f90c-6627-4c4c-859a-1c05d89f7831/L66XpXv9jI.json")
cloud_anim = load_lottieurl("https://lottie.host/5f5e27a6-2035-4200-8800-476719e7104b/Zp0p9r9jX0.json")

def get_weather_status(city):
    try:
        response = requests.get(f"https://wttr.in/{city}?format=%C", timeout=5)
        return response.text.lower()
    except: return "sunny"

# --- 4. INITIALIZATION & SPLASH SCREEN ---
if 'initialized' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("""
            <style>
            .stApp { background-color: #F2EDE4 !important; background-image: none !important; }
            .loading-text-fs {
                color: #2D2D2D !important;
                text-align: center; font-family: sans-serif;
                margin-top: 25px; font-weight: bold; text-shadow: none !important;
            }
            </style>
        """, unsafe_allow_html=True)
        st.write("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", use_container_width=True)
            st.markdown('<h1 class="loading-text-fs">BENJI LIMITED</h1>', unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
        time.sleep(0.5)
    placeholder.empty()
    st.session_state['initialized'] = True

# --- 5. BACKGROUND & SIDEBAR STYLING ---
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

# --- 6. MAIN CONTENT ---
st.title("🚜 BENJI GREL FARMER'S PRICE & NEWS PORTAL")

col_photo, col_metrics = st.columns([1, 2])
with col_photo:
    st.image("dad.jpg", width=300, caption="Portal Administrator")
with col_metrics:
    st.write("### Today's Market Summary")
    m1, m2 = st.columns(2)
    m1.metric("Global SICOM", f"${global_market_trend}", "+0.04")
    m2.metric("Actual GREL Price", f"GH₵ {current_grel_gate_price}", "-0.10")

# --- 7. PAYOUT CALCULATOR ---
st.divider()
st.subheader("💰 Farmer's Payout Calculator (Wet Weight)")
c1, c2, c3 = st.columns(3)
with c1:
    wet_kg = st.number_input("Enter Total Wet Weight (kg):", value=1000, step=100)
with c2:
    drc_val = st.slider("Select DRC % (from GREL Lab):", 40, 65, 52)
with c3:
    deduct_loan = st.checkbox("Apply 25% Loan Deduction", value=True)

# Logic for Calculator
wet_price = round(prediction_dry * (drc_val / 100), 2)
gross_total = round(wet_kg * wet_price, 2)
net_total = round(gross_total * 0.75, 2) if deduct_loan else gross_total

st.write("---")
res1, res2, res3 = st.columns(3)
res1.metric("Predicted Dry Price", f"₵{prediction_dry}/kg")
res2.metric("Your Wet Price", f"₵{wet_price}/kg")
res3.metric("Estimated Take-Home", f"₵{net_total:,}")

# --- 8. SIDEBAR & WEATHER ---
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

# --- 9. PRICE REVEAL SECTION ---
st.divider()
st.write("### 💰 Confirmed Market Rates")
col_current, col_floor = st.columns(2)
with col_current:
    st.metric("GREL Gate Price (April)", f"GH₵ {current_grel_gate_price}", delta="Current")
with col_floor:
    st.metric("TCDA Minimum Floor", f"GH₵ {tcda_min_price}", delta="Statutory")

today = datetime.date.today()
last_day = calendar.monthrange(today.year, today.month)[1]
days_left = last_day - today.day

if days_left <= 7: 
    st.subheader("📅 Next Month's Forecast")
    with st.expander("🔓 TAP HERE TO REVEAL NEXT MONTH'S PREDICTION"):
        st.write(f"### Predicted Price: **GH₵ {prediction_dry}**")
        if st.button("Confirm Reading"):
            st.balloons()
else:
    st.info(f"Predictive data for next month unlocks in {days_left - 6} days.")

# --- 10. CHART & NEWS ---
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
    st.info(f"**GREL News:** TCDA fixed minimum at **GH₵ {tcda_min_price}/kg**.")
with col_int:
    st.markdown("### International Feed")
    feed = feedparser.parse("https://news.google.com/rss/search?q=rubber+market+Ghana&hl=en-GH&gl=GH&ceid=GH:en")
    for entry in feed.entries[:3]:
        st.markdown(f"**[{entry.title.split(' - ')[0]}]({entry.link})**")

st.divider()
st.info(f"💡 **Advice:** Use the **GH₵ {current_grel_gate_price}** rate for immediate planning.")
