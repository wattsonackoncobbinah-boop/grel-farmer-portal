import streamlit as st
import streamlit.components.v1 as components

# --- 1. SET PAGE CONFIG (THIS MUST BE THE VERY FIRST STREAMLIT COMMAND) ---
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")

# --- 2. BACKGROUND & TEXT STYLING ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        
        /* Change 'cover' to a percentage like 600% to zoom in more */
        background-size: 600%; 
        
        background-position: center top; /* This keeps his face at the top */
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    /* This makes all text bright white and adds a shadow for clarity */
    h1, h2, h3, p, span, label, .stMetric {
        color: white !important;
        text-shadow: 2px 2px 4px #000000;
    }
    /* Styles the sidebar to be readable */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 70, 0, 0.9);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://www.grelghana.com/images/logo.png") 
    st.header("App Settings")
    st.write("Welcome, Farmer! Check the latest rubber rates below.")
    st.info("Updates every 15 minutes.")

# --- 4. HEADER & DAD'S PHOTO ---
st.title("🚜 BENJI GREL FARMER'S PRICE & NEWS PORTAL")

col_photo, col_metrics = st.columns([1, 2])
with col_photo:
    # Make sure 'dad.jpg' is exactly what you named your file on GitHub!
    st.image("dad.jpg", width=600, caption="Portal Administrator")

with col_metrics:
    st.write("### Today's Market Summary")
    m1, m2 = st.columns(2)
    m1.metric("Global Rubber", "$1.62", "+0.04")
    m2.metric("GREL Grade A", "7.40 GHS", "-0.10")

st.divider()

# --- 5. LIVE CHART SECTION ---
st.subheader("📈 Live Global Rubber Market (SICOM TSR20)")

tradingview_html = """
<div class="tradingview-widget-container" style="height:700px;width:100%;">
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
components.html(tradingview_html, height=700)

import feedparser # Add this to your imports at the very top

import feedparser

# --- 6. BOLD & READABLE NEWS LINKS ---
st.divider()
st.subheader("📰 Latest Rubber Industry News")

def get_news_links():
    # Searching Google News specifically for GREL and Ghana Rubber
    rss_url = "https://news.google.com/rss/search?q=GREL+Ghana+Rubber+Price&hl=en-GH&gl=GH&ceid=GH:en"
    feed = feedparser.parse(rss_url)
    return feed.entries[:5]

news_items = get_news_links()

if news_items:
    for entry in news_items:
        # Clean the title
        display_title = entry.title.split(" - ")[0]
        
        # We use '###' to make the link look like a bold header
        # and [Text](Link) to keep it clickable.
        st.markdown(f"### 🔗 **[{display_title}]({entry.link})**")
        
        # Keeping the source and date smaller so the focus stays on the headline
        st.caption(f"**Source:** {entry.source.title} | **Published:** {entry.published}")
        st.markdown("---") # Adds a clean separator line
else:
    st.write("No new rubber industry updates found today.")

st.info("💡 **Tip:** Tap any bold headline above to read the full report.")
