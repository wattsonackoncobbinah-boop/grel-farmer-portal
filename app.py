import streamlit as st
import streamlit.components.v1 as components

# --- 1. PAGE CONFIG (MUST BE FIRST) ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")

# --- 2. THE BACKGROUND & TEXT STYLING ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    h1, h2, h3, p, span, label, .stMetric {
        color: white !important;
        text-shadow: 2px 2px 4px #000000;
    }
    /* This makes the sidebar readable against the dark background */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 100, 0, 0.8);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. SIDEBAR ---
with st.sidebar:
    # Using the GitHub raw link for the logo ensures it loads every time
    st.image("https://www.grelghana.com/images/logo.png") 
    st.header("App Settings")
    st.write("Welcome, Farmer! Check the latest rubber rates below.")
    st.info("Updates every 15 minutes.")

# --- 4. HEADER & PORTRAIT ---
st.title("🚜 BENJI GREL FARMER'S PRICE & NEWS PORTAL")

# This puts your dad's photo and the key metrics side-by-side
top_col1, top_col2 = st.columns([1, 2])
with top_col1:
    st.image("dad.jpg", width=250, caption="Portal Administrator")
with top_col2:
    st.write("### Today's Market Summary")
    colA, colB = st.columns(2)
    colA.metric("Global Rubber", "$1.62", "+0.04")
    colB.metric("GREL Grade A", "7.40 GHS", "-0.10")

st.divider()

# --- 5. LIVE CHART SECTION ---
st.subheader("📈 Live Global Rubber Market (SICOM TSR20)")

tradingview_html = """
<div class="tradingview-widget-container" style="height:450px;width:100%;">
  <div id="tradingview_rubber"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "SGX:TF1!",
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "2",
    "locale": "en",
    "toolbar_bg": "#006400",
    "enable_publishing": false,
    "hide_top_toolbar": true,
    "save_image": false,
    "container_id": "tradingview_rubber"
  });
  </script>
</div>
"""
components.html(tradingview_html, height=450)

# --- 6. PRICE SUMMARY & NEWS ---
st.write(f"Last Market Update: **Friday, April 10, 2026**")
st.divider()

current_price = 8.12
next_month_price = 8.14

c1, c2 = st.columns(2)
with c1:
    st.metric("This Month's Price", f"GH₵ {current_price}", delta="+0.15")
with c2:
    st.metric("Next Month Prediction", f"GH₵ {next_month_price}", delta="+0.02")

st.subheader("📰 Why is the price changing?")
st.info("""
**Analysis:** Supply deficits in Asia and oil price fluctuations are driving the current trend. 
As shown in the chart, the global resistance level is holding, which is good news for local GREL prices.
""")

st.markdown("- [Verify April 2026 Prices on TCDA Website](https://tcda.gov.gh/news/)")
