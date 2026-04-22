from modules.llm_engine import summarize_text

def run_agent(text):

    print("[Agent] Running analysis...")

    # Simple (no chunking for stability)
    summary = summarize_text(text)

    return summary