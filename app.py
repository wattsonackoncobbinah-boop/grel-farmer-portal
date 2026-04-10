import streamlit as st
import streamlit.components.v1 as components

# --- 1. DATA & SETUP ---
# (Using our established benchmarks for April 10, 2026)
current_price = 8.12
next_month_price = 8.14

st.set_page_config(page_title="Farmer Price & News Portal", layout="wide")

# --- 2. HEADER ---
st.title("🚜 GREL Farmer Price & News Portal")
st.write(f"Last Market Update: **Friday, April 10, 2026**")

st.divider()

# --- 3. LIVE CHART SECTION (The New Addition) ---
st.subheader("📈 Live Global Rubber Market (SICOM TSR20)")
st.write("This chart shows how the world price is moving in Singapore right now.")

# TradingView Widget HTML code
tradingview_html = """
<div class="tradingview-widget-container" style="height:400px;width:100%;">
  <div id="tradingview_rubber"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "autosize": true,
    "symbol": "SGX:TF1!",
    "interval": "D",
    "timezone": "Etc/UTC",
    "theme": "light",
    "style": "2",
    "locale": "en",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_top_toolbar": true,
    "save_image": false,
    "container_id": "tradingview_rubber"
  });
  </script>
</div>
"""

# Render the chart in Streamlit
components.html(tradingview_html, height=450)

# --- 4. PRICE SUMMARY & NEWS ---
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.metric("This Month's Price", f"GH₵ {current_price}", delta="+0.15")
with col2:
    st.metric("Next Month Prediction", f"GH₵ {next_month_price}", delta="+0.02")

# News & Reasoning
st.subheader("📰 Why is the price changing?")
st.info("""
**Today's Reasoning:** The chart above shows a steady climb. This is due to the **supply deficit** in Asia and the high cost of oil. As long as that blue line on the chart stays high, 
your payout in Ghana will remain strong.
""")

st.markdown("- [Verify April 2026 Prices on TCDA Website](https://tcda.gov.gh/news/)")