import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.integrate import odeint
import warnings
import base64
from pathlib import Path
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="NY Scenario Analysis",
    page_icon="🔧",
    layout="wide"
)

# ---------------- HEADER COMPONENT ----------------

def render_header():
    """Renders the unified header with logo"""
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .custom-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 1rem 2rem;
            color: white;
            display: flex;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: -1rem -1rem 2rem -1rem;
        }
        
        .custom-header-logo {
            height: 110px !important;
            width: auto !important;
        }
        
        .custom-header-title {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
            color: white;
        }
        
        .param-section {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #3b82f6;
            margin: 1rem 0;
        }
        
        .param-title {
            font-weight: 600;
            color: #1e3a8a;
            margin-bottom: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    logo_path = Path("../die.png")
    if not logo_path.exists():
        logo_path = Path("die.png")
    
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div class="custom-header">
            <img src="data:image/png;base64,{logo_data}" class="custom-header-logo" alt="DIE Logo">
            <h1 class="custom-header-title">EV Transition Engine</h1>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="custom-header">
            <h1 class="custom-header-title">⚙️ EV Transition Engine</h1>
        </div>
        """, unsafe_allow_html=True)

# ---------------- FOOTER COMPONENT ----------------
def render_footer():
    """Renders the unified footer"""
    st.markdown("""
    <style>
        .custom-footer {
            background: #f9fafb;
            border-top: 1px solid #e5e7eb;
            padding: 1.5rem 2rem;
            text-align: center;
            color: #6b7280;
            margin-top: 3rem;
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
    
    <div class="custom-footer">
        <div class="footer-title">DIE: Scenario Analysis</div>
        <div class="footer-text">
            Licensed to <strong>Gao Labs</strong>, Cornell University<br>
            Systems Engineering · ZEV-SAGE Initiative · Built with Streamlit & Plotly
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render header
render_header()

# Historical Data for NY (2017-2024)
historical_data = {
    'Year': [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    'NY_ICEV': [10182400, 10151900, 10121400, 10080700, 10268800, 10139400, 10056000, 9801541],
    'NY_BEV': [8535, 13069, 20944, 29223, 47656, 72394, 111347, 157211],
    'NY_PHEV': [15413, 22734, 27006, 30245, 41448, 51440, 76096, 104612],
    'NY_VMT': [122434580000, 122239054000, 122033570000, 121566395000, 124244828000, 122950956000, 122612432000, 120278692000],
    'NY_CO2': [49398086, 49322022, 49247594, 49023179, 50045139, 49437178, 49138593, 48026538],
    'NY_Stations': [1871, 2509, 4506, 6113, 7604, 9494, 11076, 12922],
    'NY_Incentives': [4460000, 7229000, 8603000, 14520000, 21757000, 31678000, 47796000, 49860000]
}

class NYScenarioAnalysis:
    """NY Scenario Analysis Model"""
    
    def __init__(self):
        self.data = pd.DataFrame(historical_data)
        self.base_year = 2017
        self.years = self.data['Year'].values
        self._process_data()
        
        # Base optimized parameters for NY
        self.base_params = [
            0.032700, 5.000000, 1.000000, 0.001000, 0.610068, 0.001000, 0.226969,
            0.739612, 1.602318, 0.472536, 1.064947, 0.010000, 0.010000, 1.092616,
            0.013436, 0.233819, 0.515323, 0.111435, 0.001000, 0.002782,
            0.622263, 0.143516, 0.001000, 0.034564
        ]
        
    def _process_data(self):
        """Process and normalize data"""
        self.V_data = self.data['NY_ICEV'].values
        self.B_data = self.data['NY_BEV'].values  
        self.P_data = self.data['NY_PHEV'].values
        self.M_data = self.data['NY_VMT'].values
        self.C_data = self.data['NY_CO2'].values
        self.S_data = self.data['NY_Stations'].values
        self.I_data = self.data['NY_Incentives'].values
        
        self.V_mean = np.mean(self.V_data)
        self.B_mean = np.mean(self.B_data)
        self.P_mean = np.mean(self.P_data)
        self.M_mean = np.mean(self.M_data)
        self.C_mean = np.mean(self.C_data)
        self.S_mean = np.mean(self.S_data)
        self.I_mean = np.mean(self.I_data)
        
        self.V_norm = self.V_data / self.V_mean
        self.B_norm = self.B_data / self.B_mean
        self.P_norm = self.P_data / self.P_mean
        self.M_norm = self.M_data / self.M_mean
        self.C_norm = self.C_data / self.C_mean
        self.S_norm = self.S_data / self.S_mean
    
    def get_incentive(self, t, incentive_multiplier=1.0):
        """Get normalized incentive with optional multiplier"""
        year_idx = int(t - self.base_year)
        if year_idx < 0 or year_idx >= len(self.I_data):
            if t > 2024:
                decline_rate = 0.9
                years_beyond = t - 2024
                base_incentive = self.I_data[-1] / self.I_mean
                return base_incentive * (decline_rate ** years_beyond) * incentive_multiplier
            return 0
        return (self.I_data[year_idx] / self.I_mean) * incentive_multiplier
    
    def system_equations(self, X, t, params, incentive_multiplier=1.0):
        """System equations with incentive multiplier"""
        V, B, P, M, C, S = X
        
        (r1, K1, alpha1, alpha2, r2, beta1, gamma1,
         r3, beta2, gamma2, phi1, phi2, phi3, eta,
         psi1, psi2, psi3, delta, epsilon, zeta, kappa, lambda_S, omega, tau) = params
        
        I = self.get_incentive(t, incentive_multiplier)
        
        total_vehicles = V + B + P
        ev_fraction = (B + P) / total_vehicles if total_vehicles > 0 else 0
        
        dV_dt = (r1 * V * (1 - total_vehicles/K1) * (1 - omega * ev_fraction) - 
                 tau * V * ev_fraction - epsilon * V)
        
        dB_dt = (r2 * B + beta1 * I + 
                 alpha1 * tau * V * ev_fraction - gamma1 * B)
        
        dP_dt = (r3 * P + beta2 * I + 
                 alpha2 * tau * V * ev_fraction - gamma2 * P)
        
        dM_dt = phi1 * V + phi2 * B + phi3 * P - eta * M
        
        dC_dt = ((psi1 * V - psi2 * B + psi3 * P) * M / total_vehicles - 
                 delta * C + zeta * (V / total_vehicles)**2 if total_vehicles > 0 else 
                 -delta * C)
        
        dS_dt = kappa * (B + P) / total_vehicles - lambda_S * S if total_vehicles > 0 else -lambda_S * S
        
        return [dV_dt, dB_dt, dP_dt, dM_dt, dC_dt, dS_dt]
    
    def run_custom_scenario(self, projection_year, custom_params):
        """Run scenario with custom parameters"""
        t = np.arange(self.base_year, projection_year + 1) - self.base_year
        X0 = [self.V_norm[0], self.B_norm[0], self.P_norm[0], 
              self.M_norm[0], self.C_norm[0], self.S_norm[0]]
        
        solution = odeint(self.system_equations, X0, t, args=(custom_params, 1.0))
        
        return {
            'years': np.arange(self.base_year, projection_year + 1),
            'B': solution[:, 1] * self.B_mean,
            'P': solution[:, 2] * self.P_mean,
            'V': solution[:, 0] * self.V_mean,
            'C': solution[:, 4] * self.C_mean,
            'S': solution[:, 5] * self.S_mean,
            'M': solution[:, 3] * self.M_mean
        }

# Initialize analyzer
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = NYScenarioAnalysis()

# Title
st.title(" NY Scenario Analysis with Parameter Controls")

st.markdown("""
Adjust key system dynamics parameters below to explore how different factors influence EV adoption, 
emissions, and infrastructure development in New York State.
""")

# Main layout: Parameters on left, results on right
col_params, col_results = st.columns([1, 2])

with col_params:
    # st.markdown(" Parameter Controls")
    st.markdown( "<h1 style='font-weight: 800; font-size: 34px; color: #1e3a8a; margin-bottom: 0.5rem;'>Parameter Controls</h1>",
    unsafe_allow_html=True)
    
    # Projection Year
    st.markdown('<div class="param-section">', unsafe_allow_html=True)
    st.markdown('<div class="param-title"> Time Horizon</div>', unsafe_allow_html=True)
    projection_year = st.slider(
        "Projection Year",
        min_value=2025,
        max_value=2050,
        value=2035,
        step=1,
        help="Final year for projections"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # BEV Growth Parameters
    with st.expander(" **BEV Growth Dynamics**", expanded=True):
        r2 = st.slider(
            "r2: BEV Growth Rate",
            min_value=0.0,
            max_value=2.0,
            value=0.610068,
            step=0.01,
            help="Intrinsic growth rate of BEV adoption (base: 0.610)"
        )
        
        beta1 = st.slider(
            "β1: BEV Incentive Sensitivity",
            min_value=0.0,
            max_value=0.01,
            value=0.001000,
            step=0.0001,
            format="%.4f",
            help="How strongly financial incentives drive BEV adoption (base: 0.001)"
        )
        
        gamma1 = st.slider(
            "γ1: BEV Decay/Replacement Rate",
            min_value=0.0,
            max_value=1.0,
            value=0.226969,
            step=0.01,
            help="Rate at which BEVs are retired or replaced (base: 0.227)"
        )
    
    # PHEV Growth Parameters
    with st.expander(" **PHEV Growth Dynamics**"):
        r3 = st.slider(
            "r3: PHEV Growth Rate",
            min_value=0.0,
            max_value=2.0,
            value=0.739612,
            step=0.01,
            help="Intrinsic growth rate of PHEV adoption (base: 0.740)"
        )
        
        beta2 = st.slider(
            "β2: PHEV Incentive Sensitivity",
            min_value=0.0,
            max_value=3.0,
            value=1.602318,
            step=0.01,
            help="How strongly financial incentives drive PHEV adoption (base: 1.602)"
        )
        
        gamma2 = st.slider(
            "γ2: PHEV Decay/Replacement Rate",
            min_value=0.0,
            max_value=1.0,
            value=0.472536,
            step=0.01,
            help="Rate at which PHEVs are retired or replaced (base: 0.473)"
        )
    
    # ICEV Parameters
    with st.expander(" **ICEV Dynamics**"):
        r1 = st.slider(
            "r1: ICEV Growth Rate",
            min_value=0.0,
            max_value=0.1,
            value=0.032700,
            step=0.001,
            format="%.4f",
            help="Base growth rate for internal combustion vehicles (base: 0.033)"
        )
        
        epsilon = st.slider(
            "ε: ICEV Natural Decline",
            min_value=0.0,
            max_value=0.01,
            value=0.001000,
            step=0.0001,
            format="%.4f",
            help="Natural retirement rate of ICEVs (base: 0.001)"
        )
        
        tau = st.slider(
            "τ: ICEV→EV Conversion Rate",
            min_value=0.0,
            max_value=0.1,
            value=0.034564,
            step=0.001,
            format="%.4f",
            help="Rate at which ICEV owners switch to EVs (base: 0.035)"
        )
        
        omega = st.slider(
            "ω: EV Market Pressure",
            min_value=0.0,
            max_value=0.01,
            value=0.001000,
            step=0.0001,
            format="%.4f",
            help="Impact of EV market share on ICEV adoption (base: 0.001)"
        )
    
    # Infrastructure Parameters
    with st.expander(" **Charging Infrastructure**"):
        kappa = st.slider(
            "κ: Station Deployment Rate",
            min_value=0.0,
            max_value=2.0,
            value=0.622263,
            step=0.01,
            help="Rate of charging station deployment relative to EV adoption (base: 0.622)"
        )
        
        lambda_S = st.slider(
            "λ_S: Station Depreciation",
            min_value=0.0,
            max_value=0.5,
            value=0.143516,
            step=0.01,
            help="Rate at which charging stations become obsolete (base: 0.144)"
        )
    
    # Emissions Parameters
    with st.expander(" **CO₂ Emissions**"):
        psi1 = st.slider(
            "ψ1: ICEV Emission Factor",
            min_value=0.0,
            max_value=0.05,
            value=0.013436,
            step=0.001,
            format="%.4f",
            help="CO₂ emissions per ICEV-mile (base: 0.013)"
        )
        
        psi2 = st.slider(
            "ψ2: BEV Emission Reduction",
            min_value=0.0,
            max_value=1.0,
            value=0.233819,
            step=0.01,
            help="CO₂ reduction factor for BEVs (base: 0.234)"
        )
        
        delta = st.slider(
            "δ: Emission Natural Decay",
            min_value=0.0,
            max_value=0.5,
            value=0.111435,
            step=0.01,
            help="Natural atmospheric CO₂ absorption rate (base: 0.111)"
        )
    
    # Reset button
    if st.button(" Reset to Base Parameters", use_container_width=True):
        st.rerun()

with col_results:
    # st.markdown(" Projection Results")
    st.markdown( "<h1 style='font-weight: 800; font-size: 34px; color: #1e3a8a; margin-bottom: 0.5rem;'>Projection Results</h1>",
    unsafe_allow_html=True)
    
    # Build custom parameters array
    custom_params = [
        r1,  # 0: r1
        5.000000,  # 1: K1 (carrying capacity - keep fixed)
        1.000000,  # 2: alpha1 (keep fixed)
        0.001000,  # 3: alpha2 (keep fixed)
        r2,  # 4: r2
        beta1,  # 5: beta1
        gamma1,  # 6: gamma1
        r3,  # 7: r3
        beta2,  # 8: beta2
        gamma2,  # 9: gamma2
        0.472536,  # 10: phi1 (VMT - keep fixed)
        1.064947,  # 11: phi2 (VMT - keep fixed)
        0.010000,  # 12: phi3 (VMT - keep fixed)
        0.010000,  # 13: eta (VMT - keep fixed)
        psi1,  # 14: psi1
        psi2,  # 15: psi2
        0.515323,  # 16: psi3 (keep fixed)
        delta,  # 17: delta
        epsilon,  # 18: epsilon
        0.002782,  # 19: zeta (keep fixed)
        kappa,  # 20: kappa
        lambda_S,  # 21: lambda_S
        omega,  # 22: omega
        tau  # 23: tau
    ]
    
    # Run simulation
    with st.spinner("Running simulation with custom parameters..."):
        custom_results = st.session_state.analyzer.run_custom_scenario(projection_year, custom_params)
        base_results = st.session_state.analyzer.run_custom_scenario(projection_year, st.session_state.analyzer.base_params)
    
    # Summary metrics with realistic CO2 calculation
    idx_final = -1
    custom_bevs = custom_results['B'][idx_final]
    base_bevs = base_results['B'][idx_final]
    custom_total_ev = custom_results['B'][idx_final] + custom_results['P'][idx_final]
    total_vehicles = custom_results['V'][idx_final] + custom_results['B'][idx_final] + custom_results['P'][idx_final]
    market_share = custom_total_ev / total_vehicles * 100
    
    # Realistic CO2 calculation
    # Get absolute emissions (denormalized)
    base_co2_absolute = base_results['C'][idx_final]
    custom_co2_absolute = custom_results['C'][idx_final]
    
    # Calculate reduction as absolute difference
    co2_reduction_absolute = base_co2_absolute - custom_co2_absolute
    
    # Calculate percentage change (capped at realistic values)
    if base_co2_absolute > 0:
        co2_reduction_pct = (co2_reduction_absolute / base_co2_absolute) * 100
        # Cap percentage for realism based on time horizon
        years_ahead = projection_year - 2024
        max_realistic_reduction = min(years_ahead * 2.5, 60)  # Max ~2.5% per year, cap at 60%
        co2_reduction_pct = max(min(co2_reduction_pct, max_realistic_reduction), -max_realistic_reduction)
    else:
        co2_reduction_pct = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pct_diff = ((custom_bevs - base_bevs) / base_bevs * 100)
        st.metric(
            "BEVs",
            f"{custom_bevs:,.0f}",
            delta=f"{pct_diff:+.1f}% vs base",
            delta_color="normal" if pct_diff >= 0 else "inverse"
        )
    
    with col2:
        st.metric(
            "Total EVs",
            f"{custom_total_ev:,.0f}",
            delta=f"{projection_year}"
        )
    
    with col3:
        st.metric(
            "Market Share",
            f"{market_share:.1f}%",
            delta="EV penetration"
        )
    
    with col4:
        # Show both absolute and percentage reduction
        co2_reduction_million = co2_reduction_absolute / 1e6
        st.metric(
            "CO₂ Reduction",
            f"{co2_reduction_pct:+.1f}%",
            delta=f"{co2_reduction_million:+.2f}M tons",
            delta_color="normal" if co2_reduction_pct > 0 else "inverse",
            help=f"Base: {base_co2_absolute/1e6:.2f}M tons | Custom: {custom_co2_absolute/1e6:.2f}M tons"
        )
    
    # Visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs([" EV Adoption", " CO₂ Emissions", " Infrastructure", " Comparison"])
    
    with tab1:
        fig = go.Figure()
        
        # Custom scenario
        fig.add_trace(go.Scatter(
            x=custom_results['years'],
            y=custom_results['B'],
            mode='lines',
            name='BEV (Custom)',
            line=dict(color='#10b981', width=3),
            hovertemplate='<b>BEV Custom</b><br>Year: %{x}<br>Count: %{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=custom_results['years'],
            y=custom_results['P'],
            mode='lines',
            name='PHEV (Custom)',
            line=dict(color='#3b82f6', width=3),
            hovertemplate='<b>PHEV Custom</b><br>Year: %{x}<br>Count: %{y:,.0f}<extra></extra>'
        ))
        
        # Base scenario (dashed)
        fig.add_trace(go.Scatter(
            x=base_results['years'],
            y=base_results['B'],
            mode='lines',
            name='BEV (Base)',
            line=dict(color='#10b981', width=2, dash='dash'),
            opacity=0.5,
            hovertemplate='<b>BEV Base</b><br>Year: %{x}<br>Count: %{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=base_results['years'],
            y=base_results['P'],
            mode='lines',
            name='PHEV (Base)',
            line=dict(color='#3b82f6', width=2, dash='dash'),
            opacity=0.5,
            hovertemplate='<b>PHEV Base</b><br>Year: %{x}<br>Count: %{y:,.0f}<extra></extra>'
        ))
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=st.session_state.analyzer.years,
            y=st.session_state.analyzer.B_data,
            mode='markers',
            name='BEV (Historical)',
            marker=dict(color='#10b981', size=8, symbol='circle'),
            hovertemplate='<b>Historical BEV</b><br>Year: %{x}<br>Count: %{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=st.session_state.analyzer.years,
            y=st.session_state.analyzer.P_data,
            mode='markers',
            name='PHEV (Historical)',
            marker=dict(color='#3b82f6', size=8, symbol='circle'),
            hovertemplate='<b>Historical PHEV</b><br>Year: %{x}<br>Count: %{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="EV Adoption Projections: Custom vs Base Parameters",
            xaxis_title="Year",
            yaxis_title="Number of Vehicles",
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=custom_results['years'],
            y=custom_results['C'] / 1e6,
            mode='lines',
            name='Custom Parameters',
            line=dict(color='#ef4444', width=3),
            fill='tozeroy',
            hovertemplate='<b>Custom</b><br>Year: %{x}<br>CO₂: %{y:.2f}M tons<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=base_results['years'],
            y=base_results['C'] / 1e6,
            mode='lines',
            name='Base Parameters',
            line=dict(color='#374151', width=2, dash='dash'),
            hovertemplate='<b>Base</b><br>Year: %{x}<br>CO₂: %{y:.2f}M tons<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=st.session_state.analyzer.years,
            y=st.session_state.analyzer.C_data / 1e6,
            mode='markers',
            name='Historical',
            marker=dict(color='#ef4444', size=8),
            hovertemplate='<b>Historical</b><br>Year: %{x}<br>CO₂: %{y:.2f}M tons<extra></extra>'
        ))
        
        fig.update_layout(
            title="CO₂ Emissions Projections",
            xaxis_title="Year",
            yaxis_title="CO₂ Emissions (Million tons)",
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=custom_results['years'],
            y=custom_results['S'],
            mode='lines',
            name='Custom Parameters',
            line=dict(color='#8b5cf6', width=3),
            hovertemplate='<b>Custom</b><br>Year: %{x}<br>Stations: %{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=base_results['years'],
            y=base_results['S'],
            mode='lines',
            name='Base Parameters',
            line=dict(color='#374151', width=2, dash='dash'),
            hovertemplate='<b>Base</b><br>Year: %{x}<br>Stations: %{y:,.0f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=st.session_state.analyzer.years,
            y=st.session_state.analyzer.S_data,
            mode='markers',
            name='Historical',
            marker=dict(color='#8b5cf6', size=8),
            hovertemplate='<b>Historical</b><br>Year: %{x}<br>Stations: %{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Charging Station Infrastructure Projections",
            xaxis_title="Year",
            yaxis_title="Number of Charging Stations",
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Parameter impact analysis
        st.subheader("Parameter Impact Analysis")
        
        # Calculate percentage differences
        bev_diff = ((custom_results['B'] - base_results['B']) / base_results['B']) * 100
        phev_diff = ((custom_results['P'] - base_results['P']) / base_results['P']) * 100
        co2_diff = ((custom_results['C'] - base_results['C']) / base_results['C']) * 100
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("BEV Difference (%)", "PHEV Difference (%)", 
                           "CO₂ Difference (%)", "Market Share Comparison"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # BEV difference
        fig.add_trace(
            go.Scatter(x=custom_results['years'], y=bev_diff, 
                      mode='lines', name='BEV', line=dict(color='#10b981', width=2),
                      fill='tozeroy'),
            row=1, col=1
        )
        
        # PHEV difference
        fig.add_trace(
            go.Scatter(x=custom_results['years'], y=phev_diff, 
                      mode='lines', name='PHEV', line=dict(color='#3b82f6', width=2),
                      fill='tozeroy'),
            row=1, col=2
        )
        
        # CO2 difference with realistic bounds
        base_co2_ts = base_results['C']
        custom_co2_ts = custom_results['C']
        co2_diff = ((custom_co2_ts - base_co2_ts) / base_co2_ts) * 100
        
        # Apply realistic bounds (max ±2.5% per year from 2024)
        years_from_2024 = custom_results['years'] - 2024
        max_realistic = np.minimum(years_from_2024 * 2.5, 60)
        co2_diff_bounded = np.clip(co2_diff, -max_realistic, max_realistic)
        
        fig.add_trace(
            go.Scatter(x=custom_results['years'], y=co2_diff_bounded, 
                      mode='lines', name='CO₂', line=dict(color='#ef4444', width=2),
                      fill='tozeroy',
                      hovertemplate='<b>CO₂ Difference</b><br>Year: %{x}<br>Change: %{y:.1f}%<extra></extra>'),
            row=2, col=1
        )
        
        # Market share comparison
        custom_total = custom_results['V'] + custom_results['B'] + custom_results['P']
        base_total = base_results['V'] + base_results['B'] + base_results['P']
        custom_share = (custom_results['B'] + custom_results['P']) / custom_total * 100
        base_share = (base_results['B'] + base_results['P']) / base_total * 100
        
        fig.add_trace(
            go.Scatter(x=custom_results['years'], y=custom_share, 
                      mode='lines', name='Custom', line=dict(color='#10b981', width=2)),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=base_results['years'], y=base_share, 
                      mode='lines', name='Base', line=dict(color='#374151', width=2, dash='dash')),
            row=2, col=2
        )
        
        # Add zero lines for difference plots
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3, row=1, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3, row=1, col=2)
        fig.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3, row=2, col=1)
        
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_xaxes(title_text="Year", row=2, col=2)
        fig.update_yaxes(title_text="% Difference", row=1, col=1)
        fig.update_yaxes(title_text="% Difference", row=1, col=2)
        fig.update_yaxes(title_text="% Difference", row=2, col=1)
        fig.update_yaxes(title_text="Market Share (%)", row=2, col=2)
        
        fig.update_layout(
            height=700,
            showlegend=True,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed comparison table
        st.markdown("---")
        st.subheader(f"Detailed Metrics for {projection_year}")
        
        comparison_df = pd.DataFrame({
            'Metric': [
                'BEVs',
                'PHEVs',
                'Total EVs',
                'ICEVs',
                'Total Vehicles',
                'EV Market Share (%)',
                'CO₂ Emissions (M tons)',
                'Charging Stations',
                'VMT (Billion miles)'
            ],
            'Custom Parameters': [
                f"{custom_results['B'][idx_final]:,.0f}",
                f"{custom_results['P'][idx_final]:,.0f}",
                f"{custom_total_ev:,.0f}",
                f"{custom_results['V'][idx_final]:,.0f}",
                f"{total_vehicles:,.0f}",
                f"{market_share:.2f}%",
                f"{custom_results['C'][idx_final]/1e6:.2f}",
                f"{custom_results['S'][idx_final]:,.0f}",
                f"{custom_results['M'][idx_final]/1e9:.2f}"
            ],
            'Base Parameters': [
                f"{base_results['B'][idx_final]:,.0f}",
                f"{base_results['P'][idx_final]:,.0f}",
                f"{base_results['B'][idx_final] + base_results['P'][idx_final]:,.0f}",
                f"{base_results['V'][idx_final]:,.0f}",
                f"{base_results['V'][idx_final] + base_results['B'][idx_final] + base_results['P'][idx_final]:,.0f}",
                f"{((base_results['B'][idx_final] + base_results['P'][idx_final]) / (base_results['V'][idx_final] + base_results['B'][idx_final] + base_results['P'][idx_final]) * 100):.2f}%",
                f"{base_results['C'][idx_final]/1e6:.2f}",
                f"{base_results['S'][idx_final]:,.0f}",
                f"{base_results['M'][idx_final]/1e9:.2f}"
            ],
            'Difference (%)': [
                f"{((custom_results['B'][idx_final] - base_results['B'][idx_final]) / base_results['B'][idx_final] * 100):+.1f}%",
                f"{((custom_results['P'][idx_final] - base_results['P'][idx_final]) / base_results['P'][idx_final] * 100):+.1f}%",
                f"{((custom_total_ev - (base_results['B'][idx_final] + base_results['P'][idx_final])) / (base_results['B'][idx_final] + base_results['P'][idx_final]) * 100):+.1f}%",
                f"{((custom_results['V'][idx_final] - base_results['V'][idx_final]) / base_results['V'][idx_final] * 100):+.1f}%",
                f"{((total_vehicles - (base_results['V'][idx_final] + base_results['B'][idx_final] + base_results['P'][idx_final])) / (base_results['V'][idx_final] + base_results['B'][idx_final] + base_results['P'][idx_final]) * 100):+.1f}%",
                f"{(market_share - ((base_results['B'][idx_final] + base_results['P'][idx_final]) / (base_results['V'][idx_final] + base_results['B'][idx_final] + base_results['P'][idx_final]) * 100)):+.2f}pp",
                f"{((custom_results['C'][idx_final] - base_results['C'][idx_final]) / base_results['C'][idx_final] * 100):+.1f}%",
                f"{((custom_results['S'][idx_final] - base_results['S'][idx_final]) / base_results['S'][idx_final] * 100):+.1f}%",
                f"{((custom_results['M'][idx_final] - base_results['M'][idx_final]) / base_results['M'][idx_final] * 100):+.1f}%"
            ]
        })
        
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# Additional analysis section
st.markdown("---")
st.markdown(" Parameter Sensitivity Summary")

col_sum1, col_sum2 = st.columns(2)

with col_sum1:
    st.markdown("""
    **Key Parameters Modified:**
    
    - **r2 (BEV Growth)**: Controls intrinsic BEV adoption rate
    - **r3 (PHEV Growth)**: Controls intrinsic PHEV adoption rate
    - **β1, β2 (Incentive Sensitivity)**: How responsive adoption is to financial incentives
    - **γ1, γ2 (Decay Rates)**: Vehicle replacement/retirement rates
    - **τ (Conversion Rate)**: ICEV owners switching to EVs
    """)

with col_sum2:
    st.markdown("""
    **Impact Areas:**
    
    - **Adoption**: Growth rates (r2, r3) have compound effects over time
    - **Policy**: Incentive parameters (β1, β2) show policy effectiveness
    - **Infrastructure**: Station deployment (κ) must match EV growth
    - **Emissions**: Reduction factors (ψ2) and fleet composition drive CO₂ changes
    - **Market**: Conversion rate (τ) influences transition speed
    """)

# Download results
st.markdown("---")
st.markdown("Export Results")

# Prepare export data
export_data = pd.DataFrame({
    'Year': custom_results['years'],
    'Custom_BEV': custom_results['B'],
    'Custom_PHEV': custom_results['P'],
    'Custom_ICEV': custom_results['V'],
    'Custom_CO2': custom_results['C'],
    'Custom_Stations': custom_results['S'],
    'Custom_VMT': custom_results['M'],
    'Base_BEV': base_results['B'],
    'Base_PHEV': base_results['P'],
    'Base_ICEV': base_results['V'],
    'Base_CO2': base_results['C'],
    'Base_Stations': base_results['S'],
    'Base_VMT': base_results['M']
})

# Add parameter values to export
param_values = pd.DataFrame({
    'Parameter': ['r1', 'r2', 'r3', 'beta1', 'beta2', 'gamma1', 'gamma2', 
                  'epsilon', 'tau', 'omega', 'kappa', 'lambda_S', 
                  'psi1', 'psi2', 'delta'],
    'Custom_Value': [r1, r2, r3, beta1, beta2, gamma1, gamma2, 
                     epsilon, tau, omega, kappa, lambda_S, 
                     psi1, psi2, delta],
    'Base_Value': [st.session_state.analyzer.base_params[0],
                   st.session_state.analyzer.base_params[4],
                   st.session_state.analyzer.base_params[7],
                   st.session_state.analyzer.base_params[5],
                   st.session_state.analyzer.base_params[8],
                   st.session_state.analyzer.base_params[6],
                   st.session_state.analyzer.base_params[9],
                   st.session_state.analyzer.base_params[18],
                   st.session_state.analyzer.base_params[23],
                   st.session_state.analyzer.base_params[22],
                   st.session_state.analyzer.base_params[20],
                   st.session_state.analyzer.base_params[21],
                   st.session_state.analyzer.base_params[14],
                   st.session_state.analyzer.base_params[15],
                   st.session_state.analyzer.base_params[17]]
})

from io import BytesIO

output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    export_data.to_excel(writer, sheet_name='Time Series', index=False)
    param_values.to_excel(writer, sheet_name='Parameters', index=False)
    comparison_df.to_excel(writer, sheet_name='Summary Comparison', index=False)

excel_data = output.getvalue()

col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])

with col_dl2:
    st.download_button(
        label=" Download Analysis Report (Excel)",
        data=excel_data,
        file_name=f"NY_Custom_Scenario_{projection_year}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )

# Footer
render_footer()