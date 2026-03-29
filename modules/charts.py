import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


THEMES = {
    "Neon Dark": {
        "bg": "#0d1117", "paper": "#0d1117",
        "font": "#e2e8f0", "grid": "#1e2840",
        "colors": ["#4f8ef7", "#3ecf8e", "#f0a429", "#f06060", "#a78bfa", "#38bdf8", "#fb923c"],
    },
    "Minimal Dark": {
        "bg": "#111827", "paper": "#111827",
        "font": "#d1d5db", "grid": "#374151",
        "colors": ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#818cf8", "#4f46e5", "#7c3aed"],
    },
    "Vibrant": {
        "bg": "#0f0f0f", "paper": "#0f0f0f",
        "font": "#ffffff", "grid": "#222",
        "colors": ["#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#ff922b", "#cc5de8", "#20c997"],
    },
    "Monochrome": {
        "bg": "#0a0a0a", "paper": "#0a0a0a",
        "font": "#e5e5e5", "grid": "#2a2a2a",
        "colors": ["#ffffff", "#d4d4d4", "#a3a3a3", "#737373", "#525252", "#404040", "#262626"],
    },
}


def get_layout(theme_name: str, height: int = 320) -> dict:
    t = THEMES.get(theme_name, THEMES["Neon Dark"])
    return dict(
        paper_bgcolor=t["paper"],
        plot_bgcolor=t["bg"],
        font=dict(color=t["font"], family="JetBrains Mono, monospace", size=10),
        xaxis=dict(gridcolor=t["grid"], zeroline=False, showgrid=True, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=t["grid"], zeroline=False, showgrid=True, tickfont=dict(size=10)),
        margin=dict(l=44, r=16, t=16, b=36),
        colorway=t["colors"],
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=t["font"], size=10)),
        height=height,
        hoverlabel=dict(bgcolor="#161c2a", font_size=11, font_family="JetBrains Mono"),
    )


def section_header(title: str, sub: str = ""):
    st.markdown(f"""
    <div style="margin:1.8rem 0 0.9rem;">
        <div style="font-family:'Inter',sans-serif;font-size:0.95rem;font-weight:600;color:#e8edf5;">{title}</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#4a566a;
                    letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def card_wrap_open(title: str, subtitle: str = "", accent: str = "#4f8ef7"):
    st.markdown(f"""
    <div style="border:1px solid #1e2840;border-radius:12px;overflow:hidden;
                margin-bottom:1rem;background:#161c2a;border-top:2px solid {accent};">
        <div style="padding:0.8rem 1.1rem 0.4rem;">
            <div style="font-family:'Inter',sans-serif;font-size:0.85rem;font-weight:600;color:#e8edf5;">{title}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#4a566a;
                        letter-spacing:1px;margin-top:1px;">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)


def card_wrap_close():
    st.markdown("<div style='padding:0.5rem'></div></div>", unsafe_allow_html=True)


def insight_pill(text: str, color: str = "#4f8ef7"):
    return f"""<span style="display:inline-block;background:{color}18;border:1px solid {color}44;
    border-radius:4px;padding:2px 8px;font-family:'JetBrains Mono',monospace;
    font-size:0.7rem;color:{color};margin:2px 3px 2px 0;">{text}</span>"""


def stat_mini(label: str, value: str, accent: str = "#4f8ef7"):
    return f"""
    <div style="background:#0d1117;border:1px solid #1e2840;border-radius:8px;
                padding:0.65rem 0.9rem;border-left:2px solid {accent};">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#4a566a;
                    letter-spacing:1.5px;text-transform:uppercase;">{label}</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:1rem;font-weight:600;
                    color:#e8edf5;margin-top:2px;">{value}</div>
    </div>"""


# ── Main ──────────────────────────────────────────────────────────────────────
def render_auto_charts(df: pd.DataFrame, theme: str = "Neon Dark", key_prefix: str = "default"):
    t      = THEMES.get(theme, THEMES["Neon Dark"])
    colors = t["colors"]
    num_cols  = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols  = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

    # ── SECTION 1: DATASET SNAPSHOT ──────────────────────────────────────────
    section_header("Dataset Snapshot", "KEY METRICS AT A GLANCE")

    completeness = round((1 - df.isnull().sum().sum() / max(df.size, 1)) * 100, 1)
    memory_kb    = round(df.memory_usage(deep=True).sum() / 1024, 1)
    dupes        = int(df.duplicated().sum())
    missing_tot  = int(df.isnull().sum().sum())

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, label, val, accent in [
        (c1, "Rows",         f"{len(df):,}",        colors[0]),
        (c2, "Columns",      str(len(df.columns)),  colors[1]),
        (c3, "Completeness", f"{completeness}%",    colors[2] if completeness > 90 else colors[3]),
        (c4, "Missing",      f"{missing_tot:,}",    colors[3] if missing_tot > 0 else colors[1]),
        (c5, "Duplicates",   f"{dupes:,}",          colors[3] if dupes > 0 else colors[1]),
        (c6, "Memory",       f"{memory_kb} KB",     colors[4]),
    ]:
        with col:
            st.markdown(stat_mini(label, val, accent), unsafe_allow_html=True)

    # ── SECTION 2: DATA QUALITY ───────────────────────────────────────────────
    section_header("Data Quality", "PER-COLUMN HEALTH CHECK")

    quality_rows = []
    for col in df.columns:
        miss_pct = round(df[col].isnull().mean() * 100, 1)
        unique   = df[col].nunique()
        dtype    = str(df[col].dtype)
        status   = "Good" if miss_pct == 0 else ("Warning" if miss_pct < 10 else "Poor")
        quality_rows.append({
            "Column": col, "Type": dtype,
            "Missing %": f"{miss_pct}%",
            "Unique Values": unique,
            "Status": status,
        })

    st.dataframe(
        pd.DataFrame(quality_rows),
        use_container_width=True,
        hide_index=True,
    )

    # ── SECTION 3: CATEGORICAL INSIGHTS ──────────────────────────────────────
    if cat_cols:
        section_header("Categorical Analysis", "DISTRIBUTION OF TEXT COLUMNS")

        show_cat = cat_cols[:4]
        for i in range(0, len(show_cat), 2):
            cols_pair = st.columns(2)
            for j, col in enumerate(show_cat[i:i+2]):
                with cols_pair[j]:
                    vc     = df[col].value_counts().head(8)
                    accent = colors[(i + j) % len(colors)]
                    top_val       = vc.index[0]
                    top_pct       = round(vc.values[0] / len(df) * 100, 1)
                    coverage_pct  = round(vc.values[:3].sum() / len(df) * 100, 1)

                    # Insight pills
                    pills = (
                        insight_pill(f"Top: {top_val}", accent) +
                        insight_pill(f"{top_pct}% dominant", colors[2]) +
                        insight_pill(f"Top-3 = {coverage_pct}%", colors[1]) +
                        insight_pill(f"{df[col].nunique()} unique", colors[4])
                    )

                    card_wrap_open(col, f"{df[col].nunique()} UNIQUE VALUES", accent=accent)
                    st.markdown(f"<div style='padding:0 1.1rem 0.6rem'>{pills}</div>",
                                unsafe_allow_html=True)

                    chart_type = st.radio(
                        "Chart type", ["Bar", "Pie"],
                        horizontal=True,
                        key=f"{key_prefix}_cat_type_{col}",
                        label_visibility="collapsed"
                    )

                    if chart_type == "Bar":
                        fig = px.bar(
                            x=vc.values,
                            y=vc.index.astype(str),
                            orientation="h",
                            color_discrete_sequence=[accent],
                        )
                        fig.update_traces(marker_line_width=0)
                        fig.update_layout(**get_layout(theme, height=260))
                    else:
                        fig = px.pie(
                            values=vc.values,
                            names=vc.index.astype(str),
                            color_discrete_sequence=colors,
                            hole=0.4,
                        )
                        fig.update_traces(
                            textposition="inside",
                            textinfo="percent+label",
                            textfont_size=10,
                        )
                        fig.update_layout(**get_layout(theme, height=260))

                    st.plotly_chart(fig, width="stretch",
                                    config={"displayModeBar": False},
                                    key=f"{key_prefix}_cat_{col}")
                    card_wrap_close()

    # ── SECTION 4: NUMERIC INSIGHTS ───────────────────────────────────────────
    if num_cols:
        section_header("Numeric Insights", "DISTRIBUTIONS · OUTLIERS · RELATIONSHIPS")

        # ── Per-column insight cards
        show_num = num_cols[:6]
        for i in range(0, len(show_num), 3):
            row = st.columns(3)
            for j, col in enumerate(show_num[i:i+3]):
                with row[j]:
                    s       = df[col].dropna()
                    mean_v  = round(float(s.mean()), 2)
                    median_v= round(float(s.median()), 2)
                    std_v   = round(float(s.std()), 2)
                    skew_v  = round(float(s.skew()), 2)
                    q1, q3  = float(np.percentile(s, 25)), float(np.percentile(s, 75))
                    iqr_v   = round(q3 - q1, 2)
                    outliers= int(((s < q1 - 1.5*iqr_v) | (s > q3 + 1.5*iqr_v)).sum())
                    skew_label = "Normal" if abs(skew_v) < 0.5 else ("Right skewed" if skew_v > 0 else "Left skewed")
                    accent  = colors[(i + j) % len(colors)]

                    pills = (
                        insight_pill(skew_label, accent) +
                        insight_pill(f"{outliers} outliers", colors[3] if outliers > 0 else colors[1]) +
                        insight_pill(f"IQR {iqr_v}", colors[4])
                    )

                    st.markdown(f"""
                    <div style="background:#161c2a;border:1px solid #1e2840;border-radius:10px;
                                padding:0.9rem 1rem;border-top:2px solid {accent};margin-bottom:0.5rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                                    color:#4a566a;letter-spacing:1.5px;text-transform:uppercase;
                                    margin-bottom:6px;">{col}</div>
                        <div style="display:flex;gap:1rem;margin-bottom:8px;">
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#4a566a;">MEAN</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:600;color:#e8edf5;">{mean_v}</div>
                            </div>
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#4a566a;">MEDIAN</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:600;color:#e8edf5;">{median_v}</div>
                            </div>
                            <div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#4a566a;">STD DEV</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:0.95rem;font-weight:600;color:#e8edf5;">{std_v}</div>
                            </div>
                        </div>
                        <div>{pills}</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)

        # ── Distribution chart (top 4 numeric, 2 per row)
        for i in range(0, min(len(show_num), 4), 2):
            row = st.columns(2)
            for j, col in enumerate(show_num[i:i+2]):
                with row[j]:
                    accent = colors[(i + j) % len(colors)]
                    card_wrap_open(f"{col}", "DISTRIBUTION · HISTOGRAM", accent=accent)
                    fig = px.histogram(df, x=col, nbins=25, color_discrete_sequence=[accent])
                    fig.add_vline(x=df[col].mean(), line_dash="dash",
                                  line_color="#e8edf5", line_width=1, opacity=0.5)
                    fig.update_traces(marker_line_width=0, opacity=0.9)
                    fig.update_layout(**get_layout(theme, height=240))
                    st.plotly_chart(fig, width="stretch",
                                    config={"displayModeBar": False},
                                    key=f"{key_prefix}_hist_{col}")
                    card_wrap_close()

        # ── Correlation heatmap (only if 3+ numeric cols — actually useful)
        if len(num_cols) >= 3:
            card_wrap_open("Correlation Matrix", "PEARSON · HOW COLUMNS RELATE TO EACH OTHER", accent=colors[1])
            corr = df[num_cols].corr().round(2)
            fig  = go.Figure(go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.index.tolist(),
                colorscale=[[0, "#f06060"], [0.5, "#161c2a"], [1, "#4f8ef7"]],
                zmid=0,
                text=corr.values.round(2),
                texttemplate="%{text}",
                textfont=dict(size=10),
                showscale=True,
            ))
            fig.update_layout(**get_layout(theme, height=360))
            st.plotly_chart(fig, width="stretch",
                            config={"displayModeBar": False},
                            key=f"{key_prefix}_heatmap")

            # Highlight strong correlations as insights
            strong = []
            for a in range(len(corr)):
                for b in range(a+1, len(corr)):
                    val = corr.iloc[a, b]
                    if abs(val) >= 0.6:
                        direction = "positive" if val > 0 else "negative"
                        strong.append(f"{corr.index[a]} ↔ {corr.columns[b]}: {val} ({direction})")
            if strong:
                pills_html = "".join(insight_pill(s, colors[1] if "positive" in s else colors[3]) for s in strong[:6])
                st.markdown(f"<div style='padding:0.5rem 0 0.3rem'><strong style='font-size:0.78rem;color:#8895aa;'>Strong correlations:</strong><br>{pills_html}</div>", unsafe_allow_html=True)
            card_wrap_close()

        # ── Scatter (only if 2+ numeric cols)
        if len(num_cols) >= 2:
            card_wrap_open("Scatter Explorer", "PICK ANY TWO COLUMNS TO COMPARE", accent=colors[0])
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                x_col = st.selectbox("X", num_cols, key=f"{key_prefix}_scatter_x", label_visibility="collapsed")
            with sc2:
                y_col = st.selectbox("Y", num_cols, index=min(1, len(num_cols)-1), key=f"{key_prefix}_scatter_y", label_visibility="collapsed")
            with sc3:
                color_col = st.selectbox("Color by", ["None"] + cat_cols, key=f"{key_prefix}_scatter_color", label_visibility="collapsed")

            # Disable trendline if x == y or statsmodels not available
            try:
                import statsmodels  # noqa
                trendline = "ols" if (color_col == "None" and x_col != y_col) else None
            except ImportError:
                trendline = None

            try:
                fig = px.scatter(
                    df, x=x_col, y=y_col,
                    color=None if color_col == "None" else df[color_col].astype(str),
                    opacity=0.75,
                    color_discrete_sequence=colors,
                    trendline=trendline,
                    trendline_color_override="#e8edf5" if trendline else None,
                )
                fig.update_traces(marker=dict(size=6, line=dict(width=0)))
                fig.update_layout(**get_layout(theme, height=340))
                st.plotly_chart(fig, width="stretch",
                                config={"displayModeBar": False},
                                key=f"{key_prefix}_scatter")
            except Exception as e:
                st.warning(f"Could not render scatter plot: {e}")
            card_wrap_close()

    # ── SECTION 5: TIME SERIES ────────────────────────────────────────────────
    if date_cols and num_cols:
        section_header("Time Series", "TRENDS OVER TIME")
        ts1, ts2 = st.columns(2)
        with ts1:
            val_col = st.selectbox("Value", num_cols, key=f"{key_prefix}_ts_val", label_visibility="collapsed")
        with ts2:
            ts_type = st.radio("Type", ["Line", "Area", "Bar"], horizontal=True,
                               key=f"{key_prefix}_ts_type", label_visibility="collapsed")

        ts_df = df[[date_cols[0], val_col]].dropna().sort_values(date_cols[0])
        card_wrap_open(f"{val_col} over Time", f"{ts_type.upper()} · TIME SERIES", accent=colors[0])
        if ts_type == "Line":
            fig = px.line(ts_df, x=date_cols[0], y=val_col, color_discrete_sequence=colors)
            fig.update_traces(line=dict(width=2))
        elif ts_type == "Area":
            fig = px.area(ts_df, x=date_cols[0], y=val_col, color_discrete_sequence=colors)
            fig.update_traces(line=dict(width=2))
        else:
            fig = px.bar(ts_df, x=date_cols[0], y=val_col, color_discrete_sequence=colors)
        fig.update_layout(**get_layout(theme, height=320))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False},
                        key=f"{key_prefix}_timeseries")
        card_wrap_close()

    # ── SECTION 6: MISSING VALUE MAP ─────────────────────────────────────────
    missing_series = df.isnull().sum()
    missing_series = missing_series[missing_series > 0]
    if not missing_series.empty:
        section_header("Missing Value Map", "COLUMNS WITH NULL DATA")
        card_wrap_open("Missing Values by Column", "COUNT OF NULLS", accent=colors[3])
        fig = px.bar(
            x=missing_series.index, y=missing_series.values,
            color=missing_series.values,
            color_continuous_scale=[[0, "#3ecf8e"], [0.5, "#f0a429"], [1, "#f06060"]],
            labels={"x": "Column", "y": "Missing Count", "color": "Count"},
        )
        fig.update_traces(marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        fig.update_layout(**get_layout(theme, height=260))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False},
                        key=f"{key_prefix}_missing")
        card_wrap_close()

    # ── SECTION 7: RAW DATA ───────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    with st.expander("Data Preview", expanded=False):
        n = st.slider("Rows", 5, min(200, len(df)), 10, key=f"{key_prefix}_preview_rows")
        st.dataframe(df.head(n), use_container_width=True, hide_index=True)