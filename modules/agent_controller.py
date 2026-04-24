import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_agent(file):
    try:
        text = file.read().decode("latin-1", errors="ignore")[:4000]

        prompt = f"""
Extract structured data from this research paper.

Return ONLY JSON:
{{
 "title": "...",
 "summary": "...",
 "methodology": "...",
 "contributions": ["..."],
 "results": "...",
 "metrics": {{
    "gain": number,
    "s11": number,
    "bandwidth": number
 }}
}}

{text}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return json.dumps({
            "title": "Fallback",
            "summary": "Fallback summary",
            "methodology": "N/A",
            "contributions": [],
            "results": "N/A",
            "metrics": {"gain": 0, "s11": 0, "bandwidth": 0}
        })
