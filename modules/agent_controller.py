from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_agent(file_path, text):
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

TEXT:
{text[:12000]}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",   # ✅ WORKING MODEL
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content
