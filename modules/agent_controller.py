from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text


# ---------------- AGENT 1 ----------------
class ResearchAgent:
    def run(self, text):
        return summarize_text(text)


# ---------------- AGENT 2 ----------------
class CriticAgent:
    def review(self, data):
        try:
            # already dict (IMPORTANT)
            if "error" in data:
                return data

            if not data.get("summary"):
                data["summary"] = "Summary not generated"

            if not data.get("metrics"):
                data["metrics"] = {
                    "gain": None,
                    "s11": None,
                    "bandwidth": None
                }

            return data

        except Exception as e:
            return {
                "error": "Processing failed",
                "details": str(e)
            }


# ---------------- AGENT 3 ----------------
class FormatterAgent:
    def format(self, data):
        return data


# ---------------- COORDINATOR ----------------
class CoordinatorAgent:
    def __init__(self):
        self.research = ResearchAgent()
        self.critic = CriticAgent()
        self.formatter = FormatterAgent()

    def run(self, file_path):
        text = extract_text(file_path)

        if not text or len(text.strip()) < 50:
            return {"error": "Empty or unreadable PDF"}

        response = self.research.run(text)
        response = self.critic.review(response)
        response = self.formatter.format(response)

        return response


# ---------------- ENTRY FUNCTION ----------------
def run_agent(file_path):
    agent = CoordinatorAgent()
    return agent.run(file_path)
