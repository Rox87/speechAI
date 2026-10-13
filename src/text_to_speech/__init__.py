"""Text-to-speech convenience modules."""

from src.text_to_speech.text_to_speech_gtts import save_speech as save_speech_gtts
from src.text_to_speech.text_to_speech_openai import save_speech as save_speech_openai
from src.realtime_processing.realtime_gtts import speak as speak_gtts
from src.realtime_processing.realtime_openai import speak as speak_openai

__all__ = [
    "save_speech_gtts",
    "save_speech_openai",
    "speak_gtts",
    "speak_openai",
]
