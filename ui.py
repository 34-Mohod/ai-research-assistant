import streamlit as st
import pandas as pd
import plotly.express as px
from modules.agent_controller import run_agent
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

# ---------------- BACKGROUND ANIMATION ----------------
components.html("""
<canvas id="bg"></canvas>
<script>
const canvas = document.getElementById("bg");
const ctx = canvas.getContext("2d");

canvas.style.position = "fixed";
canvas.style.top = 0;
canvas.style.left = 0;
canvas.style.zIndex = -1;

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resize();
window.addEventListener("resize", resize);

let particles = [];
for (let i = 0; i < 40; i++) {
    particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        r: Math.random() * 2,
        dx: (Math.random() - 0.5) * 0.3,
        dy: (Math.random() - 0.5) * 0.3
    });
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
        p.x += p.dx;
        p.y += p.dy;

        if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(0,0,0,0.06)";
        ctx.fill();
    });

    requestAnimationFrame(draw);
}
draw();
</script>
""", height=0)

# ---------------- CSS ----------------
st.markdown("""
<style>
html, body {
    background-color: #FAFAFA;
    font-family: Inter, system-ui;
}

.main {
    max-width: 1100px;
    margin: auto;
}

/* HERO */
.hero {
    text-align: center;
    padding: 50px 0;
    animation: fadeUp 0.6s ease;
}

.hero h1 {
    font-size: 42px;
    color: #111827;
}

.hero p {
    color: #6B7280;
}

/* BUTTON */
.stButton>button {
    border-radius: 999px;
    padding: 10px 20px;
    background: #111827;
    color: white;
    border: none;
    transition: 0.2s ease;
}

.stButton>button:hover {
    transform: scale(1.03);
}

/* UPLOAD */
.upload-box {
    background: white;
    border: 2px dashed #E5E7EB;
    border-radius: 16px;
    padding: 30px;
    text-align: center;
}

/* METRIC */
.metric {
    background: white;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid #E5E7EB;
}

.metric h1 {
    font-size: 36px;
    margin: 0;
}

.metric p {
    color: #6B7280;
}

/* SECTION */
.section {
    background: white;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #E5E7EB;
    margin-top: 20px;
}

/* ANIMATION */
@keyframes fadeUp {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
<h1>AI Research Assistant</h1>
<p>Analyze research papers with AI instantly</p>
</div>
""", unsafe_allow_html=True)

# ---------------- UPLOAD ----------------
st.markdown('<div class="upload-box">Upload PDF files</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    " ",
    type=["pdf"],
    accept_multiple_files=True
)

generate = st.button("🚀 Generate Summary")

# ---------------- PROCESS ----------------
results = []

def extract_text(file):
    import PyPDF2
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

if generate and uploaded_files:
    with st.spinner("Processing..."):
        for file in uploaded_files:
            text = extract_text(file)
            data = run_agent(text)
            results.append(data)

# ---------------- OUTPUT ----------------
if results:
    data = results[-1]
    metrics = data["metrics"]

    c1, c2, c3 = st.columns(3)

    c1.markdown(f"<div class='metric'><p>Gain</p><h1>{metrics['gain']}</h1></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric'><p>S11</p><h1>{metrics['s11']}</h1></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric'><p>Bandwidth</p><h1>{metrics['bandwidth']}</h1></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='section'><h3>Summary</h3><p>{data['summary']}</p></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='section'><h3>Methodology</h3><p>{data['methodology']}</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='section'><h3>Contributions</h3>", unsafe_allow_html=True)
    for c in data["contributions"]:
        st.write(f"• {c}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='section'><h3>Results</h3><p>{data['results']}</p></div>", unsafe_allow_html=True)
