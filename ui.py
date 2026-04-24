import streamlit as st
import tempfile
import json
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
            "summary": str(output),
            "contributions": [],
            "methodology": "",
            "results": "",
            "metrics": {}
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

            # ✅ FIX: Flatten nested JSON (CRITICAL FIX)
            if isinstance(data.get("summary"), dict):
                inner = data["summary"]

                data["summary"] = inner.get("summary", "")
                data["methodology"] = inner.get("methodology", "")
                data["contributions"] = inner.get("contributions", [])
                data["results"] = inner.get("results", "")
                data["metrics"] = inner.get("metrics", {})

            st.session_state["current_data"] = data

# ---------------- DISPLAY ----------------
data = st.session_state.get("current_data")

if data:

    metrics = data.get("metrics", {})

    def safe(v, unit=""):
        return f"{v}{unit}" if v is not None else "N/A"

    col1, col2, col3 = st.columns(3)

    col1.markdown(
        f"<div class='metric-card'>Gain<br><h2>{safe(metrics.get('gain'), ' dBi')}</h2></div>",
        unsafe_allow_html=True
    )

    col2.markdown(
        f"<div class='metric-card'>S11<br><h2>{safe(metrics.get('s11'), ' dB')}</h2></div>",
        unsafe_allow_html=True
    )

    col3.markdown(
        f"<div class='metric-card'>Bandwidth<br><h2>{safe(metrics.get('bandwidth'), ' %')}</h2></div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    colA, colB = st.columns(2)

    with colA:
        st.markdown("### 🧠 Summary")
        st.markdown(
            f"<div class='section'>{data.get('summary','')}</div>",
            unsafe_allow_html=True
        )

    with colB:
        st.markdown("### ⚙️ Methodology")
        st.markdown(
            f"<div class='section'>{data.get('methodology','')}</div>",
            unsafe_allow_html=True
        )

    st.markdown("### 🚀 Contributions")
    for c in data.get("contributions", []):
        st.write(f"- {c}")

    st.markdown("### 📊 Results")
    st.write(data.get("results", ""))

# ---------------- RAW OUTPUT ----------------
st.markdown("---")
st.markdown("## Raw Output")

if data:
    st.code(json.dumps(data, indent=2))
