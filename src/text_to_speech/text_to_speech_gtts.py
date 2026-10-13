"""Google Text-to-Speech (gTTS) module and CLI script."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Union

from src.core.tts.synthesizer import synthesize_with_gtts
from src.realtime_processing.realtime_gtts import speak, time_elapsed


def save_speech(
    text: str,
    output_path: Union[str, Path] = "output.mp3",
    lang: Optional[str] = None,
) -> Optional[Path]:
    """Synthesize text and save to the specified file path."""
    return synthesize_with_gtts(text, output_file=output_path, lang=lang)


if __name__ == "__main__":
    sample_text = sys.argv[1] if len(sys.argv) > 1 else "Olá, este é um exemplo com Google TTS."
    speak(sample_text)
