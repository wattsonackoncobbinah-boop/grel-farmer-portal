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
    /* 1. Main App Background (Always the Image) */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; 
        background-attachment: fixed;
    }}
    
    /* 2. SPECIFIC SIDEBAR OVERRIDE */
    [data-testid="stSidebar"] {{
        background-color: {st.session_state.sidebar_color} !important;
        background-image: none !important; /* Ensures the main background image doesn't bleed in */
    }}

    /* 3. Text Visibility in Sidebar */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: white !important;
    }}

    /* 4. Main Content Text */
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
components.html(tradingview_html, height=500)

st.divider()
# News feed feedparser logic here...

# --- 11. NEWS HUB (RESTORED) ---
st.divider()
st.subheader("📰 Rubber Industry News Hub")

col_local, col_int = st.columns(2)

with col_local:
    st.markdown("### 🇬🇭 Local Updates")
    st.info(f"**Official Floor:** TCDA fixed minimum at **GH₵ {tcda_min_price}/kg**.")
    st.success("**Community:** GREL 2026 Scholarship awards are now being processed for qualifying students in the Western Region.")
    st.warning("**Weather Note:** Check the sidebar rain alerts before planning your washout schedule.")

with col_int:
    st.markdown("### 🌍 International Feed")
    try:
        # Fetching latest rubber news from Google News RSS
        news_url = "https://news.google.com/rss/search?q=rubber+market+Ghana&hl=en-GH&gl=GH&ceid=GH:en"
        feed = feedparser.parse(news_url)
        
        # Display the top 3 news stories
        for entry in feed.entries[:3]:
            st.markdown(f"**[{entry.title.split(' - ')[0]}]({entry.link})**")
            st.caption(f"Published: {entry.published}")
    except Exception as e:
        st.error("Could not load international news feed at this time.")

# --- 12. FOOTER ---
st.divider()
st.markdown(
    f"""
    <div style="text-align: center; color: gray;">
        <p>BENJI LIMITED Portal v2.0 | Admin: { "Yaw (Manual Mode)" if 'use_manual' in locals() and use_manual else "Automated System" }</p>
    </div>
    """, 
    unsafe_allow_html=True
)
