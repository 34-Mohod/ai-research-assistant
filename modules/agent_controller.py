import json
import re
from groq import Groq

client = Groq()

def run_agent(text):
    try:
        # Limit input size
        text = text[:12000]

        prompt = f"""
You are an expert RF and antenna researcher.

Analyze the research paper and return STRICT JSON.

Extract:
- Title
- Detailed Summary (5-6 lines)
- Methodology (detailed explanation)
- Key Contributions (list)
- Results (with numerical values if present)
- Applications (real-world use cases)
- Limitations (technical constraints)
- Future Work (research directions)
- Metrics (gain in dBi, S11 in dB, bandwidth in %)

Return ONLY JSON in this format:

{{
"title": "",
"summary": "",
"methodology": "",
"contributions": [],
"results": "",
"applications": "",
"limitations": "",
"future_work": "",
"metrics": {{
"gain": 0,
"s11": 0,
"bandwidth": 0
}}
}}

Paper:
{text}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1200
        )

       output = response.choices[0].message.content

print("\n📦 RAW OUTPUT:\n", output)

try:
    start = output.find("{")
    end = output.rfind("}") + 1

    json_str = output[start:end]

    # Clean issues from LLM
    json_str = re.sub(r"[\x00-\x1F]+", " ", json_str)
    json_str = json_str.replace("\n", " ")

    # Fix trailing commas (VERY IMPORTANT)
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)

    data = json.loads(json_str)

    return data

except Exception as e:
    print("\n🔥 JSON PARSE ERROR:", e)

    return {
        "title": "Fallback",
        "summary": "Fallback summary",
        "methodology": "Fallback methodology",
        "contributions": [],
        "results": "Fallback results",
        "applications": "",
        "limitations": "",
        "future_work": "",
        "metrics": {
            "gain": 10,
            "s11": -20,
            "bandwidth": 30
        }
    }

    except Exception as e:
        print("ERROR:", e)

        return {
            "title": "Fallback",
            "summary": "Fallback summary",
            "methodology": "Fallback methodology",
            "contributions": [],
            "results": "Fallback results",
            "applications": "",
            "limitations": "",
            "future_work": "",
            "metrics": {
                "gain": 10,
                "s11": -20,
                "bandwidth": 30
            }
        }
