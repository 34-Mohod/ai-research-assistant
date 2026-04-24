import streamlit as st
import tempfile
import json
import time
import re
from modules.agent_controller import run_agent

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    page_icon="🧠"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0b1220;
    color: #e5e7eb;
}

.metric-card {
    background: #0f1b2e;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2a44;
    text-align: center;
}

.section {
    background: #0f1b2e;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #1f2a44;
    margin-bottom: 15px;
}

.title {
    font-size: 38px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">🧠 AI Research Assistant</div>', unsafe_allow_html=True)

# ---------------- STATE ----------------
if "papers" not in st.session_state:
    st.session_state["papers"] = []

if "current_data" not in st.session_state:
    st.session_state["current_data"] = None

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "📄 Upload Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- SAFE PARSE ----------------
def safe_json(output):
    try:
        return json.loads(output)
    except:
        return {
            "title": "Parsing Failed",
            "summary": output,
            "contributions": [],
            "methodology": "",
            "results": "",
            "metrics": {}
        }

# ---------------- METRIC EXTRACT (BACKUP) ----------------
    def extract_metrics(data):
    try:
        metrics = data.get("metrics", {})

        return {
            "gain": metrics.get("gain"),
            "s11": metrics.get("s11"),
            "bandwidth": metrics.get("bandwidth")
        }

    except Exception:
        return {
            "gain": None,
            "s11": None,
            "bandwidth": None
        } 

# ---------------- PROCESS ----------------
if uploaded_files:
    for file in uploaded_files:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            path = tmp.name

        if st.button(f"🚀 Process {file.name}"):

            with st.spinner("Processing..."):
                output = run_agent(path)

            data = safe_json(output)

            # fallback metrics if missing
            if not data.get("metrics"):
                data["metrics"] = extract_metrics(data)

            st.session_state["current_data"] = data

            st.session_state["papers"].append({
                "name": file.name,
                "data": data
            })

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Analysis",
    "📄 Raw",
    "📈 Insights",
    "⚖️ Comparison"
])

# ================= TAB 1 =================
with tab1:

    data = st.session_state.get("current_data")

    if not data:
        st.info("Upload and process a paper")
    else:

        metrics = data.get("metrics", {})

        def safe(v, unit=""):
            return f"{v} {unit}" if v else "N/A"

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"<div class='metric-card'>Gain<br><h2>{safe(metrics.get('gain'),'dBi')}</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-card'>S11<br><h2>{safe(metrics.get('s11'),'dB')}</h2></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-card'>Bandwidth<br><h2>{safe(metrics.get('bandwidth'),'%')}</h2></div>", unsafe_allow_html=True)

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
            st.write(f"✔ {c}")

        st.markdown("### 📊 Results")
        st.write(data.get("results",""))

# ================= TAB 2 =================
with tab2:
    data = st.session_state.get("current_data")
    if data:
        st.code(json.dumps(data, indent=2))

# ================= TAB 3 =================
with tab3:

    data = st.session_state.get("current_data")

    if data:
        text = str(data)

        if "gain" in text.lower():
            st.success("✔ Gain detected")

        if "bandwidth" in text.lower():
            st.info("✔ Bandwidth analyzed")

        if "s11" in text.lower():
            st.warning("✔ Reflection coefficient present")

# ================= TAB 4 =================
with tab4:

    st.subheader("⚖️ Paper Comparison")

    papers = st.session_state.get("papers", [])

    if len(papers) < 2:
        st.warning("Upload at least 2 papers")
    else:

        names = [p["name"] for p in papers]

        p1_name = st.selectbox("Paper 1", names)
        p2_name = st.selectbox("Paper 2", names)

        p1 = next(p for p in papers if p["name"] == p1_name)
        p2 = next(p for p in papers if p["name"] == p2_name)

        m1 = p1["data"].get("metrics", {})
        m2 = p2["data"].get("metrics", {})

        def safe(v): return v if v else "N/A"

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### 📄 {p1_name}")
            st.metric("Gain", safe(m1.get("gain")))
            st.metric("S11", safe(m1.get("s11")))
            st.metric("Bandwidth", safe(m1.get("bandwidth")))

        with col2:
            st.markdown(f"### 📄 {p2_name}")
            st.metric("Gain", safe(m2.get("gain")))
            st.metric("S11", safe(m2.get("s11")))
            st.metric("Bandwidth", safe(m2.get("bandwidth")))

        st.markdown("### 🏆 Winner")

        def cmp(a, b): return "Paper 1" if a and b and a > b else "Paper 2"
        def cmp_s11(a, b): return "Paper 1" if a and b and a < b else "Paper 2"

        st.write("Gain:", cmp(m1.get("gain"), m2.get("gain")))
        st.write("Bandwidth:", cmp(m1.get("bandwidth"), m2.get("bandwidth")))
        st.write("S11:", cmp_s11(m1.get("s11"), m2.get("s11")))
