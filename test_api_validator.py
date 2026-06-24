import pytest
import os
from unittest.mock import patch, MagicMock
from api_validator import APIValidator


class TestAPIValidator:
    """Test suite for API validation."""

    def test_missing_api_key(self):
        """Test that missing API key is detected."""
        with patch.dict(os.environ, {}, clear=True):
            valid, error = APIValidator.validate_api_key_exists()
            assert valid is False
            assert "GOOGLE_API_KEY" in error
            assert "environment variable" in error

    def test_invalid_short_api_key(self):
        """Test that short/invalid API key is rejected."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "short123"}):
            valid, error = APIValidator.validate_api_key_exists()
            assert valid is False
            assert "invalid" in error.lower()
            assert "length" in error

    def test_valid_api_key_format(self):
        """Test that properly formatted API key passes initial validation."""
        test_key = "a" * 40  # 40 character key
        with patch.dict(os.environ, {"GOOGLE_API_KEY": test_key}):
            valid, error = APIValidator.validate_api_key_exists()
            assert valid is True
            assert error == ""

    def test_api_connectivity_missing_key(self):
        """Test connectivity check when key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            valid, error = APIValidator.validate_api_connectivity()
            assert valid is False

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_valid_api_connectivity(self, mock_configure, mock_model_class):
        """Test successful API connectivity."""
        mock_response = MagicMock()
        mock_response.text = "OK"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        test_key = "a" * 40
        with patch.dict(os.environ, {"GOOGLE_API_KEY": test_key}):
            valid, error = APIValidator.validate_api_connectivity()
            assert valid is True
            assert error == ""
            mock_configure.assert_called_once_with(api_key=test_key)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_empty_api_response(self, mock_configure, mock_model_class):
        """Test handling of empty API response."""
        mock_response = MagicMock()
        mock_response.text = ""

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        test_key = "a" * 40
        with patch.dict(os.environ, {"GOOGLE_API_KEY": test_key}):
            valid, error = APIValidator.validate_api_connectivity()
            assert valid is False
            assert "empty response" in error.lower()

    def test_full_validation_report_missing_key(self):
        """Test full report when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            report = APIValidator.get_full_validation_report()
            assert report["api_key_exists"] is False
            assert report["configuration_valid"] is False
            assert report["connectivity_valid"] is False
            assert report["all_valid"] is False
            assert len(report["error_messages"]) > 0

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_full_validation_report_success(self, mock_configure, mock_model_class):
        """Test full report when all validations pass."""
        mock_response = MagicMock()
        mock_response.text = "OK"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        test_key = "a" * 40
        with patch.dict(os.environ, {"GOOGLE_API_KEY": test_key}):
            report = APIValidator.get_full_validation_report()
            assert report["api_key_exists"] is True
            assert report["configuration_valid"] is True
            assert report["connectivity_valid"] is True
            assert report["all_valid"] is True

    def test_startup_validation_fails(self):
        """Test that startup validation raises error on failure."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                APIValidator.validate_on_startup()

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_startup_validation_succeeds(self, mock_configure, mock_model_class):
        """Test that startup validation succeeds with valid config."""
        mock_response = MagicMock()
        mock_response.text = "OK"

        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        test_key = "a" * 40
        with patch.dict(os.environ, {"GOOGLE_API_KEY": test_key}):
            result = APIValidator.validate_on_startup()
            assert result is True
