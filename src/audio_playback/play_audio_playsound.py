"""Audio playback script using playsound library."""

from __future__ import annotations

import sys
from pathlib import Path
from src.core.logger import logger
from src.core.audio.player import play_with_playsound


def play(file_path: str = "output.mp3") -> bool:
    """Play an audio file using playsound."""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Audio file '{file_path}' does not exist.")
        return False
    return play_with_playsound(str(path))


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "output.mp3"
    play(target)
