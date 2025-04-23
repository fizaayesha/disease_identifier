import streamlit as st
from pathlib import Path
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
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
    },        {
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

3. Recommnedations and Next Steps: Based on your analysis, suggest potential next steps, including for the tests and treatment ass applicable.

4. Treatment Suggestions: If appropriate, recommend possible treatment options or interventions.

Important Notes:
1. Scope of Response: Only respond if the image pertains to human health issues.
2. Clarity of Image: In cases where the image quality impedes clear analysis, note that certain aspects are 'Unable to be determined based on the provided image.'
3. Disclaimer: Accompany your analysis with the disclaimer "Consult with a Doctor before making any decisions"
4. Your insights are invaluable in guiding clinical decisions. Please proceed with the analysis, adhering to the structured approach outlined above
Please provide me an output response with these 4 headings Detailed Analysis,Findings Report, Recommnedations and Next Steps, Treatment Suggestions.
"""

model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config,safety_settings=safety_settings)

st.set_page_config(page_title="Disease Identifier", page_icon=":robot")

st.image("./logo.jpeg", width=200)

st.title("Disease Identifier🧑‍⚕️")

st.header("Welcome to the Disease Identifier App! 🌟. It helps the user to identify the disease and suggests the treatmnet as well!")
  
upload_file = st.file_uploader("Upload the image of the disease for the analysis", type=["jpeg", "jpg", "png", "svg"])

if upload_file:
    st.image(upload_file,width=200, caption="Uploaded Image")

submit_button = st.button("Generate the Analysis")\

if submit_button:
    image_data=upload_file.getvalue()



    image_parts = [
        {
            "mime_type":"image/jpeg",
            "data": image_data
        }
    ]
    prompt_parts = [
        image_parts[0],
        system_prompt,
    ]

    st.image(image_data, width=300)
    response = model.generate_content(prompt_parts)
    if response:
        st.title("Here is the analysis based on your image")
        st.write(response.text)

    # print(response.text)


