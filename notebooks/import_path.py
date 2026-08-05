"""Add notebooks/ to sys.path so config and utils imports work on Databricks Repos."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_notebook_import_path() -> None:
    """Expose notebooks/config and notebooks/utils to notebook imports."""
    candidates = (
        Path.cwd() / "notebooks",
        Path.cwd(),
    )
    for root in candidates:
        config_file = root / "config" / "project_config.py"
        if config_file.is_file():
            root_str = str(root)
            if root_str not in sys.path:
                sys.path.insert(0, root_str)
            return

    raise ImportError(
        "Could not locate notebooks/config/project_config.py. "
        "Run notebooks from the repository root or the notebooks/ directory."
    )


ensure_notebook_import_path()
