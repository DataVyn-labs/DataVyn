import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


THEMES = {
    "Neon Dark": {
        "bg": "#0d1328",
        "paper": "#0d1328",
        "font": "#e2e8f0",
        "grid": "#1e2d4a",
        "colors": ["#00f5ff", "#7c3aed", "#f59e0b", "#10b981", "#ec4899", "#3b82f6", "#f97316"],
    },
    "Minimal Dark": {
        "bg": "#111827",
        "paper": "#111827",
        "font": "#d1d5db",
        "grid": "#374151",
        "colors": ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe", "#ede9fe", "#f5f3ff"],
    },
    "Vibrant": {
        "bg": "#0f0f0f",
        "paper": "#0f0f0f",
        "font": "#ffffff",
        "grid": "#222",
        "colors": ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#ff922b", "#cc5de8", "#20c997"],
    },
    "Monochrome": {
        "bg": "#0a0a0a",
        "paper": "#0a0a0a",
        "font": "#e5e5e5",
        "grid": "#2a2a2a",
        "colors": ["#ffffff", "#d4d4d4", "#a3a3a3", "#737373", "#525252", "#404040", "#262626"],
    },
}


def get_layout(theme_name: str, title: str = "") -> dict:
    t = THEMES.get(theme_name, THEMES["Neon Dark"])
    return dict(
        title=dict(text=title, font=dict(color=t["font"], size=14, family="Syne, sans-serif")),
        paper_bgcolor=t["paper"],
        plot_bgcolor=t["bg"],
        font=dict(color=t["font"], family="JetBrains Mono, monospace", size=11),
        xaxis=dict(gridcolor=t["grid"], zeroline=False, showgrid=True),
        yaxis=dict(gridcolor=t["grid"], zeroline=False, showgrid=True),
        margin=dict(l=40, r=20, t=40, b=40),
        colorway=t["colors"],
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=t["font"])),
    )


def render_auto_charts(df: pd.DataFrame, theme: str = "Neon Dark", key_prefix: str = "default"):
    t = THEMES.get(theme, THEMES["Neon Dark"])
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

    # ── Row 1: Metrics
    st.markdown('<div class="dv-section-title" style="font-size:1rem;margin-top:0.5rem;">Dataset Overview</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="dv-metric"><div class="metric-label">Total Rows</div><div class="metric-value">{len(df):,}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="dv-metric"><div class="metric-label">Columns</div><div class="metric-value">{len(df.columns)}</div></div>', unsafe_allow_html=True)
    with m3:
        missing = df.isnull().sum().sum()
        st.markdown(f'<div class="dv-metric"><div class="metric-label">Missing Values</div><div class="metric-value">{missing:,}</div></div>', unsafe_allow_html=True)
    with m4:
        dupes = df.duplicated().sum()
        st.markdown(f'<div class="dv-metric"><div class="metric-label">Duplicates</div><div class="metric-value">{dupes:,}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)

    # ── Data Table Preview
    with st.expander("Data Preview", expanded=False):
        rows_show = st.slider("Rows to display", 5, min(100, len(df)), 10, key=f"{key_prefix}_preview_rows")
        st.dataframe(df.head(rows_show), use_container_width=True)

    # ── Column types breakdown
    with st.expander("Column Summary", expanded=False):
        summary_data = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing_c = df[col].isnull().sum()
            unique_c = df[col].nunique()
            summary_data.append({
                "Column": col,
                "Type": dtype,
                "Missing": missing_c,
                "Unique": unique_c,
                "Sample": str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else "—"
            })
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

    # ── Charts
    if num_cols:
        st.markdown('<div class="dv-section-title" style="font-size:1rem;">Numeric Distributions</div>', unsafe_allow_html=True)

        # Distribution histogram for each numeric col (up to 6)
        show_num = num_cols[:6]
        cols_per_row = 2
        for i in range(0, len(show_num), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, col in enumerate(show_num[i:i+cols_per_row]):
                with row_cols[j]:
                    fig = px.histogram(
                        df, x=col, nbins=30,
                        color_discrete_sequence=[t["colors"][j % len(t["colors"])]]
                    )
                    fig.update_layout(**get_layout(theme, f"{col} Distribution"))
                    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=f"{key_prefix}_hist_{col}")

        # Correlation heatmap (if 2+ numeric cols)
        if len(num_cols) >= 2:
            st.markdown('<div class="dv-section-title" style="font-size:1rem;">Correlation Heatmap</div>', unsafe_allow_html=True)
            corr = df[num_cols].corr()
            fig = go.Figure(go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.index.tolist(),
                colorscale="Viridis",
                text=np.round(corr.values, 2),
                texttemplate="%{text}",
                showscale=True,
            ))
            fig.update_layout(**get_layout(theme, "Feature Correlations"))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=f"{key_prefix}_heatmap")
        if len(num_cols) >= 1:
            st.markdown('<div class="dv-section-title" style="font-size:1rem;">Box Plots</div>', unsafe_allow_html=True)
            selected_box = st.multiselect("Select columns for box plot", num_cols, default=num_cols[:min(4, len(num_cols))], key=f"{key_prefix}_box_cols")
            if selected_box:
                fig = go.Figure()
                for i, col in enumerate(selected_box):
                    fig.add_trace(go.Box(
                        y=df[col].dropna(),
                        name=col,
                        marker_color=t["colors"][i % len(t["colors"])],
                        line_color=t["colors"][i % len(t["colors"])]
                    ))
                fig.update_layout(**get_layout(theme, "Box Plot Comparison"))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=f"{key_prefix}_boxplot")
        if len(num_cols) >= 2:
            st.markdown('<div class="dv-section-title" style="font-size:1rem;">Scatter Explorer</div>', unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                x_col = st.selectbox("X Axis", num_cols, key=f"{key_prefix}_scatter_x")
            with sc2:
                y_col = st.selectbox("Y Axis", num_cols, index=min(1, len(num_cols)-1), key=f"{key_prefix}_scatter_y")
            with sc3:
                color_col = st.selectbox("Color by", ["None"] + cat_cols, key=f"{key_prefix}_scatter_color")
            color_arg = None if color_col == "None" else color_arg if (color_arg := df[color_col].astype(str)) is None else color_col
            fig = px.scatter(
                df, x=x_col, y=y_col,
                color=None if color_col == "None" else df[color_col].astype(str),
                opacity=0.7,
                color_discrete_sequence=t["colors"]
            )
            fig.update_layout(**get_layout(theme, f"{x_col} vs {y_col}"))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=f"{key_prefix}_scatter")
        st.markdown('<div class="dv-section-title" style="font-size:1rem;">Categorical Analysis</div>', unsafe_allow_html=True)
        show_cat = cat_cols[:4]
        cols_row = st.columns(min(2, len(show_cat)))
        for i, col in enumerate(show_cat):
            with cols_row[i % 2]:
                vc = df[col].value_counts().head(12)
                chart_type = st.radio(f"{col} chart type", ["Bar", "Pie"], horizontal=True, key=f"{key_prefix}_cat_type_{col}")
                if chart_type == "Bar":
                    fig = px.bar(
                        x=vc.values, y=vc.index.astype(str),
                        orientation='h',
                        color=vc.index.astype(str),
                        color_discrete_sequence=t["colors"]
                    )
                    fig.update_layout(**get_layout(theme, f"{col} Value Counts"))
                else:
                    fig = px.pie(
                        values=vc.values,
                        names=vc.index.astype(str),
                        color_discrete_sequence=t["colors"],
                        hole=0.4
                    )
                    fig.update_layout(**get_layout(theme, f"{col} Distribution"))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=f"{key_prefix}_cat_{col}")

    if date_cols and num_cols:
        st.markdown('<div class="dv-section-title" style="font-size:1rem;">Time Series</div>', unsafe_allow_html=True)
        date_col = date_cols[0]
        val_col = st.selectbox("Value column", num_cols, key=f"{key_prefix}_ts_val")
        ts_df = df[[date_col, val_col]].dropna().sort_values(date_col)
        fig = px.line(ts_df, x=date_col, y=val_col, color_discrete_sequence=t["colors"])
        fig.update_layout(**get_layout(theme, f"{val_col} over Time"))
        fig.update_traces(line=dict(width=2))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=f"{key_prefix}_timeseries")
    missing_series = df.isnull().sum()
    missing_series = missing_series[missing_series > 0]
    if not missing_series.empty:
        st.markdown('<div class="dv-section-title" style="font-size:1rem;">Missing Values</div>', unsafe_allow_html=True)
        fig = px.bar(
            x=missing_series.index, y=missing_series.values,
            color=missing_series.values,
            color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            labels={"x": "Column", "y": "Missing Count"}
        )
        fig.update_layout(**get_layout(theme, "Missing Value Distribution"))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False}, key=f"{key_prefix}_missing")