import streamlit as st
import pandas as pd
import numpy as np
import json
from modules.state import get_state


INSIGHT_PROMPTS = {
    "🔍 Executive Summary": """You are a senior data analyst. Analyze this dataset and provide a concise executive summary in 4-5 bullet points covering: what the data represents, key patterns, standout statistics, and one actionable recommendation. Use plain language. Data info:
{data_info}
Statistics:
{stats}
""",
    "📊 Statistical Deep Dive": """As a statistician, analyze this dataset. Cover: distribution shapes, outliers, skewness, notable correlations (if present), and data quality observations. Format as clear paragraphs.
Data info:
{data_info}
Statistics:
{stats}
Sample rows:
{sample}
""",
    "⚠️ Anomaly Detection": """Analyze this dataset for anomalies, outliers, and suspicious patterns. List specific column names and values. Suggest possible explanations.
Statistics:
{stats}
Sample:
{sample}
""",
    "💡 Business Insights": """Act as a business intelligence consultant. Extract 5 actionable business insights from this data. For each insight: state the finding, its business implication, and a recommended action. Be specific.
Data info:
{data_info}
Statistics:
{stats}
""",
    "🧹 Data Quality Report": """Perform a data quality assessment. Cover: completeness, consistency, data type issues, cardinality concerns, potential encoding problems, and recommendations for cleaning. Be specific about column names.
Data info:
{data_info}
Column details:
{column_details}
""",
    "❓ Ask a Custom Question": None,
}


def build_context(df: pd.DataFrame) -> dict:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    data_info = (
        f"Rows: {len(df)}, Columns: {len(df.columns)}\n"
        f"Numeric cols: {', '.join(num_cols)}\n"
        f"Categorical cols: {', '.join(cat_cols)}\n"
        f"Missing values: {df.isnull().sum().sum()}\n"
        f"Duplicates: {df.duplicated().sum()}\n"
    )

    stats = ""
    if num_cols:
        desc = df[num_cols].describe().round(3)
        stats = desc.to_string()

    column_details = ""
    for col in df.columns:
        vc = df[col].value_counts().head(5)
        column_details += f"\n{col} ({df[col].dtype}): missing={df[col].isnull().sum()}, unique={df[col].nunique()}, top={vc.index.tolist()[:3]}"

    sample = df.head(5).to_string()

    return {
        "data_info": data_info,
        "stats": stats,
        "column_details": column_details,
        "sample": sample,
    }


def call_claude(api_key: str, prompt: str) -> str:
    import requests
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def render_ai_insights():
    st.markdown("""
    <div class="dv-section-title">🤖 AI Insights</div>
    <div class="dv-section-sub">POWERED BY CLAUDE — BRING YOUR OWN API KEY</div>
    """, unsafe_allow_html=True)

    state = get_state()
    df = state.get("df")
    api_key = state.get("api_key", "")

    # Key check
    if not api_key:
        st.markdown("""
        <div class="dv-card dv-card-violet">
            <h3>🔑 API Key Required</h3>
            <p>Add your <strong>Anthropic API key</strong> in the sidebar to unlock AI-powered insights. Your key is stored only in your session and never sent to any server except Anthropic's API.</p>
        </div>
        """, unsafe_allow_html=True)
        api_key_inline = st.text_input("Or enter your Anthropic API key here:", type="password", key="ai_key_inline")
        if api_key_inline:
            state["api_key"] = api_key_inline
            api_key = api_key_inline
            st.rerun()
        return

    # Data check
    if df is None:
        st.markdown("""
        <div class="dv-card">
            <h3>📁 No Data Loaded</h3>
            <p>Upload a file, connect to Kaggle, or connect to a database first to generate AI insights.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="dv-card dv-card-green">
        <h3>✅ Ready for Analysis</h3>
        <p>Data: <strong>{state.get('source', 'Unknown')}</strong> — {len(df):,} rows × {len(df.columns)} columns<br>
        API: <strong>Connected</strong> (key ending in ...{api_key[-6:]})</p>
    </div>
    """, unsafe_allow_html=True)

    context = build_context(df)

    # ── Insight type selector
    st.markdown('<div class="dv-section-title" style="font-size:1rem;">Select Analysis Type</div>', unsafe_allow_html=True)
    insight_type = st.selectbox("Analysis Mode", list(INSIGHT_PROMPTS.keys()), key="ai_mode")

    custom_q = ""
    if insight_type == "❓ Ask a Custom Question":
        custom_q = st.text_area(
            "Your question about the data",
            placeholder="e.g. What are the main drivers of sales? Are there seasonal patterns?",
            height=100,
            key="custom_q"
        )

    # Cache key
    cache_key = f"{insight_type}_{hash(df.to_string()[:200])}"

    if st.button("⚡ Generate Insights", key="gen_insights"):
        if insight_type == "❓ Ask a Custom Question" and not custom_q.strip():
            st.warning("Please enter your question.")
            return

        with st.spinner("🤖 Claude is analyzing your data..."):
            try:
                if insight_type == "❓ Ask a Custom Question":
                    prompt = f"""You are a data analyst. The user has loaded a dataset with these properties:
{context['data_info']}

Statistics:
{context['stats']}

Sample rows:
{context['sample']}

User's question: {custom_q}

Provide a thorough, specific answer based on the data provided."""
                else:
                    template = INSIGHT_PROMPTS[insight_type]
                    prompt = template.format(**context)

                result = call_claude(api_key, prompt)
                state["ai_calls"] = state.get("ai_calls", 0) + 1
                state["insights_cache"][cache_key] = result
                st.session_state["last_insight"] = result
                st.session_state["last_insight_type"] = insight_type

            except Exception as e:
                err_str = str(e)
                if "401" in err_str or "authentication" in err_str.lower():
                    st.error("❌ Invalid API key. Please check your Anthropic API key.")
                elif "429" in err_str:
                    st.error("❌ Rate limit reached. Please wait a moment and try again.")
                else:
                    st.error(f"❌ API error: {e}")
                return

    # Display result
    last_insight = st.session_state.get("last_insight")
    if last_insight:
        st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="dv-section-title" style="font-size:1rem;">
            {st.session_state.get('last_insight_type', 'Analysis')} Results
        </div>
        """, unsafe_allow_html=True)

        # Format the insight nicely
        lines = last_insight.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("•") or line.startswith("-") or line.startswith("*"):
                st.markdown(f'<div class="insight-block">{line}</div>', unsafe_allow_html=True)
            elif line.startswith("#") or (len(line) < 80 and line.endswith(":")):
                st.markdown(f'<div class="dv-section-title" style="font-size:0.9rem;margin:0.8rem 0 0.3rem;">{line.lstrip("#").strip()}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color:#94a3b8;font-size:0.88rem;line-height:1.7;margin-bottom:0.4rem;">{line}</p>', unsafe_allow_html=True)

        # Export insight to PDF
        st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)
        st.markdown('<div class="dv-section-title" style="font-size:1rem;">📥 Export Insight Report</div>', unsafe_allow_html=True)

        if st.button("📄 Generate PDF Report", key="gen_pdf"):
            with st.spinner("Generating PDF..."):
                try:
                    pdf_bytes = generate_insight_pdf(df, last_insight, state)
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"datavyn_insight_report.pdf",
                        mime="application/pdf",
                        key="dl_insight_pdf"
                    )
                    st.success("✅ PDF ready for download!")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

    # Batch insights
    st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)
    with st.expander("🚀 Run All Analyses at Once", expanded=False):
        st.markdown('<p style="color:#94a3b8;font-size:0.82rem;">Run all 5 analysis types and compile a comprehensive report. Uses ~5 API calls.</p>', unsafe_allow_html=True)
        if st.button("⚡ Run Full Analysis Suite", key="full_suite"):
            all_results = {}
            prog = st.progress(0)
            status = st.empty()
            modes = [k for k in INSIGHT_PROMPTS.keys() if k != "❓ Ask a Custom Question"]
            for i, mode in enumerate(modes):
                status.markdown(f'<p style="color:#00f5ff;font-size:0.82rem;">Running: {mode}...</p>', unsafe_allow_html=True)
                try:
                    template = INSIGHT_PROMPTS[mode]
                    prompt = template.format(**context)
                    result = call_claude(api_key, prompt)
                    all_results[mode] = result
                    state["ai_calls"] = state.get("ai_calls", 0) + 1
                except Exception as e:
                    all_results[mode] = f"Error: {e}"
                prog.progress((i + 1) / len(modes))

            st.session_state["full_suite_results"] = all_results
            status.markdown('<p style="color:#10b981;font-size:0.82rem;">✅ All analyses complete!</p>', unsafe_allow_html=True)

            if st.button("📄 Export Full Suite PDF", key="export_suite"):
                pdf_bytes = generate_full_suite_pdf(df, all_results, state)
                st.download_button("⬇️ Download Full Report", data=pdf_bytes, file_name="datavyn_full_report.pdf", mime="application/pdf")


def generate_insight_pdf(df: pd.DataFrame, insight_text: str, state: dict) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    import io as _io

    buf = _io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("DVTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=20, textColor=colors.HexColor("#1e293b"),
        spaceAfter=4)
    sub_style = ParagraphStyle("DVSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#64748b"),
        spaceAfter=16)
    heading_style = ParagraphStyle("DVHeading", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#7c3aed"),
        spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("DVBody", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#334155"),
        leading=15, spaceAfter=8)

    story = []
    story.append(Paragraph("DataVyn Labs — Insight Report", title_style))
    story.append(Paragraph(f"Source: {state.get('source', 'Unknown')}  |  Rows: {len(df):,}  |  Columns: {len(df.columns)}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 12))

    # Dataset stats table
    story.append(Paragraph("Dataset Summary", heading_style))
    import numpy as np
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    table_data = [["Metric", "Value"]]
    table_data.append(["Total Rows", f"{len(df):,}"])
    table_data.append(["Total Columns", str(len(df.columns))])
    table_data.append(["Numeric Columns", str(len(num_cols))])
    table_data.append(["Missing Values", f"{df.isnull().sum().sum():,}"])
    table_data.append(["Duplicate Rows", f"{df.duplicated().sum():,}"])

    tbl = Table(table_data, colWidths=[3*inch, 3*inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#7c3aed")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 16))

    # Insight text
    story.append(Paragraph("AI Analysis", heading_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 6))

    for line in insight_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue
        if line.startswith("#"):
            story.append(Paragraph(line.lstrip("#").strip(), heading_style))
        else:
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_line, body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Paragraph("Generated by DataVyn Labs • datavyn.ai", sub_style))

    doc.build(story)
    return buf.getvalue()


def generate_full_suite_pdf(df: pd.DataFrame, results: dict, state: dict) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    import io as _io

    buf = _io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("T", parent=styles["Title"], fontSize=22,
        textColor=colors.HexColor("#1e293b"), spaceAfter=6)
    sub_style = ParagraphStyle("S", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#64748b"), spaceAfter=20)
    h2_style = ParagraphStyle("H2", parent=styles["Heading1"], fontSize=14,
        textColor=colors.HexColor("#7c3aed"), spaceBefore=14, spaceAfter=8)
    body_style = ParagraphStyle("B", parent=styles["Normal"], fontSize=10,
        textColor=colors.HexColor("#334155"), leading=15, spaceAfter=6)

    story = [
        Paragraph("DataVyn Labs — Full Analysis Report", title_style),
        Paragraph(f"Source: {state.get('source', 'Unknown')}  |  Rows: {len(df):,}  |  Columns: {len(df.columns)}", sub_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#7c3aed")),
        Spacer(1, 12),
    ]

    for mode, text in results.items():
        story.append(PageBreak())
        story.append(Paragraph(mode, h2_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 8))
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 4))
                continue
            if line.startswith("#"):
                story.append(Paragraph(line.lstrip("#").strip(), h2_style))
            else:
                safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                story.append(Paragraph(safe, body_style))

    doc.build(story)
    return buf.getvalue()
