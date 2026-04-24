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

        # Extract JSON safely
        start = output.find("{")
        end = output.rfind("}") + 1
        json_str = output[start:end]

        json_str = re.sub(r"[\x00-\x1F]+", " ", json_str)

        data = json.loads(json_str)

        # Ensure all fields exist
        return {
            "title": data.get("title", "Not available"),
            "summary": data.get("summary", "Not available"),
            "methodology": data.get("methodology", "Not available"),
            "contributions": data.get("contributions", []),
            "results": data.get("results", "Not available"),
            "applications": data.get("applications", "Not available"),
            "limitations": data.get("limitations", "Not available"),
            "future_work": data.get("future_work", "Not available"),
            "metrics": {
                "gain": data.get("metrics", {}).get("gain", 0),
                "s11": data.get("metrics", {}).get("s11", 0),
                "bandwidth": data.get("metrics", {}).get("bandwidth", 0)
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
