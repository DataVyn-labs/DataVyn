import streamlit as st
import pandas as pd
import os
import json
import zipfile
import io
from modules.state import get_state
from modules.charts import render_auto_charts
from modules.export import render_export_section


def render_kaggle():
    st.markdown("""
    <div class="dv-section-title">Kaggle Connect</div>
    <div class="dv-section-sub">PULL DATASETS DIRECTLY FROM KAGGLE</div>
    """, unsafe_allow_html=True)

    state = get_state()

    st.markdown("""
    <div class="dv-card dv-card-amber">
        <h3>Authentication Required</h3>
        <p>Enter your Kaggle credentials to connect. Find them at 
        <strong>kaggle.com → Account → API → Create New Token</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        kaggle_user = st.text_input("Kaggle Username", placeholder="your_username", key="kg_user")
    with c2:
        kaggle_key = st.text_input("Kaggle API Key", type="password", placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", key="kg_key")

    if kaggle_user and kaggle_key:
        # Set env vars for kaggle
        os.environ["KAGGLE_USERNAME"] = kaggle_user
        os.environ["KAGGLE_KEY"] = kaggle_key

        st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)

        search_tab, direct_tab = st.tabs(["Search Datasets", "Direct Download"])

        with search_tab:
            st.markdown('<div class="dv-section-sub">SEARCH KAGGLE DATASETS</div>', unsafe_allow_html=True)
            query = st.text_input("Search datasets", placeholder="titanic, iris, housing prices...", key="kg_search")

            if st.button("Search", key="kg_search_btn") and query:
                with st.spinner("Searching Kaggle..."):
                    try:
                        from kaggle.api.kaggle_api_extended import KaggleApi
                        api = KaggleApi()
                        api.authenticate()
                        datasets = api.dataset_list(search=query, page=1, max_size=None)

                        if datasets:
                            results = []
                            for ds in datasets[:10]:
                                results.append({
                                    "Dataset": str(ds.ref),
                                    "Title": str(ds.title),
                                    "Size": str(ds.size),
                                    "Downloads": int(ds.downloadCount) if hasattr(ds, 'downloadCount') else 0,
                                    "Votes": int(ds.voteCount) if hasattr(ds, 'voteCount') else 0,
                                })
                            df_results = pd.DataFrame(results)
                            st.dataframe(df_results, use_container_width=True)
                            st.session_state["kg_results"] = results
                            st.info("💡 Copy the **Dataset** ref and use it in the 'Direct Download' tab")
                        else:
                            st.warning("No datasets found for that query.")
                    except ImportError:
                        st.error("Error: `kaggle` package not installed. Run: `pip install kaggle`")
                    except Exception as e:
                        st.error(f"Error: Kaggle API error: {e}")

        with direct_tab:
            st.markdown('<div class="dv-section-sub">DOWNLOAD BY DATASET REF</div>', unsafe_allow_html=True)
            dataset_ref = st.text_input(
                "Dataset Reference",
                placeholder="owner/dataset-name  e.g. uciml/iris",
                key="kg_ref"
            )

            if st.button("Download & Load", key="kg_download"):
                if not dataset_ref or "/" not in dataset_ref:
                    st.error("Please enter a valid ref like `owner/dataset-name`")
                else:
                    with st.spinner(f"Downloading {dataset_ref}..."):
                        try:
                            from kaggle.api.kaggle_api_extended import KaggleApi
                            import tempfile

                            api = KaggleApi()
                            api.authenticate()

                            with tempfile.TemporaryDirectory() as tmpdir:
                                api.dataset_download_files(dataset_ref, path=tmpdir, unzip=True)

                                # Find CSV files
                                csv_files = []
                                for root, dirs, files in os.walk(tmpdir):
                                    for f in files:
                                        if f.endswith('.csv'):
                                            csv_files.append(os.path.join(root, f))

                                if not csv_files:
                                    st.error("No CSV files found in dataset")
                                else:
                                    if len(csv_files) > 1:
                                        chosen = st.selectbox("Multiple CSV files found — select one:", csv_files, key="kg_csv_choice")
                                    else:
                                        chosen = csv_files[0]

                                    df = pd.read_csv(chosen)
                                    state["df"] = df
                                    state["source"] = dataset_ref
                                    state["filename"] = dataset_ref.replace("/", "_")
                                    st.success(f"Loaded: {os.path.basename(chosen)} — {len(df):,} rows × {len(df.columns)} cols")

                        except ImportError:
                            st.error("Error: `kaggle` package not installed. Run: `pip install kaggle`")
                        except Exception as e:
                            st.error(f"Error: Download failed: {e}")

    df = state.get("df")
    if df is not None and state.get("source", "").startswith("🏆"):
        theme = state.get("chart_theme", "Neon Dark")
        st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)
        render_auto_charts(df, theme, key_prefix="kaggle")
        render_export_section(df, state.get("filename", "kaggle_export"))

    elif not (kaggle_user and kaggle_key):
        st.markdown("""
        <div class="insight-block amber">
            <strong>Getting Kaggle API credentials:</strong><br>
            1. Go to kaggle.com and sign in<br>
            2. Navigate to Account Settings<br>
            3. Scroll to API section → "Create New API Token"<br>
            4. A kaggle.json file will be downloaded with your username and key
        </div>
        """, unsafe_allow_html=True)