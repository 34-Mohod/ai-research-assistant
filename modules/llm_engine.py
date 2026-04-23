import os
import json
from groq import Groq

# Initialize client using environment variable
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_text(text):
    text = text[:3000]

    prompt = f"""
You are an expert RF antenna research analyst.

Return STRICT JSON ONLY.

FORMAT:
{{
"title": "string",
"summary": "2-3 line summary",
"contributions": ["point1","point2","point3"],
"methodology": "short explanation",
"results": "short result",
"metrics": {{
    "gain": number,
    "s11": number,
    "bandwidth": number
}}
}}

RULES:
- No markdown
- No explanation
- Only JSON
- If value missing → use null

TEXT:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        output = response.choices[0].message.content.strip()

        # Extract JSON safely
        start = output.find("{")
        end = output.rfind("}") + 1

        if start == -1 or end == -1:
            raise ValueError("Invalid JSON from LLM")

        clean_json = output[start:end]

        return json.loads(clean_json)

    except Exception as e:
        print("LLM ERROR:", e)
        return {
            "title": "Error",
            "summary": "LLM failed",
            "contributions": [],
            "methodology": "",
            "results": "",
            "metrics": {
                "gain": None,
                "s11": None,
                "bandwidth": None
            }
        }
