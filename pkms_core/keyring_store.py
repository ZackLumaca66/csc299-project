from __future__ import annotations
import typing

try:
    import keyring
except Exception:
    keyring = None  # type: ignore

SERVICE_NAME = "pkms_core_openai"

def available() -> bool:
    return keyring is not None

def set_api_key(key: str) -> bool:
    """Store API key in OS keyring. Returns True on success, False otherwise."""
    if not keyring:
        return False
    try:
        keyring.set_password(SERVICE_NAME, 'OPENAI_API_KEY', key)
        return True
    except Exception:
        return False

def get_api_key() -> typing.Optional[str]:
    if not keyring:
        return None
    try:
        return keyring.get_password(SERVICE_NAME, 'OPENAI_API_KEY')
    except Exception:
        return None

def delete_api_key() -> bool:
    if not keyring:
        return False
    try:
        keyring.delete_password(SERVICE_NAME, 'OPENAI_API_KEY')
        return True
    except Exception:
        return False
