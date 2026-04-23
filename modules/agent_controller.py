from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text


# ---------------- AGENT 1 ----------------
class ResearchAgent:
    """
    Performs core research analysis (LLM reasoning)
    """

    def run(self, text):
        return summarize_text(text)


# ---------------- AGENT 2 ----------------
class CriticAgent:
    """
    Validates and refines output
    """

    def review(self, response):
        # simple validation (can be extended)
        if "Error" in response or len(response.strip()) < 50:
            return "⚠️ Output may be incomplete or low confidence.\n\n" + response
        return response


# ---------------- AGENT 3 ----------------
class FormatterAgent:
    """
    Final formatting / cleanup
    """

    def format(self, response):
        # basic cleanup
        return response.strip()


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
            # Step 1: Perception
            text = extract_text(file_path)

            if not text.strip():
                return "⚠️ No text extracted."

            # Step 2: Research Agent
            raw_output = self.research_agent.run(text)

            # Step 3: Critic Agent
            reviewed_output = self.critic_agent.review(raw_output)

            # Step 4: Formatter Agent
            final_output = self.formatter_agent.format(reviewed_output)

            return final_output

        except Exception as e:
            return f"⚠️ Multi-Agent Error: {str(e)}"


# ---------------- PUBLIC FUNCTION ----------------
def run_agent(file_path):
    agent = CoordinatorAgent()
    return agent.run(file_path)
