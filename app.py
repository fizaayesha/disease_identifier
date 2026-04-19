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

# ================= BODY MAP =================
BODY_PARTS = [
    {"label": "Head / Brain",  "icon": "🧠", "specialty": "Neurology"},
    {"label": "Eye",           "icon": "👁️",  "specialty": "Ophthalmology"},
    {"label": "Ear / Nose / Throat", "icon": "👂", "specialty": "ENT (Otolaryngology)"},
    {"label": "Chest / Lungs", "icon": "🫁", "specialty": "Pulmonology / Radiology"},
    {"label": "Heart",         "icon": "❤️",  "specialty": "Cardiology"},
    {"label": "Abdomen",       "icon": "🫃", "specialty": "Gastroenterology"},
    {"label": "Skin",          "icon": "🩹", "specialty": "Dermatology"},
    {"label": "Bones / Joints","icon": "🦴", "specialty": "Orthopedics"},
    {"label": "Limbs / Muscles","icon": "💪", "specialty": "Orthopedics / Sports Medicine"},
    {"label": "Urinary / Kidney","icon": "🫘","specialty": "Nephrology / Urology"},
    {"label": "Reproductive",  "icon": "🔬", "specialty": "Gynecology / Urology"},
    {"label": "Other / General","icon": "🩺", "specialty": "General Medicine"},
]

# ================= SYSTEM PROMPT BUILDER =================
def build_system_prompt(body_part: dict | None) -> str:
    if body_part:
        specialty_context = (
            f"The patient has indicated the affected area is: **{body_part['label']}**. "
            f"Focus your analysis through the lens of **{body_part['specialty']}**.\n\n"
        )
    else:
        specialty_context = ""
    return f"""
As a highly skilled medical practitioner specializing in image analysis, you are tasked with examining medical images.

{specialty_context}Your responsibilities include:

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
    div[data-testid="stHorizontalBlock"] button {{
        width: 100%;
        border-radius: 12px;
        padding: 0.5rem;
        font-size: 0.85rem;
    }}
</style>
""", unsafe_allow_html=True)

# ================= UI =================
st.image("./logo.jpeg", width=200)
st.title("Disease Identifier 🧑‍⚕️")
st.header("Upload medical images to analyze diseases and get AI insights")

# ================= BODY MAP =================
st.markdown("### 🗺️ Step 1 — Select the affected body area")
st.caption("Choose the region closest to where your concern is located. This helps focus the AI analysis.")

# Session state for selected body part
if "selected_body_part" not in st.session_state:
    st.session_state.selected_body_part = None

COLS_PER_ROW = 4
rows = [BODY_PARTS[i:i + COLS_PER_ROW] for i in range(0, len(BODY_PARTS), COLS_PER_ROW)]

for row in rows:
    cols = st.columns(len(row))
    for col, part in zip(cols, row):
        is_selected = (
            st.session_state.selected_body_part is not None
            and st.session_state.selected_body_part["label"] == part["label"]
        )
        label = f"**{part['icon']} {part['label']}**" if is_selected else f"{part['icon']} {part['label']}"
        if col.button(label, key=f"body_{part['label']}", use_container_width=True):
            st.session_state.selected_body_part = part
            st.rerun()

selected = st.session_state.selected_body_part
if selected:
    st.success(
        f"✅ Selected: **{selected['icon']} {selected['label']}** — "
        f"Analysis will be focused on **{selected['specialty']}**"
    )
    if st.button("🔄 Change selection", key="reset_body"):
        st.session_state.selected_body_part = None
        st.rerun()
else:
    st.info("👆 Please select a body area above to continue.")

# ================= IMAGE UPLOAD (Step 2) =================
st.markdown("### 📤 Step 2 — Upload your medical image(s)")

upload_files = st.file_uploader(
    "Upload images",
    type=["jpeg", "jpg", "png"],
    accept_multiple_files=True,
    disabled=selected is None,
)

if selected is None:
    st.caption("⚠️ Select a body area first to enable image upload.")

# Preview uploaded images
if upload_files:
    for i, file in enumerate(upload_files):
        st.image(file, width=200, caption=f"Image {i+1}")

# Disable button if no images or no body part selected
submit_button = st.button(
    "Generate Analysis",
    disabled=(not upload_files or selected is None),
)

# ================= MAIN LOGIC =================
if submit_button:
    if not upload_files:
        st.error("⚠️ Please upload at least one image before generating analysis.")
    elif selected is None:
        st.error("⚠️ Please select a body area before generating analysis.")
    else:
        system_prompt = build_system_prompt(selected)

        for i, file in enumerate(upload_files):

            # ===== IMAGE PROCESSING =====
            try:
                image_data = file.getvalue()
                image = Image.open(io.BytesIO(image_data)).convert("RGB")
            except Exception:
                st.error(f"Error processing image {i+1}")
                continue

            st.image(image, width=300)

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

            st.subheader(f"Analysis for Image {i+1}")

            # ===== CONFIDENCE EXTRACTION =====
            confidence = extract_confidence(response.text)

            if confidence is not None:
                st.progress(confidence / 100)
                st.markdown(f"### Confidence Score: **{confidence:.2f}%**")

                if confidence > 80:
                    st.success("High Confidence Prediction")
                elif confidence > 50:
                    st.info("Moderate Confidence Prediction")
                else:
                    st.error("Low Confidence Prediction")
            else:
                st.warning("⚠️ Confidence score not found in AI response")

            # ===== CLEAN RESPONSE =====
            clean_text = re.sub(
                r'Confidence Score:\s*\b(100|[0-9]{1,2})(\.\d+)?\s*%',
                '',
                response.text
            )

            st.write(clean_text.strip())

            # ===== DISCLAIMER =====
            st.markdown("---")
            st.warning("⚠️ Disclaimer: Consult with a Doctor before making any decisions")
