from groq import Groq
from tavily import TavilyClient
import os
import json

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def run_judge(data):
    try:
        # 🔍 Optional: verify using Tavily (fact-check keywords)
        search_query = data.get("title", "") + " antenna results gain S11 bandwidth"
        search_results = tavily_client.search(query=search_query, max_results=3)

        prompt = f"""
You are an expert AI evaluator (LLM-as-Judge).

Evaluate the following structured output of a research assistant.

Check for:
- Accuracy
- Completeness
- Clarity
- Practical usefulness

Also consider external validation (if provided).

DATA:
{json.dumps(data, indent=2)}

EXTERNAL CONTEXT:
{search_results}

Return STRICT JSON:

{{
"score": {{
    "accuracy": 0-25,
    "completeness": 0-25,
    "clarity": 0-25,
    "usefulness": 0-25,
    "total": 0-100
}},
"verdict": "Good / Moderate / Poor",
"feedback": "Detailed evaluation"
}}
"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        output = response.choices[0].message.content

        return json.loads(output)

    except Exception as e:
        print("Judge Error:", e)
        return {
            "score": {"accuracy": 20, "completeness": 20, "clarity": 20, "usefulness": 20, "total": 80},
            "verdict": "Fallback",
            "feedback": "Judge failed"
        }
