 
<img width="1282" height="681" alt="final datavynlabs" src="https://github.com/user-attachments/assets/ea49cedc-7049-47e0-9f09-0d09da5850ff" />

A production-grade Streamlit data intelligence platform.

**[![Open App](https://img.shields.io/badge/Open%20DataVyn%20App-Live-success?style=for-the-badge)](https://datavyn.streamlit.app)**
---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## 🗂️ Project Structure

```
datavyn/
├── app.py                    # Entry point
├── style.css                 # Custom dark neon theme
├── requirements.txt
└── modules/
    ├── state.py              # Session state management
    ├── sidebar.py            # Sidebar with stats & settings
    ├── overview.py           # Landing / overview page
    ├── upload.py             # File upload (CSV/JSON/Excel/Parquet)
    ├── kaggle_connect.py     # Kaggle API integration
    ├── db_connect.py         # SQLite / PostgreSQL / MySQL
    ├── ai_insights.py        # Anthropic Claude AI analysis
    ├── charts.py             # Plotly chart engine
    └── export.py             # PDF / CSV / Excel / JSON export
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **Multi-format Upload** | CSV, TSV, JSON, Excel, Parquet |
| **Auto Charts** | Histograms, scatter, heatmaps, box plots, time series |
| **Kaggle Connect** | Search & download datasets via Kaggle API |
| **Database Connect** | SQLite, PostgreSQL, MySQL + Chinook demo DB |
| **AI Insights** | 5 analysis modes powered by Claude (Anthropic API) |
| **Data Cleaning** | Drop duplicates, fill NaN, various strategies |
| **PDF Export** | Styled reports with stats tables + AI insights |
| **CSV/JSON/Excel Export** | One-click downloads in all formats |

---

## 🔑 API Keys Needed

| Service | Where to get |
|---|---|
| **Anthropic (Claude)** | console.anthropic.com → API Keys |
| **Kaggle** | kaggle.com → Account → API → Create New Token |

Enter keys via the sidebar (Anthropic) or the Kaggle Connect tab.

---

## 📦 Dependencies

- **streamlit** — UI framework
- **pandas / numpy** — data processing
- **plotly** — interactive charts
- **reportlab** — PDF generation
- **kaggle** — Kaggle API client
- **sqlalchemy** — database connectivity
- **openpyxl / pyarrow** — Excel / Parquet support

---

## 🎨 Theme

DataVyn uses a custom dark neon-industrial theme with:
- Color palette: Deep navy + cyan + violet accents
- Fonts: Syne (headings), JetBrains Mono (data/code), Space Mono (labels)
- 4 switchable chart themes: Neon Dark, Minimal Dark, Vibrant, Monochrome

---

*DataVyn Labs v1.0.0*

---

## Star History ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=DataVyn-labs/DataVyn&type=date&legend=top-left)](https://www.star-history.com/#DataVyn-labs/DataVyn&type=date&legend=top-left)


