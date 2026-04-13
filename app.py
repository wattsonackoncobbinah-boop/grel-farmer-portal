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

# --- 1. DYNAMIC DATE CALCULATIONS ---
now = datetime.datetime.now()
today_str = now.strftime("%B %d, %Y")
two_days_ago = now - datetime.timedelta(days=2)
date_range = f"{two_days_ago.strftime('%b %d')} - {now.strftime('%b %d, %Y')}"

# --- 2. CONFIG & LOGO SETUP ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")
LOGO_URL = "logo.png"

# --- 2.5 WELCOME SPLASH SCREEN (LOGO COLOR MATCHED) ---
if 'welcome_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"""
            <style>
            .stApp {{
                background-color: #F2EDE4 !important;
                background-image: none !important;
            }}
            .welcome-title {{
                color: #000000 !important;
                font-size: 40px !important;
                font-weight: 800 !important;
                text-align: center;
                margin-top: 10px;
                text-shadow: none !important;
            }}
            </style>
        """, unsafe_allow_html=True)
        
        left, mid, right = st.columns([1, 2, 1])
        with mid:
            st.write("##") 
            try:
                st.image("logo.png", width=250)
            except:
                st.image("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/logo.png", width=250)
            
            st.markdown('<div class="welcome-title">BENJI GREL FARMER PORTAL</div>', unsafe_allow_html=True)
            st.write("<p style='text-align: center; color: #444; font-size: 18px;'>Connecting Ghana's Rubber Community...</p>", unsafe_allow_html=True)
            
            bar = st.progress(0)
            for i in range(100):
                time.sleep(0.05) 
                bar.progress(i + 1)
            
            st.success("✅ System Secure & Ready")
            time.sleep(1.2)
            
    placeholder.empty()
    st.session_state.welcome_done = True

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

@st.cache_data(ttl=3600)
def get_news_data(search_term):
    try:
        url = f"https://news.google.com/rss/search?q={search_term}&hl=en-GH&gl=GH&ceid=GH:en"
        response = requests.get(url, timeout=5)
        feed = feedparser.parse(response.content)
        return feed.entries[:5]
    except:
        return []

# --- 4. SESSION STATE & SIDEBAR ---
if 'sidebar_color' not in st.session_state:
    st.session_state.sidebar_color = "#DFE8DF"

if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = "Dark"

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    
    st.subheader("🖥️ Display Settings")
    toggle_theme = st.toggle("Switch to Light Mode", value=(st.session_state.theme_mode == "Light"))
    st.session_state.theme_mode = "Light" if toggle_theme else "Dark"
    
    st.divider()
    st.header("App Settings")
    admin_key = st.text_input("🔑 Programmer Key:", type="password")
    
    if admin_key == "yaw2026":
        with st.expander("🎨 Sidebar Theme"):
            chosen_color = st.color_picker("Sidebar Color", st.session_state.sidebar_color)
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

# --- 5. DYNAMIC CSS (FORCED CONTRAST) ---
if st.session_state.theme_mode == "Dark":
    bg_overlay = "rgba(0,0,0,0.8)"  # Darker for better visibility
    text_color = "#FFFFFF"         # Pure White
    shadow = "2px 2px 4px #000000"
else:
    bg_overlay = "rgba(255,255,255,0.85)"
    text_color = "#000000"         # Pure Black
    shadow = "none"

st.markdown(f"""
    <style>
    /* Force the main background */
    .stApp {{
        background: linear-gradient({bg_overlay}, {bg_overlay}), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg") !important;
        background-size: cover !important; 
        background-attachment: fixed !important;
    }}

    /* THE MAGIC FIX: This forces everything inside the 'main' class */
    .main .stMarkdown, .main .stText, .main h1, .main h2, .main h3, .main p, .main label {{
        color: {text_color} !important;
        text-shadow: {shadow} !important;
    }}

    /* Fix the Metric Values specifically */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] p {{
        color: {text_color} !important;
    }}

    /* Sidebar Protection: Keep it Dark Text regardless of theme */
    [data-testid="stSidebar"] {{
        background-color: {st.session_state.sidebar_color} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #1A1A1A !important;
        text-shadow: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CALCULATION ENGINE ---
def predict_grel_price(global_price, exchange_rate):
    k_factor = 0.365 
    calc = global_price * exchange_rate * k_factor
    return max(round(calc, 2), tcda_min_price)

prediction_dry = predict_grel_price(1.76, usd_to_ghs)

# --- 7. MAIN CONTENT ---
# --- 7. MAIN CONTENT (THEME-AWARE TITLES) ---
# Use this instead of st.title to guarantee the color changes
st.markdown(f"<h1 style='color:{text_color}; text-shadow:{shadow};'>🚜 BENJI GREL FARMER'S PORTAL</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color:{text_color}; text-shadow:{shadow};'>Live Status: {today_str}</h3>", unsafe_allow_html=True)

col_p, col_m = st.columns([1, 2])
with col_p:
    st.image("dad.jpg", width=300, caption="Portal Administrator")
with col_m:
    st.write("### Market Summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Exchange Rate", f"₵{usd_to_ghs}")
    m2.metric("GREL Gate Price", f"₵{current_grel_gate_price}")
    m3.metric("TCDA Floor", f"₵{tcda_min_price}")

# --- 8. PAYOUT CALCULATOR ---
st.divider()
st.subheader("💰 Payout Calculator")
c1, c2, c3 = st.columns(3)
with c1:
    wet_kg = st.number_input("Total Wet Weight (kg):", value=1000, step=100)
with c2:
    drc_val = st.slider("Select DRC %:", 40, 65, 52)
with c3:
    deduct_loan = st.checkbox("Apply 25% Loan Deduction", value=True)

wet_price = round(prediction_dry * (drc_val / 100), 2)
gross_total = round(wet_kg * wet_price, 2)
net_total = round(gross_total * 0.75, 2) if deduct_loan else gross_total

r1, r2, r3 = st.columns(3)
r1.metric("Predicted Dry Price", f"₵{prediction_dry}/kg")
r2.metric("Your Wet Price", f"₵{wet_price}/kg")
r3.metric("Take-Home", f"₵{net_total:,}")

# --- 9. THE CHART ---
st.subheader("📈 Live Global Rubber Market")
tradingview_html = """
<div style="height:450px; width:100%;"><div id="tv" style="height:100%;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({"autosize":true,"symbol":"SGX:TF1!","interval":"D","theme":"dark","container_id":"tv"});</script></div>
"""
components.html(tradingview_html, height=450)

# --- 10. NEWS DASHBOARD ---
st.divider()
st.subheader(f"📰 Industry News ({date_range})")

if st.button(f"🔄 Sync Feeds for {today_str}"):
    st.cache_data.clear()
    st.rerun()

col_l, col_i = st.columns(2)
with col_l:
    st.markdown("### 🇬🇭 Local: Ahanta West & Tarkwa")
    st.info(f"🌦️ **Weather:** Monitoring {today_str} conditions...")
    local_data = get_news_data("(GREL OR Apimanim OR Tarkwa OR Axim) rubber")
    if local_data:
        for entry in local_data:
            st.markdown(f"🔗 **[{entry.title}]({entry.link})**")
            st.caption(f"📅 {entry.published[:16]}")

with col_i:
    st.markdown("### 🌍 Global Market News")
    global_data = get_news_data("rubber market price global")
    if global_data:
        for entry in global_data:
            st.markdown(f"📈 **[{entry.title}]({entry.link})**")
            st.caption(f"Published: {entry.published[:16]}")

# --- 11. FOOTER ---
st.divider()
st.markdown(f"<p style='text-align: center; color: gray; font-size: 11px;'>BENJI LIMITED | Auto-Updated: {today_str}</p>", unsafe_allow_html=True)
