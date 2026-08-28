import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configure page with Google-like settings
st.set_page_config(page_title="Data Center Build Simulator", layout="wide", initial_sidebar_state="expanded")

# Inject Google Fonts (Roboto) and custom Google brand CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #202124 !important;
        font-weight: 500 !important;
    }
    
    /* Subtle grey background for sidebar to mimic Google Cloud Console */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #DADCE0;
    }
</style>
""", unsafe_allow_html=True)

st.title("Integrated Telemetry: Schedule Impact Simulator")
st.markdown("Adjust the inputs below to calculate how telemetry deviations alter the data center critical path.")

# Sidebar inputs for Current Values
st.sidebar.header("Adjust Telemetry Inputs")
site_approval = st.sidebar.slider("Site Approval Cycle (Days)", min_value=90, max_value=150, value=115, step=5)
power_lead = st.sidebar.slider("Power Agreement Lead Time (Months)", min_value=18, max_value=36, value=24, step=1)
equip_lead = st.sidebar.slider("Critical Equipment Lead Time (Weeks)", min_value=40, max_value=70, value=52, step=2)
const_var = st.sidebar.slider("Construction Milestone Variance (Days)", min_value=0, max_value=60, value=14, step=2)

# Unit conversions to months for critical path calculation
site_mo = site_approval / 30.0
equip_mo = equip_lead / 4.33
const_var_mo = const_var / 30.0
baseline_construction = 12.0 # Baseline physical construction time

# Target Baselines
target_total = (90 / 30.0) + max(18.0, (40 / 4.33)) + baseline_construction + (0 / 30.0)

# Critical Path Logic
total_months = site_mo + max(power_lead, equip_mo) + baseline_construction + const_var_mo
variance_from_target = total_months - target_total

# Determine Google Color for the final status
# Red (#EA4335) for Off Track, Yellow (#FBBC04) for At Risk, Green (#34A853) for On Track
if variance_from_target > 3:
    status_text = "Off Track"
    status_color = "#EA4335"
elif variance_from_target > 0:
    status_text = "At Risk"
    status_color = "#FBBC04"
else:
    status_text = "On Track"
    status_color = "#34A853"

# Top Level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Projected Build", f"{total_months:.1f} Months", f"{variance_from_target:.1f} mo vs Target", delta_color="inverse")
col2.metric("Primary Bottleneck", "Utility Supply (Power)" if power_lead > equip_mo else "Procurement (Equipment)")
col3.metric("Project Status", status_text)

# Waterfall Visualization with Google Colors
fig = go.Figure(go.Waterfall(
    name="Critical Path", orientation="h",
    measure=["relative", "relative", "relative", "relative", "total"],
    y=["Site Approval", "Concurrent Supply Lead (Max)", "Baseline Construction", "Construction Variance", "Total Build Time"],
    x=[site_mo, max(power_lead, equip_mo), baseline_construction, const_var_mo, total_months],
    connector={"line": {"color": "#DADCE0", "width": 2}},
    increasing={"marker": {"color": "#4285F4"}}, # Google Blue for additive steps
    decreasing={"marker": {"color": "#34A853"}}, # Google Green for reductive steps (if any)
    totals={"marker": {"color": status_color}}   # Dynamic total color based on risk
))

fig.update_layout(
    title=dict(text="Critical Path Waterfall (Months)", font=dict(color="#202124", size=18)),
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Roboto, sans-serif", color="#5F6368"),
    xaxis=dict(showgrid=True, gridcolor="#E8EAED", zeroline=True, zerolinecolor="#DADCE0"),
    yaxis=dict(showgrid=False)
)

st.plotly_chart(fig, use_container_width=True)