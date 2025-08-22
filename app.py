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

# Load environment variables (like API key)
load_dotenv()

# Page configuration with custom styling
st.set_page_config(
    page_title="AI Quiz Generator Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
if 'total_questions_generated' not in st.session_state:
    st.session_state.total_questions_generated = 0
if 'theme' not in st.session_state:
    st.session_state.theme = "Default"

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to apply theme-based CSS with improved targeting
def apply_theme_css():
    """Applies custom CSS for different themes, ensuring text is always visible."""
    current_theme = st.session_state.get('theme', 'Default')
    
    # Theme colors
    if current_theme == "Dark Mode":
        primary_color = "#bb86fc"
        bg_color = "#1e1e1e"
        text_color = "#ffffff"
        card_bg = "#2d2d2d"
        card_text_color = "#ffffff"
        gradient = "linear-gradient(135deg, rgba(187, 134, 252, 0.1), rgba(3, 218, 198, 0.1))"
        stats_gradient = "linear-gradient(135deg, #bb86fc 0%, #03dac6 100%)"
        sidebar_bg = "#2d2d2d"
        sidebar_text_color = "#ffffff"
        header_gradient = "linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1)"
        button_bg = "#3a3a3a"
    elif current_theme == "Colorful":
        primary_color = "#4ecdc4"
        bg_color = "linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)"
        text_color = "#000000"
        card_bg = "#ffffff"
        card_text_color = "#000000"
        gradient = "linear-gradient(135deg, rgba(78, 205, 196, 0.2), rgba(255, 107, 107, 0.2))"
        stats_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        sidebar_bg = "#f0f0f0"
        sidebar_text_color = "#000000"
        header_gradient = "linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7)"
        button_bg = "#f0f0f0"
    else:  # Default
        primary_color = "#4ecdc4"
        bg_color = "#ffffff"
        text_color = "#000000"
        card_bg = "#ffffff"
        card_text_color = "#000000"
        gradient = "linear-gradient(135deg, rgba(78, 205, 196, 0.1), rgba(255, 107, 107, 0.1))"
        stats_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        sidebar_bg = "#f0f2f6"
        sidebar_text_color = "#000000"
        header_gradient = "linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1)"
        button_bg = "#f0f2f6"

    st.markdown(f"""
    <style>
        /* Overall App Styling */
        .stApp {{
            background: {bg_color};
            color: {text_color};
        }}
        
        /* Sidebar Styling */
        .st-emotion-cache-1wq0z5r, .st-emotion-cache-1wq0z5r > div {{
            background-color: {sidebar_bg} !important;
        }}
        .st-emotion-cache-1wq0z5r * {{
            color: {sidebar_text_color} !important;
        }}

        /* Header with animation */
        .main-header {{
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            background: {header_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 2rem;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ filter: drop-shadow(0 0 5px rgba(78, 205, 196, 0.4)); }}
            to {{ filter: drop-shadow(0 0 20px rgba(78, 205, 196, 0.8)); }}
        }}
        
        /* File upload section */
        .upload-section {{
            border: 2px dashed {primary_color};
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            background: {gradient};
            margin: 1rem 0;
            transition: all 0.3s ease;
        }}
        
        .upload-section:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        /* Stats cards */
        .stats-card {{
            background: {stats_gradient};
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 0.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        /* Quiz preview */
        .quiz-preview {{
            background: {card_bg};
            border-left: 5px solid {primary_color};
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            color: {card_text_color};
        }}
        
        /* Success animation */
        .success-animation {{
            animation: bounce 1s infinite;
            color: {text_color};
        }}
        
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}
        
        /* Footer text */
        .footer-text {{
            color: #666;
            text-align: center;
            padding: 2rem;
        }}
        
        /* Correcting color for specific Streamlit components */
        .st-emotion-cache-1wq0z5r .st-emotion-cache-1r65n2d * {{
            color: {sidebar_text_color} !important;
        }}
        .st-emotion-cache-1629p2 * {{
            color: {text_color} !important;
        }}
        .st-emotion-cache-h5g1k5 p {{
            color: {text_color} !important;
        }}
        .st-emotion-cache-10n2u9v {{
            color: {text_color} !important;
        }}
        .st-emotion-cache-q8s00j .st-emotion-cache-f1x2j2.e1b2p2x1 p {{
            color: {text_color} !important;
        }}
        .st-emotion-cache-q8s00j .st-emotion-cache-f1x2j2.e1b2p2x1 {{
            color: {text_color} !important;
        }}

        /* File uploader styling */
        .st-emotion-cache-1g8w4t4 > div {{
            background-color: {button_bg} !important;
        }}
        .st-emotion-cache-1g8w4t4 * {{
            color: {text_color} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# Apply theme CSS
apply_theme_css()

# Header with animation
st.markdown('<h1 class="main-header">🧠 AI Quiz Generator Pro</h1>', unsafe_allow_html=True)

# Sidebar with statistics and settings
with st.sidebar:
    st.markdown("### 📊 Dashboard")
    
    # Statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Quizzes", len(st.session_state.quiz_history))
    with col2:
        st.metric("Questions Generated", st.session_state.total_questions_generated)
    
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

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File upload section with enhanced styling
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 📁 Upload Your Document")
    st.markdown("*Supports PDF, DOCX, and TXT files*")
    
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["pdf", "docx", "txt"],
        help="Upload a document to generate quiz questions from"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # File info display
    if uploaded_file:
        st.markdown("### 📋 File Information")
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }
        for key, value in file_details.items():
            st.write(f"**{key}:** {value}")

# Progress tracking function
def show_progress_bar(message, duration=2):
    """Shows a progress bar with a status message."""
    if show_progress:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            progress_bar.progress(i + 1)
            status_text.text(f'{message} {i+1}%')
            time.sleep(duration/100)
        
        status_text.empty()
        progress_bar.empty()

# File processing
if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    def extract_text(path, ext):
        """Extracts text from different file types (PDF, DOCX, TXT)."""
        text = ""
        if ext == "pdf":
            reader = PdfReader(path)
            total_pages = len(reader.pages)
            
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            for i, page in enumerate(reader.pages):
                text += f"\n[Page {i+1}]\n" + page.extract_text()
                
                if show_progress:
                    progress_percentage = (i + 1) / total_pages
                    progress_bar.progress(progress_percentage)
                    status_text.text(f"📖 Processing page {i+1} of {total_pages} ({int(progress_percentage * 100)}%)")
            
            if show_progress:
                progress_bar.empty()
                status_text.empty()
                
        elif ext == "docx":
            doc = DocxDocument(path)
            total_paragraphs = len(doc.paragraphs)
            
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            for i, para in enumerate(doc.paragraphs):
                text += f"\n[Paragraph {i+1}]\n" + para.text
                
                if show_progress:
                    progress_percentage = (i + 1) / total_paragraphs
                    progress_bar.progress(progress_percentage)
                    status_text.text(f"📄 Processing paragraph {i+1} of {total_paragraphs} ({int(progress_percentage * 100)}%)")
            
            if show_progress:
                progress_bar.empty()
                status_text.empty()
                
        elif ext == "txt":
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                total_lines = len(lines)
                
                if show_progress:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                
                for i, line in enumerate(lines):
                    text += f"\n[Line {i+1}]\n" + line.strip()
                    
                    if show_progress and (i + 1) % 10 == 0 or i == total_lines - 1:
                        progress_percentage = (i + 1) / total_lines
                        progress_bar.progress(progress_percentage)
                        status_text.text(f"📝 Processing line {i+1} of {total_lines} ({int(progress_percentage * 100)}%)")
                
                if show_progress:
                    progress_bar.empty()
                    status_text.empty()
                    
        return text

    if st.button("🔄 Process File", type="primary"):
        with st.spinner("📖 Extracting text from your document..."):
            text_data = extract_text(tmp_path, file_extension)
            os.remove(tmp_path)

        if text_data:
            st.session_state.text_data = text_data
            st.markdown('<p class="success-animation">✅ Text successfully extracted!</p>', unsafe_allow_html=True)
            st.session_state.show_quiz_button = True
            
            # Show text preview
            with st.expander("👀 Preview Extracted Text"):
                st.text_area("Text Preview", text_data[:500] + "..." if len(text_data) > 500 else text_data, height=200)

def clean_quiz_text(text):
    """Clean the generated quiz text by removing unwanted symbols and fixing spacing."""
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'_+', '', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'(?<=\d\.)\s*(?=[A-Z])', '\n', text)
    text = re.sub(r'(?<=\))\s*(?=Answer:)', '\n', text)
    text = re.sub(r'(?<=Answer:)\s*([A-D]|True|False)', r' \1', text)
    text = re.sub(r'(\d+\.)', r'\n\1', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    return text.strip()

# Quiz configuration section
if st.session_state.get("show_quiz_button"):
    st.markdown("---")
    st.markdown("### 🎯 Customize Your Quiz")
    
    # Preset options
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
        # Set default values based on preset
        if st.session_state.get("preset") == "quick":
            default_values = {"easy_mcq": 2, "medium_mcq": 1, "hard_mcq": 0, "easy_tf": 2, "medium_tf": 0, "hard_tf": 0}
        elif st.session_state.get("preset") == "standard":
            default_values = {"easy_mcq": 3, "medium_mcq": 2, "hard_mcq": 1, "easy_tf": 3, "medium_tf": 1, "hard_tf": 0}
        elif st.session_state.get("preset") == "comprehensive":
            default_values = {"easy_mcq": 5, "medium_mcq": 4, "hard_mcq": 3, "easy_tf": 5, "medium_tf": 2, "hard_tf": 1}
        else:
            default_values = {"easy_mcq": 2, "medium_mcq": 2, "hard_mcq": 1, "easy_tf": 2, "medium_tf": 2, "hard_tf": 1}
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🟢 Multiple Choice Questions**")
            easy_mcq = st.number_input("Easy MCQs", min_value=0, value=default_values["easy_mcq"], key="easy_mcq")
            medium_mcq = st.number_input("Medium MCQs", min_value=0, value=default_values["medium_mcq"], key="medium_mcq")
            hard_mcq = st.number_input("Hard MCQs", min_value=0, value=default_values["hard_mcq"], key="hard_mcq")
        
        with col2:
            st.markdown("**🔴 True/False Questions**")
            easy_tf = st.number_input("Easy True/False", min_value=0, value=default_values["easy_tf"], key="easy_tf")
            medium_tf = st.number_input("Medium True/False", min_value=0, value=default_values["medium_tf"], key="medium_tf")
            hard_tf = st.number_input("Hard True/False", min_value=0, value=default_values["hard_tf"], key="hard_tf")
        
        # Total questions display
        total_questions = easy_mcq + medium_mcq + hard_mcq + easy_tf + medium_tf + hard_tf
        st.info(f"📊 Total Questions: **{total_questions}**")
        
        submit_btn = st.form_submit_button("🚀 Generate Quiz", type="primary", use_container_width=True)

    if submit_btn and total_questions > 0:
        prompt = f"""
You are an expert education assistant. Based on the following text:
{st.session_state.text_data}

Generate a quiz with the following format:

MULTIPLE CHOICE QUESTIONS:
- {easy_mcq} Easy MCQs
- {medium_mcq} Medium MCQs  
- {hard_mcq} Hard MCQs

TRUE/FALSE QUESTIONS:
- {easy_tf} Easy True/False questions
- {medium_tf} Medium True/False questions
- {hard_tf} Hard True/False questions

For EACH MCQ question, provide:
1. Question number and full question
2. Four options (A, B, C, D)
3. Correct Answer: (A/B/C/D)
4. Detailed Explanation: (Why this answer is correct)
5. Reference: Page [X], Line [Y]

For EACH True/False question, provide:
1. Question number and statement
2. Correct Answer: (True/False)
3. Detailed Explanation: (Why this statement is true or false)
4. Reference: Page [X], Line [Y]

Use clean text format. Clearly separate MCQ and True/False sections. Number questions continuously.
"""

        with st.spinner("🤖 AI is crafting your personalized quiz..."):
            if show_progress:
                show_progress_bar("Generating quiz", 3)
            
            response = model.generate_content(prompt)
            cleaned_text = clean_quiz_text(response.text)
            st.session_state.quiz_text = cleaned_text
            
            # Update statistics
            st.session_state.total_questions_generated += total_questions
            st.session_state.quiz_history.append({
                'filename': uploaded_file.name,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'total_questions': total_questions
            })
            
            st.balloons()  # Celebration animation
            st.success("🎉 Quiz generated successfully!")

# Quiz preview and download section
if st.session_state.get("quiz_text"):
    st.markdown("---")
    st.markdown("### 📋 Your Generated Quiz")
    
    # Tabs for better organization
    tab1, tab2 = st.tabs(["📖 Preview", "⬇️ Download"])
    
    with tab1:
        st.markdown('<div class="quiz-preview">', unsafe_allow_html=True)
        st.text_area("Generated Quiz:", value=st.session_state.quiz_text, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📥 Download Your Quiz")
        
        def save_pdf(content, file_path):
            """Saves quiz content to a PDF file."""
            styles = getSampleStyleSheet()
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            lines = content.split('\n')
            story = []
            for line in lines:
                if line.strip():
                    story.append(Paragraph(line.strip(), styles["Normal"]))
                else:
                    story.append(Spacer(1, 12))
            doc.build(story)

        def save_docx(content, file_path):
            """Saves quiz content to a DOCX file."""
            doc = DocxWriter()
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    doc.add_paragraph(line.strip())
                else:
                    doc.add_paragraph("")
            doc.save(file_path)

        def save_txt(content, file_path):
            """Saves quiz content to a TXT file."""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        download_col1, download_col2, download_col3 = st.columns(3)
        
        with download_col1:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
                save_pdf(st.session_state.quiz_text, pdf_file.name)
                with open(pdf_file.name, "rb") as f:
                    st.download_button("📄 PDF Format", f, file_name="quiz.pdf", mime="application/pdf", use_container_width=True)

        with download_col2:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as docx_file:
                save_docx(st.session_state.quiz_text, docx_file.name)
                with open(docx_file.name, "rb") as f:
                    st.download_button("📝 Word Document", f, file_name="quiz.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

        with download_col3:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as txt_file:
                save_txt(st.session_state.quiz_text, txt_file.name)
                with open(txt_file.name, "rb") as f:
                    st.download_button("📋 Text File", f, file_name="quiz.txt", mime="text/plain", use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div class="footer-text">
        Made with ❤️ using Streamlit & Google Gemini AI<br>
        <small>Transform your documents into engaging quizzes instantly!</small>
    </div>
    """, 
    unsafe_allow_html=True
)
