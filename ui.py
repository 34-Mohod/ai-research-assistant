import streamlit as st
import tempfile
from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="centered",
    page_icon="🧠"
)

# ---------------- HEADER ----------------
st.title("🧠 AI Research Assistant")
st.markdown("Upload a research paper and get structured insights instantly")

# ---------------- UPLOAD ----------------
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

# ---------------- PROCESS ----------------
if uploaded_file:

    st.write(f"📄 File: {uploaded_file.name}")
    st.write(f"📦 Size: {round(uploaded_file.size / 1024, 2)} KB")

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    st.success("✅ File uploaded successfully")

    if st.button("🚀 Generate Summary"):

        with st.spinner("Processing..."):

            text = extract_text(pdf_path)
            output = summarize_text(text)

        st.subheader("📊 Analysis Result")
        st.write(output)

        st.download_button(
            label="📥 Download Summary",
            data=output,
            file_name="summary.txt",
            mime="text/plain"
        )

else:
    st.info("Upload a PDF to start analysis")
