import streamlit as st
import tempfile
import json
import plotly.express as px
import pandas as pd

from modules.agent_controller import run_agent

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Research Assistant", layout="wide", page_icon="🧠")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {background-color:#0b1220; color:#e5e7eb;}
.metric-card {
    background:#0f1b2e;
    padding:20px;
    border-radius:14px;
    border:1px solid #1f2a44;
    text-align:center;
}
.section {
    background:#0f1b2e;
    padding:18px;
    border-radius:12px;
    border:1px solid #1f2a44;
}
.title {
    font-size:38px;
    font-weight:800;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 AI Research Assistant</div>', unsafe_allow_html=True)

# ---------------- STATE ----------------
if "papers" not in st.session_state:
    st.session_state["papers"] = []

if "current_data" not in st.session_state:
    st.session_state["current_data"] = None


# ---------------- PARSER (MOST IMPORTANT FIX) ----------------
def parse_output(output):
    try:
        data = json.loads(output)

        # 🔥 HANDLE NESTED STRUCTURE
        if isinstance(data.get("summary"), dict):
            inner = data["summary"]

            return {
                "title": inner.get("title", "Unknown"),
                "summary": inner.get("summary", ""),
                "methodology": inner.get("methodology", ""),
                "contributions": inner.get("contributions", []),
                "results": inner.get("results", ""),
                "metrics": inner.get("metrics", {})
            }

        return data

    except:
        return {
            "title": "Error",
            "summary": str(output),
            "methodology": "",
            "contributions": [],
            "results": "",
            "metrics": {}
        }


def safe(v, unit=""):
    return f"{v}{unit}" if v not in [None, ""] else "N/A"


# ---------------- RADAR (FIXED NORMALIZATION) ----------------
def radar_chart(metrics):

    gain = metrics.get("gain") or 0
    s11 = abs(metrics.get("s11") or 0)
    bw = metrics.get("bandwidth") or 0

    # normalize (VERY IMPORTANT)
    values = [
        gain / 20 if gain else 0,
        s11 / 100 if s11 else 0,
        bw / 100 if bw else 0
    ]

    df = pd.DataFrame(dict(
        r=values,
        theta=["Gain", "S11", "Bandwidth"]
    ))

    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')

    st.plotly_chart(fig, use_container_width=True)


# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "📄 Upload Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- PROCESS ----------------
if uploaded_files:
    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            path = tmp.name

        if st.button(f"🚀 Process {file.name}"):

            with st.spinner("Processing..."):
                output = run_agent(path)

            data = parse_output(output)

            st.session_state["current_data"] = data
            st.session_state["papers"].append(data)


# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📄 Raw Output", "⚖️ Comparison"])


# =========================================================
# 📊 ANALYSIS TAB
# =========================================================
with tab1:
    data = st.session_state.get("current_data")

    if data:
        metrics = data.get("metrics") or {}

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="metric-card">
        Gain<br><h2>{safe(metrics.get("gain"), " dBi")}</h2>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="metric-card">
        S11<br><h2>{safe(metrics.get("s11"), " dB")}</h2>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="metric-card">
        Bandwidth<br><h2>{safe(metrics.get("bandwidth"), " %")}</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        colA, colB = st.columns(2)

        with colA:
            st.markdown("### 🧠 Summary")
            st.markdown(f"<div class='section'>{data.get('summary','')}</div>", unsafe_allow_html=True)

        with colB:
            st.markdown("### ⚙️ Methodology")
            st.markdown(f"<div class='section'>{data.get('methodology','')}</div>", unsafe_allow_html=True)

        st.markdown("### 🚀 Contributions")
        for c in data.get("contributions", []):
            st.write(f"• {c}")

        st.markdown("### 📊 Results")
        st.write(data.get("results", ""))

        st.markdown("### 📈 Performance Radar")
        radar_chart(metrics)

    else:
        st.info("Upload and process a paper")


# =========================================================
# 📄 RAW OUTPUT
# =========================================================
with tab2:
    data = st.session_state.get("current_data")

    if data:
        st.code(json.dumps(data, indent=2))
    else:
        st.info("No data")


# =========================================================
# ⚖️ COMPARISON TAB
# =========================================================
with tab3:
    papers = st.session_state.get("papers", [])

    if len(papers) >= 2:

        rows = []

        for i, p in enumerate(papers):
            metrics = p.get("metrics") or {}

            rows.append({
                "Paper": p.get("title", f"Paper {i}"),
                "Gain": float(metrics.get("gain") or 0),
                "S11": float(metrics.get("s11") or 0),
                "Bandwidth": float(metrics.get("bandwidth") or 0)
            })

        df = pd.DataFrame(rows)

        st.dataframe(df)

        st.markdown("### 📊 Multi-Paper Radar")

        fig = px.line_polar(
            df.melt(id_vars=["Paper"]),
            r="value",
            theta="variable",
            color="Paper",
            line_close=True
        )

        fig.update_traces(fill='toself')
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Upload at least 2 papers")
