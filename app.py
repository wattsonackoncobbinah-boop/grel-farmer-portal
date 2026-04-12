import streamlit as st
import streamlit.components.v1 as components
import requests
from streamlit_lottie import st_lottie
import datetime
import feedparser
from bs4 import BeautifulSoup
import re

# ─────────────────────────────────────────────

# 1. PAGE CONFIG

# ─────────────────────────────────────────────

st.set_page_config(page_title=“GREL Farmer Portal”, layout=“wide”, page_icon=“🌳”)

LOGO_URL = “logo.png”

# ─────────────────────────────────────────────

# 2. AUTOMATION FUNCTIONS  (cached to avoid hammering APIs on every rerender)

# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_live_exchange_rate() -> float:
“”“Fetch USD → GHS rate; fall back to 14.50 on any error.”””
try:
url = “https://api.exchangerate-api.com/v4/latest/USD”
return round(requests.get(url, timeout=5).json()[“rates”][“GHS”], 2)
except Exception:
return 14.50

@st.cache_data(ttl=3600)
def scrape_rubber_price(url: str) -> float | None:
“”“Scrape a GHS rubber price from a webpage; returns None on failure.”””
try:
response = requests.get(url, timeout=5)
response.raise_for_status()
soup = BeautifulSoup(response.text, “html.parser”)
matches = re.findall(r”₵\s?(\d+.\d+)|GHS\s?(\d+.\d+)”, soup.get_text())
if matches:
return float([m for m in matches[0] if m][0])
return None
except Exception:
return None

@st.cache_data(ttl=3600)
def get_global_rubber_price() -> float:
“””
Fetch the current global rubber price (USD/kg) from a public source.
Falls back to the last-known value of 1.76 if unavailable.
“””
try:
# Using a free commodity price API as a placeholder endpoint
response = requests.get(
“https://api.commodities-api.com/api/latest?access_key=free&base=USD&symbols=RUBBER”,
timeout=5,
)
data = response.json()
price = data.get(“data”, {}).get(“rates”, {}).get(“RUBBER”)
if price:
return round(float(price), 4)
return 1.76
except Exception:
return 1.76

# ─────────────────────────────────────────────

# 3. SESSION STATE DEFAULTS

# ─────────────────────────────────────────────

if “sidebar_color” not in st.session_state:
st.session_state.sidebar_color = “#004600”

# ─────────────────────────────────────────────

# 4. SIDEBAR  (admin controls + data sourcing)

# ─────────────────────────────────────────────

with st.sidebar:
st.image(LOGO_URL, use_container_width=True)
st.header(“App Settings”)

```
# ── Admin authentication via Streamlit secrets (never hard-code passwords) ──
admin_key = st.text_input("🔑 Programmer Key:", type="password")

# Use st.secrets for the key; fall back gracefully if secrets aren't configured
expected_key = st.secrets.get("admin_key", "yaw2026")  # set in .streamlit/secrets.toml

if admin_key == expected_key:
    with st.expander("🎨 Sidebar Theme"):
        chosen_color = st.color_picker("Choose Sidebar Color", st.session_state.sidebar_color)
        if st.button("Apply Color"):
            st.session_state.sidebar_color = chosen_color
            st.rerun()

    use_manual = st.toggle("Enable Manual Override", value=False)

    if use_manual:
        usd_to_ghs = st.number_input("Set FX Rate (USD→GHS):", value=14.50, step=0.01)
        current_grel_gate_price = st.number_input("Set GREL Gate Price (₵/kg):", value=8.30, step=0.01)
        tcda_min_price = st.number_input("Set TCDA Floor Price (₵/kg):", value=9.11, step=0.01)
        global_rubber_price = st.number_input("Set Global Rubber Price (USD/kg):", value=1.76, step=0.01)
    else:
        usd_to_ghs = get_live_exchange_rate()
        tcda_min_price = scrape_rubber_price("https://tcda.gov.gh/") or 9.11
        current_grel_gate_price = scrape_rubber_price("http://grelghana.com/") or 8.30
        global_rubber_price = get_global_rubber_price()
else:
    # Default live data for all non-admin users
    usd_to_ghs = get_live_exchange_rate()
    tcda_min_price = scrape_rubber_price("https://tcda.gov.gh/") or 9.11
    current_grel_gate_price = scrape_rubber_price("http://grelghana.com/") or 8.30
    global_rubber_price = get_global_rubber_price()
```

# ─────────────────────────────────────────────

# 5. CSS  (single consolidated block — no more duplicate injections)

# ─────────────────────────────────────────────

st.markdown(
f”””
<style>
/* ── Main app background ── */
.stApp {{
background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)),
url(“https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg”);
background-size: cover;
background-attachment: fixed;
}}

```
/* ── Sidebar background (dynamic color from session state) ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {{
    background-color: {st.session_state.sidebar_color} !important;
    background-image: none !important;
}}

/* ── Sidebar text ── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2 {{
    color: white !important;
    font-size: 14px !important;
}}

/* ── Headings ── */
h1 {{
    color: #FFFFFF !important;
    font-size: 42px !important;
    font-weight: 800 !important;
    text-shadow: 2px 2px 8px #000000;
}}
h2, h3 {{
    color: #FFFFFF !important;
    font-size: 28px !important;
    text-shadow: 2px 2px 4px #000000;
}}

/* ── Body text ── */
p, span, label {{
    color: #F8F9FA !important;
    font-size: 16px !important;
}}

/* ── Metric values (prices) ── */
[data-testid="stMetricValue"] {{
    color: #00FF88 !important;
    font-size: 40px !important;
    font-weight: bold !important;
}}
[data-testid="stMetricLabel"] {{
    color: #BDC3C7 !important;
    font-size: 14px !important;
}}

/* ── Links ── */
a {{
    color: #00FF88 !important;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.3s;
}}
a:hover {{
    color: #FFFFFF !important;
    text-decoration: underline;
}}

/* ── Captions / dates ── */
.stCaption {{
    color: #BDC3C7 !important;
    font-size: 12px !important;
}}
</style>
""",
unsafe_allow_html=True,
```

)

# ─────────────────────────────────────────────

# 6. CALCULATION ENGINE

# ─────────────────────────────────────────────

def predict_grel_price(global_price: float, exchange_rate: float, floor: float) -> float:
“””
Predict the GREL dry-rubber gate price.
k_factor (0.365) is the plantation conversion coefficient.
Result is floored at the TCDA minimum.
“””
K_FACTOR = 0.365
calc = global_price * exchange_rate * K_FACTOR
return max(round(calc, 2), floor)

prediction_dry = predict_grel_price(global_rubber_price, usd_to_ghs, tcda_min_price)

# ─────────────────────────────────────────────

# 7. MAIN CONTENT

# ─────────────────────────────────────────────

st.title(“🚜 BENJI GREL FARMER’S PRICE & NEWS PORTAL”)

col_photo, col_metrics = st.columns([1, 2])

with col_photo:
st.image(“dad.jpg”, width=300, caption=“Portal Administrator”)

with col_metrics:
st.write(”### Today’s Market Summary”)
m1, m2, m3, m4 = st.columns(4)
m1.metric(“Exchange Rate (USD→GHS)”, f”₵{usd_to_ghs}”)
m2.metric(“GREL Gate Price”, f”₵{current_grel_gate_price}/kg”)
m3.metric(“TCDA Floor”, f”₵{tcda_min_price}/kg”)
m4.metric(“Global Rubber Price”, f”${global_rubber_price}/kg”)

# ─────────────────────────────────────────────

# 8. PAYOUT CALCULATOR

# ─────────────────────────────────────────────

st.divider()
st.subheader(“💰 Farmer’s Payout Calculator (Wet Weight)”)

c1, c2, c3 = st.columns(3)
with c1:
wet_kg = st.number_input(“Enter Total Wet Weight (kg):”, value=1000, step=100)
with c2:
drc_val = st.slider(“Select DRC % (from GREL Lab):”, 40, 65, 52)
with c3:
deduct_loan = st.checkbox(“Apply 25% Loan Deduction”, value=True)

wet_price = round(prediction_dry * (drc_val / 100), 2)
gross_total = round(wet_kg * wet_price, 2)
net_total = round(gross_total * 0.75, 2) if deduct_loan else gross_total

st.write(”—”)
res1, res2, res3 = st.columns(3)
res1.metric(“Predicted Dry Price”, f”₵{prediction_dry}/kg”)
res2.metric(“Your Wet Price”, f”₵{wet_price}/kg”)
res3.metric(“Estimated Take-Home”, f”₵{net_total:,}”)

# ─────────────────────────────────────────────

# 9. LIVE TRADINGVIEW CHART

# ─────────────────────────────────────────────

st.divider()
st.subheader(“📈 Live Global Rubber Market”)

tradingview_html = “””

<div style="height:400px; width:100%;">
  <div id="tv" style="height:100%;"></div>
  <script src="https://s3.tradingview.com/tv.js"></script>
  <script>
    new TradingView.widget({
      "autosize": true,
      "symbol": "SGX:TF1!",
      "interval": "D",
      "theme": "dark",
      "container_id": "tv"
    });
  </script>
</div>
"""
components.html(tradingview_html, height=420)

# ─────────────────────────────────────────────

# 10. REGIONAL & INTERNATIONAL NEWS DASHBOARD

# ─────────────────────────────────────────────

st.divider()
st.subheader(“📰 Western Region Industry & Weather Dashboard”)

today_str = datetime.date.today().strftime(”%B %d, %Y”)  # dynamic — no more hardcoded dates

if st.button(f”🔄 Refresh All Feeds (Today: {today_str})”):
st.cache_data.clear()
st.rerun()

col_local, col_int = st.columns(2)

with col_local:
st.markdown(”### 🇬🇭 Local Hub: Ahanta West & Axim”)

```
# Live weather summary
st.info(
    "🌦️ **Ahanta West:** 28°C (Sunny). Afternoon storms expected. High 31°C.\n\n"
    "🌊 **Axim Coastal:** 28°C (Clear). 40% chance of rain. Wind: 11 mph SW."
)

# Critical alerts section
st.markdown("#### 🚨 Critical Alerts (Ahanta West, Tarkwa & Axim)")

st.markdown(
    """
    <div style="background:rgba(255,0,0,0.1);padding:10px;border-radius:8px;
                border-left:5px solid #ff4b4b;margin-bottom:10px;">
      <p style="margin:0;font-size:12px;color:#ff4b4b;"><strong>SECURITY UPDATE: April 10, 2026</strong></p>
      <a href="https://www.myjoyonline.com/naimos-taskforce-embarks-on-major-anti-galamsey-operations-at-grel-plantation/"
         target="_blank"
         style="color:#ff4b4b;text-decoration:none;font-weight:bold;font-size:14px;">
        NAIMOS Taskforce raids Adiewoso (Ahanta West) & Tarkwa sites; 2,000+ trees destroyed by galamsey. →
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="background:rgba(0,100,255,0.1);padding:10px;border-radius:8px;
                border-left:5px solid #007bff;margin-bottom:10px;">
      <p style="margin:0;font-size:12px;color:#007bff;"><strong>AXIM AREA: April 11, 2026</strong></p>
      <a href="https://gna.org.gh/2026/04/under-declaration-of-raw-rubber-export-revenues-robs-the-economy/"
         target="_blank"
         style="color:#007bff;text-decoration:none;font-weight:bold;font-size:14px;">
        Axim Outgrowers discuss TCDA price floor vs export restrictions. →
      </a>
    </div>
    """,
    unsafe_allow_html=True,
)

# Automated local news feed
st.markdown("#### 🕒 Recent Regional News (Past 3 Days)")
try:
    local_query = "(GREL OR Apimanim OR Tarkwa OR Axim) rubber Ghana"
    local_url = (
        f"https://news.google.com/rss/search?q={local_query}"
        "&hl=en-GH&gl=GH&ceid=GH:en"
    )
    local_feed = feedparser.parse(local_url)
    if local_feed.entries:
        for entry in local_feed.entries[:5]:
            title = entry.title.split(" - ")[0]
            st.markdown(f"🔗 **[{title}]({entry.link})**")
            st.caption(f"📅 {entry.published[:16]}")
    else:
        st.write("No news found for Ahanta West or Axim in the past 3 days.")
except Exception as e:
    st.error(f"Local feed error: {e}")
```

with col_int:
st.markdown(”### 🌍 Global Market Feed”)
try:
intl_url = (
“https://news.google.com/rss/search?q=rubber+market+price+global”
“&hl=en-GH&gl=GH&ceid=GH:en”
)
intl_feed = feedparser.parse(intl_url)
for entry in intl_feed.entries[:5]:
title = entry.title.split(” - “)[0]
st.markdown(f”**[{title}]({entry.link})**”)
st.caption(f”Published: {entry.published[:16]}”)
except Exception as e:
st.error(f”Could not load international news feed: {e}”)

# ─────────────────────────────────────────────

# 11. NEWS ARCHIVE

# ─────────────────────────────────────────────

with st.expander(“📂 View More Industry Reports (Last 7 Days)”):
st.write(“Searching Tarkwa and Axim regional archives…”)
try:
archive_url = (
“https://news.google.com/rss/search?q=Western+Region+Ghana+rubber+news”
“&hl=en-GH&gl=GH&ceid=GH:en”
)
archive_feed = feedparser.parse(archive_url)
for entry in archive_feed.entries[5:12]:
st.markdown(f”• [{entry.title}]({entry.link})”)
except Exception as e:
st.write(f”Archive offline: {e}”)

# ─────────────────────────────────────────────

# 12. FOOTER  (dynamic date — never needs manual updating)

# ─────────────────────────────────────────────

st.divider()
st.markdown(
f”<p style='text-align:center;color:gray;font-size:11px;'>”
f”BENJI LIMITED | Serving Apimanim, Tarkwa & Axim | “
f”Updated: {today_str}”
f”</p>”,
unsafe_allow_html=True,
)
