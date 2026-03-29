import streamlit as st


def get_state() -> dict:
    """Central session state accessor."""
    if "dv_state" not in st.session_state:
        st.session_state["dv_state"] = {
            "df": None,
            "source": "—",
            "filename": None,
            "api_key": "",
            "ai_calls": 0,
            "chart_theme": "Neon Dark",
            "insights_cache": {},
        }
    return st.session_state["dv_state"]
