import streamlit as st
import tempfile
import os
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document as DocxDocument
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from docx import Document as DocxWriter
from dotenv import load_dotenv
import re
import time
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Quiz Generator Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
for key, default in {
    'quiz_history': [],
    'total_questions_generated': 0,
    'theme': "Default"
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Theme configurations
THEMES = {
    "Default": {
        "primary": "#4ecdc4", "bg": "#ffffff", "text": "#000000", "card_bg": "#ffffff",
        "sidebar_bg": "#f0f2f6", "button_bg": "#4ecdc4"
    },
    "Dark Mode": {
        "primary": "#bb86fc", "bg": "#1e1e1e", "text": "#ffffff", "card_bg": "#2d2d2d",
        "sidebar_bg": "#2d2d2d", "button_bg": "#bb86fc"
    },
    "Colorful": {
        "primary": "#4ecdc4", "bg": "linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)",
        "text": "#000000", "card_bg": "#ffffff", "sidebar_bg": "#f0f0f0", "button_bg": "#4ecdc4"
    }
}

def apply_theme():
    """Apply theme-based CSS styling"""
    theme = THEMES[st.session_state.theme]
    
    st.markdown(f"""
    <style>
        .stApp {{ background: {theme['bg']}; color: {theme['text']}; }}
        
        /* Sidebar */
        .st-emotion-cache-1wq0z5r, .st-emotion-cache-1wq0z5r > div {{ 
            background-color: {theme['sidebar_bg']} !important; 
        }}
        .st-emotion-cache-1wq0z5r * {{ color: {theme['text']} !important; }}
        
        /* Header - Always black with white text */
        header[data-testid="stHeader"] {{ background-color: #1e1e1e !important; }}
        header[data-testid="stHeader"] *, header[data-testid="stHeader"] svg {{ 
            color: #ffffff !important; fill: #ffffff !important; 
        }}
        
        /* Form elements */
        .stNumberInput input, .stTextArea textarea, .stSelectbox select {{
            color: {theme['text']} !important; background-color: {theme['card_bg']} !important;
        }}
        
        /* Buttons */
        .stButton button {{ 
            color: {theme['text']} !important; background-color: {theme['card_bg']} !important;
            border: 1px solid {theme['primary']} !important;
        }}
        .stButton button:hover {{ background-color: {theme['primary']} !important; color: white !important; }}
        .stButton button[kind="primary"] {{ background-color: {theme['primary']} !important; color: white !important; }}
        
        /* File uploader */
        .stFileUploader > div > div {{ 
            background-color: transparent !important; border: 2px dashed {theme['primary']} !important;
            border-radius: 15px !important; padding: 2rem !important;
        }}
        .stFileUploader button {{ 
            background-color: {theme['button_bg']} !important; color: white !important;
            border: none !important; border-radius: 8px !important;
        }}
        
        /* Animations */
        .main-header {{
            font-size: 3rem; font-weight: bold; text-align: center;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 2rem; animation: glow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ filter: drop-shadow(0 0 5px rgba(78, 205, 196, 0.4)); }}
            to {{ filter: drop-shadow(0 0 20px rgba(78, 205, 196, 0.8)); }}
        }}
        
        .quiz-preview {{
            background: {theme['card_bg']}; border-left: 5px solid {theme['primary']};
            padding: 1.5rem; border-radius: 10px; margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); color: {theme['text']};
        }}
    </style>
    """, unsafe_allow_html=True)

# Apply theme
apply_theme()

# Header
st.markdown('<h1 class="main-header">🧠 AI Quiz Generator Pro</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Dashboard")
    
    # Custom metrics
    col1, col2 = st.columns(2)
    metric_style = f"background-color: {THEMES[st.session_state.theme]['card_bg']}; padding: 1rem; border-radius: 8px; text-align: center; border: 1px solid #4ecdc4;"
    
    with col1:
        st.markdown(f"""
        <div style="{metric_style}">
            <div style="color: {THEMES[st.session_state.theme]['text']}; font-size: 0.875rem; font-weight: 600;">Total Quizzes</div>
            <div style="color: {THEMES[st.session_state.theme]['text']}; font-size: 1.875rem; font-weight: bold;">{len(st.session_state.quiz_history)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="{metric_style}">
            <div style="color: {THEMES[st.session_state.theme]['text']}; font-size: 0.875rem; font-weight: 600;">Questions Generated</div>
            <div style="color: {THEMES[st.session_state.theme]['text']}; font-size: 1.875rem; font-weight: bold;">{st.session_state.total_questions_generated}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quiz history
    if st.session_state.quiz_history:
        st.markdown("### 📝 Recent Quizzes")
        for i, quiz in enumerate(st.session_state.quiz_history[-3:], 1):
            with st.expander(f"Quiz {len(st.session_state.quiz_history) - 3 + i}"):
                st.write(f"**File:** {quiz['filename']}")
                st.write(f"**Date:** {quiz['date']}")
                st.write(f"**Questions:** {quiz['total_questions']}")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    new_theme = st.selectbox("Choose Theme", ["Default", "Dark Mode", "Colorful"], 
                             index=["Default", "Dark Mode", "Colorful"].index(st.session_state.theme))
    show_progress = st.checkbox("Show Progress Animations", value=True)
    
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📁 Upload Your Document")
    st.markdown("*Supports PDF, DOCX, and TXT files*")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

with col2:
    if uploaded_file:
        st.markdown("### 📋 File Information")
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
        st.write(f"**File type:** {uploaded_file.type}")

def extract_text(path, ext, show_progress=True):
    """Extract text from different file types"""
    text = ""
    
    if ext == "pdf":
        reader = PdfReader(path)
        total = len(reader.pages)
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, page in enumerate(reader.pages):
            text += f"\n[Page {i+1}]\n" + page.extract_text()
            if show_progress:
                progress_bar.progress((i + 1) / total)
                status_text.text(f"📖 Processing page {i+1} of {total}")
        
        if show_progress:
            progress_bar.empty()
            status_text.empty()
            
    elif ext == "docx":
        doc = DocxDocument(path)
        total = len(doc.paragraphs)
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        for i, para in enumerate(doc.paragraphs):
            text += f"\n[Paragraph {i+1}]\n" + para.text
            if show_progress:
                progress_bar.progress((i + 1) / total)
                status_text.text(f"📄 Processing paragraph {i+1} of {total}")
        
        if show_progress:
            progress_bar.empty()
            status_text.empty()
            
    elif ext == "txt":
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            total = len(lines)
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            for i, line in enumerate(lines):
                text += f"\n[Line {i+1}]\n" + line.strip()
                if show_progress and ((i + 1) % 10 == 0 or i == total - 1):
                    progress_bar.progress((i + 1) / total)
                    status_text.text(f"📝 Processing line {i+1} of {total}")
            
            if show_progress:
                progress_bar.empty()
                status_text.empty()
    
    return text

def clean_quiz_text(text):
    """Clean generated quiz text"""
    replacements = [
        (r'\*+', ''), (r'#+\s*', ''), (r'_+', ''),
        (r'\n\s*\n\s*\n+', '\n\n'), (r'(?<=\d\.)\s*(?=[A-Z])', '\n'),
        (r'(?<=\))\s*(?=Answer:)', '\n'), (r'(\d+\.)', r'\n\1'),
        (r'[ \t]+', ' '), (r'\n +', '\n')
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text.strip()

# File processing
if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    if st.button("🔄 Process File", type="primary"):
        with st.spinner("📖 Extracting text from your document..."):
            text_data = extract_text(tmp_path, file_extension, show_progress)
            os.remove(tmp_path)

        if text_data:
            st.session_state.text_data = text_data
            st.success("✅ Text successfully extracted!")
            st.session_state.show_quiz_button = True
            
            with st.expander("👀 Preview Extracted Text"):
                preview = text_data[:500] + "..." if len(text_data) > 500 else text_data
                st.text_area("Text Preview", preview, height=200)

# Quiz configuration
if st.session_state.get("show_quiz_button"):
    st.markdown("---")
    st.markdown("### 🎯 Customize Your Quiz")
    
    # Presets
    PRESETS = {
        "quick": {"easy_mcq": 2, "medium_mcq": 1, "hard_mcq": 0, "easy_tf": 2, "medium_tf": 0, "hard_tf": 0},
        "standard": {"easy_mcq": 3, "medium_mcq": 2, "hard_mcq": 1, "easy_tf": 3, "medium_tf": 1, "hard_tf": 0},
        "comprehensive": {"easy_mcq": 5, "medium_mcq": 4, "hard_mcq": 3, "easy_tf": 5, "medium_tf": 2, "hard_tf": 1}
    }
    
    preset_col1, preset_col2, preset_col3 = st.columns(3)
    with preset_col1:
        if st.button("📝 Quick Quiz (5 questions)", use_container_width=True):
            st.session_state.preset = "quick"
    with preset_col2:
        if st.button("📚 Standard Quiz (10 questions)", use_container_width=True):
            st.session_state.preset = "standard"
    with preset_col3:
        if st.button("🎓 Comprehensive Quiz (20 questions)", use_container_width=True):
            st.session_state.preset = "comprehensive"
    
    with st.form("quiz_form"):
        custom_prompt = st.text_area(
            "🎨 Custom Instructions (Optional)",
            placeholder="Example: Include numerical problems, focus on definitions, add code examples, etc.",
            height=100
        )
        
        st.markdown("---")
        
        # Get default values
        default_values = PRESETS.get(st.session_state.get("preset"), 
                                   {"easy_mcq": 2, "medium_mcq": 2, "hard_mcq": 1, "easy_tf": 2, "medium_tf": 2, "hard_tf": 1})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🟢 Multiple Choice Questions**")
            easy_mcq = st.number_input("Easy MCQs", min_value=0, value=default_values["easy_mcq"])
            medium_mcq = st.number_input("Medium MCQs", min_value=0, value=default_values["medium_mcq"])
            hard_mcq = st.number_input("Hard MCQs", min_value=0, value=default_values["hard_mcq"])
        
        with col2:
            st.markdown("**🔴 True/False Questions**")
            easy_tf = st.number_input("Easy True/False", min_value=0, value=default_values["easy_tf"])
            medium_tf = st.number_input("Medium True/False", min_value=0, value=default_values["medium_tf"])
            hard_tf = st.number_input("Hard True/False", min_value=0, value=default_values["hard_tf"])
        
        total_questions = easy_mcq + medium_mcq + hard_mcq + easy_tf + medium_tf + hard_tf
        st.info(f"📊 Total Questions: **{total_questions}**")
        
        submit_btn = st.form_submit_button("🚀 Generate Quiz", type="primary", use_container_width=True)

    if submit_btn and total_questions > 0:
        prompt = f"""
You are an expert education assistant. Based on the following text:
{st.session_state.text_data}

Generate a quiz with:
MULTIPLE CHOICE QUESTIONS: {easy_mcq} Easy, {medium_mcq} Medium, {hard_mcq} Hard
TRUE/FALSE QUESTIONS: {easy_tf} Easy, {medium_tf} Medium, {hard_tf} Hard

{f"SPECIAL INSTRUCTIONS: {custom_prompt.strip()}" if custom_prompt.strip() else ""}

For EACH MCQ: Question number, full question, four options (A-D), correct answer, detailed explanation, reference.
For EACH T/F: Question number, statement, correct answer (True/False), detailed explanation, reference.

Use clean text format. Clearly separate sections. Number questions continuously.
"""

        with st.spinner("🤖 AI is crafting your personalized quiz..."):
            if show_progress:
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                    time.sleep(0.03)
                progress_bar.empty()
            
            response = model.generate_content(prompt)
            st.session_state.quiz_text = clean_quiz_text(response.text)
            
            # Update statistics
            st.session_state.total_questions_generated += total_questions
            st.session_state.quiz_history.append({
                'filename': uploaded_file.name,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'total_questions': total_questions
            })
            
            st.balloons()
            st.success("🎉 Quiz generated successfully!")

# Quiz preview and download
if st.session_state.get("quiz_text"):
    st.markdown("---")
    st.markdown("### 📋 Your Generated Quiz")
    
    tab1, tab2 = st.tabs(["📖 Preview", "⬇️ Download"])
    
    with tab1:
        st.markdown('<div class="quiz-preview">', unsafe_allow_html=True)
        st.text_area("Generated Quiz:", value=st.session_state.quiz_text, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📥 Download Your Quiz")
        
        def create_file(content, file_type):
            """Create downloadable files"""
            if file_type == "pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                    doc = SimpleDocTemplate(f.name, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = [Paragraph(line.strip(), styles["Normal"]) if line.strip() else Spacer(1, 12) 
                            for line in content.split('\n')]
                    doc.build(story)
                    return f.name
            elif file_type == "docx":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
                    doc = DocxWriter()
                    for line in content.split('\n'):
                        doc.add_paragraph(line.strip() if line.strip() else "")
                    doc.save(f.name)
                    return f.name
            elif file_type == "txt":
                with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
                    f.write(content)
                    return f.name
        
        col1, col2, col3 = st.columns(3)
        
        for col, (format_type, icon, mime) in zip([col1, col2, col3], 
                                                 [("pdf", "📄", "application/pdf"),
                                                  ("docx", "📝", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                                                  ("txt", "📋", "text/plain")]):
            with col:
                file_path = create_file(st.session_state.quiz_text, format_type)
                with open(file_path, "rb") as f:
                    st.download_button(f"{icon} {format_type.upper()} Format", f, 
                                     file_name=f"quiz.{format_type}", mime=mime, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="color: #666; text-align: center; padding: 2rem;">
    Made with ❤️ using Streamlit & Google Gemini AI<br>
    <small>Transform your documents into engaging quizzes instantly!</small>
</div>
""", unsafe_allow_html=True)
