import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
import io
from modules.state import get_state


# ── System prompt — the analyst persona ───────────────────────────────────────
ANALYST_SYSTEM = """You are DataVyn AI — a senior data analyst and business strategist.
Your job is NOT to describe data. Your job is to drive decisions.

STRICT OUTPUT FORMAT — every insight must follow this structure exactly:

## INSIGHT [N] — [TITLE] | Priority: HIGH / MEDIUM / LOW

**Insight:** What specifically changed or stands out (data-backed, specific numbers)
**Reason:** Why this happened — root cause, not surface observation
**Action:** Exactly what the user should do next (specific, concrete)
**Impact:** Expected outcome if the action is taken

---

REQUIRED INSIGHT TYPES (cover as many as apply):
- Actionable insights (primary)
- Root cause analysis
- Trend & forecast
- Anomaly detection
- Segmentation (high vs low value groups)
- Correlation insights
- Data quality alerts

RULES:
- Never just describe the data
- Always explain the "why"
- Prioritize: show top 3-5 insights only, most important first
- Be concise, specific, numbers-driven
- End with a "DAILY ANALYST REPORT" section

## DAILY ANALYST REPORT
**Top Changes:** [1-2 sentences]
**Why It Happened:** [1-2 sentences, data-backed]
**What To Do Next:** [1-3 bullet points, concrete actions]
"""

PROMPT_TEMPLATES = {
    "Full AI Report": """Analyze this dataset as a senior data analyst. Give decision-driven insights only.

Dataset: {data_info}
Statistics: {stats}
Sample rows: {sample}
Column details: {column_details}

Produce the top 5 most important insights following the strict format. End with the Daily Analyst Report.""",

    "Anomaly Detection": """You are an anomaly detection specialist. Scan this dataset for anything unusual.

Dataset: {data_info}
Statistics: {stats}
Sample rows: {sample}

Find the top 3-5 anomalies. For each one follow the strict insight format.
Focus on: outliers, impossible values, suspicious patterns, sudden spikes/drops, data inconsistencies.""",

    "Trend & Forecast": """You are a forecasting analyst. Analyze trends and project what happens next.

Dataset: {data_info}
Statistics: {stats}
Sample rows: {sample}

Identify the top 3-5 trends. For each follow the strict insight format.
Include: direction of change, rate of change, forecast for next period, confidence level.""",

    "Segmentation": """You are a segmentation analyst. Identify high vs low value groups in this data.

Dataset: {data_info}
Statistics: {stats}
Column details: {column_details}
Sample rows: {sample}

Find the top 3-5 segmentation insights. For each follow the strict insight format.
Focus on: which groups perform best/worst, what separates them, where to focus resources.""",

    "Correlation Analysis": """You are a correlation analyst. Find what drives outcomes in this data.

Dataset: {data_info}
Statistics: {stats}
Sample rows: {sample}

Find the top 3-5 correlation insights. For each follow the strict insight format.
Focus on: what predicts what, causal relationships, which variables to focus on.""",

    "Data Quality Audit": """You are a data quality engineer. Audit this dataset for issues.

Dataset: {data_info}
Column details: {column_details}
Sample rows: {sample}

Find top 3-5 data quality issues. For each follow the strict insight format.
Cover: missing data impact, inconsistencies, type issues, duplicates, what to fix first.""",

    "Ask the Analyst": None,
}

PRIORITY_COLORS = {
    "HIGH":   ("#f06060", "#f0606020"),
    "MEDIUM": ("#f0a429", "#f0a42920"),
    "LOW":    ("#3ecf8e", "#3ecf8e20"),
}


def build_context(df: pd.DataFrame) -> dict:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    data_info = (
        f"Rows: {len(df):,} | Columns: {len(df.columns)}\n"
        f"Numeric columns: {', '.join(num_cols)}\n"
        f"Categorical columns: {', '.join(cat_cols)}\n"
        f"Missing values: {df.isnull().sum().sum():,}\n"
        f"Duplicate rows: {df.duplicated().sum():,}\n"
    )

    stats = ""
    if num_cols:
        desc = df[num_cols].describe().round(3)
        stats = desc.to_string()
        # Add skew and correlation hints
        skews = df[num_cols].skew().round(2)
        stats += f"\n\nSkewness:\n{skews.to_string()}"
        if len(num_cols) >= 2:
            corr = df[num_cols].corr().round(2)
            # Only strong correlations
            strong = []
            for i in range(len(corr)):
                for j in range(i+1, len(corr)):
                    v = corr.iloc[i, j]
                    if abs(v) >= 0.5:
                        strong.append(f"{corr.index[i]} <-> {corr.columns[j]}: {v}")
            if strong:
                stats += f"\n\nStrong correlations (|r|>=0.5):\n" + "\n".join(strong)

    column_details = ""
    for col in df.columns:
        vc    = df[col].value_counts().head(3)
        miss  = df[col].isnull().sum()
        uniq  = df[col].nunique()
        dtype = str(df[col].dtype)
        column_details += f"\n{col} ({dtype}): missing={miss}, unique={uniq}, top_values={vc.index.tolist()}"

    sample = df.head(8).to_string()

    return {
        "data_info":      data_info,
        "stats":          stats,
        "column_details": column_details,
        "sample":         sample,
    }


def call_claude(api_key: str, prompt: str, system: str = ANALYST_SYSTEM) -> str:
    headers = {
        "x-api-key":         api_key,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    body = {
        "model":      "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "system":     system,
        "messages":   [{"role": "user", "content": prompt}],
    }
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers, json=body, timeout=90
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"]


def render_insight_output(text: str):
    """Parse and render the structured insight output beautifully."""

    sections = text.split("\n## ")
    for i, section in enumerate(sections):
        if not section.strip():
            continue

        raw = ("## " + section) if i > 0 else section

        # ── Daily Analyst Report block
        if "DAILY ANALYST REPORT" in raw.upper():
            st.markdown("""
            <div style="background:#0d1117;border:1px solid #4f8ef7;border-radius:12px;
                        padding:1.2rem 1.4rem;margin:1.2rem 0 0.5rem;border-top:2px solid #4f8ef7;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                            color:#4f8ef7;letter-spacing:2px;text-transform:uppercase;
                            margin-bottom:0.8rem;">Daily Analyst Report</div>
            """, unsafe_allow_html=True)
            lines = raw.split("\n")[1:]
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("**") and line.endswith("**"):
                    label = line.strip("*")
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.82rem;font-weight:600;color:#e8edf5;margin:0.5rem 0 0.1rem;'>{label}</div>", unsafe_allow_html=True)
                elif line.startswith("**"):
                    parts = line.split("**")
                    label = parts[1] if len(parts) > 1 else ""
                    rest  = parts[2] if len(parts) > 2 else ""
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.82rem;margin:0.3rem 0;'><span style='font-weight:600;color:#e8edf5;'>{label}</span><span style='color:#8895aa;'>{rest}</span></div>", unsafe_allow_html=True)
                elif line.startswith("- ") or line.startswith("• "):
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.82rem;color:#8895aa;padding-left:1rem;margin:0.2rem 0;'>→ {line[2:]}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.82rem;color:#8895aa;margin:0.2rem 0;'>{line}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            continue

        # ── Insight block
        if raw.strip().startswith("## INSIGHT") or "INSIGHT" in raw[:30].upper():
            lines = raw.strip().split("\n")
            title_line = lines[0].replace("##", "").strip()

            # Parse priority
            priority = "MEDIUM"
            for p in ["HIGH", "MEDIUM", "LOW"]:
                if p in title_line.upper():
                    priority = p
                    break
            border_color, bg_color = PRIORITY_COLORS.get(priority, PRIORITY_COLORS["MEDIUM"])

            # Clean title
            title = title_line.split("|")[0].replace("INSIGHT", "").strip()
            title = title.lstrip("0123456789 —-").strip()

            st.markdown(f"""
            <div style="background:{bg_color};border:1px solid {border_color}44;
                        border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:0.75rem;
                        border-left:3px solid {border_color};">
                <div style="display:flex;justify-content:space-between;align-items:center;
                            margin-bottom:0.7rem;">
                    <div style="font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:600;
                                color:#e8edf5;">{title}</div>
                    <span style="background:{border_color}22;border:1px solid {border_color}55;
                                 border-radius:4px;padding:2px 8px;font-family:'JetBrains Mono',
                                 monospace;font-size:0.6rem;color:{border_color};
                                 letter-spacing:1px;">{priority}</span>
                </div>
            """, unsafe_allow_html=True)

            current_label = None
            label_colors = {
                "Insight":  "#38bdf8",
                "Reason":   "#a78bfa",
                "Action":   "#3ecf8e",
                "Impact":   "#f0a429",
            }

            for line in lines[1:]:
                line = line.strip()
                if not line or line == "---":
                    continue

                matched = False
                for label, lcolor in label_colors.items():
                    if line.lower().startswith(f"**{label.lower()}"):
                        rest = line.split("**", 2)[-1].lstrip(":").strip()
                        st.markdown(f"""
                        <div style="margin:0.45rem 0;">
                            <span style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
                                         color:{lcolor};letter-spacing:1.5px;text-transform:uppercase;
                                         font-weight:600;">{label}</span>
                            <div style="font-family:'Inter',sans-serif;font-size:0.83rem;
                                        color:#c8d3e0;margin-top:2px;line-height:1.6;">{rest}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        current_label = label
                        matched = True
                        break

                if not matched and line:
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.82rem;color:#8895aa;margin:0.15rem 0;padding-left:0.5rem;'>{line}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
            continue

        # ── Fallback — plain text sections
        if raw.strip():
            for line in raw.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("##") or line.startswith("#"):
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.9rem;font-weight:600;color:#e8edf5;margin:1rem 0 0.3rem;'>{line.lstrip('#').strip()}</div>", unsafe_allow_html=True)
                elif line.startswith("**"):
                    clean = line.replace("**", "")
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.83rem;font-weight:600;color:#e8edf5;margin:0.3rem 0;'>{clean}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.82rem;color:#8895aa;line-height:1.6;margin:0.1rem 0;'>{line}</div>", unsafe_allow_html=True)


def render_ai_insights():
    st.markdown("""
    <div style="margin-bottom:1.4rem;">
        <div style="font-family:'Inter',sans-serif;font-size:0.95rem;font-weight:600;color:#e8edf5;">
            AI Analyst
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#4a566a;
                    letter-spacing:1.5px;text-transform:uppercase;margin-top:2px;">
            DECISION-DRIVEN INSIGHTS — NOT JUST DATA DISPLAY
        </div>
    </div>
    """, unsafe_allow_html=True)

    state   = get_state()
    df      = state.get("df")
    api_key = state.get("api_key", "")

    # ── No API key
    if not api_key:
        st.markdown("""
        <div style="background:#161c2a;border:1px solid #818cf844;border-radius:12px;
                    padding:1.2rem 1.4rem;border-left:3px solid #818cf8;">
            <div style="font-family:'Inter',sans-serif;font-size:0.88rem;font-weight:600;
                        color:#e8edf5;margin-bottom:4px;">API Key Required</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.82rem;color:#8895aa;">
                Add your Anthropic API key in the sidebar to unlock the AI analyst.
                Your key stays in your session only.
            </div>
        </div>
        """, unsafe_allow_html=True)
        key_in = st.text_input("Anthropic API Key", type="password",
                               placeholder="sk-ant-...", key="ai_key_inline",
                               label_visibility="collapsed")
        if key_in:
            state["api_key"] = key_in
            st.rerun()
        return

    # ── No data
    if df is None:
        st.markdown("""
        <div style="background:#161c2a;border:1px solid #1e2840;border-radius:12px;
                    padding:1.2rem 1.4rem;">
            <div style="font-family:'Inter',sans-serif;font-size:0.88rem;font-weight:600;
                        color:#e8edf5;margin-bottom:4px;">No Data Loaded</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.82rem;color:#8895aa;">
                Upload a file or connect to a database first.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Status bar
    source = state.get("source", "Unknown")
    st.markdown(f"""
    <div style="background:#161c2a;border:1px solid #3ecf8e44;border-radius:10px;
                padding:0.8rem 1.1rem;margin-bottom:1.2rem;display:flex;
                justify-content:space-between;align-items:center;">
        <div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                         color:#3ecf8e;">READY</span>
            <span style="font-family:'Inter',sans-serif;font-size:0.82rem;color:#8895aa;
                         margin-left:0.7rem;">{source} — {len(df):,} rows × {len(df.columns)} cols</span>
        </div>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a566a;">
            {state.get('ai_calls', 0)} calls this session
        </span>
    </div>
    """, unsafe_allow_html=True)

    context = build_context(df)

    # ── Mode selector
    col1, col2 = st.columns([3, 1])
    with col1:
        mode = st.selectbox(
            "Analysis type",
            list(PROMPT_TEMPLATES.keys()),
            key="ai_mode",
            label_visibility="collapsed"
        )
    with col2:
        run = st.button("Run Analysis", key="gen_insights", use_container_width=True)

    # ── Custom question
    custom_q = ""
    if mode == "Ask the Analyst":
        custom_q = st.text_area(
            "Ask anything about your data",
            placeholder="e.g. Why are sales dropping in Q3? Which customer segment is most valuable?",
            height=90,
            key="custom_q",
            label_visibility="collapsed"
        )

    # ── Run
    if run:
        if mode == "Ask the Analyst" and not custom_q.strip():
            st.warning("Enter your question first.")
            return

        with st.spinner("Analyzing..."):
            try:
                if mode == "Ask the Analyst":
                    prompt = f"""The user is asking about their data. Answer as a decision-driven analyst.
Always follow the strict insight format (Insight / Reason / Action / Impact).

Dataset: {context['data_info']}
Statistics: {context['stats']}
Sample: {context['sample']}

User question: {custom_q}"""
                else:
                    prompt = PROMPT_TEMPLATES[mode].format(**context)

                result = call_claude(api_key, prompt)
                state["ai_calls"] = state.get("ai_calls", 0) + 1
                st.session_state["last_insight"]      = result
                st.session_state["last_insight_mode"] = mode

            except Exception as e:
                err = str(e)
                if "401" in err:
                    st.error("Invalid API key — check your Anthropic key.")
                elif "429" in err:
                    st.error("Rate limit hit — wait a moment and try again.")
                else:
                    st.error(f"API error: {e}")
                return

    # ── Render last result
    last = st.session_state.get("last_insight")
    if last:
        st.markdown('<hr style="border:none;border-top:1px solid #1e2840;margin:1.2rem 0;">', unsafe_allow_html=True)

        last_mode = st.session_state.get("last_insight_mode", mode)
        st.markdown(f"""
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4a566a;
                    letter-spacing:2px;text-transform:uppercase;margin-bottom:1rem;">
            {last_mode} — Results
        </div>
        """, unsafe_allow_html=True)

        render_insight_output(last)

        # ── Export
        st.markdown('<hr style="border:none;border-top:1px solid #1e2840;margin:1.2rem 0;">', unsafe_allow_html=True)
        ex1, ex2 = st.columns(2)
        with ex1:
            if st.button("Generate PDF Report", key="gen_pdf", use_container_width=True):
                with st.spinner("Building PDF..."):
                    try:
                        pdf_bytes = generate_insight_pdf(df, last, last_mode, state)
                        st.download_button(
                            "Download PDF",
                            data=pdf_bytes,
                            file_name="datavyn_analyst_report.pdf",
                            mime="application/pdf",
                            key="dl_pdf"
                        )
                    except Exception as e:
                        st.error(f"PDF error: {e}")
        with ex2:
            st.download_button(
                "Download as Text",
                data=last.encode("utf-8"),
                file_name="datavyn_insights.txt",
                mime="text/plain",
                key="dl_txt",
                use_container_width=True
            )


def generate_insight_pdf(df: pd.DataFrame, insight_text: str, mode: str, state: dict) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch,
                            leftMargin=0.8*inch, rightMargin=0.8*inch)
    styles = getSampleStyleSheet()

    BLUE   = colors.HexColor("#4f8ef7")
    DARK   = colors.HexColor("#0d1117")
    GREY   = colors.HexColor("#8895aa")
    LIGHT  = colors.HexColor("#f8fafc")
    BORDER = colors.HexColor("#e2e8f0")

    T = ParagraphStyle("T", parent=styles["Title"], fontSize=20,
                       textColor=colors.HexColor("#1e293b"), spaceAfter=4)
    S = ParagraphStyle("S", parent=styles["Normal"], fontSize=8,
                       textColor=GREY, spaceAfter=16)
    H = ParagraphStyle("H", parent=styles["Heading2"], fontSize=12,
                       textColor=BLUE, spaceBefore=12, spaceAfter=6)
    B = ParagraphStyle("B", parent=styles["Normal"], fontSize=9,
                       textColor=colors.HexColor("#334155"), leading=14, spaceAfter=5)

    story = [
        Paragraph("DataVyn — Analyst Report", T),
        Paragraph(f"Mode: {mode}  |  Source: {state.get('source','Unknown')}  |  {len(df):,} rows × {len(df.columns)} cols", S),
        HRFlowable(width="100%", thickness=1, color=BLUE),
        Spacer(1, 10),
    ]

    # Stats table
    story.append(Paragraph("Dataset Summary", H))
    tbl_data = [
        ["Metric", "Value"],
        ["Rows",             f"{len(df):,}"],
        ["Columns",          str(len(df.columns))],
        ["Missing Values",   f"{df.isnull().sum().sum():,}"],
        ["Duplicate Rows",   f"{df.duplicated().sum():,}"],
        ["Completeness",     f"{round((1 - df.isnull().sum().sum()/max(df.size,1))*100,1)}%"],
    ]
    tbl = Table(tbl_data, colWidths=[3*inch, 3.4*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,0), BLUE),
        ("TEXTCOLOR",    (0,0), (-1,0), colors.white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT, colors.white]),
        ("GRID",         (0,0), (-1,-1), 0.5, BORDER),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("TOPPADDING",   (0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
    ]))
    story += [tbl, Spacer(1, 14)]

    story.append(Paragraph("AI Analysis", H))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 6))

    for line in insight_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 3))
        elif line.startswith("##") or line.startswith("#"):
            story.append(Paragraph(line.lstrip("#").strip(), H))
        elif line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(f"<b>{line.strip('*')}</b>", B))
        elif line.startswith("**"):
            clean = line.replace("**", "")
            story.append(Paragraph(clean, B))
        elif line.startswith("- ") or line.startswith("• "):
            story.append(Paragraph(f"• {line[2:]}", B))
        else:
            safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            story.append(Paragraph(safe, B))

    story += [
        Spacer(1, 16),
        HRFlowable(width="100%", thickness=0.5, color=BORDER),
        Paragraph("Generated by DataVyn Labs · datavyn.ai", S),
    ]

    doc.build(story)
    return buf.getvalue()