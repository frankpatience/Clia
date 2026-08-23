import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="US Debt Micro-Movement Tracker",
    page_icon="📈",
    layout="wide"
)

# Constants
TARGET_THRESHOLD = 40_000_000_000_000.00  # $40 Trillion
API_URL = "https://treasury.gov"

@st.cache_data(ttl=300)  # Cache API response for 5 minutes to prevent rate limiting
def fetch_debt_data():
    """Fetches the latest national debt figures from the US Treasury API."""
    params = {
        "sort": "-record_date",
        "page[size]": 10
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        st.error(f"Error fetching data from Fiscal Data API: {e}")
        return []

# Dashboard Header
st.title("📈 US National Debt Live Endpoint Monitor")
st.markdown("Capturing macro milestones and early micro-movements for automated trading signals.")
st.divider()

# Fetch Data
raw_data = fetch_debt_data()

if raw_data:
    # Process the most recent record
    latest_record = raw_data[0]
    current_debt = float(latest_record["tot_pub_debt_out_amt"])
    record_date = latest_record["record_date"]
    
    # Calculate Metrics
    distance_to_target = TARGET_THRESHOLD - current_debt
    percent_of_target = (current_debt / TARGET_THRESHOLD) * 100
    
    # Overview Metrics Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current National Debt (USD)",
            value=f"${current_debt:,.2f}",
            delta=f"As of {record_date}",
            delta_color="off"
        )
        
    with col2:
        delta_sign = "-" if distance_to_target > 0 else "+"
        st.metric(
            label="Distance to $40T Threshold",
            value=f"${abs(distance_to_target):,.2f}",
            delta=f"{delta_sign} Remaining",
            delta_color="inverse" if distance_to_target > 0 else "normal"
        )
        
    with col3:
        st.metric(
            label="Progress to Milestone",
            value=f"{percent_of_target:.4f}%"
        )
        
    st.divider()
    
    # Historical Trend Data Analysis
    st.subheader("🔎 Recent Endpoint Updates")
    df = pd.DataFrame(raw_data)
    
    # Clean and Format DataFrame
    df["tot_pub_debt_out_amt"] = df["tot_pub_debt_out_amt"].astype(float)
    df["record_date"] = pd.to_datetime(df["record_date"])
    
    df_display = df[["record_date", "tot_pub_debt_out_amt"]].copy()
    df_display.columns = ["Record Date", "Total Public Debt Outstanding ($)"]
    
    # Plot historical micro-movements
    st.line_chart(data=df_display, x="Record Date", y="Total Public Debt Outstanding ($)")
    
    # Raw Data Table Preview
    with st.expander("View Raw JSON Endpoint Payload"):
        st.json(raw_data)

else:
    st.warning("Unable to parse API data. Please verify your connection to api.fiscaldata.treasury.gov.")

# Auto-refresh loop framework placeholder for trading desk execution
st.sidebar.header("⚙️ Dashboard Controls")
refresh_rate = st.sidebar.slider("Polling Frequency (Seconds)", 5, 60, 10)
if st.sidebar.button("Force Manual Refresh"):
    st.cache_data.clear()
    st.rerun()
