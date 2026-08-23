import streamlit as st
import requests
import time

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Macro Liquidity Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME STYLING ---
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 0rem;}
    .metric-card {
        background-color: #111827; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #3B82F6;
        margin-bottom: 15px;
    }
    .metric-title {color: #9CA3AF; font-size: 14px; font-weight: bold; text-transform: uppercase;}
    .metric-value {color: #F9FAFB; font-size: 28px; font-weight: bold; font-family: monospace;}
    .alert-banner {
        padding: 15px; 
        border-radius: 8px; 
        background-color: #7F1D1D; 
        border: 1px solid #F87171;
        color: #FCA5A5;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- U.S. TREASURY API FETCH LOGIC ---
@st.cache_data(ttl=60)  
def fetch_comprehensive_macro_data():
    base_url = "https://treasury.gov"
    debt_url = f"{base_url}/v2/accounting/od/debt_to_penny"
    dts_url = f"{base_url}/v1/accounting/dts/dts_table_1"
    
    try:
        debt_res = requests.get(debt_url, params={"sort": "-record_date", "page[size]": "1"}, timeout=5).json()
        dts_res = requests.get(dts_url, params={
            "sort": "-record_date", 
            "filter": "account_type:Status of Treasury General Account (TGA) Balance",
            "page[size]": "1"
        }, timeout=5).json()
        
        debt_record = debt_res["data"][0]
        dts_record = dts_res["data"][0]
        
        total_debt = float(debt_record["tot_pub_debt_out_amt"])
        tga_balance = float(dts_record["close_today_amt"]) * 1_000_000
        
        current_trillion = int(total_debt // 1_000_000_000_000)
        next_milestone = (current_trillion + 1) * 1_000_000_000_000
        distance_to_breach = next_milestone - total_debt
        
        return {
            "success": True,
            "debt_date": debt_record["record_date"],
            "total_debt": total_debt,
            "current_trillion": current_trillion,
            "next_milestone": next_milestone,
            "distance_to_breach": distance_to_breach,
            "cash_date": dts_record["record_date"],
            "tga_balance": tga_balance
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- APPLICATION HEADER ---
st.title("🏦 Institutional Macro Liquidity Monitor")
st.subheader("Real-Time U.S. Treasury Capital Streams & Milestone Tracking")

# --- APP SIDEBAR ENGINE ---
st.sidebar.header("🛠️ Dashboard Configurations")
webhook_url = st.sidebar.text_input("Discord/Telegram Webhook URL", type="password", placeholder="https://...")
simulate_breach = st.sidebar.checkbox("Simulate Threshold Breach Alert", value=False)
auto_refresh = st.sidebar.selectbox("Auto Refresh Interval", ["Manual", "60 Seconds", "5 Minutes"])

if auto_refresh == "60 Seconds":
    time.sleep(60)
    st.rerun()

# --- MAIN CORE LOGIC ---
# Using the single consolidated layout function name
data = fetch_comprehensive_macro_data()

if data and data["success"]:
    
    # 🚨 HARD TRIGGER ALERTS WINDOW
    is_debt_critical = data["distance_to_breach"] < 15_000_000_000 or simulate_breach
    is_tga_critical = data["tga_balance"] < 100_000_000_000
    
    if is_debt_critical:
        st.markdown(f"""
            <div class="alert-banner">
                💥 <b>CRITICAL SYSTEM ALERT: APPROACHING MILESTONE EXTRACTION POINT</b><br>
                Total National Debt is now within striking distance of breaking into <b>${data['current_trillion'] + 1} Trillion</b>. 
                Expect active algorithmic shifts out of the DXY during the 15:00 GMT+3 London/NY trading overlap.
            </div>
        """, unsafe_allow_html=True)
        
    if is_tga_critical and not is_debt_critical:
        st.markdown(f"""
            <div class="alert-banner" style="background-color: #7C2D12; border-color: #FB923C; color: #FFEDD5;">
                ⚠️ <b>LIQUIDITY DEPLETION WARNING: TGA ACCOUNT DRYING UP</b><br>
                The Federal Government's cash operating capital has fallen under $100B. Watch out for abrupt volatility 
                or sudden unannounced text statements from the Treasury.
            </div>
        """, unsafe_allow_html=True)

    # 📊 LAYOUT: RENDER DATA IN 3 COLUMN TRACKERS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">🇺🇸 Total U.S. Sovereign Debt</div>
                <div class="metric-value">${data['total_debt']:,.2f}</div>
                <div style="color:#6B7280; font-size:12px; margin-top:5px;">Data Date: {data['debt_date']}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        color = "#EF4444" if is_debt_critical else "#10B981"
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-title">🎯 Distance to {data['current_trillion'] + 1}T Milestone</div>
                <div class="metric-value" style="color: {color};">${data['distance_to_breach']:,.2f}</div>
                <div style="color:#6B7280; font-size:12px; margin-top:5px;">Threshold Target: ${data['next_milestone']:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        color = "#EF4444" if is_tga_critical else "#F59E0B"
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color};">
                <div class="metric-title">🏛️ Fed Operating Account (TGA)</div>
                <div class="metric-value" style="color: {color};">${data['tga_balance']:,.2f}</div>
                <div style="color:#6B7280; font-size:12px; margin-top:5px;">Data Date: {data['cash_date']}</div>
            </div>
        """, unsafe_allow_html=True)

    # 📈 PROGRESS VISUALIZATION BARS
    st.write("---")
    st.subheader("📉 Trillion-Dollar Cycle Completion Progress")
    
    current_trillion_start = data["current_trillion"] * 1_000_000_000_000
    total_progress_width = data["total_debt"] - current_trillion_start
    percentage_filled = total_progress_width / 1_000_000_000_000
    
    st.progress(percentage_filled)
    st.write(f"The structural expansion toward the next trillion dollar mark is currently **{percentage_filled * 100:.2f}%** completed.")

    # 🗃️ RAW INTERACTIVE DATA SPECS FOR TRACKING
    with st.expander("🔍 View Raw JSON Web Engine Packets"):
        st.json(data)
        
else:
    st.error(f"❌ Could not establish stable link to the U.S. Treasury network: {data.get('error', 'Unknown Exception')}")
