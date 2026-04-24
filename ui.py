import streamlit as st
import pandas as pd
import plotly.express as px
import json

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Research Assistant", layout="wide")

# ---------------- CSS (VERY IMPORTANT) ----------------
st.markdown("""
<style>
body {
    background-color: #0b1220;
    color: #e5e7eb;
}

.title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 20px;
}

.card {
    background: #111827;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #1f2937;
    text-align: center;
}

.section {
    background: #111827;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #1f2937;
    margin-top: 10px;
}

.metric {
    font-size: 28px;
    font-weight: bold;
}

.label {
    color: #9ca3af;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="title">🧠 AI Research Assistant</div>', unsafe_allow_html=True)

# ---------------- FALLBACK DATA ----------------
fallback_data = {
    "title": "Sub-THz Microstrip Antenna",
    "summary": "A sub-terahertz conformal antenna for stealth UAVs.",
    "methodology": "Denim substrate + PEC reflector + CST optimization.",
    "contributions": ["High gain", "Low RCS", "Wide bandwidth"],
    "results": "Gain 10.25 dBi, S11 -63 dB, Bandwidth 47%",
    "metrics": {
        "gain": 10.25,
        "s11": -63.024,
        "bandwidth": 47.12
    }
}

# ---------------- STATE ----------------
if "all_data" not in st.session_state:
    st.session_state["all_data"] = []

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader("📂 Upload Research Papers", type=["pdf"], accept_multiple_files=True)

# ---------------- PROCESS ----------------
if uploaded_files:
    for file in uploaded_files:
        if st.button(f"🚀 Process {file.name}"):

            with st.spinner("Processing..."):
                # 👉 TEMP FAKE DATA (STABLE)
                data = fallback_data

                st.session_state["all_data"].append(data)

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📄 Raw Output", "⚖️ Comparison"])

# ================= ANALYSIS =================
with tab1:

    if st.session_state["all_data"]:
        data = st.session_state["all_data"][-1]
        m = data["metrics"]

        # -------- METRICS --------
        c1, c2, c3 = st.columns(3)

        c1.markdown(f"""
        <div class="card">
            <div class="label">Gain (dBi)</div>
            <div class="metric">{m["gain"]}</div>
        </div>
        """, unsafe_allow_html=True)

        c2.markdown(f"""
        <div class="card">
            <div class="label">S11 (dB)</div>
            <div class="metric">{m["s11"]}</div>
        </div>
        """, unsafe_allow_html=True)

        c3.markdown(f"""
        <div class="card">
            <div class="label">Bandwidth (%)</div>
            <div class="metric">{m["bandwidth"]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # -------- SUMMARY + METHOD --------
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧠 Summary")
            st.markdown(f"<div class='section'>{data['summary']}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("### ⚙️ Methodology")
            st.markdown(f"<div class='section'>{data['methodology']}</div>", unsafe_allow_html=True)

        # -------- CONTRIBUTIONS --------
        st.markdown("### 🚀 Contributions")
        for c in data["contributions"]:
            st.write("•", c)

        # -------- RESULTS --------
        st.markdown("### 📊 Results")
        st.markdown(f"<div class='section'>{data['results']}</div>", unsafe_allow_html=True)

        # -------- RADAR --------
        st.markdown("### 📈 Performance Radar")

        values = [
            m["gain"] / 20,
            abs(m["s11"]) / 100,
            m["bandwidth"] / 100
        ]

        df = pd.DataFrame(dict(
            r=values,
            theta=["Gain", "S11", "Bandwidth"]
        ))

        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        st.plotly_chart(fig, use_container_width=True)

# ================= RAW =================
with tab2:
    if st.session_state["all_data"]:
        st.json(st.session_state["all_data"][-1])

# ================= COMPARISON =================
with tab3:

    data_list = st.session_state["all_data"]

    if data_list:

        rows = []

        for i, d in enumerate(data_list):
            m = d["metrics"]

            rows.append({
                "Paper": f"Paper {i+1}",
                "Gain": m["gain"],
                "S11": m["s11"],
                "Bandwidth": m["bandwidth"]
            })

        df = pd.DataFrame(rows)

        st.dataframe(df)

        fig = px.line_polar(
            df.melt(id_vars=["Paper"], var_name="Metric", value_name="Value"),
            r="Value",
            theta="Metric",
            color="Paper",
            line_close=True
        )

        st.plotly_chart(fig, use_container_width=True)
