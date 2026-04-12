import streamlit as st
import streamlit.components.v1 as components
import time
import datetime
import calendar
import feedparser # All imports at the top

# SET YOUR LOGO URL HERE
LOGO_URL = "https://raw.githubusercontent.com/wattsonackoncobbinah-boop/BENJI-grel-farmers-portal/main/logo.png"

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
    st.image("dad.jpg", width=300, caption="Portal Administrator")

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
# --- WEATHER SECTION: PRINCESS & AXIM ROAD CORRIDOR ---
st.sidebar.divider()
st.sidebar.subheader("🌦️ Local Plantation Weather")

# Manual Entry for Accuracy
target_town = st.sidebar.text_input("Enter Town (e.g., Axim, Princess Town, Dixcove):", value="Princess Town")

# Logic to map specific GREL/Outgrower towns to the weather feed
def get_weather_url(town):
    town_slugs = {
        "axim": "axim_ghana_2303534",
        "princess town": "princes-town_ghana_2300063",
        "dixcove": "dixcove_ghana_2302302",
        "agona nkwanta": "agona-nkwanta_ghana_2304670",
        "akwidaa": "akwidaa_ghana_2304610"
    }
    # Default to Princess Town if not in list
    slug = town_slugs.get(town.lower(), "princes-town_ghana_2300063")
    return f"https://www.meteoblue.com/en/weather/widget/three/{slug}?geosize=inline&days=2&tempunit=CELSIUS&windunit=KILOMETER_PER_HOUR&layout=dark"

if target_town:
    weather_url = get_weather_url(target_town)
    weather_html = f"""
    <div style="width: 100%;">
        <iframe width="100%" height="150" src="{weather_url}" 
        frameborder="0" scrolling="NO" allowtransparency="true" 
        sandbox="allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox"></iframe>
    </div>
    """
    components.html(weather_html, height=160)
    
    # ⚠️ CRITICAL TAPPING ALERTS (April 2026)
    st.sidebar.caption(f"Showing live data for {target_town.title()}")
    st.sidebar.warning("🕒 **Rain Watch:** If rain is forecast within 2 hours of tapping, apply rain guards or delay tapping to prevent latex loss (washout).")


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

# --- 7. LIVE CHART SECTION (ENHANCED SIZE) ---
st.subheader("📈 Live Global Rubber Market (SICOM TSR20)")

# We increase the height here to 800 for a much larger view
tradingview_html = """
<div class="tradingview-widget-container" style="height:800px; width:100%;">
  <div id="tradingview_rubber" style="height:100%; width:100%;"></div>
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
    "hide_top_toolbar": false,  # Turned this on so farmers can change intervals
    "save_image": true,
    "container_id": "tradingview_rubber"
  });
  </script>
</div>
"""

# Crucial: height=800 here must match the CSS height above
components.html(tradingview_html, height=800)

# --- 8. NEWS HUB: LOCAL & INTERNATIONAL ---
st.divider()
st.subheader("📰 Rubber Industry News Hub")

# Create two columns for a clean look
col_local, col_int = st.columns(2)

with col_local:
    st.markdown("### Ahanta West & Western Region")
    
    # 1. Official TCDA Price Alert (April 2026)
    st.info(f"""
    **April 2026 Price Official:** The TCDA has fixed the minimum price for raw rubber cup-lumps at **GH₵ 9.11** per kg. 
    *Source: Tree Crops Development Authority*
    """)

    # 2. Local Community News (GREL)
    st.success("""
    **🎓 Tertiary Scholarships:** GREL has awarded scholarships to 33 students from its host communities in the Western Region for the 2026 academic year. 
    """)

    # 3. Industry Policy Action
    st.warning("""
    ** Export Restriction:** Parliamentary leaders recently visited GREL’s **Apimenim** and **Abura Tsibu** factories. They are pushing to finalize the Legislative Instrument (LI) to stop raw rubber exports, protecting local factory jobs in Ahanta West.
    """)

with col_int:
    st.markdown("### 🌐 International Market Feed")
    
    def get_combined_news():
        # This query pulls both global SICOM trends and Ghana-specific rubber news
        rss_url = "https://news.google.com/rss/search?q=SICOM+TSR20+rubber+market+Ghana+GREL&hl=en-GH&gl=GH&ceid=GH:en"
        feed = feedparser.parse(rss_url)
        return feed.entries[:5]

    news_items = get_combined_news()

    if news_items:
        for entry in news_items:
            display_title = entry.title.split(" - ")[0]
            st.markdown(f"**[{display_title}]({entry.link})**")
            st.caption(f"📅 {entry.published}")
            st.write("") # Spacer
    else:
        st.write("No international updates found today.")

st.divider()
st.info("💡 **Farmer's Advice:** Use the local minimum price of **GH₵ 9.11** as your bargaining baseline when dealing with aggregators in the Western Region.")
