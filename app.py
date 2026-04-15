import streamlit as st
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="DataVyn",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from modules.sidebar import render_sidebar
from modules.upload import render_upload
from modules.kaggle_connect import render_kaggle
from modules.db_connect import render_db
from modules.ai_insights import render_ai_insights
from modules.overview import render_overview

def main():
    render_sidebar()

    st.markdown("""
    <div class="dv-header">
        <div class="dv-logo-row">
            <span class="dv-logo-icon">DV</span>
            <span class="dv-logo-text">DataVyn</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a566a;
                    letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px;">
            Powered by DataVyn Labs
        </div>
        <p class="dv-tagline">Automate Your Data. Illuminate Your Insights.</p>
    </div>
    """, unsafe_allow_html=True)

        
    st.info(" DISCLAIMER: DataVyn is currently in early beta. This app is intended for prototyping and testing purposes for [organisation](https://github.com/DataVyn-labs). For more info Visit [DataVyn](https://datavyn.vercel.app)")

    tabs = st.tabs(["Overview", "Upload Data", "Kaggle Connect", "Database Connect", "AI Insights"])

    with tabs[0]: render_overview()
    with tabs[1]: render_upload()
    with tabs[2]: render_kaggle()
    with tabs[3]: render_db()
    with tabs[4]: render_ai_insights()

if __name__ == "__main__":
    main()
    
