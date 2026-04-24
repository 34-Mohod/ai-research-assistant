import streamlit as st
import pandas as pd
import plotly.express as px
from modules.agent_controller import run_agent
import PyPDF2

st.set_page_config(layout="wide")

# ---------------- SESSION FIX (ONLY IMPORTANT ADD) ----------------
if "results" not in st.session_state:
    st.session_state.results = []

# ---------------- PREMIUM CSS ----------------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: Inter, system-ui;
    background-color: #0B0F19;
    color: #E5E7EB;
}
.block-container {
    max-width: 1100px;
    margin: auto;
    padding-top: 2rem;
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1rem;
    border-bottom: 1px solid #1F2937;
    margin-bottom: 2rem;
}
.card {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 20px;
    border-radius: 16px;
}
.metric-value {
    font-size: 34px;
    font-weight: 700;
}
.metric-label {
    color: #9CA3AF;
    font-size: 14px;
}
.section {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 20px;
}
.stButton>button {
    background: #6366F1;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="header">
    <h2>🧠 AI Research Assistant</h2>
    <div style="color:#9CA3AF;">Enterprise AI Dashboard</div>
</div>
""", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# ---------------- GENERATE ----------------
if uploaded_files:
    if st.button("🚀 Generate Summary"):

        # 🔥 clear old results before new run
        st.session_state.results = []

        with st.spinner("Analyzing paper..."):
            for file in uploaded_files:
                text = extract_text_from_pdf(file)
                data = run_agent(text)
                st.session_state.results.append(data)

# ---------------- DISPLAY ----------------
if st.session_state.results:

    data = st.session_state.results[-1]
    metrics = data["metrics"]

    tab1, tab2, tab3 = st.tabs(["Analysis", "Raw Data", "Comparison"])

    # ---------------- ANALYSIS ----------------
    with tab1:
        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="card">
            <div class="metric-label">Gain (dBi)</div>
            <div class="metric-value">{metrics['gain']}</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="card">
            <div class="metric-label">S11 (dB)</div>
            <div class="metric-value">{metrics['s11']}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="card">
            <div class="metric-label">Bandwidth (MHz)</div>
            <div class="metric-value">{metrics['bandwidth']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="section">
            <h3>🧾 Summary</h3>
            <p>{data['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- RAW ----------------
    with tab2:
        st.json(data)

    # ---------------- COMPARISON ----------------
    with tab3:

        if len(st.session_state.results) < 2:
            st.warning("Upload at least 2 papers for comparison")

        else:
            comparison_data = []

            for i, r in enumerate(st.session_state.results):
                comparison_data.append({
                    "Paper": f"Paper {i+1}",
                    "Gain": r["metrics"]["gain"],
                    "S11": r["metrics"]["s11"],
                    "Bandwidth": r["metrics"]["bandwidth"]
                })

            df = pd.DataFrame(comparison_data)

            st.subheader("📊 Comparison Table")
            st.dataframe(df, use_container_width=True)

            st.subheader("📈 Performance Comparison")

            chart_df = df.melt(
                id_vars="Paper",
                var_name="Metric",
                value_name="Value"
            )

            fig = px.bar(
                chart_df,
                x="Paper",
                y="Value",
                color="Metric",
                barmode="group"
            )

            st.plotly_chart(fig, use_container_width=True)
