import google.generativeai as genai
import streamlit as st
import re
import logging
from google.api_core.exceptions import (
    ResourceExhausted,
    PermissionDenied,
    DeadlineExceeded,
    InvalidArgument,
)

logger = logging.getLogger(__name__)

def configure_ai():
    if "GOOGLE_API_KEY" not in st.secrets:
        return False
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    return True

generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

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

def extract_confidence(text):
    match = re.search(r'\b(100|[0-9]{1,2})(\.\d+)?\s*%', text)
    if match:
        return float(match.group(0).replace('%', ''))
    return None

def analyze_image(image):
    """
    Analyze a medical image using Gemini API with granular error handling.

    Args:
        image: PIL Image object to analyze

    Returns:
        API response object or None if an error occurred

    Raises:
        Logs specific error types for monitoring and debugging:
        - ResourceExhausted: API quota exceeded
        - PermissionDenied: Invalid or missing API credentials
        - DeadlineExceeded: Request timeout
        - InvalidArgument: Invalid input parameters
    """
    try:
        # Using 1.5-flash as it's the current stable multimodal model
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(
            [system_prompt, image],
            generation_config=generation_config
        )
        return response
    except ResourceExhausted as e:
        error_msg = 'API quota exhausted. Please try again later.'
        logger.error(f'API quota exhausted: {str(e)}')
        raise Exception(error_msg) from e
    except PermissionDenied as e:
        error_msg = 'API authentication failed. Check your API key configuration.'
        logger.error(f'API authentication failed: {str(e)}')
        raise Exception(error_msg) from e
    except DeadlineExceeded as e:
        error_msg = 'Request timed out. Try with a smaller or lower resolution image.'
        logger.error(f'Request deadline exceeded: {str(e)}')
        raise Exception(error_msg) from e
    except InvalidArgument as e:
        error_msg = f'Invalid input detected: {str(e)}'
        logger.error(f'Invalid argument to API: {str(e)}')
        raise Exception(error_msg) from e
    except Exception as e:
        error_msg = f'Unexpected API error: {str(e)}'
        logger.error(f'Unexpected error during image analysis: {str(e)}', exc_info=True)
        raise
