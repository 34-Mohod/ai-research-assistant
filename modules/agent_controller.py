from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text


def run_agent(file_path):
    """
    Full pipeline:
    PDF → Extract Text → LLM → Output
    """
    try:
        text = extract_text(file_path)

        if not text or len(text.strip()) == 0:
            return "⚠️ No text extracted from PDF."

        output = summarize_text(text)

        return output

    except Exception as e:
        return f"⚠️ Agent Error: {str(e)}"

