import streamlit as st
import pandas as pd
import plotly.express as px
from modules.agent_controller import run_agent
import PyPDF2

st.set_page_config(layout="wide")

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

# ✅ FIX 1: Proper session state init (no indentation issue)
if "results" not in st.session_state:
    st.session_state.results = []

# ❌ REMOVE THIS LINE (important)
# results = []

# ---------------- GENERATE ----------------
if uploaded_files:
    if st.button("🚀 Generate Summary"):

        # ✅ Reset correctly
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

    # ✅ FIX 2: use session_state
    data = st.session_state.results[-1]
    metrics = data["metrics"]

    # ---------------- ANALYSIS ----------------
    with tab1:
        col1, col2, col3 = st.columns(3)

        col1.metric("Gain (dBi)", metrics["gain"])
        col2.metric("S11 (dB)", metrics["s11"])
        col3.metric("Bandwidth (MHz)", metrics["bandwidth"])

        st.write("### 🧾 Summary")
        st.write(data["summary"])

        st.write("### ⚙️ Methodology")
        st.write(data["methodology"])

        st.write("### 🚀 Contributions")
        for c in data["contributions"]:
            st.write(f"- {c}")

        st.write("### 📊 Results")
        st.write(data["results"])

    # ---------------- RAW ----------------
    with tab2:
        st.json(data)

    # ---------------- COMPARISON ----------------
    with tab3:

        # ✅ FIX 3: use session_state everywhere
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

            st.dataframe(df, use_container_width=True)

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
