import streamlit as st
import tempfile
from modules.pdf_extractor import extract_text
from modules.agent_controller import run_agent

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="centered",
    page_icon="🧠"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0b0f1a, #111827);
    color: white;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
}

/* Glass Card */
.card {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 18px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    margin-bottom: 25px;
}

/* Header */
.title {
    font-size: 38px;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 10px;
}

.tagline {
    text-align: center;
    color: #6b7280;
    margin-bottom: 30px;
}

/* Button */
.stButton>button {
    width: 100%;
    height: 52px;
    border-radius: 14px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(90deg, #7c3aed, #3b82f6);
    color: white;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(124,58,237,0.5);
}

/* Section Titles */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Divider */
.divider {
    height: 1px;
    background: rgba(255,255,255,0.1);
    margin: 20px 0;
}

/* Tags */
.tag {
    background: rgba(124,58,237,0.2);
    color: #c4b5fd;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    margin: 4px;
    display: inline-block;
}

/* Badges */
.badge {
    background: rgba(59,130,246,0.2);
    color: #93c5fd;
    padding: 6px 12px;
    border-radius: 10px;
    font-size: 13px;
    margin: 4px;
    display: inline-block;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown('<div class="title">🧠 AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a research paper and get structured insights instantly</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Built for RF • Antenna • AI Researchers</div>', unsafe_allow_html=True)

# ---------------- UPLOAD ----------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📄 Upload Research Paper</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["pdf"])

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- PROCESS ----------------
if uploaded_file:

    # File info
    st.markdown(f"""
    **📄 File:** {uploaded_file.name}  
    **📦 Size:** {round(uploaded_file.size / 1024, 2)} KB
    """)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.success("✅ File uploaded successfully")

    if st.button("🚀 Generate Summary"):

        progress = st.progress(0)

        for i in range(100):
            progress.progress(i + 1)

        text = extract_text(pdf_path)
        output = run_agent(text)

        progress.empty()

        # ---------------- OUTPUT ----------------
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Analysis Result</div>', unsafe_allow_html=True)

        sections = output.split("\n")
        current_section = ""
        buffer = []

        def render_section(title, content):

            st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

            if title == "🚀 Key Contributions":
                for line in content:
                    if line.strip():
                        st.markdown(f'<div class="tag">{line.replace("•","").strip()}</div>', unsafe_allow_html=True)

            elif title == "📊 Results":
                for line in content:
                    if line.strip():
                        st.markdown(f'<div class="badge">{line.replace("•","").strip()}</div>', unsafe_allow_html=True)

            else:
                st.write("\n".join(content))

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        for line in sections:

            if "Title:" in line:
                if buffer:
                    render_section(current_section, buffer)
                    buffer = []
                current_section = "📄 Title"
                buffer.append(line.replace("Title:", "").strip())

            elif "Summary:" in line:
                if buffer:
                    render_section(current_section, buffer)
                    buffer = []
                current_section = "🧠 Summary"

            elif "Key Contributions:" in line:
                if buffer:
                    render_section(current_section, buffer)
                    buffer = []
                current_section = "🚀 Key Contributions"

            elif "Methodology:" in line:
                if buffer:
                    render_section(current_section, buffer)
                    buffer = []
                current_section = "⚙️ Methodology"

            elif "Results:" in line:
                if buffer:
                    render_section(current_section, buffer)
                    buffer = []
                current_section = "📊 Results"

            elif "Limitations:" in line:
                if buffer:
                    render_section(current_section, buffer)
                    buffer = []
                current_section = "🚧 Limitations"

            elif "Future Work:" in line:
                if buffer:
                    render_section(current_section, buffer)
                    buffer = []
                current_section = "🔮 Future Work"

            else:
                buffer.append(line)

        if buffer:
            render_section(current_section, buffer)

        # -------- DOWNLOAD --------
        st.download_button(
            label="📥 Download Summary",
            data=output,
            file_name="summary.txt",
            mime="text/plain"
        )

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Upload a PDF to start analysis")