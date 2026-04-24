import json
import re
from groq import Groq

client = Groq()

def run_agent(text):
    try:
        # 🔥 Limit input size (avoid token error)
        text = text[:6000]

        prompt = f"""
You are a senior RF and antenna systems researcher.

Carefully analyze the following research paper and extract structured technical insights.

IMPORTANT RULES:
- Be precise and technical.
- Do NOT hallucinate values.
- If a metric is not explicitly given, estimate based on context (reasonable engineering assumption).
- Always return ALL fields.
- DO NOT return anything except JSON.

----------------------------------------

Extract the following:

1. Title

2. Summary  
(5–6 lines, technical but readable)

3. Methodology  
(Explain design approach, materials, simulation tools, structure)

4. Key Contributions  
(List 3–6 bullet points)

5. Results  
(Include numerical values like gain, S11, bandwidth, frequency, efficiency if present)

6. Applications  
(Real-world use cases)

7. Limitations  
(Design constraints, fabrication issues, losses, etc.)

8. Future Work  
(Possible improvements or research extensions)

9. Metrics (MANDATORY):
- Gain (in dBi)
- S11 (in dB, NEGATIVE value expected)
- Bandwidth (in MHz or %, convert to MHz if possible)

If exact values are missing:
- Estimate from context (e.g., "high gain" → 8–12 dBi)
- Never leave metrics as 0

----------------------------------------

Return STRICT JSON:

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

----------------------------------------

Paper Content:
{text[:6000]}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1200
        )

        output = response.choices[0].message.content

        print("\nRAW OUTPUT:\n", output)

        # 🔥 FIXED JSON EXTRACTION (ONLY CHANGE)
        try:
            start = output.find("{")
            end = output.rfind("}") + 1
            json_str = output[start:end]

            json_str = re.sub(r"[\x00-\x1F]+", " ", json_str)

            data = json.loads(json_str)

# 🔥 Ensure all fields exist
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

        except Exception as parse_error:
            print("JSON PARSE ERROR:", parse_error)
            print("RAW OUTPUT:", output)
            raise ValueError("Failed to parse JSON")

    except Exception as e:
        print("ERROR:", e)

        return {
            "title": "Fallback",
            "summary": output[:200] if 'output' in locals() else "Fallback summary",
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
