import streamlit as st

st.set_page_config(page_title="Decision Intelligence Engine", layout="centered")

st.markdown(
    """
    <div style="text-align:center; padding-top: 80px;">
        <h1 style="font-size: 48px; color: #1E3A8A;">⚙️ Decision Intelligence Engine</h1>
        <p style="font-size: 20px; color: #374151;">
            A unified platform for analyzing <b>Equity Coverage</b>, <b>Queue Risk</b>, and <b>Infrastructure Suitability</b>
            in the New York Zero-Emission Vehicle transition.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br><br>", unsafe_allow_html=True)

if st.button("🚀 Try It"):
    st.switch_page("pages/1_Spatial_Explorer.py")

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("Cornell Systems Engineering · ZEV-SAGE · Built with Streamlit + Folium")