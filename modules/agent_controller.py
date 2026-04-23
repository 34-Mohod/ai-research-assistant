from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text
import json


# ---------------- AGENT 1 ----------------
class ResearchAgent:
    """
    Performs core research analysis (LLM reasoning)
    """

    def run(self, text):

        prompt = f"""
You are an expert RF research analyst.

Analyze the paper and return STRICT JSON ONLY.

NO markdown. NO explanation.

FORMAT:

{{
"title": "",
"summary": "",
"contributions": [],
"methodology": "",
"results": "",
"metrics": {{
    "gain": null,
    "s11": null,
    "bandwidth": null
}}
}}

RULES:
- Gain in dBi
- S11 in dB
- Bandwidth in %
- contributions must be list

Paper:
{text}
"""

        return summarize_text(prompt)


# ---------------- AGENT 2 ----------------
class CriticAgent:
    """
    Validates and refines output
    """

    def review(self, response):

        try:
            data = json.loads(response)

            # basic validation
            if "summary" not in data or not data["summary"]:
                return json.dumps({"error": "Missing summary"})

            return response

        except:
            return json.dumps({"error": "Invalid JSON from model"})


# ---------------- AGENT 3 ----------------
class FormatterAgent:
    """
    Final formatting / cleanup
    """

    def format(self, response):

        try:
            data = json.loads(response)

            # clean values
            for key in data:
                if isinstance(data[key], str):
                    data[key] = data[key].strip()

            return json.dumps(data)

        except:
            return response


# ---------------- COORDINATOR ----------------
class CoordinatorAgent:
    """
    Orchestrates multiple agents
    """

    def __init__(self):
        self.research_agent = ResearchAgent()
        self.critic_agent = CriticAgent()
        self.formatter_agent = FormatterAgent()

    def run(self, file_path):

        try:
            # Step 1: Extract
            text = extract_text(file_path)

            if not text.strip():
                return json.dumps({"error": "Empty PDF"})

            # Step 2: Research
            response = self.research_agent.run(text)

            # Step 3: Critic
            reviewed = self.critic_agent.review(response)

            # Step 4: Formatter
            final_output = self.formatter_agent.format(reviewed)

            return final_output

        except Exception as e:
            return json.dumps({"error": str(e)})


# ---------------- ENTRY FUNCTION ----------------
def run_agent(file_path):
    coordinator = CoordinatorAgent()
    return coordinator.run(file_path)
