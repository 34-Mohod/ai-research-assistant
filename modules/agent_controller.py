import json
import re
from groq import Groq

client = Groq()

def run_agent(text):
    try:
        # 🔥 Limit input size (avoid token error)
        text = text[:6000]

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

        print("\nRAW OUTPUT:\n", output)

        # 🔥 Extract JSON safely
        match = re.search(r"\{.*\}", output, re.DOTALL)

        if match:
            json_str = match.group(0)

            # 🔥 Clean invalid characters
            json_str = re.sub(r"[\x00-\x1F]+", " ", json_str)

            data = json.loads(json_str)
            return data
        else:
            raise ValueError("No JSON found")

    except Exception as e:
        print("ERROR:", e)

        return {
            "title": "Fallback",
            "summary": "Fallback summary",
            "methodology": "Fallback methodology",
            "contributions": [],
            "results": "Fallback results",
            "metrics": {
                "gain": 10,
                "s11": -20,
                "bandwidth": 30
            }
        }
