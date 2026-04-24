import streamlit as st
import tempfile
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.agent_controller import run_agent

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    page_icon="🧠"
)

# ---------------- HEADER ----------------
st.markdown(
    "<h1 style='text-align:center;'>🧠 AI Research Assistant Dashboard</h1>",
    unsafe_allow_html=True
)

# ---------------- SESSION ----------------
if "papers" not in st.session_state:
    st.session_state["papers"] = []

# ---------------- JSON PARSER ----------------
def parse_output(output):
    try:
        data = json.loads(output)

        # 🔥 FULL FLATTENING
        if isinstance(data.get("summary"), dict):
            inner = data["summary"]
            return {
                "title": inner.get("title", ""),
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
            "metrics": {}
        }

# ---------------- UPLOAD ----------------
uploaded_files = st.file_uploader(
    "📄 Upload Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:

        if st.button(f"🚀 Process {file.name}"):

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                path = tmp.name

            with st.spinner("Analyzing paper..."):
                output = run_agent(path)

            data = parse_output(output)
            data["name"] = file.name

            st.session_state["papers"].append(data)

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs([
    "📊 Analysis",
    "📄 Raw Output",
    "⚖️ Comparison"
])

# ================= TAB 1 =================
with tab1:

    if st.session_state["papers"]:

        data = st.session_state["papers"][-1]
        metrics = data.get("metrics", {})

        # -------- METRICS --------
        col1, col2, col3 = st.columns(3)

        col1.metric("Gain (dBi)", metrics.get("gain", "N/A"))
        col2.metric("S11 (dB)", metrics.get("s11", "N/A"))
        col3.metric("Bandwidth (%)", metrics.get("bandwidth", "N/A"))

        st.divider()

        # -------- TEXT SECTIONS --------
        colA, colB = st.columns(2)

        with colA:
            st.subheader("🧠 Summary")
            st.write(data.get("summary", ""))

        with colB:
            st.subheader("⚙️ Methodology")
            st.write(data.get("methodology", ""))

        st.subheader("🚀 Contributions")
        for c in data.get("contributions", []):
            st.write(f"• {c}")

        st.subheader("📊 Results")
        st.write(data.get("results", ""))

        # -------- RADAR CHART --------
        if metrics:

            radar_df = pd.DataFrame({
                "Metric": ["Gain", "S11", "Bandwidth"],
                "Value": [
                    metrics.get("gain", 0),
                    abs(metrics.get("s11", 0)),
                    metrics.get("bandwidth", 0)
                ]
            })

            fig = px.line_polar(
                radar_df,
                r="Value",
                theta="Metric",
                line_close=True
            )

            fig.update_traces(fill="toself")

            st.subheader("📡 Performance Radar")
            st.plotly_chart(fig, use_container_width=True)

# ================= TAB 2 =================
with tab2:

    for paper in st.session_state["papers"]:
        st.subheader(paper["name"])
        st.code(json.dumps(paper, indent=2))

# ================= TAB 3 =================
with tab3:

    if len(st.session_state["papers"]) > 1:

        df = pd.DataFrame([
            {
                "Paper": p["name"],
                "Gain": p["metrics"].get("gain"),
                "S11": p["metrics"].get("s11"),
                "Bandwidth": p["metrics"].get("bandwidth")
            }
            for p in st.session_state["papers"]
        ])

        st.subheader("📊 Comparison Table")
        st.dataframe(df)

        # -------- BAR CHART --------
        fig_bar = px.bar(
            df,
            x="Paper",
            y=["Gain", "Bandwidth"],
            barmode="group"
        )

        st.plotly_chart(fig_bar)

        # -------- MULTI RADAR --------
        fig = go.Figure()

        for p in st.session_state["papers"]:
            m = p["metrics"]

            fig.add_trace(go.Scatterpolar(
                r=[
                    m.get("gain", 0),
                    abs(m.get("s11", 0)),
                    m.get("bandwidth", 0)
                ],
                theta=["Gain", "S11", "Bandwidth"],
                fill='toself',
                name=p["name"]
            ))

        fig.update_layout(polar=dict(radialaxis=dict(visible=True)))

        st.subheader("📡 Radar Comparison")
        st.plotly_chart(fig)

    else:
        st.info("Upload at least 2 papers for comparison")
