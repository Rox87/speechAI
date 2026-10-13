"""OpenAI Text-to-Speech synthesis module and CLI script."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Union

from src.core.tts.synthesizer import synthesize_with_openai
from src.core.logger import logger


def save_speech(
    text: str,
    output_path: Union[str, Path] = "output.mp3",
    voice: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[Path]:
    """Synthesize text using OpenAI TTS and save to file."""
    return synthesize_with_openai(text, output_file=output_path, voice=voice, model=model)


if __name__ == "__main__":
    sample_text = sys.argv[1] if len(sys.argv) > 1 else "Hello world! How are you?"
    out = sys.argv[2] if len(sys.argv) > 2 else "output.mp3"
    result = save_speech(sample_text, output_path=out)
    if result:
        logger.info(f"Generated speech saved to: {result}")
    else:
        logger.error("Failed to generate speech. Check OPENAI_API_KEY in .env.")