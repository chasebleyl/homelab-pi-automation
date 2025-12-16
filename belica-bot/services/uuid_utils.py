"""Utility functions for UUID validation and normalization."""


def normalize_uuid(uuid_str: str) -> str | None:
    """
    Normalize a UUID string to standard format with dashes.
    
    Handles:
    - UUID with dashes: "b16d580e-087c-4cbd-83ee-e9d8e3a8f84c"
    - UUID without dashes: "b16d580e087c4cbd83eee9d8e3a8f84c"
    
    Args:
        uuid_str: The UUID string to normalize
        
    Returns:
        Normalized UUID string with dashes, or None if invalid
    """
    uuid_str = uuid_str.strip().lower()
    uuid_no_dashes = uuid_str.replace("-", "")
    
    # Validate UUID format (32 hex characters)
    if len(uuid_no_dashes) != 32 or not all(c in "0123456789abcdef" for c in uuid_no_dashes):
        return None
    
    # Format as UUID with dashes if needed
    if "-" not in uuid_str:
        return f"{uuid_no_dashes[:8]}-{uuid_no_dashes[8:12]}-{uuid_no_dashes[12:16]}-{uuid_no_dashes[16:20]}-{uuid_no_dashes[20:]}"
    else:
        return uuid_str


def validate_uuid(uuid_str: str) -> bool:
    """
    Validate that a string is a valid UUID format.
    
    Args:
        uuid_str: The string to validate
        
    Returns:
        True if valid UUID format, False otherwise
    """
    return normalize_uuid(uuid_str) is not None

