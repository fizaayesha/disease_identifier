import io
from PIL import Image, UnidentifiedImageError

MAGIC_BYTES = {
    'jpeg': [b'\xFF\xD8\xFF'],
    'png': [b'\x89PNG\r\n\x1a\n'],
}

def validate_file_magic_bytes(file_bytes: bytes, allowed_types: list) -> tuple[bool, str]:
    """
    Validate file by magic bytes instead of relying on extension.

    Args:
        file_bytes: Raw bytes of the uploaded file
        allowed_types: List of allowed file types (e.g., ['jpeg', 'png'])

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_bytes or len(file_bytes) < 8:
        return False, "File is too small to validate."

    for file_type in allowed_types:
        if file_type.lower() in ['jpg', 'jpeg']:
            for magic in MAGIC_BYTES.get('jpeg', []):
                if file_bytes[:len(magic)] == magic:
                    return True, ""
        elif file_type.lower() == 'png':
            for magic in MAGIC_BYTES.get('png', []):
                if file_bytes[:len(magic)] == magic:
                    return True, ""

    return False, f"File does not match expected format for {', '.join(allowed_types)}."


def validate_image_integrity(file_bytes: bytes) -> tuple[bool, str]:
    """
    Validate that the file can be opened as an image by PIL.

    Args:
        file_bytes: Raw bytes of the uploaded file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        image = Image.open(io.BytesIO(file_bytes))
        image.verify()
        return True, ""
    except UnidentifiedImageError:
        return False, "File is not a valid image."
    except Exception as e:
        return False, f"File is corrupted or malformed: {str(e)}"


def validate_uploaded_file(file_bytes: bytes, file_name: str, allowed_types: list) -> tuple[bool, str]:
    """
    Perform complete validation on an uploaded file.

    Checks:
    1. Magic bytes match expected format
    2. PIL can open and read the file

    Args:
        file_bytes: Raw bytes of the uploaded file
        file_name: Name of the file (for error messages)
        allowed_types: List of allowed file types (e.g., ['jpeg', 'jpg', 'png'])

    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, magic_error = validate_file_magic_bytes(file_bytes, allowed_types)
    if not is_valid:
        return False, magic_error

    is_valid, integrity_error = validate_image_integrity(file_bytes)
    if not is_valid:
        return False, integrity_error

    return True, ""
