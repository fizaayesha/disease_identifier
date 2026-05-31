# 🧑‍⚕️ Disease Identifier



> An AI-powered web application that helps users understand possible health issues from medical images using the Google Gemini API.

> [!WARNING]
> **Disclaimer:** This tool is for **educational and informational purposes only**. Always consult a qualified doctor before making any medical decisions.

---

## 🏗️ Modular Architecture

The project is structured into dedicated modules for better maintainability and scalability:

- **`app.py`**: Main entry point and Streamlit UI logic.
- **`ai_engine.py`**: Handles Google Gemini API configurations, prompts, and image analysis.
- **`pdf_utils.py`**: Logic for generating high-quality medical reports in PDF format.
- **`history_manager.py`**: Manages local storage of analysis results and image files.

---

## 🏗️ Architecture

```
select the organ
       ↓
User uploads image
       ↓
Streamlit Interface
       ↓
Gemini API processes image
       ↓
AI generates response
       ↓
Structured output shown to user
```

---

## 🛠️ Tech Stack

- **📤 Multi-Image Upload**: Batch process medical images (JPG, PNG).
- **🖼️ Grid View**: Modern UI for previewing multiple uploaded files.
- **🧠 Advanced AI Analysis**: Powered by Google Gemini (1.5-Flash) for pattern recognition.
- **📋 Structured Reports**: Detailed findings, recommendations, and confidence scores.
- **📥 PDF Export**: Download professional medical reports for each analysis.
- **📊 CSV Export**: Export your entire analysis history for record-keeping.
- **📜 Persistent History**: Keep track of past analyses with local image storage.
- **⚡ Interactive UI**: Fast, responsive design with dark mode support.

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/fizaayesha/disease_identifier.git
   cd disease_identifier
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API key**
   Create a `.streamlit/secrets.toml` file:
   ```toml
   GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

---

## 🤝 Contributing

Contributions are welcome! Please follow our [CONTRIBUTING.md](CONTRIBUTING.md) guide.
[Please start picking issues from here on which you can work, tag me and I will assign the issue and add labels accordingly. | https://github.com/fizaayesha/disease_identifier/issues/48]

---

## 📄 License
This project is open source. See the [LICENSE](LICENSE) file for details.
