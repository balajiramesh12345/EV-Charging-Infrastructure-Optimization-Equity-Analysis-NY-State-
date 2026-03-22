
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
from pathlib import Path
import base64


# ---------------- Page Setup ----------------
st.set_page_config(page_title="NY Spatial Explorer", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)
    
    logo_path = Path("../die.png")  # Adjust path for pages folder
    if not logo_path.exists():
        logo_path = Path("die.png")  # Try direct path
    
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
            <h1 class="custom-header-title">⚙️EV Transition Engine</h1>
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
        <div class="footer-title">DIE: Spatial Explorer</div>
        <div class="footer-text">
            Licensed to <strong>Gao Labs</strong>, Cornell University<br>
            Systems Engineering · ZEV-SAGE Initiative · Built with Streamlit & Folium
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render header
render_header()

# Robust CSS: pin Folium iframe height on every rerun
st.markdown("""
<style>
/* streamlit-folium iframe (multiple fallbacks for different versions) */
iframe[title="streamlit_folium.st_folium"],
div[data-testid="stIFrame"] iframe,
.stHtml iframe {
    width: 100% !important;
    height: 650px !important;
    min-height: 650px !important;
    border: 0;
}
</style>
""", unsafe_allow_html=True)

st.title(" NY Spatial Explorer")

st.markdown("""
<style>
/* streamlit-folium iframe (multiple fallbacks for different versions) */
iframe[title="streamlit_folium.st_folium"],
div[data-testid="stIFrame"] iframe,
.stHtml iframe {
    width: 100% !important;
    height: 650px !important;
    min-height: 650px !important;
    border: 0;
}
</style>
""", unsafe_allow_html=True)



# ---------------- Paths ----------------
GEO_PATH = "GEOJSON/"
DATA_PATH = "Data/"
state_path = GEO_PATH + "State_Shoreline.geojson"
counties_path = GEO_PATH + "Counties_Shoreline.geojson"
dac_path = GEO_PATH + "Final_DAC_Attributes.geojson"
corridors_path = GEO_PATH + "AltFuels_rounds1_7_2023_11_07.geojson"
eq_geo = GEO_PATH + "Equity_Coverage.geojson"
queue_geo = GEO_PATH + "Queue_Risk_Analysis.geojson"
corridor_spacing_geo = GEO_PATH + "Corridor_Spacing_Analysis.geojson"
corridor_gaps_geo = GEO_PATH + "Corridor_Coverage_Gaps.geojson"
station_csv = DATA_PATH + "NY EV Charging stations_full.csv"

# ---------------- Cached Data Loaders ----------------
@st.cache_data(show_spinner=False)
def load_geojson(path: str):
    return gpd.read_file(path)

@st.cache_data(show_spinner=False)
def load_csv(path: str):
    return pd.read_csv(path)

def simplify_geometries(gdf: gpd.GeoDataFrame, tolerance=0.001):
    gdf = gdf.copy()
    gdf["geometry"] = gdf["geometry"].simplify(tolerance, preserve_topology=True)
    return gdf

# ---------------- Build Base Map Layers (Cached) ----------------
@st.cache_data(show_spinner=False)
def build_base_map_layers():
    state = simplify_geometries(load_geojson(state_path), 0.01)
    counties = simplify_geometries(load_geojson(counties_path), 0.005)
    dac = simplify_geometries(load_geojson(dac_path), 0.005)
    corridors = simplify_geometries(load_geojson(corridors_path), 0.01)
    return state, counties, dac, corridors

def create_base_map(include_stations=False):
    """Creates base map with state, counties, DAC, corridors, and optionally stations"""
    m = folium.Map(
        location=[42.9, -75.5],
        zoom_start=7,
        tiles="CartoDB positron",
        prefer_canvas=True
    )
    
    try:
        state, counties, dac, corridors = build_base_map_layers()
    except Exception as e:
        st.error(f"Failed to load base layers: {e}")
        return m

    # State Boundary
    folium.GeoJson(
        state,
        name="State Boundary",
        style_function=lambda _: {"color": "#004B87", "weight": 2, "fillOpacity": 0},
        show=False
    ).add_to(m)

    # County Boundaries (light gray outlines)
    folium.GeoJson(
        counties,
        name="County Boundaries",
        tooltip=folium.GeoJsonTooltip(fields=["NAME"], aliases=["County:"], labels=True),
        style_function=lambda _: {"color": "#636363", "weight": 1, "fillOpacity": 0},
    ).add_to(m)

    # DAC Areas
    folium.GeoJson(
        dac,
        name="Disadvantaged Communities",
        tooltip=folium.GeoJsonTooltip(
            fields=["County", "City_Town", "DAC_Desig"],
            aliases=["County:", "City/Town:", "Designation:"],
            labels=True
        ),
        style_function=lambda f: {
            "fillColor": "#e31a1c" if f["properties"].get("DAC_Desig") == "Designated as DAC" else "#cccccc",
            "color": "black",
            "weight": 0.3,
            "fillOpacity": 0.5,
        },
        show=False
    ).add_to(m)

    # Alt Fuel / EV Corridors
    folium.GeoJson(
        corridors,
        name="Alt Fuel / EV Corridors",
        tooltip=folium.GeoJsonTooltip(
            fields=["PRIMARY_NA", "EV"],
            aliases=["Road:", "EV Corridor:"],
            labels=True
        ),
        style_function=lambda f: {
            "color": "#3182bd" if f["properties"].get("EV") == "Y" else "#9ecae1",
            "weight": 2,
        },
        show=False
    ).add_to(m)

    # EV Charging Stations (if requested)
    if include_stations:
        try:
            stations_df = load_csv(station_csv).dropna(subset=["Latitude", "Longitude"])
            chargers_fg = folium.FeatureGroup(name="EV Charging Stations", show=True)
            for _, r in stations_df.iterrows():
                folium.CircleMarker(
                    location=[r["Latitude"], r["Longitude"]],
                    radius=3,
                    color="#22c55e",
                    fill=True,
                    fill_color="#22c55e",
                    fill_opacity=0.9,
                    weight=0.8,
                    popup=folium.Popup(
                        f"<b>{r.get('Station Name','Station')}</b><br>"
                        f"Type: {r.get('Fuel Type','EV')}<br>"
                        f"City: {r.get('City','N/A')}<br>"
                        f"Access: {r.get('Access Days Time','N/A')}",
                        max_width=260
                    ),
                ).add_to(chargers_fg)
            chargers_fg.add_to(m)
        except Exception as e:
            st.warning(f"Could not load stations: {e}")

    folium.LayerControl(collapsed=False).add_to(m)
    return m

# ---------------- Session State ----------------
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "default"
if "show_stations" not in st.session_state:
    st.session_state.show_stations = False

# ---------------- Analysis Mode Selection ----------------
st.subheader("Select Analysis Mode")
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("Equity Coverage Index"):
        st.session_state.current_mode = "equity"
        st.rerun()
with c2:
    if st.button("Queue Risk"):
        st.session_state.current_mode = "queue"
        st.rerun()
with c3:
    if st.button("Corridor Spacing"):
        st.session_state.current_mode = "corridor_spacing"
        st.rerun()
with c4:
    if st.button("Suitability / Optimization"):
        st.session_state.current_mode = "optimization"
        st.rerun()
        st.rerun()

    

    # ---------------- Equity Coverage Mode ----------------
if st.session_state.current_mode == 'equity':
    st.markdown( "<h1 style='font-weight: 800; font-size: 34px; color: #1e3a8a; margin-bottom: 0.5rem;'>Equity Coverage Analysis</h1>",
    unsafe_allow_html=True)
    
    # Description popup
    with st.expander("What is Equity Coverage?", expanded=False):
        st.markdown("""
        **Equity Coverage** assesses charging infrastructure accessibility in disadvantaged communities:
        - **DAC Area Coverage**: Percentage of Disadvantaged Community (DAC) area within each county
        - **Infrastructure Distribution**: How well charging stations serve populations with historically limited access
        - **Environmental Justice**: Ensures equitable EV transition benefits across all socioeconomic groups
        
        Higher coverage percentages indicate better infrastructure penetration in communities that need it most for a just transition.
        """)

    st.markdown("Equity Coverage Parameters")
    col_a, col_b = st.columns(2)

    col_a, col_b = st.columns(2)
    with col_a:
        pop_weight = st.slider("Population Weight (reserved)", 0.0, 1.0, 0.6, step=0.1, key="pop_weight")
    with col_b:
        dac_threshold = st.slider("DAC Coverage Threshold (%)", 0, 100, 24, key="dac_threshold")

    st.info(f"Counties ≥ {dac_threshold}% DAC coverage are colored by a cool gradient; others are muted.")

    with st.spinner("Loading equity coverage map..."):
        # Create fresh map for equity mode
        m = folium.Map(
            location=[42.9, -75.5],
            zoom_start=7,
            tiles="CartoDB positron",
            prefer_canvas=True
        )

        # Load equity coverage data
        try:
            eq_df = load_geojson(eq_geo).copy()
            eq_df["Equity_Coverage_Pct"] = pd.to_numeric(eq_df["Equity_Coverage_Pct"], errors="coerce").fillna(0.0)
            eq_df = eq_df[["NAME", "Equity_Coverage_Pct", "geometry"]]

            vmin = float(eq_df["Equity_Coverage_Pct"].min())
            vmax = float(eq_df["Equity_Coverage_Pct"].max())
            if vmin == vmax:
                vmax = vmin + 1e-6  # avoid flat color scales

            colormap = cm.linear.YlGnBu_09.scale(vmin, vmax)
            colormap.caption = "Equity Coverage (% DAC area per county)"
            thr = float(dac_threshold)

            def county_style(feat):
                pct = float(feat["properties"].get("Equity_Coverage_Pct", 0.0))
                if pct >= thr:
                    return {
                        "fillColor": colormap(pct), 
                        "color": "#222", 
                        "weight": 1.2, 
                        "fillOpacity": 0.7
                    }
                else:
                    return {
                        "fillColor": "#e9ecef", 
                        "color": "#aaa", 
                        "weight": 0.6, 
                        "fillOpacity": 0.3
                    }

            # Add equity coverage choropleth layer
            folium.GeoJson(
                eq_df,
                name="Equity Coverage (DAC %)",
                style_function=county_style,
                highlight_function=lambda f: {"weight": 3, "color": "#111", "fillOpacity": 0.85},
                tooltip=folium.GeoJsonTooltip(
                    fields=["NAME", "Equity_Coverage_Pct"],
                    aliases=["County:", "DAC Coverage (%):"],
                    sticky=True, 
                    labels=True, 
                    localize=True,
                    style="font-size: 14px; font-weight: bold;"
                ),
                show=True,
            ).add_to(m)
            
            # Add colormap legend
            colormap.add_to(m)

            # Add DAC polygons overlay for detail
            try:
                dac = load_geojson(dac_path).copy()
                dac = dac[dac["DAC_Desig"] == "Designated as DAC"]
                
                # Calculate area in square miles
                dac_aea = dac.to_crs(epsg=5070)
                dac["Area_sqmi"] = (dac_aea.geometry.area / 2_589_988.110336)
                dac = dac.to_crs(epsg=4326)

                folium.GeoJson(
                    dac,
                    name="DAC Polygons (Detail)",
                    style_function=lambda f: {
                        "fillColor": "#e31a1c", 
                        "color": "#b30000",
                        "weight": 0.5, 
                        "fillOpacity": 0.25
                    },
                    highlight_function=lambda f: {
                        "weight": 1.5, 
                        "color": "#99000d", 
                        "fillOpacity": 0.4
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=["County", "City_Town", "Area_sqmi"],
                        aliases=["County:", "Area Name:", "Area (sq mi):"],
                        sticky=True, 
                        labels=True,
                        style="font-size: 12px;"
                    ),
                    show=True,
                ).add_to(m)
            except Exception as e:
                st.warning(f"Could not add DAC detail layer: {e}")

            # Add layer control
            folium.LayerControl(collapsed=False).add_to(m)

        except Exception as e:
            st.error(f"Failed to load equity coverage data: {e}")
            st.error(f"Make sure {eq_geo} exists and is valid GeoJSON")

    # Display map
    st_folium(m, height=650, use_container_width=True, key=f"map_equity_{dac_threshold}", returned_objects=[])

    # Summary table synced to threshold
    st.markdown("---")
    st.subheader("Equity Coverage Summary")
    
    try:
        filtered = (eq_df[eq_df["Equity_Coverage_Pct"] >= thr]
                    .sort_values("Equity_Coverage_Pct", ascending=False))
        st.write(f"**Counties with ≥ {int(thr)}% DAC area coverage:** {len(filtered)}")
        
        if not filtered.empty:
            display_df = filtered[["NAME", "Equity_Coverage_Pct"]].copy()
            display_df.columns = ["County", "DAC Coverage (%)"]
            display_df = display_df.reset_index(drop=True)
            
            st.dataframe(
                display_df.style.format({"DAC Coverage (%)": "{:.2f}"}),
                height=420,
                use_container_width=True
            )
        else:
            st.warning("No counties meet the current threshold.")
    except:
        st.error("Could not generate summary table")

# ---------------- Queue Risk ----------------
elif st.session_state.current_mode == "queue":
    st.markdown( "<h1 style='font-weight: 800; font-size: 34px; color: #1e3a8a; margin-bottom: 0.5rem;'>Queue Risk Analysis</h1>",
    unsafe_allow_html=True)
    
    # Description popup
    with st.expander("What is Queue Risk?", expanded=False):
        st.markdown("""
        **Queue Risk** measures the likelihood of EV charging congestion based on:
        - **EV-to-Port Ratio**: Number of registered EVs per available charging port (60% weight)
        - **Station Coverage**: Geographic distribution and density of charging stations (40% weight)
        
        Higher scores indicate areas where EV drivers may experience longer wait times or difficulty finding available chargers.
        """)
    
    st.markdown("Adjust Risk Parameters")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        risk_threshold = st.slider("Risk Score Threshold", 0, 100, 50, step=5, key="risk_threshold",
                                   help="Counties above this score are highlighted as high risk")
    with col_b:
        ev_port_max = st.slider("Max EVs per Port (Red Alert)", 50, 500, 200, step=25, key="ev_port_max",
                                help="Counties exceeding this ratio are flagged critical")
    with col_c:
        show_stations_toggle = st.checkbox("Show Charging Stations", value=True, key="show_stations_queue")
    
    st.info(f"Highlighting counties with Queue Risk Score ≥ {risk_threshold} or EVs/Port ≥ {ev_port_max}")

    # Load queue risk data OUTSIDE spinner so it updates with slider changes
    try:
        queue_path = GEO_PATH + "Queue_Risk_Analysis.geojson"
        queue_df = load_geojson(queue_path).copy()
        
        # Ensure numeric columns
        queue_df["Queue_Risk_Score"] = pd.to_numeric(queue_df["Queue_Risk_Score"], errors="coerce").fillna(0)
        queue_df["EVs_per_Port"] = pd.to_numeric(queue_df["EVs_per_Port"], errors="coerce").fillna(0)
        queue_df["Station_Count"] = pd.to_numeric(queue_df["Station_Count"], errors="coerce").fillna(0)
        queue_df["Total_EVs"] = pd.to_numeric(queue_df["Total_EVs"], errors="coerce").fillna(0)
        
    except FileNotFoundError:
        st.error(f"Queue Risk data not found at {queue_path}")
        st.warning("Please run `calculate_queue_risk.py` first to generate the analysis.")
        queue_df = None
    except Exception as e:
        st.error(f"Failed to load queue risk data: {e}")
        queue_df = None

    if queue_df is not None:
        with st.spinner("Generating risk map..."):
            # Create map
            m = folium.Map(
                location=[42.9, -75.5],
                zoom_start=7,
                tiles="CartoDB positron",
                prefer_canvas=True
            )
            
            # Color scale for queue risk
            vmin = 0
            vmax = 100
            colormap = cm.linear.YlOrRd_09.scale(vmin, vmax)
            colormap.caption = "Queue Risk Score (0-100)"
            
            def risk_style(feat):
                score = float(feat["properties"].get("Queue_Risk_Score", 0))
                evs_per_port = float(feat["properties"].get("EVs_per_Port", 0))
                
                # Critical risk styling
                if score >= risk_threshold or evs_per_port >= ev_port_max:
                    return {
                        "fillColor": colormap(score),
                        "color": "#b30000",
                        "weight": 2,
                        "fillOpacity": 0.75
                    }
                else:
                    return {
                        "fillColor": colormap(score),
                        "color": "#666",
                        "weight": 0.8,
                        "fillOpacity": 0.5
                    }
            
            # Add queue risk choropleth
            folium.GeoJson(
                queue_df,
                name="Queue Risk Score",
                style_function=risk_style,
                highlight_function=lambda f: {"weight": 3, "color": "#000", "fillOpacity": 0.9},
                tooltip=folium.GeoJsonTooltip(
                    fields=["NAME", "Queue_Risk_Score", "EVs_per_Port", "Station_Count", "Total_EVs", "Risk_Category"],
                    aliases=["County:", "Risk Score:", "EVs per Port:", "Stations:", "Total EVs:", "Risk Level:"],
                    sticky=True,
                    labels=True,
                    style="font-size: 13px; font-weight: bold;"
                ),
                show=True,
            ).add_to(m)
            
            colormap.add_to(m)
            
            # Add charging stations with risk-based coloring
            if show_stations_toggle:
                try:
                    stations_df = load_csv(station_csv).dropna(subset=["Latitude", "Longitude"])
                    
                    # Calculate station risk (based on county it's in)
                    stations_gdf = gpd.GeoDataFrame(
                        stations_df,
                        geometry=gpd.points_from_xy(stations_df.Longitude, stations_df.Latitude),
                        crs="EPSG:4326"
                    )
                    stations_joined = gpd.sjoin(stations_gdf, queue_df[["NAME", "Queue_Risk_Score", "geometry"]], 
                                               how="left", predicate="within")
                    
                    for _, r in stations_joined.iterrows():
                        county_risk = r.get("Queue_Risk_Score", 0)
                        
                        # Color based on county risk
                        # Color based on county risk (all green scale: light → dark)
                        if county_risk >= 75:
                            color = "#00441b"  # Critical - darkest green
                        elif county_risk >= 50:
                            color = "#238b45"  # High - dark green
                        elif county_risk >= 25:
                            color = "#74c476"  # Moderate - medium green
                        else:
                            color = "#c7e9c0"  # Low - light green

                        
                        # Calculate total ports
                        total_ports = (
                            r.get("ev_level1_evse_num", 0) +
                            r.get("ev_level2_evse_num", 0) +
                            r.get("ev_dc_fast_num", 0)
                        )
                        
                        folium.CircleMarker(
                            location=[r["Latitude"], r["Longitude"]],
                            radius=3,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.8,
                            weight=1.5,
                            popup=folium.Popup(
                                f"<b>{r.get('station_name', 'Station')}</b><br>"
                                f"County Risk: {county_risk:.1f}<br>"
                                f"Total Ports: {total_ports}<br>"
                                f"Level 2: {r.get('ev_level2_evse_num', 0)}<br>"
                                f"DC Fast: {r.get('ev_dc_fast_num', 0)}<br>"
                                f"City: {r.get('city', 'N/A')}<br>"
                                f"Network: {r.get('ev_network', 'N/A')}",
                                max_width=280
                            ),
                        ).add_to(m)
                except Exception as e:
                    st.warning(f"Could not add station markers: {e}")
            
            folium.LayerControl(collapsed=False).add_to(m)
        
        st_folium(m, height=650, use_container_width=True, 
                  key=f"map_queue_{risk_threshold}_{ev_port_max}_{show_stations_toggle}", returned_objects=[])
        
        # Summary Tables
        st.markdown("---")
        st.subheader("Queue Risk Summary")
    
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(" High Risk Counties")
            high_risk = queue_df[queue_df["Queue_Risk_Score"] >= risk_threshold].sort_values(
                "Queue_Risk_Score", ascending=False
            )
            
            if not high_risk.empty:
                display_high = high_risk[["NAME", "Queue_Risk_Score", "EVs_per_Port", "Station_Count"]].copy()
                display_high.columns = ["County", "Risk Score", "EVs/Port", "Stations"]
                st.dataframe(
                    display_high.head(10).reset_index(drop=True).style.format({
                        "Risk Score": "{:.1f}",
                        "EVs/Port": "{:.1f}"
                    }),
                    height=300
                )
            else:
                st.success("No counties exceed the risk threshold!")
        
        with col2:
            st.markdown(" Stations in Critical Areas")
            critical_counties = queue_df[queue_df["Queue_Risk_Score"] >= 75]["NAME"].tolist()
            
            if critical_counties:
                try:
                    stations_df = load_csv(station_csv)
                    critical_stations = stations_df[stations_df["city"].str.contains(
                        "|".join(critical_counties), case=False, na=False
                    )]
                    
                    st.metric("Critical Area Stations", len(critical_stations))
                    st.markdown(f"**Average Ports/Station**: {critical_stations[['ev_level2_evse_num', 'ev_dc_fast_num']].sum(axis=1).mean():.1f}")
                except:
                    st.info("Station details unavailable")
            else:
                st.success(" No critical risk areas!")
        
        # Overall statistics
        st.markdown("---")
        st.markdown("Overall Statistics")
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("Mean Risk Score", f"{queue_df['Queue_Risk_Score'].mean():.1f}")
        with stat_cols[1]:
            st.metric("Critical Risk Counties", (queue_df["Risk_Category"] == "Critical").sum())
        with stat_cols[2]:
            st.metric("High Risk Counties", (queue_df["Risk_Category"] == "High").sum())
        with stat_cols[3]:
            st.metric("Total EVs", f"{queue_df['Total_EVs'].sum():,.0f}")
            
    except Exception as e:
        st.error(f"Could not generate summary: {e}")
# Add this section to replace the existing corridor spacing elif block
# in your 1_Spatial_Explorer.py file (around line 280)
# Add this section to replace the existing corridor spacing elif block
# in your 1_Spatial_Explorer.py file (around line 280)

# ---------------- Corridor Spacing Mode ----------------
elif st.session_state.current_mode == "corridor_spacing":
    st.markdown( "<h1 style='font-weight: 800; font-size: 34px; color: #1e3a8a; margin-bottom: 0.5rem;'>Corridor Spacing Analysis</h1>",
    unsafe_allow_html=True)
    
    # Description
    with st.expander(" What is Corridor Spacing Analysis?", expanded=False):
        st.markdown("""
        **Corridor Spacing Analysis** evaluates EV charging infrastructure along designated corridors:
        - **Coverage Score**: How well stations are distributed (100 = excellent, 0 = critical gaps)
        - **Average Spacing**: Distance between charging stations along the corridor
        - **Gap Categories**: 
          - Well Covered (≤30 mi spacing)
          - Adequate (30-60 mi)
          - Moderate Gap (60-100 mi)
          - Critical Gap (>100 mi)
        
        Ideal spacing is ≤50 miles to avoid EV range anxiety.
        """)
    
    # Controls
    st.markdown(" Filter Corridor Segments")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        gap_filter = st.selectbox(
            "Show Gap Category",
            ["All", "Well Covered", "Adequate", "Moderate Gap", "Critical Gap"],
            key="gap_filter"
        )
    with col_b:
        min_length = st.slider(
            "Min Corridor Length (miles)",
            0, 50, 5,
            key="min_length",
            help="Filter out very short road segments"
        )
    with col_c:
        show_stations_toggle = st.checkbox(
            "Show Charging Stations",
            value=True,
            key="show_stations_corridor"
        )
    
    # Load corridor spacing data
    try:
        corridor_spacing_gdf = load_geojson(corridor_spacing_geo).copy()
        
        # Load NY State boundary to filter corridors
        ny_state = load_geojson(state_path)
        
        # Clip corridors to NY state boundaries
        corridor_spacing_gdf = gpd.clip(corridor_spacing_gdf, ny_state)
        
        # Ensure numeric columns
        corridor_spacing_gdf["Coverage_Score"] = pd.to_numeric(
            corridor_spacing_gdf["Coverage_Score"], errors="coerce"
        ).fillna(0)
        corridor_spacing_gdf["Avg_Spacing_Miles"] = pd.to_numeric(
            corridor_spacing_gdf["Avg_Spacing_Miles"], errors="coerce"
        ).fillna(999)
        corridor_spacing_gdf["Length_Miles"] = pd.to_numeric(
            corridor_spacing_gdf["Length_Miles"], errors="coerce"
        ).fillna(0)
        corridor_spacing_gdf["Num_Stations"] = pd.to_numeric(
            corridor_spacing_gdf["Num_Stations"], errors="coerce"
        ).fillna(0)
        
        # Apply filters
        filtered_corridors = corridor_spacing_gdf[
            corridor_spacing_gdf["Length_Miles"] >= min_length
        ].copy()
        
        if gap_filter != "All":
            filtered_corridors = filtered_corridors[
                filtered_corridors["Gap_Category"] == gap_filter
            ]
        
        st.info(f"Displaying {len(filtered_corridors)} corridor segments (filtered from {len(corridor_spacing_gdf)} total)")
        
    except FileNotFoundError:
        st.error(f"Corridor spacing data not found at {corridor_spacing_geo}")
        st.warning("Please run `calculate_corridor_spacing.py` first to generate the analysis.")
        filtered_corridors = None
    except Exception as e:
        st.error(f"Failed to load corridor spacing data: {e}")
        filtered_corridors = None
    
    # Create map
    if filtered_corridors is not None and len(filtered_corridors) > 0:
        with st.spinner("Generating corridor spacing map..."):
            m = folium.Map(
                location=[42.9, -75.5],
                zoom_start=7,
                tiles="CartoDB positron",
                prefer_canvas=True
            )
            
            # Color scale for coverage score
            colormap = cm.linear.RdYlGn_11.scale(0, 100)
            colormap.caption = "Coverage Score (0=Critical Gap, 100=Well Covered)"
            
            def corridor_style(feat):
                score = float(feat["properties"].get("Coverage_Score", 0))
                category = feat["properties"].get("Gap_Category", "Unknown")
                
                # Color based on gap category
                if category == "Critical Gap":
                    color = "#d73027"  # Dark red
                    weight = 4
                elif category == "Moderate Gap":
                    color = "#fc8d59"  # Orange
                    weight = 3
                elif category == "Adequate":
                    color = "#fee08b"  # Yellow
                    weight = 2.5
                else:  # Well Covered
                    color = "#1a9850"  # Green
                    weight = 2
                
                return {
                    "color": color,
                    "weight": weight,
                    "opacity": 0.8
                }
            
            # Add corridor spacing layer
            folium.GeoJson(
                filtered_corridors,
                name="Corridor Spacing",
                style_function=corridor_style,
                highlight_function=lambda f: {
                    "weight": 6,
                    "color": "#000",
                    "opacity": 1.0
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=[
                        "Road_Name",
                        "Length_Miles",
                        "Num_Stations",
                        "Avg_Spacing_Miles",
                        "Coverage_Score",
                        "Gap_Category"
                    ],
                    aliases=[
                        "Road:",
                        "Length (mi):",
                        "Stations:",
                        "Avg Spacing (mi):",
                        "Coverage Score:",
                        "Gap Category:"
                    ],
                    sticky=True,
                    labels=True,
                    style="font-size: 13px; font-weight: bold;"
                ),
                show=True,
            ).add_to(m)
            
            colormap.add_to(m)
            
            # Add charging stations if requested
            if show_stations_toggle:
                try:
                    stations_df = load_csv(station_csv).dropna(subset=["Latitude", "Longitude"])
                    
                    for _, r in stations_df.iterrows():
                        # Calculate total ports
                        total_ports = (
                            r.get("ev_level1_evse_num", 0) +
                            r.get("ev_level2_evse_num", 0) +
                            r.get("ev_dc_fast_num", 0)
                        )
                        
                        # Color based on station capability
                        if r.get("ev_dc_fast_num", 0) > 0:
                            color = "#7c2d12"  # Brown for DC Fast
                            radius = 5
                        elif r.get("ev_level2_evse_num", 0) > 0:
                            color = "#2563eb"  # Blue for Level 2
                            radius = 4
                        else:
                            color = "#64748b"  # Gray for Level 1
                            radius = 3
                        
                        folium.CircleMarker(
                            location=[r["Latitude"], r["Longitude"]],
                            radius=radius,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.7,
                            weight=1.2,
                            popup=folium.Popup(
                                f"<b>{r.get('station_name', 'Station')}</b><br>"
                                f"Total Ports: {total_ports}<br>"
                                f"Level 2: {r.get('ev_level2_evse_num', 0)}<br>"
                                f"DC Fast: {r.get('ev_dc_fast_num', 0)}<br>"
                                f"City: {r.get('city', 'N/A')}<br>"
                                f"Network: {r.get('ev_network', 'N/A')}",
                                max_width=280
                            ),
                        ).add_to(m)
                except Exception as e:
                    st.warning(f"Could not add station markers: {e}")
            
            folium.LayerControl(collapsed=False).add_to(m)
        
        # Display map with unique key
        st_folium(
            m,
            height=650,
            use_container_width=True,
            key=f"map_corridor_spacing_{gap_filter}_{min_length}_{show_stations_toggle}",
            returned_objects=[]
        )
        
        # Summary Statistics
        st.markdown("---")
        st.subheader("Corridor Spacing Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("Critical & Moderate Gaps")
            gaps = filtered_corridors[
                filtered_corridors["Gap_Category"].isin(["Critical Gap", "Moderate Gap"])
            ].sort_values("Avg_Spacing_Miles", ascending=False)
            
            if not gaps.empty:
                display_gaps = gaps[[
                    "Road_Name",
                    "Length_Miles",
                    "Num_Stations",
                    "Avg_Spacing_Miles",
                    "Gap_Category"
                ]].copy()
                display_gaps.columns = [
                    "Road",
                    "Length (mi)",
                    "Stations",
                    "Avg Spacing (mi)",
                    "Category"
                ]
                st.dataframe(
                    display_gaps.head(10).reset_index(drop=True).style.format({
                        "Length (mi)": "{:.1f}",
                        "Avg Spacing (mi)": "{:.1f}"
                    }),
                    height=300
                )
            else:
                st.success("No critical or moderate gaps in filtered corridors!")
        
        with col2:
            st.markdown("Coverage Distribution")
            category_counts = filtered_corridors["Gap_Category"].value_counts()
            
            for category in ["Well Covered", "Adequate", "Moderate Gap", "Critical Gap"]:
                count = category_counts.get(category, 0)
                pct = (count / len(filtered_corridors) * 100) if len(filtered_corridors) > 0 else 0
                
                # Color-coded metrics
                if category == "Well Covered":
                    st.metric(f" {category}", f"{count} ({pct:.1f}%)")
                elif category == "Adequate":
                    st.metric(f" {category}", f"{count} ({pct:.1f}%)")
                elif category == "Moderate Gap":
                    st.metric(f" {category}", f"{count} ({pct:.1f}%)")
                else:
                    st.metric(f" {category}", f"{count} ({pct:.1f}%)")
        
        # Overall statistics
        st.markdown("---")
        st.markdown("Overall Statistics")
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric(
                "Mean Spacing",
                f"{filtered_corridors['Avg_Spacing_Miles'].mean():.1f} mi"
            )
        with stat_cols[1]:
            st.metric(
                "Max Spacing",
                f"{filtered_corridors['Avg_Spacing_Miles'].max():.1f} mi"
            )
        with stat_cols[2]:
            st.metric(
                "Total Corridor Miles",
                f"{filtered_corridors['Length_Miles'].sum():,.0f}"
            )
        with stat_cols[3]:
            st.metric(
                "Total Stations",
                f"{filtered_corridors['Num_Stations'].sum():,.0f}"
            )
    
    else:
        st.warning("No corridor data available with current filters")


# ---------------- Suitability / Optimization Mode ----------------
elif st.session_state.current_mode == "optimization":
    st.markdown( "<h1 style='font-weight: 800; font-size: 34px; color: #1e3a8a; margin-bottom: 0.5rem;'>Station Placement Priority Analysis</h1>",
    unsafe_allow_html=True)
    
    
    # Description
    with st.expander(" How Priority Scoring Works", expanded=False):
        st.markdown("""
        **Multi-Criteria Priority Scoring** identifies optimal locations for new charging stations using:
        
        **Scoring Criteria (Weighted):**
        - **Corridor Gaps (30%)**: Areas along corridors with large spacing between stations
        - **Equity (25%)**: Disadvantaged Communities (DAC) needing infrastructure
        - **Queue Risk (25%)**: Counties with high EV-to-port ratios
        - **Low Station Density (20%)**: Areas with few existing stations within 5 miles
        
        **Priority Categories:**
        - **Critical**: Score ≥75 - Immediate action recommended
        - **High**: Score 60-74 - Near-term deployment
        - **Moderate**: Score 40-59 - Future consideration
        """)
    
    # Controls
    st.markdown("Optimization Parameters")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        priority_filter = st.selectbox(
            "Show Priority Zones",
            ["All", "Critical Priority", "High Priority", "Moderate Priority"],
            key="priority_filter"
        )
    with col_b:
        min_score = st.slider(
            "Minimum Priority Score",
            0, 100, 40,
            key="min_priority_score",
            help="Filter zones by minimum composite score"
        )
    with col_c:
        show_existing = st.checkbox(
            "Show Existing Stations",
            value=True,
            key="show_existing_stations"
        )
    
    # Weight adjustments
    st.markdown(" Adjust Criteria Weights")
    weight_col1, weight_col2, weight_col3, weight_col4 = st.columns(4)
    with weight_col1:
        corridor_weight = st.slider("Corridor Gap", 0, 100, 30, 5, key="w_corridor") / 100
    with weight_col2:
        equity_weight = st.slider("Equity (DAC)", 0, 100, 25, 5, key="w_equity") / 100
    with weight_col3:
        queue_weight = st.slider("Queue Risk", 0, 100, 25, 5, key="w_queue") / 100
    with weight_col4:
        density_weight = st.slider("Low Density", 0, 100, 20, 5, key="w_density") / 100
    
    # Normalize weights
    total_weight = corridor_weight + equity_weight + queue_weight + density_weight
    if total_weight > 0:
        corridor_weight /= total_weight
        equity_weight /= total_weight
        queue_weight /= total_weight
        density_weight /= total_weight
    # 
    # Load priority zones data
    try:
        priority_zones_path = "GEOJSON/Station_Priority_Zones.geojson"
        priority_gdf = load_geojson(priority_zones_path).copy()
        
        # Spatially join with counties to get county names
        try:
            counties = load_geojson(counties_path)[["NAME", "geometry"]].copy()
            counties = counties.rename(columns={"NAME": "County"})
            
            # Perform spatial join to assign county names
            priority_gdf = gpd.sjoin(
                priority_gdf, 
                counties, 
                how="left", 
                predicate="intersects"
            )
            
            # If a zone intersects multiple counties, keep the first
            if "County" in priority_gdf.columns:
                priority_gdf = priority_gdf.drop_duplicates(subset=priority_gdf.columns.difference(["County"]).tolist())
            
        except Exception as e:
            st.warning(f"Could not assign county names: {e}")
            priority_gdf["County"] = "Unknown"
        
        # Recalculate composite score with user weights
        priority_gdf["Custom_Score"] = (
            priority_gdf["Corridor_Score"] * corridor_weight +
            priority_gdf["Equity_Score"] * equity_weight +
            priority_gdf["Queue_Score"] * queue_weight +
            priority_gdf["Density_Score"] * density_weight
        )
        
        # Reassign categories based on custom score
        def assign_priority(score):
            if score >= 75:
                return "Critical Priority"
            elif score >= 60:
                return "High Priority"
            elif score >= 40:
                return "Moderate Priority"
            else:
                return "Low Priority"
        
        priority_gdf["Custom_Category"] = priority_gdf["Custom_Score"].apply(assign_priority)
        # Apply filters
        filtered_zones = priority_gdf[priority_gdf["Custom_Score"] >= min_score].copy()
        
        if priority_filter != "All":
            filtered_zones = filtered_zones[
                filtered_zones["Custom_Category"] == priority_filter
            ]
        
        st.info(f"Displaying {len(filtered_zones)} priority zones (filtered from {len(priority_gdf)} total)")
        
    except FileNotFoundError:
        st.error(f"Priority zones data not found at {priority_zones_path}")
        st.warning("Please run `calculate_station_priorities.py` first to generate the optimization analysis.")
        filtered_zones = None
    except Exception as e:
        st.error(f"Failed to load priority zones: {e}")
        filtered_zones = None
    
    # Create map
    if filtered_zones is not None and len(filtered_zones) > 0:
        with st.spinner("Generating priority zone map..."):
            m = folium.Map(
                location=[42.9, -75.5],
                zoom_start=7,
                tiles="CartoDB positron",
                prefer_canvas=True
            )
            
            # Color scale for priority scores
            colormap = cm.linear.YlOrRd_09.scale(40, 100)
            colormap.caption = "Priority Score (40=Moderate, 100=Critical)"
            
            def zone_style(feat):
                score = float(feat["properties"].get("Custom_Score", 0))
                category = feat["properties"].get("Custom_Category", "Low Priority")
                
                # Color based on priority
                if category == "Critical Priority":
                    color = "#d73027"
                    opacity = 0.7
                elif category == "High Priority":
                    color = "#fc8d59"
                    opacity = 0.6
                else:  # Moderate
                    color = "#fee08b"
                    opacity = 0.5
                
                return {
                    "fillColor": color,
                    "color": "#000",
                    "weight": 1,
                    "fillOpacity": opacity
                }
            
            # Add priority zones
            folium.GeoJson(
                filtered_zones,
                name="Priority Zones",
                style_function=zone_style,
                highlight_function=lambda f: {
                    "weight": 3,
                    "color": "#000",
                    "fillOpacity": 0.85
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=[
                        "Custom_Score",
                        "Custom_Category",
                        "Corridor_Score",
                        "Equity_Score",
                        "Queue_Score",
                        "Density_Score",
                        "Nearby_Stations"
                    ],
                    aliases=[
                        "Priority Score:",
                        "Category:",
                        "Corridor Gap Score:",
                        "Equity Score:",
                        "Queue Risk Score:",
                        "Low Density Score:",
                        "Existing Stations (5mi):"
                    ],
                    sticky=True,
                    labels=True,
                    style="font-size: 12px; font-weight: bold;"
                ),
                show=True,
            ).add_to(m)
            
            colormap.add_to(m)
            
            # Add existing stations if requested
            if show_existing:
                try:
                    stations_df = load_csv(station_csv).dropna(subset=["Latitude", "Longitude"])
                    
                    for _, r in stations_df.iterrows():
                        # Simple gray markers for existing infrastructure
                        folium.CircleMarker(
                            location=[r["Latitude"], r["Longitude"]],
                            radius=3,
                            color="#64748b",
                            fill=True,
                            fill_color="#64748b",
                            fill_opacity=0.4,
                            weight=0.5,
                            popup=folium.Popup(
                                f"<b>{r.get('station_name', 'Station')}</b><br>"
                                f"City: {r.get('city', 'N/A')}",
                                max_width=200
                            ),
                        ).add_to(m)
                except Exception as e:
                    st.warning(f"Could not load existing stations: {e}")
            
            folium.LayerControl(collapsed=False).add_to(m)
        
        # Display map
        st_folium(
            m,
            height=650,
            use_container_width=True,
            key=f"map_optimization_{priority_filter}_{min_score}_{corridor_weight}",
            returned_objects=[]
        )
        
        # Summary Analysis
        st.markdown("---")
        st.subheader("Priority Zone Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(" Top 10 Priority Zones")
            
            # Ensure County column exists
            if "County" not in filtered_zones.columns:
                filtered_zones["County"] = "Unknown"
            
            top_zones = filtered_zones.nlargest(10, "Custom_Score")[[
                "County",
                "Custom_Score",
                "Custom_Category",
                "Corridor_Score",
                "Equity_Score",
                "Nearby_Stations"
            ]].copy()
            top_zones.columns = [
                "County",
                "Priority Score",
                "Category",
                "Corridor Gap",
                "Equity",
                "Existing Stations"
            ]
            st.dataframe(
                top_zones.reset_index(drop=True).style.format({
                    "Priority Score": "{:.1f}",
                    "Corridor Gap": "{:.1f}",
                    "Equity": "{:.1f}"
                }),
                height=350
            )
        with col2:
            st.markdown("Priority Distribution")
            category_counts = filtered_zones["Custom_Category"].value_counts()
            
            for category in ["Critical Priority", "High Priority", "Moderate Priority"]:
                count = category_counts.get(category, 0)
                if count > 0:
                    pct = (count / len(filtered_zones) * 100)
                    if category == "Critical Priority":
                        st.metric(f" {category}", f"{count} zones ({pct:.1f}%)")
                    elif category == "High Priority":
                        st.metric(f" {category}", f"{count} zones ({pct:.1f}%)")
                    else:
                        st.metric(f" {category}", f"{count} zones ({pct:.1f}%)")
            
            # Investment estimate
            st.markdown("---")
            st.markdown(" Deployment Estimate")
            critical_count = category_counts.get("Critical Priority", 0)
            high_count = category_counts.get("High Priority", 0)
            
            # Assume $150K per station (DC Fast charger)
            cost_per_station = 150000
            total_critical_cost = critical_count * cost_per_station
            total_high_cost = high_count * cost_per_station
            
            st.metric(
                "Critical Zones Investment",
                f"${total_critical_cost/1e6:.1f}M",
                help=f"Assumes 1 station per zone at ${cost_per_station/1000}K each"
            )
            st.metric(
                "High Priority Investment",
                f"${total_high_cost/1e6:.1f}M"
            )
        
        # Overall statistics
        st.markdown("---")
        st.markdown("Scoring Statistics")
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("Mean Score", f"{filtered_zones['Custom_Score'].mean():.1f}")
        with stat_cols[1]:
            st.metric("Median Score", f"{filtered_zones['Custom_Score'].median():.1f}")
        with stat_cols[2]:
            st.metric("Max Score", f"{filtered_zones['Custom_Score'].max():.1f}")
        with stat_cols[3]:
            st.metric("Total Zones", len(filtered_zones))
        
        # Actionable recommendations
        st.markdown("---")
        st.markdown("Recommendations for Planners")
        
        if critical_count > 0:
            st.error(f"**Immediate Action**: {critical_count} critical priority zones identified")
            st.markdown(f"- These areas score ≥75 on composite metrics")
            st.markdown(f"- Combine corridor gaps, equity needs, and queue risk")
            st.markdown(f"- Recommended for immediate funding allocation")
        
        if high_count > 0:
            st.warning(f"**Near-Term Planning**: {high_count} high priority zones")
            st.markdown(f"- Target for 1-2 year deployment timeline")
        
        st.info(" **Tip**: Adjust criteria weights above to match your policy priorities (e.g., increase equity weight for justice-focused deployment)")
        
    else:
        st.warning(" No priority zones meet current filter criteria")
# ---------------- Default ----------------
else:
    st.info(" Select an analysis mode above to begin exploring the data")
    with st.spinner("Loading map..."):
        m = create_base_map(include_stations=st.session_state.show_stations)
    st_folium(m, height=650, use_container_width=True, key="map_default", returned_objects=[])

# At the VERY END of the file, add:
render_footer()