import fitz  # PyMuPDF

def extract_text(uploaded_file):
    text = ""

    file_bytes = uploaded_file.read()

    doc = fitz.open(stream=file_bytes, filetype="pdf")

    for page in doc:
        text += page.get_text()

    return text
