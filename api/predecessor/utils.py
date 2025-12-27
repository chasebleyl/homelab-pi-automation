"""Utility functions for the Predecessor API package."""


def name_to_slug(name: str) -> str:
    """
    Convert a display name to a URL/filename-safe slug.

    Handles spaces, apostrophes, periods, ampersands, and collapses multiple dashes.

    Args:
        name: The display name (e.g., "Iggy & Scorch", "Lt. Belica", "GRIM.exe")

    Returns:
        Slug format (e.g., "iggy-scorch", "lt-belica", "grim-exe")

    Example:
        >>> name_to_slug("Iggy & Scorch")
        'iggy-scorch'
        >>> name_to_slug("Lt. Belica")
        'lt-belica'
        >>> name_to_slug("GRIM.exe")
        'grim-exe'
    """
    slug = name.lower().replace(" ", "-").replace("'", "").replace(".", "-").replace("&", "")
    # Collapse multiple consecutive dashes into single dash
    while "--" in slug:
        slug = slug.replace("--", "-")
    # Remove leading/trailing dashes
    slug = slug.strip("-")
    return slug


def calculate_per_minute(value: float | int, duration_seconds: float | int) -> float:
    """
    Calculate a per-minute rate from a total value and duration in seconds.

    Args:
        value: The total value (e.g., gold, CS, damage)
        duration_seconds: Match duration in seconds

    Returns:
        Per-minute rate. Returns 0 if duration is 0 or negative.

    Example:
        >>> calculate_per_minute(12631, 1574)  # 12631 gold over 1574 seconds
        481.5  # gold per minute
    """
    if duration_seconds <= 0:
        return 0.0
    duration_minutes = duration_seconds / 60
    return value / duration_minutes


def format_player_display_name(
    name: str | None,
    uuid: str | None,
    subscribed_name: str | None = None
) -> str:
    """
    Format a player's display name with fallback chain.

    Fallback order:
    1. API-provided name (if available)
    2. Subscribed profile name (if player is subscribed and has a stored name)
    3. Truncated UUID (if UUID available)
    4. "Unknown" (last resort)

    Args:
        name: The player's display name from API (may be None or empty)
        uuid: The player's UUID (used for fallback)
        subscribed_name: The player's name from subscribed_profiles table (optional)

    Returns:
        Display name using the fallback chain above
    """
    if name:
        return name
    if subscribed_name:
        return subscribed_name
    if uuid:
        return f"user-{uuid[:8]}..."
    return "Unknown"
