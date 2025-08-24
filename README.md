# 🧠 AI Quiz Generator Pro

A powerful Streamlit web application that transforms your documents into engaging quizzes using Google's Gemini AI. Upload PDF, DOCX, or TXT files and generate customized multiple-choice and true/false questions with detailed explanations.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **📁 Multi-format Support**: Upload PDF, DOCX, and TXT files
- **🎯 Customizable Quizzes**: Configure difficulty levels and question types
- **🎨 Multiple Themes**: Default, Dark Mode, and Colorful themes
- **📊 Progress Tracking**: Real-time processing animations
- **📝 Multiple Export Formats**: Download quizzes as PDF, DOCX, or TXT
- **📈 Quiz Statistics**: Track generated quizzes and questions
- **🎓 Preset Options**: Quick, Standard, and Comprehensive quiz templates
- **💡 Custom Instructions**: Add specific requirements for question generation

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ayushgigras/quiz_generator.git
   cd quiz_generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:8501` to access the application.

## 🔧 Configuration

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

### Customization Options

- **Quiz Difficulty**: Easy, Medium, Hard levels
- **Question Types**: Multiple Choice Questions (MCQ) and True/False
- **Custom Instructions**: Add specific requirements for question generation
- **Themes**: Choose from Default, Dark Mode, or Colorful themes
- **Export Formats**: PDF, DOCX, or plain text

## 📖 Usage

### Basic Workflow

1. **Upload Document**: Click "Choose a file" and select your PDF, DOCX, or TXT file
2. **Process File**: Click "🔄 Process File" to extract text content
3. **Customize Quiz**: 
   - Choose from preset options (Quick/Standard/Comprehensive)
   - Or manually configure question numbers by difficulty
   - Add custom instructions if needed
4. **Generate Quiz**: Click "🚀 Generate Quiz" to create your quiz
5. **Download**: Choose your preferred format (PDF, DOCX, or TXT)

### Preset Options

- **📝 Quick Quiz**: 5 questions (2 easy MCQ, 1 medium MCQ, 2 easy T/F)
- **📚 Standard Quiz**: 10 questions (balanced mix of difficulties)
- **🎓 Comprehensive Quiz**: 20 questions (extensive coverage with all difficulty levels)

### Custom Instructions Examples

- "Include numerical problems for physics concepts"
- "Focus on definitions and terminology for biology topics"
- "Add code examples for programming-related content"
- "Emphasize historical dates and events"

## 🏗️ Project Structure

```
quiz_generator/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── README.md             # Project documentation
└── .gitignore            # Git ignore file
```

## 🔍 Core Components

### File Processing
- **PDF**: Uses `pypdf` to extract text from PDF files
- **DOCX**: Uses `python-docx` to process Word documents
- **TXT**: Direct text file reading with encoding support

### AI Integration
- **Google Gemini AI**: Generates contextual quiz questions
- **Smart Prompting**: Constructs detailed prompts for quality output
- **Text Cleaning**: Processes and formats AI responses

### Export Options
- **PDF Generation**: Using `reportlab` for professional formatting
- **DOCX Creation**: Structured Word document output
- **Plain Text**: Simple text file export

## 📋 Requirements

```
streamlit>=1.28.0
google-generativeai>=0.3.0
pypdf>=3.17.0
python-docx>=0.8.11
reportlab>=4.0.4
python-dotenv>=1.0.0
plotly>=5.17.0
```

## 🎨 Themes

### Default Theme
Clean, professional interface with light background

### Dark Mode
Modern dark theme with purple accents for reduced eye strain

### Colorful Theme
Vibrant gradient backgrounds with engaging visual elements

## 📊 Features Overview

| Feature | Description |
|---------|-------------|
| File Upload | Drag & drop or browse PDF, DOCX, TXT files |
| Text Extraction | Progress-tracked extraction with page/paragraph indicators |
| Quiz Customization | Configure question types, difficulty, and count |
| AI Generation | Powered by Google Gemini for intelligent question creation |
| Multiple Exports | Download as PDF, DOCX, or plain text |
| Theme Support | Three beautiful themes to choose from |
| Statistics | Track quiz history and question generation |
| Responsive Design | Works on desktop and mobile devices |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛠️ Troubleshooting

### Common Issues

**API Key Error**
- Ensure your Gemini API key is correctly set in the `.env` file
- Verify the API key is active and has sufficient quota

**File Upload Issues**
- Check file size limits (Streamlit default: 200MB)
- Ensure file formats are supported (PDF, DOCX, TXT)

**Dependencies Error**
- Run `pip install -r requirements.txt` to install all dependencies
- Consider using a virtual environment

## 🌟 Acknowledgments

- Google Gemini AI for powerful question generation
- Streamlit for the amazing web app framework
- Contributors and users who provide feedback

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Made with ❤️ using Streamlit & Google Gemini AI**
