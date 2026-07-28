"""Typography tokens for iframe panels and Plotly charts."""

from functools import lru_cache
from pathlib import Path
from typing import Final

TYPOGRAPHY_CSS_PATH: Final[Path] = (
    Path(__file__).resolve().parent / "typography.css"
)

PLOTLY_FONT_SIZE: Final[int] = 14
PLOTLY_FONT_SIZE_TICK: Final[int] = 13
PLOTLY_FONT_SIZE_TITLE: Final[int] = 14
PLOTLY_FONT_SIZE_ANNOTATION: Final[int] = 15
PLOTLY_FONT_SIZE_CAPTION: Final[int] = 12


@lru_cache(maxsize=1)
def typography_css_variables() -> str:
    """Return the shared :root typography block for iframe injection."""
    try:
        return TYPOGRAPHY_CSS_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"Unable to load typography tokens from {TYPOGRAPHY_CSS_PATH}."
        ) from exc
