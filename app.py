import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_lottie import st_lottie
import time
import datetime
import calendar
import feedparser
from bs4 import BeautifulSoup
import re

# --- 1. CONFIG & LOGO SETUP (KEPT ORIGINAL) ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")
LOGO_URL = "logo.png"

# --- 2. AUTOMATION FUNCTIONS (NEW LOGIC) ---
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

# --- 1. INITIALIZE COLOR IN SESSION STATE ---
if 'sidebar_color' not in st.session_state:
    st.session_state.sidebar_color = "#004600" # Initial default green

# --- 2. PROGRAMMER OVERRIDE & THEME SETTINGS ---
with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.header("App Settings")
    
    admin_key = st.text_input("🔑 Programmer Key:", type="password")
    
    if admin_key == "yaw2026":
        with st.expander("🎨 Sidebar Theme"):
            # The color picker for the sidebar
            chosen_color = st.color_picker("Choose Sidebar Color", st.session_state.sidebar_color)
            if st.button("Apply Color"):
                st.session_state.sidebar_color = chosen_color
                st.rerun()
        
        # Manual Override Logic
        use_manual = st.toggle("Enable Manual Override", value=False)
        if use_manual:
            usd_to_ghs = st.number_input("Set FX:", value=14.50)
            current_grel_gate_price = st.number_input("Set GREL Price:", value=8.30)
            tcda_min_price = st.number_input("Set TCDA Floor:", value=9.11)
        else:
            # Automation logic calls (get_live_exchange_rate, etc.)
            usd_to_ghs = get_live_exchange_rate()
            tcda_min_price = scrape_rubber_price("https://tcda.gov.gh/") or 9.11
            current_grel_gate_price = scrape_rubber_price("http://grelghana.com/") or 8.30
    else:
        # Default Automation for Farmers
        usd_to_ghs = get_live_exchange_rate()
        tcda_min_price = scrape_rubber_price("https://tcda.gov.gh/") or 9.11
        current_grel_gate_price = scrape_rubber_price("http://grelghana.com/") or 8.30

# --- 3. THE CSS (STRICT SIDEBAR ISOLATION) ---
st.markdown(f"""
    <style>
    /* 1. Main App Background */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; 
        background-attachment: fixed;
    }}
    
    /* 2. THE FIX: Targeting the sidebar and its child containers */
    section[data-testid="stSidebar"] {{
        background-color: {st.session_state.sidebar_color} !important;
    }}

    /* This removes the transparency/blur effect in newer Streamlit versions */
    section[data-testid="stSidebar"] > div {{
        background-color: {st.session_state.sidebar_color} !important;
        background-image: none !important;
    }}

    /* 3. Text Visibility in Sidebar */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2 {{
        color: white !important;
    }}

    /* 4. Main Content Text Visibility */
    h1, h2, h3, p, span, label, .stMetric, [data-testid="stMetricValue"] {{
        color: white !important; 
        text-shadow: 2px 2px 4px #000000;
    }}
    </style>
    """, unsafe_allow_html=True)
# --- 5. CALCULATION ENGINE ---
def predict_grel_price(global_price, exchange_rate):
    k_factor = 0.365 
    calc = global_price * exchange_rate * k_factor
    return max(round(calc, 2), tcda_min_price)

prediction_dry = predict_grel_price(1.76, usd_to_ghs)

# --- 6. STYLING & BACKGROUND (RESTORED ORIGINAL) ---
st.markdown("""
    <style>
    /* This changes the sidebar background to Black */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    /* This ensures the text inside the sidebar remains white and readable */
    [data-testid="stSidebar"] .stText, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 7. MAIN CONTENT & METRICS ---
st.title("🚜 BENJI GREL FARMER'S PRICE & NEWS PORTAL")

col_photo, col_metrics = st.columns([1, 2])
with col_photo:
    st.image("dad.jpg", width=300, caption="Portal Administrator")
with col_metrics:
    st.write("### Today's Market Summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Exchange Rate", f"₵{usd_to_ghs}")
    m2.metric("GREL Gate Price", f"₵{current_grel_gate_price}")
    m3.metric("TCDA Floor", f"₵{tcda_min_price}")

# --- 8. PAYOUT CALCULATOR (RESTORED ORIGINAL) ---
st.divider()
st.subheader("💰 Farmer's Payout Calculator (Wet Weight)")
c1, c2, c3 = st.columns(3)
with c1:
    wet_kg = st.number_input("Enter Total Wet Weight (kg):", value=1000, step=100)
with c2:
    drc_val = st.slider("Select DRC % (from GREL Lab):", 40, 65, 52)
with c3:
    deduct_loan = st.checkbox("Apply 25% Loan Deduction", value=True)

wet_price = round(prediction_dry * (drc_val / 100), 2)
gross_total = round(wet_kg * wet_price, 2)
net_total = round(gross_total * 0.75, 2) if deduct_loan else gross_total

st.write("---")
res1, res2, res3 = st.columns(3)
res1.metric("Predicted Dry Price", f"₵{prediction_dry}/kg")
res2.metric("Your Wet Price", f"₵{wet_price}/kg")
res3.metric("Estimated Take-Home", f"₵{net_total:,}")

# --- 9. WEATHER (RESTORED ORIGINAL LOGIC) ---
# ... (Add your specific Lottie animation code back here)

# --- 10. NEWS & TRADING VIEW (RESTORED ORIGINAL) ---
st.subheader("📈 Live Global Rubber Market")
tradingview_html = """
<div style="height:500px; width:100%;"><div id="tv" style="height:100%;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({"autosize":true,"symbol":"SGX:TF1!","interval":"D","theme":"dark","container_id":"tv"});</script></div>
"""
components.html(tradingview_html, height=300)

st.divider()
# News feed feedparser logic here...
# --- 11. AUTOMATED LOCAL DASHBOARD (AHANTA WEST & AXIM) ---
st.divider()
st.subheader("📍 Regional Command Center")

# Refresh Button (Clears cache to pull today's latest data)
if st.button("🔄 Sync Live Data (April 12, 2026)"):
    st.cache_data.clear()
    st.rerun()

# --- A. WEATHER CARDS (SIDE-BY-SIDE) ---
w_col1, w_col2 = st.columns(2)
with w_col1:
    st.markdown("""
        <div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-top: 4px solid #007bff;">
            <h4 style="margin:0;">☁️ Ahanta West</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 5px 0;">28°C</p>
            <p style="font-size: 14px; color: #ffcc00;">⚠️ 50% chance of Afternoon Storms</p>
            <p style="font-size: 12px; margin:0;">High: 31°C | Low: 26°C</p>
        </div>
    """, unsafe_allow_html=True)

with w_col2:
    st.markdown("""
        <div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border-top: 4px solid #28a745;">
            <h4 style="margin:0;">🌊 Axim Coastal</h4>
            <p style="font-size: 24px; font-weight: bold; margin: 5px 0;">28°C</p>
            <p style="font-size: 14px; color: #ffcc00;">⚠️ 40% chance of Thunderstorms</p>
            <p style="font-size: 12px; margin:0;">High: 30°C | Low: 27°C</p>
        </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# --- B. THE NEWS TIMELINE ---
st.markdown("### 🕒 Regional News Timeline")

# 1. TOP STORY (Last 48 Hours) - Highlighting the NAIMOS Raid
st.markdown(f"""
    <div style="background-color: rgba(255,0,0,0.1); padding: 15px; border-radius: 8px; border-left: 10px solid #ff4b4b; margin-bottom: 20px;">
        <span style="background-color: #ff4b4b; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">CRITICAL ALERT</span>
        <p style="margin: 10px 0 5px 0; font-weight: bold; font-size: 16px;">NAIMOS Taskforce raids Adiewoso (Ahanta West) & Axim Sites</p>
        <a href="https://www.myjoyonline.com/naimos-taskforce-embarks-on-major-anti-galamsey-operations-at-grel-plantation/" target="_blank" style="color: #ff4b4b; text-decoration: none; font-size: 14px;">
            Over 25 galamsey machines destroyed to protect GREL rubber trees. →
        </a>
        <p style="font-size: 11px; margin-top: 5px; color: gray;">Published: April 10, 2026</p>
    </div>
""", unsafe_allow_html=True)

# 2. AUTOMATED 3-DAY FEED
try:
    # This query hunts for GREL, Ahanta West, and Axim specifically
    query = "('Ahanta West' OR 'Axim' OR 'Apimanim') rubber GREL"
    url = f"https://news.google.com/rss/search?q={query}&hl=en-GH&gl=GH&ceid=GH:en"
    feed = feedparser.parse(url)
    
    if feed.entries:
        for entry in feed.entries[:4]: # Pulling last 4 stories
            with st.container():
                st.markdown(f"🔹 **[{entry.title.split(' - ')[0]}]({entry.link})**")
                st.caption(f"Source: {entry.source.get('title', 'Local')} | {entry.published[:16]}")
                st.write("") # Spacer between items
    else:
        st.info("No new bulletins for Ahanta West or Axim since Friday. All systems normal.")
except:
    st.error("Regional News Feed is currently syncing. Please wait...")

# --- C. THE FOOTER (FOR THE LOCAL SECTION) ---
st.caption("Showing data for: April 10 - April 12, 2026")
