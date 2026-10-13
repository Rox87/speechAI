"""Real-time Text-to-Speech synthesis and playback using Google TTS (gTTS)."""

from __future__ import annotations

import functools
import sys
import time
from typing import Optional

from src.core.logger import logger
from src.core.config import config
from src.core.tts.synthesizer import synthesize_to_bytes
from src.core.audio.player import player


def time_elapsed(func):
    """Decorator to measure and log function execution latency."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info(f"[{func.__name__}] Time elapsed: {duration:.3f} seconds")
        return result
    return wrapper


@time_elapsed
def speak(text: str, lang: Optional[str] = None) -> bool:
    """Synthesize text using gTTS and immediately play it.

    Args:
        text: Text to speak.
        lang: Language code (defaults to config.gtts_language).

    Returns:
        bool: True if played successfully, False otherwise.
    """
    if not text or not text.strip():
        return False

    logger.info(f"Speaking with gTTS ({lang or config.gtts_language}): '{text}'")
    audio_buffer = synthesize_to_bytes(text, engine="gtts")
    if not audio_buffer:
        logger.error("Failed to synthesize audio with gTTS.")
        return False

    return player.play(audio_buffer, block=True)


if __name__ == "__main__":
    sample_text = sys.argv[1] if len(sys.argv) > 1 else "Olá! Este é um teste do sintetizador de voz do Google."
    speak(sample_text)
