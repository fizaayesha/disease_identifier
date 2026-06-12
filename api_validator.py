import os
import google.generativeai as genai
from typing import Tuple, Dict


class APIValidator:
    """
    Validates Gemini API configuration and connectivity at application startup.

    Provides clear, actionable error messages when configuration is missing or invalid.
    """

    @staticmethod
    def validate_api_key_exists() -> Tuple[bool, str]:
        """
        Check if API key environment variable is set.

        Returns:
            (is_valid, error_message)
        """
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return (False,
                "GOOGLE_API_KEY environment variable is not set.\n\n"
                "Please set it before running the application:\n"
                "  export GOOGLE_API_KEY='your-api-key-here'\n\n"
                "Or create a .env file with:\n"
                "  GOOGLE_API_KEY=your-api-key-here\n\n"
                "Get your API key from: https://console.cloud.google.com")

        if len(api_key.strip()) < 10:
            return (False,
                f"GOOGLE_API_KEY appears to be invalid (length: {len(api_key)}).\n\n"
                "The API key should be at least 20 characters long.\n"
                "Please verify you've copied the full API key from Google Cloud console.")

        return (True, "")

    @staticmethod
    def validate_api_connectivity() -> Tuple[bool, str]:
        """
        Test that API key works and service is reachable.

        Returns:
            (is_valid, error_message)
        """
        api_key = os.getenv("GOOGLE_API_KEY")

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            response = model.generate_content(
                "Say 'OK' in one word.",
                stream=False
            )

            if not response or not response.text:
                return (False,
                    "Gemini API returned an empty response.\n\n"
                    "This may indicate:\n"
                    "- API rate limits exceeded\n"
                    "- Temporary API outage\n"
                    "- Invalid API key permissions\n\n"
                    "Please try again in a few minutes.")

            return (True, "")

        except google.api_core.exceptions.InvalidArgument as e:
            return (False,
                f"Gemini API key is invalid or lacks required permissions.\n\n"
                f"Error: {str(e)}\n\n"
                "Please verify your API key in Google Cloud console:\n"
                "https://console.cloud.google.com/apis/credentials")

        except google.api_core.exceptions.PermissionDenied as e:
            return (False,
                f"Permission denied: Your API key doesn't have the required permissions.\n\n"
                f"Error: {str(e)}\n\n"
                "Please check that your API key has access to the Generative AI API.")

        except google.api_core.exceptions.ResourceExhausted as e:
            return (False,
                f"API quota exceeded: {str(e)}\n\n"
                "Please wait a moment before retrying or check your quota limits.")

        except ConnectionError:
            return (False,
                "Cannot connect to Gemini API: Connection error.\n\n"
                "Please check:\n"
                "- Your internet connection\n"
                "- Firewall/proxy settings\n"
                "- API service status at https://status.cloud.google.com")

        except Exception as e:
            return (False,
                f"Cannot connect to Gemini API.\n\n"
                f"Error: {str(e)}\n\n"
                "Please check your internet connection and API configuration.")

    @staticmethod
    def get_full_validation_report() -> Dict:
        """
        Get comprehensive validation report including all checks.

        Returns:
            Dictionary with validation results
        """
        report = {
            "configuration_valid": False,
            "connectivity_valid": False,
            "api_key_exists": False,
            "error_messages": [],
            "all_valid": False
        }

        api_key_valid, api_key_error = APIValidator.validate_api_key_exists()
        report["api_key_exists"] = api_key_valid
        if not api_key_valid:
            report["error_messages"].append(api_key_error)
            report["all_valid"] = False
            return report

        report["configuration_valid"] = True

        connectivity_valid, connectivity_error = APIValidator.validate_api_connectivity()
        report["connectivity_valid"] = connectivity_valid
        if not connectivity_valid:
            report["error_messages"].append(connectivity_error)
            report["all_valid"] = False
            return report

        report["all_valid"] = True
        return report

    @staticmethod
    def validate_on_startup() -> bool:
        """
        Perform all validation checks required at startup.

        Raises:
            ValueError with detailed error message if validation fails

        Returns:
            True if all validations pass
        """
        report = APIValidator.get_full_validation_report()

        if not report["all_valid"]:
            error_message = "\n\n".join(report["error_messages"])
            raise ValueError(f"API Configuration Error:\n\n{error_message}")

        return True


class StreamlitAPIValidator:
    """
    Streamlit-specific validation helper for clean UI error handling.
    """

    @staticmethod
    def validate_and_display(st):
        """
        Validate API configuration and display errors in Streamlit UI if needed.

        Args:
            st: Streamlit module

        Returns:
            True if validation passes, False if it fails (user should call st.stop())
        """
        try:
            APIValidator.validate_on_startup()
            return True
        except ValueError as e:
            st.error(f"{e}", icon="⚠️")
            st.info(
                "**Setup Instructions:**\n"
                "1. Get a free Gemini API key from Google Cloud\n"
                "2. Set the GOOGLE_API_KEY environment variable\n"
                "3. Restart the application\n\n"
                "For Streamlit, add to `.streamlit/secrets.toml`:\n"
                "`GOOGLE_API_KEY = 'your-key-here'`"
            )
            return False

    @staticmethod
    def create_diagnostic_page(st):
        """
        Create a diagnostics page for troubleshooting API configuration.

        Args:
            st: Streamlit module
        """
        st.set_page_config(page_title="API Configuration Diagnostic", page_icon="⚙️")
        st.title("API Configuration Diagnostic")

        st.write("Testing your Gemini API configuration...")

        report = APIValidator.get_full_validation_report()

        col1, col2 = st.columns(2)

        with col1:
            if report["api_key_exists"]:
                st.success("✓ API Key exists")
            else:
                st.error("✗ API Key missing")

            if report["configuration_valid"]:
                st.success("✓ Configuration valid")
            else:
                st.error("✗ Configuration invalid")

        with col2:
            if report["connectivity_valid"]:
                st.success("✓ API connectivity verified")
            else:
                st.error("✗ API connectivity failed")

            if report["all_valid"]:
                st.success("✓ All checks passed")
            else:
                st.error("✗ Configuration failed")

        if report["error_messages"]:
            st.error("**Issues Found:**")
            for error in report["error_messages"]:
                st.write(error)

        st.divider()

        st.info(
            "**Setup Guide:**\n"
            "1. Visit https://console.cloud.google.com\n"
            "2. Create a new project\n"
            "3. Enable the Generative AI API\n"
            "4. Create an API key (Credentials > API Keys)\n"
            "5. Set `GOOGLE_API_KEY` environment variable\n"
            "6. Refresh this page to test again"
        )

        if st.button("Retry Validation"):
            st.rerun()
