import streamlit as st
import json
import pandas as pd
import plotly.express as px
from modules.agent_controller import run_agent

st.set_page_config(layout="wide")
st.title("🧠 AI Research Assistant")

if "papers" not in st.session_state:
    st.session_state["papers"] = []

uploaded_files = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=True)

fallback_data = {
    "title": "Fallback",
    "summary": "Fallback summary",
    "methodology": "Fallback methodology",
    "contributions": [],
    "results": "Fallback results",
    "metrics": {"gain": 10, "s11": -20, "bandwidth": 30}
}

if uploaded_files:
    for file in uploaded_files:
        if st.button(f"Process {file.name}"):

            output = run_agent(file)

            try:
                data = json.loads(output)
            except:
                data = fallback_data

            st.session_state["papers"].append(data)

tab1, tab2, tab3 = st.tabs(["Analysis", "Raw", "Compare"])

# ---------- Analysis ----------
with tab1:
    if st.session_state["papers"]:
        data = st.session_state["papers"][-1]
        m = data["metrics"]

        st.metric("Gain", m["gain"])
        st.metric("S11", m["s11"])
        st.metric("Bandwidth", m["bandwidth"])

        st.write(data["summary"])
        st.write(data["methodology"])
        st.write(data["results"])

        values = [
            m["gain"]/20,
            abs(m["s11"])/100,
            m["bandwidth"]/100
        ]

        df = pd.DataFrame(dict(
            r=values,
            theta=["Gain","S11","Bandwidth"]
        ))

        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
        st.plotly_chart(fig)

# ---------- Raw ----------
with tab2:
    if st.session_state["papers"]:
        st.json(st.session_state["papers"][-1])

# ---------- Compare ----------
with tab3:
    if len(st.session_state["papers"]) > 1:
        rows = []

        for i, p in enumerate(st.session_state["papers"]):
            m = p["metrics"]
            rows.append({
                "Paper": f"P{i+1}",
                "Gain": m["gain"],
                "S11": m["s11"],
                "Bandwidth": m["bandwidth"]
            })

        df = pd.DataFrame(rows)
        st.dataframe(df)
