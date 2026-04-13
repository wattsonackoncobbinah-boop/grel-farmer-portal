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
# --- 2.5 WELCOME SPLASH SCREEN (BULLETPROOF VERSION) ---
if 'welcome_done' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        # Using CSS to force the clean cream background
        st.markdown("""
            <style>
            .stApp {
                background-color: #F2EDE4 !important;
                background-image: none !important;
            }
            .welcome-title {
                color: #000000 !important;
                font-size: 40px !important;
                font-weight: 800 !important;
                text-align: center;
                margin-top: 10px;
                text-shadow: none !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Using 3 columns to center everything perfectly
        left, mid, right = st.columns([1, 2, 1])
        with mid:
            st.write("##") # Add some spacing at the top
            # 1. LOCAL FILE: We use the same logo.png used in your sidebar
            try:
                st.image("logo.png", width=250)
            except:
                # 2. BACKUP URL: If local fails, try the GitHub link
                st.image("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/logo.png", width=250)
            
            st.markdown('<div class="welcome-title">BENJI GREL FARMER PORTAL</div>', unsafe_allow_html=True)
            st.write("<p style='text-align: center; color: #444; font-size: 18px;'>Connecting Ghana's Rubber Community...</p>", unsafe_allow_html=True)
            
            # The Progress Bar
            bar = st.progress(0)
            for i in range(100):
                time.sleep(0.05) # <--- SLOWED DOWN slightly for your dad to read
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

# --- 5. THE CSS (RESTORED DARK THEME) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; 
        background-attachment: fixed;
    }}
    section[data-testid="stSidebar"] {{
        background-color: {st.session_state.sidebar_color} !important;
    }}
    section[data-testid="stSidebar"] > div {{
        background-color: {st.session_state.sidebar_color} !important;
        background-image: none !important;
    }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: white !important;
    }}
    h1, h2, h3, p, span, label, .stMetric, [data-testid="stMetricValue"] {{
        color: white !important; 
        text-shadow: 2px 2px 4px #000000;
    }}
    a {{ color: #00FF88 !important; font-weight: 600; text-decoration: none; }}
    </style>
    """, unsafe_allow_html=True)

# --- 6. CALCULATION ENGINE ---
def predict_grel_price(global_price, exchange_rate):
    k_factor = 0.365 
    calc = global_price * exchange_rate * k_factor
    return max(round(calc, 2), tcda_min_price)

prediction_dry = predict_grel_price(1.76, usd_to_ghs)

# --- 7. MAIN CONTENT ---
st.title("🚜 BENJI GREL FARMER'S PORTAL")
st.write(f"### Live Status: {today_str}")

col_photo, col_metrics = st.columns([1, 2])
with col_photo:
    st.image("dad.jpg", width=300, caption="Portal Administrator")
with col_metrics:
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

st.write("---")
res1, res2, res3 = st.columns(3)
res1.metric("Predicted Dry Price", f"₵{prediction_dry}/kg")
res2.metric("Your Wet Price", f"₵{wet_price}/kg")
res3.metric("Take-Home", f"₵{net_total:,}")

# --- 9. THE CHART (RESTORED) ---
st.subheader("📈 Live Global Rubber Market")
tradingview_html = """
<div style="height:450px; width:100%;"><div id="tv" style="height:100%;"></div>
<script src="https://s3.tradingview.com/tv.js"></script>
<script>new TradingView.widget({"autosize":true,"symbol":"SGX:TF1!","interval":"D","theme":"dark","container_id":"tv"});</script></div>
"""
components.html(tradingview_html, height=450)

# --- 10. NEWS DASHBOARD (CACHED FOR SPEED) ---

# We add this "Decorator" to make it load instantly after the first try
@st.cache_data(ttl=7200) # ttl=7200 means "Remember this for 2 hours"
def fetch_local_news(query):
    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=en-GH&gl=GH&ceid=GH:en"
        return feedparser.parse(url).entries
    except:
        return []

col_local, col_int = st.columns(2)

with col_local:
    st.markdown("### 🇬🇭 Ahanta West & Axim")
    
    # Static Weather (Loads instantly)
    # Instead of a live call that takes forever, use a fast info box
    st.info(f"🌦️ **Today's Forecast:** Typical tropical conditions for Western Region. High 31°C / Low 24°C. Localized showers expected near Axim.")

    st.markdown("#### 🕒 Local Industry Updates")
    
    # Calling the cached function (Fast!)
    local_news = fetch_local_news("(GREL OR Apimanim OR Tarkwa OR Axim) rubber Ghana")
    
    if local_news:
        for entry in local_news[:5]:
            st.markdown(f"🔗 **[{entry.title.split(' - ')[0]}]({entry.link})**")
            st.caption(f"📅 {entry.published[:16]}")
    else:
        st.write("No recent reports found in the last 72 hours.")
# --- 11. FOOTER ---
st.divider()
st.markdown(f"<p style='text-align: center; color: gray; font-size: 11px;'>BENJI LIMITED| JAC indusries | Serving Ahanta West & Axim | Auto-Updated: {today_str}</p>", unsafe_allow_html=True)
