# Task Decomposition

## Input
- PDF file uploaded by user

## Processing Steps

1. UI Layer
   - Upload PDF
   - Trigger processing

2. PDF Processing
   - Extract text using PyMuPDF

3. LLM Processing
   - Send text to Groq API
   - Apply structured prompt

4. Output Structuring
   - Generate formatted sections

5. Display
   - Show results in UI
   - Allow download

## Output
- Structured research summary
