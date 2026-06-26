import streamlit as st
import google.generativeai as genai
import re
import csv
import io
from PIL import Image, UnidentifiedImageError
from io import StringIO
from fpdf import FPDF
import os
import json
from datetime import datetime
import uuid
import hashlib
from api_validator import APIValidator

# ================= API KEY VALIDATION AT STARTUP =================
try:
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error(
            "⚠️ API Key Configuration Error\n\n"
            "The GOOGLE_API_KEY is missing from your Streamlit secrets.\n\n"
            "To fix this:\n"
            "1. Create a `.streamlit/secrets.toml` file\n"
            "2. Add: `GOOGLE_API_KEY = 'your-api-key-here'`\n"
            "3. Get your key from: https://console.cloud.google.com"
        )
        st.info(
            "**Alternatively** (for environment variables):\n"
            "Set via shell: `export GOOGLE_API_KEY='your-key'`"
        )
        st.stop()

    api_key = st.secrets["GOOGLE_API_KEY"]

    if len(api_key.strip()) < 10:
        st.error(
            f"⚠️ API Key Validation Failed\n\n"
            f"API key is too short (length: {len(api_key)}).\n"
            "Please verify you've copied the full API key from Google Cloud console."
        )
        st.stop()

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Say 'OK' in one word.", stream=False)
        if not response or not response.text:
            st.warning(
                "⚠️ API Connectivity Test Failed\n\n"
                "The Gemini API returned an unexpected response.\n"
                "Please check:\n"
                "- Your internet connection\n"
                "- API rate limits\n"
                "- API key permissions\n\n"
                "Retrying in a moment..."
            )
    except google.api_core.exceptions.InvalidArgument as e:
        st.error(
            "⚠️ API Key Invalid\n\n"
            f"Error: {str(e)}\n\n"
            "Please verify your API key in Google Cloud console."
        )
        st.stop()
    except Exception as e:
        st.warning(
            f"⚠️ API Connectivity Warning\n\n"
            f"Could not verify API connectivity: {str(e)}\n\n"
            "The application will attempt to proceed, but errors may occur."
        )

except Exception as e:
    st.error(f"Unexpected error during API validation: {str(e)}")
    st.stop()

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

# ================= USER AUTH =================
USERS_FILE = "users.json"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username: str, password: str) -> tuple[bool, str]:
    users = load_users()
    if username.strip() == "":
        return False, "Username cannot be empty."
    if username in users:
        return False, "Username already exists."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[username] = hash_password(password)
    save_users(users)
    return True, "Account created successfully!"

def verify_user(username: str, password: str) -> bool:
    users = load_users()
    return users.get(username) == hash_password(password)

# ================= AUTH GATE =================
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

def show_auth_page():
    st.set_page_config(page_title="Disease Identifier – Login", page_icon="🧑‍⚕️")
    st.title("🧑‍⚕️ Disease Identifier")
    st.markdown("### Please log in to continue")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if verify_user(username, password):
                st.session_state.authenticated_user = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab_register:
        new_user = st.text_input("Choose a username", key="reg_user")
        new_pass = st.text_input("Choose a password (min 6 chars)", type="password", key="reg_pass")
        if st.button("Create Account", use_container_width=True):
            ok, msg = register_user(new_user, new_pass)
            if ok:
                st.success(msg + " Please log in.")
            else:
                st.error(msg)

if st.session_state.authenticated_user is None:
    show_auth_page()
    st.stop()

# ---- From here on the user is authenticated ----
current_user = st.session_state.authenticated_user

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

    try:
        pdf.image("./logo.jpeg", x=10, y=8, w=33)
    except Exception:
        pass

    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(30, 144, 255)
    pdf.cell(0, 20, "Medical Analysis Report", ln=True, align="R")

    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    if confidence is not None:
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Confidence Score: {confidence:.2f}%", ln=True)
        pdf.ln(5)

    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(50, 50, 50)
    safe_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, safe_text)

    pdf.ln(20)
    pdf.set_font("helvetica", "I", 10)
    pdf.set_text_color(128, 128, 128)
    pdf.multi_cell(
        0, 10,
        "Disclaimer: This report is AI-generated and intended for informational "
        "purposes only. Consult with a qualified healthcare professional before "
        "making any medical decisions.",
        align="C"
    )

    return pdf.output()

# ================= PER-USER HISTORY MANAGEMENT =================
BASE_HISTORY_DIR = "history"

def _user_paths(username: str) -> tuple[str, str, str]:
    """Return (history_dir, metadata_file, images_dir) for a given user."""
    history_dir = os.path.join(BASE_HISTORY_DIR, username)
    metadata_file = os.path.join(history_dir, "metadata.json")
    images_dir = os.path.join(history_dir, "images")
    return history_dir, metadata_file, images_dir

def _ensure_user_dirs(username: str):
    _, _, images_dir = _user_paths(username)
    os.makedirs(images_dir, exist_ok=True)

_ensure_user_dirs(current_user)

def save_to_history(image, confidence, clean_text, filename):
    _, metadata_file, images_dir = _user_paths(current_user)
    history = []
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    image_id = str(uuid.uuid4())
    image_path = os.path.join(images_dir, f"{image_id}.png")
    image.save(image_path)

    entry = {
        "id": image_id,
        "timestamp": timestamp,
        "image_name": filename,
        "image_path": image_path,
        "confidence": confidence,
        "text": clean_text,
    }

    history.insert(0, entry)
    with open(metadata_file, "w") as f:
        json.dump(history, f, indent=4)
    return entry

def load_history():
    _, metadata_file, _ = _user_paths(current_user)
    if not os.path.exists(metadata_file):
        return []
    try:
        with open(metadata_file, "r") as f:
            return json.load(f)
    except Exception:
        return []

def clear_history():
    _, metadata_file, _ = _user_paths(current_user)
    if os.path.exists(metadata_file):
        os.remove(metadata_file)

# ================= FILE UPLOAD LIMITS =================
MAX_FILES_PER_BATCH = 10
MAX_FILE_SIZE = 5 * 1024 * 1024

# ================= GEMINI ANALYSIS =================
def analyze_image(image: Image.Image):
    model = genai.GenerativeModel(
        model_name="models/gemini-1.5-flash",
        generation_config=generation_config,
    )
    return model.generate_content([system_prompt, image])

# ================= STREAMLIT CONFIG =================
st.set_page_config(page_title="Disease Identifier", page_icon="🧑‍⚕️")

# Theme state
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = True

col1, col2, col3 = st.columns([7, 2, 1])
with col2:
    st.toggle("Dark Mode", key="theme_mode")
with col3:
    if st.button("Logout"):
        st.session_state.authenticated_user = None
        st.session_state.analysis_results = []
        st.session_state.view_history = None
        st.rerun()

theme_colors = {
    True:  {'bg': '#1E1E1E', 'text': '#FFFFFF'},
    False: {'bg': '#FFFFFF',  'text': '#000000'},
}[st.session_state.theme_mode]

st.markdown(f"""
<style>
    .stApp {{
        background-color: {theme_colors['bg']};
        color: {theme_colors['text']};
    }}
</style>
""", unsafe_allow_html=True)

# ================= UI =================
try:
    st.image("./logo.jpeg", width=150)
except Exception:
    pass

st.title("🧑‍⚕️ Disease Identifier")
st.markdown("### AI-Powered Medical Image Analysis")
st.caption(f"Logged in as **{current_user}** · Upload medical images (X-rays, skin scans, etc.) to get instant AI-driven diagnostic insights.")

upload_files = st.file_uploader(
    "Upload images",
    type=["jpeg", "jpg", "png"],
    accept_multiple_files=True,
)

# File count and size validation
if upload_files:
    valid_files = []
    skipped_count = 0

    if len(upload_files) > MAX_FILES_PER_BATCH:
        st.warning(
            f"⚠️ You selected {len(upload_files)} files, but the maximum is {MAX_FILES_PER_BATCH} files per batch. "
            f"The first {MAX_FILES_PER_BATCH} files will be processed, and {len(upload_files) - MAX_FILES_PER_BATCH} will be skipped."
        )
        upload_files = upload_files[:MAX_FILES_PER_BATCH]

    for file in upload_files:
        if file.size > MAX_FILE_SIZE:
            st.warning(f"⚠️ File '{file.name}' exceeds 5 MB and will be skipped.")
            skipped_count += 1
        else:
            valid_files.append(file)

    if valid_files:
        st.subheader("🖼️ Selected Images")
        cols = st.columns(4)
        for i, file in enumerate(valid_files):
            with cols[i % 4]:
                st.image(file, use_container_width=True, caption=f"Image {i+1}")

        if st.button("🚀 Generate Analysis", type="primary", use_container_width=True):
            st.session_state.view_history = None
            st.session_state.analysis_results = []

            total = len(valid_files)
            progress_bar = st.progress(0, text="Starting analysis...")

            for i, file in enumerate(valid_files):
                progress_bar.progress(i / total, text=f"Analyzing image {i+1} of {total}...")

                # ===== FIX FOR ISSUE #50: Proper exception handling for Image.open() =====
                # Image.open() is lazy — it doesn't fully decode the image until it's used.
                # Calling image.verify() forces full decoding immediately so corrupt or
                # malformed images are caught here instead of crashing the app later.
                try:
                    image_data = file.getvalue()
                    # verify() detects corruption but closes the file after, so we
                    # must re-open a fresh copy for actual use
                    Image.open(io.BytesIO(image_data)).verify()
                    image = Image.open(io.BytesIO(image_data))
                except UnidentifiedImageError:
                    st.error(f"❌ Image {i+1} ('{file.name}') is not a valid image file and was skipped.")
                    continue
                except Exception:
                    st.error(f"❌ Image {i+1} ('{file.name}') is corrupted or malformed and was skipped.")
                    continue
                # ===== END FIX =====

                with st.status(f"🔍 Analyzing Image {i+1}...", expanded=False) as status:
                    try:
                        response = analyze_image(image)
                        if response and response.text:
                            conf = extract_confidence(response.text)
                            clean_text = re.sub(
                                r'Confidence Score:\s*\b(100|[0-9]{1,2})(\.\d+)?\s*%',
                                '',
                                response.text,
                            ).strip()

                            res_entry = {
                                "image": image,
                                "confidence": conf,
                                "clean_text": clean_text,
                                "original_index": i + 1,
                                "image_name": file.name,
                            }
                            st.session_state.analysis_results.append(res_entry)
                            save_to_history(image, conf, clean_text, file.name)
                            status.update(label=f"✅ Image {i+1} Analyzed", state="complete")
                        else:
                            st.error(f"Could not analyze image {i+1}")
                    except Exception as e:
                        st.error(f"Error analyzing image {i+1}: {e}")

            progress_bar.progress(1.0, text="✅ All images analyzed!")

# ================= SESSION STATE DEFAULTS =================
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []
if "view_history" not in st.session_state:
    st.session_state.view_history = None

# ================= SIDEBAR HISTORY (per-user) =================
with st.sidebar:
    st.markdown("---")
    st.header(f"📜 History — {current_user}")
    history = load_history()

    if not history:
        st.info("No past analyses found.")
    else:
        if st.button("Clear History"):
            clear_history()
            st.rerun()

        for item in history:
            if st.button(
                f"{item['timestamp']}\n{item['image_name']}",
                key=item['id'],
                use_container_width=True,
            ):
                st.session_state.view_history = item

        if st.session_state.view_history:
            if st.button("⬅️ Back to Current", use_container_width=True):
                st.session_state.view_history = None
                st.rerun()

# ================= DISPLAY RESULTS =================
results_to_show = []
if st.session_state.view_history:
    h = st.session_state.view_history
    try:
        results_to_show = [{
            "image": Image.open(h['image_path']),
            "confidence": h['confidence'],
            "clean_text": h['text'],
            "title": f"Historical Report: {h['image_name']}",
            "timestamp": h['timestamp'],
            "image_name": h['image_name'],
        }]
    except Exception:
        st.error("Could not load historical image. The file may have been moved or deleted.")
    if st.button("⬅️ Back to Current Results"):
        st.session_state.view_history = None
        st.rerun()
else:
    results_to_show = [
        {**r, "title": f"Analysis for Image {r['original_index']}", "timestamp": None}
        for r in st.session_state.analysis_results
    ]

for result in results_to_show:
    st.markdown("---")
    if result.get("timestamp"):
        st.caption(f"Analysis from {result['timestamp']}")
    st.title(result['title'])
    st.image(result['image'], width=300)

    if result['confidence'] is not None:
        st.progress(result['confidence'] / 100)
        st.markdown(f"### Confidence Score: **{result['confidence']:.2f}%**")

        if result['confidence'] > 80:
            st.success("High Confidence Prediction")
        elif result['confidence'] > 50:
            st.info("Moderate Confidence Prediction")
        else:
            st.warning("⚠️ Low Confidence Prediction")
    else:
        st.warning("⚠️ Confidence score not found in AI response")

    st.write(result['clean_text'])

    pdf_bytes = generate_pdf(result['clean_text'], result['confidence'])
    st.download_button(
        label="📥 Download Report (PDF)",
        data=bytes(pdf_bytes),
        file_name=f"analysis_{result.get('image_name', 'report')}.pdf",
        mime="application/pdf",
    )
    st.info("⚠️ Disclaimer: Consult with a Doctor before making any decisions")