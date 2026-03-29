import streamlit as st
from modules.state import get_state


def render_sidebar():
    with st.sidebar:
        state = get_state()

        # ── Brand
        st.markdown("""
        <div style="padding:1.2rem 0 1rem;border-bottom:1px solid #1e2840;margin-bottom:1.2rem;">
            <div style="font-family:'Inter',sans-serif;font-size:1.2rem;font-weight:700;color:#e8edf5;">
                DataVyn
            </div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#4a566a;
                        letter-spacing:2px;text-transform:uppercase;margin-top:3px;">
                Powered by DataVyn Labs
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Session Stats — read fresh from state every rerun
        df       = state.get("df")
        rows     = f"{len(df):,}"       if df is not None else "—"
        cols     = str(len(df.columns)) if df is not None else "—"
        source   = state.get("source", "—")
        ai_calls = str(state.get("ai_calls", 0))

        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;font-weight:600;
                    color:#4a566a;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.6rem;">
            Session Stats
        </div>
        """, unsafe_allow_html=True)

        for label, value in [("Data Source", source), ("Rows", rows), ("Columns", cols), ("AI Calls", ai_calls)]:
            st.markdown(f"""
            <div style="background:#161c2a;border:1px solid #1e2840;border-radius:8px;
                        padding:0.65rem 0.9rem;margin-bottom:0.4rem;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;
                            color:#4a566a;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:2px;">
                    {label}
                </div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:1rem;
                            font-weight:600;color:#e8edf5;">
                    {value}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Divider
        st.markdown('<div style="border-top:1px solid #1e2840;margin:1rem 0;"></div>', unsafe_allow_html=True)

        # ── Settings
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;font-weight:600;
                    color:#4a566a;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.6rem;">
            Settings
        </div>
        """, unsafe_allow_html=True)

        chart_theme = st.selectbox(
            "Chart Theme",
            ["Neon Dark", "Minimal Dark", "Vibrant", "Monochrome"],
            key="chart_theme",
            label_visibility="collapsed"
        )
        state["chart_theme"] = chart_theme

        # ── Divider
        st.markdown('<div style="border-top:1px solid #1e2840;margin:1rem 0;"></div>', unsafe_allow_html=True)

        # ── API Key
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;font-weight:600;
                    color:#4a566a;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.6rem;">
            Anthropic API Key
        </div>
        """, unsafe_allow_html=True)

        api_key_input = st.text_input(
            "API Key",
            type="password",
            value=state.get("api_key", ""),
            placeholder="sk-ant-...",
            key="api_key_input",
            label_visibility="collapsed"
        )
        if api_key_input:
            state["api_key"] = api_key_input
            st.success("Key saved")

        # ── Footer
        st.markdown("""
        <div style="border-top:1px solid #1e2840;margin-top:2rem;padding-top:0.8rem;
                    font-family:'JetBrains Mono',monospace;font-size:0.58rem;
                    color:#4a566a;text-align:center;">
            DataVyn Labs &nbsp;·&nbsp; v1.0.0
        </div>
        """, unsafe_allow_html=True)