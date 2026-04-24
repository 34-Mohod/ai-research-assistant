import json
from groq import Groq

client = Groq(api_key="YOUR_API_KEY")

def run_agent(pdf_path):
    try:
        prompt = """
        Extract research paper info STRICTLY in JSON:

        {
          "title": "...",
          "summary": "...",
          "contributions": [],
          "methodology": "...",
          "results": "...",
          "metrics": {
            "gain": number,
            "s11": number,
            "bandwidth": number
          }
        }

        RULES:
        - Only JSON
        - Double quotes
        - No explanation
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ stable model  [oai_citation:0‡console.groq.com](https://console.groq.com/docs/models?utm_source=chatgpt.com)
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # 🔥 Force JSON safe
        content = content.replace("'", '"')

        data = json.loads(content)

        # 🔥 GUARANTEE structure
        return {
            "title": data.get("title", ""),
            "summary": data.get("summary", ""),
            "contributions": data.get("contributions", []),
            "methodology": data.get("methodology", ""),
            "results": data.get("results", ""),
            "metrics": data.get("metrics", {})
        }

    except Exception as e:
        print("Agent error:", e)

        return {
            "title": "Error",
            "summary": "",
            "contributions": [],
            "methodology": "",
            "results": "",
            "metrics": {}
        }
