import streamlit as st
import io
import re
import csv
from PIL import Image, UnidentifiedImageError
from io import StringIO
from ai_engine import configure_ai, analyze_image, extract_confidence
from pdf_utils import generate_pdf
from history_manager import load_history, save_to_history, clear_all_history

# ================= API INITIALIZATION =================
if not configure_ai():
    st.error("API Key not found. Please set GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

# ================= STREAMLIT CONFIG =================
st.set_page_config(page_title="Disease Identifier", page_icon="🧑‍⚕️", layout="wide")

# Theme state
if 'theme_mode' not in st.session_state:
    st.session_state.theme_mode = True

# Theme styling
theme_colors = {
    True: {'bg': '#1E1E1E', 'text': '#FFFFFF'},
    False: {'bg': '#FFFFFF', 'text': '#000000'}
}[st.session_state.theme_mode]

st.markdown(f"""
<style>
    .stApp {{ background-color: {theme_colors['bg']}; color: {theme_colors['text']}; }}
    .main-header {{ text-align: center; padding: 20px; }}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.image("./logo.jpeg", width=100)
    st.title("Settings & History")
    st.toggle("Dark Mode", key="theme_mode")
    
    st.divider()
    st.header("📜 Analysis History")
    history = load_history()
    
    if history:
        if st.button("🗑️ Clear All History", use_container_width=True):
            clear_all_history()
            st.rerun()
            
        # CSV Export
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "image_name", "confidence", "text"])
        writer.writeheader()
        for item in history:
            writer.writerow({
                "timestamp": item["timestamp"],
                "image_name": item["image_name"],
                "confidence": item["confidence"],
                "text": item["text"].replace("\n", " ")
            })
        
        st.download_button(
            label="📊 Export History (CSV)",
            data=output.getvalue(),
            file_name="analysis_history.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.divider()
        for item in history:
            if st.button(f"{item['timestamp']}\n{item['image_name']}", key=item['id'], use_container_width=True):
                st.session_state.view_history = item

# ================= MAIN UI =================
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.title("🧑‍⚕️ Disease Identifier")
st.markdown("### AI-Powered Medical Image Analysis")
st.caption("Upload medical images (X-rays, skin scans, etc.) for instant AI insights.")
st.markdown("</div>", unsafe_allow_html=True)

upload_files = st.file_uploader(
    "Upload images (Max 5MB each)",
    type=["jpeg", "jpg", "png"],
    accept_multiple_files=True
)

if upload_files:
    MAX_FILE_SIZE = 5 * 1024 * 1024
    valid_files = [f for f in upload_files if f.size <= MAX_FILE_SIZE]
    
    if len(valid_files) < len(upload_files):
        st.warning(f"⚠️ {len(upload_files) - len(valid_files)} files exceeded the 5MB limit and were skipped.")
    
    if valid_files:
        st.subheader("🖼️ Selected Images")
        cols = st.columns(4)
        for i, file in enumerate(valid_files):
            with cols[i % 4]:
                st.image(file, use_container_width=True, caption=f"Image {i+1}")
        
        if st.button("🚀 Generate Analysis", type="primary", use_container_width=True):
            st.session_state.view_history = None
            st.session_state.analysis_results = []
            
            for i, file in enumerate(valid_files):
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
                            clean_text = re.sub(r'Confidence Score:\s*\b(100|[0-9]{1,2})(\.\d+)?\s*%', '', response.text).strip()
                            
                            res_entry = {
                                "image": image,
                                "confidence": conf,
                                "clean_text": clean_text,
                                "original_index": i + 1,
                                "image_name": file.name
                            }
                            st.session_state.analysis_results.append(res_entry)
                            save_to_history(image, conf, clean_text, file.name)
                            status.update(label=f"✅ Image {i+1} Analyzed", state="complete")
                        else:
                            st.error(f"Could not analyze image {i+1}")
                    except Exception as e:
                        st.error(f"Error analyzing image {i+1}: {e}")

# ================= DISPLAY RESULTS =================
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []
if "view_history" not in st.session_state:
    st.session_state.view_history = None

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
    except Exception:
        st.error("Could not load historical image. The file may have been moved or deleted.")
    if st.button("⬅️ Back to Current Results"):
        st.session_state.view_history = None
        st.rerun()
else:
    results_to_show = [
        {**r, "title": f"Analysis for {r['image_name']}", "timestamp": None} 
        for r in st.session_state.analysis_results
    ]

for result in results_to_show:
    st.divider()
    if result.get("timestamp"):
        st.caption(f"📅 Analysis from {result['timestamp']}")
    
    res_col1, res_col2 = st.columns([1, 2])
    with res_col1:
        st.image(result['image'], use_container_width=True)
    
    with res_col2:
        st.header(result['title'])
        if result['confidence'] is not None:
            st.progress(result['confidence'] / 100)
            st.markdown(f"### Confidence Score: **{result['confidence']:.2f}%**")
        else:
            st.warning("⚠️ Confidence score not provided by AI")
        
        st.write(result['clean_text'])
        
        pdf_bytes = generate_pdf(result['clean_text'], result['confidence'])
        st.download_button(
            label="📥 Download Report (PDF)",
            data=bytes(pdf_bytes),
            file_name=f"analysis_{result.get('image_name', 'report')}.pdf",
            mime="application/pdf"
        )
        st.info("⚠️ Disclaimer: Consult with a Doctor before making any decisions")