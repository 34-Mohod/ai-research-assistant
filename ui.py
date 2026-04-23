# ==============================
# AI RESEARCH ASSISTANT - PRO UI
# ==============================

import streamlit as st
import tempfile
import time
import json
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any

# -----------------------------
# External (your backend)
# -----------------------------
try:
    from modules.agent_controller import run_agent
except Exception:
    # graceful fallback if import fails (keeps UI usable)
    def run_agent(path: str) -> str:
        return "⚠️ Backend not available. Please fix modules/agent_controller import."

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Research Assistant Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# GLOBAL STATE
# -----------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []
if "settings" not in st.session_state:
    st.session_state.settings = {
        "mode": "Technical",
        "creativity": 0.3,
        "theme": "Dark",
        "show_logs": True,
        "auto_parse": True,
    }

# -----------------------------
# THEME / CSS
# -----------------------------
DARK = """
<style>
:root{
  --bg:#0b1220; --card:#0f172a; --muted:#94a3b8; --text:#e5e7eb;
  --accent:#6366f1; --accent2:#22c55e; --border:#1f2937;
}
body{background:var(--bg); color:var(--text);}
.title{font-size:40px;font-weight:800;text-align:center;color:#c7d2fe;}
.subtitle{text-align:center;color:var(--muted);margin-bottom:18px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;}
.small{color:var(--muted);font-size:12px;}
.badge{padding:4px 8px;border-radius:8px;border:1px solid var(--border);margin-right:6px;}
.ok{color:#22c55e;} .warn{color:#eab308;} .err{color:#ef4444;}
.stButton>button{background:linear-gradient(90deg,#6366f1,#3b82f6);color:white;border:none;border-radius:10px;height:44px;font-weight:600;}
.section-title{font-weight:700;color:#c7d2fe;margin:8px 0;}
hr{border:0;border-top:1px solid var(--border);}
</style>
"""

LIGHT = """
<style>
:root{
  --bg:#f8fafc; --card:#ffffff; --muted:#475569; --text:#0f172a;
  --accent:#4f46e5; --accent2:#16a34a; --border:#e5e7eb;
}
body{background:var(--bg); color:var(--text);}
.title{font-size:40px;font-weight:800;text-align:center;color:#4338ca;}
.subtitle{text-align:center;color:var(--muted);margin-bottom:18px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;}
.small{color:var(--muted);font-size:12px;}
.badge{padding:4px 8px;border-radius:8px;border:1px solid var(--border);margin-right:6px;}
.ok{color:#16a34a;} .warn{color:#ca8a04;} .err{color:#dc2626;}
.stButton>button{background:linear-gradient(90deg,#4f46e5,#2563eb);color:white;border:none;border-radius:10px;height:44px;font-weight:600;}
.section-title{font-weight:700;color:#4338ca;margin:8px 0;}
hr{border:0;border-top:1px solid var(--border);}
</style>
"""

st.markdown(DARK if st.session_state.settings["theme"] == "Dark" else LIGHT, unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="title">AI Research Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a research paper → get structured insights + RF signals</div>', unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.settings["mode"] = st.selectbox(
        "Mode", ["Technical", "Simple"], index=0 if st.session_state.settings["mode"]=="Technical" else 1
    )
    st.session_state.settings["creativity"] = st.slider(
        "Creativity", 0.0, 1.0, st.session_state.settings["creativity"], 0.05
    )
    st.session_state.settings["theme"] = st.selectbox(
        "Theme", ["Dark", "Light"], index=0 if st.session_state.settings["theme"]=="Dark" else 1
    )
    st.session_state.settings["auto_parse"] = st.checkbox("Auto Parse Sections", st.session_state.settings["auto_parse"])
    st.session_state.settings["show_logs"] = st.checkbox("Show Logs", st.session_state.settings["show_logs"])

    st.markdown("---")
    st.markdown("**Model**: LLaMA3 (Groq)")
    st.markdown("**Status**: <span class='ok'>Active</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📜 History")
    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history[-8:]), 1):
            st.markdown(f"{i}. {h['name']} <span class='small'>({h['time']})</span>", unsafe_allow_html=True)
    else:
        st.write("No history yet")

# -----------------------------
# UTILITIES
# -----------------------------
@st.cache_data(show_spinner=False)
def read_bytes(file) -> bytes:
    return file.read()

def now_str() -> str:
    return datetime.now().strftime("%H:%M:%S")

def log(msg: str):
    if st.session_state.settings["show_logs"]:
        st.write(f"🧩 {msg}")

# -----------------------------
# SMART PARSER
# -----------------------------
SECTION_HINTS = [
    "title", "summary", "abstract",
    "introduction", "background",
    "method", "methodology", "approach", "proposed",
    "results", "evaluation", "performance",
    "discussion",
    "contribution", "contributions",
    "limitation", "limitations",
    "future", "future work", "future scope",
    "conclusion"
]

def is_section_header(line: str) -> bool:
    l = line.lower().strip()
    if not l:
        return False
    # heuristic: short prefix + colon OR contains strong keywords
    if ":" in l and len(l.split(":")[0]) < 40:
        return True
    return any(k in l for k in SECTION_HINTS)

def normalize_header(line: str) -> str:
    l = line.strip()
    if ":" in l:
        key = l.split(":", 1)[0].strip()
    else:
        key = l.strip()
    return key.title()

def parse_output(output: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = defaultdict(list)
    current = "General"
    sections[current] = []

    lines = [x.strip() for x in output.split("\n") if x.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        if is_section_header(line):
            key = normalize_header(line)
            current = key
            if current not in sections:
                sections[current] = []

            # capture inline content after colon
            if ":" in line:
                rest = line.split(":", 1)[1].strip()
                if rest:
                    sections[current].append(rest)
            else:
                # capture following paragraph lines until next header
                j = i + 1
                while j < len(lines) and not is_section_header(lines[j]):
                    sections[current].append(lines[j])
                    j += 1
                i = j - 1
        else:
            sections[current].append(line)

        i += 1

    return sections

# -----------------------------
# RF INSIGHTS ENGINE
# -----------------------------
RF_PATTERNS = {
    "gain": r"\b(gain)\b",
    "s11": r"\b(s11|return loss)\b",
    "bandwidth": r"\b(bandwidth)\b",
    "radiation": r"\b(radiation|pattern)\b",
    "efficiency": r"\b(efficiency)\b",
    "frequency": r"\b(ghz|mhz|thz)\b",
}

def rf_insights(text: str) -> Tuple[Dict[str, bool], int]:
    flags = {}
    score = 0
    for k, pat in RF_PATTERNS.items():
        found = bool(re.search(pat, text, re.I))
        flags[k] = found
        score += int(found)
    return flags, score

# -----------------------------
# METRICS / SUMMARY CARDS
# -----------------------------
def render_metrics(flags: Dict[str, bool], score: int):
    cols = st.columns(6)
    items = list(flags.items())
    for i, (k, v) in enumerate(items[:6]):
        with cols[i]:
            st.markdown(
                f"<div class='card'><div class='small'>{k.upper()}</div>"
                f"<div class='{ 'ok' if v else 'err' }'>{'Detected' if v else '—'}</div></div>",
                unsafe_allow_html=True
            )
    st.markdown("<br/>", unsafe_allow_html=True)
    st.progress(score / max(len(flags), 1))
    if score >= 4:
        st.success(f"High technical richness ({score}/{len(flags)})")
    elif score >= 2:
        st.warning(f"Moderate technical depth ({score}/{len(flags)})")
    else:
        st.error(f"Low RF signal density ({score}/{len(flags)})")

# -----------------------------
# RENDER SECTION
# -----------------------------
def render_section(title: str, content: List[str]):
    with st.expander(title, expanded=True):
        if any(k in title.lower() for k in ["contribution", "result"]):
            for line in content:
                st.markdown(f"- {line.replace('•','').strip()}")
        else:
            st.write("\n".join(content))

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("📄 Upload Research Paper (PDF)", type=["pdf"])

# -----------------------------
# PROCESS
# -----------------------------
if uploaded_file:
    file_bytes = read_bytes(uploaded_file)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        pdf_path = tmp.name

    st.success("File uploaded")

    colA, colB, colC = st.columns([1,1,2])
    with colA:
        run_btn = st.button("🚀 Generate Summary")
    with colB:
        clear_btn = st.button("🧹 Clear")
    with colC:
        st.caption(f"Size: {len(file_bytes)/1024:.1f} KB")

    if clear_btn:
        st.session_state.result = None
        st.rerun()

    if run_btn:
        log("Starting pipeline")
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress.progress(i + 1)

        output = run_agent(pdf_path)
        st.session_state.result = output

        st.session_state.history.append({
            "name": uploaded_file.name,
            "time": now_str()
        })

        progress.empty()
        log("Completed")

# -----------------------------
# OUTPUT
# -----------------------------
if st.session_state.result:
    output = st.session_state.result

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Structured",
        "🧾 Raw",
        "📈 RF Insights",
        "📦 Export"
    ])

    # -------- TAB 1 --------
    with tab1:
        if st.session_state.settings["auto_parse"]:
            data = parse_output(output)
            for title, content in data.items():
                render_section(title, content)
        else:
            st.write(output)

    # -------- TAB 2 --------
    with tab2:
        st.code(output)

    # -------- TAB 3 --------
    with tab3:
        flags, score = rf_insights(output)
        render_metrics(flags, score)

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("🔍 Detected Signals")
        for k, v in flags.items():
            st.write(f"{'✔' if v else '—'} {k}")

    # -------- TAB 4 --------
    with tab4:
        st.subheader("Export Options")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 Download TXT",
                data=output,
                file_name="summary.txt"
            )

        with col2:
            try:
                data = parse_output(output)
                st.download_button(
                    "📥 Download JSON",
                    data=json.dumps(data, indent=2),
                    file_name="summary.json"
                )
            except Exception:
                st.warning("Parsing failed for JSON export")

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("📋 Copy")
        st.text_area("Copy Output", output, height=200)

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown(
    "<div class='small' style='text-align:center'>AI Research Assistant • Built for RF / Antenna Analysis</div>",
    unsafe_allow_html=True
)
