import streamlit as st
from modules.state import get_state


def render_overview():
    st.markdown("""
    <div class="dv-section-title">Welcome to DataVyn</div>
    <div class="dv-section-sub">AUTOMATED DATA INTELLIGENCE — POWERED BY DATAVYN LABS</div>
    """, unsafe_allow_html=True)

    state = get_state()
    df = state.get("df")

    if df is not None:
        source = state.get("source", "Unknown")
        st.markdown(f"""
        <div class="dv-card dv-card-green">
            <h3>Data Ready</h3>
            <p><strong>{source}</strong> — {len(df):,} rows × {len(df.columns)} columns loaded.
            Go to the <strong>Upload Data</strong> tab to explore charts and insights.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="fc-badge badge-cyan">Core</span>
            <div class="fc-icon fc-icon-blue">CSV</div>
            <div class="fc-title">Multi-Format Ingestion</div>
            <div class="fc-desc">Upload CSV, JSON, Excel, Parquet, TSV — instantly converted to rich visualizations and summaries.</div>
        </div>
        <div class="feature-card">
            <span class="fc-badge badge-violet">Connect</span>
            <div class="fc-icon fc-icon-purple">KGL</div>
            <div class="fc-title">Kaggle Integration</div>
            <div class="fc-desc">Connect with your Kaggle credentials to pull datasets directly into your workspace.</div>
        </div>
        <div class="feature-card">
            <span class="fc-badge badge-amber">Connect</span>
            <div class="fc-icon fc-icon-amber">DB</div>
            <div class="fc-title">Database Connect</div>
            <div class="fc-desc">Query SQLite, PostgreSQL, MySQL databases and fetch live data into your pipeline.</div>
        </div>
        <div class="feature-card">
            <span class="fc-badge badge-green">AI</span>
            <div class="fc-icon fc-icon-green">AI</div>
            <div class="fc-title">AI-Powered Insights</div>
            <div class="fc-desc">Use your Anthropic API key to get deep contextual insights, anomaly detection, and narrative summaries.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)
    st.markdown('<div class="dv-section-title" style="font-size:0.9rem;">Quick Start</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="insight-block"><strong>Step 1</strong><br>Upload a CSV, JSON, or Excel file via the Upload Data tab.</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="insight-block violet"><strong>Step 2</strong><br>Explore auto-generated charts, statistics, and column analysis.</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="insight-block amber"><strong>Step 3</strong><br>Add your Anthropic key in the sidebar, run AI Insights, and export a PDF.</div>', unsafe_allow_html=True)