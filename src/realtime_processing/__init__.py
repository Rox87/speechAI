"""Real-time audio processing and speech services."""

from src.realtime_processing.realtime_gtts import speak as speak_gtts
from src.realtime_processing.realtime_openai import speak as speak_openai
from src.realtime_processing.speech_to_text_realtime import (
    record_and_transcribe_loop,
    record_and_transcribe,
)

__all__ = [
    "speak_gtts",
    "speak_openai",
    "record_and_transcribe_loop",
    "record_and_transcribe",
]
