import os
import tempfile
import streamlit as st
import google.generativeai as genai
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from docx import Document
from pptx import Presentation
from fpdf import FPDF

# ==============================
# CONFIG
# ==============================
st.set_page_config(page_title="AI Quiz Generator Pro", layout="wide")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state in one go
for key, val in {
    "quiz": [], "quiz_generated": False, "theme": "Default",
    "num_mcqs": 5, "num_tf": 5, "difficulty": "Medium"
}.items():
    st.session_state.setdefault(key, val)

# ==============================
# THEMES
# ==============================
THEMES = {
    "Default": {"bg": "#f5f5f5", "card": "#ffffff", "primary": "#4CAF50", "accent": "#45a049"},
    "Midnight Blue": {"bg": "#0f172a", "card": "#1e293b", "primary": "#3b82f6", "accent": "#2563eb"},
    "Crimson Red": {"bg": "#fef2f2", "card": "#fee2e2", "primary": "#dc2626", "accent": "#b91c1c"},
    "Emerald Green": {"bg": "#f0fdf4", "card": "#dcfce7", "primary": "#10b981", "accent": "#059669"},
    "Royal Purple": {"bg": "#f5f3ff", "card": "#ede9fe", "primary": "#8b5cf6", "accent": "#7c3aed"},
}
CSS_TEMPLATE = """
<style>
.stApp {{ background-color: {bg}; }}
div[data-testid="stExpander"], .stSelectbox, .stTextInput, .stNumberInput {{
    background-color: {card}; border-radius: 12px; padding: 10px; margin: 5px 0;
}}
.stButton>button {{
    background-color: {primary}; color: white; border-radius: 8px; padding: 8px 16px;
}}
.stButton>button:hover {{ background-color: {accent}; }}
</style>
"""
st.markdown(CSS_TEMPLATE.format(**THEMES[st.session_state.theme]), unsafe_allow_html=True)

# ==============================
# HELPERS
# ==============================
def extract_text(file):
    """Extract text from PDF, DOCX, or TXT with progress bar."""
    text, ext = "", file.name.lower().split(".")[-1]
    with st.progress(0, text="Extracting content...") as prog:
        if ext == "pdf":
            for i, el in enumerate(partition_pdf(filename=file.name)):
                text += str(el) + "\n"; prog.progress((i+1)/10)
        elif ext == "docx":
            for i, el in enumerate(partition_docx(filename=file.name)):
                text += str(el) + "\n"; prog.progress((i+1)/10)
        elif ext == "txt":
            text = file.read().decode("utf-8")
        else:
            st.error("Unsupported file type")
    return text.strip()

def generate_quiz(text, n_mcq, n_tf, difficulty):
    """Generate quiz using Gemini AI."""
    prompt = f"""
    Create a quiz from the following text with:
    - {n_mcq} Multiple Choice Questions (A–D, only one correct)
    - {n_tf} True/False
    - Difficulty: {difficulty}
    Provide format:
    MCQ:
    Q1. Question?
    A.
    B.
    C.
    D.
    Answer: X
    TF:
    Q1. Statement?
    Answer: True/False
    """
    return genai.GenerativeModel("gemini-pro").generate_content(prompt + text).text

def export_quiz(quiz, fmt):
    """Export quiz to PDF/DOCX/TXT."""
    if fmt == "pdf":
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
        [pdf.multi_cell(0, 10, q) for q in quiz]
        return pdf.output(dest="S").encode("latin-1")
    elif fmt == "docx":
        doc = Document(); [doc.add_paragraph(q) for q in quiz]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name); return open(tmp.name, "rb").read()
    else:
        return "\n\n".join(quiz).encode("utf-8")

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.image("https://img.icons8.com/?size=100&id=IQJ0OnhOPcRQ&format=png", width=100)
    st.title("⚙️ Controls")
    st.session_state.theme = st.selectbox("🎨 Theme", list(THEMES))
    st.session_state.num_mcqs = st.number_input("📝 MCQs", 1, 20, st.session_state.num_mcqs)
    st.session_state.num_tf = st.number_input("✔️ True/False", 1, 20, st.session_state.num_tf)
    st.session_state.difficulty = st.selectbox("📊 Difficulty", ["Easy","Medium","Hard"],
                                               index=["Easy","Medium","Hard"].index(st.session_state.difficulty))

# ==============================
# MAIN UI
# ==============================
st.title("🧠 AI Quiz Generator Pro")
st.write("Upload material → Generate quiz → Preview & Export")

uploaded = st.file_uploader("📂 Upload File (PDF/DOCX/TXT)", type=["pdf","docx","txt"])
if uploaded and st.button("🚀 Generate Quiz"):
    txt = extract_text(uploaded)
    if txt:
        with st.spinner("Generating quiz..."):
            q = generate_quiz(txt, st.session_state.num_mcqs, st.session_state.num_tf, st.session_state.difficulty)
            st.session_state.quiz = q.splitlines(); st.session_state.quiz_generated = True
            st.success("✅ Quiz ready!")

if st.session_state.quiz_generated:
    st.subheader("📋 Preview")
    st.text_area("", "\n".join(st.session_state.quiz), height=400)

    st.subheader("💾 Export")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ PDF", data=export_quiz(st.session_state.quiz,"pdf"), file_name="quiz.pdf")
    with c2:
        st.download_button("⬇️ DOCX", data=export_quiz(st.session_state.quiz,"docx"), file_name="quiz.docx")
    with c3:
        st.download_button("⬇️ TXT", data=export_quiz(st.session_state.quiz,"txt"), file_name="quiz.txt")
