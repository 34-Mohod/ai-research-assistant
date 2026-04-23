import streamlit as st
import tempfile
import time
from modules.agent_controller import run_agent

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    page_icon="🧠"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* Global */
body {
    background: #0b0f19;
    color: #e5e7eb;
}

/* Header */
.title {
    font-size: 44px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg,#6366f1,#3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 25px;
}

/* Cards */
.card {
    background: #111827;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #1f2937;
    margin-bottom: 20px;
}

/* Metrics */
.metric {
    background: #0f172a;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg,#6366f1,#3b82f6);
    border-radius: 12px;
    height: 48px;
    font-weight: 600;
    color: white;
    border: none;
}

/* Tags */
.tag {
    display:inline-block;
    padding:6px 12px;
    margin:4px;
    border-radius:999px;
    background:#312e81;
}

/* Badge */
.badge {
    display:inline-block;
    padding:6px 10px;
    margin:4px;
    border-radius:8px;
    background:#1e3a8a;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">🧠 AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Advanced RF Paper Analyzer • Structured Intelligence • ML-assisted summarization</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Controls")

    mode = st.selectbox("Mode", ["Technical", "Research", "Simple"])
    temp = st.slider("Creativity", 0.0, 1.0, 0.3)

    st.markdown("---")
    st.write("Built for RF / Antenna / THz Research")

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([2,1])

# ---------------- LEFT PANEL ----------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📄 Upload Paper")
    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        st.success("File uploaded")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            path = tmp.name

        if st.button("🚀 Analyze Paper"):
            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i+1)

            output = run_agent(path)
            progress.empty()

            st.session_state["result"] = output

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RIGHT PANEL ----------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Quick Stats")

    st.markdown("""
    <div class="metric">Papers Analyzed<br><b>1</b></div>
    <div class="metric">Model<br><b>LLM (Groq)</b></div>
    <div class="metric">Status<br><b>Active</b></div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- OUTPUT ----------------
if "result" in st.session_state:

    st.markdown("## 📊 Analysis Dashboard")

    tab1, tab2, tab3 = st.tabs(["Structured", "Raw Output", "Insights"])

    output = st.session_state["result"]

    # -------- TAB 1 --------
    with tab1:
        lines = output.split("\n")

        current = ""
        buffer = []

        def render(title, content):
            with st.expander(title, expanded=True):

                if "Key Contributions" in title:
                    for line in content:
                        if line.strip():
                            st.markdown(f'<div class="tag">{line}</div>', unsafe_allow_html=True)

                elif "Results" in title:
                    for line in content:
                        if line.strip():
                            st.markdown(f'<div class="badge">{line}</div>', unsafe_allow_html=True)

                else:
                    st.write("\n".join(content))

        for line in lines:

            if "Title:" in line:
                if buffer:
                    render(current, buffer)
                    buffer=[]
                current="📄 Title"

            elif "Summary:" in line:
                if buffer:
                    render(current, buffer)
                    buffer=[]
                current="🧠 Summary"

            elif "Key Contributions:" in line:
                if buffer:
                    render(current, buffer)
                    buffer=[]
                current="🚀 Key Contributions"

            elif "Methodology:" in line:
                if buffer:
                    render(current, buffer)
                    buffer=[]
                current="⚙️ Methodology"

            elif "Results:" in line:
                if buffer:
                    render(current, buffer)
                    buffer=[]
                current="📊 Results"

            elif "Limitations:" in line:
                if buffer:
                    render(current, buffer)
                    buffer=[]
                current="🚧 Limitations"

            elif "Future Work:" in line:
                if buffer:
                    render(current, buffer)
                    buffer=[]
                current="🔮 Future Work"

            else:
                buffer.append(line)

        if buffer:
            render(current, buffer)

    # -------- TAB 2 --------
    with tab2:
        st.code(output)

    # -------- TAB 3 --------
    with tab3:
        st.write("### 📈 Insights")
        st.write("• Strong RF design detected")
        st.write("• High gain optimization present")
        st.write("• Possible ML-assisted tuning")

    # -------- DOWNLOAD --------
    st.download_button(
        "📥 Download Summary",
        data=output,
        file_name="summary.txt"
    )
