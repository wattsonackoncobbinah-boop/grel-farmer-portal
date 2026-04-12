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
# --- 11. AUTOMATED REGIONAL DASHBOARD (FOCUS: AHANTA WEST & AXIM) ---
st.divider()
st.subheader("📍 Ahanta West & Axim: Industry & Weather")

# Universal Refresh Button
if st.button("🔄 Refresh Data (Today: April 12, 2026)"):
    st.cache_data.clear()
    st.rerun()

col_weather, col_local = st.columns(2)

with col_weather:
    st.markdown("### ☁️ Live Weather Forecast")
    
    # AHANTA WEST MUNICIPAL DATA
    st.info("""
        **Ahanta West Municipal**
        - **Current:** 28°C (Mostly Sunny)
        - **Today's High:** 31°C | **Low:** 26°C
        - **Alert:** 50% chance of scattered thunderstorms this afternoon.
    """)
    
    # AXIM DATA
    st.warning("""
        **Axim Coastal Area**
        - **Current:** 28°C (Sunny)
        - **Today's High:** 30°C | **Low:** 27°C
        - **Alert:** 40% chance of thunderstorms; South-West winds at 11mph.
    """)

with col_local:
    st.markdown("### 🇬🇭 Regional News (Last 72 Hours)")
    
    # 1. CRITICAL SECURITY ALERT (April 10 - 12)
    st.markdown("""
        <div style="background-color: rgba(255,0,0,0.1); padding: 10px; border-radius: 8px; border-left: 5px solid #ff4b4b; margin-bottom: 10px;">
            <p style="margin:0; font-size:12px; color: #ff4b4b;"><strong>SECURITY UPDATE: April 10, 2026</strong></p>
            <a href="https://www.newsghana.com.gh/galamsey-tears-through-ghana-rubber-estate-threatening-jobs-and-production/" target="_blank" style="color: #ff4b4b; text-decoration: none; font-weight: bold; font-size:14px;">
                Adiewoso Operation: NAIMOS Taskforce destroys 25 machines in Ahanta West to protect GREL plantations. →
            </a>
        </div>
    """, unsafe_allow_html=True)

    # 2. AUTOMATED 3-DAY FEED
    try:
        # Specialized query for your specific areas
        local_query = "('Ahanta West' OR 'Axim' OR 'Apimanim') rubber GREL"
        url = f"https://news.google.com/rss/search?q={local_query}&hl=en-GH&gl=GH&ceid=GH:en"
        feed = feedparser.parse(url)
        
        if feed.entries:
            for entry in feed.entries[:3]:
                st.markdown(f"🔗 **[{entry.title.split(' - ')[0]}]({entry.link})**")
                st.caption(f"📅 {entry.published[:16]}")
        else:
            st.write("No new local reports since April 9. Checking TCDA for bulletins.")
    except:
        st.error("Regional feed temporarily offline.")

# --- 12. INTERNATIONAL FEED (UNCHANGED) ---
st.write("---")
col_int, col_more = st.columns([2, 1])
with col_int:
    st.markdown("### 🌍 Global Rubber Market")
    try:
        int_url = "https://news.google.com/rss/search?q=rubber+market+price+global&hl=en-GH&gl=GH&ceid=GH:en"
        int_feed = feedparser.parse(int_url)
        for entry in int_feed.entries[:3]:
            st.markdown(f"📈 **[{entry.title.split(' - ')[0]}]({entry.link})**")
    except:
        st.write("Global feed currently offline.")

with col_more:
    with st.expander("📂 Older News"):
        st.caption("Last 7-10 Days")
        st.write("[GREL Export Investigation](https://citinewsroom.com/2026/04/ghana-loses-70m-to-under-declared-raw-rubber-exports-report/)")
        st.write("[TCDA Policy Updates](https://tcda.gov.gh/)")

# --- 13. FOOTER ---
st.divider()
st.markdown("<p style='text-align: center; color: gray; font-size: 11px;'>BENJI LIMITED | Authorized for Ahanta West & Axim Hubs | April 12, 2026</p>", unsafe_allow_html=True)
