import streamlit as st
import pandas as pd
import plotly.express as px
from modules.agent_controller import run_agent
import PyPDF2

st.set_page_config(layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.card {
    background: #0f172a;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
.section {
    background: #0f172a;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🧠 AI Research Assistant")

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Papers",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- PDF TEXT EXTRACT ----------------
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text


results = []

# ---------------- BUTTON ----------------
if uploaded_files:
    if st.button("🚀 Generate Summary"):
        with st.spinner("Processing..."):
            for file in uploaded_files:
                text = extract_text_from_pdf(file)
                data = run_agent(text)
                results.append(data)

# ---------------- DISPLAY ----------------
if results:
    data = results[-1]
    metrics = data["metrics"]

    tab1, tab2, tab3 = st.tabs(["Analysis", "Raw", "Comparison"])

    # -------- ANALYSIS --------
    with tab1:
        c1, c2, c3 = st.columns(3)

        c1.markdown(f"<div class='card'><h3>Gain</h3><h1>{metrics['gain']}</h1></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'><h3>S11</h3><h1>{metrics['s11']}</h1></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'><h3>Bandwidth</h3><h1>{metrics['bandwidth']}</h1></div>", unsafe_allow_html=True)

        st.markdown("---")

        st.markdown(f"<div class='section'><h2>Summary</h2><p>{data['summary']}</p></div>", unsafe_allow_html=True)

        st.markdown(f"<div class='section'><h2>Methodology</h2><p>{data['methodology']}</p></div>", unsafe_allow_html=True)

        st.markdown("<div class='section'><h2>Contributions</h2>", unsafe_allow_html=True)
        for c in data["contributions"]:
            st.write(f"- {c}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='section'><h2>Results</h2><p>{data['results']}</p></div>", unsafe_allow_html=True)

        st.markdown(f"<div class='section'><h2>📊 Applications</h2><p>{data.get('applications','')}</p></div>", unsafe_allow_html=True)

        st.markdown(f"<div class='section'><h2>⚠ Limitations</h2><p>{data.get('limitations','')}</p></div>", unsafe_allow_html=True)

        st.markdown(f"<div class='section'><h2>🔮 Future Work</h2><p>{data.get('future_work','')}</p></div>", unsafe_allow_html=True)

        # Radar Chart
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

        st.plotly_chart(fig)

    # -------- RAW --------
    with tab2:
        st.json(data)

    # -------- COMPARISON --------
    with tab3:
        st.write("Comparison coming soon...")
