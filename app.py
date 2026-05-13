try:
    import streamlit as st
except Exception:
    st = None

try:
    import google.generativeai as genai
except Exception:
    genai = None

import re
try:
    from PIL import Image
except Exception:
    Image = None

import io
try:
    from fpdf import FPDF
except Exception:
    FPDF = None
import os

import json
from datetime import datetime
import uuid

<<<<<<< HEAD
# Keep the app runnable in Streamlit, but allow unit tests to import `extract_confidence`
# in environments where streamlit/gemini are not installed.
if st is not None and genai is not None:
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("API Key not found. Please set GOOGLE_API_KEY in Streamlit secrets.")
        st.stop()

    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

=======
# ================= CONFIGURATION =================
>>>>>>> bfc743c (Improve confidence parsing; tolerant cleaning; add tests)
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

<<<<<<< HEAD
# System prompt for Gemini
=======
# If running inside Streamlit, ensure API key is present and configure Gemini
if st is not None:
    if "GOOGLE_API_KEY" not in getattr(st, "secrets", {}):
        st.error("API Key not found. Please set GOOGLE_API_KEY in Streamlit secrets.")
        st.stop()
    if genai is not None:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])


# ================= SYSTEM PROMPT =================
>>>>>>> bfc743c (Improve confidence parsing; tolerant cleaning; add tests)
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

<<<<<<< HEAD
def extract_confidence(text: str):
    """Extract confidence percentage from model output.

    Looks for the first numeric value near the word "confidence".
    Supports formats like "Confidence: 87%" and "Confidence: 0.87".
    """

    if not text:
        return None

    normalized = " ".join(str(text).split())

    patterns = [
        (
            r"(?i)\b(?:confidence(?:\s*score)?|probability|likelihood|certainty|confident)\b"
            r"\s*(?:[:\-–—=]|\bis\b)?\s*"
            r"(?:\babout\b|\baround\b|\bapproximately\b|\bapprox\.?\b)?\s*"
            r"~?\s*(\d+(?:\.\d+)?)\s*(%|percent)?",
            False,
        ),
        (
            r"(?i)(\d+(?:\.\d+)?)\s*(%|percent)?\s*"
            r"\b(?:confidence(?:\s*score)?|confident|probability|likelihood|certainty)\b",
            True,
        ),
        (
            r"(?i)\b(?:confidence(?:\s*score)?|probability|likelihood|certainty|confident)\b"
            r".*?\b(\d+(?:\.\d+)?)\s*/\s*100\b",
            False,
        ),
        (r"(?i)\b(\d{1,3}(?:\.\d+)?)\s*(%|percent)\b", False),
    ]

    candidate = None
    has_percent_symbol = False

    for pattern, number_before_keyword in patterns:
        match = re.search(pattern, normalized)
        # ================= CONFIGURATION =================
        generation_config = {
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }

        # If running inside Streamlit, ensure API key is present and configure Gemini
        if st is not None:
            if "GOOGLE_API_KEY" not in getattr(st, "secrets", {}):
                st.error("API Key not found. Please set GOOGLE_API_KEY in Streamlit secrets.")
                st.stop()
            if genai is not None:
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    Handles common variants such as:
    - 'Confidence Score: 87%'
    - 'confidence: 0.87' (interpreted as fraction)
    - '87 percent' or '87%'
    - 'Confidence is 87.5%'

    Returns a float in range 0..100 or None if not found.
    """
    if not text:
        return None

    # 1) Percent with explicit '%' sign (e.g. '87%', '100%')
    m = re.search(r"(?P<num>\d{1,3}(?:\.\d+)?)\s*%", text)
    if m:
        try:
            val = float(m.group('num'))
            return max(0.0, min(100.0, val))
        except Exception:
            pass

    # 2) Keywords with 'percent' (e.g. '87 percent')
    m = re.search(r"(?i)(?P<num>\d{1,3}(?:\.\d+)?)\s*(?:percent|per cent)\b", text)
    if m:
        try:
            val = float(m.group('num'))
            return max(0.0, min(100.0, val))
        except Exception:
            pass

    # 3) Confidence near a fractional value (e.g. 'confidence: 0.87', '.87')
    m = re.search(r"(?i)confidence[^0-9\n\r]{0,10}(?P<num>0?\.\d+)", text)
    if m:

        # ================= CONFIDENCE EXTRACTOR =================
        def extract_confidence(text):
            """Extract a confidence value from model text.

            Handles common variants such as:
            - 'Confidence Score: 87%'
            - 'confidence: 0.87' (interpreted as fraction)
            - '87 percent' or '87%'
            - 'Confidence is 87.5%'

            Returns a float in range 0..100 or None if not found.
            """
            if not text:
                return None

            # 1) Percent with explicit '%' sign (e.g. '87%', '100%')
            m = re.search(r"(?P<num>\d{1,3}(?:\.\d+)?)\s*%", text)
            if m:
                try:
                    val = float(m.group('num'))
                    return max(0.0, min(100.0, val))
                except Exception:
                    pass

            # 2) Keywords with 'percent' (e.g. '87 percent')
            m = re.search(r"(?i)(?P<num>\d{1,3}(?:\.\d+)?)\s*(?:percent|per cent)\b", text)
            if m:
                try:
                    val = float(m.group('num'))
                    return max(0.0, min(100.0, val))
                except Exception:
                    pass

            # 3) Confidence near a fractional value (e.g. 'confidence: 0.87', '.87')
            m = re.search(r"(?i)confidence[^0-9\n\r]{0,10}(?P<num>0?\.\d+)", text)
            if m:
                try:
                    val = float(m.group('num')) * 100.0
                    return max(0.0, min(100.0, val))
                except Exception:
                    pass

            # 4) Generic standalone fraction like '0.87' (prefer only if 'confidence' nearby)
            m = re.search(r"(?i)(?:confidence).{0,40}?([0]?\.?\d{1,3})", text)
            if m:
                try:
                    val = float(m.group(1))
                    if 0.0 <= val <= 1.0:
                        return val * 100.0
                    if 0.0 <= val <= 100.0:
                        return val
                except Exception:
                    pass

            return None
    }[st.session_state.theme_mode]

    # Apply CSS
<<<<<<< HEAD
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {theme_colors['bg']};
                color: {theme_colors['text']};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

=======
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {theme_colors['bg']};
            color: {theme_colors['text']};
        }}
    </style>
    """, unsafe_allow_html=True)

    # ================= UI =================
>>>>>>> bfc743c (Improve confidence parsing; tolerant cleaning; add tests)
    st.image("./logo.jpeg", width=200)
    st.title("Disease Identifier 🧑‍⚕️")
    st.header("Upload medical images to analyze diseases and get AI insights")

    upload_files = st.file_uploader(
        "Upload images",
        type=["jpeg", "jpg", "png"],
<<<<<<< HEAD
        accept_multiple_files=True,
    )
else:
    upload_files = None

# File size validation (5MB limit)
if st is not None and upload_files:

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    valid_files = []
    
    for file in upload_files:
        if file.size > MAX_FILE_SIZE:
            st.warning(f"⚠️ File '{file.name}' exceeds 5MB limit and will be skipped.")
        else:
            valid_files.append(file)
    
    if not valid_files:
        st.error("❌ No valid files to process. All files exceed 5MB limit.")
        st.stop()
    
    upload_files = valid_files

# Preview uploaded images
if st is not None:
    if upload_files:
        for i, file in enumerate(upload_files):
            st.image(file, width=200, caption=f"Image {i+1}")

submit_button = st.button("Generate Analysis") if st is not None else False

# Guard session_state usage so `import app` works when streamlit isn't installed.
if st is not None:
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = []
    if "view_history" not in st.session_state:
        st.session_state.view_history = None

    # Sidebar History
    with st.sidebar:
        st.markdown("---")
    st.header("📜 Analysis History")
    history = load_history()
    if not history:
        st.info("No past analyses found.")
    else:
        if st.button("Clear History"):
            if os.path.exists(METADATA_FILE):
                os.remove(METADATA_FILE)
            # Optionally delete images too, but for safety let's just clear metadata
            st.rerun()
            
        for item in history:
            # Display history items as buttons
            if st.button(f"{item['timestamp']}\n{item['image_name']}", key=item['id'], use_container_width=True):
                st.session_state.view_history = item

        if st.session_state.view_history:
            if st.button("⬅️ Back to Current", use_container_width=True):
                st.session_state.view_history = None
                st.rerun()

if submit_button:
    st.session_state.view_history = None # Clear history view when new analysis is triggered
    if not upload_files:
        st.error("Please upload at least one image before clicking 'Generate Analysis'.")
    else:
        st.session_state.analysis_results = [] # Reset for new batch
        for i, file in enumerate(upload_files):
            try:
                image_data = file.getvalue()
                image = Image.open(io.BytesIO(image_data))
            except Exception:
                st.error(f"Error processing image {i+1}")
                continue

            with st.spinner(f"Analyzing Image {i+1}..."):
                try:
                    model = genai.GenerativeModel('models/gemini-2.5-flash')
                    response = model.generate_content(
                        [system_prompt, image],
                        generation_config=generation_config
                    )
                except Exception as e:
                    st.error(f"API Error for Image {i+1}: {str(e)}")
                    continue
 
            if not response or not getattr(response, "text", None):
                st.error(f"Invalid response for Image {i+1}")
                continue

            confidence = extract_confidence(response.text)
    
            # Remove confidence line in a tolerant way so the report body is clean.
            confidence_line_regex = (
                r"(?mi)^\s*"
                r"confidence\s*(?:score)?\b\s*"
                r"(?:\(|\[)?\s*"
                r"(?:[:\-–—=]|\bis\b)?\s*"
                r"~?\s*"
                r"[0-9]+(?:\.[0-9]+)?\s*%?\s*"
                r"(?:percent)?\b?\s*"
                r"(?:\)|\])?"
            )

            clean_text = re.sub(confidence_line_regex, "", response.text).strip()

            # As an extra fallback, remove inline occurrences like "Confidence: 87%".
            clean_text = re.sub(
                r"(?i)\bconfidence(?:\s*score)?\b\s*(?:\(|\[)?\s*(?:[:\-–—=]|\bis\b)?\s*~?\s*"
                r"[0-9]+(?:\.[0-9]+)?\s*%?\s*"
                r"(?:percent)?\b?\s*(?:\)|\])?",
                "",
                clean_text,
            ).strip()

            st.session_state.analysis_results.append({
                "image": image,
                "confidence": confidence,
                "clean_text": clean_text,
                "original_index": i + 1
            })
            save_to_history(image, confidence, clean_text, file.name)

# Display Persisted Results
results_to_show = []
if st is not None and st.session_state.view_history:
    h = st.session_state.view_history
    try:
        results_to_show = [{
            "image": Image.open(h['image_path']),
            "confidence": h['confidence'],
            "clean_text": h['text'],
            "title": f"Historical Report: {h['image_name']}",
            "timestamp": h['timestamp']
        }]
    except Exception as e:
        st.error(f"Error loading history: {e}")
else:
    results_to_show = []
    if st is not None:
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
            st.error("Low Confidence Prediction")
    else:
        st.warning("⚠️ Confidence score not found in AI response")

    st.write(result['clean_text'])

    pdf_bytes = generate_pdf(result['clean_text'], result['confidence'])
    st.download_button(
        label="📥 Download Analysis Report as PDF",
        data=bytes(pdf_bytes),
        file_name=f"analysis_report_{result.get('original_index', 'history')}.pdf",
        mime="application/pdf"
=======
        accept_multiple_files=True
>>>>>>> bfc743c (Improve confidence parsing; tolerant cleaning; add tests)
    )

    # File size validation (5MB limit)
    if upload_files:
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
        valid_files = []
        
        for file in upload_files:
            if file.size > MAX_FILE_SIZE:
                st.warning(f"⚠️ File '{file.name}' exceeds 5MB limit and will be skipped.")
            else:
                valid_files.append(file)
        
        if not valid_files:
            st.error("❌ No valid files to process. All files exceed 5MB limit.")
            st.stop()
        
        upload_files = valid_files

    # Preview uploaded images
    if upload_files:
        for i, file in enumerate(upload_files):
            st.image(file, width=200, caption=f"Image {i+1}")

    submit_button = st.button("Generate Analysis")

    # ================= MAIN LOGIC =================
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = []
    if "view_history" not in st.session_state:
        st.session_state.view_history = None

    # Sidebar History
    with st.sidebar:
        st.markdown("---")
        st.header("📜 Analysis History")
        history = load_history()
        if not history:
            st.info("No past analyses found.")
        else:
            if st.button("Clear History"):
                if os.path.exists(METADATA_FILE):
                    os.remove(METADATA_FILE)
                # Optionally delete images too, but for safety let's just clear metadata
                st.rerun()
                
            for item in history:
                # Display history items as buttons
                if st.button(f"{item['timestamp']}\n{item['image_name']}", key=item['id'], use_container_width=True):
                    st.session_state.view_history = item

            if st.session_state.view_history:
                if st.button("⬅️ Back to Current", use_container_width=True):
                    st.session_state.view_history = None
                    st.rerun()

    if submit_button:
        st.session_state.view_history = None # Clear history view when new analysis is triggered
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
                        if genai is None:
                            raise RuntimeError("Generative API not available")
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        response = model.generate_content(
                            [system_prompt, image],
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
                clean_text = response.text or ""

                # Remove any lines that mention confidence (case-insensitive)
                clean_text = re.sub(r'(?im)^[ \t]*.*\bconfidence\b.*$', '', clean_text).strip()

                # Remove explicit percent tokens (e.g. '87%')
                clean_text = re.sub(r'(?i)\b\d{1,3}(?:\.\d+)?\s*%\b', '', clean_text)

                # Remove 'percent' spelled-out forms (e.g. '87 percent')
                clean_text = re.sub(r'(?i)\b\d{1,3}(?:\.\d+)?\s*(?:percent|per cent)\b', '', clean_text)

                # Remove fractional confidence mentions near the word 'confidence' (e.g. 'confidence: 0.87')
                clean_text = re.sub(r'(?i)confidence[^\n]{0,40}?0?\.\d+', '', clean_text)

                # Collapse excessive blank lines
                clean_text = re.sub(r'\n\s*\n+', '\n\n', clean_text).strip()

                st.session_state.analysis_results.append({
                    "image": image,
                    "confidence": confidence,
                    "clean_text": clean_text,
                    "original_index": i + 1
                })
                save_to_history(image, confidence, clean_text, file.name)

    # Display Persisted Results
    results_to_show = []
    if st.session_state.view_history:
        h = st.session_state.view_history
        try:
            results_to_show = [{
                "image": Image.open(h['image_path']),
                "confidence": h['confidence'],
                "clean_text": h['text'],
                "title": f"Historical Report: {h['image_name']}",
                "timestamp": h['timestamp']
            }]
        except Exception as e:
            st.error(f"Error loading history: {e}")
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
                st.error("Low Confidence Prediction")
        else:
            st.warning("⚠️ Confidence score not found in AI response")

        st.write(result['clean_text'])

        # ===== PDF DOWNLOAD BUTTON =====
        pdf_bytes = generate_pdf(result['clean_text'], result['confidence'])
        st.download_button(
            label="📥 Download Analysis Report as PDF",
            data=bytes(pdf_bytes),
            file_name=f"analysis_report_{result.get('original_index', 'history')}.pdf",
            mime="application/pdf"
        )

        st.warning("⚠️ Disclaimer: Consult with a Doctor before making any decisions")
