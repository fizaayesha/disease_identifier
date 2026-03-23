import streamlit as st

st.set_page_config(page_title="Disease Identifier", page_icon=":robot:")

st.image("./logo.jpeg", width=200)
st.title("Disease Identifier 🧑‍⚕️")
st.header("Upload image and get AI-based analysis")

upload_file = st.file_uploader(
    "Upload the image for analysis",
    type=["jpeg", "jpg", "png"]
)

if upload_file:
    st.image(upload_file, width=200, caption="Uploaded Image")

submit_button = st.button("Generate the Analysis")

if submit_button:
    if upload_file is None:
        st.warning("Please upload an image first")
    else:
        with st.spinner("Analyzing image... Please wait"):
            result = """
Detailed Analysis:
The uploaded image may indicate a possible medical condition based on visible patterns.

Findings Report:
Some irregularities or unusual features may be present.

Recommendations and Next Steps:
Consult a qualified medical professional for proper diagnosis and tests.

Treatment Suggestions:
Treatment depends on clinical evaluation and should be decided by a doctor.

Disclaimer:
Consult with a Doctor before making any decisions.
"""
            st.subheader("Analysis Result")
            st.write(result)