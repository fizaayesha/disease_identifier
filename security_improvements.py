import logging
import sys
from functools import wraps
from typing import Any, Callable
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('disease_identifier.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class SecurityHeadersConfig:
    """Production-ready security headers configuration."""

    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }

    @staticmethod
    def get_headers() -> dict:
        """Return security headers for HTTP responses."""
        return SecurityHeadersConfig.SECURITY_HEADERS.copy()


class SanitizedErrorHandler:
    """Sanitize error messages to prevent information disclosure."""

    SENSITIVE_PATTERNS = [
        'password',
        'token',
        'secret',
        'api_key',
        'credential',
        'auth',
    ]

    @staticmethod
    def sanitize_error_message(error_message: str, include_trace: bool = False) -> str:
        """
        Sanitize error message to remove sensitive information.

        Args:
            error_message: Raw error message
            include_trace: Whether to include stack trace (False for production)

        Returns:
            Sanitized error message safe for client response
        """
        if not error_message:
            return "An error occurred. Please try again."

        message_lower = error_message.lower()

        for pattern in SanitizedErrorHandler.SENSITIVE_PATTERNS:
            if pattern in message_lower:
                logger.warning(f"Potential sensitive info in error: {pattern}")
                return "An error occurred. Please try again."

        if 'traceback' in message_lower or 'stack' in message_lower:
            logger.error(f"Raw error: {error_message}")
            return "An error occurred. Please try again."

        return error_message[:100]

    @staticmethod
    def log_error_with_context(error: Exception, context: dict = None) -> None:
        """
        Log error with full context for debugging.

        Args:
            error: Exception that occurred
            context: Additional context information
        """
        ctx_str = f" | Context: {context}" if context else ""
        logger.error(f"Exception: {type(error).__name__} - {str(error)}{ctx_str}", exc_info=True)


class InputValidator:
    """Validate and sanitize user inputs."""

    MAX_USERNAME_LENGTH = 50
    MAX_PASSWORD_LENGTH = 256
    MAX_FILE_SIZE = 5 * 1024 * 1024
    MAX_STRING_LENGTH = 1000

    DANGEROUS_CHARS = ['<', '>', '"', "'", '&', '%', '\\', '\x00']

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username format and length."""
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(username) > InputValidator.MAX_USERNAME_LENGTH:
            return False, f"Username must not exceed {InputValidator.MAX_USERNAME_LENGTH} characters."
        if any(char in username for char in InputValidator.DANGEROUS_CHARS):
            return False, "Username contains invalid characters."
        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters."
        if len(password) > InputValidator.MAX_PASSWORD_LENGTH:
            return False, f"Password must not exceed {InputValidator.MAX_PASSWORD_LENGTH} characters."
        if ' ' not in password and not any(c.isupper() for c in password):
            logger.warning("Weak password format detected (consider uppercase characters)")
        return True, ""

    @staticmethod
    def validate_input_length(input_str: str, max_length: int = MAX_STRING_LENGTH) -> tuple[bool, str]:
        """Validate input string length to prevent DoS attacks."""
        if not isinstance(input_str, str):
            return False, "Input must be a string."
        if len(input_str) > max_length:
            return False, f"Input exceeds maximum length of {max_length} characters."
        return True, ""

    @staticmethod
    def sanitize_string(input_str: str) -> str:
        """Remove potentially dangerous characters from input."""
        if not isinstance(input_str, str):
            return ""
        sanitized = input_str
        for char in InputValidator.DANGEROUS_CHARS:
            sanitized = sanitized.replace(char, '')
        return sanitized.strip()


class AuditLogger:
    """Log all state-mutating actions for audit trails."""

    @staticmethod
    def log_authentication(username: str, success: bool, ip_address: str = None) -> None:
        """Log authentication attempts."""
        status = "successful" if success else "failed"
        ip_info = f" from {ip_address}" if ip_address else ""
        logger.info(f"Authentication {status} for user: {username}{ip_info}")

    @staticmethod
    def log_file_upload(username: str, filename: str, file_size: int, status: str) -> None:
        """Log file upload actions."""
        logger.info(f"File upload by {username}: {filename} ({file_size} bytes) - {status}")

    @staticmethod
    def log_analysis(username: str, image_name: str, confidence: float = None) -> None:
        """Log medical image analysis actions."""
        conf_str = f" with confidence {confidence:.2f}%" if confidence else ""
        logger.info(f"Image analysis by {username}: {image_name}{conf_str}")

    @staticmethod
    def log_history_action(username: str, action: str) -> None:
        """Log history-related actions."""
        logger.info(f"History action by {username}: {action}")


def require_auth(func: Callable) -> Callable:
    """Decorator to enforce authentication on endpoints."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'authenticated_user' not in kwargs:
            logger.warning(f"Unauthorized access attempt to {func.__name__}")
            raise PermissionError("Authentication required")
        return func(*args, **kwargs)
    return wrapper


def with_error_handling(func: Callable) -> Callable:
    """Decorator for centralized error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            SanitizedErrorHandler.log_error_with_context(e, {'function': func.__name__})
            sanitized_msg = SanitizedErrorHandler.sanitize_error_message(str(e))
            raise RuntimeError(sanitized_msg) from e
    return wrapper


def with_input_validation(func: Callable) -> Callable:
    """Decorator for input validation on endpoints."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, str):
                is_valid, error_msg = InputValidator.validate_input_length(value)
                if not is_valid:
                    logger.warning(f"Input validation failed for {key}: {error_msg}")
                    raise ValueError(error_msg)
        return func(*args, **kwargs)
    return wrapper
