import streamlit as st
import tempfile
import time
import re
import matplotlib.pyplot as plt

# 👉 If this fails, comment it temporarily
from modules.agent_controller import run_agent


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    page_icon="🧠"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: #e2e8f0;
}

.title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 25px;
}

.metric-card {
    background: #111827;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    text-align: center;
}

.section-card {
    background: #111827;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    margin-bottom: 15px;
}

.stButton > button {
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    color: white;
    border-radius: 10px;
    height: 45px;
    border: none;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">🧠 AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">RF • Antenna • THz • AI-powered Research Analysis</div>', unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📄 Upload Research Paper", type=["pdf"])

# ---------------- SESSION ----------------
if "output" not in st.session_state:
    st.session_state.output = None


# ---------------- CLEAN FUNCTION ----------------
def clean_line(line):
    return line.replace("*", "").strip()


# ---------------- PARSER ----------------
def parse_output(output):

    sections = {
        "title": [],
        "summary": [],
        "contributions": [],
        "methodology": [],
        "results": []
    }

    current = None

    for raw in output.split("\n"):
        line = clean_line(raw)

        if not line:
            continue

        lower = line.lower()

        if "title" in lower:
            current = "title"
            continue

        elif "summary" in lower:
            current = "summary"
            continue

        elif "key contributions" in lower:
            current = "contributions"
            continue

        elif "methodology" in lower:
            current = "methodology"
            continue

        elif "results" in lower:
            current = "results"
            continue

        if current:
            sections[current].append(line)

    # remove garbage
    for key in sections:
        sections[key] = [l for l in sections[key] if l not in ["", ".", "**"]]

    return sections


# ---------------- METRIC EXTRACTOR ----------------
def extract_metrics(text):
    gain = None
    s11 = None
    bandwidth = None

    gain_match = re.search(r'(\d+\.?\d*)\s*dBi', text)
    s11_match = re.search(r'-\d+\.?\d*\s*dB', text)
    bw_match = re.search(r'(\d+\.?\d*)\s*%', text)

    if gain_match:
        gain = float(gain_match.group(1))

    if s11_match:
        s11 = float(s11_match.group(0).replace(" dB", ""))

    if bw_match:
        bandwidth = float(bw_match.group(1))

    return gain, s11, bandwidth


# ---------------- PROCESS ----------------
if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.success("File uploaded")

    if st.button("🚀 Generate"):

        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        try:
            output = run_agent(pdf_path)
        except:
            output = "ERROR: Agent not working"

        st.session_state.output = output
        progress.empty()


# ---------------- OUTPUT ----------------
if st.session_state.output:

    output = st.session_state.output

    sections = parse_output(output)
    gain, s11, bandwidth = extract_metrics(output)

    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "🧾 Raw", "📈 Insights"])

    # ================= TAB 1 =================
    with tab1:

        # ---- METRICS ----
        col1, col2, col3 = st.columns(3)

        col1.markdown(f'<div class="metric-card"><h3>Gain</h3><h2>{gain if gain else "N/A"} dBi</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card"><h3>S11</h3><h2>{s11 if s11 else "N/A"} dB</h2></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-card"><h3>Bandwidth</h3><h2>{bandwidth if bandwidth else "N/A"} %</h2></div>', unsafe_allow_html=True)

        st.markdown("---")

        # ---- CONTENT ----
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧠 Summary")
            st.markdown('<div class="section-card">' + " ".join(sections["summary"]) + '</div>', unsafe_allow_html=True)

            st.markdown("### 🚀 Contributions")
            st.markdown('<div class="section-card">' + " ".join(sections["contributions"]) + '</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### ⚙️ Methodology")
            st.markdown('<div class="section-card">' + " ".join(sections["methodology"]) + '</div>', unsafe_allow_html=True)

            st.markdown("### 📊 Results")
            st.markdown('<div class="section-card">' + " ".join(sections["results"]) + '</div>', unsafe_allow_html=True)

        st.markdown("---")

        # ---- CHART ----
        if gain and bandwidth:
            st.subheader("📈 Performance Chart")

            fig, ax = plt.subplots()
            ax.bar(["Gain", "Bandwidth"], [gain, bandwidth])
            st.pyplot(fig)

        # ---- SCORE ----
        if gain:
            score = min(100, int(gain * 8))
            st.subheader("🏆 Score")
            st.progress(score / 100)
            st.success(f"{score}/100")

    # ================= TAB 2 =================
    with tab2:
        st.code(output)

    # ================= TAB 3 =================
    with tab3:

        st.subheader("📈 Insights")

        if gain and gain > 10:
            st.success("High gain antenna detected")

        if s11 and s11 < -10:
            st.info("Good impedance matching")

        if bandwidth and bandwidth > 30:
            st.warning("Wide bandwidth design")

        st.write("✔ RF Analysis Complete")
