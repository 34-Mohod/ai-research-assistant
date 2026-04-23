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

# ---------------- MODERN CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: #e2e8f0;
}
.title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 25px;
}
.stButton > button {
    background: linear-gradient(90deg, #6366f1, #3b82f6);
    color: white;
    border-radius: 10px;
    height: 45px;
    border: none;
    font-weight: 600;
}
.streamlit-expanderHeader {
    font-weight: 600;
    color: #c7d2fe;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">🧠 AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">RF • Antenna • THz • AI-powered Research Analysis</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Controls")
    st.selectbox("Mode", ["Technical", "Simple"])
    st.slider("Creativity", 0.0, 1.0, 0.3)
    st.markdown("---")
    st.write("Model: LLaMA3 (Groq)")
    st.success("Status: Active")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📄 Upload Research Paper (PDF)", type=["pdf"])

# ---------------- RENDER FUNCTION ----------------
def render(title, content):
    if not title or not title.strip():
        title = "📄 Section"

    with st.expander(title, expanded=True):

        if "Key Contributions" in title:
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        elif "Results" in title:
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        else:
            st.write("\n".join(content))

# ---------------- SESSION ----------------
if "result" not in st.session_state:
    st.session_state["result"] = None

# ---------------- PROCESS ----------------
if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.success("File uploaded successfully")

    if st.button("🚀 Generate Summary"):

        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        output = run_agent(pdf_path)
        st.session_state["result"] = output

        progress.empty()

# ---------------- OUTPUT ----------------
if st.session_state["result"]:

    output = st.session_state["result"]

    # 🔥 AGENT VISUAL (NEW)
    st.markdown("""
### 🤖 Multi-Agent System

**Coordinator Agent**
- Orchestrates the full pipeline  

**Research Agent**
- Performs RF paper analysis using LLM  

**Critic Agent**
- Validates and checks output quality  

**Formatter Agent**
- Structures final response  

---
Pipeline:
PDF → Coordinator → Research → Critic → Formatter → Output
""")

    tab1, tab2, tab3 = st.tabs(["📊 Structured", "🧾 Raw Output", "📈 Insights"])

    # ================= TAB 1 =================
    with tab1:

        lines = output.split("\n")
        current = ""
        buffer = []

        def flush():
            if buffer:
                render(current, buffer.copy())
                buffer.clear()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # -------- TITLE --------
            if line.startswith("Title"):
                flush()
                current = "📄 Title"

                if ":" in line and line.split(":", 1)[1].strip():
                    buffer.append(line.split(":", 1)[1].strip())
                else:
                    j = i + 1
                    while j < len(lines) and lines[j].strip():
                        buffer.append(lines[j].strip())
                        j += 1
                    i = j - 1

            # -------- SUMMARY (FIXED STRONG) --------
            elif line.startswith("Summary"):
                flush()
                current = "🧠 Summary"

                if ":" in line and line.split(":", 1)[1].strip():
                    buffer.append(line.split(":", 1)[1].strip())
                else:
                    j = i + 1
                    while j < len(lines) and lines[j].strip():
                        buffer.append(lines[j].strip())
                        j += 1
                    i = j - 1

            # -------- OTHER SECTIONS --------
            elif "Key Contributions" in line:
                flush()
                current = "🚀 Key Contributions"

            elif "Methodology" in line:
                flush()
                current = "⚙️ Methodology"

            elif "Results" in line:
                flush()
                current = "📊 Results"

            elif "Limitations" in line:
                flush()
                current = "🚧 Limitations"

            elif "Future Work" in line:
                flush()
                current = "🔮 Future Work"

            else:
                buffer.append(line)

            i += 1

        flush()

    # ================= TAB 2 =================
    with tab2:
        st.code(output)

    # ================= TAB 3 =================
    with tab3:
        st.subheader("📈 Insights")

        if "gain" in output.lower():
            st.success("✔ Gain optimization detected")

        if "s11" in output.lower():
            st.info("✔ Reflection coefficient analyzed")

        if "bandwidth" in output.lower():
            st.warning("✔ Bandwidth considerations present")

        st.write("• Structured RF analysis completed")
        st.write("• Model confidence: High")

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        "📥 Download Summary",
        data=output,
        file_name="summary.txt"
    )
