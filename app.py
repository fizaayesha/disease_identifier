import streamlit as st
from google import genai
import re
from PIL import Image
import io

# ================= API KEY CHECK =================
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("API Key not found. Please set GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

# ================= CLIENT =================
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# ================= SYSTEM PROMPT =================
system_prompt = """
As a highly skilled medical practitioner specializing in image analysis, you are tasked with examining medical images.

Your responsibilities include:

1. Detailed Analysis
2. Findings Report
3. Recommendations and Next Steps
4. Treatment Suggestions

5. Confidence Score:
Always include a confidence score explicitly in this format:
"Confidence Score: XX%"

Important Notes:
- Only respond if image is related to human health
- If unclear, say "Unable to determine"
- Always include this disclaimer:
"Consult with a Doctor before making any decisions"
"""

# ================= CONFIDENCE EXTRACTOR =================
def extract_confidence(text):
    match = re.search(r'\b(100|[0-9]{1,2})(\.\d+)?\s*%', text)
    if match:
        return float(match.group(0).replace('%', ''))
    return None

# ================= STREAMLIT CONFIG =================
st.set_page_config(page_title="Disease Identifier", page_icon="🧑‍⚕️")

# Theme state
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = True

col1, col2 = st.columns([8, 2])
with col2:
    st.toggle("Dark Mode", key="theme_mode")

# Theme colors
theme_colors = {
    True: {'bg': '#1E1E1E', 'text': '#FFFFFF'},
    False: {'bg': '#FFFFFF', 'text': '#000000'}
}[st.session_state.theme_mode]

# Apply CSS
st.markdown(f"""
<style>
    .stApp {{
        background-color: {theme_colors['bg']};
        color: {theme_colors['text']};
    }}
</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.image("./logo.jpeg", width=200)
st.title("Disease Identifier 🧑‍⚕️")
st.header("Upload medical images to analyze diseases and get AI insights")

upload_files = st.file_uploader(
    "Upload images",
    type=["jpeg", "jpg", "png"],
    accept_multiple_files=True
)

# Preview uploaded images
if upload_files:
    for i, file in enumerate(upload_files):
        st.image(file, width=200, caption=f"Image {i+1}")

submit_button = st.button("Generate Analysis")

# ================= MAIN LOGIC =================
if submit_button and upload_files:
    for i, file in enumerate(upload_files):

        # ===== IMAGE VALIDATION =====
        try:
            image_data = file.getvalue()
            image = Image.open(io.BytesIO(image_data))
        except Exception:
            st.error(f"Invalid image file for Image {i+1}")
            continue

        st.image(image, width=300)

        # ===== API CALL =====
        with st.spinner(f"Analyzing Image {i+1}..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[system_prompt, image],
                    config=generation_config
                )
            except Exception as e:
                st.error(f"Error generating response: {e}")
                continue

        # ===== RESPONSE VALIDATION =====
        if not response or not hasattr(response, "text") or not response.text:
            st.error("Invalid response from AI model")
            continue

        st.title(f"Analysis for Image {i+1}")

        # ===== CONFIDENCE EXTRACTION =====
        confidence = extract_confidence(response.text)

        if confidence is not None:
            st.progress(confidence / 100)
            st.markdown(f"### Confidence Score: **{confidence:.2f}%**")

            # Confidence level indicator
            if confidence > 80:
                st.success("High Confidence Prediction")
            elif confidence > 50:
                st.info("Moderate Confidence Prediction")
            else:
                st.error("Low Confidence Prediction")
        else:
            st.warning("⚠️ Confidence score not found in AI response")

        # ===== CLEAN RESPONSE (SAFE) =====
        clean_text = re.sub(
            r'Confidence Score:\s*\b(100|[0-9]{1,2})(\.\d+)?\s*%',
            '',
            response.text
        )

        st.write(clean_text.strip())

        # ===== DISCLAIMER =====
        st.markdown("---")
        st.warning("⚠️ Disclaimer: Consult with a Doctor before making any decisions")
