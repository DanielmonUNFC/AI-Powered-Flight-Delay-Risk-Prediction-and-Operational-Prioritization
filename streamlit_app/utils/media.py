"""Asset loading helpers for static dashboard media."""

from __future__ import annotations

import base64
import html
import mimetypes
from pathlib import Path

ASSETS_ROOT = Path(__file__).resolve().parent.parent / "assets"


def asset_path(*parts: str) -> Path:
    """Resolve a path under the dashboard assets directory."""
    return ASSETS_ROOT.joinpath(*parts)


def file_to_data_uri(path: Path) -> str | None:
    """Encode a local image file as a data URI, or return None if missing."""
    if not path.is_file():
        return None

    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type:
        suffix = path.suffix.lower()
        if suffix == ".svg":
            mime_type = "image/svg+xml"
        else:
            mime_type = "application/octet-stream"

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def initials_from_name(name: str) -> str:
    """Build up to two uppercase initials from a display name."""
    parts = [part for part in name.split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()


def render_initials_avatar(name: str) -> str:
    """Return HTML for a circular initials avatar fallback."""
    initials = html.escape(initials_from_name(name))
    return (
        f'<div class="project-team__avatar project-team__avatar--fallback" '
        f'aria-hidden="true">{initials}</div>'
    )
