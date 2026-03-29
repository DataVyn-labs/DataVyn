import streamlit as st
import pandas as pd
from modules.state import get_state
from modules.charts import render_auto_charts
from modules.export import render_export_section


SUPPORTED = {
    "csv":     pd.read_csv,
    "tsv":     lambda f: pd.read_csv(f, sep="\t"),
    "json":    lambda f: pd.read_json(f),
    "xlsx":    lambda f: pd.read_excel(f),
    "xls":     lambda f: pd.read_excel(f),
    "parquet": lambda f: pd.read_parquet(f),
}


def parse_file(uploaded_file) -> pd.DataFrame:
    ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
    if ext not in SUPPORTED:
        raise ValueError(f"Unsupported file type: .{ext}")
    return SUPPORTED[ext](uploaded_file)


def render_upload():
    st.markdown("""
    <div class="dv-section-title">Upload Data</div>
    <div class="dv-section-sub">CSV · JSON · EXCEL · PARQUET · TSV</div>
    """, unsafe_allow_html=True)

    state = get_state()

    uploaded = st.file_uploader(
        "Drop your data file here or click to browse",
        type=["csv", "tsv", "json", "xlsx", "xls", "parquet"],
    )

    # Only parse when a NEW file is uploaded (filename changed)
    if uploaded is not None:
        last = st.session_state.get("_last_uploaded_file")
        if last != uploaded.name:
            with st.spinner("Parsing your data..."):
                try:
                    df = parse_file(uploaded)

                    # Auto-detect datetime columns
                    for col in df.columns:
                        if df[col].dtype == object:
                            try:
                                df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
                            except Exception:
                                pass

                    state["df"] = df
                    state["source"] = uploaded.name
                    state["filename"] = uploaded.name
                    # Mark this file as processed — prevents re-parse on every rerun
                    st.session_state["_last_uploaded_file"] = uploaded.name
                    st.success(f"Loaded **{uploaded.name}** — {len(df):,} rows × {len(df.columns)} columns")
                except Exception as e:
                    st.error(f"Failed to parse file: {e}")
                    return

    # Only show charts if data was loaded from THIS tab (upload source)
    df = state.get("df")

    if df is not None and state.get("source") is not None:
        theme = state.get("chart_theme", "Neon Dark")

        with st.expander("Data Cleaning Options", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Drop All Duplicates", key="drop_dupes"):
                    before = len(df)
                    df = df.drop_duplicates()
                    state["df"] = df
                    st.success(f"Removed {before - len(df)} duplicate rows")
                if st.button("Drop Rows with Any NaN", key="drop_nan"):
                    before = len(df)
                    df = df.dropna()
                    state["df"] = df
                    st.success(f"Removed {before - len(df)} rows")
            with c2:
                import numpy as np
                fill_strategy = st.selectbox(
                    "Fill NaN Strategy",
                    ["None", "Mean (numeric)", "Median (numeric)", "Mode", "Zero"],
                    key="fill_strat"
                )
                if st.button("Apply Fill Strategy", key="apply_fill"):
                    num_cols = df.select_dtypes(include=[np.number]).columns
                    if fill_strategy == "Mean (numeric)":
                        df[num_cols] = df[num_cols].fillna(df[num_cols].mean())
                    elif fill_strategy == "Median (numeric)":
                        df[num_cols] = df[num_cols].fillna(df[num_cols].median())
                    elif fill_strategy == "Mode":
                        df = df.fillna(df.mode().iloc[0])
                    elif fill_strategy == "Zero":
                        df = df.fillna(0)
                    state["df"] = df
                    st.success("NaN values filled")

        render_auto_charts(df, theme, key_prefix="upload")
        render_export_section(df, state.get("filename", "datavyn_export"))

    elif df is None:
        st.markdown("""
        <div class="dv-card">
            <h3>Supported Formats</h3>
            <p>
                <strong>CSV / TSV</strong> — comma or tab separated values<br>
                <strong>JSON</strong> — flat or nested JSON arrays<br>
                <strong>Excel</strong> — .xlsx and .xls files<br>
                <strong>Parquet</strong> — columnar binary format
            </p>
        </div>
        """, unsafe_allow_html=True)