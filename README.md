# 🧑‍⚕️ Disease Identifier

> An AI-powered web application that helps users understand possible health issues from medical images using the Google Gemini API.

> [!WARNING]
> **Disclaimer:** This tool is for **educational and informational purposes only**. Always consult a qualified doctor before making any medical decisions.

---

## 🌐 Live Demo

👉 [disease-identifier.streamlit.app](https://disease-identifier.streamlit.app/)

---

## ✨ Features

- 📤 Upload medical images (JPG or PNG)
- 🤖 AI-based disease analysis powered by Google Gemini
- 📋 Generates a structured report including:
  - Detailed Analysis
  - Findings Report
  - Recommendations
  - Treatment Suggestions
- ⚡ Fast and interactive UI built with Streamlit

---

## 🏗️ Architecture

```
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

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Backend | Python |
| AI Model | Google Gemini API |
| Deployment | Streamlit Cloud |

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.x installed
- Streamlit installed

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/fizaayesha/disease_identifier.git
cd disease_identifier
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
```

- On Linux / Mac:
  ```bash
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  venv\Scripts\activate
  ```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create a `.streamlit/secrets.toml` file and add:

```toml
GOOGLE_API_KEY = "your-google-api-key"
```

**5. Run the application**

```bash
streamlit run app.py
```

---

## 🤝 Contributing

Contributions are welcome! 🚀

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit and push: `git commit -m "Add your message"` → `git push origin feature/your-feature-name`
5. Open a Pull Request

For detailed guidelines, check the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### 🟢 Good First Issues

New to open source? Start with beginner-friendly tasks:

- 🎨 Improving UI/UX
- ⏳ Adding loading indicators
- ✅ Adding input validation
- 🛡️ Improving error handling

Find these tasks under issues labeled [`good-first-issue`](../../issues?q=label%3Agood-first-issue).

---

## 📄 License

This project is open source. See the [LICENSE](LICENSE) file for details.
