import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
import re
import time
import datetime
import calendar
import feedparser

# --- 1. CONFIG & LOGO SETUP ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")
LOGO_URL = "logo.png"

# --- 2. AUTOMATION FUNCTIONS ---
def get_live_exchange_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        return round(requests.get(url, timeout=5).json()['rates']['GHS'], 2)
    except:
        return 14.50

def scrape_rubber_price(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text()
        matches = re.findall(r"₵\s?(\d+\.\d+)|GHS\s?(\d+\.\d+)", text_content)
        if matches:
            return float([m for m in matches[0] if m][0])
        return None
    except:
        return None

# --- 3. SIDEBAR & SECURE PROGRAMMER OVERRIDE ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.header("⚙️ Portal Settings")
    
    # Secure Admin Access
    st.divider()
    admin_key = st.text_input("🔑 Programmer Key:", type="password")
    
    # Default Automation Values
    if 'manual_active' not in st.session_state:
        st.session_state.manual_active = False

    if admin_key == "yaw2026": # This is your secret password
        st.success("Access Granted, Yaw.")
        st.session_state.manual_active = st.toggle("Enable Manual Override", value=st.session_state.manual_active)
        
        if st.session_state.manual_active:
            manual_fx = st.number_input("Set FX (USD/GHS):", value=14.50)
            manual_grel = st.number_input("Set GREL Price:", value=8.30)
            manual_tcda = st.number_input("Set TCDA Floor:", value=9.11)
            
            usd_to_ghs = manual_fx
            current_grel_gate_price = manual_grel
            tcda_min_price = manual_tcda
    
    # If not in manual mode or password wrong, use automation
    if not st.session_state.manual_active:
        with st.spinner("Fetching live market data..."):
            usd_to_ghs = get_live_exchange_rate()
            tcda_min_price = scrape_rubber_price("https://tcda.gov.gh/") or 9.11
            current_grel_gate_price = scrape_rubber_price("http://grelghana.com/") or 8.30

# --- 4. PREDICTION ENGINE ---
def predict_grel_price(global_price, exchange_rate):
    k_factor = 0.365 
    calc = global_price * exchange_rate * k_factor
    return max(round(calc, 2), tcda_min_price)

prediction_dry = predict_grel_price(1.76, usd_to_ghs)

# --- 5. INITIALIZATION & STYLING ---
if 'initialized' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<style>.stApp { background-color: #F2EDE4 !important; }</style>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", use_container_width=True)
            st.markdown('<h1 style="text-align:center;">BENJI LIMITED</h1>', unsafe_allow_html=True)
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
    placeholder.empty()
    st.session_state['initialized'] = True

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; background-attachment: fixed;
    }
    h1, h2, h3, p, span, label, .stMetric { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. MAIN DASHBOARD ---
st.title("🚜 BENJI GREL FARMER'S PORTAL")

m1, m2, m3 = st.columns(3)
m1.metric("Exchange Rate", f"₵{usd_to_ghs}")
m2.metric("GREL Gate Price", f"₵{current_grel_gate_price}")
m3.metric("TCDA Floor", f"₵{tcda_min_price}")

st.divider()
st.subheader("💰 Payout Calculator")
c1, c2 = st.columns(2)
with c1:
    wet_kg = st.number_input("Wet Weight (kg):", value=1000)
with c2:
    drc_val = st.slider("DRC %:", 40, 65, 52)

wet_price = round(prediction_dry * (drc_val / 100), 2)
net_total = round((wet_kg * wet_price) * 0.75, 2)

st.metric("Estimated Take-Home Pay", f"₵{net_total:,}")

# --- 7. WEATHER & NEWS ---
with st.sidebar:
    st.divider()
    target_town = st.text_input("📍 Weather Location:", value="Princess Town")
    st.info(f"Weather for {target_town} would load here.")

st.divider()
st.subheader("📰 Industry News")
st.info("💡 Automation is active. Enter Programmer Key in sidebar to adjust prices manually.")
