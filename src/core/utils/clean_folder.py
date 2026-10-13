"""Backwards compatibility alias for clean_folder.

This module re-exports `clean_folder` from `temp_file_cleaner`
to maintain backwards compatibility with existing imports.
"""

from src.core.utils.temp_file_cleaner import clean_folder, clean_temp_dir

__all__ = ["clean_folder", "clean_temp_dir"]

if __name__ == "__main__":
    clean_temp_dir()
