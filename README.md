# Disease Identifier 🧑‍⚕️

An AI-powered medical image analysis web application that helps users understand potential health issues from uploaded images. The app leverages Google Gemini API to generate structured medical insights including analysis, findings, and recommendations.

> ⚠️ Disclaimer: This tool is for educational and informational purposes only. Always consult a qualified medical professional before making any decisions.

---

## 🚀 Features

- 📤 Upload medical images (JPG, PNG, etc.)
- 🧠 AI-based disease analysis using Gemini
- 📋 Structured medical report:
  - Detailed Analysis
  - Findings Report
  - Recommendations
  - Treatment Suggestions
- ⚡ Fast and interactive UI with Streamlit

---

## 🏗️ Architecture

User Upload → Streamlit UI → Gemini API → AI Response → Structured Output

---

## 🧠 Tech Stack

- Frontend/UI: Streamlit  
- Backend: Python  
- AI Model: Google Gemini API  
- Deployment: Streamlit Cloud  

---

## 📸 Demo

👉 Live App: https://disease-identifier.streamlit.app/  
(Add screenshots here for better visibility)

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.x
- Streamlit

---

### 🔧 Local Setup

1. Clone the Repository
```bash
git clone https://github.com/fizaayesha/disease_identifier.git
cd disease_identifier

2. Create Virtual Environment
python -m venv venv
source venv/bin/activate   # For Linux/Mac
venv\Scripts\activate      # For Windows

3. Install Dependencies
pip install -r requirements.txt

4. Add API Key
Create a .streamlit directory and inside it create secrets.toml file:
GOOGLE_API_KEY = "your-google-api-key"

5. Run the App
streamlit run app.py

## 🤝 Contributing

We welcome contributions from the community! 🚀

Steps to Contribute:
Fork the repository
Create a new branch (feature/your-feature-name)
Make your changes
Commit and push
Open a Pull Request

## 🏷️ Good First Issues

If you're new to open source, you can start with:

Improve UI/UX
Add loading indicators
Add input validation
Enhance error handling

Check issues labeled good-first-issue
