"""Real-time Text-to-Speech synthesis and playback using OpenAI TTS."""

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
def speak(
    text: str,
    voice: Optional[str] = None,
    model: Optional[str] = None,
) -> bool:
    """Synthesize text using OpenAI TTS and immediately play the result.

    Args:
        text: Text string to speak.
        voice: Voice name (nova, alloy, echo, fable, onyx, shimmer).
        model: TTS model (tts-1 or tts-1-hd).

    Returns:
        bool: True if synthesized and played successfully, False otherwise.
    """
    if not text or not text.strip():
        return False

    if not config.has_openai_key:
        logger.error("OPENAI_API_KEY is not configured in .env.")
        return False

    voice_name = voice or config.openai_tts_voice
    logger.info(f"Speaking with OpenAI TTS ({voice_name}): '{text}'")

    audio_buffer = synthesize_to_bytes(text, engine="openai")
    if not audio_buffer:
        logger.error("Failed to generate audio from OpenAI TTS.")
        return False

    return player.play(audio_buffer, block=True)


if __name__ == "__main__":
    sample_text = sys.argv[1] if len(sys.argv) > 1 else "Hello! This is a test of OpenAI Text-to-Speech."
    speak(sample_text)
