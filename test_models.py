import google.generativeai as genai
import streamlit as st

# Configure
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# List all available models
print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")