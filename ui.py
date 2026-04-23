import streamlit as st
import tempfile
from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant Pro",
    layout="wide",
    page_icon="🧠"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

/* GLOBAL */
body {
    background: linear-gradient(135deg, #0b0f1a, #111827);
    color: white;
}

/* TITLE */
.main-title {
    font-size: 48px;
    font-weight: 900;
    text-align: center;
    background: linear-gradient(90deg,#a78bfa,#60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 20px;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 15px 50px rgba(0,0,0,0.4);
    margin-bottom: 25px;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    height: 55px;
    border-radius: 14px;
    background: linear-gradient(90deg,#7c3aed,#3b82f6);
    color: white;
    font-weight: 700;
}

/* TAG */
.tag {
    display:inline-block;
    background: rgba(124,58,237,0.2);
    color:#c4b5fd;
    padding:6px 12px;
    border-radius:999px;
    margin:4px;
}

/* BADGE */
.badge {
    display:inline-block;
    background: rgba(59,130,246,0.2);
    color:#93c5fd;
    padding:6px 12px;
    border-radius:10px;
    margin:4px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("⚙️ Controls")

    tone = st.selectbox("Summary Style", ["Technical", "Short", "Detailed"])
    temperature = st.slider("Creativity", 0.0, 1.0, 0.3)

    st.markdown("---")
    st.markdown("### 📊 About")
    st.write("AI-powered RF Research Analyzer")

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">🧠 AI Research Assistant PRO</div>', unsafe_allow_html=True)
st.markdown("### Upload a research paper and get deep structured insights")

# ---------------- UPLOAD ----------------
col1, col2 = st.columns([2,1])

with col1:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

with col2:
    st.info("Supports IEEE papers, journals, reports")

# ---------------- PROCESS ----------------
if uploaded_file:

    st.markdown('<div class="card">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("File", uploaded_file.name)
    c2.metric("Size (KB)", round(uploaded_file.size/1024,2))
    c3.metric("Status", "Ready")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    if st.button("🚀 Generate Summary"):

        progress = st.progress(0)

        for i in range(100):
            progress.progress(i+1)

        text = extract_text(pdf_path)
        output = summarize_text(text)

        progress.empty()

        st.markdown('</div>', unsafe_allow_html=True)

        # ---------------- OUTPUT TABS ----------------
        tab1, tab2 = st.tabs(["📊 Structured Output", "📄 Raw Output"])

        with tab1:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            sections = output.split("\n")
            current = "📄 Section"
            buffer = []

            def render(title, content):
    # Ensure title is never empty
                if not title or not title.strip():
                   title = "📄 Section"

    with st.expander(title, expanded=True):

        if title == "🚀 Key Contributions":
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        elif title == "📊 Results":
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        else:
            st.write("\n".join(content))

        if title == "🚀 Key Contributions":
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        elif title == "📊 Results":
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        else:
            st.write("\n".join(content))

                    if title == "🚀 Key Contributions":
                        for line in content:
                            if line.strip():
                                st.markdown(f'<div class="tag">{line.replace("•","")}</div>', unsafe_allow_html=True)

                    elif title == "📊 Results":
                        for line in content:
                            if line.strip():
                                st.markdown(f'<div class="badge">{line.replace("•","")}</div>', unsafe_allow_html=True)

                    else:
                        st.write("\n".join(content))

            for line in sections:

                if "Title:" in line:
                    if buffer:
                        render(current, buffer)
                        buffer=[]
                    current="📄 Title"
                    buffer.append(line.replace("Title:","").strip())

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

            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.write(output)

        # ---------------- DOWNLOAD ----------------
        st.download_button(
            label="📥 Download Summary",
            data=output,
            file_name="summary.txt",
            mime="text/plain"
        )

else:
    st.warning("Upload a PDF to begin")
