# header.py
import base64
from pathlib import Path
import streamlit as st

def render_header(title="Decision Intelligence Engine", logo_path="die.png"):
    logo_file = Path(logo_path)

    if logo_file.exists():
        with open(logo_file, "rb") as f:
            logo_data = base64.b64encode(f.read()).decode()
        logo_html = f"""
        <div class="custom-header">
            <img src="data:image/png;base64,{logo_data}" class="custom-header-logo" alt="DIE Logo">
            <h1>{title}</h1>
        </div>
        """
    else:
        logo_html = f"<h1>{title}</h1>"

    st.markdown("""
    <style>
    .custom-header {
        display: flex;
        align-items: center;
        gap: 15px;
        background: linear-gradient(90deg, #0A2E6E 0%, #1C68D4 100%);
        color: white;
        padding: 10px 25px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .custom-header-logo {
        width: 180px !important;   /* ✅ adjust logo size here */
        height: auto !important;
    }
    .custom-header h1 {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(logo_html, unsafe_allow_html=True)
