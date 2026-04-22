import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from modules.pdf_extractor import extract_text
from modules.agent_controller import run_agent

pdf_path = "data/sample.pdf"

print("\nExtracting text...\n")

text = extract_text(pdf_path)

print("\nRunning AI Agent...\n")

result = run_agent(text)

print("\nFINAL OUTPUT:\n")
import json
print(json.dumps(result, indent=2))