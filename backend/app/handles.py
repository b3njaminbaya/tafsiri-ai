from typing import Optional


def public_handle(display_name: Optional[str], email: str) -> str:
    """Prefer the user's chosen display name; otherwise fall back to the
    email local-part — enough for public attribution/recognition without
    exposing a full email address (including provider domain).
    """
    return display_name or email.split("@")[0]
