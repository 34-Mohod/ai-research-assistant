import streamlit as st
import tempfile
import pandas as pd
import plotly.express as px

from modules.agent_controller import run_agent

st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("🧠 AI Research Assistant")

uploaded_files = st.file_uploader("Upload Research Papers", type="pdf", accept_multiple_files=True)

# ---------- RADAR ----------
def radar_chart(metrics):
    gain = metrics.get("gain", 0) or 0
    s11 = abs(metrics.get("s11", 0) or 0)
    bw = metrics.get("bandwidth", 0) or 0

    values = [
        min(gain / 15, 1),
        min(s11 / 60, 1),
        min(bw / 50, 1)
    ]

    df = pd.DataFrame({
        "Metric": ["Gain", "S11", "Bandwidth"],
        "Value": values
    })

    fig = px.line_polar(df, r="Value", theta="Metric", line_close=True)
    fig.update_traces(fill='toself')

    st.plotly_chart(fig, use_container_width=True)

# ---------- PROCESS ----------
if uploaded_files:

    all_results = []

    for file in uploaded_files:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            path = tmp.name

        if st.button(f"🚀 Process {file.name}"):

            with st.spinner("Processing..."):
                data = run_agent(path)

            metrics = data.get("metrics", {})

            all_results.append({
                "paper": file.name,
                "gain": metrics.get("gain", 0),
                "s11": metrics.get("s11", 0),
                "bandwidth": metrics.get("bandwidth", 0)
            })

            tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📄 Raw Output", "⚖️ Comparison"])

            # ---------- ANALYSIS ----------
            with tab1:

                c1, c2, c3 = st.columns(3)

                c1.metric("Gain", metrics.get("gain", "N/A"))
                c2.metric("S11", metrics.get("s11", "N/A"))
                c3.metric("Bandwidth", metrics.get("bandwidth", "N/A"))

                st.markdown("---")

                colA, colB = st.columns(2)

                with colA:
                    st.subheader("🧠 Summary")
                    st.write(data.get("summary", ""))

                with colB:
                    st.subheader("⚙️ Methodology")
                    st.write(data.get("methodology", ""))

                st.subheader("🚀 Contributions")
                for c in data.get("contributions", []):
                    st.write("-", c)

                st.subheader("📊 Results")
                st.write(data.get("results", ""))

                st.subheader("📈 Performance Radar")
                radar_chart(metrics)

            # ---------- RAW ----------
            with tab2:
                st.json(data)

            # ---------- COMPARISON ----------
            with tab3:

                if len(all_results) > 1:
                    df = pd.DataFrame(all_results)

                    st.dataframe(df)

                    fig = px.line_polar(
                        df,
                        r="gain",
                        theta=["gain", "s11", "bandwidth"],
                        color="paper",
                        line_close=True
                    )

                    st.plotly_chart(fig)

                else:
                    st.info("Upload multiple papers for comparison.")
