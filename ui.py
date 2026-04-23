import streamlit as st

import tempfile

from modules.pdf_extractor import extract_text

from modules.agent_controller import run_agent

st.set_page_config(page_title="AI Research Assistant", layout="centered")

st.title("🧠 AI Research Assistant")

st.write("Upload a research paper and get structured insights.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

def render_section(title, content):

    if not title or not title.strip():

        title = "Section"

    with st.expander(title, expanded=True):

        if isinstance(content, list):

            for line in content:

                if line.strip():

                    st.write(line)

        else:

            st.write(content)

if uploaded_file:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

        tmp.write(uploaded_file.read())

        pdf_path = tmp.name

    st.success("File uploaded")

    if st.button("Generate Summary"):

        text = extract_text(pdf_path)

        output = run_agent(text)

        sections = output.split("\n")

        current = ""

        buffer = []

        for line in sections:

            if "Title:" in line:

                if buffer:

                    render_section(current, buffer)

                    buffer = []

                current = "📄 Title"

                buffer.append(line.replace("Title:", "").strip())

            elif "Summary:" in line:

                if buffer:

                    render_section(current, buffer)

                    buffer = []

                current = "🧠 Summary"

            elif "Key Contributions:" in line:

                if buffer:

                    render_section(current, buffer)

                    buffer = []

                current = "🚀 Key Contributions"

            elif "Methodology:" in line:

                if buffer:

                    render_section(current, buffer)

                    buffer = []

                current = "⚙️ Methodology"

            elif "Results:" in line:

                if buffer:

                    render_section(current, buffer)

                    buffer = []

                current = "📊 Results"

            elif "Limitations:" in line:

                if buffer:

                    render_section(current, buffer)

                    buffer = []

                current = "🚧 Limitations"

            elif "Future Work:" in line:

                if buffer:

                    render_section(current, buffer)

                    buffer = []

                current = "🔮 Future Work"

            else:

                buffer.append(line)

        if buffer:

            render_section(current, buffer)

        st.download_button(

            "Download Summary",

            data=output,

            file_name="summary.txt"

        )

else:

    st.info("Upload a PDF to begin")
