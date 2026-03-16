import streamlit as st
import pandas as pd
from modules.state import get_state
from modules.charts import render_auto_charts
from modules.export import render_export_section


DB_PRESETS = {
    "SQLite (local file)": {
        "driver": "sqlite",
        "fields": ["Database File Path"],
        "example": "/path/to/database.db",
    },
    "PostgreSQL": {
        "driver": "postgresql",
        "fields": ["Host", "Port", "Database", "Username", "Password"],
        "defaults": {"Port": "5432"},
        "example": "host=localhost port=5432 dbname=mydb",
    },
    "MySQL / MariaDB": {
        "driver": "mysql",
        "fields": ["Host", "Port", "Database", "Username", "Password"],
        "defaults": {"Port": "3306"},
        "example": "mysql://user:pass@localhost/mydb",
    },
    "Public Sample DB (Chinook)": {
        "driver": "sqlite_sample",
        "fields": [],
        "example": "Built-in demo database",
    },
}


def get_sqlite_sample():
    """Download and return the Chinook demo SQLite DB."""
    import urllib.request
    import tempfile
    import os

    url = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite")
    try:
        urllib.request.urlretrieve(url, tmp.name)
        return tmp.name
    except Exception:
        # Fallback: create a tiny demo DB
        import sqlite3
        conn = sqlite3.connect(tmp.name)
        conn.execute("CREATE TABLE demo (id INTEGER, name TEXT, value REAL)")
        for i in range(50):
            conn.execute("INSERT INTO demo VALUES (?, ?, ?)", (i, f"item_{i}", i * 1.5))
        conn.commit()
        conn.close()
        return tmp.name


def render_db():
    st.markdown("""
    <div class="dv-section-title">Database Connect</div>
    <div class="dv-section-sub">SQLITE · POSTGRESQL · MYSQL · SAMPLE DBs</div>
    """, unsafe_allow_html=True)

    state = get_state()

    db_type = st.selectbox("Select Database Type", list(DB_PRESETS.keys()), key="db_type")
    preset = DB_PRESETS[db_type]

    conn_str = None

    if preset["driver"] == "sqlite_sample":
        st.markdown("""
        <div class="dv-card dv-card-green">
            <h3>🎵 Chinook Sample Database</h3>
            <p>The Chinook database represents a digital media store, including tables for artists, albums, tracks, invoices, and customers. Perfect for exploring DataVyn features.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📥 Load Chinook Demo DB", key="load_chinook"):
            with st.spinner("Downloading Chinook database..."):
                try:
                    db_path = get_sqlite_sample()
                    st.session_state["db_path"] = db_path
                    st.session_state["db_driver"] = "sqlite"
                    st.success("Success: Chinook DB loaded! Select a table below.")
                except Exception as e:
                    st.error(f"Error: {e}")

    elif preset["driver"] == "sqlite":
        db_path = st.text_input("SQLite Database File Path", placeholder="/path/to/database.db", key="sqlite_path")
        if db_path:
            st.session_state["db_path"] = db_path
            st.session_state["db_driver"] = "sqlite"

    else:
        defaults = preset.get("defaults", {})
        fields = preset["fields"]
        cols = st.columns(min(3, len(fields)))
        field_vals = {}
        for i, field in enumerate(fields):
            with cols[i % len(cols)]:
                if field == "Password":
                    field_vals[field] = st.text_input(field, type="password", key=f"db_{field}")
                else:
                    field_vals[field] = st.text_input(field, value=defaults.get(field, ""), key=f"db_{field}")

        if all(field_vals.get(f) for f in fields if f != "Password"):
            host = field_vals.get("Host", "localhost")
            port = field_vals.get("Port", "5432")
            database = field_vals.get("Database", "")
            user = field_vals.get("Username", "")
            password = field_vals.get("Password", "")
            driver = preset["driver"]

            if driver == "postgresql":
                conn_str = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            elif driver == "mysql":
                conn_str = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

            st.session_state["db_conn_str"] = conn_str
            st.session_state["db_driver"] = driver

    # ── Table Browser
    st.markdown('<hr class="dv-divider">', unsafe_allow_html=True)

    db_ready = st.session_state.get("db_path") or st.session_state.get("db_conn_str")

    if db_ready:
        if st.button("List Tables", key="list_tables"):
            with st.spinner("Connecting..."):
                try:
                    tables = get_tables()
                    st.session_state["db_tables"] = tables
                    if tables:
                        st.success(f"Found {len(tables)} tables: {', '.join(tables)}")
                    else:
                        st.warning("No tables found.")
                except Exception as e:
                    st.error(f"Error: Connection failed: {e}")

        tables = st.session_state.get("db_tables", [])
        if tables:
            selected_table = st.selectbox("Select Table", tables, key="db_table_select")

            col1, col2 = st.columns([3, 1])
            with col1:
                custom_query = st.text_area(
                    "Custom SQL Query (optional)",
                    value=f"SELECT * FROM {selected_table} LIMIT 1000",
                    height=80,
                    key="db_query"
                )
            with col2:
                st.write("")
                st.write("")
                limit = st.number_input("Row Limit", value=1000, min_value=10, max_value=50000, key="db_limit")

            if st.button("Run Query", key="run_query"):
                with st.spinner("Executing query..."):
                    try:
                        df = execute_query(custom_query)
                        state["df"] = df
                        state["source"] = selected_table
                        state["filename"] = selected_table
                        st.success(f"Success: {len(df):,} rows × {len(df.columns)} columns returned")
                    except Exception as e:
                        st.error(f"Error: Query failed: {e}")

    df = state.get("df")
    if df is not None and state.get("source", "").startswith("🗄️"):
        theme = state.get("chart_theme", "Neon Dark")
        render_auto_charts(df, theme, key_prefix="db")
        render_export_section(df, state.get("filename", "db_export"))

    if not db_ready:
        st.markdown("""
        <div class="insight-block">
            <strong>Connection Tips:</strong><br>
            • SQLite: provide the full path to your .db / .sqlite file<br>
            • PostgreSQL / MySQL: ensure the server is accessible from this machine<br>
            • Try the <strong>Chinook Sample DB</strong> to explore DataVyn features instantly
        </div>
        """, unsafe_allow_html=True)


def get_tables():
    import sqlite3
    try:
        from sqlalchemy import create_engine, inspect
        driver = st.session_state.get("db_driver")
        if driver == "sqlite":
            engine = create_engine(f"sqlite:///{st.session_state['db_path']}")
        else:
            engine = create_engine(st.session_state["db_conn_str"])
        inspector = inspect(engine)
        return inspector.get_table_names()
    except ImportError:
        # Fallback to sqlite3
        db_path = st.session_state.get("db_path")
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
        return tables


def execute_query(query: str) -> pd.DataFrame:
    import sqlite3
    try:
        from sqlalchemy import create_engine, text
        driver = st.session_state.get("db_driver")
        if driver == "sqlite":
            engine = create_engine(f"sqlite:///{st.session_state['db_path']}")
        else:
            engine = create_engine(st.session_state["db_conn_str"])
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except ImportError:
        db_path = st.session_state.get("db_path")
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df