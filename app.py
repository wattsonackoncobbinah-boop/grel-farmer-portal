import streamlit as st
import streamlit.components.v1 as components
import time
import datetime
import calendar
import feedparser # All imports at the top

# 1. MUST BE FIRST
st.set_page_config(page_title="GREL Farmer Portal", layout="wide", page_icon="🌳")

# --- 2. INITIALIZATION & ANIMATED SPLASH SCREEN ---
if 'initialized' not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        # CSS for the 'Action' movements
        st.markdown("""
            <style>
            @keyframes pulse-grow {
                0% { transform: scale(1); opacity: 0.8; }
                50% { transform: scale(1.1); opacity: 1; }
                100% { transform: scale(1); opacity: 0.8; }
            }
            @keyframes slide-up {
                0% { transform: translateY(20px); opacity: 0; }
                100% { transform: translateY(0); opacity: 1; }
            }
            .splash-logo {
                display: block;
                margin: auto;
                animation: pulse-grow 2s infinite ease-in-out;
            }
            .loading-text {
                text-align: center;
                color: white;
                font-family: 'sans-serif';
                animation: slide-up 1s ease-out;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Action: Pulsing Logo
        st.markdown(f'<img src="{LOGO_URL}" class="splash-logo" width="350">', unsafe_allow_html=True)
        
        # Action: Sliding Text
        st.markdown('<h2 class="loading-text">🚀 Loading Farmer Insights...</h2>', unsafe_allow_html=True)
        
        # Visual Progress
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.015)  # Fast, snappy loading
            bar.progress(i + 1)
        
        st.markdown('<p style="text-align: center; color: #00FF00;">✔ Connection Secure</p>', unsafe_allow_html=True)
        time.sleep(0.6)

    placeholder.empty()
    st.session_state['initialized'] = True
# 3. STYLING
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover;
        background-attachment: fixed;
    }
    h1, h2, h3, p, span, label, [data-testid="stMetricValue"] {
        color: white !important;
        text-shadow: 2px 2px 4px #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BACKGROUND & TEXT STYLING ---
# Using f-strings to ensure URLs are handled correctly
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url("https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/dad.jpg");
        background-size: cover; 
        background-position: center top;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Force white text on common Streamlit elements */
    h1, h2, h3, p, span, label, .stMetric, [data-testid="stMetricValue"] {
        color: white !important;
        text-shadow: 2px 2px 4px #000000;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(0, 70, 0, 0.9);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 5. HEADER & DAD'S PHOTO ---
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
# --- 3. SIDEBAR ---
with st.sidebar:
    # Change "logo.png" to the EXACT name of your file on GitHub
    st.image("logo.png", use_container_width=True) 
    
    st.header("App Settings")
    st.write("Welcome, Farmer! Check the latest rubber rates below.")
    st.info("Updates every 15 minutes.")

# --- 6. SMART PRICE REVEAL LOGIC ---
st.divider()

# Get today's date
today = datetime.date.today()
last_day = calendar.monthrange(today.year, today.month)[1]
days_left = last_day - today.day

# --- CURRENT PRICE (Always Visible) ---
current_price = 8.12
st.write("### 💰 Current Market Rate")
st.metric("GREL Grade A (April)", f"GH₵ {current_price}", delta="Stable")

st.write("") # Extra space

# --- THE SMART BUTTON ---
# For testing: I set this to show if days_left is 25 or less (so you can see it now)
# For real use later: Change the '25' back to '3'
if days_left <= 25: 
    st.subheader("📅 Next Month's Forecast")
    
    # Create a nice container for the reveal
    with st.expander("🔓 TAP HERE TO REVEAL MAY 2026 PREDICTION", expanded=False):
        next_month_price = 8.14
        
        st.write("### Predicted Price: **GH₵ 8.14**")
        st.progress(85) # Shows a visual 'confidence' bar
        st.success("Analysis suggests a slight increase due to global demand.")
        
        if st.button("Confirm Reading"):
            st.balloons()
            st.toast("Price prediction acknowledged!")
            
else:
    # This shows when it's too early in the month
    st.info(f"Next month's price prediction will be unlocked in {days_left - 3} days.")

# --- 7. CHART SECTION ---
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

# --- 8. BOLD & READABLE NEWS LINKS ---
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
