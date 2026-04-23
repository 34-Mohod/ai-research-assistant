import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_text(text):

    text = text[:4000]

    prompt = f"""
You are an RF research expert.

Return STRICT JSON ONLY.

FORMAT:
{{
"title": "string",
"summary": "2-3 line technical summary",
"contributions": ["point1","point2"],
"methodology": "short explanation",
"results": "short result summary",
"metrics": {{
  "gain": number,
  "s11": number,
  "bandwidth": number
}}
}}

RULES:
- NO markdown
- NO explanation
- NO empty fields
- If not found → estimate realistic values

TEXT:
{text}
"""

    try:
        res = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        output = res.choices[0].message.content.strip()

        # 🔥 CLEAN JSON
        start = output.find("{")
        end = output.rfind("}") + 1
        clean = output[start:end]

        json.loads(clean)  # validate

        return clean

    except Exception as e:
        return json.dumps({
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
        })

