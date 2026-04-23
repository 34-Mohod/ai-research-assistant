import streamlit as st
import tempfile
import re
import plotly.graph_objects as go
from modules.agent_controller import run_agent

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Research Assistant Pro", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {background-color: #0f172a; color: #e2e8f0;}

.card {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1f2937;
    margin-bottom: 15px;
}

.metric {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("# 🧠 AI Research Assistant Pro")

# ---------------- FILE INPUT ----------------
colA, colB = st.columns(2)

file1 = colA.file_uploader("Upload Paper 1", type=["pdf"])
file2 = colB.file_uploader("Upload Paper 2 (optional)", type=["pdf"])

# ---------------- PARSER ----------------
def extract(pattern, text):
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""

def find_val(key, text):
    m = re.search(key + r".*?([-+]?\d+\.?\d*)", text, re.IGNORECASE)
    return float(m.group(1)) if m else 0

def parse(text):
    return {
        "title": extract(r"Title:\s*(.+)", text),
        "summary": extract(r"Summary:\s*(.*?)\n\n", text),
        "contrib": extract(r"Key Contributions:\s*(.*?)\n\n", text),
        "method": extract(r"Methodology:\s*(.*?)\n\n", text),
        "results": extract(r"Results:\s*(.*?)\n\n", text),
        "gain": find_val("Gain", text),
        "s11": find_val("S11", text),
        "bw": find_val("Bandwidth", text)
    }

# ---------------- RUN ----------------
def process(file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file.read())
        return parse(run_agent(tmp.name))

if st.button("🚀 Analyze"):
    if file1:
        st.session_state["p1"] = process(file1)
    if file2:
        st.session_state["p2"] = process(file2)

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Comparison", "🧠 Insights"])

# =========================================================
# ================= TAB 1 DASHBOARD ========================
# =========================================================
with tab1:
    if "p1" in st.session_state:

        d = st.session_state["p1"]

        st.markdown(f"## 📄 {d['title'] or 'Research Paper'}")

        # -------- METRICS --------
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'><div>Gain</div><div class='metric'>{d['gain']} dBi</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><div>S11</div><div class='metric'>{d['s11']} dB</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><div>Bandwidth</div><div class='metric'>{d['bw']}%</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        left, right = st.columns([1.2, 1])

        with left:
            st.markdown("### 🧠 Summary")
            st.markdown(f"<div class='card'>{d['summary']}</div>", unsafe_allow_html=True)

            st.markdown("### 🚀 Contributions")
            for c in d["contrib"].split("•"):
                if c.strip():
                    st.write("✔", c.strip())

        with right:
            st.markdown("### ⚙️ Methodology")
            st.markdown(f"<div class='card'>{d['method']}</div>", unsafe_allow_html=True)

            st.markdown("### 📊 Results")
            for r in d["results"].split(","):
                if r.strip():
                    st.write("•", r.strip())

        st.markdown("---")

        # -------- RADAR CHART --------
        st.markdown("### 📡 Performance Radar")

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=[d["gain"], abs(d["s11"]), d["bw"]],
            theta=["Gain", "S11", "Bandwidth"],
            fill='toself'
        ))

        fig.update_layout(
            polar=dict(bgcolor="#0f172a"),
            paper_bgcolor="#0f172a",
            font=dict(color="white")
        )

        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# ================= TAB 2 COMPARISON =======================
# =========================================================
with tab2:
    if "p1" in st.session_state and "p2" in st.session_state:

        p1 = st.session_state["p1"]
        p2 = st.session_state["p2"]

        st.markdown("## 📊 Comparison")

        df = {
            "Metric": ["Gain", "S11", "Bandwidth"],
            "Paper 1": [p1["gain"], p1["s11"], p1["bw"]],
            "Paper 2": [p2["gain"], p2["s11"], p2["bw"]],
        }

        st.dataframe(df)

        fig = go.Figure()

        fig.add_trace(go.Bar(name="Paper 1", x=df["Metric"], y=df["Paper 1"]))
        fig.add_trace(go.Bar(name="Paper 2", x=df["Metric"], y=df["Paper 2"]))

        fig.update_layout(barmode='group', paper_bgcolor="#0f172a", font=dict(color="white"))

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Upload 2 papers for comparison")

# =========================================================
# ================= TAB 3 INSIGHTS =========================
# =========================================================
with tab3:
    if "p1" in st.session_state:

        d = st.session_state["p1"]

        st.markdown("## 🧠 AI Insights")

        score = 0

        if d["gain"] > 8:
            st.success("✔ Strong Gain")
            score += 30

        if d["s11"] < -10:
            st.success("✔ Good Impedance Matching")
            score += 30

        if d["bw"] > 20:
            st.success("✔ Wide Bandwidth")
            score += 40

        st.markdown("---")

        st.subheader("🏆 Final Score")
        st.progress(score / 100)
        st.success(f"{score}/100")

    else:
        st.warning("Run analysis first")
