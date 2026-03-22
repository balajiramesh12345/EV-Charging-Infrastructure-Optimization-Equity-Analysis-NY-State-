import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="EV Transition Engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS matching Spatial Explorer aesthetic ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    
    /* Header matching pages */
    .custom-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem 2rem;
        color: white;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: -1rem -1rem 0rem -1rem;
    }
    
    .custom-header-logo {
        height: 40px;
        width: auto;
    }
    
    .custom-header-title {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        max-width: 1000px;
        margin: 0 auto 2rem auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 1rem;
        line-height: 1.2;
        text-align: center;
        width: 100%;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #4b5563;
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 3rem auto;
        max-width: 1200px;
        padding: 0 2rem;
    }
    
    .feature-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        font-size: 0.95rem;
        color: #6b7280;
        line-height: 1.5;
    }
    
    /* CTA Buttons */
    .cta-section {
        text-align: center;
        padding: 2rem;
        margin: 3rem auto;
        max-width: 800px;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.8rem 2.5rem;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
    }
    
    /* Stats Section */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 3rem auto;
        max-width: 1000px;
        padding: 0 2rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #4b5563;
        font-weight: 500;
    }
    
    /* Footer matching pages */
    .custom-footer {
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
        padding: 1.5rem 2rem;
        text-align: center;
        color: #6b7280;
        margin-top: 4rem;
    }
    
    .footer-title {
        font-weight: 600;
        color: #1e3a8a;
        font-size: 1rem;
        margin-bottom: 0.3rem;
    }
    
    .footer-text {
        font-size: 0.85rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- Header with Logo ---
logo_path = Path("die.png")
header_html = '<div class="custom-header">'
if logo_path.exists():
    with open(logo_path, "rb") as f:
        logo_data = base64.b64encode(f.read()).decode()
    header_html += f'''
    <img src="data:image/png;base64,{logo_data}" 
         class="custom-header-logo" 
         alt="DIE Logo"
         style="width:180px; height:auto; margin-right:15px;">
    '''
    # header_html += f'<img src="data:image/png;base64,{logo_data}" class="custom-header-logo" alt="DIE Logo">'
else:
    header_html += '⚙️'
header_html += '<h1 class="custom-header-title">EV Transition Engine</h1></div>'
st.markdown(header_html, unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">Welcome to the EV Transition Engine</h1>
    <p class="hero-subtitle">
        A comprehensive platform for Zero-Emission Vehicle planning, spatial analysis, 
        and scenario modeling. Transform complex data into actionable insights for sustainable transportation planning.
    </p>
</div>
""", unsafe_allow_html=True)

# --- Stats Section ---
st.markdown("""
<div class="stats-container">
    <div class="stat-box">
        <div class="stat-number">2017-2024</div>
        <div class="stat-label">Historical Data</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">157K+</div>
        <div class="stat-label">NY BEVs (2024)</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">12.9K+</div>
        <div class="stat-label">Charging Stations</div>
    </div>
    <div class="stat-box">
        <div class="stat-number">2050</div>
        <div class="stat-label">Projections to</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- CTA Section ---
st.markdown("""
<div style="text-align: center; margin: 3rem auto 2rem auto; max-width: 800px;">
    <h2 style="font-size: 1.8rem; font-weight: 700; color: #1e3a8a; margin-bottom: 2rem;">
        Try Our Decision Intelligence Tools
    </h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("**Spatial Explorer**", use_container_width=True, key="spatial_btn"):
            st.switch_page("pages/1_Spatial_Explorer.py")

    
    with btn_col2:
        if st.button("**Scenario Analysis**", use_container_width=True, key="scenario_btn"):
            st.switch_page("pages/2_Scenarios.py")

# --- Additional Info Section ---
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Key Capabilities
    
    **Spatial Analysis:**
    - Equity coverage mapping for disadvantaged communities
    - Queue risk assessment by county
    - Corridor spacing and gap identification
    - Multi-criteria station placement optimization
    
    **Scenario Modeling:**
    - BEV adoption rate sensitivity (±2%)
    - Incentive impact analysis (±20%)
    - Market share projections
    - CO₂ emissions forecasting
    """)

with col2:
    st.markdown("""
    ### Data Sources
    
    **Geographic Data:**
    - NY State boundaries and county shapefiles
    - Disadvantaged Community designations
    - Alternative fuel corridors
    - Charging station locations
    
    **Historical Data:**
    - Vehicle registrations (ICEV, BEV, PHEV)
    - Vehicle miles traveled (VMT)
    - CO₂ emissions
    - Incentive programs
    """)

# --- Footer ---
st.markdown("""
<div class="custom-footer">
    <div class="footer-title">Decision Intelligence Engine (DIE)</div>
    <div class="footer-text">
        Licensed to <strong>Gao Labs</strong>, Cornell University<br>
        Systems Engineering · ZEV-SAGE Initiative · Built with Streamlit
    </div>
</div>
""", unsafe_allow_html=True)