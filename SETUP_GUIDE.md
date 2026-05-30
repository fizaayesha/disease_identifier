# 🛠️ Gemini API Setup Guide

To use the **Disease Identifier**, you need an API key from Google Gemini.

## 1. Get your API Key
1. Go to the [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Click on **"Create API key in new project"**.
3. Copy your unique API Key.

## 2. Configure Streamlit Secrets
Streamlit uses a local secrets file for development.

1. In the project root, create a folder named `.streamlit`:
   ```bash
   mkdir .streamlit
   ```
2. Create a file named `secrets.toml` inside that folder:
   ```bash
   # Windows
   echo GOOGLE_API_KEY = "PASTE_YOUR_KEY_HERE" > .streamlit/secrets.toml
   
   # Linux / Mac
   touch .streamlit/secrets.toml
   ```
3. Add your key to the file:
   ```toml
   GOOGLE_API_KEY = "your-api-key-here-12345"
   ```

## 3. Important Security Note
- Never commit your `secrets.toml` file to Git.
- It is already included in the `.gitignore` of this project.
- If deploying to **Streamlit Cloud**, add your secret in the App Settings dashboard under **"Secrets"**.
