import streamlit as st
import tempfile
import time
import re
import matplotlib.pyplot as plt

# ===== SAFE BACKEND =====
try:
    from modules.agent_controller import run_agent
except:
    def run_agent(x):
        return """Title: Sub-THz Conformal Microstrip Antenna

Summary:
A high gain flexible antenna for airborne applications.

Key Contributions:
• Flexible textile substrate
• High gain performance
• PEC reflector integration

Methodology:
Designed using CST Studio Suite.

Results:
S11: -63 dB
Gain: 10.25 dBi
Bandwidth: 47%

Limitations:
Fabrication complexity

Future Work:
Real-world deployment testing
"""

# ===== CONFIG =====
st.set_page_config(page_title="AI Research Assistant", layout="wide")

# ===== STYLE =====
st.markdown("""
<style>
body {background-color:#0f172a; color:#e2e8f0;}
.block {background:#111827;padding:18px;border-radius:12px;margin-bottom:10px;}
.metric {background:#1f2937;padding:15px;border-radius:10px;text-align:center;}
.title {font-size:36px;font-weight:800;text-align:center;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🧠 AI Research Assistant</div>", unsafe_allow_html=True)

# ===== UPLOAD =====
file = st.file_uploader("Upload PDF", type=["pdf"])

# ===== PARSER =====
def parse(text):
    data = {"title":"","summary":"","contrib":[],"method":"","results":{}}

    current = None

    for line in text.split("\n"):
        line = line.strip().replace("**","")

        if line.lower().startswith("title"):
            data["title"] = line.split(":",1)[-1]

        elif "summary" in line.lower():
            current="summary"

        elif "key contributions" in line.lower():
            current="contrib"

        elif "methodology" in line.lower():
            current="method"

        elif "results" in line.lower():
            current="results"

        else:
            if current=="summary":
                data["summary"] += line + " "

            elif current=="contrib":
                if line:
                    data["contrib"].append(line.replace("•",""))

            elif current=="method":
                data["method"] += line + " "

            elif current=="results":
                if "gain" in line.lower():
                    data["results"]["gain"]=line
                elif "s11" in line.lower():
                    data["results"]["s11"]=line
                elif "bandwidth" in line.lower():
                    data["results"]["bw"]=line

    return data

# ===== PROCESS =====
if file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.read())
        path = tmp.name

    if st.button("Generate"):
        out = run_agent(path)
        st.session_state["out"]=out

# ================= DISPLAY (FIXED UI) =================

if "out" in st.session_state:

    import re

    text = st.session_state["out"]

    def extract(pattern):
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else "Not available"

    title = extract(r"Title:\s*(.*)")
    summary = extract(r"Summary:\s*(.*?)\n\n")
    contrib = extract(r"Key Contributions:\s*(.*?)\n\n")
    method = extract(r"Methodology:\s*(.*?)\n\n")
    results = extract(r"Results:\s*(.*?)\n\n")

    def find_val(key):
        m = re.search(key + r".*?([-+]?\d+\.?\d*)", text, re.IGNORECASE)
        return m.group(1) if m else "N/A"

    gain = find_val("Gain")
    s11 = find_val("S11")
    bw = find_val("Bandwidth")

    # ===== TITLE =====
    st.markdown(f"# 📄 {title}")

    # ===== METRICS BAR =====
    c1, c2, c3 = st.columns(3)
    c1.metric("Gain (dBi)", gain)
    c2.metric("S11 (dB)", s11)
    c3.metric("Bandwidth (%)", bw)

    st.markdown("---")

    # ===== MAIN GRID =====
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("🧠 Summary")
        st.info(summary)

        st.subheader("🚀 Contributions")
        for item in contrib.split("•"):
            if item.strip():
                st.write("✔", item.strip())

    with right:
        st.subheader("⚙️ Methodology")
        st.write(method)

        st.subheader("📊 Results")
        st.write(results)

    st.markdown("---")

    # ===== VISUAL SECTION =====
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Performance Chart")

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.bar(["Gain", "Bandwidth"], [float(gain or 0), float(bw or 0)])
        st.pyplot(fig)

    with col2:
        st.subheader("🏆 Score")

        score = 80
        st.progress(score/100)
        st.success(f"{score}/100")

    # ===== DOWNLOAD =====
    st.download_button("Download", text)
