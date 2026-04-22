from modules.llm_engine import summarize_text

# 🔹 Split text into chunks
def chunk_text(text, size=8000):
    return [text[i:i+size] for i in range(0, len(text), size)]


def run_agent(text):

    print("\n[Agent] Starting analysis...\n")

    # 🔹 Small document → direct
    if len(text) < 5000:
        print("[Agent] Small document → Direct processing\n")
        return summarize_text(text)

    # 🔹 Large document → chunking
    print("[Agent] Large document → Using chunking strategy\n")

    chunks = chunk_text(text)
    summaries = []

    MAX_CHUNKS = 3   # control cost + speed

    for i, chunk in enumerate(chunks[:MAX_CHUNKS]):
        print(f"[Agent] Processing chunk {i+1}/{len(chunks)}")

        try:
            result = summarize_text(chunk)

            # If error from LLM, skip
            if isinstance(result, dict) and "error" in result:
                print("[Agent] Invalid JSON from LLM, skipping chunk")
                continue

            summaries.append(result)

        except Exception as e:
            print(f"[Agent] Error: {e}")
            break

    print("\n[Agent] Combining results...\n")

    # 🔹 Combine structured outputs intelligently
    combined_text = ""

    for s in summaries:
        combined_text += f"""
Title: {s.get('title', '')}
Summary: {s.get('summary', '')}
Contributions: {s.get('contributions', [])}
Methodology: {s.get('methodology', '')}
Results: {s.get('results', '')}
Limitations: {s.get('limitations', [])}
Future Work: {s.get('future_work', [])}
"""

    # 🔹 Final refined summary (structured again)
    final_result = summarize_text(combined_text)

    return final_result