![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![LLM](https://img.shields.io/badge/LLM-Groq-green)

# 🧠 AI Research Assistant

An AI-powered system to analyze and summarize research papers with structured outputs.

---

## 🚀 Features
- Upload research paper (PDF)
- Extract text using PyMuPDF
- Generate structured summary using LLM (Groq API - LLaMA 3)
- RF-focused analysis (Gain, S11, Bandwidth, Radiation)
- Clean UI using Streamlit
- Downloadable output

---

## 🏗️ Architecture
See architecture diagram below:

![Architecture](architecture.png)

---
## 🎥 Demo Video

Watch the working demo here:  
https://drive.google.com/file/d/1encU9aMi3axmI6CwBVRyPgsHumy_rcvw/view?usp=sharing
## ⚙️ Tech Stack
- Python
- Streamlit
- PyMuPDF
- Groq API (LLaMA 3)

---

## 📊 Output Format
- Title
- Summary
- Key Contributions
- Methodology
- Results
- Limitations
- Future Work

---

## 🌐 Live App
(https://34-mohod-ai-research-assistant-ui-mvxkvq.streamlit.app)

---

## 👨‍💻 Author
Safalya Mohod,
Sharvari Kinkar 

---

## 💡 What makes this unique
- RF-domain specific analysis (not generic summarizer)
- Structured JSON output for engineering workflows
- Extracts key antenna metrics (Gain, S11, Bandwidth)
- Clean Streamlit dashboard for visualization

---

## ⚠️ Limitations
- Dependent on Groq API rate limits
- Large PDFs may be truncated
- JSON parsing depends on LLM output format
- Performance varies with input quality

---

## 🚀 Future Improvements
- Multi-agent system (Analyzer + Evaluator)
- Better PDF parsing (tables, equations)
- Advanced visualization dashboard
- Support for multiple LLM providers

---

## 📁 Project Structure
```
ai-research-assistant/
│
├── ui.py
├── modules/
├── utils/
├── assets/
├── requirements.txt
└── README.md
```

---

## 🖼️ UI Preview
![UI](assets/ui.png)

## 📊 Output Example
![Output](assets/output.png)

