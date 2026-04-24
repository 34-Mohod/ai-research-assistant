from groq import Groq
import json
import os
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    else:
        raise ValueError("No JSON found")

def judge_papers(results):

    prompt = f"""
You are an expert RF engineer.

Compare these research papers based on:
- Gain (higher is better)
- S11 (more negative is better)
- Bandwidth (higher is better)

DATA:
{json.dumps(results, indent=2)}

Return ONLY JSON:

{{
  "winner": "Paper X",
  "reason": "short technical explanation",
  "scorecard": {{
    "Paper 1": score,
    "Paper 2": score
  }}
}}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    output = response.choices[0].message.content

    return extract_json(output)
