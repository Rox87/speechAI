"""Real-time speech-to-text transcription module."""

from __future__ import annotations

import time
from typing import Optional, Callable
from src.core.logger import logger
from src.core.config import config
from src.core.audio.recorder import record_audio_to_bytes
from src.core.audio.audio_transcriber import transcribe_audio


def record_and_transcribe_loop(
    chunk_duration: Optional[float] = None,
    on_transcript: Optional[Callable[[str], None]] = None,
    max_iterations: Optional[int] = None,
) -> None:
    """Continuously record audio chunks and transcribe in real-time.

    Args:
        chunk_duration: Duration of each chunk in seconds. Defaults to config.record_duration.
        on_transcript: Optional callback function receiving transcribed text.
        max_iterations: Optional maximum loop cycles before stopping.
    """
    duration = chunk_duration or config.record_duration
    logger.info(f"Starting real-time audio transcription ({duration}s chunks)... Press Ctrl+C to stop.")

    iteration = 0
    try:
        while max_iterations is None or iteration < max_iterations:
            iteration += 1
            start_t = time.time()

            # Record chunk
            audio_buffer = record_audio_to_bytes(duration=duration)

            # Transcribe
            text = transcribe_audio(audio_buffer, engine=config.stt_engine)
            elapsed = time.time() - start_t

            if text and text.strip():
                logger.info(f"[{elapsed:.2f}s] Transcription: {text}")
                if on_transcript:
                    on_transcript(text)
            else:
                logger.debug(f"[{elapsed:.2f}s] No speech detected in chunk.")

    except KeyboardInterrupt:
        logger.info("\nReal-time transcription stopped by user.")
    except Exception as e:
        logger.error(f"Error in transcription loop: {e}")


# Backwards compatibility function
def record_and_transcribe(chunk_duration: float = 5.0) -> None:
    """Legacy wrapper for real-time transcription."""
    record_and_transcribe_loop(chunk_duration=chunk_duration)


if __name__ == "__main__":
    record_and_transcribe_loop()
