# modules/agent_controller.py

from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text
import json

# ---------------- AGENT 1 ----------------
class ResearchAgent:
    """
    Performs core research analysis (LLM reasoning)
    """

    def run(self, text):
        # ✅ FIX: Send raw text, NOT custom prompt
        return summarize_text(text)


# ---------------- AGENT 2 ----------------
class CriticAgent:
    """
    Validates and refines output
    """

    def review(self, response):
        try:
            data = json.loads(response)

            # if LLM returned error
            if "error" in data:
                return response

            # basic validation
            if not data.get("summary"):
                data["summary"] = "Summary not generated"

            if not data.get("metrics"):
                data["metrics"] = {
                    "gain": None,
                    "s11": None,
                    "bandwidth": None
                }

            return json.dumps(data)

        except:
            # fallback if not valid JSON
            return json.dumps({
                "error": "Invalid JSON from LLM",
                "raw": response
            })


# ---------------- AGENT 3 ----------------
class FormatterAgent:
    """
    Final cleanup
    """

    def format(self, response):
        return response.strip()


# ---------------- COORDINATOR ----------------
class CoordinatorAgent:
    """
    Orchestrates full pipeline
    """

    def __init__(self):
        self.research = ResearchAgent()
        self.critic = CriticAgent()
        self.formatter = FormatterAgent()

    def run(self, file_path):

        # Step 1: Extract text
        text = extract_text(file_path)

        if not text or len(text.strip()) < 50:
            return json.dumps({
                "error": "Empty or unreadable PDF"
            })

        # Step 2: LLM analysis
        response = self.research.run(text)

        # Step 3: Validation
        response = self.critic.review(response)

        # Step 4: Cleanup
        response = self.formatter.format(response)

        return response


# ---------------- ENTRY FUNCTION ----------------
def run_agent(file_path):
    agent = CoordinatorAgent()
    return agent.run(file_path)
