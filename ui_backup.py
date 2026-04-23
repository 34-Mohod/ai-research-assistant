import streamlit as st
import tempfile
import time
from modules.agent_controller import run_agent

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant Pro",
    layout="wide",
    page_icon="🧠"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

/* Container */
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* Title */
.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #8b5cf6, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

/* Card */
.card {
    background: rgba(255,255,255,0.04);
    padding: 25px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    margin-bottom: 20px;
}

/* Button */
.stButton>button {
    width: 100%;
    height: 50px;
    border-radius: 12px;
    background: linear-gradient(90deg, #7c3aed, #3b82f6);
    color: white;
    font-weight: 600;
    border: none;
}

/* Section */
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 10px;
}

/* Tags */
.tag {
    display: inline-block;
    background: rgba(124,58,237,0.2);
    color: #c4b5fd;
    padding: 6px 12px;
    border-radius: 999px;
    margin: 4px;
}

/* Badge */
.badge {
    display: inline-block;
    background: rgba(59,130,246,0.2);
    color: #93c5fd;
    padding: 6px 12px;
    border-radius: 8px;
    margin: 4px;
}

/* Divider */
.divider {
    height: 1px;
    background: rgba(255,255,255,0.1);
    margin: 15px 0;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">🧠 AI Research Assistant Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload research papers and extract structured RF insights</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Controls")

    summary_style = st.selectbox(
        "Summary Style",
        ["Technical", "Simple", "Research-Oriented"]
    )

    temperature = st.slider("Creativity", 0.0, 1.0, 0.3)

    st.markdown("---")

    st.markdown("### ℹ️ About")
    st.write("AI-powered RF research analyzer using LLM")

# ---------------- UPLOAD ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📄 Upload Paper</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PROCESS ----------------
if uploaded_file:

    st.success("File uploaded successfully")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    if st.button("🚀 Generate Summary"):

        progress = st.progress(0)

        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        output = run_agent(pdf_path)

        progress.empty()

        # ---------------- OUTPUT ----------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Analysis Result</div>', unsafe_allow_html=True)

        sections = output.split("\n")

        current = ""
        buffer = []

        def render(title, content):
            if not title.strip():
                title = "📌 Section"

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

        for line in sections:

            if "Title:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []
                current = "📄 Title"

            elif "Summary:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []
                current = "🧠 Summary"

            elif "Key Contributions:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []
                current = "🚀 Key Contributions"

            elif "Methodology:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []
                current = "⚙️ Methodology"

            elif "Results:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []
                current = "📊 Results"

            elif "Limitations:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []
                current = "🚧 Limitations"

            elif "Future Work:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []
                current = "🔮 Future Work"

            else:
                buffer.append(line)

        if buffer:
            render(current, buffer)

        st.download_button(
            "📥 Download Summary",
            data=output,
            file_name="summary.txt"
        )

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Upload a PDF to start analysis")
