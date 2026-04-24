import streamlit as st
import pandas as pd
import plotly.express as px
from modules.agent_controller import run_agent
import PyPDF2

st.set_page_config(layout="wide")

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
.section {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 20px;
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

# ---------------- SESSION STATE ----------------
if "results" not in st.session_state:
    st.session_state.results = []

# ---------------- GENERATE ----------------
if uploaded_files:
    if st.button("🚀 Generate Summary"):

        st.session_state.results = []

        with st.spinner("Analyzing paper..."):
            for file in uploaded_files:
                text = extract_text_from_pdf(file)
                data = run_agent(text)

                if isinstance(data, dict) and "metrics" in data:
                    st.session_state.results.append(data)
                else:
                    st.warning("Skipped invalid response")

# ---------------- DISPLAY ----------------
if st.session_state.results:

    tab1, tab2, tab3 = st.tabs(["Analysis", "Raw Data", "Comparison"])

    data = st.session_state.results[-1]
    metrics = data["metrics"]

    # ---------------- ANALYSIS ----------------
    with tab1:

        # ✅ NEW: Title
        st.markdown(f"""
        <div class="section">
            <h3>📄 Title</h3>
            <p>{data.get('title','')}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        col1.metric("Gain (dBi)", metrics["gain"])
        col2.metric("S11 (dB)", metrics["s11"])
        col3.metric("Bandwidth (MHz)", metrics["bandwidth"])

        # ✅ NEW: Progress bars
        st.markdown("### 📊 Performance Breakdown")
        st.progress(min(max(metrics["gain"]/20, 0), 1))
        st.caption("Gain Quality")

        st.progress(min(max(abs(metrics["s11"])/50, 0), 1))
        st.caption("S11 Performance")

        st.progress(min(max(metrics["bandwidth"]/100, 0), 1))
        st.caption("Bandwidth Strength")

        st.markdown(f"""
        <div class="section">
            <h3>🧾 Summary</h3>
            <p>{data['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="section">
            <h3>⚙️ Methodology</h3>
            <p>{data['methodology']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section'><h3>🚀 Contributions</h3>", unsafe_allow_html=True)
        for c in data["contributions"]:
            st.markdown(f"- {c}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="section">
            <h3>📊 Results</h3>
            <p>{data['results']}</p>
        </div>
        """, unsafe_allow_html=True)

        # ✅ NEW: Applications
        st.markdown("<div class='section'><h3>📌 Applications</h3></div>", unsafe_allow_html=True)
        if data.get("applications"):
            for app in data["applications"].split("."):
                if app.strip():
                    st.markdown(f"• {app.strip()}")
        else:
            st.info("No applications extracted")

        # ✅ NEW: Limitations
        st.markdown("<div class='section'><h3>⚠️ Limitations</h3></div>", unsafe_allow_html=True)
        if data.get("limitations"):
            for lim in data["limitations"].split("."):
                if lim.strip():
                    st.markdown(f"• {lim.strip()}")
        else:
            st.info("No limitations found")

        # ✅ NEW: Future Work
        st.markdown("<div class='section'><h3>🔮 Future Work</h3></div>", unsafe_allow_html=True)
        if data.get("future_work"):
            for fw in data["future_work"].split("."):
                if fw.strip():
                    st.markdown(f"• {fw.strip()}")
        else:
            st.info("No future work identified")

        # Radar chart
        df = pd.DataFrame(dict(
            r=[
                metrics["gain"]/20,
                abs(metrics["s11"])/100,
                metrics["bandwidth"]/100
            ],
            theta=["Gain", "S11", "Bandwidth"]
        ))

        fig = px.line_polar(df, r="r", theta="theta", line_close=True)
        fig.update_traces(fill='toself')
        st.plotly_chart(fig, use_container_width=True)

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

            # ✅ NEW: Ranking
            st.subheader("🏆 Ranking (Higher Gain)")
            df_sorted = df.sort_values(by="Gain", ascending=False)
            st.dataframe(df_sorted, use_container_width=True)

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
