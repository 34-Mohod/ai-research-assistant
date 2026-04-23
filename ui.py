import streamlit as st
import tempfile
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from modules.agent_controller import run_agent

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant Pro+",
    layout="wide",
    page_icon="🧠"
)

# ---------------- STATE ----------------
if "results" not in st.session_state:
    st.session_state.results = []

# ---------------- HEADER ----------------
st.title("🧠 AI Research Assistant Pro+")
st.caption("Advanced RF Research Analyzer with Comparison + Charts + Scoring")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Settings")

    mode = st.selectbox("Mode", ["Technical", "Simple"])
    creativity = st.slider("Creativity", 0.0, 1.0, 0.3)

    st.markdown("---")
    st.subheader("📊 Tools")
    compare_mode = st.checkbox("Enable Comparison Mode")
    show_charts = st.checkbox("Enable Charts", True)
    show_score = st.checkbox("Enable Scoring", True)

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader(
    "Upload Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

# ---------------- HELPER: PARSER ----------------
def parse_output(output):
    sections = {}
    current = "General"
    sections[current] = []

    for line in output.split("\n"):
        line = line.strip()
        if not line:
            continue

        if ":" in line and len(line.split(":")[0]) < 40:
            key = line.split(":")[0].strip().title()
            current = key
            sections[current] = []

            rest = line.split(":", 1)[1].strip()
            if rest:
                sections[current].append(rest)
        else:
            sections[current].append(line)

    return sections

# ---------------- HELPER: RF PARAM EXTRACTION ----------------
def extract_rf_metrics(text):
    metrics = {
        "gain": None,
        "bandwidth": None,
        "frequency": None
    }

    gain_match = re.search(r'(\d+\.?\d*)\s*dB', text, re.I)
    bw_match = re.search(r'(\d+\.?\d*)\s*GHz', text, re.I)
    freq_match = re.search(r'(\d+\.?\d*)\s*THz', text, re.I)

    if gain_match:
        metrics["gain"] = float(gain_match.group(1))

    if bw_match:
        metrics["bandwidth"] = float(bw_match.group(1))

    if freq_match:
        metrics["frequency"] = float(freq_match.group(1))

    return metrics

# ---------------- HELPER: SCORING ----------------
def compute_score(text):
    score = 0

    if "gain" in text.lower():
        score += 2
    if "s11" in text.lower():
        score += 2
    if "bandwidth" in text.lower():
        score += 2
    if "radiation" in text.lower():
        score += 2
    if "efficiency" in text.lower():
        score += 2

    return score

# ---------------- PROCESS ----------------
if uploaded_files:

    for file in uploaded_files:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            path = tmp.name

        if st.button(f"Analyze {file.name}"):

            with st.spinner("Processing..."):
                output = run_agent(path)

                parsed = parse_output(output)
                metrics = extract_rf_metrics(output)
                score = compute_score(output)

                st.session_state.results.append({
                    "name": file.name,
                    "output": output,
                    "parsed": parsed,
                    "metrics": metrics,
                    "score": score
                })

# ---------------- DISPLAY ----------------
if st.session_state.results:

    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Individual Analysis",
        "📊 Comparison",
        "📈 Charts",
        "🏆 Scoring"
    ])

    # -------- INDIVIDUAL --------
    with tab1:
        for res in st.session_state.results:
            st.subheader(res["name"])

            for title, content in res["parsed"].items():
                with st.expander(title):
                    st.write("\n".join(content))

    # -------- COMPARISON --------
    with tab2:

        if len(st.session_state.results) < 2:
            st.warning("Upload at least 2 papers for comparison")
        else:
            df = pd.DataFrame([
                {
                    "Paper": r["name"],
                    "Gain": r["metrics"]["gain"],
                    "Bandwidth": r["metrics"]["bandwidth"],
                    "Frequency": r["metrics"]["frequency"],
                    "Score": r["score"]
                }
                for r in st.session_state.results
            ])

            st.dataframe(df)

    # -------- CHARTS --------
    with tab3:

        if show_charts and len(st.session_state.results) >= 1:

            df = pd.DataFrame([
                {
                    "Paper": r["name"],
                    "Gain": r["metrics"]["gain"] or 0,
                    "Bandwidth": r["metrics"]["bandwidth"] or 0,
                    "Score": r["score"]
                }
                for r in st.session_state.results
            ])

            st.subheader("Gain Comparison")
            fig, ax = plt.subplots()
            ax.bar(df["Paper"], df["Gain"])
            plt.xticks(rotation=45)
            st.pyplot(fig)

            st.subheader("Bandwidth Comparison")
            fig, ax = plt.subplots()
            ax.bar(df["Paper"], df["Bandwidth"])
            plt.xticks(rotation=45)
            st.pyplot(fig)

    # -------- SCORING --------
    with tab4:

        if show_score:
            for r in st.session_state.results:
                st.subheader(r["name"])

                score = r["score"]

                if score >= 8:
                    st.success(f"High Quality ({score}/10)")
                elif score >= 5:
                    st.warning(f"Moderate Quality ({score}/10)")
                else:
                    st.error(f"Low Quality ({score}/10)")

                st.progress(score / 10)
