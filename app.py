import streamlit as st
from pathlib import Path
from google import genai
import re
from PIL import Image
import io

# NEW CLIENT
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },        
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    }
]

system_prompt = """
As a highly skilled medical practitioner specializing in image analysis, you are tasked with examining medical images for a reowned hospital. Your expertise is crucial in identifying any anomalies, diseases, or health issues that may be present in the images.

Your responsibilities include:

1. Detailed Analysis: Thoroughly analyze each image, focusing on identifying any abnormal findings.
  
2. Findings Report:- Document all observed anomalies or signs of disease. Clearly articulate these finding in a structure format.

3. Recommendations and Next Steps: Based on your analysis, suggest potential next steps, including for the tests and treatment ass applicable.

4. Treatment Suggestions: If appropriate, recommend possible treatment options or interventions.

5. Confidence Score: Provide a confidence score (0-100%) indicating how confident you are in your analysis.

Important Notes:
1. Scope of Response: Only respond if the image pertains to human health issues.
2. Clarity of Image: In cases where the image quality impedes clear analysis, note that certain aspects are 'Unable to be determined based on the provided image.'
3. Disclaimer: Accompany your analysis with the disclaimer "Consult with a Doctor before making any decisions"
4. Your insights are invaluable in guiding clinical decisions. Please proceed with the analysis, adhering to the structured approach outlined above
Please provide me an output response with these 4 headings Detailed Analysis,Findings Report, Recommendations and Next Steps, Treatment Suggestions.
"""

# Confidence extractor
def extract_confidence(text):
    match = re.search(r'(\d{1,3})\s*%', text)
    if match:
        return int(match.group(1))
    return None

st.set_page_config(page_title="Disease Identifier", page_icon=":robot")

# Theme state initialization
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = True

col1, col2 = st.columns([8, 2])
with col2:
    st.toggle("Dark Mode", key="theme_mode")

# Define theme colors
theme_colors = {
    True: {'bg': '#1E1E1E', 'text': '#FFFFFF', 'btn_border': '#555555', 'btn_bg': '#333333', 'uploader': '#2E2E2E'},
    False: {'bg': '#FFFFFF', 'text': '#000000', 'btn_border': '#CCCCCC', 'btn_bg': '#F0F2F6', 'uploader': '#F0F2F6'}
}[st.session_state.theme_mode]

# Apply theme CSS
st.markdown(f"""
<style>
    .stApp, .stApp > header {{
        background-color: {theme_colors['bg']} !important;
        color: {theme_colors['text']} !important;
    }}
    h1, h2, h3, h4, h5, h6, p, label, span, div.stMarkdown {{
        color: {theme_colors['text']} !important;
    }}
    .stButton>button, [data-testid="stFileUploader"] button {{
        border-color: {theme_colors['btn_border']} !important;
        color: {theme_colors['text']} !important;
        background-color: {theme_colors['btn_bg']} !important;
    }}
    [data-testid="stFileUploader"] section {{
        background-color: {theme_colors['uploader']} !important;
        color: {theme_colors['text']} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.image("./logo.jpeg", width=200)

st.title("Disease Identifier🧑‍⚕️")

st.header("Welcome to the Disease Identifier App! 🌟. It helps the user to identify the disease and suggests the treatment as well!")
  
upload_files = st.file_uploader(
    "Upload the image of the disease for the analysis",
    type=["jpeg", "jpg", "png", "svg"],
    accept_multiple_files=True
)
# Multiple Images Uploading
if upload_files:
    for i, file in enumerate(upload_files):
        st.image(file, width=200, caption=f"Uploaded Image {i+1}")

submit_button = st.button("Generate the Analysis")

if submit_button and upload_files:
    for i, file in enumerate(upload_files):
        image_data = file.getvalue()

        # FIXED: Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))

        contents = [system_prompt, image]

        st.image(image_data, width=300)

        with st.spinner(f"Analyzing image {i+1}..."):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents
            )

        if response:
            st.title(f"Analysis for Image {i+1}")

            confidence = extract_confidence(response.text)
            if confidence is not None:
                st.progress(confidence / 100)
                st.markdown(f"### Confidence Score: **{confidence}%**")

            st.write(response.text)
