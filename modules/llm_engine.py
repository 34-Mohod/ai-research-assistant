import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def summarize_text(text):
    text = text[:3000]

    prompt = f"""
You are an RF antenna research expert.

Return STRICT JSON ONLY.

FORMAT:
{{
  "title": "string",
  "summary": "2-3 lines",
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
- If missing → use null

TEXT:
{text}
"""

    try:
        response = client.chat.completions.create(
            model = "llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        output = response.choices[0].message.content.strip()

        # extract JSON safely
        start = output.find("{")
        end = output.rfind("}") + 1
        clean = output[start:end]

        return json.loads(clean)

    except Exception as e:
        return {
            "error": "LLM failed",
            "details": str(e)
        }
