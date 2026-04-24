import streamlit as st
import pandas as pd
import plotly.express as px
from modules.agent_controller import run_agent
from modules.judge_agent import judge_papers
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

/* Main Container */
.block-container {
    max-width: 1100px;
    margin: auto;
    padding-top: 2rem;
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1rem;
    border-bottom: 1px solid #1F2937;
    margin-bottom: 2rem;
}

/* Cards */
.card {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 20px;
    border-radius: 16px;
    transition: 0.2s ease;
}

.card:hover {
    transform: translateY(-3px);
    border-color: #374151;
}

/* Metrics */
.metric-value {
    font-size: 34px;
    font-weight: 700;
}

.metric-label {
    color: #9CA3AF;
    font-size: 14px;
}

/* Sections */
.section {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 24px;
    border-radius: 16px;
    margin-bottom: 20px;
}

.section h3 {
    margin-bottom: 10px;
}

/* Buttons */
.stButton>button {
    background: #6366F1;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    transition: 0.2s;
}

.stButton>button:hover {
    background: #4F46E5;
}

/* Tabs */
div[role="tablist"] {
    gap: 10px;
}

button[role="tab"] {
    background: #111827;
    border-radius: 999px;
    padding: 8px 18px;
    border: 1px solid #1F2937;
}

button[aria-selected="true"] {
    background: #6366F1 !important;
    color: white !important;
}

/* Code block */
pre {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 15px;
    border-radius: 12px;
    overflow-x: auto;
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

results = []

if uploaded_files:
    if st.button("🚀 Generate Summary"):
        with st.spinner("Analyzing paper..."):
            for file in uploaded_files:
                text = extract_text_from_pdf(file)
                data = run_agent(text)
                results.append(data)

# ---------------- DISPLAY ----------------
if results:
    data = results[-1]
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

        st.markdown("")

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

        st.markdown(f"""
        <div class="section">
            <h3>📌 Applications</h3>
            <p>{data.get('applications','')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="section">
            <h3>⚠ Limitations</h3>
            <p>{data.get('limitations','')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="section">
            <h3>🔮 Future Work</h3>
            <p>{data.get('future_work','')}</p>
        </div>
        """, unsafe_allow_html=True)

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
        st.markdown("### Raw Output")
        st.json(data)

    # ---------------- COMPARISON ----------------
    with tab3:

        if len(results) < 2:
            st.warning("Upload at least 2 papers for comparison")

        else:
            comparison_data = []

            for i, r in enumerate(results):
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

            # -------- JUDGE (ADDED) --------
            st.markdown("---")
            st.subheader("🧠 AI Judge Verdict")

            if st.button("⚖️ Evaluate Papers"):

                try:
                    with st.spinner("AI is evaluating..."):
                        verdict = judge_papers(results)

                    st.success(f"🏆 Winner: {verdict['winner']}")
                    st.markdown(f"**Reason:** {verdict['reason']}")
                    st.markdown("### 📊 Scores")
                    st.json(verdict["scorecard"])

                except Exception as e:
                    st.error("Judge failed")
                    st.exception(e)    
