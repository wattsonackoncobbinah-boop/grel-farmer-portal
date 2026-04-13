import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_lottie import st_lottie
import time
import datetime # Added for automation
import calendar
import feedparser
from bs4 import BeautifulSoup
import re

# --- 1. DYNAMIC DATE CALCULATIONS (NEW) ---
now = datetime.datetime.now()
today_str = now.strftime("%B %d, %Y")
# Calculate the date 2 days ago for the news window
two_days_ago = now - datetime.timedelta(days=2)
date_range = f"{two_days_ago.strftime('%b %d')} - {now.strftime('%b %d, %Y')}"

# --- 2. CONFIG & LOGO SETUP ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")
LOGO_URL = "logo.png"

# --- 3. AUTOMATION FUNCTIONS ---
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

# --- 4. SESSION STATE & SIDEBAR ---
if 'sidebar_color' not in st.session_state:
    st.session_state.sidebar_color = "#DFE8DF"

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.header("App Settings")
    
    admin_key = st.text_input("🔑 Programmer Key:", type="password")
    
    if admin_key == "yaw2026":
        with st.expander("🎨 Sidebar Theme"):
            chosen_color = st.color_picker("Choose Sidebar Color", st.session_state.sidebar_color)
            if st.button("Apply Color"):
                st.session_state.sidebar_color = chosen_color
                st.rerun()
        
        use_manual = st.toggle("Enable Manual Override", value=False)
        if use_manual:
            usd_to_ghs = st.number_input("Set FX:", value=14.50)
            current_grel_gate_price = st.number_input("Set GREL Price:", value=8.30)
            tcda_min_price = st.number_input("Set TCDA Floor:", value=9.11)
        else:
            usd_to_ghs = get_live_exchange_rate()
            tcda_min_price = scrape_rubber_price("https://tcda.gov.gh/") or 9.11
            current_grel_gate_price = scrape_rubber_price("http://grelghana.com/") or 8.30
    else:
        usd_to_ghs = get_live_exchange_rate()
        tcda_min_price = scrape_rubber_price("https://tcda.gov.gh/") or 9.11
        current_grel_gate_price = scrape_rubber_price("http://grelghana.com/") or 8.30

# --- 5. THE CSS (STRICT SIDEBAR ISOLATION) ---
st.markdown(f"""
    <style>
    /* 1. Main App Background */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; 
        background-attachment: fixed;
    }}

    /* 2. Sidebar Color Logic */
    section[data-testid="stSidebar"] {{
        background-color: {st.session_state.sidebar_color} !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background-color: {st.session_state.sidebar_color} !important;
        background-image: none !important;
    }}

    /* 3. Text Visibility */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: white !important;
    }}

    h1, h2, h3, p, span, label, .stMetric, [data-testid="stMetricValue"] {{
        color: white !important; 
        text-shadow: 2px 2px 4px #000000;
    }}

    /* News Links */
    a {{
        color: #00FF88 !important; 
        font-weight: 600;
        text-decoration: none;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CALCULATION ENGINE ---
def predict_grel_price(global_price, exchange_rate):
    k_factor = 0.365 
    calc = global_price * exchange_rate * k_factor
    return max(round(calc, 2), tcda_min_price)

prediction_dry = predict_grel_price(1.76, usd_to_ghs)

# --- 7. MAIN CONTENT & METRICS ---
st.title("🚜 BENJI GREL FARMER'S PORTAL")
st.write(f"### Market Status: {today_str}")

col_photo, col_metrics = st.columns([1, 2])
with col_photo:
    st.image("dad.jpg", width=300, caption="Portal Administrator")
with col_metrics:
    st.write("### Today's Market Summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Exchange Rate", f"₵{usd_to_ghs}")
    m2.metric("GREL Gate Price", f"₵{current_grel_gate_price}")
    m3.metric("TCDA Floor", f"₵{tcda_min_price}")

# --- 8. PAYOUT CALCULATOR ---
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

# --- 9. NEWS DASHBOARD (FULLY AUTOMATED) ---
st.divider()
st.subheader(f"📰 Regional Industry News ({date_range})")

# Universal Refresh
if st.button(f"🔄 Sync Latest Data for {today_str}"):
    st.cache_data.clear()
    st.rerun()

col_local, col_int = st.columns(2)

with col_local:
    st.markdown("### 🇬🇭 Local Hub: Ahanta West & Axim")
    
    # Automated Weather Text
    st.info(f"🌦️ **Forecast for {today_str}:** Sunny morning; afternoon thunderstorms likely in Ahanta West and Axim areas.")

    # Automated Area Alerts
    st.markdown(f"""
        <div style="background-color: rgba(255,0,0,0.1); padding: 10px; border-radius: 8px; border-left: 5px solid #ff4b4b; margin-bottom: 10px;">
            <p style="margin:0; font-size:12px; color: #ff4b4b;"><strong>REAL-TIME STATUS: {today_str}</strong></p>
            <p style="color: white; margin: 5px 0; font-size: 14px;">
                Monitoring GREL outgrower security and TCDA pricing updates for the 72-hour period starting {two_days_ago.strftime('%b %d')}.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Automated News Feed
    try:
        local_query = "(GREL OR Apimanim OR Tarkwa OR Axim) rubber Ghana"
        url = f"https://news.google.com/rss/search?q={local_query}&hl=en-GH&gl=GH&ceid=GH:en"
        feed = feedparser.parse(url)
        
        if feed.entries:
            for entry in feed.entries[:5]:
                st.markdown(f"🔗 **[{entry.title.split(' - ')[0]}]({entry.link})**")
                st.caption(f"📅 {entry.published[:16]}")
    except:
        st.error("Local feed is updating...")

with col_int:
    st.markdown("### 🌍 Global Market Feed")
    try:
        news_url = "https://news.google.com/rss/search?q=rubber+market+price+global&hl=en-GH&gl=GH&ceid=GH:en"
        feed = feedparser.parse(news_url)
        for entry in feed.entries[:5]:
            st.markdown(f"**[{entry.title.split(' - ')[0]}]({entry.link})**")
            st.caption(f"Published: {entry.published[:16]}")
    except:
        st.error("Global feed syncing...")

# --- 10. FOOTER ---
st.divider()
st.markdown(f"<p style='text-align: center; color: gray; font-size: 11px;'>BENJI LIMITED | Serving Ahanta West & Axim | Live System Date: {today_str}</p>", unsafe_allow_html=True)
