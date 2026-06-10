"""
PDF input validation module for disease_identifier.

Enforces limits on PDF file size and page count to prevent
out-of-memory crashes and denial-of-service attacks.
"""

import PyPDF2
import io
import logging

logger = logging.getLogger(__name__)

# Configuration constants for PDF processing limits
MAX_PDF_PAGES = 50
MAX_FILE_SIZE_MB = 50

# File size in bytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class PDFValidationError(Exception):
    """Raised when PDF validation fails."""
    pass


def get_pdf_page_count(pdf_bytes):
    """
    Extract page count from PDF bytes without loading entire file into memory.

    Args:
        pdf_bytes: Bytes object containing PDF data

    Returns:
        Integer page count

    Raises:
        PDFValidationError: If PDF is malformed or unreadable
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        return len(pdf_reader.pages)
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f'Failed to read PDF: {str(e)}')
        raise PDFValidationError(f'Malformed PDF file: {str(e)}') from e
    except Exception as e:
        logger.error(f'Unexpected error reading PDF: {str(e)}')
        raise PDFValidationError(f'Could not process PDF: {str(e)}') from e


def validate_pdf_file(pdf_file):
    """
    Validate PDF file for size and page count limits.

    Args:
        pdf_file: Streamlit UploadedFile object

    Returns:
        Dictionary with validation result:
        {
            'valid': bool,
            'page_count': int (only if valid),
            'error': str (only if invalid)
        }

    Enforces:
        - File size limit: 50 MB
        - Page count limit: 50 pages
    """
    validation_result = {
        'valid': False,
        'page_count': None,
        'error': None
    }

    # Check file size
    if pdf_file.size > MAX_FILE_SIZE_BYTES:
        validation_result['error'] = (
            f'PDF exceeds {MAX_FILE_SIZE_MB}MB limit. '
            f'File size: {pdf_file.size / (1024 * 1024):.2f}MB'
        )
        logger.warning(f'PDF file too large: {pdf_file.name} ({pdf_file.size} bytes)')
        return validation_result

    # Check page count
    try:
        pdf_bytes = pdf_file.getvalue()
        page_count = get_pdf_page_count(pdf_bytes)

        if page_count > MAX_PDF_PAGES:
            validation_result['error'] = (
                f'PDF exceeds {MAX_PDF_PAGES} pages limit. '
                f'Pages: {page_count}'
            )
            logger.warning(f'PDF has too many pages: {pdf_file.name} ({page_count} pages)')
            return validation_result

        # Validation successful
        validation_result['valid'] = True
        validation_result['page_count'] = page_count
        logger.info(f'PDF validated successfully: {pdf_file.name} ({page_count} pages)')
        return validation_result

    except PDFValidationError as e:
        validation_result['error'] = str(e)
        return validation_result
    except Exception as e:
        validation_result['error'] = f'Error validating PDF: {str(e)}'
        logger.error(f'Unexpected error validating PDF: {str(e)}', exc_info=True)
        return validation_result
