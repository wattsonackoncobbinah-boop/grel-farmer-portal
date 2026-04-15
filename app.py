import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import datetime
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

# --- 2.5 WELCOME SPLASH SCREEN (STRICTLY IMAGE ONLY) ---
if 'welcome_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"""
            <style>
            /* 1. Eliminate all default Streamlit spacing and scrolling */
            .stApp {{
                margin: 0px !important;
                padding: 0px !important;
            }}
            
            /* 2. Create a fullscreen fixed layer for the image */
            .img-splash {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-image: url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/Logo.png.png");
                background-size: cover; /* Stretches to fill whole screen */
                background-position: center;
                background-repeat: no-repeat;
                z-index: 999999; /* Higher than any other element */
            }}

            /* 3. Hide absolutely every other UI element */
            header, footer, .stDeployButton, [data-testid="stHeader"] {{
                display: none !important;
            }}
            </style>
            
            <div class="img-splash"></div>
        """, unsafe_allow_html=True)
        
        # Internal timer to keep the image up for 3 seconds
        time.sleep(3.0) 
        
    placeholder.empty()
    st.session_state.welcome_done = True



# --- 3. AUTOMATION FUNCTIONS ---
def get_live_exchange_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        return round(requests.get(url, timeout=5).json()['rates']['GHS'], 2)
    except: return 14.50

def scrape_rubber_price(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        matches = re.findall(r"₵\s?(\d+\.\d+)|GHS\s?(\d+\.\d+)", soup.get_text())
        if matches: return float([m for m in matches[0] if m][0])
        return None
    except: return None

@st.cache_data(ttl=3600)
def get_news_data(search_term):
    try:
        url = f"https://news.google.com/rss/search?q={search_term}&hl=en-GH&gl=GH&ceid=GH:en"
        response = requests.get(url, timeout=5)
        feed = feedparser.parse(response.content)
        return feed.entries[:5]
    except: return []

# --- 4. SESSION STATE & SIDEBAR ---
if 'sidebar_color' not in st.session_state: st.session_state.sidebar_color = "#DFE8DF"
if 'theme_mode' not in st.session_state: st.session_state.theme_mode = "Dark"

with st.sidebar:
    st.image(LOGO_URL, use_container_width=True)
    st.subheader("🖥️ Display Settings")
    toggle_theme = st.toggle("Switch to Light Mode", value=(st.session_state.theme_mode == "Light"))
    st.session_state.theme_mode = "Light" if toggle_theme else "Dark"
    st.divider()
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
        tcda_min_price = 9.11
        current_grel_gate_price = 8.30

# --- 5. DYNAMIC CSS (FINAL BOSS VERSION) ---
if st.session_state.theme_mode == "Dark":
    bg_overlay, text_color, metric_c, shadow = "rgba(0,0,0,0.8)", "#FFFFFF", "#FFFFFF", "2px 2px 4px #000000"
else:
    bg_overlay, text_color, metric_c, shadow = "rgba(255,255,255,0.85)", "#1A1A1A", "#2E7D32", "none"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient({bg_overlay}, {bg_overlay}), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg") !important;
        background-size: cover !important; background-attachment: fixed !important;
    }}
    .main * {{ color: {text_color}; text-shadow: {shadow}; }}
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] p {{ color: {metric_c} !important; }}
    section[data-testid="stSidebar"] {{ background-color: {st.session_state.sidebar_color} !important; }}
    [data-testid="stSidebar"] * {{ color: #1A1A1A !important; text-shadow: none !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 7. MAIN CONTENT ---
st.markdown(f"<h1 style='color:{text_color}; text-shadow:{shadow};'>🚜 BENJI GREL FARMER'S PORTAL</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='color:{text_color}; text-shadow:{shadow};'>Live Status: {today_str}</h3>", unsafe_allow_html=True)

col_p, col_m = st.columns([1, 2])
with col_p:
    st.image("dad.jpg", width=300, caption="Portal Administrator")
with col_m:
    st.markdown(f"<h3 style='color:{text_color};'>Market Summary</h3>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Exchange Rate", f"₵{usd_to_ghs}")
    m2.metric("GREL Gate Price", f"₵{current_grel_gate_price}")
    m3.metric("TCDA Floor", f"₵{tcda_min_price}")

# --- 8. PAYOUT CALCULATOR ---
st.divider()
st.markdown(f"<h2 style='color:{text_color};'>💰 Payout Calculator</h2>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<span style='color:{text_color};'>Total Wet Weight (kg):</span>", unsafe_allow_html=True)
    wet_kg = st.number_input("", value=1000, step=100, label_visibility="collapsed")
with c2:
    st.markdown(f"<span style='color:{text_color};'>Select DRC %:</span>", unsafe_allow_html=True)
    drc_val = st.slider("", 40, 65, 52, label_visibility="collapsed")
with c3:
    deduct_loan = st.checkbox("Apply 25% Loan Deduction", value=True)

prediction_dry = max(round(1.76 * usd_to_ghs * 0.365, 2), tcda_min_price)
wet_price = round(prediction_dry * (drc_val / 100), 2)
net_total = round((wet_kg * wet_price) * 0.75, 2) if deduct_loan else round(wet_kg * wet_price, 2)

r1, r2, r3 = st.columns(3)
r1.metric("Predicted Dry Price", f"₵{prediction_dry}/kg")
r2.metric("Your Wet Price", f"₵{wet_price}/kg")
r3.metric("Take-Home", f"₵{net_total:,}")

# --- 9. THE CHART ---
st.subheader("📈 Live Global Rubber Market")
components.html('<div style="height:400px;"><div id="tv" style="height:100%;"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"SGX:TF1!","interval":"D","theme":"dark","container_id":"tv"});</script></div>', height=400)

# --- 10. NEWS DASHBOARD ---
st.divider()
st.markdown(f"<h2 style='color:{text_color};'>📰 Industry News ({date_range})</h2>", unsafe_allow_html=True)
if st.button(f"🔄 Sync Feeds for {today_str}"):
    st.cache_data.clear()
    st.rerun()

col_l, col_i = st.columns(2)
with col_l:
    st.markdown(f"<h3 style='color:{text_color};'>🇬🇭 Local: Ahanta West</h3>", unsafe_allow_html=True)
    local_data = get_news_data("(GREL OR Apimanim OR Tarkwa OR Axim) rubber")
    if local_data:
        for entry in local_data:
            st.markdown(f"🔗 <a href='{entry.link}' style='color:#00FF88; font-weight:bold;'>{entry.title}</a>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:{text_color}; font-size:12px; margin-top:-15px;'>📅 {entry.published[:16]}</p>", unsafe_allow_html=True)

with col_i:
    st.markdown(f"<h3 style='color:{text_color};'>🌍 Global Market News</h3>", unsafe_allow_html=True)
    global_data = get_news_data("rubber market price global")
    if global_data:
        for entry in global_data:
            st.markdown(f"📈 <a href='{entry.link}' style='color:#00FF88; font-weight:bold;'>{entry.title}</a>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:{text_color}; font-size:12px; margin-top:-15px;'>Published: {entry.published[:16]}</p>", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: center; color: gray; font-size: 11px;'>BENJI LIMITED | Auto-Updated: {today_str}</p>", unsafe_allow_html=True)
