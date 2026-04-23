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

# ---------------- HEADER ----------------
st.title("🧠 AI Research Assistant")
st.write("Upload a research paper and get structured insights.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

# ---------------- RENDER FUNCTION ----------------
def render(title, content):
    if not title or not title.strip():
        title = "📄 Section"

    with st.expander(title, expanded=True):

        # Key Contributions → tags
        if "Key Contributions" in title:
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        # Results → badges style
        elif "Results" in title:
            for line in content:
                if line.strip():
                    st.markdown(f"- {line.replace('•','').strip()}")

        else:
            st.write("\n".join(content))

# ---------------- PROCESS ----------------
if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.success("File uploaded successfully")

    if st.button("🚀 Generate Summary"):

        # progress bar
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)

        # run pipeline
        output = run_agent(pdf_path)

        progress.empty()

        # ---------------- PARSING ----------------
        lines = output.split("\n")

        current = ""
        buffer = []

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # -------- TITLE --------
            if "Title:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []

                current = "📄 Title"

                if i + 1 < len(lines):
                    buffer.append(lines[i + 1].strip())
                    i += 1

            # -------- SUMMARY --------
            elif "Summary:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []

                current = "🧠 Summary"

                if i + 1 < len(lines):
                    buffer.append(lines[i + 1].strip())
                    i += 1

            # -------- CONTRIBUTIONS --------
            elif "Key Contributions:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []

                current = "🚀 Key Contributions"

            # -------- METHODOLOGY --------
            elif "Methodology:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []

                current = "⚙️ Methodology"

            # -------- RESULTS --------
            elif "Results:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []

                current = "📊 Results"

            # -------- LIMITATIONS --------
            elif "Limitations:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []

                current = "🚧 Limitations"

            # -------- FUTURE WORK --------
            elif "Future Work:" in line:
                if buffer:
                    render(current, buffer)
                    buffer = []

                current = "🔮 Future Work"

            else:
                buffer.append(line)

            i += 1

        # render last section
        if buffer:
            render(current, buffer)

        # ---------------- DOWNLOAD ----------------
        st.download_button(
            "📥 Download Summary",
            data=output,
            file_name="summary.txt"
        )

else:
    st.info("Upload a PDF to begin")
