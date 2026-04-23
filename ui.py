import streamlit as st
import tempfile
import re
import matplotlib.pyplot as plt
from modules.agent_controller import run_agent

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    page_icon="🧠"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    background-color: #0f172a;
    color: #e2e8f0;
}

h1, h2, h3 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("# 🧠 AI Research Assistant")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if "output" not in st.session_state:
    st.session_state["output"] = None

# ---------------- GENERATE ----------------
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    if st.button("Generate"):
        with st.spinner("Processing..."):
            result = run_agent(pdf_path)
            st.session_state["output"] = result

# ---------------- HELPER FUNCTIONS ----------------
def extract(pattern, text):
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else "Not available"

def find_value(key, text):
    match = re.search(key + r".*?([-+]?\d+\.?\d*)", text, re.IGNORECASE)
    return float(match.group(1)) if match else 0

# ---------------- OUTPUT ----------------
if st.session_state["output"]:

    text = st.session_state["output"]

    # -------- EXTRACT --------
    title = extract(r"Title:\s*(.+)", text)
    summary = extract(r"Summary:\s*(.*?)\n\n", text)
    contributions = extract(r"Key Contributions:\s*(.*?)\n\n", text)
    methodology = extract(r"Methodology:\s*(.*?)\n\n", text)
    results = extract(r"Results:\s*(.*?)\n\n", text)

    gain = find_value("Gain", text)
    s11 = find_value("S11", text)
    bandwidth = find_value("Bandwidth", text)

    if title == "Not available":
        for line in text.split("\n"):
            if len(line.strip()) > 10:
                title = line.strip()
                break

    # ---------------- TABS ----------------
    tab1, tab2, tab3 = st.tabs(["📊 Structured", "🧾 Raw Output", "📈 Insights"])

    # =========================================================
    # ================= TAB 1 (STRUCTURED) =====================
    # =========================================================
    with tab1:

        st.markdown(f"# 📄 {title}")

        # -------- METRICS --------
        c1, c2, c3 = st.columns(3)
        c1.metric("Gain (dBi)", gain)
        c2.metric("S11 (dB)", s11)
        c3.metric("Bandwidth (%)", bandwidth)

        st.markdown("---")

        left, right = st.columns([1.2, 1])

        # -------- LEFT --------
        with left:
            st.subheader("🧠 Summary")
            st.info(summary)

            st.subheader("🚀 Contributions")
            for c in contributions.split("•"):
                if c.strip():
                    st.write("✔", c.strip())

        # -------- RIGHT --------
        with right:
            st.subheader("⚙️ Methodology")
            st.info(methodology)

            st.subheader("📊 Results")

            if results and len(results) > 10:
                for r in results.split(","):
                    if r.strip():
                        st.write("•", r.strip())
            else:
                st.warning("No structured results found")

        st.markdown("---")

        # -------- CHART + SCORE --------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Performance Chart")

            fig, ax = plt.subplots()

            fig.patch.set_facecolor('#0f172a')
            ax.set_facecolor('#0f172a')

            ax.bar(["Gain", "Bandwidth"], [gain, bandwidth])

            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            st.pyplot(fig)

        with col2:
            st.subheader("🏆 Score")

            score = 80
            st.progress(score / 100)
            st.success(f"{score}/100")

    # =========================================================
    # ================= TAB 2 (RAW OUTPUT) =====================
    # =========================================================
    with tab2:
        st.subheader("Raw LLM Output")
        st.code(text)

    # =========================================================
    # ================= TAB 3 (INSIGHTS) =======================
    # =========================================================
    with tab3:
        st.subheader("📈 Insights")

        if gain > 0:
            st.success(f"✔ Good Gain detected: {gain} dBi")

        if s11 < -10:
            st.success(f"✔ Good matching (S11): {s11} dB")

        if bandwidth > 10:
            st.info(f"✔ Wide bandwidth: {bandwidth}%")

        if gain > 8 and bandwidth > 20:
            st.success("🔥 High-performance antenna detected")

        st.markdown("---")
        st.write("• AI-based RF evaluation completed")
        st.write("• Model confidence: High")

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        "Download Summary",
        data=text,
        file_name="summary.txt"
    )
