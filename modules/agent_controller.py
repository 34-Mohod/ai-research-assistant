from modules.pdf_extractor import extract_text
from modules.llm_engine import summarize_text


class PerceptionModule:
    """
    Handles input understanding (PDF → text)
    """

    def __init__(self):
        pass

    def process(self, file_path):
        text = extract_text(file_path)

        if not text or len(text.strip()) == 0:
            raise ValueError("No readable text found in PDF.")

        return text


class ReasoningModule:
    """
    Handles core intelligence (LLM reasoning)
    """

    def __init__(self):
        pass

    def analyze(self, text):
        # You can extend here later (multi-prompt, chain, etc.)
        response = summarize_text(text)
        return response


class ActionModule:
    """
    Handles output formatting / delivery
    """

    def __init__(self):
        pass

    def format(self, response):
        # Future: post-processing, structuring, validation
        return response


class ResearchAgent:
    """
    Main Agent Controller
    """

    def __init__(self):
        self.perception = PerceptionModule()
        self.reasoning = ReasoningModule()
        self.action = ActionModule()

    def run(self, file_path):
        try:
            # Step 1: Perception
            text = self.perception.process(file_path)

            # Step 2: Reasoning
            response = self.reasoning.analyze(text)

            # Step 3: Action
            output = self.action.format(response)

            return output

        except Exception as e:
            return f"⚠️ Agent Error: {str(e)}"


# -------- PUBLIC FUNCTION (UI CALLS THIS) --------
def run_agent(file_path):
    agent = ResearchAgent()
    return agent.run(file_path)
