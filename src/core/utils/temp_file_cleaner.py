"""Utility functions for safely managing and cleaning temporary audio files."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional, Union, List
from src.core.logger import logger
from src.core.config import config


def clean_folder(
    folder_path: Union[str, Path] = None,
    pattern: str = "*",
    max_age_seconds: Optional[float] = None,
) -> int:
    """Safely delete files in the specified directory.

    Args:
        folder_path: Directory path to clean. Defaults to configured temp_dir.
        pattern: Glob pattern to filter files (e.g. '*.mp3', '*.wav'). Defaults to '*'.
        max_age_seconds: Only delete files older than this age in seconds. None deletes all matching files.

    Returns:
        int: Number of files successfully deleted.
    """
    target_path = Path(folder_path) if folder_path is not None else config.temp_dir

    if not target_path.exists():
        logger.warning(f"Cleanup directory does not exist: {target_path}")
        return 0

    if not target_path.is_dir():
        logger.error(f"Cleanup path is not a directory: {target_path}")
        return 0

    deleted_count = 0
    now = time.time()

    # Filter only files matching the pattern
    files: List[Path] = [f for f in target_path.glob(pattern) if f.is_file()]

    if not files:
        logger.debug(f"No files matching '{pattern}' found in {target_path}")
        return 0

    for file in files:
        # Ignore .gitkeep or hidden files
        if file.name.startswith("."):
            continue

        try:
            if max_age_seconds is not None:
                file_age = now - file.stat().st_mtime
                if file_age < max_age_seconds:
                    continue

            file.unlink()
            deleted_count += 1
            logger.debug(f"Deleted temporary file: {file.name}")
        except PermissionError:
            logger.warning(f"File locked or permission denied: {file.name}")
        except Exception as e:
            logger.warning(f"Could not delete {file.name}: {e}")

    if deleted_count > 0:
        logger.info(f"Cleaned {deleted_count} file(s) from {target_path}")

    return deleted_count


def clean_temp_dir() -> int:
    """Clean all temporary audio files in the default configured temp directory."""
    return clean_folder(config.temp_dir)


if __name__ == "__main__":
    clean_temp_dir()
