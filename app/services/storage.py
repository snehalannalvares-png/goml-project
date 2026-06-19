import mimetypes
import os

# Known types we expect, but we accept anything that comes in
_MIME_OVERRIDES = {
    "opus": "audio/ogg; codecs=opus",
    "mid": "audio/midi",
    "midi": "audio/midi",
    "wav": "audio/wav",
}


def build_s3_prefix(user_id: str, session_id: str) -> str:
    return f"/{user_id}/{session_id}/"


def build_s3_key(user_id: str, session_id: str, filename: str) -> str:
    return f"{user_id}/{session_id}/{filename}"


def resolve_file_type(filename: str) -> str:
    """Return the lowercased extension (without dot), or 'bin' if unknown."""
    ext = os.path.splitext(filename)[1].lstrip(".").lower()
    return ext if ext else "bin"


def content_type_for(filename: str) -> str:
    ext = resolve_file_type(filename)
    if ext in _MIME_OVERRIDES:
        return _MIME_OVERRIDES[ext]
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"
