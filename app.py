import streamlit as st
from google import genai
import re
from PIL import Image
import io
from fpdf import FPDF

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

# ================= PDF GENERATOR =================
def generate_pdf(clean_text, confidence):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    try:
        pdf.image("./logo.jpeg", x=10, y=8, w=33)
    except:
        pass
        
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(30, 144, 255) # DodgerBlue
    pdf.cell(0, 20, "Medical Analysis Report", ln=True, align="R")
    
    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Content
    if confidence is not None:
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Confidence Score: {confidence:.2f}%", ln=True)
        pdf.ln(5)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    # Basic cleaning for standard PDF fonts
    safe_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, safe_text)
    
    # Footer
    pdf.ln(20)
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(0, 10, "Disclaimer: This report is AI-generated and intended for informational purposes only. Consult with a qualified healthcare professional before making any medical decisions.", align="C")
    
    return pdf.output()

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
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []

if submit_button:
    if not upload_files:
        st.error("Please upload at least one image before clicking 'Generate Analysis'.")
    else:
        st.session_state.analysis_results = [] # Reset for new batch
        for i, file in enumerate(upload_files):
            # ===== IMAGE PROCESSING + ERROR HANDLING =====
            try:
                image_data = file.getvalue()
                image = Image.open(io.BytesIO(image_data))
            except Exception:
                st.error(f"Error processing image {i+1}")
                continue

            # ===== API CALL =====
            with st.spinner(f"Analyzing Image {i+1}..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[system_prompt, image],
                        generation_config=generation_config
                    )
                except Exception as e:
                    st.error(f"API Error for Image {i+1}: {str(e)}")
                    continue

            # ===== RESPONSE VALIDATION =====
            if not response or not getattr(response, "text", None):
                st.error(f"Invalid response for Image {i+1}")
                continue

            # ===== CONFIDENCE EXTRACTION =====
            confidence = extract_confidence(response.text)

            # ===== CLEAN RESPONSE =====
            clean_text = re.sub(
                r'Confidence Score:\s*\b(100|[0-9]{1,2})(\.\d+)?\s*%',
                '',
                response.text
            ).strip()

            st.session_state.analysis_results.append({
                "image": image,
                "confidence": confidence,
                "clean_text": clean_text,
                "original_index": i + 1
            })

# Display Persisted Results
for result in st.session_state.analysis_results:
    st.markdown("---")
    st.title(f"Analysis for Image {result['original_index']}")
    st.image(result['image'], width=300)

    if result['confidence'] is not None:
        st.progress(result['confidence'] / 100)
        st.markdown(f"### Confidence Score: **{result['confidence']:.2f}%**")

        if result['confidence'] > 80:
            st.success("High Confidence Prediction")
        elif result['confidence'] > 50:
            st.info("Moderate Confidence Prediction")
        else:
            st.error("Low Confidence Prediction")
    else:
        st.warning("⚠️ Confidence score not found in AI response")

    st.write(result['clean_text'])

    # ===== PDF DOWNLOAD BUTTON =====
    pdf_bytes = generate_pdf(result['clean_text'], result['confidence'])
    st.download_button(
        label="📥 Download Analysis Report as PDF",
        data=pdf_bytes,
        file_name=f"analysis_report_{result['original_index']}.pdf",
        mime="application/pdf"
    )

    st.warning("⚠️ Disclaimer: Consult with a Doctor before making any decisions")
