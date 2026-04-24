from modules.agent_controller import run_agent

file = open("your_pdf.pdf", "rb")

result = run_agent(file)

print(result)
